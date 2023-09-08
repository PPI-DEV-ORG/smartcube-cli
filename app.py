import multiprocessing
from internal.modules.IPCamera import *
from internal.modules.USBCamera import *
from internal.modules.VideoProcessor import *
from internal.modules.ObjectDetectorModel import *
 
def detectObject(camera: CameraDevice, videoProcessor: VideoProcessor):
    model = ObjectDetectorModel(videoProcessor)
    camera.streamVideoFrame(lambda frame: videoProcessor.presentInWindow(model.processFrame(frame)))

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


