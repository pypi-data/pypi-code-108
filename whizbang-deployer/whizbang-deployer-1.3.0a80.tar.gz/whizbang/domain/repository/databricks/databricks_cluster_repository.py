import abc
from time import sleep

from whizbang.domain.models.databricks.databricks_cluster import DatabricksCluster
from whizbang.domain.repository.databricks.databricks_repository_base import DatabricksRepositoryBase, IDatabricksRepository
from whizbang.data.databricks.databricks_client_args import DatabricksClientArgs
from whizbang.data.databricks.databricks_cluster_context import IDatabricksClusterContext
from whizbang.data.databricks.databricks_context_factory import IDatabricksContextFactory
from whizbang.domain.shared_types.databricks_api_type import DatabricksApiType
from whizbang.util.deployment_helpers import timestamp

import logging
_log = logging.getLogger(__name__) 

class IDatabricksClusterRepository(IDatabricksRepository):

    @abc.abstractmethod
    def get_cluster(self, client_args: DatabricksClientArgs, cluster_id: str):
        """"""

    @abc.abstractmethod
    def start_cluster(self, client_args: DatabricksClientArgs, cluster: DatabricksCluster):
        """"""

    @abc.abstractmethod
    def stop_cluster(self, client_args, cluster: DatabricksCluster):
        """"""

    @abc.abstractmethod
    def pin_cluster(self, client_args, cluster: DatabricksCluster):
        """"""


class DatabricksClusterRepository(DatabricksRepositoryBase, IDatabricksClusterRepository):
    def __init__(self, context_factory: IDatabricksContextFactory):
        DatabricksRepositoryBase.__init__(self, databricks_context_factory=context_factory)
        self.terminated = 'TERMINATED'
        self.running = 'RUNNING'

    @property
    def context_type(self) -> str: return DatabricksApiType.cluster

    def create(self, client_args: DatabricksClientArgs, t_object: DatabricksCluster):
        context: IDatabricksClusterContext = self._get_context(client_args)

        result = context.create_cluster(
            cluster_dict=t_object.cluster_dict
        )
        return result

    def get(self, client_args: DatabricksClientArgs) -> 'list[DatabricksCluster]':
        context: IDatabricksClusterContext = self._get_context(client_args)
        result = context.get_clusters()
        if result != {}:
            result = result['clusters']
        existing_clusters = []
        for cluster in result:
            existing_clusters.append(DatabricksCluster(cluster))
        return existing_clusters

    def update(self, client_args: DatabricksClientArgs, t_object: DatabricksCluster):
        context: IDatabricksClusterContext = self._get_context(client_args)
        cluster_id = t_object.cluster_dict['cluster_id']
        state = self.__wait_till_ready(context=context, cluster_id=cluster_id)
        result = context.update_cluster(
            cluster_dict=t_object.cluster_dict
        )
        if state == 'TERMINATED':
            self.__wait_till_ready(context=context, cluster_id=cluster_id)
            self.stop_cluster(client_args=client_args, cluster=t_object)
        return result

    def get_cluster(self, client_args: DatabricksClientArgs, cluster_id: str):
        context: IDatabricksClusterContext = self._get_context(client_args)
        result = context.get_cluster(cluster_id=cluster_id)
        return result

    def __wait_till_ready(self, context, cluster_id: str):
        state = None
        
        while state is None:
            cluster = context.get_cluster(cluster_id)
            if cluster['state'] == self.running or cluster['state'] == self.terminated:
                state = cluster['state']
                break
            _log.debug(timestamp(f'Waiting for cluster with id {cluster_id} to start.'))
            sleep(5)
            
        return state

    def start_cluster(self, client_args: DatabricksClientArgs, cluster: DatabricksCluster):
        cluster_id = cluster.cluster_dict['cluster_id']
        context: IDatabricksClusterContext = self._get_context(client_args)
        cluster = context.get_cluster(cluster_id)
        result = None
        if cluster['state'] == self.terminated:
            context.start_cluster(cluster_id=cluster_id)
            self.__wait_till_ready(context=context, cluster_id=cluster_id)
            result = 'terminate'
        elif cluster['state'] != self.running:
            result = self.__wait_till_ready(context=context, cluster_id=cluster_id)
            if result == self.terminated:
                context.start_cluster(cluster_id=cluster_id)
                self.__wait_till_ready(context=context, cluster_id=cluster_id)
                result = 'terminate'
            else:
                result = None
        return result

    def stop_cluster(self, client_args: DatabricksClientArgs, cluster: DatabricksCluster):
        cluster_id = cluster.cluster_dict['cluster_id']
        context: IDatabricksClusterContext = self._get_context(client_args)
        result = context.stop_cluster(cluster_id=cluster_id)
        return result

    def pin_cluster(self, client_args, cluster: DatabricksCluster):
        cluster_id = cluster.cluster_dict['cluster_id']
        context: IDatabricksClusterContext = self._get_context(client_args)
        result = context.pin_cluster(cluster_id=cluster_id)
        return result
