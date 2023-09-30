from internal.modules.IPCamera import *
from internal.modules.USBCamera import *
from internal.modules.VideoProcessor import *
from internal.modules.ModelRegistrar import ModelRegistrar
from internal.modules.DeviceRegistrar import DeviceRegistrar
from internal.registered_models.ObjectDetectorModel import *
import multiprocessing
import string
import time
import requests
import numpy as np
import asyncio
import random

BASE_API_URL = "http://localhost:8080"

lastDetectionTime = time.time()
breakTimeWhenObjectDetected = 15

# #Init OpenCV
videoProcessor = VideoProcessor()

def instantiateDevice(device: dict[str, CameraDevice], videoProcessor: VideoProcessor):

    model = device["assigned_model_class"](videoProcessor)  # type: ignore

    device["device_instance"].streamVideoFrame(lambda frame: videoProcessor.presentInWindow(model.processFrame(frame, 0.5, 0.6, 60, 50, handleOnObjectDetected)))


def handleOnObjectDetected(classLabel, confidence, frame):
    global lastDetectionTime
    currentTime = time.time()

    # Cek apakah sudah 30 detik sejak pemanggilan terakhir
    if currentTime - lastDetectionTime >= breakTimeWhenObjectDetected:

        desc = f"Deteksi objek: {classLabel} dengan kepercayaan {confidence}%"

        print(desc)

        # send notification
        asyncio.run(sendNotification(frame, classLabel, desc))

        # Perbarui waktu terakhir callback dipanggil
        lastDetectionTime = currentTime


async def sendNotification(frame: np.ndarray, ckassLabel: str, description):
    
    data = {
        "title": f"Telah terdeteksi object {ckassLabel}",
        "description": description,
    }

    fileName = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12)) + '.jpeg'

    files = {'image': (fileName, videoProcessor.convertFrameToImage(frame), 'image/jpeg')}

    try:
        response = requests.post(BASE_API_URL + "/notification", data=data, files=files)

        if response.status_code == 200:
            print("Notification sent successfully")
        else:
            print(f"Failed to send notification. Status code: {response.status_code}")
    except:
        print("Error occured")
   
    

def main():

    modelRegistrar = ModelRegistrar()
    modelRegistrar.load()

    deviceRegistar = DeviceRegistrar()
    deviceRegistar.loadCamera(modelRegistrar=modelRegistrar, videoProcessor=videoProcessor)

    processes = []
    for device in deviceRegistar.getDevicesInstance():
        p = multiprocessing.Process(target=instantiateDevice, args=(device,videoProcessor)) #child
        p.daemon = True
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

if __name__ == '__main__':
    main()
