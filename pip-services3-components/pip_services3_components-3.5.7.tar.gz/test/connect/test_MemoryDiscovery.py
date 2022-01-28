# -*- coding: utf-8 -*-
from pip_services3_commons.config import ConfigParams

from pip_services3_components.connect import MemoryDiscovery, ConnectionParams


class TestMemoryDiscovery:

    def test_read_connections(self):
        config = ConfigParams.from_tuples(
            "connections.key1.host", "10.1.1.100",
            "connections.key1.port", "8080",
            "connections.key2.host", "10.1.1.101",
            "connections.key2.port", "8082"
        )

        discovery = MemoryDiscovery()
        discovery.configure(config)

        # Resolve one
        connection = discovery.resolve_one("123", "key1")
        assert "10.1.1.100" == connection.get_host()
        assert 8080 == connection.get_port()

        connection = discovery.resolve_one("123", "key2")
        assert "10.1.1.101" == connection.get_host()
        assert 8082 == connection.get_port()

        # Resolve all
        discovery.register(None, "key1", ConnectionParams.from_tuples("host", "10.3.3.151"))

        connections = discovery.resolve_all("123", "key1")

        assert len(connections) > 1
