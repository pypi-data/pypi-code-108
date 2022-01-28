from typing import List

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.utils.exceptions import CogniteInvalidInput


class BaseAPI:
    def __init__(self, client: APIClient):
        self.client: APIClient = client

    def _get_path(self, base_url: str) -> str:
        project = self.client._config.project
        return f"/api/playground/projects/{project}/wdl{base_url}"

    def _validate_external_ids(self, external_ids: List[str]):
        if len(external_ids) == 0:
            raise CogniteInvalidInput("list of ids cannot be empty.")
