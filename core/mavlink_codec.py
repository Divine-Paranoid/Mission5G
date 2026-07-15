"""
core/mavlink_codec.py - Production-grade Binary Parser for MAVLink v2 Telemetry Frames.
Extracts live structural states from the Menthosa Suparna 5G Drone.
"""
import struct
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("MAVLinkCodec")

class MavlinkFrameDecoder:
    """
    Decodes the raw binary packet arrays received from the PX4 flight controller
    via the 5G cellular communication channel.
    """
    
    @staticmethod
    def parse_global_position_int(payload: bytes) -> Optional[Dict[str, Any]]:
        """Parses MAVLink #33 GLOBAL_POSITION_INT frames for precise location metrics."""
        if len(payload) < 28:
            return None
        try:
            # MAVLink format payload definition:
            # time_boot_ms (uint32), lat (int32), lon (int32), alt (int32), relative_alt (int32)
            # vx (int16), vy (int16), vz (int16), hdg (uint16)
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
            # format context alignment map mapping to battery voltage fields safely
            # voltage_battery (uint16_t) at byte offset index 10
            voltage = struct.unpack_with_offset = struct.unpack("<H", payload[10:12])[0]
            # remaining tracking metrics extraction
            remaining = struct.unpack("<b", payload[14:15])[0]
            return {
                "voltage": voltage / 1000.0, # Convert mV to Volts
                "battery_remaining": remaining
            }
        except Exception as e:
            logger.error(f"Failed to decode battery system payload array status: {e}")
            return None