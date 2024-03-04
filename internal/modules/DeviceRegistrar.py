from internal.contracts.IDeviceRegistrar import IDeviceRegistrar
from internal.contracts.IModelRegistrar import IModelRegistrar
from internal.contracts.IVideoProcessor import IVideoProcessor
from internal.contracts.IDevice import Device
from internal.contracts.IAIModel import IAIModel
from internal.modules.USBCamera import USBCamera
from internal.modules.IPCamera import IPCamera
from internal.modules.WirelessSensor import WirelessSensor
from internal.contracts.IHttpClient import IHttpClient
import internal.constants.device as device_constant
import internal.constants.model as model_constant
import os
import json
from typing import Union


class DeviceRegistrar(IDeviceRegistrar):

    __devices_instance: list[dict[str, Device | IAIModel]] = []
    __devices_config = {}

    def __init__(self) -> None:
        super().__init__()
        self.loadEdgeConfigFile()

    def loadEdgeConfigFile(self):
        # load devices config
        with open(os.path.join(os.path.dirname(__file__), '../config') + '/devices.json', 'r') as file:
            self.__devices_config = json.load(file)['devices']

    def loadDevices(self, modelRegistrar: IModelRegistrar, videoProcessor: IVideoProcessor, httpClient: IHttpClient) -> None:
        for device_config in self.__devices_config:
            if (device_config['type'] == 'camera'):
                if (modelRegistrar.getModelClass(int(device_config['assigned_model_index'])).getModelType() == device_config["assigned_model_type"]):
                    # instatiate camera device usb
                    if (device_config["source_type"] == device_constant.USB_CAMERA_DEVICE):
                        self.__devices_instance.append({
                            "device_instance": USBCamera(device_config["device_id"], device_config["source_address"], device_config, videoProcessor),
                            "assigned_model_class": modelRegistrar.getModelClass(int(device_config['assigned_model_index']))
                        })

                    # instatiate camera device rtsp
                    if (device_config["source_type"] == device_constant.RTSP_CAMERA_DEVICE):
                        self.__devices_instance.append({
                            "device_instance": IPCamera(device_config["device_id"], device_config["source_address"], device_config, videoProcessor),
                            "assigned_model_class": modelRegistrar.getModelClass(int(device_config['assigned_model_index']))
                        })

            elif (device_config['type'] == 'sensor'):
                if (modelRegistrar.getModelClass(int(device_config['assigned_model_index'])).getModelType() == device_config["assigned_model_type"]):
                    self.__devices_instance.append({
                        "device_instance": WirelessSensor(device_config["device_id"], device_config["source_address"], device_config["additional_info"], httpClient),
                        "assigned_model_class": modelRegistrar.getModelClass(int(device_config['assigned_model_index']))
                    })

    def reloadDevices(self, modelRegistrar: IModelRegistrar, videoProcessor: IVideoProcessor, httpClient: IHttpClient) -> None:

        # Reopen file
        self.loadEdgeConfigFile()

        # Set instance bucket empty
        self.__devices_instance = []

        # reload device
        self.loadDevices(modelRegistrar=modelRegistrar,
                        videoProcessor=videoProcessor,
                        httpClient=httpClient)

    def getDevicesInstance(self) -> list[dict[str, Union[Device, IAIModel]]]:
        return self.__devices_instance
