"""
core/network.py - Production NiralOS REST 5G Core Controller Client with Simulation Fallback.
Source of Truth: DoT 100 5G Labs Training Architecture Manuals.
"""
import logging
import requests
import time
from typing import Dict, Any, Optional
from config import NiralConfig, DroneConfig

logger = logging.getLogger("NiralOSClient")

class NiralAPI:
    def __init__(self, base_url: str = NiralConfig.BASE_URL):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.token: Optional[str] = None
        
        # Simulation indicator flag if physical network framework is unreachable
        self.simulation_mode = False

    def login(self) -> bool:
        """Executes secure login handshake profile matching Manual Sec 3.7.21."""
        url = f"{self.base_url}/token"
        payload = {
            "username": NiralConfig.USERNAME,
            "password": NiralConfig.PASSWORD
        }
        try:
            # Enforce short timeout to detect if hardware switch is present
            response = self.session.post(url, json=payload, timeout=2.0)
            response.raise_for_status()
            data = response.json()
            self.token = data.get("accessToken")
            logger.info("Secure JWT Bearer Token generated successfully from NiralOS Gateway.")
            return True
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as net_err:
            # --- SIMULATION FALLBACK BYPASS TRAP ---
            logger.warning(f"Lab Core Unreachable. Activating local loopback simulation bypass mode: {net_err}")
            self.simulation_mode = True
            self.token = "simulated_vvdn_jwt_token_string"
            return True
            # ----------------------------------------
        except Exception as e:
            logger.error(f"Authentication rejected by NiralOS endpoint interface: {e}")
            return False

    def create_slice(self, sst: int, sd: str, default_indicator: bool = True) -> bool:
        """Provisions network isolation plane parameters (Manual Sec 3.7.11)."""
        if self.simulation_mode:
            logger.info(f"[SIMULATED 5G CORE] POST /v2/5gcore/subscriber/addSlice -> Created Slice Plan (SST: {sst}, SD: {sd})")
            return True

        url = f"{self.base_url}/v2/5gcore/subscriber/addSlice"
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        
        payload = {
            "sst": sst,
            "sd": sd,
            "default_indicator": default_indicator,
            "session": [
                {
                    "name": NiralConfig.DEFAULT_APN,
                    "apn_id": "3",
                    "type": 1, 
                    "qos": {
                        "index": 9,
                        "arp": {"priority_level": 1, "pre_emption_capability": 2, "pre_emption_vulnerability": 2}
                    },
                    "ambr": {
                        "downlink": {"value": 100, "unit": 3},
                        "uplink": {"value": 50, "unit": 3}
                    },
                    "ue": {}, "smf": {}, "pcc_rule": []
                }
            ]
        }
        try:
            res = self.session.post(url, json=payload, headers=headers, timeout=3.0)
            return res.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Failed to create slice profile on Niral Core: {e}")
            return False

    def assign_slice_to_device(self, sst: int, sd: str) -> bool:
        """Binds the active aircraft IMSI subscriber profile to the target network slice (Manual Sec 3.7.13)."""
        if self.simulation_mode:
            logger.info(f"[SIMULATED 5G CORE] POST /v2/5gcore/subscriber/addSubscriber -> Bound IMSI {DroneConfig.DEVICE_IMSI} to Slice (SST: {sst}, SD: {sd})")
            return True

        url = f"{self.base_url}/v2/5gcore/subscriber/addSubscriber"
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        
        payload = {
            "schema_version": 1,
            "imsi": DroneConfig.DEVICE_IMSI,
            "deviceType": "Iot",
            "security": {"aliseName": "SuparnaAircraftNode", "amf": "8000"},
            "ambr": {"downlink": {"value": 300, "unit": 3}, "uplink": {"value": 50, "unit": 3}},
            "slice": [
                {
                    "sst": sst, "sd": sd, "default_indicator": True,
                    "session": [{
                        "name": NiralConfig.DEFAULT_APN, "apn_id": "3", "type": 1,
                        "qos": {"index": 9, "arp": {"priority_level": 1, "pre_emption_capability": 2, "pre_emption_vulnerability": 2}},
                        "ambr": {"downlink": {"value": 150, "unit": 3}, "uplink": {"value": 20, "unit": 3}},
                        "ue": {}, "smf": {}, "pcc_rule": []
                    }]
                }
            ],
            "mcc": DroneConfig.MCC, "mnc": DroneConfig.MNC
        }
        try:
            res = self.session.post(url, json=payload, headers=headers, timeout=3.0)
            return res.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Failed to push subscriber slice linkage assignment: {e}")
            return False

    def health_check(self) -> bool:
        if self.simulation_mode:
            return True
        url = f"{self.base_url}/v2/5gcore/overview/cards_core_gnb_ue_graph/range=hour"
        try:
            res = self.session.get(url, timeout=2.0)
            return res.status_code == 200
        except Exception:
            return False