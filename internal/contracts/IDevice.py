from abc import ABC, abstractmethod
from typing import Callable

import numpy as np

class Device(ABC): #Interfaces
    
    @abstractmethod
    def getDeviceMetadata(self) -> dict:
        pass

class CameraDevice(Device):

    @abstractmethod
    def streamVideoFrame(self, callback: Callable[[np.ndarray], None]) -> None:
        pass