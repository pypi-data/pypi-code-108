import typing as t

from pyarrow.flight import ClientAuthHandler, FlightClient  # type: ignore

from tktl.core.clients.future.taktile import DeploymentApiClient
from tktl.core.config import settings
from tktl.core.loggers import LOG
from tktl.core.schemas.repository import (
    RepositoryDeployment,
    _format_grpc_url,
    load_certs,
)

from .endpoint import ArrowEndpoints


class ApiKeyClientAuthHandler(ClientAuthHandler):
    def __init__(self, api_key: str):
        super().__init__()
        self._api_key = api_key

    def authenticate(self, outgoing, incoming):
        outgoing.write(self._api_key)
        self._api_key = incoming.read()

    def get_token(self):
        return self._api_key


class ArrowClient:

    endpoints: ArrowEndpoints

    def __init__(
        self,
        api_key: str,
        repository_name: str,
        branch_name: str,
        url: t.Optional[str] = None,
    ):
        self._api_key = api_key
        self._repository_name = repository_name
        self._branch_name = branch_name
        self._url = ArrowClient.__get_url(
            url=url,
            repository_name=repository_name,
            branch_name=branch_name,
            api_key=api_key,
        )

        self._client = ArrowClient.__get_deployment_client(
            url=self._url, api_key=self._api_key
        )

        self._actions = self._client.list_actions()

        self.endpoints = ArrowEndpoints(client=self._client, actions=self._actions)

    @staticmethod
    def __get_deployment(
        *, repository_name: str, branch_name: str, client: DeploymentApiClient
    ) -> RepositoryDeployment:
        return client.get_deployment_by_branch_name(
            repository_name=repository_name, branch_name=branch_name
        )

    @staticmethod
    def __get_dapi_client(*, api_key: str) -> DeploymentApiClient:
        client = DeploymentApiClient(api_key)

        return client

    @staticmethod
    def __get_deployment_client(*, url: str, api_key: str) -> FlightClient:
        certs = None if settings.LOCAL_STACK else load_certs()
        client = FlightClient(location=url, tls_root_certs=certs)
        LOG.trace(f"Performing authentication request against {url}")
        client.authenticate(ApiKeyClientAuthHandler(api_key=api_key))

        return client

    @staticmethod
    def __get_url(
        *, url: t.Optional[str], repository_name: str, branch_name: str, api_key: str
    ) -> str:
        if url:
            return url

        client = ArrowClient.__get_dapi_client(api_key=api_key)
        deployment = ArrowClient.__get_deployment(
            repository_name=repository_name, branch_name=branch_name, client=client
        )

        return _format_grpc_url(deployment.public_docs_url)
