from dataclasses import dataclass

from mindfoundry.client.horizon.generated import Client

from .datasets_client import DatasetsClient
from .pipelines_client import PipelinesClient

_DEFAULT_TIMEOUT_SECONDS = 180


@dataclass
class Connection:
    base_url: str
    api_key: str


class HorizonClient:
    def __init__(
        self,
        connection: Connection,
        timeout: float = _DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        # Even though our swagger includes "servers":[{"url":"/api"}] it's not currently used by
        # openapi-python-client. See https://github.com/triaxtec/openapi-python-client/issues/112
        base_url = f"{connection.base_url}/api"
        headers = {"X-ApiKey": connection.api_key}
        client = Client(base_url=base_url, headers=headers, timeout=timeout)

        self._connection = connection
        self._datasets_client = DatasetsClient(client)
        self._pipelines_client = PipelinesClient(client)

    @property
    def datasets(self) -> DatasetsClient:
        return self._datasets_client

    @property
    def pipelines(self) -> PipelinesClient:
        return self._pipelines_client
