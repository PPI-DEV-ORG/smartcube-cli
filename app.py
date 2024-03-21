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
from internal.contracts.IDevice import CameraDevice
from internal.contracts.IObjectDetectorModel import IObjectDetectorModel
from internal.contracts.IHttpClient import IHttpClient
import threading
import multiprocessing
import json
import logging
from dotenv import load_dotenv

load_dotenv()

def instantiateModel(modelClass: IObjectDetectorModel, videoProcessor: VideoProcessor, inputQueue: multiprocessing.Queue, outputQueue: multiprocessing.Queue):
    model: IObjectDetectorModel = modelClass(videoProcessor)  # type: ignore
    devId = 0

    def onObjectDetected(classLabel, confidence, frame):
        # notificationService.handleOnObjectDetected(devId, classLabel, confidence, frame)
        outputQueue.put((devId, classLabel, confidence, frame))

    while True:
        try:
            deviceId, frame = inputQueue.get()
            devId = deviceId
            processed_frame = model.inferenceFrame(frame, onObjectDetected)
            videoProcessor.presentInWindow(deviceId, processed_frame)

        except Exception as e:
            print("Error in while inferencing frames", e)

def instantiateCamera(device: dict[str, CameraDevice], inputQueue: multiprocessing.Queue):
    devMetada = device['device_instance'].getDeviceMetadata()

    def sendFrameToModel(frame):
        inputQueue.put((devMetada['device_id'], frame))

    device["device_instance"].streamVideoFrame(lambda frame: sendFrameToModel(frame))


# All dependencies are bootstrapped inside this function
def main():

    # active model process
    activeModelQueue = {}
    activeModelProcesses: list[multiprocessing.Process] = []
    outputQueues = []

    # cameras threads
    camerasChildThreads: list[threading.Thread] = []

    # notification threads
    notificationServiceThreads: list[threading.Thread] = []

    # device process list
    deviceProcessesIndex: list[dict] = []

    # init pre configured http client
    httpClient: IHttpClient = HttpClient()

    # init video processor
    videoProcessor = VideoProcessor()

    # init registered models
    modelRegistrar = ModelRegistrar()
    modelRegistrar.load()

    # init model manager
    modelManager = ModelManager(modelRegistrar=modelRegistrar)
    modelManager.printConsole()

    # init all devices in config/devices.json
    deviceRegistar = DeviceRegistrar()
    deviceRegistar.loadDevices(modelRegistrar=modelRegistrar, videoProcessor=videoProcessor, httpClient=httpClient)
    deviceRegistar.printConsole()
    
    # init notification module
    notificationService = Notification(
        videoProcessor=videoProcessor, httpClient=httpClient)

    # init host devices status module
    hostDevice = HostDeviceStatus()

    # config
    config = Config()

    # connect to MQTT
    mqttService = MQTTService()

    # restart device process
    def restartDevice(processIndex, messageMetadata):
        print("restart device is being develop")
        # try:
        #     deviceProcesses[int(processIndex)].terminate()
        #     time.sleep(1)
        #     deviceProcesses[int(processIndex)] = multiprocessing.Process(
        #         target=instantiateCamera,
        #         args=(deviceRegistar.getDevicesInstance()[int(processIndex)],
        #               videoProcessor,
        #               notificationService))
        #     deviceProcesses[int(processIndex)].daemon = True
        #     deviceProcesses[int(processIndex)].start()

        #     logging.info("device config restarted")
        #     # notify user
        #     mqttService.publish(json.dumps({'command': '/msg', 'data': "device config restarted"}))

        # except Exception as e:
        #     logging.error(f"restarting device config failed: {e}")
        #     # notify user
        #     mqttService.publish(json.dumps({'command': '/msg', 'data': f"restarting device config failed: {e}"}))

    # start device process
    def startDevice(processIndex, messageMetadata):
        try:
            # instantiate inference models in different child process and assign i/o queue for transmitting frames
            for device in deviceRegistar.getDevicesInstance():
                if device['device_instance'].type() == 'camera': # type: ignore
                    devMetadata = device['device_instance'].getDeviceMetadata() # type: ignore
                    activeModelKey = f"{devMetadata['assigned_model_type']} + {devMetadata['assigned_model_index']}"
                    if activeModelKey not in activeModelQueue:
                        outputQueue = multiprocessing.Queue()
                        activeModelQueue[activeModelKey] = {
                            "inputQueue": multiprocessing.Queue(),
                            "outputQueue": outputQueue,
                        }
                        outputQueues.append(outputQueue)
                        p = multiprocessing.Process(target=instantiateModel, args=(modelRegistrar.getModelClass(
                            devMetadata['assigned_model_index']),
                            videoProcessor,
                            activeModelQueue[activeModelKey]["inputQueue"],
                            activeModelQueue[activeModelKey]["outputQueue"]))
                        p.daemon = True
                        p.start()
                        activeModelProcesses.append(p)

            # start camera stream
            device = deviceRegistar.getDevicesInstance()[int(processIndex)]
            if device['device_instance'].type() == 'camera':  # type: ignore
                    devMetadata = device['device_instance'].getDeviceMetadata() # type: ignore
                    activeModelKey = f"{devMetadata['assigned_model_type']} + {devMetadata['assigned_model_index']}"
                    p = threading.Thread(target=instantiateCamera, args=(device, activeModelQueue[activeModelKey]['inputQueue']))
                    p.daemon = True
                    p.start()
                    camerasChildThreads.append(p)

            mqttService.publish(json.dumps({'command': '/msg', 'data': "device started successfully"}))

        except Exception as e:
            logging.error(f"starting device config failed: {e}")
            mqttService.publish(json.dumps({'command': '/msg', 'data': f"starting device failed: {e}"}))

    # synchronize Edge Config
    def syncEdgeConfig(arg, metadata):
        try:
            response = httpClient.getSession().get(
                f"{httpClient.baseUrl()}/edge-device-config")
            if response.status_code == 200:
                # Rewrite devices.json to sync configuration between backend to edge config
                devicesConfig = {"devices": json.loads(
                    response.content.decode())["data"]}
                with open('internal/config/devices.json', "w") as outfile:
                    outfile.write(json.dumps(devicesConfig, indent=4))

                # Reload Device configuration
                deviceRegistar.reloadDevices(
                    modelRegistrar=modelRegistrar,
                    videoProcessor=videoProcessor,
                    httpClient=httpClient)

                logging.info("edge config synchronized")
                mqttService.publish(json.dumps({'command': '/msg', 'data': "edge devices config synchronized"}))

            else:
                logging.info(f"failed to fetch edge devices config. status code: {response.status_code}")
                mqttService.publish(json.dumps(
                    {'command': '/msg', 'data': f"edge server failed to fetch edge devices config. status code: {response.status_code}"}))

        except json.JSONDecodeError as e:
            logging.info(f"error synchronize edge config: {e}")
            mqttService.publish(json.dumps({'command': '/msg', 'data': f"error synchronize edge config: {e}"}))

    # prepare command manager
    def commandManager():
        # Command response
        hostDeviceStatusData = json.dumps(
            {'command': '/hostDeviceStatus', 'data': hostDevice.brief()}, indent=4)
        deviceConfigData = json.dumps(
            {'command': '/getDeviceConfig', 'data': config.getDevicesConfig()}, indent=4)
        installedModelsData = json.dumps(
            {'command': '/getInstalledModels', 'data': modelManager.getRegisteredModelsMetadata()}, indent=4)
        deviceProcessesIndexData = json.dumps(
            {'command': '/getProcesses', 'data': deviceProcessesIndex}, indent=4)

        # Command Manager
        commandManager = CommandManager()
        commandManager.registerCommand("/restartDevice", '', restartDevice)
        commandManager.registerCommand("/startDevice", '', startDevice)
        commandManager.registerCommand(
            "/getProcesses", '', lambda arg, metadata: mqttService.publish(deviceProcessesIndexData))
        commandManager.registerCommand(
            "/hostDeviceStatus", '', lambda arg, metadata: mqttService.publish(hostDeviceStatusData))
        commandManager.registerCommand(
            "/getDeviceConfig", '', lambda arg, metadata: mqttService.publish(deviceConfigData))
        commandManager.registerCommand(
            "/getInstalledModels", '', lambda arg, metadata: mqttService.publish(installedModelsData))
        commandManager.registerCommand("/syncEdgeConfig", "", syncEdgeConfig)

        # Recieve message and process the command
        mqttService.run(commandManager.receiveMessage)

    # listening to remote command using MQTT protocol
    commandListener = threading.Thread(target=commandManager)
    commandListener.start()

    # instantiate inference models in different child process and assign i/o queue for transmitting frames
    for device in deviceRegistar.getDevicesInstance():
        if device['device_instance'].type() == 'camera':  # type: ignore
            devMetadata = device['device_instance'].getDeviceMetadata() # type: ignore
            activeModelKey = f"{devMetadata['assigned_model_type']} + {devMetadata['assigned_model_index']}"
            if activeModelKey not in activeModelQueue:
                outputQueue = multiprocessing.Queue()
                activeModelQueue[activeModelKey] = {
                    "inputQueue": multiprocessing.Queue(),
                    "outputQueue": outputQueue,
                }
                outputQueues.append(outputQueue)
                p = multiprocessing.Process(target=instantiateModel, args=(modelRegistrar.getModelClass(
                    devMetadata['assigned_model_index']),
                    videoProcessor,
                    activeModelQueue[activeModelKey]["inputQueue"],
                    activeModelQueue[activeModelKey]["outputQueue"]))
                p.daemon = True
                p.start()
                activeModelProcesses.append(p)

    # start camera stream
    for device in deviceRegistar.getDevicesInstance():
        if device['device_instance'].type() == 'camera':  # type: ignore
            devMetadata = device['device_instance'].getDeviceMetadata() # type: ignore
            activeModelKey = f"{devMetadata['assigned_model_type']} + {devMetadata['assigned_model_index']}"
            p = threading.Thread(target=instantiateCamera, args=(device, activeModelQueue[activeModelKey]['inputQueue']))
            p.daemon = True
            p.start()
            camerasChildThreads.append(p)


    def sendNotif(outputQueue: multiprocessing.Queue):
        while True:
            deviceId, classLabel, confidence, frame = outputQueue.get()
            # print(deviceId, classLabel, confidence)
            try:
                notificationService.handleOnObjectDetected(deviceId, classLabel, confidence, frame)
            except Exception as e:
                print(f"Error while sending notification: {e}")

    # take frame that should be notified
    for outputQueue in outputQueues:
        t = threading.Thread(target=sendNotif, args=([outputQueue]))
        t.daemon = True
        t.start()
        notificationServiceThreads.append(t)

    for modelProcess in activeModelProcesses:
        modelProcess.join()

    for cameraThread in camerasChildThreads:
        cameraThread.join()

    for notifThread in notificationServiceThreads:
        notifThread.join()

if __name__ == '__main__':
    main()
