from abc import ABC, abstractmethod
from collections.abc import Callable

import numpy as np

class IVideoProcessor(ABC): #Interfaces
    
    @abstractmethod
    def streamVideoFrameRTSP(self, rtsp: str, callbackFrame: Callable[[np.ndarray], None]):
        pass

    @abstractmethod
    def streamVideoFrameUSB(self, deviceNumber: int, callbackFrame: Callable[[np.ndarray], None]):
        pass

    @abstractmethod
    def drawRectangle(self, frame: np.ndarray, bbox: np.ndarray):
        pass

    @abstractmethod
    def presentInWindow(self, frame: np.ndarray):
        pass

    @abstractmethod
    def redraw(self, frame: np.ndarray, bbox: np.ndarray):
        pass