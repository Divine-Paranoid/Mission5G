"""
main.py - Centralized Orchestration Engine with Live Video Dashboard Visualizer.
Source of Truth: DoT 100 5G Labs Architecture Manuals.
"""
import sys
import time
import signal
import logging
import cv2
import numpy as np
from config import SystemConfig, CameraConfig, DroneConfig, NiralConfig, NetworkPolicyConfig
from core.camera import CameraManager
from core.detector import ObjectDetector
from core.drone_vvdn import Suparna5GDrone
from core.verification import RuleBasedVerification, VerificationContext, VerificationState
from core.decision_engine import DecisionEngine, MissionState
from core.network import NiralAPI

logging.basicConfig(level=SystemConfig.LOG_LEVEL, format=SystemConfig.LOG_FORMAT)
logger = logging.getLogger("VVDN_OrchestratorCore")

RUNNING = True
def sig_handler(signum, frame):
    global RUNNING
    RUNNING = False
signal.signal(signal.SIGINT, sig_handler)

def main():
    logger.info("Launching VVDN/DoT Ecosystem Production Orchestrator...")
    
    camera = CameraManager()
    detector = ObjectDetector(model_path="yolov8n.pt")
    drone = Suparna5GDrone()
    
    verifier = VerificationContext(strategy=RuleBasedVerification())
    decision_engine = DecisionEngine(policy_configurations=NetworkPolicyConfig.POLICIES)
    niral_client = NiralAPI()
    
    if not camera.connect() or not drone.connect() or not niral_client.login():
        logger.critical("Subsystem initialization crashed or was rejected by lab hardware links.")
        sys.exit(1)
        
    active_sst, active_sd = None, None
    last_anomaly_time = 0.0
    COOLDOWN_WINDOW_SEC = 2.0
    
    # GUI Visual Dashboard Metrics
    current_ui_state = "NORMAL"
    current_ui_slice = "slice-default-embb"
    api_status_log = "System Quiescent"
    
    logger.info("Ecosystem stable. Entering operational runtime loop...")
    
    while RUNNING:
        try:
            ok, cam_frame = camera.get_frame()
            if not ok or cam_frame is None:
                time.sleep(0.04)
                continue
                
            # Run Inference and fetch the pre-painted frame from our detector layer
            cam_telemetry, painted_frame = detector.detect(cam_frame)
            camera_has_detections = len(cam_telemetry.labels) > 0
            
            if camera_has_detections:
                last_anomaly_time = time.time()
            
            drone_labels, drone_confs = [], []
            if camera_has_detections and decision_engine.current_state == MissionState.NORMAL:
                if drone.takeoff():
                    drone.start_video()
                    
            if drone._streaming:
                drone_ok, drone_frame = drone.get_frame()
                if drone_ok and drone_frame is not None:
                    drone_telemetry, _ = detector.detect(drone_frame)
                    drone_labels = drone_telemetry.labels
                    drone_confs = drone_telemetry.confidences.tolist() if hasattr(drone_telemetry.confidences, "tolist") else list(drone_telemetry.confidences)
                    if len(drone_labels) > 0:
                        last_anomaly_time = time.time()
                    
            v_state = verifier.run_verification(cam_telemetry.labels, drone_labels, drone_confs)
            
            if v_state == VerificationState.NOT_VERIFIED and (time.time() - last_anomaly_time < COOLDOWN_WINDOW_SEC):
                if camera_has_detections or decision_engine.current_state == MissionState.VERIFY:
                    v_state = VerificationState.NEED_MORE_INFORMATION
                    camera_has_detections = True
            
            target_mission_state = decision_engine.evaluate_state(camera_has_detections, v_state)
            policy = NetworkPolicyConfig.POLICIES[target_mission_state.value]
            
            current_ui_state = target_mission_state.value
            
            if active_sst != policy["sst"] or active_sd != policy["sd"]:
                api_status_log = f"TRIGGERED CORE UPDATE -> SST: {policy['sst']}"
                if niral_client.create_slice(policy["sst"], policy["sd"]):
                    if niral_client.assign_slice_to_device(policy["sst"], policy["sd"]):
                        active_sst = policy["sst"]
                        active_sd = policy["sd"]
                        current_ui_slice = f"SST-{policy['sst']}-SD-{policy['sd']}"
                        api_status_log = "5G CORE SLICE PROVISIONED SUCCESSFULLY"
            
            # --- LIVE GRAPHICAL DASHBOARD HUD OVERLAY ---
            # Frame ke top-left corner par ek black overlay translucent panel status board banate hain
            overlay = painted_frame.copy()
            cv2.rectangle(overlay, (10, 10), (550, 180), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.6, painted_frame, 0.4, 0, painted_frame)
            
            # Text parameters display mapping
            cv2.putText(painted_frame, f"VVDN 5G MISSION STATE: {current_ui_state}", (20, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(painted_frame, f"ACTIVE 5G SLICE PROFILE: {current_ui_slice}", (20, 75), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(painted_frame, f"DRONE BATT: {drone.telemetry['battery_remaining']}% | ALT: {drone.telemetry['relative_alt']}m", (20, 110), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(painted_frame, f"NIRALOS CORE SIGNAL: {api_status_log}", (20, 145), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 1)
            
            # Render visual window locally
            cv2.imshow("DTU 5G USE CASE LAB - ORCHESTRATOR DASHBOARD", painted_frame)
            
            # Escape key parameter tracking (Press 'q' inside video dashboard to exit)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                logger.info("User triggered exit via GUI dashboard interface.")
                break
                
        except Exception as e:
            logger.error(f"Pipeline error crash state intercept: {e}")
            
    camera.disconnect()
    drone.disconnect()
    cv2.destroyAllWindows()
    logger.info("Orchestrator safely offline.")

if __name__ == "__main__":
    main()