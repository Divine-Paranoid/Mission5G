"""
core/camera.py - Production Video Ingestion for Sparsh 5G Bullet Camera with Local Simulation Backend Auto-Switching.
Source of Truth: DoT 100 5G Labs Architecture Manuals.
"""
import logging
import cv2
import numpy as np
from typing import Tuple, Optional
from config import CameraConfig

logger = logging.getLogger("SparshCameraManager")

class CameraManager:
    def __init__(self, rtsp_url=CameraConfig.RTSP_URL):
        self.rtsp_url = rtsp_url
        self._cap: Optional[cv2.VideoCapture] = None

    def connect(self) -> bool:
        try:
            # Safely handle string-represented integers from bypass configs
            actual_source = self.rtsp_url
            if isinstance(actual_source, str) and actual_source.isdigit():
                actual_source = int(actual_source)

            # --- SMART BACKEND AUTO-SWITCHING ---
            if isinstance(actual_source, int):
                logger.info(f"Bypass Triggered: Opening local hardware camera device [{actual_source}] via native OS video APIs.")
                # Use default/DirectShow backend for integrated/USB hardware cameras on Windows
                self._cap = cv2.VideoCapture(actual_source)
            else:
                logger.info(f"Production Mode: Opening hardware binding to Sparsh 5G Camera via FFMPEG stream context: {actual_source}")
                # Use FFMPEG backend for network RTSP streams exclusively
                self._cap = cv2.VideoCapture(actual_source, cv2.CAP_FFMPEG)
            # -------------------------------------

            # Low-latency optimization buffer hooks
            if self._cap is not None:
                self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)

            if not self._cap or not self._cap.isOpened():
                logger.error("Failed to connect to target Sparsh camera feed buffer link.")
                return False
                
            logger.info("Connection established to camera endpoint target successfully.")
            return True
            
        except Exception as e:
            logger.exception(f"Critical exception encountered opening camera channel: {e}")
            return False

    def is_connected(self) -> bool:
        return self._cap is not None and self._cap.isOpened()

    def get_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        if not self.is_connected():
            return False, None
        try:
            assert self._cap is not None
            ret, frame = self._cap.read()
            if not ret or frame is None:
                return False, None
            return True, frame
        except Exception as e:
            logger.error(f"Error extracting frame from streaming buffer matrix: {e}")
            return False, None

    def release(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None
            logger.info("Released camera hardware context resource handles safely.")

    def __enter__(self) -> "CameraManager":
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.release()