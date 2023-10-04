from internal.contracts.IModelRegistrar import IModelRegistrar
from internal.contracts.IAIModel import IAIModel

class ModelManager:
    
    modelRegistrar: IModelRegistrar

    def __init__(self, modelRegistrar: IModelRegistrar) -> None:
        self.modelRegistrar = modelRegistrar

    def getRegisteredModel(self) -> list[IAIModel]:
        return self.modelRegistrar.getAllModelClass()


