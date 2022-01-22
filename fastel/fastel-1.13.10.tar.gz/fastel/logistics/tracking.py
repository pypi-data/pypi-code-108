import hashlib
import hmac
from typing import Any, Dict, Set

import requests


class TrackingClient:
    url = "https://api.trackingmore.com/v2"

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def _get(self, path: str) -> Dict[str, Any]:
        headers = {
            "Content-Type": "application/json",
            "Trackingmore-Api-Key": self._api_key,
        }
        full_url = f"{self.url}{path}"
        resp = requests.get(url=full_url, headers=headers)
        resp.raise_for_status()
        return resp.json()  # type: ignore

    def _post(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        headers = {
            "Content-Type": "application/json",
            "Trackingmore-Api-Key": self._api_key,
        }
        full_url = f"{self.url}{path}"
        resp = requests.post(url=full_url, json=data, headers=headers)
        resp.raise_for_status()
        return resp.json()  # type: ignore

    def create_tracking(self, logistics_id: str, carrier_code: str) -> Dict[str, Any]:
        data = {"tracking_number": logistics_id, "carrier_code": carrier_code}
        resp = self._post("/trackings/post", data=data)
        return resp

    def get_tracking(self, logistics_id: str, carrier_code: str) -> Dict[str, Any]:
        path = f"/trackings/{carrier_code}/{logistics_id}"
        resp = self._get(path)
        return resp

    def verify_signature(self, timestamp: int, signature: str, key: str) -> None:
        bytes_timestamp = str(timestamp).encode()
        bytes_key = key.encode()
        sign = hmac.new(
            key=bytes_key, msg=bytes_timestamp, digestmod=hashlib.sha256
        ).hexdigest()
        if sign != signature:
            raise ValueError("invalid signature")

    def verify(self, timestamp: int, signature: str, keys: Set[str]) -> bool:
        for key in keys:
            try:
                self.verify_signature(timestamp, signature, key)
                return True
            except ValueError:
                continue
        raise ValueError("invalid signature")
