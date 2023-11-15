from abc import ABC, abstractmethod
from typing import Callable

class IMQTTService(ABC):

    @abstractmethod
    def connect(self):
        pass
    
    @abstractmethod
    def subscribe(self, callback):
        pass

    @abstractmethod
    def publish(self, message: str):
        pass

    @abstractmethod
    def run(self, callback: Callable):
        pass