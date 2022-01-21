import logging
from typing import Optional

import requests
import requests.auth
from requests import models

from resistant_documents_client.base import ApiClientBase

logger = logging.getLogger(__name__)


class ApiKeyAuth(requests.auth.AuthBase):

    def __init__(self, api_key: str):
        self.api_key = api_key

    def __call__(self, r: models.PreparedRequest) -> models.PreparedRequest:
        r.headers["Authorization"] = self.api_key
        return r


class ResistantDocumentsClient(ApiClientBase):

    _SUBMIT_ENDPOINT = "/v1/pdf/submit"
    _RESULTS_ENDPOINT = "/v1/pdf/results/{submission_id}"
    _CONTENT_ENDPOINT = "/v1/pdf/content/{submission_id}"
    _PRESIGN_ENDPOINT = "/v1/pdf/presign/{submission_id}"
    _QUALITY_ENDPOINT = "/v1/pdf/quality/{submission_id}"

    def __init__(self, api_key: str, api_url: str = "https://api.pdf.resistant.ai") -> None:
        self.api_url = api_url if api_url[-1] != "/" else api_url[:-1]
        session = requests.Session()
        session.auth = ApiKeyAuth(api_key)
        super().__init__(session)

    @property
    def _submit_url(self) -> str:
        return f"{self.api_url}{ResistantDocumentsClient._SUBMIT_ENDPOINT}"

    @property
    def _results_url(self):
        return f"{self.api_url}{ResistantDocumentsClient._RESULTS_ENDPOINT}"

    @property
    def _content_url(self):
        return f"{self.api_url}{ResistantDocumentsClient._CONTENT_ENDPOINT}"

    @property
    def _quality_url(self):
        return f"{self.api_url}{ResistantDocumentsClient._QUALITY_ENDPOINT}"

    def submit(self, data: bytes, query_id: str = "", pipeline_configuration: Optional[str] = None):
        return self._submit(self._submit_url, data, query_id, pipeline_configuration)

    def results(self, submission_id: str, max_num_retries: int = ApiClientBase.MAX_NUM_RETRIES_POLL) -> dict:
        return self._poll(self._results_url, submission_id, max_num_retries)

    def content(self, submission_id: str, max_num_retries: int = ApiClientBase.MAX_NUM_RETRIES_POLL) -> dict:
        return self._poll(self._content_url, submission_id, max_num_retries)

    def quality(self, submission_id: str, max_num_retries: int = ApiClientBase.MAX_NUM_RETRIES_POLL) -> dict:
        return self._poll(self._quality_url, submission_id, max_num_retries)

    def analyze(self, data: bytes, query_id: str = "", max_num_retries: int = ApiClientBase.MAX_NUM_RETRIES_POLL) -> dict:
        submission_id = self.submit(data, query_id)
        return self.results(submission_id, max_num_retries)

    def presign(self, submission_id: str, expiration: int):
        url = f"{self.api_url}{ResistantDocumentsClient._PRESIGN_ENDPOINT}"
        response = self._api_session.post(url.format(submission_id=submission_id), json={'expiration': expiration})

        response.raise_for_status()
        return response.json()
