from internal.contracts.IObjectDetectorModel import IObjectDetectorModel
from internal.contracts.IVideoProcessor import IVideoProcessor
from collections.abc import Callable
from tflite_support.task import core
from tflite_support.task import processor
from tflite_support.task import vision
from typing import Any
from tensorflow.python.keras.utils.data_utils import get_file
import os

import numpy as np

_MARGIN = 15  # pixels
_ROW_SIZE = 10  # pixels
_FONT_SIZE = 1
_FONT_THICKNESS = 1
_TEXT_COLOR = (0, 0, 255)  # red

class ModelLoader_Visual_FireSmokeDetector(IObjectDetectorModel):

    __detector: vision.ObjectDetector
    __videoProcessor: IVideoProcessor
    __confidence: int
    __model_path: str

    __score_threshold: float
    __onDetected: Callable[[str, int, np.ndarray], None]

    def __init__(self, videoProcessor: IVideoProcessor) -> None:
        self.cacheDir = "./pretrained_models"
        self.__videoProcessor = videoProcessor
        self.__model_path = "./pretrained_models/firesmoke_detector_daylight/model.tflite"
        self.__downloadModel("https://storage.googleapis.com/smartcube-bucket/smartcube_models/firesmoke_detector_daylight.zip")
        self.__loadModel()

    @staticmethod
    def getModelType() -> str:
        return "objectDetection"
    
    def getModelVersion(self) -> str:
        return "firesmoke_detector_daylight@v1.0.0"
    
    @staticmethod
    def getModelMetadata() -> dict[str, Any]:
        return {
            "model_name": "firesmoke_detector_ssd_mobilenet_v2_fpnlite",
            "version": "v2.0.0",
            "smcb_wrapper_version": "v1.0.0",
        }

    def inferenceFrame(
        self, 
        frame: np.ndarray, 
        iou_threshold: float = 0.5,
        score_threshold: float = 0.7,
        confidence: int = 50,
        max_output_size: int = 50,
        onDetected: Callable[[str, int, np.ndarray], None] = lambda classLabel, confidence, frame: None
    ) -> np.ndarray:
    
        self.__score_threshold = score_threshold
        self.__confidence = confidence
        self.__onDetected = onDetected
        self.__max_output = max_output_size

        return self.__detectObject(frame)

    def __downloadModel(self, modelUrl):

        fileName = os.path.basename(modelUrl)

        os.makedirs(self.cacheDir, exist_ok=True)

        get_file(fname=fileName, origin=modelUrl, cache_dir=self.cacheDir,
                 cache_subdir="", extract=True)
        
    def __loadModel(self):

        # Initialize the object detection model
        base_options = core.BaseOptions(file_name=self.__model_path, use_coral=False, num_threads=1)
        detection_options = processor.DetectionOptions(max_results=50, score_threshold=0.7)
        options = vision.ObjectDetectorOptions(base_options=base_options, detection_options=detection_options)
        self.__detector = vision.ObjectDetector.create_from_options(options)
        
        print("Model " + self.getModelMetadata()['model_name'] + " loaded successfully...")

    def __detectObject(self, frame: np.ndarray) -> np.ndarray:
        # Create a TensorImage object from the RGB image.
        input_tensor = vision.TensorImage.create_from_array(frame)

        # Run object detection estimation using the model.
        detection_result = self.__detector.detect(input_tensor)

        probability = 0
        category_name = ""

        for detection in detection_result.detections:
            # Draw bounding_box
            bbox = detection.bounding_box
            start_point = bbox.origin_x, bbox.origin_y
            end_point = bbox.origin_x + bbox.width, bbox.origin_y + bbox.height

            # Draw label and score
            category = detection.categories[0]
            category_name = category.category_name
            probability = round(category.score, 2)
            result_text = category_name + ' (' + str(probability) + ')'
            
            self.__videoProcessor.writeText(frame, result_text, _TEXT_COLOR, _MARGIN + bbox.origin_x, _MARGIN + _ROW_SIZE + bbox.origin_y) # type: ignore
            self.__videoProcessor.drawRectangle(frame=frame, bbox=[(start_point), (end_point)], color=_TEXT_COLOR)  # type: ignore

        # print(probability, self.__confidence / 100.0, probability > (self.__confidence / 100.0))
        if (probability > (self.__confidence / 100.0)):
            self.__onDetected(category_name, int(probability * 100), frame) 

        return frame