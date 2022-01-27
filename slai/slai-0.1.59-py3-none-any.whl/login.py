import requests
import sys

from http import HTTPStatus
from slai.clients.identity import get_identity_client
from slai.modules.parameters import from_config
from slai.exceptions import (
    InvalidCredentials,
)


class Login:
    APP_BASE_URL = from_config(
        key="APP_BASE_URL",
        default="https://beta.slai.io",
    )

    def __init__(self, *, client_id=None, client_secret=None, key_type=None):
        self.identity_client = get_identity_client(
            client_id=client_id, client_secret=client_secret, key_type=key_type
        )

        if client_id is None or client_secret is None:
            self._notebook_auth_flow()
        else:
            self.client_id = client_id
            self.client_secret = client_secret

        self._validate_credentials()

    def _validate_credentials(self):
        try:
            _ = self.identity_client.validate_credentials()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == HTTPStatus.BAD_REQUEST:
                if e.response.json()["detail"][0] == "invalid_key_type":
                    raise InvalidCredentials("invalid_key_type")

            raise InvalidCredentials("invalid_credentials")

        # cache credentials on slai module
        setattr(
            sys.modules["slai"],
            "credentials",
            {"client_id": self.client_id, "client_secret": self.client_secret},
        )

        setattr(
            sys.modules["slai"],
            "authenticated",
            True,
        )
