import abc

from whizbang.data.databricks.databricks_client_args import DatabricksClientArgs
from whizbang.domain.manager.databricks.databricks_manager_base import DatabricksManagerBase, IDatabricksManager
from whizbang.domain.manager.databricks.databricks_pool_manager import IDatabricksPoolManager
from whizbang.domain.models.databricks.databricks_cluster import DatabricksCluster
from whizbang.domain.models.databricks.databricks_pool import DatabricksPool
from whizbang.domain.models.databricks.databricks_secret_scope import DatabricksSecretScope
from whizbang.domain.repository.databricks.databricks_cluster_repository import IDatabricksClusterRepository
from whizbang.util.json_helpers import jsonpath_parse, jsonpath_set, update_json_values


class IDatabricksClusterManager(IDatabricksManager):
    @abc.abstractmethod
    def get_cluster(self, client_args: DatabricksClientArgs, cluster_id: str):
        """"""

    @abc.abstractmethod
    def start_cluster(self, client_args, cluster: DatabricksCluster):
        """"""

    @abc.abstractmethod
    def stop_cluster(self, client_args, cluster: DatabricksCluster):
        """"""

    @abc.abstractmethod
    def pin_cluster(self, client_args, cluster: DatabricksCluster):
        """"""

    @staticmethod
    @abc.abstractmethod
    def update_cluster_env_variables(cluster_fields: dict, cluster: DatabricksCluster):
        """"""


class DatabricksClusterManager(DatabricksManagerBase, IDatabricksClusterManager):
    def __init__(self, repository: IDatabricksClusterRepository, pool_manager: IDatabricksPoolManager):
        self.pool_manager = pool_manager
        DatabricksManagerBase.__init__(self, repository)
        self.repository: IDatabricksClusterRepository

    @staticmethod
    def update_cluster_env_variables(cluster_fields: dict, cluster: DatabricksCluster):
        if cluster_fields is None:
            return
        update_json_values(new_values=cluster_fields, existing_dictionary=cluster.cluster_dict)

    def save(self, client_args: DatabricksClientArgs, new_cluster: DatabricksCluster):
        existing_clusters: 'list[DatabricksCluster]' = self.repository.get(client_args=client_args)
        existing_pools: 'list[DatabricksPool]' = self.pool_manager.get(client_args=client_args)

        # check if cluster is part of an instance pool
        if 'instance_pool_name' in new_cluster.cluster_dict:
            for existing_pool in existing_pools:
                if new_cluster.cluster_dict['instance_pool_name'] == existing_pool.pool_name:
                    new_cluster.cluster_dict['instance_pool_id'] = existing_pool.pool_dict.get('instance_pool_id')

        for existing_cluster in existing_clusters:
            if new_cluster.cluster_name == existing_cluster.cluster_name:
                new_cluster.cluster_dict['cluster_id'] = existing_cluster.cluster_dict['cluster_id']
                return self.repository.update(client_args=client_args, t_object=new_cluster)

        result = self.repository.create(client_args=client_args, t_object=new_cluster)
        new_cluster.cluster_dict['cluster_id'] = result.get('cluster_id')

        return result

    def get_cluster(self, client_args: DatabricksClientArgs, cluster_id: str):
        return self.repository.get_cluster(client_args=client_args, cluster_id=cluster_id)

    def start_cluster(self, client_args: DatabricksClientArgs, cluster: DatabricksCluster):
        return self.repository.start_cluster(client_args=client_args, cluster=cluster)

    def stop_cluster(self, client_args: DatabricksClientArgs, cluster: DatabricksCluster):
        return self.repository.stop_cluster(client_args=client_args, cluster=cluster)

    def pin_cluster(self, client_args: DatabricksClientArgs, cluster: DatabricksCluster):
        return self.repository.pin_cluster(client_args=client_args, cluster=cluster)
