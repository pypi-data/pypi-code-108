"""
Base classes for Rest and Arrow client
"""
import typing as t

from taktile_client.config import collect_api_key, settings
from taktile_client.deployment_api import DeploymentApiClient

EndpointClass = t.TypeVar("EndpointClass")


class ApiKeyException(Exception):
    """Exception related to problems with the API key"""


class Client(t.Generic[EndpointClass]):
    """
    Abstract base client for talking to models deployed with Taktile.

    Parameters
    ----------
    api_key : str
        api_key to use
    repository_name : str
        repository_name of the form "taktile-org/repo-name"
    branch_name : str
        branch_name either "main" or "refs/heads/main"
    """

    def __init__(
        self,
        repository_name: str,
        branch_name: str,
        api_key: t.Optional[str] = None,
        headers: t.Optional[t.Dict[str, str]] = None,
    ):
        if api_key is None:
            api_key = collect_api_key()

        if not api_key and not settings.DEBUG:
            raise ApiKeyException(
                "No API key found in environment (TAKTILE_API_KEY) or "
                f"config file ({settings.TAKTILE_CONFIG_FILE.absolute()}). "
                "Please specify an API key when instantiating the client."
            )

        self._api_key = api_key
        principal, repository = repository_name.split("/")
        client = DeploymentApiClient(api_key=api_key, headers=headers)
        host = client.get_host(
            principal=principal, repository=repository, branch=branch_name
        )

        url = self._url_from_host(host)

        self._endpoints = self._initalize_endpoints(url, api_key)

    def _url_from_host(self, host: str) -> str:
        raise NotImplementedError

    def _initalize_endpoints(
        self, url: str, api_key: t.Optional[str]
    ) -> EndpointClass:
        raise NotImplementedError

    @classmethod
    def from_url(
        cls: t.Type["Client[t.Any]"], url: str, api_key: t.Optional[str]
    ) -> "Client[t.Any]":
        """
        Instantiate client from url

        Parameters
        ----------
        api_key : str
            api_key to use
        url : str
            url where the model is deployed

        Returns
        -------
        Client

        """
        obj = t.cast("Client[t.Any]", cls.__new__(cls))
        obj._endpoints = obj._initalize_endpoints(url, api_key)
        return obj

    @property
    def endpoints(self) -> EndpointClass:
        """
        The arrow endpoints

        Returns
        -------
        ArrowEndpoints

        """
        return self._endpoints
