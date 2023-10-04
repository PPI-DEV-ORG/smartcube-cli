from internal.modules.VideoProcessor import VideoProcessor
from internal.modules.ModelRegistrar import ModelRegistrar
from internal.modules.DeviceRegistrar import DeviceRegistrar
from internal.modules.Notification import Notification
from internal.modules.HostDeviceStatus import HostDeviceStatus
from internal.modules.MQTT import MQTTService
from internal.modules.CommandManager import CommandManager
from internal.contracts.IDevice import CameraDevice
import threading
import multiprocessing
import time


def instantiateDevice(device: dict[str, CameraDevice], videoProcessor: VideoProcessor, notification: Notification):
    model = device["assigned_model_class"](videoProcessor)  # type: ignore
    device["device_instance"].streamVideoFrame(lambda frame: videoProcessor.presentInWindow(
        model.inferenceFrame(frame, 0.5, 0.6, 60, 50, notification.handleOnObjectDetected)))


def main():

    processes: list[multiprocessing.Process] = []

    #Init Video Processor
    videoProcessor = VideoProcessor()

    #Init Registered Models
    modelRegistrar = ModelRegistrar()
    modelRegistrar.load()

    #Init All Devices In config/devices.json
    deviceRegistar = DeviceRegistrar()
    deviceRegistar.loadCamera(modelRegistrar=modelRegistrar, videoProcessor=videoProcessor)

    #Init Notification Module
    notification = Notification(videoProcessor=videoProcessor)

    #Init Host Devices Status Module
    hostDevice = HostDeviceStatus()


    def restartDevice(arg, messageMetadata):
        processes[0].terminate()
        time.sleep(2)
        processes[0] = multiprocessing.Process(target=instantiateDevice, args=(deviceRegistar.getDevicesInstance()[0], videoProcessor, notification)) #child
        processes[0].daemon = True
        processes[0].start()


    def getRunningProcesses(arg, messageMetadata):
        print(processes)

    def getHostDeviceStatus(arg, messageMetadata):
        print(hostDevice.brief())

    def registerRemoteCommand():
        commandManager = CommandManager()
        commandManager.registerCommand("/restart", '', restartDevice)
        commandManager.registerCommand("/getProcesses", '', getRunningProcesses)
        commandManager.registerCommand("/hostDeviceStatus", '', getHostDeviceStatus)

        mqttService = MQTTService()
        mqttService.run(commandManager.recieveMessage)
        

    #Listening to Remote Command using MQTT Protocol
    commandListener = threading.Thread(target=registerRemoteCommand)
    commandListener.start()


    for device in deviceRegistar.getDevicesInstance():
        p = multiprocessing.Process(target=instantiateDevice, args=(device, videoProcessor, notification)) #child
        p.daemon = True
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

if __name__ == '__main__':
    main()
