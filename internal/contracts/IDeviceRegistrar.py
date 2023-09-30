from abc import ABC, abstractmethod
from internal.contracts.IVideoProcessor import IVideoProcessor
from internal.contracts.IModelRegistrar import IModelRegistrar
from internal.contracts.IDevice import Device

class IDeviceRegistrar(ABC):

    @abstractmethod
    def loadCamera(self, modelRegistrar: IModelRegistrar, videoProcessor: IVideoProcessor) -> None:
        pass

    @abstractmethod
    def getDevicesInstance(self) -> list[Device]:
        pass