# -*- coding: utf-8 -*-
"""
    pip_services3_components.connect.ConnectionParams
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Connection parameters implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Any, List

from pip_services3_commons.config import ConfigParams
from pip_services3_commons.data import StringValueMap


class ConnectionParams(ConfigParams):
    """
    Contains connection parameters to connect to external services.

    They are used together with credential parameters, but usually stored
    separately from more protected sensitive values.

    ### Configuration parameters ###
        - discovery_key: key to retrieve parameters from discovery service
        - protocol:      connection protocol like http, https, tcp, udp
        - host:          host name or IP address
        - port:          port number
        - uri:           resource URI or connection string with all parameters in it

    In addition to standard parameters ConnectionParams may contain any number of custom parameters

    Example:

    .. code-block:: python

        connection = ConnectionParams.from_tuples("protocol", "http",
                                                  "host", "10.1.1.100",
                                                  "port", "8080",
                                                  "cluster", "mycluster")

        host = connection.get_host()                              # Result: "10.1.1.100"
        port = connection.get_port()                              # Result: 8080
        cluster = connection.get_as_nullable_string("cluster")    # Result: "mycluster"
    """

    def __init__(self, map: Any = None):
        """
        Creates a new connection parameters and fills it with values.

        :param map: (optional) an object to be converted into key-value pairs to initialize this connection.
        """
        super(ConnectionParams, self).__init__(map)

    def use_discovery(self) -> bool:
        """
        Checks if these connection parameters shall be retrieved from DiscoveryService.
        The connection parameters are redirected to DiscoveryService when discovery_key parameter is set.

        :return: true if connection shall be retrieved from DiscoveryService
        """
        return "discovery_key" in self

    def get_discovery_key(self) -> str:
        """
        Gets the key to retrieve this connection from DiscoveryService.
        If this key is null, than all parameters are already present.

        :return: the discovery key to retrieve connection.
        """
        return self.get_as_nullable_string("discovery_key")

    def set_discovery_key(self, value: str):
        """
        Sets the key to retrieve these parameters from DiscoveryService.

        :param value: a new key to retrieve connection.
        """
        self.put("discovery_key", value)

    def get_protocol(self) -> str:
        """
        Gets the connection protocol.

        :return: the connection protocol or the default value if it's not set.
        """
        return super().get_as_string('protocol')

    def get_protocol_with_default(self, default_value: str = None) -> str:
        """
        Gets the connection protocol with default value.

        :param default_value: (optional) the default protocol

        :return: the connection protocol or the default value if it's not set.
        """
        return super().get_as_string_with_default("protocol", default_value)

    def set_protocol(self, value: str):
        """
        Sets the connection protocol.

        :param value: a new connection protocol.
        """
        self.put("protocol", value)

    def get_host(self) -> str:
        """
        Gets the host name or IP address.

        :return: the host name or IP address.
        """
        host = self.get_as_nullable_string("host")
        host = host if not (host is None) else self.get_as_nullable_string("ip")
        return host

    def set_host(self, value: str):
        """
        Sets the host name or IP address.

        :param value: a new host name or IP address.
        """
        self.put("host", value)

    def get_port(self) -> int:
        """
        Gets the port number.

        :return: the port number.
        """
        return super().get_as_integer("port")

    def get_port_with_default(self, default_port: int) -> int:
        """
        Gets the port number with default value.

        :param default_port:    a default port number.
        :return:                the port number.
        """
        return super().get_as_integer_with_default("port", default_port)

    def set_port(self, value: int):
        """
        Sets the port number.

        :param value: a new port number.
        """
        self.set_as_object("port", value)

    def get_uri(self) -> str:
        """
        Gets the resource URI or connection string. Usually it includes all connection parameters in it.

        :return: the resource URI or connection string.
        """
        return self.get_as_string("uri")

    def set_uri(self, value: str):
        """
        Sets the resource URI or connection string.

        :param value: a new resource URI or connection string.
        """
        self.set_as_object("uri", value)

    @staticmethod
    def from_string(line: str) -> 'ConnectionParams':
        """
        Creates a new ConnectionParams object filled with key-value pairs serialized as a string.

        :param line: a string with serialized key-value pairs as **"key1=value1;key2=value2;..."**
                     Example: **"Key1=123;Key2=ABC;Key3=2016-09-16T00:00:00.00Z"**

        :return: a new ConnectionParams object.
        """
        map = StringValueMap.from_string(line)
        return ConnectionParams(map)

    @staticmethod
    def from_tuples(*tuples: Any) -> 'ConnectionParams':
        """
        Creates a new ConnectionParams object filled with provided key-value pairs called tuples.
        Tuples parameters contain a sequence of key1, value1, key2, value2, ... pairs.

        :param tuples: the tuples to fill a new ConnectionParams object.

        :return: a new ConnectionParams object.
        """
        map = StringValueMap.from_tuples_array(tuples)
        return ConnectionParams(map)

    @staticmethod
    def many_from_config(config: ConfigParams) -> List['ConnectionParams']:
        """
        Retrieves all ConnectionParams from configuration parameters
        from "connections" section. If "connection" section is present instead,
        than it returns a list with only one ConnectionParams.

        :param config: a configuration parameters to retrieve connections

        :return: a list of retrieved ConnectionParams
        """
        result = []

        # Try to get multiple connections first
        connections = config.get_section("connections")
        if len(connections) > 0:
            sections_names = connections.get_section_names()
            for section in sections_names:
                connection = connections.get_section(section)
                result.append(ConnectionParams(connection))
        # Then try to get a single connection
        else:
            connection = config.get_section("connection")
            result.append(ConnectionParams(connection))

        return result

    @staticmethod
    def from_config(config: ConfigParams) -> 'ConnectionParams':
        """
        Retrieves a single ConnectionParams from configuration parameters
        from "connection" section. If "connections" section is present instead,
        then is returns only the first connection element.

        :param config: ConnectionParams, containing a section named "connection(s)".

        :return: the generated ConnectionParams object.
        """
        connections = ConnectionParams.many_from_config(config)
        return connections[0] if len(connections) > 0 else None
