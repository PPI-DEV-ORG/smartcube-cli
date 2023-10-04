import os, json

class Config:

    __config = {}

    def __init__(self) -> None:
        super().__init__()

        #load devices config
        with open(os.path.join(os.path.dirname(__file__), '../config') + '/devices.json', 'r') as file:
            self.__config = json.load(file)

    def getDevicesConfig(self) -> dict:
        return self.__config["devices"]