import abc
from typing import Any

from core.context_factory_repository_base import IContextFactoryRepository


class IContextManager(metaClass=abc.ABCMeta):
    @abc.abstractmethod
    def save(self, context_args, t_object) -> Any:
        """The ContextManager save interface"""


class ContextManagerBase(IContextManager):
    def __init__(self, repository: IContextFactoryRepository):
        self._repository = repository

    def save(self, context_args, t_object) -> Any:
        self._repository.save(context_args, t_object)
