from abc import abstractmethod

from whizbang.domain.manager.az.az_manager_base import IAzManager, AzManagerBase
from whizbang.domain.models.az_resource_base import AzResourceBase
from whizbang.domain.repository.az.az_resource_repository_base import IAzResourceRepository


class IAzResourceManager(IAzManager):
    """The AzResourceRepository interface"""

    @abstractmethod
    def create(self, resource: AzResourceBase):
        """create resource"""


class AzResourceManagerBase(AzManagerBase, IAzResourceManager):
    def __init__(self, repository: IAzResourceRepository):
        AzManagerBase.__init__(self, repository)
        self._repository: IAzResourceRepository

    def create(self, resource: AzResourceBase):
        return self._repository.create(resource)
