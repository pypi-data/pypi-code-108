# -*- coding: utf-8 -*-
from pip_services3_commons.config import IConfigurable, ConfigParams
from pip_services3_commons.refer import IReferenceable, IReferences
from pip_services3_components.auth import CredentialResolver
from pip_services3_components.connect import ConnectionResolver

from .AwsConnectionParams import AwsConnectionParams


class AwsConnectionResolver(IConfigurable, IReferenceable):
    """
    Helper class to retrieve AWS connection and credential parameters,
    validate them and compose a :class:`AwsConnectionParams <pip_services3_aws.connect.AwsConnectionParams.AwsConnectionParams>` value.

    ### Configuration parameters ###
    - connections:
        - discovery_key:               (optional) a key to retrieve the connection from :class:`IDiscovery <pip_services3_components.connect.IDiscovery.IDiscovery>`
        - region:                      (optional) AWS region
        - partition:                   (optional) AWS partition
        - service:                     (optional) AWS service
        - resource_type:               (optional) AWS resource type
        - resource:                    (optional) AWS resource id
        - arn:                         (optional) AWS resource ARN
    - credentials:
        - store_key:                   (optional) a key to retrieve the credentials from :class:`ICredentialStore <pip_services3_components.auth.ICredentialStore.ICredentialStore>`
        - access_id:                   AWS access/client id
        - access_key:                  AWS access/client id

    ### References ###
        - `*:discovery:*:*:1.0`        (optional) :class:`IDiscovery <pip_services3_components.connect.IDiscovery.IDiscovery>` services to resolve connection
        - *:credential-store:*:*:1.0   (optional) Credential stores to resolve credentials

    See :class:`ConnectionParams <pip_services3_components.connect.ConnectionParams.ConnectionParams>` (in the Pip.Services components package),
    :class:`IDiscovery <pip_services3_components.connect.IDiscovery.IDiscovery>` (in the Pip.Services components package)

    .. code-block:: python
    
        config = ConfigParams.from_tuples(
            "connection.region", "us-east1",
            "connection.service", "s3",
            "connection.bucket", "mybucket",
            "credential.access_id", "XXXXXXXXXX",
            "credential.access_key", "XXXXXXXXXX"
        )

        connection_resolver = AwsConnectionResolver()
        connection_resolver.configure(config)
        connection_resolver.set_references(references)

        connection_params = connection_resolver.resolve("123")

    """

    def __init__(self):
        # The connection resolver.
        self.__connection_resolver: ConnectionResolver = ConnectionResolver()

        # The credential resolver.
        self.__credential_resolver: CredentialResolver = CredentialResolver()

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        self.__connection_resolver.configure(config)
        self.__credential_resolver.configure(config)

    def set_references(self, references: IReferences):
        """
        Sets references to dependent components.

        :param references: references to locate the component dependencies.
        """
        self.__connection_resolver.set_references(references)
        self.__credential_resolver.set_references(references)

    def resolve(self, correlation_id: str) -> AwsConnectionParams:
        """
        Resolves connection and credential parameters and generates a single
        AWSConnectionParams value.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :return: AWSConnectionParams value or error.
        """
        connection = AwsConnectionParams()

        connection_params = self.__connection_resolver.resolve(correlation_id)
        connection.append(connection_params)

        credential_params = self.__credential_resolver.lookup(correlation_id)
        connection.append(credential_params)

        # Force ARN parsing
        connection.set_arn(connection.get_arn())

        # Perform validation
        connection.validate(correlation_id)

        return connection
