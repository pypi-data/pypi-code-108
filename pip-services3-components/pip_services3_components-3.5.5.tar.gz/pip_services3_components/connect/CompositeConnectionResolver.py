# -*- coding: utf-8 -*-

from typing import List, Optional

from pip_services3_commons.config import IConfigurable, ConfigParams
from pip_services3_commons.errors import ConfigException
from pip_services3_commons.refer import IReferenceable, IReferences

from pip_services3_components.auth import CredentialResolver, CredentialParams
from .ConnectionResolver import ConnectionResolver
from .ConnectionParams import ConnectionParams


class CompositeConnectionResolver(IReferenceable, IConfigurable):
    """
    Helper class that resolves connection and credential parameters,
    validates them and generates connection options.

    ### Configuration parameters ###
        - connection(s):
            - discovery_key:               (optional) a key to retrieve the connection from :class:`IDiscovery <pip_services3_components.connect.IDiscovery.IDiscovery>`
            - protocol:                    communication protocol
            - host:                        host name or IP address
            - port:                        port number
            - uri:                         resource URI or connection string with all parameters in it
        - credential(s):
            - store_key:                   (optional) a key to retrieve the credentials from :class:`ICredentialStore <pip_services3_components.auth.ICredentialStore.ICredentialStore>`
            - username:                    user name
            - password:                    user password

    ### References ###
        - `\*:discovery:\*:\*:1.0`         (optional) :class:`IDiscovery <pip_services3_components.connect.IDiscovery.IDiscovery>` services to resolve connections
        - `\*:credential-store:\*:\*:1.0`  (optional) Credential stores to resolve credentials
    """

    def __init__(self):
        super(CompositeConnectionResolver, self).__init__()

        # The connection options
        self._options: ConfigParams = None

        # The connections resolver.
        self._connection_resolver = ConnectionResolver()

        # The credentials resolver.
        self._credential_resolver = CredentialResolver()

        # The cluster support (multiple connections)
        self._cluster_supported = True

        # The default protocol
        self._default_protocol: str = None

        # The default port number
        self._default_port: int = 0

        # The list of supported protocols
        self._supported_protocols: List[str] = []

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        self._connection_resolver.configure(config)
        self._credential_resolver.configure(config)
        self._options = config.get_section('options')

    def set_references(self, references: IReferences):
        """
        Sets references to dependent components.

        :param references: references to locate the component dependencies.
        """
        self._connection_resolver.set_references(references)
        self._credential_resolver.set_references(references)

    def resolve(self, correlation_id: Optional[str]) -> ConfigParams:
        """
        Resolves connection options from connection and credential parameters.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :return: resolved options or error
        """

        connections = self._connection_resolver.resolve_all(correlation_id)

        if len(connections) > 0 and not self._cluster_supported:
            raise ConfigException(
                correlation_id,
                "MULTIPLE_CONNECTIONS_NOT_SUPPORTED",
                "Multiple (cluster) connections are not supported"
            )

        # Validate connections
        for connection in connections:
            self._validate_connection(correlation_id, connection)

        credential = self._credential_resolver.lookup(correlation_id)
        # Validate credential
        self._validate_credential(correlation_id, credential)

        options = self._compose_options(connections, credential, self._options)

        return options

    def compose(self, correlation_id: Optional[str], connections: List[ConnectionParams], credential: CredentialParams,
                parameters: ConfigParams) -> ConfigParams:
        """
        Composes Composite connection options from connection and credential parameters.

        :param correlation_id:  (optional) transaction id to trace execution through call chain.
        :param connections:    connection parameters
        :param credential:     credential parameters
        :param parameters:     optional parameters
        :return:               resolved options or error.
        """
        # Validate connection parameters
        for connection in connections:
            self._validate_connection(correlation_id, connection)

        # Validate credential parameters
        self._validate_credential(correlation_id, credential)

        options = self._compose_options(connections, credential, parameters)

        return options

    def _validate_connection(self, correlation_id: Optional[str], connection: ConnectionParams):
        """
        Validates connection parameters.
        This method can be overriden in child classes.

        :param correlation_id:  (optional) transaction id to trace execution through call chain.
        :param connection:      connection parameters to be validated
        :return:                error or `None` if validation was successful
        """

        if connection is None:
            raise ConfigException(correlation_id, "NO_CONNECTION", "Connection parameters are not set is not set")

        # URI usually contains all information
        uri = connection.get_uri()
        if uri is not None: return None

        protocol = connection.get_protocol_with_default(self._default_protocol)
        if protocol is None:
            raise ConfigException(correlation_id, "NO_PROTOCOL", "Connection protocol is not set")

        if self._supported_protocols is not None and protocol in self._supported_protocols:
            raise ConfigException(correlation_id, "UNSUPPORTED_PROTOCOL",
                                  "The protocol " + protocol + " is not supported")

        host = connection.get_host()
        if host is None:
            raise ConfigException(correlation_id, "NO_HOST", "Connection host is not set")

        port = connection.get_port_with_default(self._default_port)
        if port == 0:
            raise ConfigException(correlation_id, "NO_PORT", "Connection port is not set")

        return None

    def _validate_credential(self, correlation_id: Optional[str], credential: CredentialParams):
        """
        Validates credential parameters.
        This method can be overriden in child classes.

        :param correlation_id:  (optional) transaction id to trace execution through call chain.
        :param credential:      credential parameters to be validated
        :return:                error or `None` if validation was successful
        """
        return None

    def _compose_options(self, connections: List[ConnectionParams], credential: CredentialParams,
                         parameters: ConfigParams) -> ConfigParams:
        # Connection options
        options = ConfigParams()

        # Merge connection parameters
        for connection in connections:
            options = self._merge_connection(options, connection)

        # Merge credential parameters
        options = self._merge_credential(options, credential)

        # Merge optional parameters
        options = self._merge_optional(options, parameters)

        # Perform final processing
        options = self._finalize_options(options)

        return options

    def _merge_connection(self, options: ConfigParams, connection: ConnectionParams) -> ConfigParams:
        """
        Merges connection options with connection parameters
        This method can be overriden in child classes.

        :param options: connection options
        :param connection: connection parameters to be merged
        :return:  merged connection options.
        """
        merged_options = options.set_defaults(connection)
        return merged_options

    def _merge_credential(self, options: ConfigParams, credential: CredentialParams) -> ConfigParams:
        """
        Merges connection options with credential parameters
        This method can be overriden in child classes.

        :param options:     connection options
        :param credential:  credential parameters to be merged
        :return:            merged connection options.
        """
        merged_options = options.override(credential)
        return merged_options

    def _merge_optional(self, options: ConfigParams, parameters: ConfigParams) -> ConfigParams:
        """
        Merges connection options with optional parameters
        This method can be overriden in child classes.

        :param options: connection options
        :param parameters: optional parameters to be merged
        :return:  merged connection options.
        """
        merged_options = options.override(parameters)
        return merged_options

    def _finalize_options(self, options: ConfigParams) -> ConfigParams:
        """
        Finalize merged options
        This method can be overriden in child classes.

        :param options: connection options
        :return: finalized connection options
        """
        return options
