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
from internal.helper.helper import generateRandomString
import threading
import multiprocessing
import time
import json
import logging
from dotenv import load_dotenv

load_dotenv()


def instantiateModel(modelClass: IObjectDetectorModel, videoProcessor: VideoProcessor, notificationService: Notification, inputQueue: multiprocessing.Queue, outputQueue: multiprocessing.Queue):

    print("Child process is running")

    model: IObjectDetectorModel = modelClass(videoProcessor)  # type: ignore
    devId = 0
    # Event: this will run when there is at least 1 object detected

    def onObjectDetected(classLabel, confidence, frame):
        # print("device id on object detected", devId)
        notificationService.handleOnObjectDetected(
            devId, classLabel, confidence, frame)

    while True:
        try:
            # Menerima frame dari webcam threads melalui input_queue
            deviceId, frame = inputQueue.get()
            devId = deviceId
            # Proses frame (contoh: konversi ke grayscale)
            processed_frame = model.inferenceFrame(
                frame, 0.7, 0.6, 50, 50, onObjectDetected)
            

            videoProcessor.presentInWindow(deviceId, processed_frame)

            # Mengirim hasil ke main process melalui output_queue
            outputQueue.put((deviceId, processed_frame))

        except Exception as e:
            print("Error in child process:", e)


def instantiateCamera(device: dict[str, CameraDevice], inputQueue: multiprocessing.Queue):
    devMetada = device['device_instance'].getDeviceMetadata()

    def sendFrameToModel(frame):
        inputQueue.put((devMetada['device_id'], frame))

    # Stream Frame
    device["device_instance"].streamVideoFrame(lambda frame: sendFrameToModel(frame))


# All dependencies are bootstrapped inside this function
def main():

    # Device process list
    deviceProcesses: list[multiprocessing.Process] = []
    deviceProcessesIndex: list[dict] = []

    # Init pre configured http client
    httpClient: IHttpClient = HttpClient()

    # Init Video Processor
    videoProcessor = VideoProcessor()

    # Init Registered Models
    modelRegistrar = ModelRegistrar()
    modelRegistrar.load()

    # Init Model Manager
    print("\nInstalled Models:")
    modelManager = ModelManager(modelRegistrar=modelRegistrar)
    for i in range(0, len(modelManager.getRegisteredModelsMetadata())):
        print(f"{i+1}.", modelManager.getRegisteredModelsMetadata()[i])

    # Init All Devices In config/devices.json
    print("\nDevices Config:")
    deviceRegistar = DeviceRegistrar()
    deviceRegistar.loadDevices(modelRegistrar=modelRegistrar,
                               videoProcessor=videoProcessor, httpClient=httpClient)
    for i in range(0, len(deviceRegistar.getDevicesInstance())):
        print(f"{i+1}.", deviceRegistar.getDevicesInstance()[i])
    print("\n")

    # Init Notification Module
    notificationService = Notification(
        videoProcessor=videoProcessor, httpClient=httpClient)

    # Init Host Devices Status Module
    hostDevice = HostDeviceStatus()

    # Config
    config = Config()

    # Connect to MQTT
    mqttService = MQTTService()

    # Restart Device Process
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

    # Start Device Process
    def startDevice(processIndex, messageMetadata):
        print("start device is being develop")
        # # print(deviceRegistar.getDevicesInstance())
        # try:
        #     logging.info("starting edge device configuration")
        #     p = multiprocessing.Process(
        #         target=instantiateCamera,
        #         args=(deviceRegistar.getDevicesInstance()[int(processIndex)],
        #               videoProcessor,
        #               notificationService))
        #     p.daemon = True
        #     p.start()

        #     deviceProcesses.append(p)
        #     mqttService.publish(json.dumps({'command': '/msg', 'data': "device config started"}))

        # except Exception as e:
        #     logging.error(f"starting device config failed: {e}")
        #     # notify user
        #     mqttService.publish(json.dumps({'command': '/msg', 'data': f"starting device config failed: {e}"}))

    # Synchronize Edge Config
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
                # notify user
                mqttService.publish(json.dumps(
                    {'command': '/msg', 'data': "edge config synchronized"}))

            else:
                logging.info(
                    f"failed to fetch edge devices config. status code: {response.status_code}")
                # notify user
                mqttService.publish(json.dumps(
                    {'command': '/msg', 'data': f"edge server failed to fetch edge devices config. status code: {response.status_code}"}))

        except json.JSONDecodeError as e:
            logging.info(f"error synchronize edge config: {e}")
            # notify user
            mqttService.publish(json.dumps(
                {'command': '/msg', 'data': f"error synchronize edge config: {e}"}))

    # Prepare command manager
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

    # Listening to Remote Command using MQTT Protocol
    commandListener = threading.Thread(target=commandManager)
    commandListener.start()

    # Instantiate in multi processes & threads
    processCounter = 0

    # Active Model Process
    activeModelQueue = {}
    activeModelProcesses: list[multiprocessing.Process] = []
    outputQueues = []

    # Cameras Threads
    camerasChildThreads: list[threading.Thread] = []

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
                    devMetadata['assigned_model_index']),  # type: ignore
                    videoProcessor, notificationService,
                    activeModelQueue[activeModelKey]["inputQueue"],
                    activeModelQueue[activeModelKey]["outputQueue"]))

                p.daemon = True
                p.start()
                activeModelProcesses.append(p)


    for device in deviceRegistar.getDevicesInstance():
        if device['device_instance'].type() == 'camera':  # type: ignore

            devMetadata = device['device_instance'].getDeviceMetadata() # type: ignore

            activeModelKey = f"{devMetadata['assigned_model_type']} + {devMetadata['assigned_model_index']}"
            p = threading.Thread(target=instantiateCamera, args=(
                device, activeModelQueue[activeModelKey]['inputQueue']))
            p.daemon = True
            p.start()
            camerasChildThreads.append(p)

            # deviceProcessesIndex.append({
            #     # type: ignore
            #     "device_id": device['device_instance'].getDeviceId(), # type: ignore
            #     "type": "camera",
            #     "process_index": processCounter
            # })
            # processCounter += 1


    for p in activeModelProcesses:
        p.join()

    for q in camerasChildThreads:
        q.join()


if __name__ == '__main__':
    main()
