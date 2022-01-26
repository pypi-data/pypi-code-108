import json
import logging
import os
from base64 import b64decode
from datetime import datetime
from typing import Optional

from ._http import Connection
from ._utils import read_env


class Auth(Connection):  # nosec B107
    def __init__(
        self,
        api_endpoint: str = None,
        api_token: str = None,
        _token: Optional[str] = None,
        auto_connect=True,
        allow_self_certificate=True,
    ):
        self._logger = logging.getLogger("vectice.auth")
        endpoint, self._API_TOKEN = read_env("VECTICE_API_ENDPOINT", "VECTICE_API_TOKEN")
        if api_endpoint is not None:
            endpoint = api_endpoint
        if api_token is not None:
            self._API_TOKEN = api_token
        if not self._API_TOKEN:
            raise ValueError("VECTICE_API_TOKEN is not provided.")
        super().__init__(api_endpoint=endpoint, allow_self_certificate=allow_self_certificate)
        self._jwt = None
        self._jwt_expiration = None
        if _token:
            self._token = _token
        elif auto_connect:
            self._refresh_token()
        self.vectice_path: Optional[str] = None

    @property
    def _token(self) -> Optional[str]:
        if self._jwt_expiration is None:
            return None
        # Refresh token 1 min before expiration
        if datetime.now().timestamp() >= self._jwt_expiration - 60:
            self._refresh_token()
        return self._jwt

    @_token.setter
    def _token(self, jwt: str) -> None:
        self._jwt = jwt
        self._jwt_expiration = self._get_jwt_expiration(jwt)
        self._request_headers = {"Authorization": "Bearer " + jwt}

    def _refresh_token(self) -> None:
        self._logger.info("Vectice: Refreshing token... ")
        response = self._post("/metadata/authenticate", {"apiKey": self._API_TOKEN})
        self._token = response["token"]
        self._logger.info("Success!")

    def auth_project_token(self, project_token) -> None:
        self._logger.info("Vectice: Validating project token... ")
        response = self._get(f"/metadata/project/{project_token}/validate/")
        self._logger.info(
            f"The entered token is OK, and allows you to work on the '{response['name']}' Project, part of the '{response['workspace']['name']}' Workspace"
        )
        self.vectice_path = f"All your work is being captured in the '{response['name']}' Project, part of the '{response['workspace']['name']}' Workspace"

    @staticmethod
    def auth_api_token(api_token: str, api_endpoint: Optional[str]):
        logging.info("Vectice: Validating api token... ")
        if api_endpoint is None and os.getenv("VECTICE_API_ENDPOINT"):
            api_endpoint = os.getenv("VECTICE_API_ENDPOINT")
        elif api_endpoint is None and not os.getenv("VECTICE_API_ENDPOINT"):
            raise ValueError("No api endpoint could be found to connect to the Vectice App!")
        try:
            Connection(api_endpoint)._post("/metadata/authenticate", {"apiKey": api_token})
        except Exception as e:
            raise RuntimeError(f"Could not authenticate due to: {e}")
        logging.info("Success!")

    @staticmethod
    def _get_jwt_expiration(jwt: str) -> int:
        jwt_payload = jwt.split(".")[1]
        jwt_payload_with_padding = f"{jwt_payload}{'=' * (4 - len(jwt_payload) % 4)}"
        return int(json.loads(b64decode(jwt_payload_with_padding))["exp"])

    def token(self) -> Optional[str]:
        return self._token

    def connect(self) -> None:
        self._refresh_token()
