from whizbang.domain.manager.az.az_manager_base import AzManagerBase
from whizbang.domain.models.webapp_settings import WebappSettings
from whizbang.domain.repository.az.az_webapp_repository import AzWebappRepository


class AzWebappManager(AzManagerBase):
    def __init__(self, repository: AzWebappRepository):
        AzManagerBase.__init__(self, repository)
        self._repository: AzWebappRepository = repository

    def add_setting(self, settings: WebappSettings):
        return self._repository.create_app_settings(settings=settings)

    def set_continuous_deployment(self, enable_continuous_deployment: bool,
                                  webapp_name: str,
                                  resource_group_name: str,
                                  deployment_slot_name: str = 'production'):
        return self._repository.set_continuous_deployment(enable_continuous_deployment=enable_continuous_deployment,
                                                          webapp_name=webapp_name,
                                                          resource_group_name=resource_group_name,
                                                          deployment_slot_name=deployment_slot_name)

    def swap_deployment_slot(self, deployment_slot_name: str,
                             webapp_name: str,
                             resource_group_name: str):
        return self._repository.swap_deployment_slot(deployment_slot_name=deployment_slot_name,
                                                     webapp_name=webapp_name,
                                                     resource_group_name=resource_group_name)
