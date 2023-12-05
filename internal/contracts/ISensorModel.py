from abc import ABC, abstractmethod
from typing import Callable, Any
from internal.contracts.IAIModel import IAIModel

class ISensorModel(IAIModel, ABC): #Interfaces

    @abstractmethod
    def inferData(self, data: Any, onInfered: Callable[[Any], None], onThresholdExceeded: Callable[[Any], None]):
        pass