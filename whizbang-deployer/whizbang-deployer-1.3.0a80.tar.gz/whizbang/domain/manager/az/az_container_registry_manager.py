from whizbang.domain.manager.az.az_manager_base import AzManagerBase
from whizbang.domain.repository.az.az_container_registry_repository import AzContainerRegistryRepository


class AzContainerRegistryManager(AzManagerBase):
    def __init__(self, repository: AzContainerRegistryRepository):
        AzManagerBase.__init__(self, repository)
        self._repository: AzContainerRegistryRepository

    def get_tags(self, registry_name: str, repository_name: str, subscription: str):
        return self._repository.get_tags(registry_name=registry_name,
                                         repository_name=repository_name,
                                         subscription=subscription)
