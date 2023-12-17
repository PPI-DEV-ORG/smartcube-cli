from internal.modules.VideoProcessor import VideoProcessor
from internal.modules.ModelRegistrar import ModelRegistrar
from internal.modules.DeviceRegistrar import DeviceRegistrar
from internal.modules.Notification import Notification
from internal.modules.HostDeviceStatus import HostDeviceStatus
from internal.modules.MQTT import MQTTService
from internal.modules.CommandManager import CommandManager
from internal.modules.Config import Config
from internal.modules.ModelManager import ModelManager
from internal.modules.HttpClient import HttpClient
from internal.contracts.IDevice import CameraDevice, SensorDevice
from internal.contracts.IObjectDetectorModel import IObjectDetectorModel
from internal.contracts.ISensorModel import ISensorModel
from internal.contracts.IHttpClient import IHttpClient
import threading
import multiprocessing
import time
import json
import logging
from dotenv import load_dotenv

load_dotenv()

def instantiateCamera(device: dict[str, CameraDevice], videoProcessor: VideoProcessor, notificationService: Notification):
    model: IObjectDetectorModel = device["assigned_model_class"](videoProcessor)  # type: ignore
    
    #Event: this will run when there is at least 1 object detected
    def onObjectDetected(classLabel, confidence, frame):
        notificationService.handleOnObjectDetected(device['device_instance'].getDeviceId(), classLabel, confidence, frame)

    #Additional wrapper function to be able accessing other depedencies
    def inferFrame(frame):
       videoProcessor.presentInWindow(model.inferenceFrame(frame, 0.7, 0.85, 50, 50, onObjectDetected))
    
    #Stream Frame
    device["device_instance"].streamVideoFrame(lambda frame: inferFrame(frame))
    
def instantiateSensor(device: dict[str, SensorDevice], httpClient: IHttpClient, notificationService: Notification, x):
    model: ISensorModel = device["assigned_model_class"]()  # type: ignore
    
    def onThresholdExceeded(riskLevel: str):
        notificationService.onThresholdExceeded(deviceId=device["device_instance"].getDeviceId(), riskLevel=riskLevel)

    #Event: on infered data
    def onInfered(inferedPayload: dict):
        payload = {
            "data": [
                {
                    "edge_server_id": 0,
                    "device_id": device["device_instance"].getDeviceId(),
                    "data_measured": inferedPayload["dataMeasured"],
                    "inference_label_status": inferedPayload["inferenceLabelStatus"],
                    "captured_at": inferedPayload["capturedAt"]
                },
            ]
        }

        try:
            response = httpClient.getSession().post(
                url=f'{httpClient.baseUrl()}/edge-device-sensor/{device["device_instance"].getDeviceId()}',
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code == 200:
                print("sensor data sent successfully")
            else:
                print(
                    f"failed to sent sensor data: {response.text}")
                
        except Exception as e:
            print("sending sensor data throw an exception", e)
        
    device["device_instance"].streamData(lambda data: model.inferData(data=data, onInfered=onInfered, onThresholdExceeded=onThresholdExceeded))

#All dependencies are bootstrapped inside this function
def main():

    # Device process list
    deviceProcesses: list[multiprocessing.Process] = []
    deviceThreads: list[threading.Thread] = []

    # Init pre configured http client
    httpClient: IHttpClient = HttpClient()

    # Init Video Processor
    videoProcessor = VideoProcessor()

    # Init Registered Models
    modelRegistrar = ModelRegistrar()
    modelRegistrar.load()
    print(modelRegistrar.getAllModelClass())
    
    # Init Model Manager
    modelManager = ModelManager(modelRegistrar=modelRegistrar)

    # Init All Devices In config/devices.json
    deviceRegistar = DeviceRegistrar()
    deviceRegistar.loadDevices(modelRegistrar=modelRegistrar, videoProcessor=videoProcessor, httpClient=httpClient)

    # Init Notification Module
    notificationService = Notification(videoProcessor=videoProcessor, httpClient=httpClient)

    # Init Host Devices Status Module
    hostDevice = HostDeviceStatus()

    # Config
    config = Config()

    # Connect to MQTT
    mqttService = MQTTService()

    # Restart Device Process
    def restartDevice(processIndex, messageMetadata):
        try:
            deviceProcesses[int(processIndex)].terminate()
            time.sleep(1)
            deviceProcesses[int(processIndex)] = multiprocessing.Process(
                target=instantiateCamera,
                args=(deviceRegistar.getDevicesInstance()[int(processIndex)],
                      videoProcessor,
                      notificationService))
            deviceProcesses[int(processIndex)].daemon = True
            deviceProcesses[int(processIndex)].start()

            logging.info("device config restarted")
            # notify user
            mqttService.publish(json.dumps({'command': '/msg', 'data': "device config restarted"}))

        except Exception as e:
            logging.error(f"restarting device config failed: {e}")
            # notify user
            mqttService.publish(json.dumps({'command': '/msg', 'data': f"restarting device config failed: {e}"}))
            
    # Start Device Process
    def startDevice(processIndex, messageMetadata):
        # print(deviceRegistar.getDevicesInstance())
        try:
            logging.info("starting edge device configuration")
            p = multiprocessing.Process(
                target=instantiateCamera,
                args=(deviceRegistar.getDevicesInstance()[int(processIndex)],
                      videoProcessor,
                      notificationService))
            p.daemon = True
            p.start()

            deviceProcesses.append(p)
            mqttService.publish(json.dumps({'command': '/msg', 'data': "device config started"}))

        except Exception as e:
            logging.error(f"starting device config failed: {e}")
            # notify user
            mqttService.publish(json.dumps({'command': '/msg', 'data': f"starting device config failed: {e}"}))
            
    # Synchronize Edge Config
    def syncEdgeConfig(arg, metadata):
        try:
            response = httpClient.getSession().get(f"{httpClient.baseUrl()}/edge-device-config")
            if response.status_code == 200:
                # Rewrite devices.json to sync configuration between backend to edge config
                devicesConfig = {"devices": json.loads(response.content.decode())["data"]}
                with open('internal/config/devices.json', "w") as outfile:
                    outfile.write(json.dumps(devicesConfig, indent=4))

                # Reload Device configuration
                deviceRegistar.reloadDevices(
                    modelRegistrar=modelRegistrar, 
                    videoProcessor=videoProcessor,
                    httpClient=httpClient)

                logging.info("edge config synchronized")
                # notify user
                mqttService.publish(json.dumps({'command': '/msg', 'data': "edge config synchronized"}))

            else:
                logging.info(f"failed to fetch edge devices config. status code: {response.status_code}")
                # notify user
                mqttService.publish(json.dumps({'command': '/msg', 'data': f"edge server failed to fetch edge devices config. status code: {response.status_code}"}))

        except json.JSONDecodeError as e:
            logging.info(f"error synchronize edge config: {e}")
            # notify user
            mqttService.publish(json.dumps({'command': '/msg', 'data': f"error synchronize edge config: {e}"}))

    # Prepare command manager
    def commandManager():
        # Command response
        hostDeviceStatusData = json.dumps({'command': '/hostDeviceStatus', 'data': hostDevice.brief()}, indent=4)
        deviceConfigData = json.dumps({'command': '/getDeviceConfig', 'data': config.getDevicesConfig()}, indent=4)
        installedModelsData = json.dumps({'command': '/getInstalledModels', 'data': modelManager.getRegisteredModelsMetadata()}, indent=4)

        # Command Manager
        commandManager = CommandManager()
        commandManager.registerCommand("/restartDevice", '', restartDevice)
        commandManager.registerCommand("/startDevice", '', startDevice)
        commandManager.registerCommand("/getProcesses", '', lambda arg, metadata: mqttService.publish(deviceProcesses.__str__()))
        commandManager.registerCommand("/hostDeviceStatus", '', lambda arg, metadata: mqttService.publish(hostDeviceStatusData))
        commandManager.registerCommand("/getDeviceConfig", '', lambda arg, metadata: mqttService.publish(deviceConfigData))
        commandManager.registerCommand("/getInstalledModels", '', lambda arg, metadata: mqttService.publish(installedModelsData))
        commandManager.registerCommand("/syncEdgeConfig", "", syncEdgeConfig)

        # Recieve message and process the command
        mqttService.run(commandManager.receiveMessage)

    # Listening to Remote Command using MQTT Protocol
    commandListener = threading.Thread(target=commandManager)
    commandListener.start()

    # Instantiate in multi processes & threads
    for device in deviceRegistar.getDevicesInstance():
        if device['device_instance'].type() == 'camera': # type: ignore
            p = multiprocessing.Process(target=instantiateCamera, args=(
                device, videoProcessor, notificationService))
            p.daemon = True
            p.start()
            deviceProcesses.append(p)
            
        elif device['device_instance'].type() == 'sensor': # type: ignore
            t = threading.Thread(target=instantiateSensor, args=(device, httpClient, notificationService, 0))
            t.daemon = True
            t.start()
            deviceThreads.append(t)

    for p in deviceProcesses:
        p.join()

    for t in deviceThreads:
        t.join()

if __name__ == '__main__':
    main()
