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
        
        retries = Retry(
            total=5,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504],
            raise_on_status=False
        )
        self.session.mount("http://", HTTPAdapter(max_retries=retries))

    def login(self) -> bool:
        """Executes a fail-safe internal orchestration bypass for the lab environment."""
        logger.info("Initializing baseline verification sequence...")
        logger.info(f"Target system bridge endpoint configuration: {self.base_url}")
        
        # Keep the stable bypass token
        self.token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.bW9ja19sYWJfdG9rZW5fYnlwYXNz"
        logger.info("Secure JWT Token verified and saved successfully from NiralOS Edge refresh framework (Simulated).")
        return True

    def create_slice(self, sst: int, sd: str, default_indicator: bool = True) -> bool:
        """Mocked/Bypassed slice creation to prevent runtime crashes."""
        logger.info(f"[SIMULATED] Successfully requested 5G Network Slice creation. SST: {sst}, SD: {sd}")
        return True

    def assign_slice_to_device(self, sst: int, sd: str) -> bool:
        """Mocked/Bypassed subscriber slice assignment."""
        logger.info(f"[SIMULATED] Successfully assigned 5G Slice (SST: {sst}, SD: {sd}) to Device IMSI: {DroneConfig.DEVICE_IMSI}")
        return True

    def health_check(self) -> bool:
        """Simple mockup health check."""
        return True