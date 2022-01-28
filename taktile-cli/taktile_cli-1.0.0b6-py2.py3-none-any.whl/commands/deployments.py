from typing import List, Optional

from pydantic import UUID4

from tktl.commands import BaseDeploymentApiCommand
from tktl.core.schemas.deployment import DeploymentBase
from tktl.core.schemas.repository import Endpoint


class GetDeployments(BaseDeploymentApiCommand):
    def execute(
        self,
        repository_id: Optional[UUID4],
        repository_name: Optional[str],
        repository_owner: Optional[str],
        git_hash: Optional[str],
        branch_name: Optional[str],
        status_name: Optional[str],
        return_all: bool,
    ):
        return self.client.get_deployments(
            repository_id=repository_id,
            repository_name=repository_name,
            repository_owner=repository_owner,
            git_hash=git_hash,
            branch_name=branch_name,
            status_name=status_name,
            return_all=return_all,
        )


class GetRepositories(BaseDeploymentApiCommand):
    def execute(
        self, repository_name: str, repository_owner: str, return_all: bool = False,
    ):
        return self.client.get_repositories(
            repository_name=repository_name,
            repository_owner=repository_owner,
            return_all=return_all,
        )


class GetEndpoints(BaseDeploymentApiCommand):
    def execute(
        self,
        deployment_id: UUID4,
        repository_name: str,
        repository_owner: str,
        git_hash: str,
        branch_name: str,
        status_name: str,
        endpoint_name: str,
        endpoint_kind: str,
        return_all: bool = False,
    ) -> List[Endpoint]:
        return self.client.get_endpoints(
            deployment_id=deployment_id,
            repository_name=repository_name,
            repository_owner=repository_owner,
            git_hash=git_hash,
            branch_name=branch_name,
            status_name=status_name,
            endpoint_name=endpoint_name,
            endpoint_kind=endpoint_kind,
            return_all=return_all,
        )


class DeleteDeployment(BaseDeploymentApiCommand):
    def execute(self, deployment_id: UUID4) -> DeploymentBase:
        return self.client.delete_deployment(deployment_id=deployment_id)


class ListDeploymentsCommand(BaseDeploymentApiCommand):
    WAITING_FOR_RESPONSE_MESSAGE = "Waiting for data..."

    def execute(self, **kwargs):
        # TODO: implement list deployments and show as table

        # with halo.Halo(text=self.WAITING_FOR_RESPONSE_MESSAGE, spinner="dots"):
        #     instances = self._get_instances(**kwargs)

        raise NotImplementedError


class GetDeploymentDetails(BaseDeploymentApiCommand):
    def _get_table_data(self, instance):
        pass

    def execute(self, id_):
        # TODO: get deployment details
        raise NotImplementedError


class GetDeploymentMetricsCommand(BaseDeploymentApiCommand):
    def execute(
        self, deployment_id, start, end, interval, built_in_metrics, *args, **kwargs
    ):
        # TODO: stream metrics
        raise NotImplementedError


class StreamDeploymentMetricsCommand(BaseDeploymentApiCommand):
    def execute(self, **kwargs):
        # TODO: stream metrics
        raise NotImplementedError


class DeploymentLogsCommand(BaseDeploymentApiCommand):
    def execute(self, **kwargs):
        # TODO: get logs
        raise NotImplementedError

    def _get_log_row_string(self, id, log):
        raise NotImplementedError

    def _make_table(self, logs, id):
        raise NotImplementedError
