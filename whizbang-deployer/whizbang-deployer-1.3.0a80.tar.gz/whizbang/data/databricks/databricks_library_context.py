import abc

from databricks_cli.libraries.api import LibrariesApi
from databricks_cli.sdk import ApiClient

from whizbang.data.databricks.databricks_context_base import DatabricksContextBase, IDatabricksContextBase


class IDatabricksLibraryContext(IDatabricksContextBase):
    """"""

    @abc.abstractmethod
    def install_library(self, cluster_id, library_dict):
        """"""

    @abc.abstractmethod
    def cluster_status(self, cluster_id):
        """"""


class DatabricksLibraryContext(DatabricksContextBase, IDatabricksLibraryContext):
    def __init__(self, api_client: ApiClient, api):
        DatabricksContextBase.__init__(self, api_client=api_client, api=api)

    def install_library(self, cluster_id, library_dict):
        def _create_cluster(api: LibrariesApi, cluster_id, library_dict):

            return api.install_libraries(
                cluster_id=cluster_id,
                libraries=library_dict
            )
        return self._execute(func=_create_cluster, cluster_id=cluster_id, library_dict=library_dict)

    def cluster_status(self, cluster_id):
        def _cluster_status(api: LibrariesApi, cluster_id):
            return api.cluster_status(cluster_id=cluster_id)

        return self._execute(func=_cluster_status, cluster_id=cluster_id)
