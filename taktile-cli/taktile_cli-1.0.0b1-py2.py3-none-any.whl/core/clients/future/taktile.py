import typing as t
from json import JSONDecodeError

from pydantic import UUID4

from tktl.constants import URL_UNAVAILABLE
from tktl.core.clients.future.http import API
from tktl.core.clients.http_client import interpret_response
from tktl.core.clients.utils import (
    filter_deployments,
    filter_endpoints,
    filter_repositories,
)
from tktl.core.config import settings
from tktl.core.exceptions import APIClientException, TaktileSdkError
from tktl.core.loggers import LOG
from tktl.core.schemas.deployment import DeploymentBase
from tktl.core.schemas.repository import (
    Endpoint,
    Repository,
    RepositoryDeployment,
    RepositoryList,
    _format_http_url,
)
from tktl.core.t import DeploymentStatesT
from tktl.core.utils import flatten, lru_cache


class DeploymentApiClient(API):
    SCHEME: str

    def __init__(self, api_key: str):
        super().__init__(settings.DEPLOYMENT_API_URL, headers={"X-Api-Key": api_key})
        self._api_key = api_key

    @lru_cache(timeout=50, typed=False)
    def __get_repositories(self) -> RepositoryList:
        response = self.get(f"{settings.API_V1_STR}/models")
        return interpret_response(response=response, model=RepositoryList)

    def _get_repositories(self) -> RepositoryList:
        repositories = self.__get_repositories()
        if not repositories:
            raise TaktileSdkError(
                "No repositories found on your account, so no resources can be fetched"
            )
        return repositories

    def get_deployments(
        self,
        repository_id: t.Optional[UUID4],
        git_hash: t.Optional[str],
        branch_name: t.Optional[str],
        status_name: t.Optional[str],
        repository_name: t.Optional[str],
        repository_owner: t.Optional[str],
        return_all: bool,
    ) -> t.Optional[t.List[RepositoryDeployment]]:

        repositories = filter_repositories(
            self._get_repositories().get_repositories(),
            repository_name=repository_name,
            repository_owner=repository_owner,
        )

        if repository_id:
            repo = [r for r in repositories if r.id == repository_id]
            if not repo:
                LOG.warning("No repositories with matching id found")
                return None
            else:
                deployments = repo[0].deployments
        else:
            deployments = flatten([r.deployments for r in repositories])

        if return_all:
            filtered_deployments = deployments
        else:
            filtered_deployments = filter_deployments(
                deployments,
                git_hash=git_hash,
                branch_name=branch_name,
                status_name=status_name,
            )

        def get_number_of_endpoints(deployment: RepositoryDeployment):
            try:
                return len(get_endpoints_for_deployment(deployment))
            except (JSONDecodeError, APIClientException):
                return 0

        endpoints_for_deployment = [
            get_number_of_endpoints(deployment) for deployment in filtered_deployments
        ]
        for e, d in zip(endpoints_for_deployment, filtered_deployments):
            d.n_endpoints = e
        return filtered_deployments

    def get_repositories(
        self,
        repository_name: str = None,
        repository_owner: str = None,
        return_all: bool = False,
    ) -> t.List[Repository]:
        repositories = self._get_repositories().get_repositories()
        if return_all:
            return repositories
        return filter_repositories(
            repositories,
            repository_name=repository_name,
            repository_owner=repository_owner,
        )

    def get_endpoints(
        self,
        deployment_id: UUID4 = None,
        endpoint_kind: str = None,
        endpoint_name: str = None,
        repository_name: str = None,
        repository_owner: str = None,
        git_hash: str = None,
        branch_name: str = None,
        status_name: str = None,
        return_all: bool = False,
    ) -> t.List[Endpoint]:
        repositories = filter_repositories(
            self._get_repositories().get_repositories(),
            repository_name=repository_name,
            repository_owner=repository_owner,
        )
        deployments = filter_deployments(
            deployments=flatten([r.deployments for r in repositories]),
            git_hash=git_hash,
            branch_name=branch_name,
            status_name=status_name,
        )

        if deployment_id:
            deployments = [d for d in deployments if d.id == deployment_id]
            if not deployments:
                LOG.warning(
                    f"No endpoints for deployment with id {deployment_id} found"
                )
        endpoints = flatten(
            [get_endpoints_for_deployment(deployment) for deployment in deployments]
        )
        if return_all:
            return endpoints
        return filter_endpoints(
            endpoints, endpoint_kind=endpoint_kind, endpoint_name=endpoint_name
        )

    def get_deployment_by_branch_name(self, repository_name: str, branch_name: str):
        # owner is guaranteed not to have a slash in it so can split on first occurrence
        owner, name = repository_name.split("/", 1)
        repositories = filter_repositories(
            self._get_repositories().get_repositories(),
            repository_name=name,
            repository_owner=owner,
        )
        if not repositories:
            raise TaktileSdkError(f"No repos named {repository_name} found")

        deployments = filter_deployments(
            deployments=flatten([r.deployments for r in repositories]),
            branch_name=branch_name,
            status_name=DeploymentStatesT.list(),
        )
        if not deployments:
            raise TaktileSdkError("No running deployments found")

        if len(deployments) > 1:
            raise TaktileSdkError(
                "More than one deployment for single branch and repo found. "
                "Exiting, as this should not happen"
            )
        return deployments[0]

    def get_endpoint_by_name(
        self, repository_name: str, branch_name: str, endpoint_name: str
    ) -> t.Tuple[RepositoryDeployment, Endpoint]:
        deployment = self.get_deployment_by_branch_name(
            repository_name=repository_name, branch_name=branch_name
        )
        endpoints = get_endpoints_for_deployment(deployment)
        for endpoint in endpoints:
            if endpoint.name == endpoint_name:
                return deployment, endpoint
        raise TaktileSdkError(f"No endpoint named {endpoint_name} found")

    def delete_deployment(self, deployment_id: UUID4) -> DeploymentBase:
        response = self.delete(f"{settings.API_V1_STR}/deployments/{deployment_id}")
        return interpret_response(response=response, model=DeploymentBase)


def get_endpoints_for_deployment(deployment: RepositoryDeployment) -> t.List[Endpoint]:
    url = _format_http_url(deployment.public_docs_url, docs=False)
    if url == URL_UNAVAILABLE:
        return []
    client = API(api_url=url)
    endpoint = client.get("info")
    endpoint_models = interpret_response(endpoint, Endpoint)
    for endpoint in endpoint_models:
        endpoint.deployment_id = deployment.id
    return endpoint_models
