import cv2
from internal.contracts.IVideoProcessor import *
from PIL import Image

class VideoProcessor(IVideoProcessor):

    def openStream(self, url):
        cap = cv2.VideoCapture(url)
        if not cap.isOpened():
            print("Error: Could not open stream.")
            return None
        return cap

    def streamVideoFrameRTSP(self, rtsp: str, callback: Callable[[np.ndarray], None]):
        cap = self.openStream(rtsp)
        isStreaming = True
        ct = 0

        while True:
            if isStreaming:
                while True:
                    try:
                        if cap is None:
                            isStreaming = False
                            break

                        ct += 1
                        ret = cap.grab()
                        if not ret: 
                            print("Error: Failed to read frame.")
                            isStreaming = False
                            break

                        if ct % 4 == 0: # skip some frames
                            ret, frame = cap.retrieve()
                            callback(frame)

                    except Exception as e:
                        print("Error:", e)
                        isStreaming = False
                        break

            # Attempt to reconnect
            while not isStreaming:
                    print("Attempting to reconnect...")
                    
                    cap = self.openStream(rtsp)
                    if cap is not None:
                        isStreaming = True
                        print("Reconnected!")
                    else:
                        # Delay before attempting to reconnect
                        cv2.waitKey(3000) # 3 seconds delay before retrying`

    def streamVideoFrameUSB(self, deviceNumber: int, callback: Callable[[np.ndarray], None]):
        cap = cv2.VideoCapture(deviceNumber)
        ct = 0
        while True:
            ct += 1
            ret = cap.grab()
            if ct % 2 == 0: # skip some frames
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