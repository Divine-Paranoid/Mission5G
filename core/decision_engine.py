"""
core/decision_engine.py - Policy-Driven 5G Slice Transition State Machine.
Source of Truth: DoT 100 5G Labs Training Architecture Manuals.
"""
import logging
from enum import Enum
from typing import Dict, Any
from core.verification import VerificationState

logger = logging.getLogger("VVDN_DecisionEngine")

class MissionState(Enum):
    NORMAL = "NORMAL"
    VERIFY = "VERIFY"
    EMERGENCY = "EMERGENCY"
    RECOVERY = "RECOVERY"

class DecisionEngine:
    def __init__(self, policy_configurations: Dict[str, Dict[str, Any]]):
        self._policies = policy_configurations
        self.current_state = MissionState.NORMAL

    def evaluate_state(self, camera_has_detections: bool, verification_status: VerificationState) -> MissionState:
        previous_state = self.current_state

        # State Transition Matrix
        if verification_status == VerificationState.VERIFIED:
            self.current_state = MissionState.EMERGENCY
        elif verification_status == VerificationState.NEED_MORE_INFORMATION and camera_has_detections:
            self.current_state = MissionState.VERIFY
        elif verification_status == VerificationState.NOT_VERIFIED and previous_state == MissionState.EMERGENCY:
            self.current_state = MissionState.RECOVERY
        elif verification_status == VerificationState.NOT_VERIFIED:
            self.current_state = MissionState.NORMAL

        if self.current_state != previous_state:
            logger.info(f"System State Transition Executed: {previous_state.value} -> {self.current_state.value}")
        return self.current_state