import abc

from whizbang.data.databricks.databricks_client_args import DatabricksClientArgs
from whizbang.domain.repository.databricks.databricks_repository_base import IDatabricksRepository


class IDatabricksManager(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def save(self, client_args: DatabricksClientArgs, t_object):
        """databricks manager save interface"""

    @abc.abstractmethod
    def get(self, client_args: DatabricksClientArgs):
        """gets a list of databricks objects"""


class DatabricksManagerBase(IDatabricksManager):
    def __init__(self, repository: IDatabricksRepository):
        self.repository = repository

    def save(self, client_args: DatabricksClientArgs, t_object):
        return self.repository.create(client_args, t_object)

    def get(self, client_args: DatabricksClientArgs):
        return self.repository.get(client_args=client_args)
