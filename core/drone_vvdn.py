import socket
import threading
import time
import logging
import struct
import cv2
import numpy as np
from typing import Tuple, Optional

from core.mavlink_codec import MavlinkFrameDecoder
from config import DroneConfig

logger = logging.getLogger("SuparnaDroneDriver")

class Suparna5GDrone:
    def __init__(self, drone_ip: str = DroneConfig.DRONE_IP, port: int = DroneConfig.MAVLINK_PORT):
        self.drone_ip = drone_ip
        self.port = port
        self._socket: Optional[socket.socket] = None
        self._video_cap: Optional[cv2.VideoCapture] = None
        self._running = False
        self._streaming = False
        self._thread: Optional[threading.Thread] = None

        # Telemetry State Registers
        self.telemetry = {
            "lat": 0.0, "lon": 0.0, "alt": 0.0, "relative_alt": 0.0,
            "voltage": 16.8, "battery_remaining": 100, "ground_velocity": 0.0
        }

    def connect(self) -> bool:
        logger.info(f"Binding network socket to receive MAVLink telemetry streams on UDP port {self.port}")
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._socket.bind(("0.0.0.0", self.port))
            self._socket.settimeout(2.0)
            self._running = True

            self._thread = threading.Thread(target=self._recv_loop, daemon=True)
            self._thread.start()
            return True
        except Exception as e:
            logger.error(f"Critical connection failure to Suparna MAVLink channel: {e}")
            return False

    def _recv_loop(self):
        while self._running:
            try:
                assert self._socket is not None
                data, _ = self._socket.recvfrom(4096)
                if len(data) < 12:  # MAVLink v2 headers minimum length constraint
                    continue

                if data[0] == 0xFD:
                    msg_id = struct.unpack("<I", data[7:10] + b'\x00')[0]
                    payload_offset = 12

                    if msg_id == 33: # GLOBAL_POSITION_INT
                        pos = MavlinkFrameDecoder.parse_global_position_int(data[payload_offset:])
                        if pos:
                            self.telemetry.update(pos)
                            self.telemetry["ground_velocity"] = np.sqrt(pos["vx"]**2 + pos["vy"]**2)
                    elif msg_id == 1: # SYS_STATUS
                        bat = MavlinkFrameDecoder.parse_sys_status(data[payload_offset:])
                        if bat:
                            self.telemetry.update(bat)
            except socket.timeout:
                continue
            except Exception as e:
                logger.error(f"Mavlink processing loop error scenario: {e}")

    def takeoff(self) -> bool:
        if self.telemetry["ground_velocity"] > 0.3:
            logger.error(f"Takeoff Rejected: Ground drift {self.telemetry['ground_velocity']}m/s exceeds 0.3m/s safety threshold.")
            return False
        logger.info("[MAVLink Command] Transmitting standard takeoff packet array context (MAV_CMD_NAV_TAKEOFF)")
        return self._send_mavlink_cmd(22)

    def land(self) -> bool:
        logger.info("[MAVLink Command] Triggering controlled auto-land validation path (MAV_CMD_NAV_LAND)")
        return self._send_mavlink_cmd(21)

    def start_video(self) -> bool:
        logger.info(f"Connecting to onboard payload stream gateway: {DroneConfig.RTSP_STREAM_URL}")
        try:
            self._video_cap = cv2.VideoCapture(DroneConfig.RTSP_STREAM_URL, cv2.CAP_FFMPEG)
            self._streaming = self._video_cap.isOpened()
            return self._streaming
        except Exception as e:
            logger.error(f"Failed to mount payload video stream link: {e}")
            self._streaming = False
            return False

    def get_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        if not self._streaming or self._video_cap is None:
            return False, None
        try:
            return self._video_cap.read()
        except Exception as e:
            logger.error(f"Error pulling payload video matrix frame: {e}")
            return False, None

    def _send_mavlink_cmd(self, command_id: int) -> bool:
        if self._socket:
            try:
                mock_packet = struct.pack("<BBBBBBH", 0xFD, 0x01, 0x00, 0x00, 0x01, command_id, 0x00)
                self._socket.sendto(mock_packet, (self.drone_ip, self.port))
                return True
            except Exception as e:
                logger.error(f"Failed to issue outbound UDP MAVLink payload command: {e}")
                return False
        return False

    def disconnect(self) -> bool:
        self._running = False
        self._streaming = False
        if self._socket:
            self._socket.close()
        if self._video_cap:
            self._video_cap.release()
        logger.info("Suparna interface disconnected cleanly.")
        return True

    def emergency_stop(self) -> bool:
        return self._send_mavlink_cmd(400)
