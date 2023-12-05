from collections.abc import Callable
from internal.contracts.IDevice import SensorDevice
from typing import Any
import time, json
from internal.contracts.IHttpClient import IHttpClient

class WirelessSensor(SensorDevice):

    def __init__(self, deviceId: int, sourceAddress: str, metadata: dict, httpClient: IHttpClient):
        self.metadata = metadata
        self.devideId = deviceId
        self.sourceAddress = sourceAddress
        self.httpClient = httpClient

    def type(self) -> str:
        return "sensor"

    def getDeviceMetadata(self):
        return self.metadata
    
    def getDeviceId(self) -> int:
        return self.devideId
    
    def streamData(self, callback: Callable[[Any], None]):
        while True:
            try:
                response = self.httpClient.getSession().get(self.sourceAddress)
                if response.status_code == 200:
                    callback(json.loads(response.content.decode()))
            except Exception as e:
                print(f"fetch sensor data error: {e}")
                
            time.sleep(10)
