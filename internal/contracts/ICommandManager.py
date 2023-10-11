from abc import ABC, abstractmethod

class MessageMetadata:
    type: str
    deviceId: str
    userId: str

class ICommandManager(ABC):

    @abstractmethod
    def receiveMessage(self, message: str):
        pass

    @abstractmethod
    def extractCommandAndArguments(self, messageText: str, messageMetadata: MessageMetadata):
        pass

    @abstractmethod
    def registerCommand(self, commandName, argumentPatternMatching, handler):
        pass