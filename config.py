"""
config.py - Centralized Configuration Profiles (MEC VM Internal Deployment Mode)
"""
import os
import logging

class SystemConfig:
    PROJECT_NAME = "VVDN-DoT Mission-Aware Private 5G Drone Orchestration"
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    # VM deployment me absolute ya standardized log path use karein
    LOG_FILE_PATH = "/var/log/mission_aware_5g/system_orchestrator.log"

class CameraConfig:
    """Sparsh 5G Camera (MEC Routing Path via N6 Local Breakout)."""
    CAMERA_IP = os.getenv("DTU_SPARSH_CAM_IP", "192.168.128.10")
    USER = "admin"
    PASS = "admin123"
    RTSP_URL = f"rtsp://{USER}:{PASS}@{CAMERA_IP}:554/avstream/channel=1/stream=0.sdp"
    FRAME_WIDTH = 1920
    FRAME_HEIGHT = 1080
    FPS = 25

class DroneConfig:
    """Menthosa Suparna 5G Drone (UDP Telemetry listener on MEC interface)."""
    # VM ke andar local port par drone data push karega via 5G UPF Data Path
    DRONE_IP = os.getenv("DTU_SUPARNA_DRONE_IP", "10.42.0.1")
    MAVLINK_PORT = 14550  
    RTSP_STREAM_URL = f"rtsp://{DRONE_IP}:10000/drone_cam"
    DEVICE_IMSI = "001010000000001"
    MCC = "001"
    MNC = "01"

class NiralConfig:
    """NiralOS Private 5G Core Controller (Access from Network compute node VM)."""
    MOCK_MODE = False
    
    # Proxmox host IP par hi chal rahe NiralOS Edge Controller ka dashboard/API destination
    BASE_URL = "http://172.16.0.3:8082" 
    USERNAME = "admin"
    PASSWORD = "admin@1234"
    DEFAULT_APN = "ims"

class NetworkPolicyConfig:
    """Declarative 5G Network Slicing and dynamic QoS profiles mapping."""
    POLICIES = {
        "NORMAL":    {"sst": 1, "sd": "000001", "priority": 4, "bandwidth_val": 50,  "bandwidth_unit": 3, "index": 9},
        "VERIFY":    {"sst": 2, "sd": "000002", "priority": 2, "bandwidth_val": 150, "bandwidth_unit": 3, "index": 4},
        "EMERGENCY": {"sst": 3, "sd": "000003", "priority": 1, "bandwidth_val": 300, "bandwidth_unit": 3, "index": 1},
        "RECOVERY":  {"sst": 1, "sd": "000001", "priority": 3, "bandwidth_val": 75,  "bandwidth_unit": 3, "index": 9}
    }