import multiprocessing
import string
from internal.modules.IPCamera import *
from internal.modules.USBCamera import *
from internal.modules.VideoProcessor import *
from internal.modules.ObjectDetectorModel import *
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

def detectObject(camera: CameraDevice, videoProcessor: VideoProcessor):
    model = ObjectDetectorModel(videoProcessor)
    camera.streamVideoFrame(lambda frame: videoProcessor.presentInWindow(model.processFrame(frame, 0.5, 0.6, 60, 50, handleOnObjectDetected)))


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

    response = requests.post(BASE_API_URL + "/notification", data=data, files=files)

    if response.status_code == 200:
        print("Notification sent successfully")
    else:
        print(f"Failed to send notification. Status code: {response.status_code}")
    

def main():

    #Init Cameras
    cameras: list[CameraDevice] = [
        # IPCamera("rtsp://192.168.212.254:8080/h264.sdp", {'device_vendor_number': 'MK100212'}, videoProcessor),
        # IPCamera("rtsp://192.168.212.198:8080/h264.sdp", {'device_vendor_number': 'MK100212'}, videoProcessor),
        USBCamera(0, {'device_vendor_number': 'MLL100212'},  videoProcessor)
    ]

    processes = []
    for camera in cameras:
        p = multiprocessing.Process(target=detectObject, args=(camera,videoProcessor)) #child
        p.daemon = True
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

if __name__ == '__main__':
    main()
