from abc import ABC, abstractmethod

import numpy as np

class IObjectDetectorModel(ABC): #Interfaces

    @abstractmethod
    def processFrame(self, frame: np.ndarray) -> np.ndarray:
        pass