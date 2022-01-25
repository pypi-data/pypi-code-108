import abc
from databricks_cli.sdk import ApiClient, ClusterService
from databricks_cli.clusters.api import ClusterApi

from whizbang.data.databricks.databricks_context_base import DatabricksContextBase, IDatabricksContextBase


class IDatabricksClusterContext(IDatabricksContextBase):
    """"""

    @abc.abstractmethod
    def create_cluster(self, cluster_dict):
        """"""

    @abc.abstractmethod
    def get_clusters(self):
        """"""

    @abc.abstractmethod
    def update_cluster(self, cluster_dict):
        """"""

    @abc.abstractmethod
    def start_cluster(self, cluster_id):
        """"""

    @abc.abstractmethod
    def stop_cluster(self, cluster_id):
        """"""

    @abc.abstractmethod
    def get_cluster(self, cluster_id):
        """"""

    @abc.abstractmethod
    def pin_cluster(self, cluster_id):
        """"""


class DatabricksClusterContext(DatabricksContextBase, IDatabricksClusterContext):
    def __init__(self, api_client: ApiClient, api, service: ClusterService):
        DatabricksContextBase.__init__(self, api_client=api_client, api=api)
        self.service = service

    def create_cluster(self, cluster_dict):
        def _create_cluster(api: ClusterApi, cluster_dict):
            return api.create_cluster(json=cluster_dict)

        return self._execute(func=_create_cluster, cluster_dict=cluster_dict)

    def get_clusters(self):
        def _get(api: ClusterApi):
            return api.list_clusters()

        return self._execute(func=_get)

    def update_cluster(self, cluster_dict):
        def _update_cluster(api: ClusterApi, cluster_dict):
            return api.edit_cluster(json=cluster_dict)

        return self._execute(func=_update_cluster, cluster_dict=cluster_dict)

    def start_cluster(self, cluster_id):
        def _start_cluster(api: ClusterApi, cluster_id):
            return api.start_cluster(cluster_id=cluster_id)

        return self._execute(func=_start_cluster, cluster_id=cluster_id)

    def stop_cluster(self, cluster_id):
        def _stop_cluster(api: ClusterApi, cluster_id):
            return api.delete_cluster(cluster_id=cluster_id)

        return self._execute(func=_stop_cluster, cluster_id=cluster_id)

    def get_cluster(self, cluster_id):
        def _get_cluster(api: ClusterApi, cluster_id):
            return api.get_cluster(cluster_id=cluster_id)

        return self._execute(func=_get_cluster, cluster_id=cluster_id)

    def pin_cluster(self, cluster_id):
        def _pin_cluster(api: ClusterApi, cluster_id, service: ClusterService):
            return service.pin_cluster(cluster_id=cluster_id)

        return self._execute(func=_pin_cluster, cluster_id=cluster_id, service=self.service)
