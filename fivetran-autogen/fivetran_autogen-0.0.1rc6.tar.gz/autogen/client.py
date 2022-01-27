import os
import requests
from typing import Dict
from base64 import b64encode

FIVETRAN_API_KEY = os.getenv("FIVETRAN_API_KEY")
FIVETRAN_API_SECRET = os.getenv("FIVETRAN_API_SECRET")


class FivetranClient:
    def __init__(self, api_key, api_secret):
        self.session: requests.Session = requests.Session()
        header_token = b64encode(f"{api_key}:{api_secret}".encode("utf-8")).decode(
            "utf-8"
        )
        self.session.headers = {
            "Authorization": f"Basic {header_token}",
            "Content-Type": "application/json",
        }

    def get_connector_details(self, connector_id: str) -> Dict:
        url = f"https://api.fivetran.com/v1/connectors/{connector_id}"
        response = self.session.get(url, params={"limit": 1000})
        response.raise_for_status()
        result = response.json()
        cursor = result["data"].get("next_cursor")
        while cursor:
            response = self.session.get(url, params={"cursor": cursor, "limit": 1000})
            response.raise_for_status()
            result["data"]["items"].extend(response.json()["data"]["items"])
            cursor = response.json()["data"].get("next_cursor")
        return result

    def get_all_groups(self) -> Dict:
        url = "https://api.fivetran.com/v1/groups"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_all_connectors_in_group(self, group_id: str) -> Dict:
        url = f"https://api.fivetran.com/v1/groups/{group_id}/connectors"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_connector_schema_config(self, connector_id: str) -> Dict:
        url = f"https://api.fivetran.com/v1/connectors/{connector_id}/schemas"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
