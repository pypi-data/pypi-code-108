import datetime
import os
from typing import *

from oauthlib.oauth2 import BackendApplicationClient, OAuth2Error
from requests_oauthlib import OAuth2Session


def generate_oidc_token(
    *,
    token_url: Optional[str] = None,
    token_client_id: Optional[str] = None,
    token_client_secret: Optional[str] = None,
    token_scopes: Optional[str] = None,
    token_custom_args: Optional[Dict[str, str]] = None,
) -> Callable[[], str]:
    """Returns a callable that can be invoked to generate an OIDC token from info provided.

    Args:
        token_url (Optional[str]): If none, will attempt to use the environmental variable :code:`COGNITE_TOKEN_URL`.
        token_client_id (Optional[str]): The id for the token. If none, will attempt to use the environmental variable :code:`COGNITE_CLIENT_ID`.
        token_client_secret (Optional[str]): The secret for the token. If none, will attempt to use the environmental variable :code:`COGNITE_CLIENT_SECRET`.
        token_scopes (Optional[str]): A comma-separated list of token scopes. If none, will attempt to use the environmental variable :code:`COGNITE_TOKEN_SCOPES`
        token_custom_args (Optional[Dict[str, str]]): Custom args for tokens.
    """
    token_url = token_url or os.getenv("COGNITE_TOKEN_URL")
    token_client_id = token_client_id or os.getenv("COGNITE_CLIENT_ID")
    token_client_secret = token_client_secret or os.getenv("COGNITE_CLIENT_SECRET")
    token_scopes = token_scopes or os.getenv("COGNITE_TOKEN_SCOPES", "").split(",")
    token_custom_args = token_custom_args or {}

    def inner():
        gen = TokenGenerator(token_url, token_client_id, token_client_secret, token_scopes, token_custom_args)

        return gen._access_token

    return inner


class TokenGenerator:
    """Used to generate an OIDC token from the appropriate information."""

    def __init__(
        self, token_url: str, client_id: str, client_secret: str, scopes: List[str], custom_args: Dict[str, str]
    ):
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.scopes = scopes
        self.custom_args = custom_args

        if self.token_params_set():
            self._generate_access_token()
        else:
            self._access_token = None
            self._access_token_expires_at = None

    def return_access_token(self):
        if not self.token_params_set():
            raise Exception("Could not generate access token - missing token generation arguments")
        elif self._access_token is None:
            raise Exception("Could not generate access token from provided token generation arguments")

        if self._access_token_expires_at < datetime.datetime.now().timestamp():
            self._generate_access_token()

        return self._access_token

    def _generate_access_token(self):
        try:
            client = BackendApplicationClient(client_id=self.client_id)
            oauth = OAuth2Session(client=client)
            token_result = oauth.fetch_token(
                token_url=self.token_url,
                client_id=self.client_id,
                client_secret=self.client_secret,
                scope=self.scopes,
                **self.custom_args,
            )
        except OAuth2Error as oauth_error:
            raise Exception(
                "Error generating access token: {0}, {1}, {2}".format(
                    oauth_error.error, oauth_error.status_code, oauth_error.description
                )
            )
        else:
            self._access_token = token_result.get("access_token")
            self._access_token_expires_at = token_result.get("expires_at")

    def token_params_set(self):
        return (
            self.client_id is not None
            and self.client_secret is not None
            and self.token_url is not None
            and self.scopes is not None
        )
