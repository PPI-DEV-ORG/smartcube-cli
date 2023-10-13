from abc import ABC, abstractmethod

class IAIModel(ABC):

    @staticmethod
    @abstractmethod
    def getModelType() -> str:
        pass

    @abstractmethod
    def getModelVersion(self) -> str:
        pass
    
    @staticmethod
    @abstractmethod
    def getModelMetadata() -> dict[str, str]:
        pass