from collections.abc import Callable
from internal.contracts.IDevice import CameraDevice
from internal.contracts.IVideoProcessor import *

class USBCamera(CameraDevice):

    def __init__(self, deviceNumber: int, metadata: dict, videoProcessor: IVideoProcessor):
        self.metadata = metadata
        self.deviceNumber = deviceNumber
        self.videoProcessor = videoProcessor

    def getDeviceMetadata(self):
        return self.metadata

    def streamVideoFrame(self, callback: Callable[[np.ndarray], None]):
        self.videoProcessor.streamVideoFrameUSB(self.deviceNumber, callback)