from abc import ABC, abstractmethod
from collections.abc import Callable

import numpy as np

class IObjectDetectorModel(ABC): #Interfaces

    @abstractmethod
    def processFrame(self, frame: np.ndarray, callback: Callable[[np.ndarray, list], None]):
        pass