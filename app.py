from internal.modules.VideoProcessor import VideoProcessor
from internal.modules.ModelRegistrar import ModelRegistrar
from internal.modules.DeviceRegistrar import DeviceRegistrar
from internal.modules.Notification import Notification
from internal.modules.HostDeviceStatus import HostDeviceStatus
from internal.modules.MQTT import MQTTService
from internal.modules.CommandManager import CommandManager
from internal.modules.Config import Config
from internal.contracts.IDevice import CameraDevice
from internal.modules.ModelManager import ModelManager
import threading
import multiprocessing
import time
import json

def instantiateDevice(device: dict[str, CameraDevice], videoProcessor: VideoProcessor, notificationService: Notification):
    model = device["assigned_model_class"](videoProcessor)  # type: ignore
    device["device_instance"].streamVideoFrame(lambda frame: videoProcessor.presentInWindow(
        model.inferenceFrame(frame, 0.5, 0.6, 60, 50, notificationService.handleOnObjectDetected)))


def main():

    processes: list[multiprocessing.Process] = []

    #Init Video Processor
    videoProcessor = VideoProcessor()

    #Init Registered Models
    modelRegistrar = ModelRegistrar()
    modelRegistrar.load()

    #Init Model Manager
    modelManager = ModelManager(modelRegistrar=modelRegistrar)

    #Init All Devices In config/devices.json
    deviceRegistar = DeviceRegistrar()
    deviceRegistar.loadCamera(modelRegistrar=modelRegistrar, videoProcessor=videoProcessor)

    #Init Notification Module
    notificationService = Notification(videoProcessor=videoProcessor)

    #Init Host Devices Status Module
    hostDevice = HostDeviceStatus()

    #Config
    config = Config()
    
    def restartDevice(processIndex, messageMetadata):
        processes[int(processIndex)].terminate()
        time.sleep(2)
        processes[int(processIndex)] = multiprocessing.Process(
            target=instantiateDevice, 
            args=(deviceRegistar.getDevicesInstance()[int(processIndex)], 
            videoProcessor, 
            notificationService))
        processes[int(processIndex)].daemon = True
        processes[int(processIndex)].start()


    def commandManager():

        #Connect to MQTT
        mqttService = MQTTService()
        
        #Command Manager
        commandManager = CommandManager()
        commandManager.registerCommand("/restartDevice", '', restartDevice)
        commandManager.registerCommand("/getProcesses", '', lambda arg, metadata: mqttService.publish(processes.__str__()))
        commandManager.registerCommand("/hostDeviceStatus", '',  lambda arg, metadata: mqttService.publish(json.dumps(hostDevice.brief(), indent=4)))
        commandManager.registerCommand("/getDeviceConfig", '', lambda arg, metadata: mqttService.publish(json.dumps(config.getDevicesConfig(), indent=4)))
        commandManager.registerCommand("/getInstalledModels", '', lambda arg, metadata: mqttService.publish(json.dumps(modelManager.getRegisteredModelsMetadata(), indent=4)))        
        
        mqttService.run(commandManager.receiveMessage)

    #Listening to Remote Command using MQTT Protocol
    commandListener = threading.Thread(target=commandManager)
    commandListener.start()

    for device in deviceRegistar.getDevicesInstance():
        p = multiprocessing.Process(target=instantiateDevice, args=(device, videoProcessor, notificationService))
        p.daemon = True
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

if __name__ == '__main__':
    main()
