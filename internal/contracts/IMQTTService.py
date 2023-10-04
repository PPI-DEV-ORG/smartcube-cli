from abc import ABC, abstractmethod
from typing import Callable

class IMQTTService(ABC):

    @abstractmethod
    def connectMqtt(self):
        pass
    
    @abstractmethod
    def subscribe(self, client, callback):
        pass

    @abstractmethod
    def run(self, callback: Callable):
        pass