import json

import requests

from cognite.air._air_api_url import retrieve_air_api_url
from cognite.client import CogniteClient


class AdminAPI:
    _ENDPOINT = "/"

    def __init__(self, client: CogniteClient, staging: bool = True):
        self.client = client
        self.staging = staging
        self.headers = {"api-key": self.client.config.api_key, "Content-Type": "application/json"}

    @property
    def _api_url(self) -> str:
        return retrieve_air_api_url(self.client, self.staging)

    def _post(self, payload):
        r = requests.post(self._api_url + self._ENDPOINT, data=json.dumps(payload), headers=self.headers)
        r.raise_for_status()

    def _get(self):
        pass
