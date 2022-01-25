import os
from typing import ClassVar

from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process import anonymous_traversal

from graphdb.interface.connection_iface import GraphDbConnectionInterface
from graphdb.utils import get_cpu_count


class GraphDbConnection(GraphDbConnectionInterface):

    def __init__(
            self,
            connection_uri: str,
            pool_size: int = 0,
            max_workers: int = 0,
    ):
        self.pool_size = pool_size
        self.max_workers = max_workers
        self.connection_uri = connection_uri
        if max_workers == 0:
            self.max_workers = get_cpu_count() * int(os.getenv("MAX_WORKERS_CONSTANT", 5))

        if pool_size == 0:
            self.pool_size = get_cpu_count() + (int(os.getenv("MAX_POOL_CONSTANT", 2)) + 1)

        self.driver = anonymous_traversal.traversal().withRemote(
            DriverRemoteConnection(
                self.connection_uri,
                "g",
                pool_size=self.pool_size,
                max_workers=self.max_workers,
            ),
        )

    def get_connection(
            self,
    ) -> DriverRemoteConnection:
        """Get aws neptune connection object
        :return: object aws neptune driver connection
        """
        return self.driver

    @classmethod
    def from_uri(
            cls,
            connection_uri: str,
            pool_size: int = 0,
            max_workers: int = 0,
    ) -> ClassVar:
        """Create object connection from connection uri only
        :param connection_uri: string connection uru
        :param pool_size: integer default pool size for current connection
        :param max_workers: integer default maximum workers for connection
        :return: current object class
        """
        return cls(connection_uri, pool_size, max_workers)
