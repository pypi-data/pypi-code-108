import abc

from whizbang.data.databricks.databricks_client_args import DatabricksClientArgs
from whizbang.domain.manager.databricks.databricks_cluster_manager import IDatabricksClusterManager
from whizbang.domain.manager.databricks.databricks_manager_base import DatabricksManagerBase, IDatabricksManager
from whizbang.domain.models.databricks.databricks_library import DatabricksLibrary
from whizbang.domain.models.databricks.databricks_cluster import DatabricksCluster
from whizbang.domain.repository.databricks.databricks_library_repository import IDatabricksLibraryRepository


class IDatabricksLibraryManager(IDatabricksManager):
    @abc.abstractmethod
    def cluster_status(self, client_args: DatabricksClientArgs, cluster: DatabricksCluster):
        """"""


class DatabricksLibraryManager(DatabricksManagerBase, IDatabricksLibraryManager):
    def __init__(self, repository: IDatabricksLibraryRepository, cluster_manager: IDatabricksClusterManager):
        self.cluster_manager = cluster_manager
        DatabricksManagerBase.__init__(self, repository)
        self.repository: IDatabricksLibraryRepository

    def __skip_existing_libraries(self, client_args: DatabricksClientArgs,
                                  libraries: DatabricksLibrary,
                                  cluster: DatabricksCluster):
        libraries_to_install: DatabricksLibrary = libraries
        cluster_status: dict = self.cluster_status(client_args=client_args, cluster=cluster)
        if 'library_statuses' in cluster_status.keys():
            for status in cluster_status['library_statuses']:
                for library in libraries.library_dict['libraries']:
                    if library == status['library'] and \
                            (status['status'] == 'INSTALLED' or
                             status['status'] == 'PENDING' or
                             status['status'] == 'INSTALLING'):
                        libraries_to_install.library_dict['libraries'].remove(library)
        return libraries_to_install

    def save(self, client_args, new_libraries: DatabricksLibrary):
        existing_clusters: 'list[DatabricksCluster]' = self.cluster_manager.get(client_args=client_args)
        list_to_terminate: 'list[DatabricksCluster]' = []
        if new_libraries.install_all is True:
            for existing_cluster in existing_clusters:
                result = self.cluster_manager.start_cluster(client_args=client_args, cluster=existing_cluster)
                new_libraries.library_dict.update({'cluster_id': existing_cluster.cluster_dict['cluster_id']})
                self.repository.create(client_args=client_args, t_object=new_libraries)
                if result is not None:
                    list_to_terminate.append(existing_cluster)
        else:
            for existing_cluster in existing_clusters:
                if existing_cluster.cluster_dict['cluster_name'] == new_libraries.library_dict['cluster_name']:
                    new_libraries: DatabricksLibrary = self.__skip_existing_libraries(client_args=client_args,
                                                                                      libraries=new_libraries,
                                                                                      cluster=existing_cluster)
                    if len(new_libraries.library_dict['libraries']) > 0:
                        result = self.cluster_manager.start_cluster(client_args=client_args, cluster=existing_cluster)
                        new_libraries.library_dict.update(
                            {'cluster_id': existing_cluster.cluster_dict['cluster_id']})
                        self.repository.create(client_args=client_args, t_object=new_libraries)
                        if result is not None:
                            list_to_terminate.append(existing_cluster)
        for cluster in list_to_terminate:
            self.cluster_manager.stop_cluster(client_args=client_args, cluster=cluster)

    def cluster_status(self, client_args: DatabricksClientArgs, cluster: DatabricksCluster):
        return self.repository.cluster_status(client_args=client_args, cluster=cluster)
