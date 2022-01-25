from whizbang.data.databricks.databricks_client_args import DatabricksClientArgs
from whizbang.domain.manager.databricks.databricks_manager_base import DatabricksManagerBase, IDatabricksManager
from whizbang.domain.models.databricks.databricks_secret_scope import DatabricksSecretScope

from whizbang.domain.repository.databricks.databricks_secret_scope_repository import DatabricksSecretScopeRepository


class IDatabricksSecretScopeManager(IDatabricksManager):
    """"""


class DatabricksSecretScopeManager(DatabricksManagerBase, IDatabricksSecretScopeManager):
    def __init__(self, repository: DatabricksSecretScopeRepository):
        DatabricksManagerBase.__init__(self, repository)

    def save(self, client_args: DatabricksClientArgs, t_object: DatabricksSecretScope):
        if t_object is None:
            return
        result = self.repository.get(client_args=client_args)
        exists = False
        if 'scopes' in result.keys():
            for scope in result['scopes']:
                if t_object.keyvault_resource_id == scope['keyvault_metadata']['resource_id']:
                    exists = True
        if not exists:
            self.repository.create(client_args=client_args, t_object=t_object)
        else:
            self.repository.update(client_args=client_args, t_object=t_object)
