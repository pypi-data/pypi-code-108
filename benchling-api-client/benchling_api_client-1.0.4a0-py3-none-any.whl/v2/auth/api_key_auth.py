import base64

import attr

from benchling_api_client.v2.benchling_client import AuthorizationMethod


@attr.s(auto_attribs=True)
class ApiKeyAuth(AuthorizationMethod):
    """
    API Key Authorization.

    Use in combination with the Benchling() client constructor to be authorized with HTTP Basic Authorization

    :param api_key: The Benchling-provided API key to use.
    """

    api_key: str

    def get_authorization_header(self) -> str:
        """Get content for a HTTP Authorization header."""
        token_encoded = base64.b64encode(f"{self.api_key}:".encode())
        return f"Basic {token_encoded.decode()}"
