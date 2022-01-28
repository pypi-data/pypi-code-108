from meili_sdk.clients.base import BaseAPIClient

__all__ = ("PersistentTokenClient",)


class PersistentTokenClient(BaseAPIClient):
    AUTHORIZATION_TOKEN_HEADER = "API-Token"  # nosec
