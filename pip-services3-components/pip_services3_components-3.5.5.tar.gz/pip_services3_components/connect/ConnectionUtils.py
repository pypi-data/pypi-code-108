# -*- coding: utf-8 -*-
import urllib.parse
from typing import Optional

from pip_services3_commons.config import ConfigParams


class ConnectionUtils:
    """
    A set of utility functions to process connection parameters
    """

    @staticmethod
    def concat(options1: ConfigParams, options2: ConfigParams, *keys: str) -> ConfigParams:
        """
        Concatinates two options by combining duplicated properties into comma-separated list

        :param options1:    first options to merge
        :param options2:    second options to merge
        :param keys:        when define it limits only to specific keys
        """

        options = ConfigParams.from_value(options1)
        for key in options2.get_keys():
            value1 = options1.get_as_string(key) or ''
            value2 = options2.get_as_string(key) or ''

            if value1 != '' and value2 != '':
                if keys is None or len(keys) == 0 or key in keys:
                    options.set_as_object(key, value1 + ',' + value2)

            elif value1 != '':
                options.set_as_object(key, value1)
            elif value2 != '':
                options.set_as_object(key, value2)

        return options

    @staticmethod
    def __concat_values(value1: Optional[str], value2: Optional[str]) -> str:
        if value1 is None or value1 == '': return value2
        if value2 is None or value2 == '': return value1
        return value1 + ',' + value2

    @staticmethod
    def parse_uri(uri: str, default_protocol: str, default_port: str) -> ConfigParams:
        """
        Parses URI into config parameters.
        The URI shall be in the following form:
        `protocol://username@password@host1:port1,host2:port2,...?param1=abc&param2=xyz&...`

        :param uri: the URI to be parsed
        :param default_protocol: a default protocol
        :param default_port: a default port
        :return: a configuration parameters with URI elements
        """
        options = ConfigParams()

        if uri is None or uri == '': return options

        uri = uri.strip()

        # Process parameters
        pos = uri.find('?')
        if pos > 0:
            params = uri[pos + 1:]
            uri = uri[0: pos]

            param_list = params.split('&')
            for param in param_list:
                pos = param.find('=')
                if pos >= 0:
                    key = urllib.parse.unquote(param[0:pos])
                    value = urllib.parse.unquote(param[pos + 1:])
                    options.set_as_object(key, value)
                else:
                    options.set_as_object(urllib.parse.unquote(param), None)

        # Process protocol
        pos = uri.find('://')
        if pos > 0:
            protocol = uri[0:pos]
            uri = uri[pos + 3:]
            options.set_as_object("protocol", protocol)
        else:
            options.set_as_object('protocol', default_protocol)

        # Process user and password
        pos = uri.find('@')
        if pos > 0:
            user_and_pass = uri[0:pos]
            uri = uri[pos + 1:]

            pos = user_and_pass.find(':')
            if pos > 0:
                options.set_as_object('username', user_and_pass[0:pos])
                options.set_as_object('password', user_and_pass[pos + 1:])
            else:
                options.set_as_object('username', user_and_pass)

        # Process host and ports
        servers = uri.split(",")
        for server in servers:
            pos = server.find(':')
            if pos > 0:
                options.set_as_object("servers",
                                      ConnectionUtils.__concat_values(options.get_as_string("servers"), server))
                options.set_as_object("host",
                                      ConnectionUtils.__concat_values(options.get_as_string("host"), server[0:pos]))
                options.set_as_object("port",
                                      ConnectionUtils.__concat_values(options.get_as_string("port"), server[pos + 1:]))
            else:
                options.set_as_object("servers", ConnectionUtils.__concat_values(options.get_as_string("servers"),
                                                                                 server + ":" + str(default_port)))
                options.set_as_object("host", ConnectionUtils.__concat_values(options.get_as_string("host"), server))
                options.set_as_object("port",
                                      ConnectionUtils.__concat_values(options.get_as_string("port"), str(default_port)))

        return options

    @staticmethod
    def compose_uri(options: ConfigParams, default_protocol: str, default_port: int) -> str:
        """
        Composes URI from config parameters.
        The result URI will be in the following form:
        protocol://username@password@host1:port1,host2:port2,...?param1=abc&param2=xyz&...

        :param options: configuration parameters
        :param default_protocol:  a default protocol
        :param default_port: a default port
        :return: a composed URI
        """
        builder = ''

        protocol = options.get_as_string_with_default("protocol", default_protocol)
        if protocol is not None:
            builder = protocol + '://' + builder

        username = options.get_as_nullable_string('username')
        if username is not None:
            builder += username
            password = options.get_as_nullable_string('password')
            if password is not None:
                builder += ':' + password
            builder += '@'

        servers = ''
        default_ports_str = '' if default_port is None or default_port < 0 else str(default_port)
        hosts = options.get_as_string_with_default('host', '???').split(',')
        ports = options.get_as_string_with_default('port', default_ports_str).split(',')
        for index in range(len(hosts)):
            if len(servers) > 0:
                servers += ','

            host = hosts[index]
            servers += host

            port = ports[index] if len(ports) > index else default_ports_str
            port = port if port != '' else default_ports_str
            if port != '':
                servers += ':' + port

        builder += servers

        params = ''
        reserved_keys = ["protocol", "host", "port", "username", "password", "servers"]
        for key in options.get_keys():
            if key in reserved_keys:
                continue

            if len(params) > 0:
                params += '&'

            params += urllib.parse.quote(key)

            value = options.get_as_nullable_string(key)
            if value is not None and value != '':
                params += '=' + urllib.parse.quote(value)

        if len(params) > 0:
            builder += '?' + params

        return str(builder)

    @staticmethod
    def include(options: ConfigParams, *keys: str) -> ConfigParams:
        """
        Includes specified keys from the config parameters.

        :param options: configuration parameters to be processed.
        :param keys: a list of keys to be included.
        :return: a processed config parameters.
        """

        if keys is None or len(keys) == 0: return options

        result = ConfigParams()

        for key in options.get_keys():
            if key in keys:
                result.set_as_object(key, options.get_as_string(key))

        return result

    @staticmethod
    def exclude(options: ConfigParams, *keys: str) -> ConfigParams:
        """
        Excludes specified keys from the config parameters.

        :param options: configuration parameters to be processed.
        :param keys: a list of keys to be excluded.
        :return: a processed config parameters.
        """
        if keys is None or len(keys) == 0: return options

        result = options.clone()

        for key in keys:
            result.remove(key)

        return result
