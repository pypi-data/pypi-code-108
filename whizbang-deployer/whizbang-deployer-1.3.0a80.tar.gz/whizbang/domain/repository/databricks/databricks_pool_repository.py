from whizbang.data.databricks.databricks_client_args import DatabricksClientArgs
from whizbang.data.databricks.databricks_context_factory import IDatabricksContextFactory
from whizbang.data.databricks.databricks_pool_context import IDatabricksPoolContext
from whizbang.domain.models.databricks.databricks_pool import DatabricksPool
from whizbang.domain.repository.databricks.databricks_repository_base import DatabricksRepositoryBase, IDatabricksRepository
from whizbang.domain.shared_types.databricks_api_type import DatabricksApiType


class IDatabricksPoolRepository(IDatabricksRepository):
    """"""


class DatabricksPoolRepository(DatabricksRepositoryBase, IDatabricksPoolRepository):
    def __init__(self, context_factory: IDatabricksContextFactory):
        DatabricksRepositoryBase.__init__(self, databricks_context_factory=context_factory)

    @property
    def context_type(self) -> str: return DatabricksApiType.pool

    def create(self, client_args: DatabricksClientArgs, t_object: DatabricksPool):
        context: IDatabricksPoolContext = self._get_context(client_args)

        result = context.create_pool(
            pool_dict=t_object.pool_dict
        )
        return result

    def get(self, client_args: DatabricksClientArgs) -> 'list[DatabricksPool]':
        context: IDatabricksPoolContext = self._get_context(client_args)
        result = context.get_pools()
        if result != {}:
            result = result['instance_pools']
        existing_pools = []
        for pool in result:
            existing_pools.append(DatabricksPool(pool))
        return existing_pools

    def update(self, client_args: DatabricksClientArgs, t_object: DatabricksPool):
        context: IDatabricksPoolContext = self._get_context(client_args)
        result = context.update_pool(
            pool_dict=t_object.pool_dict
        )
        return result
