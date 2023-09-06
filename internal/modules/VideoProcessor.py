import cv2

from internal.contracts.IVideoProcessor import *

class VideoProcessor(IVideoProcessor):

    def streamVideoFrameRTSP(self, rtsp: str, callbackFrame):
        cap = cv2.VideoCapture(rtsp)
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            callbackFrame(frame)
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()

    def streamVideoFrameUSB(self, deviceNumber: int, callbackFrame):
        cap = cv2.VideoCapture(deviceNumber)
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            callbackFrame(frame)
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()

    def presentInWindow(self, frame):
        cv2.imshow(f'Camera [x]', frame)

    def drawRectangle(self, frame: np.ndarray, bbox: list):
        cv2.rectangle(frame, bbox[0], bbox[1], (0, 255, 0), 2)

    def redraw(self, frame: np.ndarray, bbox: list):
        self.drawRectangle(frame, bbox)
        self.presentInWindow(frame)