from abc import ABC, abstractmethod
from typing import Callable
from internal.contracts.IAIModel import IAIModel
import numpy as np

class IObjectDetectorModel(IAIModel, ABC): #Interfaces

    @abstractmethod
    def inferenceFrame(
        self, 
        frame: np.ndarray,
        onObjectDetected: Callable[[str, int, np.ndarray], None] = lambda classLabel, confidence, frame: None
        ) -> np.ndarray:
        pass