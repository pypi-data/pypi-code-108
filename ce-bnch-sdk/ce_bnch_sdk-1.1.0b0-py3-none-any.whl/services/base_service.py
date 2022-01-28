from abc import ABC

from benchling_api_client.client import Client

from benchling_sdk.helpers.retry_helpers import RetryStrategy


class BaseService(ABC):
    """Abstract class for Benchling functional namespaces."""

    _client: Client
    _retry_strategy: RetryStrategy

    def __init__(self, client: Client, retry_strategy: RetryStrategy = RetryStrategy()):
        """
        Initialize a service.

        :param client: Underlying generated Client.
        :param retry_strategy: Retry strategy for failed HTTP calls
        """
        self._client = client
        self._retry_strategy = retry_strategy

    @property
    def client(self) -> Client:
        """Provide access to the underlying generated Benchling Client."""
        return self._client

    @property
    def retry_strategy(self) -> RetryStrategy:
        """Provide access to the underlying user-specified RetryStrategy."""
        return self._retry_strategy
