import logging
from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np
import torch
from ultralytics import YOLO
from config import DetectorConfig

logger = logging.getLogger("VVDN_ObjectDetector")

@dataclass(frozen=True)
class DetectionResult:
    labels: List[str]
    confidences: np.ndarray
    bounding_boxes: np.ndarray

class ObjectDetector:
    def __init__(self, model_path: str = DetectorConfig.MODEL_PATH, default_conf: float = DetectorConfig.CONFIDENCE_THRESHOLD):
        self.model_path = model_path
        self.default_conf = default_conf
        self._model: Optional[YOLO] = None
        self._load_model()

    def _load_model(self) -> None:
        logger.info(f"Loading YOLO framework onto memory matrix path: {self.model_path}")
        try:
            original_torch_load = torch.load

            def safe_torch_load(*args, **kwargs):
                kwargs['weights_only'] = False
                return original_torch_load(*args, **kwargs)

            torch.load = safe_torch_load
            self._model = YOLO(self.model_path)

            torch.load = original_torch_load
            logger.info("YOLO Engine locked successfully.")

        except Exception as e:
            logger.critical(f"Inference engine failed to mount weight allocation: {e}")
            raise RuntimeError(f"Initialization failure on target model weights: {e}") from e

    def detect(self, frame: np.ndarray) -> Tuple[DetectionResult, np.ndarray]:
        if self._model is None:
            raise RuntimeError("Model layout unallocated.")
        try:
            results = self._model.predict(source=frame, conf=self.default_conf, verbose=False)
            img_results = results[0]

            boxes_data = img_results.boxes.xyxy.cpu().numpy()
            confs_data = img_results.boxes.conf.cpu().numpy()
            classes_data = img_results.boxes.cls.cpu().numpy()

            parsed_labels = [self._model.names[int(cls_idx)] for cls_idx in classes_data]

            dto = DetectionResult(
                labels=parsed_labels,
                confidences=confs_data,
                bounding_boxes=boxes_data
            )
            return dto, img_results.plot()
        except Exception as e:
            logger.error(f"Inference cycle execution error scenario: {e}")
            return DetectionResult([], np.empty(0), np.empty((0, 4))), frame
