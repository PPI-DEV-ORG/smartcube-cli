import cv2
import multiprocessing
from internal.modules.IPCamera import *
from internal.modules.USBCamera import *
from internal.modules.VideoProcessor import *
from internal.modules.ObjectDetectorModel import *


def present(frame, bbox):
    cv2.rectangle(frame, bbox[0], bbox[1], (0, 255, 0), 2)
    cv2.imshow(f'Camera [x]', frame)


def main():

    #Init Detection Model
    objectDetectorModel = ObjectDetectorModel()

    #Init OpenCV
    videoProcessor = VideoProcessor()

    #Init Cameras
    cameras = [
        IPCamera("rtsp://192.168.212.254:8080/h264.sdp", {'device_vendor_number': 'MK100212'}, videoProcessor),
        USBCamera(0, {'device_vendor_number': 'MLL100212'}, videoProcessor)
    ]

    # Mulai proses pemrosesan untuk setiap kamera
    processes = []
    for camera in cameras:
        p = multiprocessing.Process(
            target=camera.streamVideoFrame, 
            args=((lambda frame: objectDetectorModel.processFrame(frame, present)),))
        p.start()
        processes.append(p)

    # Tunggu semua proses selesai
    for p in processes:
        p.join()
   
if __name__ == '__main__':
    main()


