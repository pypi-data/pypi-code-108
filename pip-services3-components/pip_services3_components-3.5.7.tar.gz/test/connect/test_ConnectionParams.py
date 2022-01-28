# -*- coding: utf-8 -*-
"""
    tests.auth.test_ConnectionParams
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    :copyright: (c) Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from pip_services3_components.connect import ConnectionParams


class TestConnectionParams:

    def test_discovery(self):
        connection = ConnectionParams()
        connection.set_discovery_key(None)
        assert None is connection.get_discovery_key()

        connection.set_discovery_key("Discovery key value")
        assert "Discovery key value" == connection.get_discovery_key()
        assert True is connection.use_discovery()

    def test_protocol(self):
        connection = ConnectionParams()
        connection.set_protocol(None)
        assert connection.get_protocol() == ''
        assert connection.get_protocol() == ''
        assert connection.get_protocol_with_default("https") == "https"

        connection.set_protocol("https")
        assert connection.get_protocol() == "https"

    def test_host(self):
        connection = ConnectionParams()
        assert None is connection.get_host()
        connection.set_host(None)
        assert None is connection.get_host()

        connection.set_host("localhost")
        assert "localhost" == connection.get_host()

    def test_port(self):
        connection = ConnectionParams()
        assert None is connection.get_host()

        connection.set_port(3000)
        assert 3000 == connection.get_port()

    def test_uri(self):
        connection = ConnectionParams()
        assert '' == connection.get_uri()

        connection.set_uri("https://pipgoals:3000")
        assert "https://pipgoals:3000" == connection.get_uri()
