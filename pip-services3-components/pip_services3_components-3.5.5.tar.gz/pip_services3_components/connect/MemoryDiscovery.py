# -*- coding: utf-8 -*-
"""
    pip_services3_components.connect.MemoryDiscovery
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Memory discovery implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import List, Optional

from pip_services3_commons.config import ConfigParams
from pip_services3_commons.config.IReconfigurable import IReconfigurable

from .ConnectionParams import ConnectionParams
from .IDiscovery import IDiscovery


class DiscoveryItem:
    """
    Used to store key-identifiable information about connections.
    """
    key: str = None
    connection: ConnectionParams = None


class MemoryDiscovery(IDiscovery, IReconfigurable):
    """
    Discovery service that keeps connections in memory.

    ### Configuration parameters ###
        - [connection key 1]:
        - ...                          connection parameters for key 1
        - [connection key 2]:
        - ...                          connection parameters for key N

    Example:

    .. code-block:: python
    
        config = ConfigParams.from_tuples(
        "key1.host", "10.1.1.100",
        "key1.port", "8080",
        "key2.host", "10.1.1.100",
        "key2.port", "8082")

        discovery = MemoryDiscovery()
        discovery.read_connections(config)

        discovery.resolve("123", "key1")
    """

    def __init__(self, config: ConfigParams = None):
        """
        Creates a new instance of discovery service.

        :param config: (optional) configuration with connection parameters.
        """
        self.__items: List[DiscoveryItem] = []
        if not (config is None):
            self.configure(config)

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        self.read_connections(config)

    def read_connections(self, connections: ConfigParams):
        """
        Reads connections from configuration parameters.
        Each section represents an individual Connection params

        :param connections: configuration parameters to be read
        """
        del self.__items[:]
        for key in connections.get_keys():
            item = DiscoveryItem()
            item.key = key
            value = connections.get_as_nullable_string(key)
            item.connection = ConnectionParams.from_string(value)
            self.__items.append(item)

    def register(self, correlation_id: Optional[str], key: str, connection: ConnectionParams) -> ConnectionParams:
        """
        Registers connection parameters into the discovery service.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param key: a key to uniquely identify the connection parameters.

        :param connection: a connection to be registered.

        :returns: the registered connection parameters.
        """
        item = DiscoveryItem()
        item.key = key
        item.connection = connection
        self.__items.append(item)
        return connection

    def resolve_one(self, correlation_id: Optional[str], key: str) -> ConnectionParams:
        """
        Resolves a single connection parameters by its key.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param key: a key to uniquely identify the connection.

        :return: a resolved connection.
        """
        connection = None
        for item in self.__items:
            if item.key == key and not (item.connection is None):
                connection = item.connection
                break
        return connection

    def resolve_all(self, correlation_id: Optional[str], key: str) -> List[ConnectionParams]:
        """
        Resolves all connection parameters by their key.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param key: a key to uniquely identify the connections.

        :return: a list with resolved connections.
        """
        connections = []
        for item in self.__items:
            if item.key == key and not (item.connection is None):
                connections.append(item.connection)
        return connections
