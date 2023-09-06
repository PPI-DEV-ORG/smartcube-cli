from internal.contracts.IObjectDetectorModel import *

class ObjectDetectorModel(IObjectDetectorModel):

    def processFrame(self, frame: np.ndarray, callback: Callable[[np.ndarray, list], None]):
        height, width, _ = frame.shape
        center_x, center_y = width // 2, height // 2
        callback(frame, [(center_x - 50, center_y - 50), (center_x + 50, center_y + 50)])