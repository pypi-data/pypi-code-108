from typing import Optional, Union

from pyarrow.flight import FlightClient  # type: ignore
from taktile_types.enums.instance import ServiceType

from tktl.core.clients.http_client import API
from tktl.core.clients.taktile import DeploymentApiClient
from tktl.core.loggers import LOG, Logger, set_verbosity
from tktl.core.schemas.repository import Endpoint
from tktl.login import login


class Client(object):
    TRANSPORT: ServiceType

    def __init__(
        self,
        api_key: str,
        repository_name: str,
        branch_name: str,
        endpoint_name: str,
        local: bool = False,
        logger: Logger = LOG,
        verbosity: int = 0,
    ):
        set_verbosity(verbosity)
        login(api_key)
        self.local = local
        self.taktile_client = DeploymentApiClient(logger=logger)
        self.repository_name = repository_name
        self.branch_name = branch_name
        self.endpoint_name = endpoint_name
        self.logger = logger
        self._location: Optional[str] = None
        self._endpoint = None
        self._client: Union[None, API, FlightClient] = None
        self._endpoint_has_rest_sample_data: Optional[bool] = False
        self._endpoint_has_arrow_sample_data: Optional[bool] = False

    @property
    def local_endpoint(self) -> str:
        raise NotImplementedError

    @classmethod
    def for_url(cls, api_key: str, url: str, endpoint_name: str):
        raise NotImplementedError

    @staticmethod
    def format_url(url: Optional[str]) -> str:
        raise NotImplementedError

    @property
    def endpoint_has_rest_sample_data(self) -> Optional[bool]:
        return self._endpoint_has_rest_sample_data

    @endpoint_has_rest_sample_data.setter
    def endpoint_has_rest_sample_data(self, value: bool) -> None:
        self._endpoint_has_rest_sample_data = value

    @property
    def endpoint_has_arrow_sample_data(self) -> Optional[bool]:
        return self._endpoint_has_arrow_sample_data

    @endpoint_has_arrow_sample_data.setter
    def endpoint_has_arrow_sample_data(self, value: bool):
        self._endpoint_has_arrow_sample_data = value

    @property
    def client(self) -> Union[API, FlightClient]:
        return self._client

    @client.setter
    def client(self, client: Union[API, FlightClient]):
        self._client = client

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        self._location = value

    def set_client_and_location(self, location: str, client: Union[API, FlightClient]):
        self._location = location
        self._client = client

    def get_deployment_location(self):
        deployment = self.taktile_client.get_deployment_by_branch_name(
            repository_name=self.repository_name, branch_name=self.branch_name,
        )
        return self.format_url(deployment.public_docs_url)

    def get_endpoint_and_location(self) -> str:
        if self.local:
            location = self.local_endpoint
        else:
            location = self._get_endpoint_location()
        return location

    def _set_data_available(self, endpoint: Endpoint) -> None:
        self.endpoint_has_rest_sample_data = endpoint.has_rest_sample_data
        self.endpoint_has_arrow_sample_data = endpoint.has_arrow_sample_data

    def _get_endpoint_location(self) -> str:
        deployment, endpoint = self.taktile_client.get_endpoint_by_name(
            repository_name=self.repository_name,
            endpoint_name=self.endpoint_name,
            branch_name=self.branch_name,
        )
        self._set_data_available(endpoint=endpoint)
        return self.format_url(deployment.public_docs_url)

    def list_deployments(self):
        raise NotImplementedError

    def get_sample_data(self):
        raise NotImplementedError

    def get_schema(self, *args, **kwargs):
        raise NotImplementedError

    def health(self):
        raise NotImplementedError
