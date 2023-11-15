from internal.contracts.IModelRegistrar import IModelRegistrar
from internal.contracts.IAIModel import IAIModel
import os, importlib

class ModelRegistrar(IModelRegistrar):

    __imported_models: list = []
    __modules_directory = ""
    __models_path = "registered_models"
    
    def __init__(self) -> None:
        super().__init__()
        self.__modules_directory = os.path.join(os.path.dirname(__file__), f'../{self.__models_path}/')

    def load(self) -> None:
        for module_file in os.listdir(self.__modules_directory):

            if module_file.endswith('.py'):

                module_name = os.path.splitext(module_file)[0]

                module = importlib.import_module(f'internal.{self.__models_path}.{module_name}')
                
                for name, obj in vars(module).items():
                    # print(str(obj))
                    if isinstance(obj, type):
                        if self.__models_path in str(obj):
                            self.__imported_models.append(obj)

    
    def getModelClass(self, index) -> IAIModel:
        return self.__imported_models[index]
        

    def getAllModelClass(self) -> list[IAIModel]:
        return self.__imported_models