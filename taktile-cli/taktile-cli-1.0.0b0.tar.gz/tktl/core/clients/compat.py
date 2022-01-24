import typing as t
from urllib.parse import urlsplit

from packaging import version
from taktile_client import ArrowClient as TaktileClientArrowClient
from taktile_client.client import ApiKeyException, Client
from taktile_client.config import collect_api_key, settings
from taktile_client.deployment_api import DeploymentApiClient
from taktile_client.model import Model

from tktl.core.clients.future.arrow import ArrowClient as FutureArrowClient


# TODO: delete this class in release 1.1.0 and replace it with taktile_client.ArrowClient
class ArrowClient:
    def __init__(
        self,
        api_key: t.Optional[str],
        repository_name: t.Optional[str],
        branch_name: t.Optional[str],
        url: t.Optional[str] = None,
    ):
        api_key = api_key or collect_api_key()
        if not api_key:
            raise ApiKeyException(
                "No API key found in environment (TAKTILE_API_KEY) or "
                f"config file ({settings.TAKTILE_CONFIG_FILE}). "
                "Please specify an API key when instantiating the client."
            )

        if repository_name and branch_name:
            rest_url = self._rest_url_from_repo_and_branch(
                repository_name, branch_name, api_key
            )
        elif url:
            rest_url = self._rest_url_from_grpc_url(url)
        else:
            raise ValueError(
                "Either repository_name and branch_name or url must be specified."
            )

        taktile_cli_version = self._fetch_taktile_cli_version(rest_url, api_key)
        client: t.Union[TaktileClientArrowClient, FutureArrowClient, Client[t.Any]]
        if taktile_cli_version < version.parse("1.0.0"):
            if repository_name and branch_name:
                client = FutureArrowClient(
                    repository_name=repository_name,
                    branch_name=branch_name,
                    api_key=api_key,
                )
            elif url:
                client = FutureArrowClient(
                    repository_name="", branch_name="", api_key=api_key, url=url
                )
            else:
                raise ValueError(
                    "Either repository_name and branch_name or url must be specified."
                )

        else:
            if repository_name and branch_name:
                client = TaktileClientArrowClient(
                    repository_name=repository_name,
                    branch_name=branch_name,
                    api_key=api_key,
                )
            elif url:
                client = TaktileClientArrowClient.from_url(url=url, api_key=api_key)
            else:
                raise ValueError(
                    "Either repository_name and branch_name or url must be specified."
                )

        self.endpoints = client.endpoints

    @classmethod
    def _fetch_taktile_cli_version(
        cls, rest_url: str, api_key: t.Optional[str]
    ) -> t.Union[version.Version, version.LegacyVersion]:
        info = Model(url=rest_url, api_key=api_key).get_info()
        return version.parse(info.taktile_cli)

    @classmethod
    def _rest_url_from_repo_and_branch(
        cls, repository_name: str, branch_name: str, api_key: t.Optional[str]
    ) -> str:
        principal, repository = repository_name.split("/")
        client = DeploymentApiClient(api_key=api_key, headers=None)
        host = client.get_host(
            principal=principal, repository=repository, branch=branch_name
        )
        if settings.DEBUG:
            return f"http://{host}"
        return f"https://{host}"

    @classmethod
    def _rest_url_from_grpc_url(cls, url: str):
        host = urlsplit(url).netloc
        if settings.DEBUG:
            return f"http://{host}"
        return f"https://{host}"

    @classmethod
    def from_url(cls, url: str, api_key: t.Optional[str]) -> "ArrowClient":
        return cls(api_key, url=url, repository_name=None, branch_name=None)
