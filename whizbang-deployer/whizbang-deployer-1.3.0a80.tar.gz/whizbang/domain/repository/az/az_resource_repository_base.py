from abc import abstractmethod

from whizbang.data.az_cli_context import AzCliContext
from whizbang.domain.models.az_resource_base import AzResourceBase
from whizbang.domain.repository.az.az_repository_base import IAzRepository, AzRepositoryBase


class IAzResourceRepository(IAzRepository):
    """The AzResourceRepository interface"""

    @abstractmethod
    def create(self, resource: AzResourceBase):
        """create resource"""


class AzResourceRepositoryBase(AzRepositoryBase, IAzResourceRepository):
    def __init__(self, context: AzCliContext):
        AzRepositoryBase.__init__(self, context)

    @abstractmethod
    def create(self, resource: AzResourceBase):
        raise NotImplementedError
