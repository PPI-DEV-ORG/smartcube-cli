import multiprocessing
from internal.modules.IPCamera import *
from internal.modules.USBCamera import *
from internal.modules.VideoProcessor import *
from internal.modules.ObjectDetectorModel import *
import time
import requests
import numpy as np
from concurrent.futures import ThreadPoolExecutor


lastDetectionTime = time.time()
breakTimeWhenObjectDetected = 30 # seconds
BASE_API_URL = "http://localhost:3000"

def detectObject(camera: CameraDevice, videoProcessor: VideoProcessor):
    model = ObjectDetectorModel(videoProcessor)
    camera.streamVideoFrame(lambda frame: videoProcessor.presentInWindow(
        model.processFrame(frame, 0.7, 0.6, 60, 50, handleOnObjectDetected)))

def handleOnObjectDetected(classLabel, confidence, frame):
    global lastDetectionTime
    currentTime = time.time()

    # Cek apakah sudah 30 detik sejak pemanggilan terakhir
    if currentTime - lastDetectionTime >= breakTimeWhenObjectDetected:
        print("frame : ", frame)
        print(f"Deteksi objek: {classLabel} dengan kepercayaan {confidence}%")

        # send notification
        sendNotification(frame)

        # Perbarui waktu terakhir callback dipanggil
        lastDetectionTime = currentTime

def sendNotification(frame: np.ndarray):
    # Membuat ThreadPoolExecutor dengan jumlah thread sesuai kebutuhan
    # Misalnya, kita gunakan 5 thread di sini
    with ThreadPoolExecutor(max_workers=2) as executor:
        # Membuat beberapa tugas untuk mengirim notifikasi
        executor.submit(handleSendNotification, frame)

def handleSendNotification(frame: np.ndarray):
    print("Sending notification...")

    data = {
        "title": "Objek terdeteksi",
        "description": "Objek terdeteksi pada kamera 1",
    }

    files = {
        'image': ('gambar.png', open('1kb.png', 'rb'), 'image/png')
    }

    response = requests.post(BASE_API_URL + "/notification", data=data, files=files)

    # Cek status kode HTTP untuk memastikan permintaan berhasil
    if response.status_code == 200:
        print("Notification sent successfully")
    else:
        print(f"Failed to send notification. Status code: {response.status_code}")


def main():

    #Init OpenCV
    videoProcessor = VideoProcessor() #Parent

    #Init Cameras
    cameras: list[CameraDevice] = [
        # IPCamera("rtsp://192.168.212.254:8080/h264.sdp", {'device_vendor_number': 'MK100212'}, videoProcessor),
        # IPCamera("rtsp://192.168.212.198:8080/h264.sdp", {'device_vendor_number': 'MK100212'}, videoProcessor),
        USBCamera(0, {'device_vendor_number': 'MLL100212'},  videoProcessor)
    ]

    processes = []
    # Spawn Child Process for each device
    for camera in cameras:
        p = multiprocessing.Process(target=detectObject, args=(camera,videoProcessor)) #child
        p.daemon = True
        p.start()
        processes.append(p)

    # Tunggu semua proses selesai
    for p in processes:
        p.join()

if __name__ == '__main__':
    main()
