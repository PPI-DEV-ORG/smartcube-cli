from internal.contracts.IDeviceRegistrar import IDeviceRegistrar
from internal.contracts.IModelRegistrar import IModelRegistrar
from internal.contracts.IVideoProcessor import IVideoProcessor
from internal.contracts.IDevice import Device
from internal.modules.USBCamera import USBCamera
from internal.modules.IPCamera import IPCamera
import os, json

class DeviceRegistrar(IDeviceRegistrar):

    __devices_instance: list = []
    __devices_config = {}

    def __init__(self) -> None:
        super().__init__()

        #load devices config
        with open(os.path.join(os.path.dirname(__file__), '../config') + '/devices.json', 'r') as file:
            self.__devices_config = json.load(file)['devices']

    def loadCamera(self, modelRegistrar: IModelRegistrar, videoProcessor: IVideoProcessor) -> None:
        for device_config in self.__devices_config:
            # if(device_config['assigned_model_type'] == modelRegistrar.getModelInstance(int(device_config['assigned_model_index'])).getModelType()):
                
            #instatiate device usb
            if(device_config["source_type"] == "usb"):
                self.__devices_instance.append({
                    "device_instance": USBCamera(device_config["usb_id"], device_config["additional_info"], videoProcessor),
                    "assigned_model_class": modelRegistrar.getModelClass(int(device_config['assigned_model_index']))
                })
                
            #instatiate device rtsp
            if(device_config["source_type"] == "rtsp"):
                self.__devices_instance.append(IPCamera(device_config["rtsp_address"], device_config["additional_info"], videoProcessor))

    def getDevicesInstance(self) -> list[Device]:
        return self.__devices_instance