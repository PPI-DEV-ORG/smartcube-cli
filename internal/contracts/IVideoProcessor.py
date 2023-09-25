from abc import ABC, abstractmethod
from collections.abc import Callable
import io
import typing

import numpy as np

class IVideoProcessor(ABC): #Interfaces
    
    @abstractmethod
    def streamVideoFrameRTSP(self, rtsp: str, callback: Callable[[np.ndarray], None]):
        pass

    @abstractmethod
    def streamVideoFrameUSB(self, deviceNumber: int, callback: Callable[[np.ndarray], None]):
        pass

    @abstractmethod
    def drawRectangle(self, frame: np.ndarray, bbox: list[tuple], color: int):
        pass

    @abstractmethod
    def writeText(self, frame: np.ndarray, text: str,  color: typing.Sequence[float], xcoordinate: int, ycoordinate: int):
        pass

    @abstractmethod
    def presentInWindow(self, frame: np.ndarray):
        pass

    @abstractmethod
    def redraw(self, frame: np.ndarray, bbox: np.ndarray):
        pass

    @abstractmethod
    def convertFrameToImage(self, frame: np.ndarray) -> io.BufferedReader:
        pass