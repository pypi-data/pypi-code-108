from whizbang.domain.manager.databricks.databricks_manager_base import DatabricksManagerBase, IDatabricksManager
from whizbang.domain.models.databricks.databricks_pool import DatabricksPool
from whizbang.domain.repository.databricks.databricks_pool_repository import IDatabricksPoolRepository


class IDatabricksPoolManager(IDatabricksManager):
    """"""


class DatabricksPoolManager(DatabricksManagerBase, IDatabricksPoolManager):
    def __init__(self, repository: IDatabricksPoolRepository):
        DatabricksManagerBase.__init__(self, repository)

    def save(self, client_args, new_pool: DatabricksPool):
        existing_pools: 'list[DatabricksPool]' = self.repository.get(client_args=client_args)
        for existing_pool in existing_pools:
            if new_pool.pool_name == existing_pool.pool_name:
                new_pool.pool_dict.update({'instance_pool_id': existing_pool.pool_dict['instance_pool_id']})
                return self.repository.update(client_args=client_args, t_object=new_pool)
        return self.repository.create(client_args=client_args, t_object=new_pool)
