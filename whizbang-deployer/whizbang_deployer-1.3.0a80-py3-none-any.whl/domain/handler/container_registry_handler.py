from whizbang.config.app_config import AppConfig
from whizbang.domain.handler.handler_base import HandlerBase
from whizbang.domain.manager.az.az_container_registry_manager import AzContainerRegistryManager


class ContainerRegistryHandler(HandlerBase):
    def __init__(self,  app_config: AppConfig, manager: AzContainerRegistryManager):
        HandlerBase.__init__(self, app_config=app_config)
        self.manager = manager

    def get_tags(self, registry_name: str, repository_name: str, subscription: str):
        return self.manager.get_tags(registry_name=registry_name,
                                     repository_name=repository_name,
                                     subscription=subscription)
