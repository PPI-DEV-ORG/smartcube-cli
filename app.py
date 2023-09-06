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

    # Init Detection Model
    objectDetectorModel = ObjectDetectorModel()

    # Init OpenCV
    videoProcessor = VideoProcessor()

    #RTSP
    # camera_ids = [
    # 'rtsp://192.168.215.211:8080/h264.sdp', 
    # 'rtsp://192.168.215.214:8081/h264.sdp', 
    # 'rtsp://192.168.215.219:8080/h264.sdp']
    # camera_ids = [0]

    #Init IP Camera
    cameras = [
        IPCamera("rtsp://192.168.212.254:8080/h264.sdp", {'device_vendor_number': 'MK100212'}, videoProcessor),
        # IPCamera(1, {'device_vendor_number': 'MK100212'}, videoProcessor),
        # IPCamera(2, {'device_vendor_number': 'MK100212'}, videoProcessor),
        # IPCamera(3, {'device_vendor_number': 'MK100212'}, videoProcessor),

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


