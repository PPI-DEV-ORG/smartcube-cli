import multiprocessing
from internal.modules.IPCamera import *
from internal.modules.USBCamera import *
from internal.modules.VideoProcessor import *
from internal.modules.ObjectDetectorModel import *
import time

lastDetectionTime = time.time()
breakTimeWhenObjectDetected = 30 # seconds

def detectObject(camera: CameraDevice, videoProcessor: VideoProcessor):
    model = ObjectDetectorModel(videoProcessor, 0.5, 0.5, 60, 50, handleOnObjectDetected)
    camera.streamVideoFrame(lambda frame: videoProcessor.presentInWindow(model.processFrame(frame)))

def handleOnObjectDetected(classLabel, confidence, frame):
    global lastDetectionTime
    currentTime = time.time()

    # Cek apakah sudah 30 detik sejak pemanggilan terakhir
    if currentTime - lastDetectionTime >= breakTimeWhenObjectDetected:
        print("frame : ", frame)
        print(f"Deteksi objek: {classLabel} dengan kepercayaan {confidence}%")

        # Perbarui waktu terakhir callback dipanggil
        lastDetectionTime = currentTime

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
