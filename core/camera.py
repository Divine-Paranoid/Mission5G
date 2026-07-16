import os
import logging
import cv2
import time
from typing import Optional, Tuple
import numpy as np
from config import CameraConfig

os.environ["OPENCV_FFMPEG_LOGLEVEL"] = "-8"

logger = logging.getLogger("SparshCameraManager")

class CameraManager:
    def __init__(self, rtsp_url: str = CameraConfig.RTSP_URL):
        self.rtsp_url = rtsp_url
        self.cap: Optional[cv2.VideoCapture] = None

    def connect(self) -> bool:
        logger.info(f"Production Mode: Opening hardware binding to Sparsh 5G Camera via FFMPEG stream context: {self.rtsp_url}")

        self.cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)

        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            logger.info("Connection established to camera endpoint target successfully.")
            return True
        else:
            logger.critical("Unable to bind camera hardware link over specified network profiles.")
            return False

    def get_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        if self.cap is None or not self.cap.isOpened():
            return False, None

        ret, frame = self.cap.read()
        if not ret or frame is None:
            time.sleep(0.01)
            ret, frame = self.cap.read()

        return ret, frame

    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        return self.get_frame()

    def disconnect(self) -> None:
        if self.cap and self.cap.isOpened():
            self.cap.release()
            logger.info("Sparsh 5G Camera bindings released cleanly.")
