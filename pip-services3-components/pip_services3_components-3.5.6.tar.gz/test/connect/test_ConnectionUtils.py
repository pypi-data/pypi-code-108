# -*- coding: utf-8 -*-
from pip_services3_commons.config import ConfigParams

from pip_services3_components.connect.ConnectionUtils import ConnectionUtils


class TestConnectionUtils:

    def test_concat_options(self):
        options1 = ConfigParams.from_tuples(
            "host", "server1",
            "port", "8080",
            "param1", "ABC"
        )

        options2 = ConfigParams.from_tuples(
            "host", "server2",
            "port", "8080",
            "param2", "XYZ"
        )

        options = ConnectionUtils.concat(options1, options2)

        assert len(options) == 4
        assert "server1,server2" == options.get_as_nullable_string("host")
        assert "8080,8080" == options.get_as_nullable_string("port")
        assert "ABC" == options.get_as_nullable_string("param1")
        assert "XYZ" == options.get_as_nullable_string("param2")

    def test_include_keys(self):
        options1 = ConfigParams.from_tuples(
            "host", "server1",
            "port", "8080",
            "param1", "ABC"
        )

        options = ConnectionUtils.include(options1, "host", "port")

        assert len(options) == 2
        assert "server1" == options.get_as_nullable_string("host")
        assert "8080", options.get_as_nullable_string("port")
        assert options.get_as_nullable_string("param1") is None

    def test_exclude_keys(self):
        options1 = ConfigParams.from_tuples(
            "host", "server1",
            "port", "8080",
            "param1", "ABC"
        )

        options = ConnectionUtils.exclude(options1, "host", "port")

        assert len(options) == 1
        assert options.get_as_nullable_string("host") is None
        assert options.get_as_nullable_string("port") is None
        assert "ABC" == options.get_as_nullable_string("param1")

    def test_parse_uri_1(self):
        options = ConnectionUtils.parse_uri("broker1", "kafka", 9092)
        assert len(options) == 4
        assert "broker1:9092" == options.get_as_nullable_string("servers")
        assert "kafka" == options.get_as_nullable_string("protocol")
        assert "broker1" == options.get_as_nullable_string("host")
        assert "9092" == options.get_as_nullable_string("port")

        options = ConnectionUtils.parse_uri("tcp://broker1:8082", "kafka", 9092)
        assert len(options) == 4
        assert "broker1:8082" == options.get_as_nullable_string("servers")
        assert "tcp" == options.get_as_nullable_string("protocol")
        assert "broker1" == options.get_as_nullable_string("host")
        assert "8082" == options.get_as_nullable_string("port")

        options = ConnectionUtils.parse_uri("tcp://user:pass123@broker1:8082", "kafka", 9092)
        assert len(options) == 6
        assert "broker1:8082" == options.get_as_nullable_string("servers")
        assert "tcp" == options.get_as_nullable_string("protocol")
        assert "broker1" == options.get_as_nullable_string("host")
        assert "8082" == options.get_as_nullable_string("port")
        assert "user" == options.get_as_nullable_string("username")
        assert "pass123" == options.get_as_nullable_string("password")

        options = ConnectionUtils.parse_uri("tcp://user:pass123@broker1,broker2:8082", "kafka", 9092)
        assert len(options) == 6
        assert "broker1:9092,broker2:8082" == options.get_as_nullable_string("servers")
        assert "tcp" == options.get_as_nullable_string("protocol")
        assert "broker1,broker2" == options.get_as_nullable_string("host")
        assert "9092,8082" == options.get_as_nullable_string("port")
        assert "user" == options.get_as_nullable_string("username")
        assert "pass123" == options.get_as_nullable_string("password")

        options = ConnectionUtils.parse_uri("tcp://user:pass123@broker1:8082,broker2:8082?param1=ABC&param2=XYZ",
                                            "kafka", 9092)
        assert len(options) == 8
        assert "broker1:8082,broker2:8082" == options.get_as_nullable_string("servers")
        assert "tcp" == options.get_as_nullable_string("protocol")
        assert "broker1,broker2" == options.get_as_nullable_string("host")
        assert "8082,8082" == options.get_as_nullable_string("port")
        assert "user" == options.get_as_nullable_string("username")
        assert "pass123" == options.get_as_nullable_string("password")
        assert "ABC" == options.get_as_nullable_string("param1")
        assert "XYZ" == options.get_as_nullable_string("param2")

    def test_parse_uri_2(self):
        options = ConfigParams.from_tuples(
            "host", "broker1,broker2",
            "port", ",8082",
            "username", "user",
            "password", "pass123",
            "param1", "ABC",
            "param2", "XYZ",
            "param3", None
        )

        uri = ConnectionUtils.compose_uri(options, "tcp", 9092)
        assert uri == "tcp://user:pass123@broker1:9092,broker2:8082?param1=ABC&param2=XYZ&param3"

        uri = ConnectionUtils.compose_uri(options, None, None)
        assert uri == "user:pass123@broker1,broker2:8082?param1=ABC&param2=XYZ&param3"
