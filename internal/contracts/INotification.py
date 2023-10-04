from abc import ABC, abstractmethod
import numpy as np

class INotification:

    @abstractmethod
    def handleOnObjectDetected(self, classLabel: str, confidence: int, frame: np.ndarray) -> None:
        pass