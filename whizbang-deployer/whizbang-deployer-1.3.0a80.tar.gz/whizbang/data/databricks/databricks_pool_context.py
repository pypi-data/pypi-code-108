import abc

from databricks_cli.instance_pools.api import InstancePoolsApi
from databricks_cli.sdk import ApiClient

from whizbang.data.databricks.databricks_context_base import IDatabricksContextBase, DatabricksContextBase


class IDatabricksPoolContext(IDatabricksContextBase):
    """"""

    @abc.abstractmethod
    def create_pool(self, pool_dict):
        """"""

    @abc.abstractmethod
    def get_pools(self):
        """"""

    @abc.abstractmethod
    def update_pool(self, pool_dict):
        """"""


class DatabricksPoolContext(DatabricksContextBase, IDatabricksPoolContext):
    def __init__(self, api_client: ApiClient, api):
        DatabricksContextBase.__init__(self, api_client=api_client, api=api)

    def create_pool(self, pool_dict):
        def _create_pool(api: InstancePoolsApi, pool_dict):
            return api.create_instance_pool(json=pool_dict)

        return self._execute(func=_create_pool, pool_dict=pool_dict)

    def get_pools(self):
        def _get(api: InstancePoolsApi):
            return api.list_instance_pools()

        return self._execute(func=_get)

    def update_pool(self, pool_dict):
        def _update_pool(api: InstancePoolsApi, pool_dict):
            return api.edit_instance_pool(json=pool_dict)

        return self._execute(func=_update_pool, pool_dict=pool_dict)
