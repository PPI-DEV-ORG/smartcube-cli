from internal.contracts.IModelRegistrar import IModelRegistrar
from internal.contracts.IAIModel import IAIModel
from typing import Any

class ModelManager:
    
    __modelRegistrar: IModelRegistrar

    def __init__(self, modelRegistrar: IModelRegistrar) -> None:
        self.__modelRegistrar = modelRegistrar

    def getRegisteredModel(self) -> list[IAIModel]:
        return self.__modelRegistrar.getAllModelClass()

    def getRegisteredModelsMetadata(self) -> list[dict[str, Any]]:
        modelsMetadata: list[dict[str, Any]] = []

        for i in range(len(self.__modelRegistrar.getAllModelClass())):
            modelsMetadata.append(self.__modelRegistrar.getAllModelClass()[i].getModelMetadata())

        return modelsMetadata

    def printConsole(self):
        print("\nInstalled Models:")
        for i in range(0, len(self.getRegisteredModelsMetadata())):
            print(f"{i+1}.", self.getRegisteredModelsMetadata()[i])
        print("\n")