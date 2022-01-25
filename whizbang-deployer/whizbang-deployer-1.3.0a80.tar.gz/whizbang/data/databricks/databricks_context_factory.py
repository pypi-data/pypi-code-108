import abc
import logging

from databricks_cli.clusters.api import ClusterApi
from databricks_cli.libraries.api import LibrariesApi
from databricks_cli.sdk import ApiClient, ClusterService, JobsService
from databricks_cli.secrets.api import SecretApi
from databricks_cli.workspace.api import WorkspaceApi
from databricks_cli.jobs.api import JobsApi
from databricks_cli.instance_pools.api import InstancePoolsApi
from databricks_cli.tokens.api import TokensApi

from whizbang.core.context_factory_base import ContextFactoryBase, IContextFactory
from whizbang.data.az_cli_context import AzCliContext
from whizbang.data.databricks.databricks_client_args import DatabricksClientArgs
from whizbang.data.databricks.databricks_cluster_context import DatabricksClusterContext
from whizbang.data.databricks.databricks_job_context import DatabricksJobContext
from whizbang.data.databricks.databricks_library_context import DatabricksLibraryContext
from whizbang.data.databricks.databricks_pool_context import DatabricksPoolContext
from whizbang.data.databricks.databricks_secret_context import DatabricksSecretContext
from whizbang.data.databricks.databricks_token_context import DatabricksTokenContext
from whizbang.data.databricks.databricks_workspace_context import DatabricksWorkspaceContext
from whizbang.domain.shared_types.databricks_api_type import DatabricksApiType

_log = logging.getLogger(__name__) 

class IDatabricksContextFactory(IContextFactory, metaclass=abc.ABCMeta):
    """The DatabricksContextFactory interface"""

    @abc.abstractmethod
    def get_context(self, context_args: DatabricksClientArgs, api_type):
        """"""


class DatabricksContextFactory(ContextFactoryBase, IDatabricksContextFactory):
    def __init__(self, az_cli_context: AzCliContext):
        self._az_cli_context = az_cli_context

    def get_context(self, context_args: DatabricksClientArgs, api_type):
        if context_args.token is None:
            context_args.token = self._get_token()

        client = ApiClient(host=context_args.host, token=context_args.token)

        try:
            if api_type == DatabricksApiType.workspace:
                api = WorkspaceApi(client)
                return DatabricksWorkspaceContext(client, api)
            if api_type == DatabricksApiType.secret:
                api = SecretApi(client)
                return DatabricksSecretContext(client, api)
            if api_type == DatabricksApiType.job:
                api = JobsApi(client)
                service = JobsService(client)
                return DatabricksJobContext(api_client=client, api=api, service=service)
            if api_type == DatabricksApiType.cluster:
                api = ClusterApi(client)
                service = ClusterService(client)
                return DatabricksClusterContext(api_client=client, api=api, service=service)
            if api_type == DatabricksApiType.pool:
                api = InstancePoolsApi(client)
                return DatabricksPoolContext(client, api)
            if api_type == DatabricksApiType.library:
                api = LibrariesApi(client)
                return DatabricksLibraryContext(client, api)
            if api_type == DatabricksApiType.token:
                api = TokensApi(client)
                return DatabricksTokenContext(client, api)

            raise AssertionError(f'api type {api_type} not found')
        except AssertionError as _e:
            _log.exception(_e)
            raise _e

    def _get_token(self) -> str:
        token_result = self._az_cli_context.execute(
            'account get-access-token --resource 2ff814a6-3304-4ab8-85cb-cd0e6f879c1d').results
        token = token_result['accessToken']
        return token
