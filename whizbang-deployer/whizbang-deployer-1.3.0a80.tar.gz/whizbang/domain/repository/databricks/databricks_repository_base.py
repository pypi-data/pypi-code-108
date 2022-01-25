import abc

from whizbang.core.context_factory_repository_base import IContextFactoryRepository, ContextFactoryRepositoryBase
from whizbang.data.databricks.databricks_client_args import DatabricksClientArgs
from whizbang.data.databricks.databricks_context_factory import IDatabricksContextFactory


class IDatabricksRepository(IContextFactoryRepository, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def create(self, client_args: DatabricksClientArgs, t_object):
        """databricks repository create method interface"""

    @abc.abstractmethod
    def get(self, client_args: DatabricksClientArgs):
        """databricks repository get method interface"""

    @abc.abstractmethod
    def update(self, client_args: DatabricksClientArgs, t_object):
        """databricks repository update method interface"""


class DatabricksRepositoryBase(ContextFactoryRepositoryBase, IDatabricksRepository):
    def __init__(self, databricks_context_factory: IDatabricksContextFactory):
        ContextFactoryRepositoryBase.__init__(self, context_factory=databricks_context_factory)

    @abc.abstractmethod
    def create(self, client_args: DatabricksClientArgs, t_object):
        """abstract create"""
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, client_args: DatabricksClientArgs):
        """abstract create"""
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, client_args: DatabricksClientArgs, t_object):
        """abstract create"""
        raise NotImplementedError
