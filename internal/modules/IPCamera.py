from collections.abc import Callable
from internal.contracts.IDevice import CameraDevice
from internal.contracts.IVideoProcessor import *

class IPCamera(CameraDevice):

    def __init__(self, deviedeId: int, rtsp: str, metadata: dict, videoProcessor: IVideoProcessor):
        self.metadata = metadata
        self.rtsp = rtsp
        self.devideId = deviedeId
        self.videoProcessor = videoProcessor

    def type(self) -> str:
        return "camera"

    def getDeviceMetadata(self):
        return self.metadata
    
    def getDeviceId(self) -> int:
        return self.devideId

    def streamVideoFrame(self, callback: Callable[[np.ndarray], None]):
        self.videoProcessor.streamVideoFrameRTSP(self.rtsp, callback)