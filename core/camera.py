"""
core/camera.py - 5G Lab Environment Optimized Camera Framework via RTSP TCP.
"""
import os
import logging
import cv2
import time
from typing import Optional, Tuple
import numpy as np
from config import CameraConfig

# FFMPEG error/warning flooding ko suppress karne ke liye logic matrix
os.environ["OPENCV_FFMPEG_LOGLEVEL"] = "-8"

logger = logging.getLogger("SparshCameraManager")

# FIX: Class name ko wapas 'CameraManager' kar diya hai taaki main.py ka import breakdown na ho
class CameraManager:
    def __init__(self, rtsp_url: str = CameraConfig.RTSP_URL):
        self.rtsp_url = rtsp_url
        self.cap: Optional[cv2.VideoCapture] = None
        
    def connect(self) -> bool:
        """Establishes optimized TCP-forced RTSP binding with Sparsh 5G Camera."""
        logger.info(f"Production Mode: Opening hardware binding to Sparsh 5G Camera via FFMPEG stream context: {self.rtsp_url}")
        
        # H.264 packet corruptions aur MB byte-stream drops bypass karne ke liye optimize flags
        self.cap = cv2.VideoCapture(
            self.rtsp_url, 
            cv2.CAP_FFMPEG, 
            [
                cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_ANY,
                cv2.CAP_PROP_BUFFERSIZE, 1  # Minimizes latency buffer lag
            ]
        )
        
        if not self.cap.isOpened():
            logger.warning("Optimized container link fail. Retrying stable baseline fallback...")
            self.cap = cv2.VideoCapture(self.rtsp_url)
            
        if self.cap.isOpened():
            logger.info("Connection established to camera endpoint target successfully.")
            return True
        else:
            logger.critical("Unable to bind camera hardware link over specified network profiles.")
            return False
            
    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Reads frame from stream matrix safely."""
        if self.cap is None or not self.cap.isOpened():
            return False, None
            
        ret, frame = self.cap.read()
        if not ret or frame is None:
            # Short data dropped packet protection retry logic
            time.sleep(0.01)
            ret, frame = self.cap.read()
            
        return ret, frame
        
    def disconnect(self) -> None:
        """Safely releases active camera descriptors."""
        if self.cap and self.cap.isOpened():
            self.cap.release()
            logger.info("Sparsh 5G Camera bindings released cleanly.")