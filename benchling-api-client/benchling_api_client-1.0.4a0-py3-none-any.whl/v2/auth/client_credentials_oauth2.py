import base64
from dataclasses import dataclass
from datetime import datetime, timedelta
import threading
from typing import Optional

import httpx

from benchling_api_client.v2.benchling_client import AuthorizationMethod
from benchling_api_client.v2.types import Response

MINIMUM_TOKEN_EXPIRY_BUFFER = 60


class Token:
    """Represents an OAuth2 token response model."""

    def __init__(self, access_token: str, refresh_time: datetime):
        """
        Initialize Token.

        :param access_token: The raw token value for authorizing with the API
        :param refresh_time: Calculated value off of token time-to-live for when a new token should be generated.
        """
        self.access_token = access_token
        self.refresh_time = refresh_time

    def valid(self) -> bool:
        """Return whether token is still valid for use or should be regenerated."""
        return datetime.now() < self.refresh_time

    @classmethod
    def from_token_response(cls, token_response):
        """
        Construct Token from deserializing token endpoint response.

        Deserializes response from token endpoint and calculates expiry time with buffer for when token should be
        regenerated.

        :param token_response: The response from an RFC6749 POST /token endpoint.
        """
        token_type: str = token_response.get("token_type")
        access_token: str = token_response.get("access_token")
        expires_in: float = token_response.get("expires_in")
        assert token_type == "Bearer"
        # Add in a buffer to safeguard against race conditions with token expiration.
        # Buffer is 10% of expires_in time, clamped between [1, MINIMUM_TOKEN_EXPIRY_BUFFER] seconds.
        refresh_delta = expires_in - max(1, min(MINIMUM_TOKEN_EXPIRY_BUFFER, expires_in * 0.1))
        refresh_time = datetime.now() + timedelta(seconds=refresh_delta)
        return cls(access_token, refresh_time)


@dataclass
class TokenVendError(Exception):
    def __init__(self, response: Response):
        self.content = response.content
        super(TokenVendError, self).__init__(f"{response.status_code}: {response.content}")


class ClientCredentialsOAuth2(AuthorizationMethod):
    """
    OAuth2 client credentials for authorization.

    Use in combination with the Benchling() client constructor to be authorized with OAuth2 client_credentials grant
    type.
    """

    _data_for_token_request = {
        "grant_type": "client_credentials",
    }

    def __init__(self, client_id: str, client_secret: str, token_url: str):
        """
        Initialize ClientCredentialsOAuth2.

        :param client_id: Client id in client_credentials grant type
        :param client_secret: Client secret in client_credentials grant type
        :param token_url: A fully-qualified URL pointing at the access token request endpoint such as
                          https://benchling.com/api/v2/token
        """
        self._token_url = token_url
        token_encoded = base64.b64encode(f"{client_id}:{client_secret}".encode())
        self._header_for_token_request = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {token_encoded.decode()}",
        }
        self._token: Optional[Token] = None
        self._lock = threading.Lock()

    def vend_new_token(self):
        """Make RFC6749 request to token URL to generate a new bearer token for client credentials OAuth2 flow."""
        response: httpx.Response = httpx.post(
            self._token_url,
            data=ClientCredentialsOAuth2._data_for_token_request,
            headers=self._header_for_token_request,
        )

        if response.status_code == 200:
            as_json = response.json()
            self._token = Token.from_token_response(as_json)
        else:
            raise TokenVendError(response)

    def get_authorization_header(self) -> str:
        """
        Generate HTTP Authorization request header.

        If a token has not yet been requested or is close to its expiry time, a new token is requested.
        Otherwise, re-use existing valid token.
        """
        with self._lock:
            if self._token is None or not self._token.valid():
                self.vend_new_token()
        assert self._token is not None
        return f"Bearer {self._token.access_token}"
