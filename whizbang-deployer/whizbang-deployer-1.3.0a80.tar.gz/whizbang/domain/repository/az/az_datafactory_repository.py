from whizbang.data.az_cli_context import AzCliContext
from whizbang.data.az_cli_response import AzCliResponse
from whizbang.domain.repository.az.az_repository_base import AzRepositoryBase


class AzDatafactoryRepository(AzRepositoryBase):
    def __init__(self, context: AzCliContext):
        AzRepositoryBase.__init__(self, context)

    @property
    def _resource_provider(self) -> str:
        return "datafactory"

    def get_integration_runtime_key(self,
                                    datafactory_name: str,
                                    resource_group: str,
                                    integration_runtime_name: str) -> str:
        auth_keys: dict = self._execute(f'integration-runtime list-auth-key'
                                        f' --factory-name {datafactory_name}'
                                        f' --resource-group {resource_group}'
                                        f' --integration-runtime-name {integration_runtime_name}').results
        if auth_keys is not None:
            return auth_keys["authKey1"]

    def get_datafactory(self,
                        factory_name: str,
                        resource_group: str):
        return self._execute(f'show'
                             f' --factory-name {factory_name}'
                             f' --resource-group {resource_group}').results

    def get_integration_runtime_connection_info(self,
                                                factory_name: str,
                                                integration_runtime_name: str,
                                                resource_group: str) -> dict:
        result = self._execute(f'integration-runtime get-connection-info'
                               f' --factory-name {factory_name}'
                               f' --integration-runtime-name {integration_runtime_name}'
                               f' --resource-group {resource_group}')
        return result.results
