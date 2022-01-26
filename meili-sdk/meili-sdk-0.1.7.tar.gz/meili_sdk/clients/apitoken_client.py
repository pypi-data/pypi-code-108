from meili_sdk.clients.base import BaseAPIClient

__all__ = ("APITokenClient",)


class APITokenClient(BaseAPIClient):
    AUTHORIZATION_TOKEN_HEADER = "Token"  # nosec
