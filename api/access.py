# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

import os
import logging
import requests
from utils import get_headers

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class AccessClient:
    def __init__(self, connection_string: str, dev_mode: bool):
        self.connection_string = connection_string
        self.dev = dev_mode

        # Check for the environment variable at startup.
        if not self.dev:
            self.IDENTITY_API_URL = os.environ.get('IDENTITY_API_URL')
            if not self.IDENTITY_API_URL:
                logger.error("IDENTITY_API_URL environment variable is not set.")
                raise KeyError("IDENTITY_API_URL environment variable is not set.")

    def get_user_details(self, headers):
        # If in dev mode, return dummy data.
        if self.dev:
            logger.info("Dev mode enabled, returning dummy user details.")
            return {"username": "Test User1", "user_id": "1234-5678-99ab-cdef"}
        
        # Build the full URL for the API call.
        url = f"{self.IDENTITY_API_URL}/api/v1/user-details"
        logger.info("Making API call to %s", url)

        try:
            res = requests.get(url, headers=get_headers(headers))
        except Exception as e:
            logger.exception("Error making API call: %s", e)
            return {"error": "API call failed", "details": str(e)}

        if res.status_code == 200:
            data = res.json()
            logger.info("Received successful response from API")
            # Map displayName to username and username to user_id.
            return {
                "username": data["content"]["displayName"],
                "user_id": data["content"]["username"]
            }
        else:
            logger.error("API call returned error status %s: %s", res.status_code, res.text)
            return res.json()