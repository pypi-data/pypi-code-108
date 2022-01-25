import abc

from whizbang.core.context_factory_base import ContextFactoryBase, IContextFactory


class IContextFactoryRepository(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def _get_context(self, client_args):
        """"""


class ContextFactoryRepositoryBase(IContextFactoryRepository):
    def __init__(self, context_factory: IContextFactory):
        self._context_factory = context_factory

    @property
    @abc.abstractmethod
    def context_type(self) -> str:
        """return context type"""

    def _get_context(self, context_args):
        return self._context_factory.get_context(context_args, self.context_type)
