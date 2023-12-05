from abc import ABC, abstractmethod
from typing import Callable, Any
import numpy as np

class Device(ABC): #Interfaces
    
    @abstractmethod
    def getDeviceMetadata(self) -> dict:
        pass

    @abstractmethod
    def type(self) -> str:
        pass

    @abstractmethod
    def getDeviceId(self) -> Any:
        pass

class CameraDevice(Device):

    @abstractmethod
    def streamVideoFrame(self, callback: Callable[[np.ndarray], None]) -> None:
        pass

class SensorDevice(Device):

    @abstractmethod
    def streamData(self, callback: Callable[[Any], None]) -> None:
        pass