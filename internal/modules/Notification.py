import time
import asyncio
import random
import string
import numpy as np
from internal.contracts.IVideoProcessor import IVideoProcessor
from internal.contracts.INotification import INotification
from internal.contracts.IHttpClient import IHttpClient

class Notification(INotification):

    __videoProcessor: IVideoProcessor
    __httpClient: IHttpClient

    __lastDetectionTime = time.time()
    __breakTimeWhenObjectDetected = 15

    def __init__(self, videoProcessor: IVideoProcessor, httpClient: IHttpClient) -> None:
        self.__videoProcessor = videoProcessor
        self.__httpClient = httpClient

    def handleOnObjectDetected(self, classLabel, confidence, frame):
        currentTime = time.time()

        if currentTime - self.__lastDetectionTime >= self.__breakTimeWhenObjectDetected:

            desc = f"Object {classLabel} terdeteksi dengan kepercayaan {confidence}% pada pukul {currentTime}"

            asyncio.run(self.sendNotification(frame, classLabel, desc))

            self.__lastDetectionTime = currentTime

    async def sendNotification(self, frame: np.ndarray, classLabel: str, description):

        data = {
            "title": f"Telah terdeteksi object {classLabel}",
            "description": description,
        }
        fileName = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12)) + '.jpeg'
        files = {'image': (fileName, self.__videoProcessor.convertFrameToImage(frame), 'image/jpeg')}

        try:
            response = self.__httpClient.getSession().post(
                url=f"{self.__httpClient.baseUrl()}/notification",
                data=data,
                files=files,
            )

            if response.status_code == 200:
                print("Notification sent successfully")
            else:
                print(
                    f"Failed to send notification. Status code: {response.status_code}")
                
        except Exception as e:
            print("Send Notification error occured", e)
