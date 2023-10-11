from internal.contracts.ICommandManager import ICommandManager, MessageMetadata
from typing import Callable, Any
import re

class CommandManager(ICommandManager):

    __commands: list[dict[str, Any]] = []

    def __init__(self) -> None:
        self.__register_commands()

    def __register_commands(self):
        self.registerCommand("/hello", '', self.hello)

    def receiveMessage(self, message: str):
        
        splittedMsg = message.split(" ")
        command = splittedMsg[0]
        if len(splittedMsg) < 2:
            argument = ""
        else:
            argument = splittedMsg[1]
        
        messageMetadata = MessageMetadata()
        messageMetadata.deviceId = "1"
        messageMetadata.userId = "1"
        messageMetadata.type = ""

        response = self.extractCommandAndArguments(f"{command} {argument}", messageMetadata)
        if isinstance(response, Exception):
            return response
        else:
            return response

    def extractCommandAndArguments(self, messageText: str, messageMetadata: MessageMetadata):
        command_name = messageText.split(" ")[0]
        argument = messageText.split(" ")[1]

        for cmd in self.__commands:
            if cmd["commandName"] == command_name:
                if cmd["parameterPatternMatching"] != "" or cmd["parameterPatternMatching"] is not None:
                    if argument is not None and not re.match(cmd["parameterPatternMatching"], argument):
                        return Exception("Invalid input")
                return cmd["handler"](argument, messageMetadata)

    def registerCommand(self, commandName: str, argumentPatternMatching, handler: Callable):
        self.__commands.append({
            "commandName": commandName,
            "parameterPatternMatching": argumentPatternMatching,
            "handler": handler,
        })

    def hello(self, arg, messageMetadata):
        print(f"successfully running command /hello with arguments {arg}")

        return "success"


