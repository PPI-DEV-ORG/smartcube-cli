from abc import ABC, abstractmethod

class IAIModel(ABC):

    @abstractmethod
    def getModelType(self) -> str:
        pass

    @abstractmethod
    def getModelVersion(self) -> str:
        pass