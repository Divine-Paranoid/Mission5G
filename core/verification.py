import logging
from enum import Enum
from typing import List
from config import FusionConfig

logger = logging.getLogger("VVDN_FusionEngine")

class VerificationState(Enum):
    VERIFIED = "VERIFIED"
    NOT_VERIFIED = "NOT_VERIFIED"
    NEED_MORE_INFORMATION = "NEED_MORE_INFORMATION"

class RuleBasedVerification:
    def __init__(self, require_match: bool = FusionConfig.REQUIRE_EXACT_CLASS_MATCH, conf_thresh: float = FusionConfig.DRONE_MIN_CONFIDENCE):
        self.require_match = require_match
        self.conf_thresh = conf_thresh

    def evaluate(self, camera_labels: List[str], drone_labels: List[str], drone_confs: List[float]) -> VerificationState:
        try:
            # Case 1: Ground system tracks anomaly, but Drone hasn't arrived/finished streaming yet
            if len(camera_labels) > 0 and len(drone_labels) == 0:
                return VerificationState.NEED_MORE_INFORMATION

            # Case 2: Neither sensor architecture tracks anomalies
            if len(camera_labels) == 0 and len(drone_labels) == 0:
                return VerificationState.NOT_VERIFIED

            # Case 3: Fixed camera normal, but drone registers target (possible false trigger)
            if len(camera_labels) == 0 and len(drone_labels) > 0:
                return VerificationState.NEED_MORE_INFORMATION

            # Case 4: Both sensors register active data
            if self.require_match:
                matched_classes = set(camera_labels).intersection(set(drone_labels))
                if not matched_classes:
                    logger.warning("Class intersection empty. Sensor telemetry mismatch.")
                    return VerificationState.NOT_VERIFIED

                for cls in matched_classes:
                    idx = drone_labels.index(cls)
                    if drone_confs[idx] >= self.conf_thresh:
                        logger.info(f"Anomaly verified successfully for target class: '{cls}'")
                        return VerificationState.VERIFIED
                return VerificationState.NEED_MORE_INFORMATION
            else:
                if len(drone_confs) > 0 and max(drone_confs) >= self.conf_thresh:
                    return VerificationState.VERIFIED
                return VerificationState.NEED_MORE_INFORMATION
        except Exception as e:
            logger.error(f"Exception encountered inside sensor fusion verification logic: {e}")
            return VerificationState.NEED_MORE_INFORMATION

class VerificationContext:
    def __init__(self, strategy: RuleBasedVerification):
        self._strategy = strategy

    def run_verification(self, camera_detections: List[str], drone_detections: List[str], drone_confidences: List[float]) -> VerificationState:
        return self._strategy.evaluate(camera_detections, drone_detections, drone_confidences)
