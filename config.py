"""
config.py - Complete & Centralized Configuration Profiles for the VVDN 5G Lab Ecosystem.
"""
import os

class SystemConfig:
    PROJECT_NAME = "VVDN-DoT Mission-Aware Private 5G Drone Orchestration"
    LOG_LEVEL = 20  # INFO level
    LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    LOG_FILE_PATH = "logs/system_orchestrator.log"

class CameraConfig:
    CAMERA_IP = os.getenv("DTU_SPARSH_CAM_IP", "192.168.128.10")
    USER = "admin"
    PASS = "admin123"
    RTSP_URL = f"rtsp://{USER}:{PASS}@{CAMERA_IP}:554/avstream/channel=1/stream=0.sdp"
    FRAME_WIDTH = 1920
    FRAME_HEIGHT = 1080
    FPS = 25

class DetectorConfig:
    MODEL_PATH = "yolov8n.pt"
    CONFIDENCE_THRESHOLD = 0.45

class DroneConfig:
    DRONE_IP = os.getenv("DTU_SUPARNA_DRONE_IP", "10.42.0.1")
    MAVLINK_PORT = 14550  
    RTSP_STREAM_URL = f"rtsp://{DRONE_IP}:10000/drone_cam"
    DEVICE_IMSI = "001010000000001"
    MCC = "001"
    MNC = "01"

# === YAHAN PE HAI FUSION CONFIG ===
class FusionConfig:
    REQUIRE_EXACT_CLASS_MATCH = True
    DRONE_MIN_CONFIDENCE = 0.50

class NiralConfig:
    MOCK_MODE = False
    BASE_URL = "http://172.16.0.3:8082" 
    USERNAME = "admin"
    PASSWORD = "admin@1234"
    DEFAULT_APN = "ims"

class NetworkPolicyConfig:
    POLICIES = {
        "NORMAL":    {"sst": 1, "sd": "000001", "priority": 4, "bandwidth_val": 50,  "bandwidth_unit": 3, "index": 9},
        "VERIFY":    {"sst": 2, "sd": "000002", "priority": 2, "bandwidth_val": 150, "bandwidth_unit": 3, "index": 4},
        "EMERGENCY": {"sst": 3, "sd": "000003", "priority": 1, "bandwidth_val": 300, "bandwidth_unit": 3, "index": 1},
        "RECOVERY":  {"sst": 1, "sd": "000001", "priority": 3, "bandwidth_val": 75,  "bandwidth_unit": 3, "index": 9}
    }