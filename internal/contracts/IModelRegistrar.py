from abc import ABC, abstractmethod
from internal.contracts.IAIModel import IAIModel

class IModelRegistrar(ABC):

    @abstractmethod
    def load(self) -> None:
        pass

    @abstractmethod
    def getModelClass(self, index: int) -> IAIModel:
        pass

    @abstractmethod
    def getAllModelClass(self) -> list[IAIModel]:
        pass