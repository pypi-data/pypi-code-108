from abc import ABC, abstractmethod
from typing import ClassVar

from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection


class GraphDbConnectionInterface(ABC):

    @classmethod
    def from_uri(
            cls,
            connection_uri: str,
    ) -> ClassVar:
        """Create object connection from connection uri only
        :param connection_uri: string connection uru
        :return: current object class
        """
        raise NotImplementedError

    @abstractmethod
    def get_connection(
            self,
    ) -> DriverRemoteConnection:
        """Get aws neptune connection object
        :return: object neptune driver connection
        """
        raise NotImplementedError
