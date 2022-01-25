from abc import ABC

from whizbang.domain.repository.az.az_repository_base import IAzRepository


class IAzManager(ABC):
    """"""


class AzManagerBase(IAzManager):
    def __init__(self, repository: IAzRepository):
        self._repository = repository
