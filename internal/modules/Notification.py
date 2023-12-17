import time
import asyncio
import random
import string
import numpy as np
from internal.contracts.IVideoProcessor import IVideoProcessor
from internal.contracts.INotification import INotification
from internal.contracts.IHttpClient import IHttpClient
from internal.helper.helper import getTimeNow

class Notification(INotification):

    __videoProcessor: IVideoProcessor
    __httpClient: IHttpClient

    __lastDetectionTime = time.time()
    __breakTimeWhenObjectDetected = 15

    def __init__(self, videoProcessor: IVideoProcessor, httpClient: IHttpClient) -> None:
        self.__videoProcessor = videoProcessor
        self.__httpClient = httpClient

    def handleOnObjectDetected(self, deviceId: int, classLabel: str, confidence: int, frame: np.ndarray):
        currentTime = time.time()
        if currentTime - self.__lastDetectionTime >= self.__breakTimeWhenObjectDetected:
            data = {
                "device_id": deviceId,
                "title": f"Telah terdeteksi object {classLabel}",
                "description": f"Object {classLabel} terdeteksi dengan kepercayaan {confidence}% pada pukul {getTimeNow(format='%Y-%m-%d')}",
                "device_type": "camera",
                "object_label": classLabel,
                "risk_level": "test"
            }
            fileName = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12)) + '.jpeg'
            files = {'image': (fileName, self.__videoProcessor.convertFrameToImage(frame), 'image/jpeg')}

            asyncio.run(self.storeNotificationWithFile(data=data, files=files))

            self.__lastDetectionTime = currentTime

    def onThresholdExceeded(self, deviceId: int, riskLevel: str):
        currentTime = time.time()
        if currentTime - self.__lastDetectionTime >= self.__breakTimeWhenObjectDetected:
            data = {
                "device_id": deviceId,
                "title": f"Berpotensi adanya kebakaran",
                "description": f"Berpotensi adanya kebakaran",
                "device_type": "sensor",
                "risk_level": riskLevel,
            }

            asyncio.run(self.storeNotification(data=data))

            self.__lastDetectionTime = currentTime

    async def storeNotificationWithFile(self, data: dict, files: dict):
        try:
            response = self.__httpClient.getSession().post(
                url=f"{self.__httpClient.baseUrl()}/notification",
                data=data,
                files=files,
            )

            if response.status_code == 200:
                print("notification sent successfully")
            else:
                print(
                    f"failed to send notification. Status code: {response.text}")
                
        except Exception as e:
            print("send Notification error occured", e)

    async def storeNotification(self, data: dict):
        try:
            response = self.__httpClient.getSession().post(
                url=f"{self.__httpClient.baseUrl()}/notification",
                data=data,
            )

            if response.status_code == 200:
                print("notification sent successfully")
            else:
                print(
                    f"failed to send notification: {response.text}")
                
        except Exception as e:
            print("send Notification error occured", e)
