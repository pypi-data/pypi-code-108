import abc
from databricks_cli.sdk import ApiClient


class IDatabricksContextBase(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def _execute(self, func, **kwargs):
        """interface method for execute databricks cli command"""


class DatabricksContextBase(IDatabricksContextBase):
    def __init__(self, api_client: ApiClient, api):
        self.__client = api_client
        self.__api = api

    def _execute(self, func, **kwargs):
        result = func(self.__api, **kwargs)
        self.__client.close()

        return result
