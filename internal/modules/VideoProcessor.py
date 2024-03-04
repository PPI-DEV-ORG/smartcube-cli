import cv2
from internal.contracts.IVideoProcessor import *
from PIL import Image

class VideoProcessor(IVideoProcessor):

    def streamVideoFrameRTSP(self, rtsp: str, callback: Callable[[np.ndarray], None]):
        cap = cv2.VideoCapture(rtsp)
        ct = 0
        while True:
            ct += 1
            ret = cap.grab()
            if ct % 6 == 0: # skip some frames
                ret, frame = cap.retrieve()
                if not ret: break
                callback(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()

    def streamVideoFrameUSB(self, deviceNumber: int, callback: Callable[[np.ndarray], None]):
        cap = cv2.VideoCapture(deviceNumber)
        ct = 0
        while True:
            ct += 1
            ret = cap.grab()
            if ct % 6 == 0: # skip some frames
                ret, frame = cap.retrieve()
                if not ret: break
                callback(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()

    def presentInWindow(self, devideId, frame):
        cv2.imshow(f'Camera {devideId}', frame)
        cv2.waitKey(1)

    def writeText(self, frame: np.ndarray, text: str,  color: typing.Sequence[float], xcoordinate: int, ycoordinate: int):
        cv2.putText(frame, text, (xcoordinate, ycoordinate - 10), cv2.FONT_HERSHEY_PLAIN, 1, color, 2) # type: ignore

    def drawRectangle(self, frame: np.ndarray, bbox: list, color: int):
        cv2.rectangle(frame, bbox[0], bbox[1], color, 2)

    def redraw(self, frame: np.ndarray, bbox: list):
        self.drawRectangle(frame, bbox, 1)
        # self.presentInWindow(frame)
        
    def convertFrameToImage(self, frame: np.ndarray) -> io.BufferedReader:
        frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        # Create an in-memory binary stream
        buffered_stream = io.BytesIO()

        # Save the PIL Image to the binary stream in a specific format (e.g., JPEG)
        frame_pil.save(buffered_stream, format="JPEG")

        buffered_stream.seek(0)

        # Create a BufferedReader from the binary stream
        buffered_reader = io.BufferedReader(buffered_stream) # type: ignore

        # buffered_reader.close()

        return buffered_reader