"""BambooAPIClient client for Bamboo Flexibility API defined in https://github.com/bambooenergy/..."""  # noqa: E501

from __future__ import absolute_import

import configparser
import os

from bambooapi_client import ApiClient, Configuration

from .sites_api import SitesApi
from .tariffs_api import TariffsApi
from .users_api import UsersApi
from .weather_api import WeatherApi


class BambooAPIClient(object):
    """BambooAPIClient is client for Bamboo Flexibility API."""

    def __init__(
        self,
        url,
        token,
        debug=None,
        timeout=10000,
        **kwargs,
    ):
        """Initialize defaults.

        :param url: Bamboo Flexibility API server url (ex. http://localhost).
        :param token: auth token
        :param debug: enable verbose logging of http requests
        :param timeout: HTTP client timeout setting for a request specified in
            milliseconds. If one number provided, it will be total request
            timeout. It can also be a pair (tuple) of (connection, read)
            timeouts.
        :key bool verify_ssl: Set this to false to skip verifying SSL
            certificate when calling API from https server.
        :key str ssl_ca_cert: Set this to customize the certificate file to
            verify the peer.
        :key str proxy: Set this to configure the http proxy to be used
            (ex. http://localhost:3128)
        :key int connection_pool_maxsize: Number of connections to save that
            can be reused by urllib3.
            Defaults to "multiprocessing.cpu_count() * 5".
        """
        self.url = url
        self.token = token

        conf = Configuration(discard_unknown_keys=True)
        if self.url.endswith('/'):
            conf.host = self.url[:-1]
        else:
            conf.host = self.url
        conf.debug = debug
        conf.verify_ssl = kwargs.get('verify_ssl', True)
        conf.ssl_ca_cert = kwargs.get('ssl_ca_cert', None)
        conf.proxy = kwargs.get('proxy', None)
        conf.connection_pool_maxsize = kwargs.get(
            'connection_pool_maxsize',
            conf.connection_pool_maxsize,
        )
        conf.timeout = timeout

        auth_token = self.token
        auth_header_name = 'Authorization'
        auth_header_value = 'Bearer ' + auth_token

        self.api_client = ApiClient(
            configuration=conf,
            header_name=auth_header_name,
            header_value=auth_header_value,
        )

    def __enter__(self):
        """Enter the runtime context of this instance.

        It binds this method’s return value to the target(s) specified in the
        `as` clause of the statement.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context of this instance and close the client."""
        self.close()

    @classmethod
    def from_config_file(
        cls,
        config_file: str = 'config.ini',
        debug=None,
    ):
        """Configure client via configuration file.

        The supported formats:
            - https://docs.python.org/3/library/configparser.html
            - https://toml.io/en/
        Configuration options:
            - url
            - token
            - timeout
            - verify_ssl
            - ssl_ca_cert
            - connection_pool_maxsize
        config.ini example::
            [bambooapi]
            url=http://localhost
            token=my-token
            timeout=6000
            connection_pool_maxsize=25
        config.toml example::
            [bambooapi]
                url = 'http://localhost'
                token = 'my-token'
                timeout = 6000
                connection_pool_maxsize = 25
        """
        config = configparser.ConfigParser()
        config.read(config_file)

        def config_value(key: str):
            return config['bambooapi'][key].strip('"')

        url = config_value('url')
        token = config_value('token')

        timeout = None

        if config.has_option('bambooapi', 'timeout'):
            timeout = config_value('timeout')

        verify_ssl = True
        if config.has_option('bambooapi', 'verify_ssl'):
            verify_ssl = config_value('verify_ssl')

        ssl_ca_cert = None
        if config.has_option('bambooapi', 'ssl_ca_cert'):
            ssl_ca_cert = config_value('ssl_ca_cert')

        connection_pool_maxsize = None
        if config.has_option('bambooapi', 'connection_pool_maxsize'):
            connection_pool_maxsize = config_value('connection_pool_maxsize')

        return cls(url, token, debug=debug, timeout=_to_int(timeout),
                   verify_ssl=_to_bool(verify_ssl), ssl_ca_cert=ssl_ca_cert,
                   connection_pool_maxsize=_to_int(connection_pool_maxsize))

    @classmethod
    def from_env_properties(cls, debug=None):
        """Configure client via environment properties.

        Supported environment properties:
            - BAMBOOAPI_V1_URL
            - BAMBOOAPI_V1_TOKEN
            - BAMBOOAPI_V1_TIMEOUT
            - BAMBOOAPI_V1_VERIFY_SSL
            - BAMBOOAPI_V1_SSL_CA_CERT
            - BAMBOOAPI_V1_CONNECTION_POOL_MAXSIZE
        """
        url = os.getenv('BAMBOOAPI_V1_URL', 'http://localhost')
        token = os.getenv('BAMBOOAPI_V1_TOKEN', 'my-token')
        timeout = os.getenv('BAMBOOAPI_V1_TIMEOUT', '10000')
        verify_ssl = os.getenv('BAMBOOAPI_V1_VERIFY_SSL', 'True')
        ssl_ca_cert = os.getenv('BAMBOOAPI_V1_SSL_CA_CERT', None)
        connection_pool_maxsize = os.getenv(
            'BAMBOOAPI_V1_CONNECTION_POOL_MAXSIZE',
            None,
        )

        return cls(url, token, debug=debug, timeout=_to_int(timeout),
                   verify_ssl=_to_bool(verify_ssl), ssl_ca_cert=ssl_ca_cert,
                   connection_pool_maxsize=_to_int(connection_pool_maxsize))

    def sites_api(self) -> SitesApi:
        """Create a Sites API instance."""
        return SitesApi(self)

    def close(self):
        """Shutdown the client."""
        if self.api_client:
            self.api_client.close()
            self.api_client = None

    def users_api(self) -> UsersApi:
        """Create the Users API instance."""
        return UsersApi(self)

    def weather_api(self) -> WeatherApi:
        """Create the Weather API instance."""
        return WeatherApi(self)

    def tariffs_api(self) -> TariffsApi:
        """Create the Tariff API instance."""
        return TariffsApi(self)


def _to_bool(bool_value):
    return str(bool_value).lower() in ('yes', 'true')


def _to_int(int_value):
    return int(int_value) if int_value is not None else None
