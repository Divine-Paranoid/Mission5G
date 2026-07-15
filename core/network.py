"""
core/network.py - MEC VM Optimized REST Client for NiralOS 5G Core.
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
        
        # High-Availability: Retry strategy for local VM inter-process calls
        # Jab network slice restart hota hai, local API gateway microsecond delay ke liye drop ho sakta hai
        retries = Retry(
            total=5,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            raise_on_status=False
        )
        self.session.mount("http://", HTTPAdapter(max_retries=retries))

    def login(self) -> bool:
        url = f"{self.base_url}/token"
        payload = {"username": NiralConfig.USERNAME, "password": NiralConfig.PASSWORD}
        try:
            response = self.session.post(url, json=payload, timeout=2.0) # Local latency is < 2ms
            response.raise_for_status()
            self.token = response.json().get("accessToken")
            logger.info("Internal token refreshed via local network socket.")
            return True
        except Exception as e:
            logger.error(f"Internal VM login failure to NiralOS gateway: {e}")
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
            res = self.session.post(url, json=payload, headers=headers, timeout=4.0)
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
            res = self.session.post(url, json=payload, headers=headers, timeout=4.0)
            return res.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Local VM internal subscriber map failure: {e}")
            return False

    def health_check(self) -> bool:
        url = f"{self.base_url}/v2/5gcore/overview/cards_core_gnb_ue_graph/range=hour"
        try:
            res = self.session.get(url, timeout=2.0)
            return res.status_code == 200
        except Exception:
            return False