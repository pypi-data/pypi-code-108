import logging
import time
from typing import List, Optional

from oauthlib.oauth2 import BackendApplicationClient
from requests import HTTPError
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session

from resistant_documents_client.base import ApiClientBase
from resistant_documents_client.utils import is_valid_oauth_credentials

logger = logging.getLogger(__name__)


class ClientCredentialsSession(OAuth2Session):

    def __init__(self, client_id: str, client_secret: str, token_url: str, scope: List[str]):
        super().__init__(client_id=client_id, client=BackendApplicationClient(client_id=client_id), scope=scope)
        self.token_url = token_url
        self.client_secret = client_secret

    def request(self, method, url, data=None, headers=None, withhold_token=False, client_id=None, client_secret=None, **kwargs):
        if url != self.token_url:
            if not self.token or self.token.get("expires_at", 0) < time.time():
                self.fetch_token(
                    self.token_url,
                    auth=HTTPBasicAuth(client_id or self.client_id, client_secret or self.client_secret),
                    body=f'scope={" ".join(self.scope)}'
                )
        return super().request(method, url, data, headers, withhold_token, client_id, client_secret, **kwargs)


class ResistantDocumentsClient(ApiClientBase):
    SUBMISSIONS_SCOPES = ("submissions.read", "submissions.write")
    PROD_API_URL = "https://api.documents.resistant.ai"
    PROD_TOKEN_URL = "https://id.resistant.ai/oauth2/aus17c52xbW6c0yA9417/v1/token"

    _SUBMIT_ENDPOINT = "/v2/submission"
    _FRAUD_ENDPOINT = "/v2/submission/{submission_id}/fraud"
    _CONTENT_ENDPOINT = "/v2/submission/{submission_id}/content"
    _QUALITY_ENDPOINT = "/v2/submission/{submission_id}/quality"

    def __init__(self, client_id: str, client_secret: str, token_url: str = PROD_TOKEN_URL,
                 api_url: str = PROD_API_URL,
                 scopes: List[str] = SUBMISSIONS_SCOPES,
                 ) -> None:
        self.api_url = api_url if api_url[-1] != "/" else api_url[:-1]
        if is_valid_oauth_credentials(client_id, client_secret):
            raise ValueError("Fill client id and client secret properly, at least one of them is empty or None.")

        api_session = ClientCredentialsSession(client_id, client_secret, token_url, scopes)
        super().__init__(api_session)

    @property
    def _submit_url(self) -> str:
        return f"{self.api_url}{ResistantDocumentsClient._SUBMIT_ENDPOINT}"

    @property
    def _fraud_url(self):
        return f"{self.api_url}{ResistantDocumentsClient._FRAUD_ENDPOINT}"

    @property
    def _content_url(self):
        return f"{self.api_url}{ResistantDocumentsClient._CONTENT_ENDPOINT}"

    @property
    def _quality_url(self):
        return f"{self.api_url}{ResistantDocumentsClient._QUALITY_ENDPOINT}"

    def submit(self, data: bytes, query_id: str = "", pipeline_configuration: Optional[str] = None):
        return self._submit(self._submit_url, data, query_id, pipeline_configuration)

    def fraud(self, submission_id: str, max_num_retries: int = ApiClientBase.MAX_NUM_RETRIES_POLL, with_metadata: Optional[bool] = None) -> dict:
        try:
            query_params = {"with_metadata": with_metadata} if with_metadata is not None else None
            return self._poll(self._fraud_url, submission_id, max_num_retries, query_params)
        except HTTPError as e:
            if e.response.status_code == 400:
                presign_response = self._api_session.get(self._fraud_url.format(submission_id=submission_id), params={"presign": True})
                presign_response.raise_for_status()
                data_response = self._s3_session.get(presign_response.json()["download_url"])
                data_response.raise_for_status()
                return data_response.json()
            else:
                raise e

    def content(self, submission_id: str, max_num_retries: int = ApiClientBase.MAX_NUM_RETRIES_POLL) -> dict:
        return self._poll(self._content_url, submission_id, max_num_retries)

    def quality(self, submission_id: str, max_num_retries: int = ApiClientBase.MAX_NUM_RETRIES_POLL) -> dict:
        return self._poll(self._quality_url, submission_id, max_num_retries)

    def analyze(self, data: bytes, query_id: str = "", max_num_retries: int = ApiClientBase.MAX_NUM_RETRIES_POLL) -> dict:
        submission_id = self.submit(data, query_id)
        return self.fraud(submission_id, max_num_retries)
