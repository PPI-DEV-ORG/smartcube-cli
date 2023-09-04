from abc import ABC, abstractmethod
import cv2
import numpy as np
import multiprocessing


#Video Frame Reader Abstractions
class VideoProcessor(ABC): #Interfaces
    
    @abstractmethod
    def streamVideoFrameRTSP(self, rtsp: str, callback_frame):
        pass

    @abstractmethod
    def drawRectangle(self, frame, bbox):
        pass

    @abstractmethod
    def presentInWindow(self, frame):
        pass

    @abstractmethod
    def redraw(self, frame, bbox):
        pass

class OpenCV_VideoProcessor(VideoProcessor):

    def streamVideoFrameRTSP(self, rtsp: str, callback_frame):
        cap = cv2.VideoCapture(rtsp)
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            callback_frame(frame)
                
            # Tekan 'q' untuk keluar dari loop
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()

    def presentInWindow(self, frame):
        # Tampilkan frame yang telah diproses
        cv2.imshow(f'Camera [x]', frame)

    def drawRectangle(self, frame, bbox):
        cv2.rectangle(frame, bbox[0], bbox[1], (0, 255, 0), 2)

    def redraw(self, frame, bbox):
        self.drawRectangle(frame, bbox)
        self.presentInWindow(frame)

# Object Detection Model Abstraction
class ObjectDetectorModel(ABC): #Interfaces

    @abstractmethod
    def processFrame(self, frame):
        pass

class CNN_Model_v1(ObjectDetectorModel):
    def processFrame(self, frame, callback):
        height, width, _ = frame.shape
        center_x, center_y = width // 2, height // 2
        callback(frame, [(center_x - 50, center_y - 50), (center_x + 50, center_y + 50)])


# Device Hardware Abstractions
class Device(ABC): #Interfaces
    
    @abstractmethod
    def getDeviceMetadata(self):
        pass

class CameraDevice(Device):

    @abstractmethod
    def streamVideoFrame(self, callback_frame):
        pass

class IPCamera(CameraDevice):

    def __init__(self, rtsp: str, metadata: dict, videoProcessor: VideoProcessor):
        self.metadata = metadata
        self.rtsp = rtsp
        self.videoProcessor = videoProcessor

    def getDeviceMetadata(self):
        return self.metadata

    def streamVideoFrame(self, callback_frame):
        self.videoProcessor.streamVideoFrameRTSP(self.rtsp, callback_frame)


def present(frame, bbox):
    cv2.rectangle(frame, bbox[0], bbox[1], (0, 255, 0), 2)
    cv2.imshow(f'Camera [x]', frame)


def main():

    # Init CNN
    objectDetectorModel = CNN_Model_v1()

    # Init OpenCV
    videoProcessor = OpenCV_VideoProcessor()

    #RTSP
    # camera_ids = [
    # 'rtsp://192.168.215.211:8080/h264.sdp', 
    # 'rtsp://192.168.215.214:8081/h264.sdp', 
    # 'rtsp://192.168.215.219:8080/h264.sdp']
    # camera_ids = [0]

    #Init IP Camera
    cameras = [
        IPCamera(0, {'ipAddress': '192.168.0.1'}, videoProcessor),
        IPCamera(1, {'ipAddress': '192.168.0.1'}, videoProcessor),
        IPCamera(2, {'ipAddress': '192.168.0.1'}, videoProcessor),
        IPCamera(3, {'ipAddress': '192.168.0.1'}, videoProcessor),
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


