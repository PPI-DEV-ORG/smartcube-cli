import time, asyncio, random, string, requests
import numpy as np
from internal.contracts.IVideoProcessor import IVideoProcessor
from internal.contracts.INotification import INotification

class Notification(INotification):
    
    BASE_API_URL = "http://localhost:8080"

    lastDetectionTime = time.time()
    breakTimeWhenObjectDetected = 15
    videoProcessor: IVideoProcessor

    def __init__(self, videoProcessor: IVideoProcessor) -> None:
        self.videoProcessor = videoProcessor

    def handleOnObjectDetected(self, classLabel, confidence, frame):
        currentTime = time.time()

        # Cek apakah sudah 30 detik sejak pemanggilan terakhir
        if currentTime - self.lastDetectionTime >= self.breakTimeWhenObjectDetected:

            desc = f"Deteksi objek: {classLabel} dengan kepercayaan {confidence}%"

            print(desc)

            # send notification
            asyncio.run(self.sendNotification(frame, classLabel, desc))

            # Perbarui waktu terakhir callback dipanggil
            self.lastDetectionTime = currentTime

    async def sendNotification(self, frame: np.ndarray, classLabel: str, description):
    
        data = {
            "title": f"Telah terdeteksi object {classLabel}",
            "description": description,
        }

        fileName = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12)) + '.jpeg'

        files = {'image': (fileName, self.videoProcessor.convertFrameToImage(frame), 'image/jpeg')}

        try:
            response = requests.post(self.BASE_API_URL + "/notification", data=data, files=files)

            if response.status_code == 200:
                print("Notification sent successfully")
            else:
                print(f"Failed to send notification. Status code: {response.status_code}")
        except:
            print("Error occured")
   