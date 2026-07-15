"""
config.py - Centralized Configuration Profiles for the VVDN 5G Lab Ecosystem.
Source of Truth: DoT 100 5G Labs Architecture Manuals.
"""
import os
import logging

class SystemConfig:
    PROJECT_NAME = "VVDN-DoT Mission-Aware Private 5G Drone Orchestration"
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    LOG_FILE_PATH = "logs/system_orchestrator.log"

class CameraConfig:
    """Sparsh 5G Camera Subsystem Configuration (Manual: 5G Camera, Sec 1.3.1 & 1.9.1)."""
    CAMERA_IP = "192.168.128.10"
    USER = "admin"
    PASS = "admin123"
    
    # Target Production RTSP Path Mapping
    RTSP_URL = f"rtsp://{USER}:{PASS}@{CAMERA_IP}:554/avstream/channel=1/stream=0.sdp"
    FRAME_WIDTH = 1920
    FRAME_HEIGHT = 1080
    FPS = 25

class DetectorConfig:
    """AI Object Inference Thresholds."""
    MODEL_PATH = "yolov8n.pt"
    CONFIDENCE_THRESHOLD = 0.45

class DroneConfig:
    """Menthosa Suparna 5G Drone Subsystem Configuration (Manual: 5G Drone, Sec 4.17 & 4.23.1)."""
    DRONE_IP = "10.42.0.1"
    MAVLINK_PORT = 14550  
    RTSP_STREAM_URL = f"rtsp://{DRONE_IP}:10000/drone_cam"
    
    # Cellular Subscriber Registration Mapping
    DEVICE_IMSI = "001010000000001"  # Target Lab test IMSI
    MCC = "001"
    MNC = "01"

class FusionConfig:
    """Sensor Ingestion Data Cross-Examination Tuning."""
    REQUIRE_EXACT_CLASS_MATCH = True
    DRONE_MIN_CONFIDENCE = 0.50

class NiralConfig:
    """NiralOS Private 5G Core Controller Specifications (Manual: 5G Lab, Sec 3.7)."""
    BASE_URL = "http://172.16.0.22:8082"
    USERNAME = "admin"
    PASSWORD = "admin@1234"
    DEFAULT_APN = "ims"  

class NetworkPolicyConfig:
    """Declarative 5G Network Slicing and dynamic QoS profiles mapping."""
    POLICIES = {
        "NORMAL": {
            "sst": 1,
            "sd": "000001",
            "priority": 4,
            "bandwidth_val": 50,
            "bandwidth_unit": 3, 
            "index": 9,          
            "remarks": "Optimized for steady-state fixed camera streaming."
        },
        "VERIFY": {
            "sst": 2,
            "sd": "000002",
            "priority": 2,
            "bandwidth_val": 150,
            "bandwidth_unit": 3,
            "index": 4,          
            "remarks": "Elevated slice routing supporting live drone feedback."
        },
        "EMERGENCY": {
            "sst": 3,
            "sd": "000003",
            "priority": 1,
            "bandwidth_val": 300,
            "bandwidth_unit": 3,
            "index": 1,          
            "remarks": "Maximum priority bandwidth reservation for active anomaly response."
        },
        "RECOVERY": {
            "sst": 1,
            "sd": "000001",
            "priority": 3,
            "bandwidth_val": 75,
            "bandwidth_unit": 3,
            "index": 9,
            "remarks": "Post-event monitoring and diagnostics data synchronization."
        }
    }