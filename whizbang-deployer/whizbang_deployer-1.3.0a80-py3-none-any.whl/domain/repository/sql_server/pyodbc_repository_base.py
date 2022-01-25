import abc

from whizbang.core.context_factory_repository_base import IContextFactoryRepository, ContextFactoryRepositoryBase
from whizbang.data.pyodbc.pyodbc_context_factory import IPyodbcContextFactory


class IPyodbcRepository(IContextFactoryRepository, metaclass=abc.ABCMeta):
    """"""


class PyodbcRepositoryBase(ContextFactoryRepositoryBase, IPyodbcRepository):
    def __init__(self, context_factory: IPyodbcContextFactory):
        ContextFactoryRepositoryBase.__init__(self, context_factory)

    @property
    def context_type(self) -> None: return None
