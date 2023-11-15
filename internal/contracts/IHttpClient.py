from abc import ABC, abstractmethod
import requests

class IHttpClient(ABC):

    @abstractmethod
    def getSession(self) -> requests.Session:
        pass

    @abstractmethod
    def baseUrl(self) -> str:
        pass