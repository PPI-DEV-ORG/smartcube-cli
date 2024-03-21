from abc import ABC, abstractmethod
from internal.contracts.IVideoProcessor import IVideoProcessor
from internal.contracts.IModelRegistrar import IModelRegistrar
from internal.contracts.IHttpClient import IHttpClient
from internal.contracts.IDevice import Device
from internal.contracts.IAIModel import IAIModel
from typing import Union

class IDeviceRegistrar(ABC):

    @abstractmethod
    def loadDevices(self, modelRegistrar: IModelRegistrar, videoProcessor: IVideoProcessor, httpClient: IHttpClient) -> None:
        pass

    @abstractmethod
    def reloadDevices(self, modelRegistrar: IModelRegistrar, videoProcessor: IVideoProcessor, httpClient: IHttpClient) -> None:
        pass

    @abstractmethod
    def getDevicesInstance(self) -> list[dict[str, Union[Device, IAIModel]]]:
        pass

    @abstractmethod
    def printConsole(self) -> None:
        pass