from abc import ABC, abstractmethod

import numpy as np

class Device(ABC): #Interfaces
    
    @abstractmethod
    def getDeviceMetadata(self):
        pass

class CameraDevice(Device):

    @abstractmethod
    def streamVideoFrame(self, callbackFrame: np.ndarray):
        pass