from internal.contracts.IObjectDetectorModel import *
from internal.contracts.IVideoProcessor import IVideoProcessor
from tensorflow.python.keras.utils.data_utils import get_file
import time, os, tensorflow as tf

np.random.seed(123)

class ObjectDetectorModel(IObjectDetectorModel):

    def __init__(self, videoProcessor: IVideoProcessor):
        self.cacheDir = "./pretrained_models"
        self.modelName = "ssd_mobilenet_v2_320x320_coco17_tpu-8"
        self.colorList: np.ndarray
        self.classesList: list[str]
        self.model = None
        self.videoProcessor = videoProcessor
        self.__readClasses("coco.names")
        self.__downloadModel("http://download.tensorflow.org/models/object_detection/tf2/20200711/ssd_mobilenet_v2_320x320_coco17_tpu-8.tar.gz")
        self.__loadTensorModel()

    def processFrame(self, frame: np.ndarray) -> np.ndarray: 
        return self.__detectObject(frame)
       
    def __downloadModel(self, modelUrl):

        fileName = os.path.basename(modelUrl)
        self.modelName = fileName[:fileName.index('.')]

        os.makedirs(self.cacheDir, exist_ok=True)

        get_file(fname=fileName, origin=modelUrl, cache_dir=self.cacheDir,
                 cache_subdir="checkpoints", extract=True)
        
    def __readClasses(self, classesFilePath):
        with open(classesFilePath, 'r') as f:
            self.classesList = f.read().splitlines()
        self.colorList = np.random.uniform(low=0, high=255, size=(len(self.classesList), 3))

    def __loadTensorModel(self):
        tf.keras.backend.clear_session()
        self.model = tf.saved_model.load(os.path.join(self.cacheDir, "checkpoints", self.modelName, "saved_model"))

        print("Model " + self.modelName + " loaded successfully...")

    def __detectObject(self, frame: np.ndarray) -> np.ndarray:

        inputTensor = tf.convert_to_tensor(frame, dtype=tf.uint8)
        inputTensor = inputTensor[tf.newaxis, ...]

        detections = self.model(inputTensor)  # type: ignore

        bboxs = detections['detection_boxes'][0].numpy()
        classIndexes = detections['detection_classes'][0].numpy().astype(np.int32)
        classScores = detections['detection_scores'][0].numpy()

        imH, imW, imC = frame.shape

        bboxIdx = tf.image.non_max_suppression(bboxs, classScores, max_output_size=50,
        iou_threshold=0.5, score_threshold=0.5)

        if len(bboxIdx) != 0:
            for i in bboxIdx:

                bbox = tuple(bboxs[i].tolist())
                classConfidence = round(100*classScores[i])
                classIndex = classIndexes[i]

                classLabelText = self.classesList[classIndex]
                classColor = self.colorList[classIndex]

                displayText = '{}: {}%'.format(classLabelText, classConfidence)

                ymin, xmin, ymax, xmax = bbox

                xmin, xmax, ymin, ymax = (xmin * imW, xmax * imW, ymin * imH, ymax * imH)
                xmin, xmax, ymin, ymax = int(xmin), int(xmax), int(ymin), int(ymax)

                self.videoProcessor.writeText(frame, displayText, classColor, xmin, ymin) # type: ignore
                self.videoProcessor.drawRectangle(frame, [(xmin, ymin), (xmax, ymax)], classColor) # type: ignore

        return frame