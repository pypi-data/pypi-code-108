"""Graphql Client responsible for make API requests."""
from typing import Dict, Optional
import requests

from redbrick_slicer import __version__ as sdk_version  # pylint: disable=cyclic-import


class RBClient:
    """Client to communicate with RedBrick AI GraphQL Server."""

    def __init__(self, url: str) -> None:
        """Construct RBClient."""
        self.url = url.rstrip("/") + "/graphql/"
        self.session = requests.Session()
        self.auth_token: Optional[str] = None

    def __del__(self) -> None:
        """Garbage collect and close session."""
        self.session.close()

    @property
    def headers(self) -> Dict:
        """Get request headers."""
        if not self.auth_token:
            raise ValueError("No api key or auth token provided")
        return {"RB-SDK-Version": sdk_version, "Authorization": self.auth_token}

    def execute_query(
        self, query: str, variables: Dict, raise_for_error: bool = True
    ) -> Dict:
        """Execute a graphql query."""
        response = self.session.post(
            self.url,
            headers=self.headers,
            json={"query": query, "variables": variables},
        )
        self._check_status_msg(response.status_code)
        return self._process_json_response(response.json(), raise_for_error)

    @staticmethod
    def _check_status_msg(response_status: int) -> None:
        if response_status >= 500:
            raise ConnectionError(
                "Internal Server Error: You are probably using an invalid API key"
            )
        if response_status == 403:
            raise PermissionError("Problem authenticating with Api Key")

    @staticmethod
    def _process_json_response(
        response_data: Dict, raise_for_error: bool = True
    ) -> Dict:
        """Process JSON resonse."""
        if "errors" in response_data:
            errors = []
            for error in response_data["errors"]:
                errors.append(error["message"])
                print(error["message"])

            if raise_for_error:
                raise ValueError("\n".join(errors))

            del response_data["errors"]

        res = {}
        if "data" in response_data:
            res = response_data["data"]
        else:
            res = response_data
        return res
