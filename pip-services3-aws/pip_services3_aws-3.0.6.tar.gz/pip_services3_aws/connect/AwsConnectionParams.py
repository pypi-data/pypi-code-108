# -*- coding: utf-8 -*-
from typing import Any, Optional

from pip_services3_commons.config import ConfigParams
from pip_services3_commons.data import StringValueMap
from pip_services3_commons.errors import ConfigException
from pip_services3_components.auth import CredentialParams
from pip_services3_components.connect import ConnectionParams


class AwsConnectionParams(ConfigParams):
    """
    Contains connection parameters to authenticate against Amazon Web Services (AWS)
    and connect to specific AWS resource.

    The class is able to compose and parse AWS resource ARNs.

    ### Configuration parameters ###
        - access_id:     application access id
        - client_id:     alternative to access_id
        - access_key:    application secret key
        - client_key:    alternative to access_key
        - secret_key:    alternative to access_key

    In addition to standard parameters :class:`CredentialParams <pip_services3_components.auth.CredentialParams.CredentialParams>` may contain any number of custom parameters

    Example:

    .. code-block:: python

        connection = AwsConnectionParams.from_tuples(
            "region", "us-east-1",
            "access_id", "XXXXXXXXXXXXXXX",
            "secret_key", "XXXXXXXXXXXXXXX",
            "service", "s3",
            "bucket", "mybucket"
        )

        region = connection.get_region()                      # Result: "us-east-1"
        access_id = connection.get_access_id()                # Result: "XXXXXXXXXXXXXXX"
        secret_key = connection.get_access_key()              # Result: "XXXXXXXXXXXXXXX"
        pin = connection.get_as_nullable_string("bucket")     # Result: "mybucket"

    """

    def __init__(self, values: Any = None):
        """
        Creates an new instance of the connection parameters.

        :param values: (optional) an object to be converted into key-value pairs to initialize this connection.
        """
        super().__init__(values)

    def get_partition(self) -> str:
        """
        Gets the AWS partition name.

        :return: the AWS partition name.
        """
        return super().get_as_nullable_string("partition") or 'aws'

    def set_partition(self, value: str):
        """
        Sets the AWS partition name.

        :param value: a new AWS partition name.
        """
        super().put("partition", value)

    def get_service(self) -> str:
        """
        Gets the AWS service name.

        :return: the AWS service name.
        """
        return super().get_as_nullable_string("service") or super().get_as_nullable_string("protocol")

    def set_service(self, value: str):
        """
        Sets the AWS service name.

        :param value: a new AWS service name.
        """
        super().put("service", value)

    def get_region(self) -> str:
        """
        Gets the AWS region.

        :return: the AWS region.
        """

        return super().get_as_nullable_string("region")

    def set_region(self, value: str):
        """
        Sets the AWS region.

        :param value: a new AWS region.
        """
        super().put("region", value)

    def get_account(self) -> str:
        """
        Gets the AWS account id.

        :return: the AWS account id.
        """
        return super().get_as_nullable_string('account')

    def set_account(self, value: str):
        """
        Sets the AWS account id.

        :param value: the AWS account id.
        """
        super().put('account', value)

    def get_resource_type(self) -> str:
        """
        Gets the AWS resource type.

        :return: the AWS resource type.
        """
        return super().get_as_nullable_string("resource_type")

    def set_resource_type(self, value: Optional[str]):
        """
        Sets the AWS resource type.

        :param value: a new AWS resource type.
        """
        super().put("resource_type", value)

    def get_resource(self) -> str:
        """
        Gets the AWS resource id.

        :return: the AWS resource id.
        """
        return super().get_as_nullable_string("resource")

    def set_resource(self, value: str):
        """
        Sets the AWS resource id.

        :param value: a new AWS resource id.
        """
        super().put("resource", value)

    def get_arn(self) -> str:
        """
        Gets the AWS resource ARN.
        If the ARN is not defined it automatically generates it from other properties.

        :return: the AWS resource ARN.
        """
        arn = super().get_as_nullable_string("arn")
        if arn: return arn

        arn = "arn"
        partition = self.get_partition() or "aws"
        arn += ":" + partition
        service = self.get_service() or ""
        arn += ":" + service
        region = self.get_region() or ""
        arn += ":" + region
        account = self.get_account() or ""
        arn += ":" + account
        resource_type = self.get_resource_type() or ""
        if resource_type != "":
            arn += ":" + resource_type
        resource = self.get_resource() or ""
        arn += ":" + resource

        return arn

    def set_arn(self, value: str):
        """
        Sets the AWS resource ARN.
        When it sets the value, it automatically parses the ARN
        and sets individual parameters.

        :param value: a new AWS resource ARN.
        """
        super().put('arn', value)

        if value is not None:
            tokens = value.split(':')
            self.set_partition(tokens[1])
            self.set_service(tokens[2])
            self.set_region(tokens[3])
            self.set_account(tokens[4])
            if len(tokens) > 6:
                self.set_resource_type(tokens[5])
                self.set_resource(tokens[6])
            else:
                temp = tokens[5]
                pos = temp.find("/")
                if pos > 0:
                    self.set_resource_type(temp[:pos])
                    self.set_resource(temp[pos + 1:])
                else:
                    self.set_resource_type(None)
                    self.set_resource(temp)

    def get_access_id(self) -> str:
        """
        Gets the AWS access id.

        :return: the AWS access id.
        """
        return super().get_as_nullable_string("access_id") or super().get_as_nullable_string("client_id")

    def set_access_id(self, value: str):
        """
        Sets the AWS access id.

        :param value: the AWS access id.
        """
        super().put('access_id', value)

    def get_access_key(self) -> str:
        """
        Gets the AWS client key.

        :return: the AWS client key.
        """
        return super().get_as_nullable_string("access_key") or super().get_as_nullable_string("client_key")

    def set_access_key(self, value: str):
        """
        Sets the AWS client key.

        :param value: a new AWS client key.
        """
        super().put('access_key', value)

    @staticmethod
    def from_string(line: str) -> 'AwsConnectionParams':
        """
        Creates a new AwsConnectionParams object filled with key-value pairs serialized as a string.

        :param line: a string with serialized key-value pairs as "key1=value1;key2=value2;..."  Example: "Key1=123;Key2=ABC;Key3=2016-09-16T00:00:00.00Z"
        :return: a new AwsConnectionParams object.
        """
        map = StringValueMap.from_string(line)
        return AwsConnectionParams(map)

    def validate(self, correlation_id: Optional[str]):
        """
        Validates this connection parameters

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        arn = self.get_arn()
        if arn == "arn:aws::::":
            raise ConfigException(
                correlation_id,
                "NO_AWS_CONNECTION",
                "AWS connection is not set"
            )

        if self.get_access_id() is None:
            raise ConfigException(
                correlation_id,
                "NO_ACCESS_ID",
                "No access_id is configured in AWS credential"
            )

        if self.get_access_id() is None:
            raise ConfigException(
                correlation_id,
                "NO_ACCESS_KEY",
                "No access_key is configured in AWS credential"
            )

    @staticmethod
    def from_config(config: ConfigParams) -> 'AwsConnectionParams':
        """
        Retrieves AwsConnectionParams from configuration parameters.
        The values are retrieves from "connection" and "credential" sections.

        :param config: configuration parameters
        :return: the generated AwsConnectionParams object.
        """
        result = AwsConnectionParams()
        credentials = CredentialParams.many_from_config(config)
        for credential in credentials:
            result.append(credential)

        connections = ConnectionParams.many_from_config(config)
        for connection in connections:
            result.append(connection)

        return result

    @staticmethod
    def merge_configs(*configs: 'ConfigParams') -> 'AwsConnectionParams':
        """
        Retrieves AwsConnectionParams from multiple configuration parameters.
        The values are retrieves from "connection" and "credential" sections.

        :param configs: a list with configuration parameters
        :return: the generated AwsConnectionParams object.
        """
        config = ConfigParams.merge_configs(*configs)
        return AwsConnectionParams(config)
