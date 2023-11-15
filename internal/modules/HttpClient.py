import requests, os
from internal.contracts.IHttpClient import IHttpClient
from dotenv import dotenv_values

class HttpClient(IHttpClient):

    __sess = requests.Session()

    def __init__(self):
        self.__sess.headers = {
            "Authorization": "Bearer " + str(dotenv_values(".env")["EDGE_ACCESS_TOKEN"])
        }

    def getSession(self) -> requests.Session:
        return self.__sess
    
    def baseUrl(self) -> str:
        return str(dotenv_values(".env")["SMARTCUBE_API_URL"])