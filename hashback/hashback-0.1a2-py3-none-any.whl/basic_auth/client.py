import requests.auth

from ..http_client import RequestsClient
from ..http_protocol import ServerProperties


class BasicAuthClient(RequestsClient):

    def __init__(self, server: ServerProperties):
        super().__init__(server)
        if server.credentials is not None:
            self._auth = requests.auth.HTTPBasicAuth(
                username=server.credentials.username,
                password=server.credentials.password,
            )
        else:
            self._auth = None

    def _send_raw_request(self, method: str, url: str, stream_response: bool, **kwargs) -> requests.Response:
        return super()._send_raw_request(method, url, stream_response, auth=self._auth, **kwargs)
