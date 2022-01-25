from whizbang.data.databricks.databricks_client_args import DatabricksClientArgs
from whizbang.data.databricks.databricks_context_factory import DatabricksContextFactory
from whizbang.domain.models.databricks.databricks_secret_scope import DatabricksSecretScope
from whizbang.domain.repository.databricks.databricks_repository_base import DatabricksRepositoryBase
from whizbang.domain.shared_types.databricks_api_type import DatabricksApiType


class DatabricksSecretScopeRepository(DatabricksRepositoryBase):
    def __init__(self, context_factory: DatabricksContextFactory):
        DatabricksRepositoryBase.__init__(self, context_factory)

    @property
    def context_type(self) -> str: return DatabricksApiType.secret

    def create(self, client_args: DatabricksClientArgs, t_object: DatabricksSecretScope):
        context = self._get_context(client_args)
        return context.create_keyvault_secret_scope(
            keyvault_name=t_object.keyvault_name,
            keyvault_resource_id=t_object.keyvault_resource_id,
            keyvault_dns=t_object.keyvault_dns
        )

    def get(self, client_args: DatabricksClientArgs):
        context = self._get_context(context_args=client_args)

        return context.get_secret_scopes()

    def update(self, client_args: DatabricksClientArgs, t_object: DatabricksSecretScope):
        context = self._get_context(context_args=client_args)
        context.delete_scope()
        return context.create_keyvault_secret_scope(
            keyvault_name=t_object.keyvault_name,
            keyvault_resource_id=t_object.keyvault_resource_id,
            keyvault_dns=t_object.keyvault_dns
        )
