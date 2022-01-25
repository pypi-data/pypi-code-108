import abc

from whizbang.data.databricks.databricks_client_args import DatabricksClientArgs
from whizbang.data.databricks.databricks_context_factory import IDatabricksContextFactory
from whizbang.data.databricks.databricks_library_context import IDatabricksLibraryContext
from whizbang.domain.models.databricks.databricks_cluster import DatabricksCluster
from whizbang.domain.models.databricks.databricks_library import DatabricksLibrary
from whizbang.domain.repository.databricks.databricks_repository_base import DatabricksRepositoryBase, IDatabricksRepository
from whizbang.domain.shared_types.databricks_api_type import DatabricksApiType


class IDatabricksLibraryRepository(IDatabricksRepository):
    @abc.abstractmethod
    def cluster_status(self, client_args: DatabricksClientArgs, cluster: DatabricksCluster):
        """"""


class DatabricksLibraryRepository(DatabricksRepositoryBase, IDatabricksLibraryRepository):
    def __init__(self, context_factory: IDatabricksContextFactory):
        DatabricksRepositoryBase.__init__(self, databricks_context_factory=context_factory)

    @property
    def context_type(self) -> str: return DatabricksApiType.library

    def create(self, client_args: DatabricksClientArgs, t_object: DatabricksLibrary):
        context: IDatabricksLibraryContext = self._get_context(client_args)
        result = context.install_library(
            cluster_id=t_object.library_dict['cluster_id'],
            library_dict=t_object.library_dict['libraries']
        )
        return result

    def cluster_status(self, client_args: DatabricksClientArgs, cluster: DatabricksCluster):
        cluster_id = cluster.cluster_dict['cluster_id']
        context: IDatabricksLibraryContext = self._get_context(client_args)
        result = context.cluster_status(cluster_id=cluster_id)
        return result

    def get(self, client_args: DatabricksClientArgs):
        """Not implemented"""
        raise NotImplementedError()

    def update(self, client_args: DatabricksClientArgs, t_object):
        """Not implemented"""
        raise NotImplementedError()

