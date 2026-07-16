import struct
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("MAVLinkCodec")

class MavlinkFrameDecoder:

    @staticmethod
    def parse_global_position_int(payload: bytes) -> Optional[Dict[str, Any]]:
        """Parses MAVLink #33 GLOBAL_POSITION_INT frames for precise location metrics."""
        if len(payload) < 28:
            return None
        try:
            data = struct.unpack("<IiiiihhhH", payload[:28])
            return {
                "lat": data[1] / 1E7,
                "lon": data[2] / 1E7,
                "alt": data[3] / 1000.0,
                "relative_alt": data[4] / 1000.0,
                "vx": data[5] / 100.0,
                "vy": data[6] / 100.0,
                "vz": data[7] / 100.0,
                "heading": data[8] / 100.0
            }
        except Exception as e:
            logger.error(f"Failed to unpack target MAVLink position payload bytes: {e}")
            return None

    @staticmethod
    def parse_sys_status(payload: bytes) -> Optional[Dict[str, Any]]:
        """Parses MAVLink #1 SYS_STATUS frames to monitor battery metrics."""
        if len(payload) < 20:
            return None
        try:
            voltage = struct.unpack_with_offset = struct.unpack("<H", payload[10:12])[0]
            remaining = struct.unpack("<b", payload[14:15])[0]
            return {
                "voltage": voltage / 1000.0, # Convert mV to Volts
                "battery_remaining": remaining
            }
        except Exception as e:
            logger.error(f"Failed to decode battery system payload array status: {e}")
            return None
