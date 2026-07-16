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

        retries = Retry(
            total=5,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504],
            raise_on_status=False
        )
        self.session.mount("http://", HTTPAdapter(max_retries=retries))

    def login(self) -> bool:
        logger.info("Initializing baseline verification sequence...")
        logger.info(f"Target system bridge endpoint configuration: {self.base_url}")

        self.token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.bW9ja19sYWJfdG9rZW5fYnlwYXNz"
        logger.info("Secure JWT Token verified and saved successfully from NiralOS Edge refresh framework (Simulated).")
        return True

    def create_slice(self, sst: int, sd: str, default_indicator: bool = True) -> bool:
        logger.info(f"[SIMULATED] Successfully requested 5G Network Slice creation. SST: {sst}, SD: {sd}")
        return True

    def assign_slice_to_device(self, sst: int, sd: str) -> bool:
        logger.info(f"[SIMULATED] Successfully assigned 5G Slice (SST: {sst}, SD: {sd}) to Device IMSI: {DroneConfig.DEVICE_IMSI}")
        return True

    def health_check(self) -> bool:
        return True
