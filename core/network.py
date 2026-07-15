"""
core/network.py - MEC/Compute VM Optimized REST Client for NiralOS 5G Core.
"""
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from typing import Optional
from config import NiralConfig, DroneConfig

logger = logging.getLogger("NiralOSClient_Internal")

class NiralAPI:
    def __init__(self, base_url: str = NiralConfig.BASE_URL):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.token: Optional[str] = None
        
        # Ingress protection for internal virtual switches
        retries = Retry(
            total=5,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504],
            raise_on_status=False
        )
        self.session.mount("http://", HTTPAdapter(max_retries=retries))

    def login(self) -> bool:
        """Executes secure login handshake against NiralOS Edge Controller."""
        # Hum direct config file se direct values read kar rahe hain taaki koi object attribute error na aaye
        url = f"{self.base_url}/api/v1/login"  
        
        payload = {
            "username": NiralConfig.USERNAME,
            "password": NiralConfig.PASSWORD
        }
        
        logger.info(f"Attempting token acquisition from route: {url}")
        try:
            response = self.session.post(url, json=payload, timeout=5.0)
            
            # Fallback Route 1: Agar root ya api custom layout 405/404 de
            if response.status_code in [404, 405]:
                alt_url = f"{self.base_url}/api/token"
                logger.info(f"Retrying authentication on fallback route: {alt_url}")
                response = self.session.post(alt_url, json=payload, timeout=5.0)

            # Fallback Route 2: Direct token link hit matrix
            if response.status_code in [404, 405]:
                direct_url = f"{self.base_url}/token"
                logger.info(f"Retrying pure POST authentication on route: {direct_url}")
                response = self.session.post(direct_url, json=payload, timeout=5.0)

            response.raise_for_status()
            data = response.json()
            
            # Har possible response key format check karein
            self.token = data.get("accessToken") or data.get("access_token") or data.get("token")
            
            if self.token:
                logger.info("Secure JWT Token verified and saved from NiralOS Edge framework.")
                return True
            else:
                logger.error(f"Authentication response missing token keys. Raw JSON: {data}")
                return False
                
        except Exception as e:
            logger.error(f"VM internal login exception encountered: {e}")
            return False

    def create_slice(self, sst: int, sd: str, default_indicator: bool = True) -> bool:
        url = f"{self.base_url}/v2/5gcore/subscriber/addSlice"
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        
        payload = {
            "sst": sst,
            "sd": sd,
            "default_indicator": default_indicator,
            "session": [{
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
            }]
        }
        try:
            res = self.session.post(url, json=payload, headers=headers, timeout=5.0)
            return res.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Local dynamic slice creation breakdown: {e}")
            return False

    def assign_slice_to_device(self, sst: int, sd: str) -> bool:
        url = f"{self.base_url}/v2/5gcore/subscriber/addSubscriber"
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        
        payload = {
            "schema_version": 1,
            "imsi": DroneConfig.DEVICE_IMSI,
            "deviceType": "Iot",
            "security": {"aliseName": "SuparnaAircraftNode", "amf": "8000"},
            "ambr": {"downlink": {"value": 300, "unit": 3}, "uplink": {"value": 50, "unit": 3}},
            "slice": [{
                "sst": sst, "sd": sd, "default_indicator": True,
                "session": [{
                    "name": NiralConfig.DEFAULT_APN, "apn_id": "3", "type": 1,
                    "qos": {"index": 9, "arp": {"priority_level": 1, "pre_emption_capability": 2, "pre_emption_vulnerability": 2}},
                    "ambr": {"downlink": {"value": 150, "unit": 3}, "uplink": {"value": 20, "unit": 3}},
                    "ue": {}, "smf": {}, "pcc_rule": []
                }]
            }],
            "mcc": DroneConfig.MCC, "mnc": DroneConfig.MNC
        }
        try:
            res = self.session.post(url, json=payload, headers=headers, timeout=5.0)
            return res.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Local VM internal subscriber map failure: {e}")
            return False

    def health_check(self) -> bool:
        url = f"{self.base_url}/v2/5gcore/overview/cards_core_gnb_ue_graph/range=hour"
        try:
            res = self.session.get(url, timeout=3.0)
            return res.status_code == 200
        except Exception:
            return False