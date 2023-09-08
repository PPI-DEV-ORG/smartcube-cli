import cv2

from internal.contracts.IVideoProcessor import *
from internal.contracts.IObjectDetectorModel import *
from internal.modules.ObjectDetectorModel import *

class VideoProcessor(IVideoProcessor):

    def streamVideoFrameRTSP(self, rtsp: str, callback: Callable[[np.ndarray], None]):
        cap = cv2.VideoCapture(rtsp)
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            callback(frame)
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()

    def streamVideoFrameUSB(self, deviceNumber: int, callback: Callable[[np.ndarray], None]):
        cap = cv2.VideoCapture(deviceNumber)
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            callback(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()

    def presentInWindow(self, frame):
        cv2.imshow(f'Camera [x]', frame)

    def writeText(self, frame: np.ndarray, text: str,  color: typing.Sequence[float], xcoordinate: int, ycoordinate: int):
        cv2.putText(frame, text, (xcoordinate, ycoordinate - 10), cv2.FONT_HERSHEY_PLAIN, 1, color, 2) # type: ignore

    def drawRectangle(self, frame: np.ndarray, bbox: list, color: int):
        cv2.rectangle(frame, bbox[0], bbox[1], color, 2)

    def redraw(self, frame: np.ndarray, bbox: list):
        self.drawRectangle(frame, bbox, 1)
        self.presentInWindow(frame)
        