from whizbang.data.az_cli_context import AzCliContext
from whizbang.domain.models.webapp_settings import WebappSettings
from whizbang.domain.repository.az.az_repository_base import AzRepositoryBase


class AzWebappRepository(AzRepositoryBase):
    def __init__(self, context: AzCliContext):
        AzRepositoryBase.__init__(self, context)

    @property
    def _resource_provider(self) -> str: return 'webapp'

    def create_app_settings(self, settings: WebappSettings):
        response = self._execute(f'config appsettings set --resource-group {settings.resource_group}'
                               f' --name {settings.webapp_name}'
                               f' --settings {settings.setting_key}={settings.setting_value}')
        return response.results

    def set_continuous_deployment(self, enable_continuous_deployment: bool,
                                  webapp_name: str,
                                  resource_group_name: str,
                                  deployment_slot_name: str = 'production'):
        response = self._execute(f'deployment container config'
                               f' --enable-cd {enable_continuous_deployment}'
                               f' --name {webapp_name}'
                               f' --resource-group {resource_group_name}'
                               f' --slot {deployment_slot_name}')
        return response.results

    def swap_deployment_slot(self, deployment_slot_name: str,
                             webapp_name: str,
                             resource_group_name: str):
        response = self._execute(f'deployment slot swap'
                               f' --slot {deployment_slot_name}'
                               f' --name {webapp_name}'
                               f' --resource-group {resource_group_name}')
        return response.results
