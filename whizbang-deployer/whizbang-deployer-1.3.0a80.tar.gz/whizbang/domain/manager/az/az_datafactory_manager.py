from whizbang.data.az_cli_response import AzCliResponse
from whizbang.domain.exceptions import AzCliResourceDoesNotExist
from whizbang.domain.manager.az.az_manager_base import AzManagerBase
from whizbang.domain.models.datafactory.integration_runtime_connection_info import IntegrationRuntimeConnectionInfo
from whizbang.domain.repository.az.az_datafactory_repository import AzDatafactoryRepository


class AzDatafactoryManager(AzManagerBase):
    def __init__(self, repository: AzDatafactoryRepository):
        AzManagerBase.__init__(self, repository=repository)
        self._repository: AzDatafactoryRepository

    def get_integration_runtime_key(self,
                                    datafactory_name: str,
                                    resource_group: str,
                                    integration_runtime_name: str) -> str:
        return self._repository.get_integration_runtime_key(datafactory_name=datafactory_name,
                                                            resource_group=resource_group,
                                                            integration_runtime_name=integration_runtime_name)

    def get_datafactory(self,
                        factory_name: str,
                        resource_group: str):
        try:
            return self._repository.get_datafactory(factory_name=factory_name, resource_group=resource_group)
        except AzCliResourceDoesNotExist as dne:
            # if datafactory does not exist, return none rather than raise exception
            return None

    def get_integration_runtime_connection_info(self,
                                                factory_name: str,
                                                integration_runtime_name: str,
                                                resource_group: str) -> IntegrationRuntimeConnectionInfo:
        results: dict = self._repository.get_integration_runtime_connection_info(factory_name=factory_name,
                                                                                 integration_runtime_name=integration_runtime_name,
                                                                                 resource_group=resource_group)
        connection_info = IntegrationRuntimeConnectionInfo(**results)
        return connection_info
