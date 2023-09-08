from collections.abc import Callable

from internal.contracts.IDevice import CameraDevice
from internal.contracts.IVideoProcessor import *

class IPCamera(CameraDevice):

    def __init__(self, rtsp: str, metadata: dict, videoProcessor: IVideoProcessor):
        self.metadata = metadata
        self.rtsp = rtsp
        self.videoProcessor = videoProcessor

    def getDeviceMetadata(self):
        return self.metadata

    def streamVideoFrame(self, callback: Callable[[np.ndarray], None]):
        self.videoProcessor.streamVideoFrameRTSP(self.rtsp, callback)