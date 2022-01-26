'''
# AWS Database Migration Service Construct Library

This module is part of the [AWS Cloud Development Kit](https://github.com/aws/aws-cdk) project.

```python
import aws_cdk.aws_dms as dms
```

> The construct library for this service is in preview. Since it is not stable yet, it is distributed
> as a separate package so that you can pin its version independently of the rest of the CDK. See the package:
>
> <span class="package-reference">@aws-cdk/aws-dms-alpha</span>

<!--BEGIN CFNONLY DISCLAIMER-->

There are no hand-written ([L2](https://docs.aws.amazon.com/cdk/latest/guide/constructs.html#constructs_lib)) constructs for this service yet.
However, you can still use the automatically generated [L1](https://docs.aws.amazon.com/cdk/latest/guide/constructs.html#constructs_l1_using) constructs, and use this service exactly as you would using CloudFormation directly.

For more information on the resources and properties available for this service, see the [CloudFormation documentation for AWS::DMS](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/AWS_DMS.html).

(Read the [CDK Contributing Guide](https://github.com/aws/aws-cdk/blob/master/CONTRIBUTING.md) if you are interested in contributing to this construct library.)

<!--END CFNONLY DISCLAIMER-->
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

import constructs
from .. import (
    CfnResource as _CfnResource_9df397a6,
    CfnTag as _CfnTag_f6864754,
    IInspectable as _IInspectable_c2943556,
    IResolvable as _IResolvable_da3f097b,
    TagManager as _TagManager_0a598cb3,
    TreeInspector as _TreeInspector_488e0dd5,
)


@jsii.implements(_IInspectable_c2943556)
class CfnCertificate(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_dms.CfnCertificate",
):
    '''A CloudFormation ``AWS::DMS::Certificate``.

    The ``AWS::DMS::Certificate`` resource creates an SSL certificate that encrypts connections between AWS DMS endpoints and the replication instance.

    :cloudformationResource: AWS::DMS::Certificate
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-certificate.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_dms as dms
        
        cfn_certificate = dms.CfnCertificate(self, "MyCfnCertificate",
            certificate_identifier="certificateIdentifier",
            certificate_pem="certificatePem",
            certificate_wallet="certificateWallet"
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        certificate_identifier: typing.Optional[builtins.str] = None,
        certificate_pem: typing.Optional[builtins.str] = None,
        certificate_wallet: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AWS::DMS::Certificate``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param certificate_identifier: A customer-assigned name for the certificate. Identifiers must begin with a letter and must contain only ASCII letters, digits, and hyphens. They can't end with a hyphen or contain two consecutive hyphens.
        :param certificate_pem: The contents of a ``.pem`` file, which contains an X.509 certificate.
        :param certificate_wallet: The location of an imported Oracle Wallet certificate for use with SSL. Example: ``filebase64("${path.root}/rds-ca-2019-root.sso")``
        '''
        props = CfnCertificateProps(
            certificate_identifier=certificate_identifier,
            certificate_pem=certificate_pem,
            certificate_wallet=certificate_wallet,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _TreeInspector_488e0dd5) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateIdentifier")
    def certificate_identifier(self) -> typing.Optional[builtins.str]:
        '''A customer-assigned name for the certificate.

        Identifiers must begin with a letter and must contain only ASCII letters, digits, and hyphens. They can't end with a hyphen or contain two consecutive hyphens.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-certificate.html#cfn-dms-certificate-certificateidentifier
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateIdentifier"))

    @certificate_identifier.setter
    def certificate_identifier(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "certificateIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificatePem")
    def certificate_pem(self) -> typing.Optional[builtins.str]:
        '''The contents of a ``.pem`` file, which contains an X.509 certificate.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-certificate.html#cfn-dms-certificate-certificatepem
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificatePem"))

    @certificate_pem.setter
    def certificate_pem(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "certificatePem", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateWallet")
    def certificate_wallet(self) -> typing.Optional[builtins.str]:
        '''The location of an imported Oracle Wallet certificate for use with SSL.

        Example: ``filebase64("${path.root}/rds-ca-2019-root.sso")``

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-certificate.html#cfn-dms-certificate-certificatewallet
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateWallet"))

    @certificate_wallet.setter
    def certificate_wallet(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "certificateWallet", value)


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_dms.CfnCertificateProps",
    jsii_struct_bases=[],
    name_mapping={
        "certificate_identifier": "certificateIdentifier",
        "certificate_pem": "certificatePem",
        "certificate_wallet": "certificateWallet",
    },
)
class CfnCertificateProps:
    def __init__(
        self,
        *,
        certificate_identifier: typing.Optional[builtins.str] = None,
        certificate_pem: typing.Optional[builtins.str] = None,
        certificate_wallet: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a ``CfnCertificate``.

        :param certificate_identifier: A customer-assigned name for the certificate. Identifiers must begin with a letter and must contain only ASCII letters, digits, and hyphens. They can't end with a hyphen or contain two consecutive hyphens.
        :param certificate_pem: The contents of a ``.pem`` file, which contains an X.509 certificate.
        :param certificate_wallet: The location of an imported Oracle Wallet certificate for use with SSL. Example: ``filebase64("${path.root}/rds-ca-2019-root.sso")``

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-certificate.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_dms as dms
            
            cfn_certificate_props = dms.CfnCertificateProps(
                certificate_identifier="certificateIdentifier",
                certificate_pem="certificatePem",
                certificate_wallet="certificateWallet"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if certificate_identifier is not None:
            self._values["certificate_identifier"] = certificate_identifier
        if certificate_pem is not None:
            self._values["certificate_pem"] = certificate_pem
        if certificate_wallet is not None:
            self._values["certificate_wallet"] = certificate_wallet

    @builtins.property
    def certificate_identifier(self) -> typing.Optional[builtins.str]:
        '''A customer-assigned name for the certificate.

        Identifiers must begin with a letter and must contain only ASCII letters, digits, and hyphens. They can't end with a hyphen or contain two consecutive hyphens.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-certificate.html#cfn-dms-certificate-certificateidentifier
        '''
        result = self._values.get("certificate_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_pem(self) -> typing.Optional[builtins.str]:
        '''The contents of a ``.pem`` file, which contains an X.509 certificate.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-certificate.html#cfn-dms-certificate-certificatepem
        '''
        result = self._values.get("certificate_pem")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_wallet(self) -> typing.Optional[builtins.str]:
        '''The location of an imported Oracle Wallet certificate for use with SSL.

        Example: ``filebase64("${path.root}/rds-ca-2019-root.sso")``

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-certificate.html#cfn-dms-certificate-certificatewallet
        '''
        result = self._values.get("certificate_wallet")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnCertificateProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnEndpoint(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_dms.CfnEndpoint",
):
    '''A CloudFormation ``AWS::DMS::Endpoint``.

    The ``AWS::DMS::Endpoint`` resource creates an AWS DMS endpoint.

    Currently, the only endpoint setting types that AWS CloudFormation supports are *DynamoDBSettings* , *ElasticSearchSettings* , and *NeptuneSettings* .

    :cloudformationResource: AWS::DMS::Endpoint
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_dms as dms
        
        cfn_endpoint = dms.CfnEndpoint(self, "MyCfnEndpoint",
            endpoint_type="endpointType",
            engine_name="engineName",
        
            # the properties below are optional
            certificate_arn="certificateArn",
            database_name="databaseName",
            doc_db_settings=dms.CfnEndpoint.DocDbSettingsProperty(
                secrets_manager_access_role_arn="secretsManagerAccessRoleArn",
                secrets_manager_secret_id="secretsManagerSecretId"
            ),
            dynamo_db_settings=dms.CfnEndpoint.DynamoDbSettingsProperty(
                service_access_role_arn="serviceAccessRoleArn"
            ),
            elasticsearch_settings=dms.CfnEndpoint.ElasticsearchSettingsProperty(
                endpoint_uri="endpointUri",
                error_retry_duration=123,
                full_load_error_percentage=123,
                service_access_role_arn="serviceAccessRoleArn"
            ),
            endpoint_identifier="endpointIdentifier",
            extra_connection_attributes="extraConnectionAttributes",
            ibm_db2_settings=dms.CfnEndpoint.IbmDb2SettingsProperty(
                secrets_manager_access_role_arn="secretsManagerAccessRoleArn",
                secrets_manager_secret_id="secretsManagerSecretId"
            ),
            kafka_settings=dms.CfnEndpoint.KafkaSettingsProperty(
                broker="broker",
                include_control_details=False,
                include_null_and_empty=False,
                include_table_alter_operations=False,
                include_transaction_details=False,
                no_hex_prefix=False,
                partition_include_schema_table=False,
                sasl_password="saslPassword",
                sasl_user_name="saslUserName",
                security_protocol="securityProtocol",
                ssl_ca_certificate_arn="sslCaCertificateArn",
                ssl_client_certificate_arn="sslClientCertificateArn",
                ssl_client_key_arn="sslClientKeyArn",
                ssl_client_key_password="sslClientKeyPassword",
                topic="topic"
            ),
            kinesis_settings=dms.CfnEndpoint.KinesisSettingsProperty(
                include_control_details=False,
                include_null_and_empty=False,
                include_table_alter_operations=False,
                include_transaction_details=False,
                message_format="messageFormat",
                no_hex_prefix=False,
                partition_include_schema_table=False,
                service_access_role_arn="serviceAccessRoleArn",
                stream_arn="streamArn"
            ),
            kms_key_id="kmsKeyId",
            microsoft_sql_server_settings=dms.CfnEndpoint.MicrosoftSqlServerSettingsProperty(
                secrets_manager_access_role_arn="secretsManagerAccessRoleArn",
                secrets_manager_secret_id="secretsManagerSecretId"
            ),
            mongo_db_settings=dms.CfnEndpoint.MongoDbSettingsProperty(
                auth_mechanism="authMechanism",
                auth_source="authSource",
                auth_type="authType",
                database_name="databaseName",
                docs_to_investigate="docsToInvestigate",
                extract_doc_id="extractDocId",
                nesting_level="nestingLevel",
                password="password",
                port=123,
                secrets_manager_access_role_arn="secretsManagerAccessRoleArn",
                secrets_manager_secret_id="secretsManagerSecretId",
                server_name="serverName",
                username="username"
            ),
            my_sql_settings=dms.CfnEndpoint.MySqlSettingsProperty(
                secrets_manager_access_role_arn="secretsManagerAccessRoleArn",
                secrets_manager_secret_id="secretsManagerSecretId"
            ),
            neptune_settings=dms.CfnEndpoint.NeptuneSettingsProperty(
                error_retry_duration=123,
                iam_auth_enabled=False,
                max_file_size=123,
                max_retry_count=123,
                s3_bucket_folder="s3BucketFolder",
                s3_bucket_name="s3BucketName",
                service_access_role_arn="serviceAccessRoleArn"
            ),
            oracle_settings=dms.CfnEndpoint.OracleSettingsProperty(
                secrets_manager_access_role_arn="secretsManagerAccessRoleArn",
                secrets_manager_oracle_asm_access_role_arn="secretsManagerOracleAsmAccessRoleArn",
                secrets_manager_oracle_asm_secret_id="secretsManagerOracleAsmSecretId",
                secrets_manager_secret_id="secretsManagerSecretId"
            ),
            password="password",
            port=123,
            postgre_sql_settings=dms.CfnEndpoint.PostgreSqlSettingsProperty(
                secrets_manager_access_role_arn="secretsManagerAccessRoleArn",
                secrets_manager_secret_id="secretsManagerSecretId"
            ),
            redis_settings=dms.CfnEndpoint.RedisSettingsProperty(
                auth_password="authPassword",
                auth_type="authType",
                auth_user_name="authUserName",
                port=123,
                server_name="serverName",
                ssl_ca_certificate_arn="sslCaCertificateArn",
                ssl_security_protocol="sslSecurityProtocol"
            ),
            redshift_settings=dms.CfnEndpoint.RedshiftSettingsProperty(
                secrets_manager_access_role_arn="secretsManagerAccessRoleArn",
                secrets_manager_secret_id="secretsManagerSecretId"
            ),
            resource_identifier="resourceIdentifier",
            s3_settings=dms.CfnEndpoint.S3SettingsProperty(
                bucket_folder="bucketFolder",
                bucket_name="bucketName",
                compression_type="compressionType",
                csv_delimiter="csvDelimiter",
                csv_row_delimiter="csvRowDelimiter",
                external_table_definition="externalTableDefinition",
                service_access_role_arn="serviceAccessRoleArn"
            ),
            server_name="serverName",
            ssl_mode="sslMode",
            sybase_settings=dms.CfnEndpoint.SybaseSettingsProperty(
                secrets_manager_access_role_arn="secretsManagerAccessRoleArn",
                secrets_manager_secret_id="secretsManagerSecretId"
            ),
            tags=[CfnTag(
                key="key",
                value="value"
            )],
            username="username"
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        endpoint_type: builtins.str,
        engine_name: builtins.str,
        certificate_arn: typing.Optional[builtins.str] = None,
        database_name: typing.Optional[builtins.str] = None,
        doc_db_settings: typing.Optional[typing.Union["CfnEndpoint.DocDbSettingsProperty", _IResolvable_da3f097b]] = None,
        dynamo_db_settings: typing.Optional[typing.Union["CfnEndpoint.DynamoDbSettingsProperty", _IResolvable_da3f097b]] = None,
        elasticsearch_settings: typing.Optional[typing.Union["CfnEndpoint.ElasticsearchSettingsProperty", _IResolvable_da3f097b]] = None,
        endpoint_identifier: typing.Optional[builtins.str] = None,
        extra_connection_attributes: typing.Optional[builtins.str] = None,
        ibm_db2_settings: typing.Optional[typing.Union["CfnEndpoint.IbmDb2SettingsProperty", _IResolvable_da3f097b]] = None,
        kafka_settings: typing.Optional[typing.Union["CfnEndpoint.KafkaSettingsProperty", _IResolvable_da3f097b]] = None,
        kinesis_settings: typing.Optional[typing.Union["CfnEndpoint.KinesisSettingsProperty", _IResolvable_da3f097b]] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        microsoft_sql_server_settings: typing.Optional[typing.Union["CfnEndpoint.MicrosoftSqlServerSettingsProperty", _IResolvable_da3f097b]] = None,
        mongo_db_settings: typing.Optional[typing.Union["CfnEndpoint.MongoDbSettingsProperty", _IResolvable_da3f097b]] = None,
        my_sql_settings: typing.Optional[typing.Union["CfnEndpoint.MySqlSettingsProperty", _IResolvable_da3f097b]] = None,
        neptune_settings: typing.Optional[typing.Union["CfnEndpoint.NeptuneSettingsProperty", _IResolvable_da3f097b]] = None,
        oracle_settings: typing.Optional[typing.Union["CfnEndpoint.OracleSettingsProperty", _IResolvable_da3f097b]] = None,
        password: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        postgre_sql_settings: typing.Optional[typing.Union["CfnEndpoint.PostgreSqlSettingsProperty", _IResolvable_da3f097b]] = None,
        redis_settings: typing.Optional[typing.Union["CfnEndpoint.RedisSettingsProperty", _IResolvable_da3f097b]] = None,
        redshift_settings: typing.Optional[typing.Union["CfnEndpoint.RedshiftSettingsProperty", _IResolvable_da3f097b]] = None,
        resource_identifier: typing.Optional[builtins.str] = None,
        s3_settings: typing.Optional[typing.Union["CfnEndpoint.S3SettingsProperty", _IResolvable_da3f097b]] = None,
        server_name: typing.Optional[builtins.str] = None,
        ssl_mode: typing.Optional[builtins.str] = None,
        sybase_settings: typing.Optional[typing.Union["CfnEndpoint.SybaseSettingsProperty", _IResolvable_da3f097b]] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AWS::DMS::Endpoint``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param endpoint_type: The type of endpoint. Valid values are ``source`` and ``target`` .
        :param engine_name: The type of engine for the endpoint. Valid values, depending on the ``EndpointType`` value, include ``"mysql"`` , ``"oracle"`` , ``"postgres"`` , ``"mariadb"`` , ``"aurora"`` , ``"aurora-postgresql"`` , ``"opensearch"`` , ``"redshift"`` , ``"s3"`` , ``"db2"`` , ``"azuredb"`` , ``"sybase"`` , ``"dynamodb"`` , ``"mongodb"`` , ``"kinesis"`` , ``"kafka"`` , ``"elasticsearch"`` , ``"docdb"`` , ``"sqlserver"`` , and ``"neptune"`` .
        :param certificate_arn: The Amazon Resource Name (ARN) for the certificate.
        :param database_name: The name of the endpoint database. For a MySQL source or target endpoint, do not specify DatabaseName. To migrate to a specific database, use this setting and ``targetDbType`` .
        :param doc_db_settings: Settings in JSON format for the source DocumentDB endpoint. For more information about the available settings, see the configuration properties section in `Using DocumentDB as a Target for AWS Database Migration Service <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Source.DocumentDB.html>`_ in the *AWS Database Migration Service User Guide.*
        :param dynamo_db_settings: Settings in JSON format for the target Amazon DynamoDB endpoint. For information about other available settings, see `Using Object Mapping to Migrate Data to DynamoDB <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.DynamoDB.html#CHAP_Target.DynamoDB.ObjectMapping>`_ in the *AWS Database Migration Service User Guide.*
        :param elasticsearch_settings: Settings in JSON format for the target OpenSearch endpoint. For more information about the available settings, see `Extra Connection Attributes When Using OpenSearch as a Target for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.Elasticsearch.html#CHAP_Target.Elasticsearch.Configuration>`_ in the *AWS Database Migration Service User Guide* .
        :param endpoint_identifier: The database endpoint identifier. Identifiers must begin with a letter and must contain only ASCII letters, digits, and hyphens. They can't end with a hyphen, or contain two consecutive hyphens.
        :param extra_connection_attributes: Additional attributes associated with the connection. Each attribute is specified as a name-value pair associated by an equal sign (=). Multiple attributes are separated by a semicolon (;) with no additional white space. For information on the attributes available for connecting your source or target endpoint, see `Working with AWS DMS Endpoints <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Endpoints.html>`_ in the *AWS Database Migration Service User Guide.*
        :param ibm_db2_settings: Not currently supported by AWS CloudFormation .
        :param kafka_settings: Settings in JSON format for the target Apache Kafka endpoint. For more information about the available settings, see `Using object mapping to migrate data to a Kafka topic <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.Kafka.html#CHAP_Target.Kafka.ObjectMapping>`_ in the *AWS Database Migration Service User Guide.*
        :param kinesis_settings: Settings in JSON format for the target endpoint for Amazon Kinesis Data Streams. For more information about the available settings, see `Using Amazon Kinesis Data Streams as a Target for AWS Database Migration Service <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.Kinesis.html>`_ in the *AWS Database Migration Service User Guide.*
        :param kms_key_id: An AWS KMS key identifier that is used to encrypt the connection parameters for the endpoint. If you don't specify a value for the ``KmsKeyId`` parameter, then AWS DMS uses your default encryption key. AWS KMS creates the default encryption key for your AWS account . Your AWS account has a different default encryption key for each AWS Region .
        :param microsoft_sql_server_settings: Not currently supported by AWS CloudFormation .
        :param mongo_db_settings: Not currently supported by AWS CloudFormation .
        :param my_sql_settings: Settings in JSON format for the source and target MySQL endpoint. For information about other available settings, see `Extra connection attributes when using MySQL as a source for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Source.MySQL.html#CHAP_Source.MySQL.ConnectionAttrib>`_ and `Extra connection attributes when using a MySQL-compatible database as a target for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.MySQL.html#CHAP_Target.MySQL.ConnectionAttrib>`_ in the *AWS Database Migration Service User Guide.*
        :param neptune_settings: ``AWS::DMS::Endpoint.NeptuneSettings``.
        :param oracle_settings: Settings in JSON format for the source and target Oracle endpoint. For information about other available settings, see `Extra connection attributes when using Oracle as a source for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Source.Oracle.html#CHAP_Source.Oracle.ConnectionAttrib>`_ and `Extra connection attributes when using Oracle as a target for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.Oracle.html#CHAP_Target.Oracle.ConnectionAttrib>`_ in the *AWS Database Migration Service User Guide.*
        :param password: The password to be used to log in to the endpoint database.
        :param port: The port used by the endpoint database.
        :param postgre_sql_settings: Not currently supported by AWS CloudFormation .
        :param redis_settings: Settings in JSON format for the target Redis endpoint.
        :param redshift_settings: Not currently supported by AWS CloudFormation .
        :param resource_identifier: A friendly name for the resource identifier at the end of the ``EndpointArn`` response parameter that is returned in the created ``Endpoint`` object. The value for this parameter can have up to 31 characters. It can contain only ASCII letters, digits, and hyphen ('-'). Also, it can't end with a hyphen or contain two consecutive hyphens, and can only begin with a letter, such as ``Example-App-ARN1`` . For example, this value might result in the ``EndpointArn`` value ``arn:aws:dms:eu-west-1:012345678901:rep:Example-App-ARN1`` . If you don't specify a ``ResourceIdentifier`` value, AWS DMS generates a default identifier value for the end of ``EndpointArn`` .
        :param s3_settings: Settings in JSON format for the target Amazon S3 endpoint. For more information about the available settings, see `Extra Connection Attributes When Using Amazon S3 as a Target for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.S3.html#CHAP_Target.S3.Configuring>`_ in the *AWS Database Migration Service User Guide.*
        :param server_name: The name of the server where the endpoint database resides.
        :param ssl_mode: The Secure Sockets Layer (SSL) mode to use for the SSL connection. The default is ``none`` . .. epigraph:: When ``engine_name`` is set to S3, then the only allowed value is ``none`` .
        :param sybase_settings: Settings in JSON format for the source and target SAP ASE endpoint. For information about other available settings, see `Extra connection attributes when using SAP ASE as a source for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Source.SAP.html#CHAP_Source.SAP.ConnectionAttrib>`_ and `Extra connection attributes when using SAP ASE as a target for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.SAP.html#CHAP_Target.SAP.ConnectionAttrib>`_ in the *AWS Database Migration Service User Guide.*
        :param tags: One or more tags to be assigned to the endpoint.
        :param username: The user name to be used to log in to the endpoint database.
        '''
        props = CfnEndpointProps(
            endpoint_type=endpoint_type,
            engine_name=engine_name,
            certificate_arn=certificate_arn,
            database_name=database_name,
            doc_db_settings=doc_db_settings,
            dynamo_db_settings=dynamo_db_settings,
            elasticsearch_settings=elasticsearch_settings,
            endpoint_identifier=endpoint_identifier,
            extra_connection_attributes=extra_connection_attributes,
            ibm_db2_settings=ibm_db2_settings,
            kafka_settings=kafka_settings,
            kinesis_settings=kinesis_settings,
            kms_key_id=kms_key_id,
            microsoft_sql_server_settings=microsoft_sql_server_settings,
            mongo_db_settings=mongo_db_settings,
            my_sql_settings=my_sql_settings,
            neptune_settings=neptune_settings,
            oracle_settings=oracle_settings,
            password=password,
            port=port,
            postgre_sql_settings=postgre_sql_settings,
            redis_settings=redis_settings,
            redshift_settings=redshift_settings,
            resource_identifier=resource_identifier,
            s3_settings=s3_settings,
            server_name=server_name,
            ssl_mode=ssl_mode,
            sybase_settings=sybase_settings,
            tags=tags,
            username=username,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _TreeInspector_488e0dd5) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrExternalId")
    def attr_external_id(self) -> builtins.str:
        '''A value that can be used for cross-account validation.

        :cloudformationAttribute: ExternalId
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrExternalId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''One or more tags to be assigned to the endpoint.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointType")
    def endpoint_type(self) -> builtins.str:
        '''The type of endpoint.

        Valid values are ``source`` and ``target`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-endpointtype
        '''
        return typing.cast(builtins.str, jsii.get(self, "endpointType"))

    @endpoint_type.setter
    def endpoint_type(self, value: builtins.str) -> None:
        jsii.set(self, "endpointType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineName")
    def engine_name(self) -> builtins.str:
        '''The type of engine for the endpoint.

        Valid values, depending on the ``EndpointType`` value, include ``"mysql"`` , ``"oracle"`` , ``"postgres"`` , ``"mariadb"`` , ``"aurora"`` , ``"aurora-postgresql"`` , ``"opensearch"`` , ``"redshift"`` , ``"s3"`` , ``"db2"`` , ``"azuredb"`` , ``"sybase"`` , ``"dynamodb"`` , ``"mongodb"`` , ``"kinesis"`` , ``"kafka"`` , ``"elasticsearch"`` , ``"docdb"`` , ``"sqlserver"`` , and ``"neptune"`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-enginename
        '''
        return typing.cast(builtins.str, jsii.get(self, "engineName"))

    @engine_name.setter
    def engine_name(self, value: builtins.str) -> None:
        jsii.set(self, "engineName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateArn")
    def certificate_arn(self) -> typing.Optional[builtins.str]:
        '''The Amazon Resource Name (ARN) for the certificate.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-certificatearn
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateArn"))

    @certificate_arn.setter
    def certificate_arn(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "certificateArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> typing.Optional[builtins.str]:
        '''The name of the endpoint database.

        For a MySQL source or target endpoint, do not specify DatabaseName. To migrate to a specific database, use this setting and ``targetDbType`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-databasename
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseName"))

    @database_name.setter
    def database_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "databaseName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="docDbSettings")
    def doc_db_settings(
        self,
    ) -> typing.Optional[typing.Union["CfnEndpoint.DocDbSettingsProperty", _IResolvable_da3f097b]]:
        '''Settings in JSON format for the source DocumentDB endpoint.

        For more information about the available settings, see the configuration properties section in `Using DocumentDB as a Target for AWS Database Migration Service <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Source.DocumentDB.html>`_ in the *AWS Database Migration Service User Guide.*

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-docdbsettings
        '''
        return typing.cast(typing.Optional[typing.Union["CfnEndpoint.DocDbSettingsProperty", _IResolvable_da3f097b]], jsii.get(self, "docDbSettings"))

    @doc_db_settings.setter
    def doc_db_settings(
        self,
        value: typing.Optional[typing.Union["CfnEndpoint.DocDbSettingsProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "docDbSettings", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dynamoDbSettings")
    def dynamo_db_settings(
        self,
    ) -> typing.Optional[typing.Union["CfnEndpoint.DynamoDbSettingsProperty", _IResolvable_da3f097b]]:
        '''Settings in JSON format for the target Amazon DynamoDB endpoint.

        For information about other available settings, see `Using Object Mapping to Migrate Data to DynamoDB <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.DynamoDB.html#CHAP_Target.DynamoDB.ObjectMapping>`_ in the *AWS Database Migration Service User Guide.*

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-dynamodbsettings
        '''
        return typing.cast(typing.Optional[typing.Union["CfnEndpoint.DynamoDbSettingsProperty", _IResolvable_da3f097b]], jsii.get(self, "dynamoDbSettings"))

    @dynamo_db_settings.setter
    def dynamo_db_settings(
        self,
        value: typing.Optional[typing.Union["CfnEndpoint.DynamoDbSettingsProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "dynamoDbSettings", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticsearchSettings")
    def elasticsearch_settings(
        self,
    ) -> typing.Optional[typing.Union["CfnEndpoint.ElasticsearchSettingsProperty", _IResolvable_da3f097b]]:
        '''Settings in JSON format for the target OpenSearch endpoint.

        For more information about the available settings, see `Extra Connection Attributes When Using OpenSearch as a Target for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.Elasticsearch.html#CHAP_Target.Elasticsearch.Configuration>`_ in the *AWS Database Migration Service User Guide* .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-elasticsearchsettings
        '''
        return typing.cast(typing.Optional[typing.Union["CfnEndpoint.ElasticsearchSettingsProperty", _IResolvable_da3f097b]], jsii.get(self, "elasticsearchSettings"))

    @elasticsearch_settings.setter
    def elasticsearch_settings(
        self,
        value: typing.Optional[typing.Union["CfnEndpoint.ElasticsearchSettingsProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "elasticsearchSettings", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointIdentifier")
    def endpoint_identifier(self) -> typing.Optional[builtins.str]:
        '''The database endpoint identifier.

        Identifiers must begin with a letter and must contain only ASCII letters, digits, and hyphens. They can't end with a hyphen, or contain two consecutive hyphens.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-endpointidentifier
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpointIdentifier"))

    @endpoint_identifier.setter
    def endpoint_identifier(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "endpointIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="extraConnectionAttributes")
    def extra_connection_attributes(self) -> typing.Optional[builtins.str]:
        '''Additional attributes associated with the connection.

        Each attribute is specified as a name-value pair associated by an equal sign (=). Multiple attributes are separated by a semicolon (;) with no additional white space. For information on the attributes available for connecting your source or target endpoint, see `Working with AWS DMS Endpoints <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Endpoints.html>`_ in the *AWS Database Migration Service User Guide.*

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-extraconnectionattributes
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "extraConnectionAttributes"))

    @extra_connection_attributes.setter
    def extra_connection_attributes(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "extraConnectionAttributes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ibmDb2Settings")
    def ibm_db2_settings(
        self,
    ) -> typing.Optional[typing.Union["CfnEndpoint.IbmDb2SettingsProperty", _IResolvable_da3f097b]]:
        '''Not currently supported by AWS CloudFormation .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-ibmdb2settings
        '''
        return typing.cast(typing.Optional[typing.Union["CfnEndpoint.IbmDb2SettingsProperty", _IResolvable_da3f097b]], jsii.get(self, "ibmDb2Settings"))

    @ibm_db2_settings.setter
    def ibm_db2_settings(
        self,
        value: typing.Optional[typing.Union["CfnEndpoint.IbmDb2SettingsProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "ibmDb2Settings", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kafkaSettings")
    def kafka_settings(
        self,
    ) -> typing.Optional[typing.Union["CfnEndpoint.KafkaSettingsProperty", _IResolvable_da3f097b]]:
        '''Settings in JSON format for the target Apache Kafka endpoint.

        For more information about the available settings, see `Using object mapping to migrate data to a Kafka topic <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.Kafka.html#CHAP_Target.Kafka.ObjectMapping>`_ in the *AWS Database Migration Service User Guide.*

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-kafkasettings
        '''
        return typing.cast(typing.Optional[typing.Union["CfnEndpoint.KafkaSettingsProperty", _IResolvable_da3f097b]], jsii.get(self, "kafkaSettings"))

    @kafka_settings.setter
    def kafka_settings(
        self,
        value: typing.Optional[typing.Union["CfnEndpoint.KafkaSettingsProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "kafkaSettings", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kinesisSettings")
    def kinesis_settings(
        self,
    ) -> typing.Optional[typing.Union["CfnEndpoint.KinesisSettingsProperty", _IResolvable_da3f097b]]:
        '''Settings in JSON format for the target endpoint for Amazon Kinesis Data Streams.

        For more information about the available settings, see `Using Amazon Kinesis Data Streams as a Target for AWS Database Migration Service <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.Kinesis.html>`_ in the *AWS Database Migration Service User Guide.*

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-kinesissettings
        '''
        return typing.cast(typing.Optional[typing.Union["CfnEndpoint.KinesisSettingsProperty", _IResolvable_da3f097b]], jsii.get(self, "kinesisSettings"))

    @kinesis_settings.setter
    def kinesis_settings(
        self,
        value: typing.Optional[typing.Union["CfnEndpoint.KinesisSettingsProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "kinesisSettings", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''An AWS KMS key identifier that is used to encrypt the connection parameters for the endpoint.

        If you don't specify a value for the ``KmsKeyId`` parameter, then AWS DMS uses your default encryption key.

        AWS KMS creates the default encryption key for your AWS account . Your AWS account has a different default encryption key for each AWS Region .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-kmskeyid
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyId"))

    @kms_key_id.setter
    def kms_key_id(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "kmsKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="microsoftSqlServerSettings")
    def microsoft_sql_server_settings(
        self,
    ) -> typing.Optional[typing.Union["CfnEndpoint.MicrosoftSqlServerSettingsProperty", _IResolvable_da3f097b]]:
        '''Not currently supported by AWS CloudFormation .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-microsoftsqlserversettings
        '''
        return typing.cast(typing.Optional[typing.Union["CfnEndpoint.MicrosoftSqlServerSettingsProperty", _IResolvable_da3f097b]], jsii.get(self, "microsoftSqlServerSettings"))

    @microsoft_sql_server_settings.setter
    def microsoft_sql_server_settings(
        self,
        value: typing.Optional[typing.Union["CfnEndpoint.MicrosoftSqlServerSettingsProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "microsoftSqlServerSettings", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mongoDbSettings")
    def mongo_db_settings(
        self,
    ) -> typing.Optional[typing.Union["CfnEndpoint.MongoDbSettingsProperty", _IResolvable_da3f097b]]:
        '''Not currently supported by AWS CloudFormation .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-mongodbsettings
        '''
        return typing.cast(typing.Optional[typing.Union["CfnEndpoint.MongoDbSettingsProperty", _IResolvable_da3f097b]], jsii.get(self, "mongoDbSettings"))

    @mongo_db_settings.setter
    def mongo_db_settings(
        self,
        value: typing.Optional[typing.Union["CfnEndpoint.MongoDbSettingsProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "mongoDbSettings", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mySqlSettings")
    def my_sql_settings(
        self,
    ) -> typing.Optional[typing.Union["CfnEndpoint.MySqlSettingsProperty", _IResolvable_da3f097b]]:
        '''Settings in JSON format for the source and target MySQL endpoint.

        For information about other available settings, see `Extra connection attributes when using MySQL as a source for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Source.MySQL.html#CHAP_Source.MySQL.ConnectionAttrib>`_ and `Extra connection attributes when using a MySQL-compatible database as a target for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.MySQL.html#CHAP_Target.MySQL.ConnectionAttrib>`_ in the *AWS Database Migration Service User Guide.*

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-mysqlsettings
        '''
        return typing.cast(typing.Optional[typing.Union["CfnEndpoint.MySqlSettingsProperty", _IResolvable_da3f097b]], jsii.get(self, "mySqlSettings"))

    @my_sql_settings.setter
    def my_sql_settings(
        self,
        value: typing.Optional[typing.Union["CfnEndpoint.MySqlSettingsProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "mySqlSettings", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="neptuneSettings")
    def neptune_settings(
        self,
    ) -> typing.Optional[typing.Union["CfnEndpoint.NeptuneSettingsProperty", _IResolvable_da3f097b]]:
        '''``AWS::DMS::Endpoint.NeptuneSettings``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-neptunesettings
        '''
        return typing.cast(typing.Optional[typing.Union["CfnEndpoint.NeptuneSettingsProperty", _IResolvable_da3f097b]], jsii.get(self, "neptuneSettings"))

    @neptune_settings.setter
    def neptune_settings(
        self,
        value: typing.Optional[typing.Union["CfnEndpoint.NeptuneSettingsProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "neptuneSettings", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="oracleSettings")
    def oracle_settings(
        self,
    ) -> typing.Optional[typing.Union["CfnEndpoint.OracleSettingsProperty", _IResolvable_da3f097b]]:
        '''Settings in JSON format for the source and target Oracle endpoint.

        For information about other available settings, see `Extra connection attributes when using Oracle as a source for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Source.Oracle.html#CHAP_Source.Oracle.ConnectionAttrib>`_ and `Extra connection attributes when using Oracle as a target for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.Oracle.html#CHAP_Target.Oracle.ConnectionAttrib>`_ in the *AWS Database Migration Service User Guide.*

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-oraclesettings
        '''
        return typing.cast(typing.Optional[typing.Union["CfnEndpoint.OracleSettingsProperty", _IResolvable_da3f097b]], jsii.get(self, "oracleSettings"))

    @oracle_settings.setter
    def oracle_settings(
        self,
        value: typing.Optional[typing.Union["CfnEndpoint.OracleSettingsProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "oracleSettings", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="password")
    def password(self) -> typing.Optional[builtins.str]:
        '''The password to be used to log in to the endpoint database.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-password
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "password"))

    @password.setter
    def password(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "password", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> typing.Optional[jsii.Number]:
        '''The port used by the endpoint database.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-port
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "port"))

    @port.setter
    def port(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "port", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="postgreSqlSettings")
    def postgre_sql_settings(
        self,
    ) -> typing.Optional[typing.Union["CfnEndpoint.PostgreSqlSettingsProperty", _IResolvable_da3f097b]]:
        '''Not currently supported by AWS CloudFormation .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-postgresqlsettings
        '''
        return typing.cast(typing.Optional[typing.Union["CfnEndpoint.PostgreSqlSettingsProperty", _IResolvable_da3f097b]], jsii.get(self, "postgreSqlSettings"))

    @postgre_sql_settings.setter
    def postgre_sql_settings(
        self,
        value: typing.Optional[typing.Union["CfnEndpoint.PostgreSqlSettingsProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "postgreSqlSettings", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="redisSettings")
    def redis_settings(
        self,
    ) -> typing.Optional[typing.Union["CfnEndpoint.RedisSettingsProperty", _IResolvable_da3f097b]]:
        '''Settings in JSON format for the target Redis endpoint.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-redissettings
        '''
        return typing.cast(typing.Optional[typing.Union["CfnEndpoint.RedisSettingsProperty", _IResolvable_da3f097b]], jsii.get(self, "redisSettings"))

    @redis_settings.setter
    def redis_settings(
        self,
        value: typing.Optional[typing.Union["CfnEndpoint.RedisSettingsProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "redisSettings", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="redshiftSettings")
    def redshift_settings(
        self,
    ) -> typing.Optional[typing.Union["CfnEndpoint.RedshiftSettingsProperty", _IResolvable_da3f097b]]:
        '''Not currently supported by AWS CloudFormation .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-redshiftsettings
        '''
        return typing.cast(typing.Optional[typing.Union["CfnEndpoint.RedshiftSettingsProperty", _IResolvable_da3f097b]], jsii.get(self, "redshiftSettings"))

    @redshift_settings.setter
    def redshift_settings(
        self,
        value: typing.Optional[typing.Union["CfnEndpoint.RedshiftSettingsProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "redshiftSettings", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceIdentifier")
    def resource_identifier(self) -> typing.Optional[builtins.str]:
        '''A friendly name for the resource identifier at the end of the ``EndpointArn`` response parameter that is returned in the created ``Endpoint`` object.

        The value for this parameter can have up to 31 characters. It can contain only ASCII letters, digits, and hyphen ('-'). Also, it can't end with a hyphen or contain two consecutive hyphens, and can only begin with a letter, such as ``Example-App-ARN1`` . For example, this value might result in the ``EndpointArn`` value ``arn:aws:dms:eu-west-1:012345678901:rep:Example-App-ARN1`` . If you don't specify a ``ResourceIdentifier`` value, AWS DMS generates a default identifier value for the end of ``EndpointArn`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-resourceidentifier
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceIdentifier"))

    @resource_identifier.setter
    def resource_identifier(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "resourceIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Settings")
    def s3_settings(
        self,
    ) -> typing.Optional[typing.Union["CfnEndpoint.S3SettingsProperty", _IResolvable_da3f097b]]:
        '''Settings in JSON format for the target Amazon S3 endpoint.

        For more information about the available settings, see `Extra Connection Attributes When Using Amazon S3 as a Target for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.S3.html#CHAP_Target.S3.Configuring>`_ in the *AWS Database Migration Service User Guide.*

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-s3settings
        '''
        return typing.cast(typing.Optional[typing.Union["CfnEndpoint.S3SettingsProperty", _IResolvable_da3f097b]], jsii.get(self, "s3Settings"))

    @s3_settings.setter
    def s3_settings(
        self,
        value: typing.Optional[typing.Union["CfnEndpoint.S3SettingsProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "s3Settings", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverName")
    def server_name(self) -> typing.Optional[builtins.str]:
        '''The name of the server where the endpoint database resides.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-servername
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serverName"))

    @server_name.setter
    def server_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "serverName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sslMode")
    def ssl_mode(self) -> typing.Optional[builtins.str]:
        '''The Secure Sockets Layer (SSL) mode to use for the SSL connection. The default is ``none`` .

        .. epigraph::

           When ``engine_name`` is set to S3, then the only allowed value is ``none`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-sslmode
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sslMode"))

    @ssl_mode.setter
    def ssl_mode(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "sslMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sybaseSettings")
    def sybase_settings(
        self,
    ) -> typing.Optional[typing.Union["CfnEndpoint.SybaseSettingsProperty", _IResolvable_da3f097b]]:
        '''Settings in JSON format for the source and target SAP ASE endpoint.

        For information about other available settings, see `Extra connection attributes when using SAP ASE as a source for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Source.SAP.html#CHAP_Source.SAP.ConnectionAttrib>`_ and `Extra connection attributes when using SAP ASE as a target for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.SAP.html#CHAP_Target.SAP.ConnectionAttrib>`_ in the *AWS Database Migration Service User Guide.*

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-sybasesettings
        '''
        return typing.cast(typing.Optional[typing.Union["CfnEndpoint.SybaseSettingsProperty", _IResolvable_da3f097b]], jsii.get(self, "sybaseSettings"))

    @sybase_settings.setter
    def sybase_settings(
        self,
        value: typing.Optional[typing.Union["CfnEndpoint.SybaseSettingsProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "sybaseSettings", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="username")
    def username(self) -> typing.Optional[builtins.str]:
        '''The user name to be used to log in to the endpoint database.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-username
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "username"))

    @username.setter
    def username(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "username", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_dms.CfnEndpoint.DocDbSettingsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "secrets_manager_access_role_arn": "secretsManagerAccessRoleArn",
            "secrets_manager_secret_id": "secretsManagerSecretId",
        },
    )
    class DocDbSettingsProperty:
        def __init__(
            self,
            *,
            secrets_manager_access_role_arn: typing.Optional[builtins.str] = None,
            secrets_manager_secret_id: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Not currently supported by AWS CloudFormation .

            :param secrets_manager_access_role_arn: Not currently supported by AWS CloudFormation .
            :param secrets_manager_secret_id: Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-docdbsettings.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_dms as dms
                
                doc_db_settings_property = dms.CfnEndpoint.DocDbSettingsProperty(
                    secrets_manager_access_role_arn="secretsManagerAccessRoleArn",
                    secrets_manager_secret_id="secretsManagerSecretId"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if secrets_manager_access_role_arn is not None:
                self._values["secrets_manager_access_role_arn"] = secrets_manager_access_role_arn
            if secrets_manager_secret_id is not None:
                self._values["secrets_manager_secret_id"] = secrets_manager_secret_id

        @builtins.property
        def secrets_manager_access_role_arn(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-docdbsettings.html#cfn-dms-endpoint-docdbsettings-secretsmanageraccessrolearn
            '''
            result = self._values.get("secrets_manager_access_role_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def secrets_manager_secret_id(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-docdbsettings.html#cfn-dms-endpoint-docdbsettings-secretsmanagersecretid
            '''
            result = self._values.get("secrets_manager_secret_id")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "DocDbSettingsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_dms.CfnEndpoint.DynamoDbSettingsProperty",
        jsii_struct_bases=[],
        name_mapping={"service_access_role_arn": "serviceAccessRoleArn"},
    )
    class DynamoDbSettingsProperty:
        def __init__(
            self,
            *,
            service_access_role_arn: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Provides the Amazon Resource Name (ARN) of the AWS Identity and Access Management (IAM) role used to define an Amazon DynamoDB target endpoint.

            :param service_access_role_arn: The Amazon Resource Name (ARN) used by the service to access the IAM role. The role must allow the ``iam:PassRole`` action.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-dynamodbsettings.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_dms as dms
                
                dynamo_db_settings_property = dms.CfnEndpoint.DynamoDbSettingsProperty(
                    service_access_role_arn="serviceAccessRoleArn"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if service_access_role_arn is not None:
                self._values["service_access_role_arn"] = service_access_role_arn

        @builtins.property
        def service_access_role_arn(self) -> typing.Optional[builtins.str]:
            '''The Amazon Resource Name (ARN) used by the service to access the IAM role.

            The role must allow the ``iam:PassRole`` action.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-dynamodbsettings.html#cfn-dms-endpoint-dynamodbsettings-serviceaccessrolearn
            '''
            result = self._values.get("service_access_role_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "DynamoDbSettingsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_dms.CfnEndpoint.ElasticsearchSettingsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "endpoint_uri": "endpointUri",
            "error_retry_duration": "errorRetryDuration",
            "full_load_error_percentage": "fullLoadErrorPercentage",
            "service_access_role_arn": "serviceAccessRoleArn",
        },
    )
    class ElasticsearchSettingsProperty:
        def __init__(
            self,
            *,
            endpoint_uri: typing.Optional[builtins.str] = None,
            error_retry_duration: typing.Optional[jsii.Number] = None,
            full_load_error_percentage: typing.Optional[jsii.Number] = None,
            service_access_role_arn: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Provides information that defines an OpenSearch endpoint.

            :param endpoint_uri: The endpoint for the OpenSearch cluster. AWS DMS uses HTTPS if a transport protocol (http/https) is not specified.
            :param error_retry_duration: The maximum number of seconds for which DMS retries failed API requests to the OpenSearch cluster.
            :param full_load_error_percentage: The maximum percentage of records that can fail to be written before a full load operation stops. To avoid early failure, this counter is only effective after 1000 records are transferred. OpenSearch also has the concept of error monitoring during the last 10 minutes of an Observation Window. If transfer of all records fail in the last 10 minutes, the full load operation stops.
            :param service_access_role_arn: The Amazon Resource Name (ARN) used by the service to access the IAM role. The role must allow the ``iam:PassRole`` action.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-elasticsearchsettings.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_dms as dms
                
                elasticsearch_settings_property = dms.CfnEndpoint.ElasticsearchSettingsProperty(
                    endpoint_uri="endpointUri",
                    error_retry_duration=123,
                    full_load_error_percentage=123,
                    service_access_role_arn="serviceAccessRoleArn"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if endpoint_uri is not None:
                self._values["endpoint_uri"] = endpoint_uri
            if error_retry_duration is not None:
                self._values["error_retry_duration"] = error_retry_duration
            if full_load_error_percentage is not None:
                self._values["full_load_error_percentage"] = full_load_error_percentage
            if service_access_role_arn is not None:
                self._values["service_access_role_arn"] = service_access_role_arn

        @builtins.property
        def endpoint_uri(self) -> typing.Optional[builtins.str]:
            '''The endpoint for the OpenSearch cluster.

            AWS DMS uses HTTPS if a transport protocol (http/https) is not specified.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-elasticsearchsettings.html#cfn-dms-endpoint-elasticsearchsettings-endpointuri
            '''
            result = self._values.get("endpoint_uri")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def error_retry_duration(self) -> typing.Optional[jsii.Number]:
            '''The maximum number of seconds for which DMS retries failed API requests to the OpenSearch cluster.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-elasticsearchsettings.html#cfn-dms-endpoint-elasticsearchsettings-errorretryduration
            '''
            result = self._values.get("error_retry_duration")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def full_load_error_percentage(self) -> typing.Optional[jsii.Number]:
            '''The maximum percentage of records that can fail to be written before a full load operation stops.

            To avoid early failure, this counter is only effective after 1000 records are transferred. OpenSearch also has the concept of error monitoring during the last 10 minutes of an Observation Window. If transfer of all records fail in the last 10 minutes, the full load operation stops.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-elasticsearchsettings.html#cfn-dms-endpoint-elasticsearchsettings-fullloaderrorpercentage
            '''
            result = self._values.get("full_load_error_percentage")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def service_access_role_arn(self) -> typing.Optional[builtins.str]:
            '''The Amazon Resource Name (ARN) used by the service to access the IAM role.

            The role must allow the ``iam:PassRole`` action.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-elasticsearchsettings.html#cfn-dms-endpoint-elasticsearchsettings-serviceaccessrolearn
            '''
            result = self._values.get("service_access_role_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ElasticsearchSettingsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_dms.CfnEndpoint.IbmDb2SettingsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "secrets_manager_access_role_arn": "secretsManagerAccessRoleArn",
            "secrets_manager_secret_id": "secretsManagerSecretId",
        },
    )
    class IbmDb2SettingsProperty:
        def __init__(
            self,
            *,
            secrets_manager_access_role_arn: typing.Optional[builtins.str] = None,
            secrets_manager_secret_id: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Not currently supported by AWS CloudFormation .

            :param secrets_manager_access_role_arn: Not currently supported by AWS CloudFormation .
            :param secrets_manager_secret_id: Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-ibmdb2settings.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_dms as dms
                
                ibm_db2_settings_property = dms.CfnEndpoint.IbmDb2SettingsProperty(
                    secrets_manager_access_role_arn="secretsManagerAccessRoleArn",
                    secrets_manager_secret_id="secretsManagerSecretId"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if secrets_manager_access_role_arn is not None:
                self._values["secrets_manager_access_role_arn"] = secrets_manager_access_role_arn
            if secrets_manager_secret_id is not None:
                self._values["secrets_manager_secret_id"] = secrets_manager_secret_id

        @builtins.property
        def secrets_manager_access_role_arn(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-ibmdb2settings.html#cfn-dms-endpoint-ibmdb2settings-secretsmanageraccessrolearn
            '''
            result = self._values.get("secrets_manager_access_role_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def secrets_manager_secret_id(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-ibmdb2settings.html#cfn-dms-endpoint-ibmdb2settings-secretsmanagersecretid
            '''
            result = self._values.get("secrets_manager_secret_id")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "IbmDb2SettingsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_dms.CfnEndpoint.KafkaSettingsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "broker": "broker",
            "include_control_details": "includeControlDetails",
            "include_null_and_empty": "includeNullAndEmpty",
            "include_table_alter_operations": "includeTableAlterOperations",
            "include_transaction_details": "includeTransactionDetails",
            "no_hex_prefix": "noHexPrefix",
            "partition_include_schema_table": "partitionIncludeSchemaTable",
            "sasl_password": "saslPassword",
            "sasl_user_name": "saslUserName",
            "security_protocol": "securityProtocol",
            "ssl_ca_certificate_arn": "sslCaCertificateArn",
            "ssl_client_certificate_arn": "sslClientCertificateArn",
            "ssl_client_key_arn": "sslClientKeyArn",
            "ssl_client_key_password": "sslClientKeyPassword",
            "topic": "topic",
        },
    )
    class KafkaSettingsProperty:
        def __init__(
            self,
            *,
            broker: typing.Optional[builtins.str] = None,
            include_control_details: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            include_null_and_empty: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            include_table_alter_operations: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            include_transaction_details: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            no_hex_prefix: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            partition_include_schema_table: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            sasl_password: typing.Optional[builtins.str] = None,
            sasl_user_name: typing.Optional[builtins.str] = None,
            security_protocol: typing.Optional[builtins.str] = None,
            ssl_ca_certificate_arn: typing.Optional[builtins.str] = None,
            ssl_client_certificate_arn: typing.Optional[builtins.str] = None,
            ssl_client_key_arn: typing.Optional[builtins.str] = None,
            ssl_client_key_password: typing.Optional[builtins.str] = None,
            topic: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Not currently supported by AWS CloudFormation .

            :param broker: Not currently supported by AWS CloudFormation .
            :param include_control_details: Shows detailed control information for table definition, column definition, and table and column changes in the Kafka message output. The default is ``false`` .
            :param include_null_and_empty: Include NULL and empty columns for records migrated to the endpoint. The default is ``false`` .
            :param include_table_alter_operations: Includes any data definition language (DDL) operations that change the table in the control data, such as ``rename-table`` , ``drop-table`` , ``add-column`` , ``drop-column`` , and ``rename-column`` . The default is ``false`` .
            :param include_transaction_details: Provides detailed transaction information from the source database. This information includes a commit timestamp, a log position, and values for ``transaction_id`` , previous ``transaction_id`` , and ``transaction_record_id`` (the record offset within a transaction). The default is ``false`` .
            :param no_hex_prefix: Set this optional parameter to ``true`` to avoid adding a '0x' prefix to raw data in hexadecimal format. For example, by default, AWS DMS adds a '0x' prefix to the LOB column type in hexadecimal format moving from an Oracle source to a Kafka target. Use the ``NoHexPrefix`` endpoint setting to enable migration of RAW data type columns without adding the '0x' prefix.
            :param partition_include_schema_table: Prefixes schema and table names to partition values, when the partition type is ``primary-key-type`` . Doing this increases data distribution among Kafka partitions. For example, suppose that a SysBench schema has thousands of tables and each table has only limited range for a primary key. In this case, the same primary key is sent from thousands of tables to the same partition, which causes throttling. The default is ``false`` .
            :param sasl_password: The secure password you created when you first set up your MSK cluster to validate a client identity and make an encrypted connection between server and client using SASL-SSL authentication.
            :param sasl_user_name: The secure user name you created when you first set up your MSK cluster to validate a client identity and make an encrypted connection between server and client using SASL-SSL authentication.
            :param security_protocol: Set secure connection to a Kafka target endpoint using Transport Layer Security (TLS). Options include ``ssl-encryption`` , ``ssl-authentication`` , and ``sasl-ssl`` . ``sasl-ssl`` requires ``SaslUsername`` and ``SaslPassword`` .
            :param ssl_ca_certificate_arn: The Amazon Resource Name (ARN) for the private certificate authority (CA) cert that AWS DMS uses to securely connect to your Kafka target endpoint.
            :param ssl_client_certificate_arn: The Amazon Resource Name (ARN) of the client certificate used to securely connect to a Kafka target endpoint.
            :param ssl_client_key_arn: The Amazon Resource Name (ARN) for the client private key used to securely connect to a Kafka target endpoint.
            :param ssl_client_key_password: The password for the client private key used to securely connect to a Kafka target endpoint.
            :param topic: Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kafkasettings.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_dms as dms
                
                kafka_settings_property = dms.CfnEndpoint.KafkaSettingsProperty(
                    broker="broker",
                    include_control_details=False,
                    include_null_and_empty=False,
                    include_table_alter_operations=False,
                    include_transaction_details=False,
                    no_hex_prefix=False,
                    partition_include_schema_table=False,
                    sasl_password="saslPassword",
                    sasl_user_name="saslUserName",
                    security_protocol="securityProtocol",
                    ssl_ca_certificate_arn="sslCaCertificateArn",
                    ssl_client_certificate_arn="sslClientCertificateArn",
                    ssl_client_key_arn="sslClientKeyArn",
                    ssl_client_key_password="sslClientKeyPassword",
                    topic="topic"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if broker is not None:
                self._values["broker"] = broker
            if include_control_details is not None:
                self._values["include_control_details"] = include_control_details
            if include_null_and_empty is not None:
                self._values["include_null_and_empty"] = include_null_and_empty
            if include_table_alter_operations is not None:
                self._values["include_table_alter_operations"] = include_table_alter_operations
            if include_transaction_details is not None:
                self._values["include_transaction_details"] = include_transaction_details
            if no_hex_prefix is not None:
                self._values["no_hex_prefix"] = no_hex_prefix
            if partition_include_schema_table is not None:
                self._values["partition_include_schema_table"] = partition_include_schema_table
            if sasl_password is not None:
                self._values["sasl_password"] = sasl_password
            if sasl_user_name is not None:
                self._values["sasl_user_name"] = sasl_user_name
            if security_protocol is not None:
                self._values["security_protocol"] = security_protocol
            if ssl_ca_certificate_arn is not None:
                self._values["ssl_ca_certificate_arn"] = ssl_ca_certificate_arn
            if ssl_client_certificate_arn is not None:
                self._values["ssl_client_certificate_arn"] = ssl_client_certificate_arn
            if ssl_client_key_arn is not None:
                self._values["ssl_client_key_arn"] = ssl_client_key_arn
            if ssl_client_key_password is not None:
                self._values["ssl_client_key_password"] = ssl_client_key_password
            if topic is not None:
                self._values["topic"] = topic

        @builtins.property
        def broker(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kafkasettings.html#cfn-dms-endpoint-kafkasettings-broker
            '''
            result = self._values.get("broker")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def include_control_details(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''Shows detailed control information for table definition, column definition, and table and column changes in the Kafka message output.

            The default is ``false`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kafkasettings.html#cfn-dms-endpoint-kafkasettings-includecontroldetails
            '''
            result = self._values.get("include_control_details")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def include_null_and_empty(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''Include NULL and empty columns for records migrated to the endpoint.

            The default is ``false`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kafkasettings.html#cfn-dms-endpoint-kafkasettings-includenullandempty
            '''
            result = self._values.get("include_null_and_empty")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def include_table_alter_operations(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''Includes any data definition language (DDL) operations that change the table in the control data, such as ``rename-table`` , ``drop-table`` , ``add-column`` , ``drop-column`` , and ``rename-column`` .

            The default is ``false`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kafkasettings.html#cfn-dms-endpoint-kafkasettings-includetablealteroperations
            '''
            result = self._values.get("include_table_alter_operations")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def include_transaction_details(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''Provides detailed transaction information from the source database.

            This information includes a commit timestamp, a log position, and values for ``transaction_id`` , previous ``transaction_id`` , and ``transaction_record_id`` (the record offset within a transaction). The default is ``false`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kafkasettings.html#cfn-dms-endpoint-kafkasettings-includetransactiondetails
            '''
            result = self._values.get("include_transaction_details")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def no_hex_prefix(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''Set this optional parameter to ``true`` to avoid adding a '0x' prefix to raw data in hexadecimal format.

            For example, by default, AWS DMS adds a '0x' prefix to the LOB column type in hexadecimal format moving from an Oracle source to a Kafka target. Use the ``NoHexPrefix`` endpoint setting to enable migration of RAW data type columns without adding the '0x' prefix.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kafkasettings.html#cfn-dms-endpoint-kafkasettings-nohexprefix
            '''
            result = self._values.get("no_hex_prefix")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def partition_include_schema_table(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''Prefixes schema and table names to partition values, when the partition type is ``primary-key-type`` .

            Doing this increases data distribution among Kafka partitions. For example, suppose that a SysBench schema has thousands of tables and each table has only limited range for a primary key. In this case, the same primary key is sent from thousands of tables to the same partition, which causes throttling. The default is ``false`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kafkasettings.html#cfn-dms-endpoint-kafkasettings-partitionincludeschematable
            '''
            result = self._values.get("partition_include_schema_table")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def sasl_password(self) -> typing.Optional[builtins.str]:
            '''The secure password you created when you first set up your MSK cluster to validate a client identity and make an encrypted connection between server and client using SASL-SSL authentication.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kafkasettings.html#cfn-dms-endpoint-kafkasettings-saslpassword
            '''
            result = self._values.get("sasl_password")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def sasl_user_name(self) -> typing.Optional[builtins.str]:
            '''The secure user name you created when you first set up your MSK cluster to validate a client identity and make an encrypted connection between server and client using SASL-SSL authentication.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kafkasettings.html#cfn-dms-endpoint-kafkasettings-saslusername
            '''
            result = self._values.get("sasl_user_name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def security_protocol(self) -> typing.Optional[builtins.str]:
            '''Set secure connection to a Kafka target endpoint using Transport Layer Security (TLS).

            Options include ``ssl-encryption`` , ``ssl-authentication`` , and ``sasl-ssl`` . ``sasl-ssl`` requires ``SaslUsername`` and ``SaslPassword`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kafkasettings.html#cfn-dms-endpoint-kafkasettings-securityprotocol
            '''
            result = self._values.get("security_protocol")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def ssl_ca_certificate_arn(self) -> typing.Optional[builtins.str]:
            '''The Amazon Resource Name (ARN) for the private certificate authority (CA) cert that AWS DMS uses to securely connect to your Kafka target endpoint.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kafkasettings.html#cfn-dms-endpoint-kafkasettings-sslcacertificatearn
            '''
            result = self._values.get("ssl_ca_certificate_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def ssl_client_certificate_arn(self) -> typing.Optional[builtins.str]:
            '''The Amazon Resource Name (ARN) of the client certificate used to securely connect to a Kafka target endpoint.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kafkasettings.html#cfn-dms-endpoint-kafkasettings-sslclientcertificatearn
            '''
            result = self._values.get("ssl_client_certificate_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def ssl_client_key_arn(self) -> typing.Optional[builtins.str]:
            '''The Amazon Resource Name (ARN) for the client private key used to securely connect to a Kafka target endpoint.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kafkasettings.html#cfn-dms-endpoint-kafkasettings-sslclientkeyarn
            '''
            result = self._values.get("ssl_client_key_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def ssl_client_key_password(self) -> typing.Optional[builtins.str]:
            '''The password for the client private key used to securely connect to a Kafka target endpoint.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kafkasettings.html#cfn-dms-endpoint-kafkasettings-sslclientkeypassword
            '''
            result = self._values.get("ssl_client_key_password")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def topic(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kafkasettings.html#cfn-dms-endpoint-kafkasettings-topic
            '''
            result = self._values.get("topic")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "KafkaSettingsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_dms.CfnEndpoint.KinesisSettingsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "include_control_details": "includeControlDetails",
            "include_null_and_empty": "includeNullAndEmpty",
            "include_table_alter_operations": "includeTableAlterOperations",
            "include_transaction_details": "includeTransactionDetails",
            "message_format": "messageFormat",
            "no_hex_prefix": "noHexPrefix",
            "partition_include_schema_table": "partitionIncludeSchemaTable",
            "service_access_role_arn": "serviceAccessRoleArn",
            "stream_arn": "streamArn",
        },
    )
    class KinesisSettingsProperty:
        def __init__(
            self,
            *,
            include_control_details: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            include_null_and_empty: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            include_table_alter_operations: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            include_transaction_details: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            message_format: typing.Optional[builtins.str] = None,
            no_hex_prefix: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            partition_include_schema_table: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            service_access_role_arn: typing.Optional[builtins.str] = None,
            stream_arn: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Not currently supported by AWS CloudFormation ..

            :param include_control_details: Shows detailed control information for table definition, column definition, and table and column changes in the Kinesis message output. The default is ``false`` .
            :param include_null_and_empty: Include NULL and empty columns for records migrated to the endpoint. The default is ``false`` .
            :param include_table_alter_operations: Includes any data definition language (DDL) operations that change the table in the control data, such as ``rename-table`` , ``drop-table`` , ``add-column`` , ``drop-column`` , and ``rename-column`` . The default is ``false`` .
            :param include_transaction_details: Provides detailed transaction information from the source database. This information includes a commit timestamp, a log position, and values for ``transaction_id`` , previous ``transaction_id`` , and ``transaction_record_id`` (the record offset within a transaction). The default is ``false`` .
            :param message_format: Not currently supported by AWS CloudFormation .
            :param no_hex_prefix: Set this optional parameter to ``true`` to avoid adding a '0x' prefix to raw data in hexadecimal format. For example, by default, AWS DMS adds a '0x' prefix to the LOB column type in hexadecimal format moving from an Oracle source to an Amazon Kinesis target. Use the ``NoHexPrefix`` endpoint setting to enable migration of RAW data type columns without adding the '0x' prefix.
            :param partition_include_schema_table: Prefixes schema and table names to partition values, when the partition type is ``primary-key-type`` . Doing this increases data distribution among Kinesis shards. For example, suppose that a SysBench schema has thousands of tables and each table has only limited range for a primary key. In this case, the same primary key is sent from thousands of tables to the same shard, which causes throttling. The default is ``false`` .
            :param service_access_role_arn: Not currently supported by AWS CloudFormation .
            :param stream_arn: Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kinesissettings.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_dms as dms
                
                kinesis_settings_property = dms.CfnEndpoint.KinesisSettingsProperty(
                    include_control_details=False,
                    include_null_and_empty=False,
                    include_table_alter_operations=False,
                    include_transaction_details=False,
                    message_format="messageFormat",
                    no_hex_prefix=False,
                    partition_include_schema_table=False,
                    service_access_role_arn="serviceAccessRoleArn",
                    stream_arn="streamArn"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if include_control_details is not None:
                self._values["include_control_details"] = include_control_details
            if include_null_and_empty is not None:
                self._values["include_null_and_empty"] = include_null_and_empty
            if include_table_alter_operations is not None:
                self._values["include_table_alter_operations"] = include_table_alter_operations
            if include_transaction_details is not None:
                self._values["include_transaction_details"] = include_transaction_details
            if message_format is not None:
                self._values["message_format"] = message_format
            if no_hex_prefix is not None:
                self._values["no_hex_prefix"] = no_hex_prefix
            if partition_include_schema_table is not None:
                self._values["partition_include_schema_table"] = partition_include_schema_table
            if service_access_role_arn is not None:
                self._values["service_access_role_arn"] = service_access_role_arn
            if stream_arn is not None:
                self._values["stream_arn"] = stream_arn

        @builtins.property
        def include_control_details(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''Shows detailed control information for table definition, column definition, and table and column changes in the Kinesis message output.

            The default is ``false`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kinesissettings.html#cfn-dms-endpoint-kinesissettings-includecontroldetails
            '''
            result = self._values.get("include_control_details")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def include_null_and_empty(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''Include NULL and empty columns for records migrated to the endpoint.

            The default is ``false`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kinesissettings.html#cfn-dms-endpoint-kinesissettings-includenullandempty
            '''
            result = self._values.get("include_null_and_empty")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def include_table_alter_operations(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''Includes any data definition language (DDL) operations that change the table in the control data, such as ``rename-table`` , ``drop-table`` , ``add-column`` , ``drop-column`` , and ``rename-column`` .

            The default is ``false`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kinesissettings.html#cfn-dms-endpoint-kinesissettings-includetablealteroperations
            '''
            result = self._values.get("include_table_alter_operations")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def include_transaction_details(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''Provides detailed transaction information from the source database.

            This information includes a commit timestamp, a log position, and values for ``transaction_id`` , previous ``transaction_id`` , and ``transaction_record_id`` (the record offset within a transaction). The default is ``false`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kinesissettings.html#cfn-dms-endpoint-kinesissettings-includetransactiondetails
            '''
            result = self._values.get("include_transaction_details")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def message_format(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kinesissettings.html#cfn-dms-endpoint-kinesissettings-messageformat
            '''
            result = self._values.get("message_format")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def no_hex_prefix(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''Set this optional parameter to ``true`` to avoid adding a '0x' prefix to raw data in hexadecimal format.

            For example, by default, AWS DMS adds a '0x' prefix to the LOB column type in hexadecimal format moving from an Oracle source to an Amazon Kinesis target. Use the ``NoHexPrefix`` endpoint setting to enable migration of RAW data type columns without adding the '0x' prefix.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kinesissettings.html#cfn-dms-endpoint-kinesissettings-nohexprefix
            '''
            result = self._values.get("no_hex_prefix")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def partition_include_schema_table(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''Prefixes schema and table names to partition values, when the partition type is ``primary-key-type`` .

            Doing this increases data distribution among Kinesis shards. For example, suppose that a SysBench schema has thousands of tables and each table has only limited range for a primary key. In this case, the same primary key is sent from thousands of tables to the same shard, which causes throttling. The default is ``false`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kinesissettings.html#cfn-dms-endpoint-kinesissettings-partitionincludeschematable
            '''
            result = self._values.get("partition_include_schema_table")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def service_access_role_arn(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kinesissettings.html#cfn-dms-endpoint-kinesissettings-serviceaccessrolearn
            '''
            result = self._values.get("service_access_role_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def stream_arn(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-kinesissettings.html#cfn-dms-endpoint-kinesissettings-streamarn
            '''
            result = self._values.get("stream_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "KinesisSettingsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_dms.CfnEndpoint.MicrosoftSqlServerSettingsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "secrets_manager_access_role_arn": "secretsManagerAccessRoleArn",
            "secrets_manager_secret_id": "secretsManagerSecretId",
        },
    )
    class MicrosoftSqlServerSettingsProperty:
        def __init__(
            self,
            *,
            secrets_manager_access_role_arn: typing.Optional[builtins.str] = None,
            secrets_manager_secret_id: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Not currently supported by AWS CloudFormation .

            :param secrets_manager_access_role_arn: Not currently supported by AWS CloudFormation .
            :param secrets_manager_secret_id: Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-microsoftsqlserversettings.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_dms as dms
                
                microsoft_sql_server_settings_property = dms.CfnEndpoint.MicrosoftSqlServerSettingsProperty(
                    secrets_manager_access_role_arn="secretsManagerAccessRoleArn",
                    secrets_manager_secret_id="secretsManagerSecretId"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if secrets_manager_access_role_arn is not None:
                self._values["secrets_manager_access_role_arn"] = secrets_manager_access_role_arn
            if secrets_manager_secret_id is not None:
                self._values["secrets_manager_secret_id"] = secrets_manager_secret_id

        @builtins.property
        def secrets_manager_access_role_arn(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-microsoftsqlserversettings.html#cfn-dms-endpoint-microsoftsqlserversettings-secretsmanageraccessrolearn
            '''
            result = self._values.get("secrets_manager_access_role_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def secrets_manager_secret_id(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-microsoftsqlserversettings.html#cfn-dms-endpoint-microsoftsqlserversettings-secretsmanagersecretid
            '''
            result = self._values.get("secrets_manager_secret_id")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "MicrosoftSqlServerSettingsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_dms.CfnEndpoint.MongoDbSettingsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "auth_mechanism": "authMechanism",
            "auth_source": "authSource",
            "auth_type": "authType",
            "database_name": "databaseName",
            "docs_to_investigate": "docsToInvestigate",
            "extract_doc_id": "extractDocId",
            "nesting_level": "nestingLevel",
            "password": "password",
            "port": "port",
            "secrets_manager_access_role_arn": "secretsManagerAccessRoleArn",
            "secrets_manager_secret_id": "secretsManagerSecretId",
            "server_name": "serverName",
            "username": "username",
        },
    )
    class MongoDbSettingsProperty:
        def __init__(
            self,
            *,
            auth_mechanism: typing.Optional[builtins.str] = None,
            auth_source: typing.Optional[builtins.str] = None,
            auth_type: typing.Optional[builtins.str] = None,
            database_name: typing.Optional[builtins.str] = None,
            docs_to_investigate: typing.Optional[builtins.str] = None,
            extract_doc_id: typing.Optional[builtins.str] = None,
            nesting_level: typing.Optional[builtins.str] = None,
            password: typing.Optional[builtins.str] = None,
            port: typing.Optional[jsii.Number] = None,
            secrets_manager_access_role_arn: typing.Optional[builtins.str] = None,
            secrets_manager_secret_id: typing.Optional[builtins.str] = None,
            server_name: typing.Optional[builtins.str] = None,
            username: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Not currently supported by AWS CloudFormation .

            :param auth_mechanism: Not currently supported by AWS CloudFormation .
            :param auth_source: Not currently supported by AWS CloudFormation .
            :param auth_type: Not currently supported by AWS CloudFormation .
            :param database_name: Not currently supported by AWS CloudFormation .
            :param docs_to_investigate: Not currently supported by AWS CloudFormation .
            :param extract_doc_id: Not currently supported by AWS CloudFormation .
            :param nesting_level: Not currently supported by AWS CloudFormation .
            :param password: Not currently supported by AWS CloudFormation .
            :param port: Not currently supported by AWS CloudFormation .
            :param secrets_manager_access_role_arn: Not currently supported by AWS CloudFormation .
            :param secrets_manager_secret_id: Not currently supported by AWS CloudFormation .
            :param server_name: Not currently supported by AWS CloudFormation .
            :param username: Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_dms as dms
                
                mongo_db_settings_property = dms.CfnEndpoint.MongoDbSettingsProperty(
                    auth_mechanism="authMechanism",
                    auth_source="authSource",
                    auth_type="authType",
                    database_name="databaseName",
                    docs_to_investigate="docsToInvestigate",
                    extract_doc_id="extractDocId",
                    nesting_level="nestingLevel",
                    password="password",
                    port=123,
                    secrets_manager_access_role_arn="secretsManagerAccessRoleArn",
                    secrets_manager_secret_id="secretsManagerSecretId",
                    server_name="serverName",
                    username="username"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if auth_mechanism is not None:
                self._values["auth_mechanism"] = auth_mechanism
            if auth_source is not None:
                self._values["auth_source"] = auth_source
            if auth_type is not None:
                self._values["auth_type"] = auth_type
            if database_name is not None:
                self._values["database_name"] = database_name
            if docs_to_investigate is not None:
                self._values["docs_to_investigate"] = docs_to_investigate
            if extract_doc_id is not None:
                self._values["extract_doc_id"] = extract_doc_id
            if nesting_level is not None:
                self._values["nesting_level"] = nesting_level
            if password is not None:
                self._values["password"] = password
            if port is not None:
                self._values["port"] = port
            if secrets_manager_access_role_arn is not None:
                self._values["secrets_manager_access_role_arn"] = secrets_manager_access_role_arn
            if secrets_manager_secret_id is not None:
                self._values["secrets_manager_secret_id"] = secrets_manager_secret_id
            if server_name is not None:
                self._values["server_name"] = server_name
            if username is not None:
                self._values["username"] = username

        @builtins.property
        def auth_mechanism(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-authmechanism
            '''
            result = self._values.get("auth_mechanism")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def auth_source(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-authsource
            '''
            result = self._values.get("auth_source")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def auth_type(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-authtype
            '''
            result = self._values.get("auth_type")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def database_name(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-databasename
            '''
            result = self._values.get("database_name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def docs_to_investigate(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-docstoinvestigate
            '''
            result = self._values.get("docs_to_investigate")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def extract_doc_id(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-extractdocid
            '''
            result = self._values.get("extract_doc_id")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def nesting_level(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-nestinglevel
            '''
            result = self._values.get("nesting_level")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def password(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-password
            '''
            result = self._values.get("password")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def port(self) -> typing.Optional[jsii.Number]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-port
            '''
            result = self._values.get("port")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def secrets_manager_access_role_arn(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-secretsmanageraccessrolearn
            '''
            result = self._values.get("secrets_manager_access_role_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def secrets_manager_secret_id(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-secretsmanagersecretid
            '''
            result = self._values.get("secrets_manager_secret_id")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def server_name(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-servername
            '''
            result = self._values.get("server_name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def username(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mongodbsettings.html#cfn-dms-endpoint-mongodbsettings-username
            '''
            result = self._values.get("username")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "MongoDbSettingsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_dms.CfnEndpoint.MySqlSettingsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "secrets_manager_access_role_arn": "secretsManagerAccessRoleArn",
            "secrets_manager_secret_id": "secretsManagerSecretId",
        },
    )
    class MySqlSettingsProperty:
        def __init__(
            self,
            *,
            secrets_manager_access_role_arn: typing.Optional[builtins.str] = None,
            secrets_manager_secret_id: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Not currently supported by AWS CloudFormation .

            :param secrets_manager_access_role_arn: Not currently supported by AWS CloudFormation .
            :param secrets_manager_secret_id: Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mysqlsettings.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_dms as dms
                
                my_sql_settings_property = dms.CfnEndpoint.MySqlSettingsProperty(
                    secrets_manager_access_role_arn="secretsManagerAccessRoleArn",
                    secrets_manager_secret_id="secretsManagerSecretId"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if secrets_manager_access_role_arn is not None:
                self._values["secrets_manager_access_role_arn"] = secrets_manager_access_role_arn
            if secrets_manager_secret_id is not None:
                self._values["secrets_manager_secret_id"] = secrets_manager_secret_id

        @builtins.property
        def secrets_manager_access_role_arn(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mysqlsettings.html#cfn-dms-endpoint-mysqlsettings-secretsmanageraccessrolearn
            '''
            result = self._values.get("secrets_manager_access_role_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def secrets_manager_secret_id(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-mysqlsettings.html#cfn-dms-endpoint-mysqlsettings-secretsmanagersecretid
            '''
            result = self._values.get("secrets_manager_secret_id")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "MySqlSettingsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_dms.CfnEndpoint.NeptuneSettingsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "error_retry_duration": "errorRetryDuration",
            "iam_auth_enabled": "iamAuthEnabled",
            "max_file_size": "maxFileSize",
            "max_retry_count": "maxRetryCount",
            "s3_bucket_folder": "s3BucketFolder",
            "s3_bucket_name": "s3BucketName",
            "service_access_role_arn": "serviceAccessRoleArn",
        },
    )
    class NeptuneSettingsProperty:
        def __init__(
            self,
            *,
            error_retry_duration: typing.Optional[jsii.Number] = None,
            iam_auth_enabled: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            max_file_size: typing.Optional[jsii.Number] = None,
            max_retry_count: typing.Optional[jsii.Number] = None,
            s3_bucket_folder: typing.Optional[builtins.str] = None,
            s3_bucket_name: typing.Optional[builtins.str] = None,
            service_access_role_arn: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Provides information that defines an Amazon Neptune endpoint.

            :param error_retry_duration: The number of milliseconds for AWS DMS to wait to retry a bulk-load of migrated graph data to the Neptune target database before raising an error. The default is 250.
            :param iam_auth_enabled: If you want AWS Identity and Access Management (IAM) authorization enabled for this endpoint, set this parameter to ``true`` . Then attach the appropriate IAM policy document to your service role specified by ``ServiceAccessRoleArn`` . The default is ``false`` .
            :param max_file_size: The maximum size in kilobytes of migrated graph data stored in a .csv file before AWS DMS bulk-loads the data to the Neptune target database. The default is 1,048,576 KB. If the bulk load is successful, AWS DMS clears the bucket, ready to store the next batch of migrated graph data.
            :param max_retry_count: The number of times for AWS DMS to retry a bulk load of migrated graph data to the Neptune target database before raising an error. The default is 5.
            :param s3_bucket_folder: A folder path where you want AWS DMS to store migrated graph data in the S3 bucket specified by ``S3BucketName``.
            :param s3_bucket_name: The name of the Amazon S3 bucket where AWS DMS can temporarily store migrated graph data in .csv files before bulk-loading it to the Neptune target database. AWS DMS maps the SQL source data to graph data before storing it in these .csv files.
            :param service_access_role_arn: The Amazon Resource Name (ARN) of the service role that you created for the Neptune target endpoint. The role must allow the ``iam:PassRole`` action. For more information, see `Creating an IAM Service Role for Accessing Amazon Neptune as a Target <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.Neptune.html#CHAP_Target.Neptune.ServiceRole>`_ in the *AWS Database Migration Service User Guide.*

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-neptunesettings.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_dms as dms
                
                neptune_settings_property = dms.CfnEndpoint.NeptuneSettingsProperty(
                    error_retry_duration=123,
                    iam_auth_enabled=False,
                    max_file_size=123,
                    max_retry_count=123,
                    s3_bucket_folder="s3BucketFolder",
                    s3_bucket_name="s3BucketName",
                    service_access_role_arn="serviceAccessRoleArn"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if error_retry_duration is not None:
                self._values["error_retry_duration"] = error_retry_duration
            if iam_auth_enabled is not None:
                self._values["iam_auth_enabled"] = iam_auth_enabled
            if max_file_size is not None:
                self._values["max_file_size"] = max_file_size
            if max_retry_count is not None:
                self._values["max_retry_count"] = max_retry_count
            if s3_bucket_folder is not None:
                self._values["s3_bucket_folder"] = s3_bucket_folder
            if s3_bucket_name is not None:
                self._values["s3_bucket_name"] = s3_bucket_name
            if service_access_role_arn is not None:
                self._values["service_access_role_arn"] = service_access_role_arn

        @builtins.property
        def error_retry_duration(self) -> typing.Optional[jsii.Number]:
            '''The number of milliseconds for AWS DMS to wait to retry a bulk-load of migrated graph data to the Neptune target database before raising an error.

            The default is 250.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-neptunesettings.html#cfn-dms-endpoint-neptunesettings-errorretryduration
            '''
            result = self._values.get("error_retry_duration")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def iam_auth_enabled(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''If you want AWS Identity and Access Management (IAM) authorization enabled for this endpoint, set this parameter to ``true`` .

            Then attach the appropriate IAM policy document to your service role specified by ``ServiceAccessRoleArn`` . The default is ``false`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-neptunesettings.html#cfn-dms-endpoint-neptunesettings-iamauthenabled
            '''
            result = self._values.get("iam_auth_enabled")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def max_file_size(self) -> typing.Optional[jsii.Number]:
            '''The maximum size in kilobytes of migrated graph data stored in a .csv file before AWS DMS bulk-loads the data to the Neptune target database. The default is 1,048,576 KB. If the bulk load is successful, AWS DMS clears the bucket, ready to store the next batch of migrated graph data.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-neptunesettings.html#cfn-dms-endpoint-neptunesettings-maxfilesize
            '''
            result = self._values.get("max_file_size")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def max_retry_count(self) -> typing.Optional[jsii.Number]:
            '''The number of times for AWS DMS to retry a bulk load of migrated graph data to the Neptune target database before raising an error.

            The default is 5.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-neptunesettings.html#cfn-dms-endpoint-neptunesettings-maxretrycount
            '''
            result = self._values.get("max_retry_count")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def s3_bucket_folder(self) -> typing.Optional[builtins.str]:
            '''A folder path where you want AWS DMS to store migrated graph data in the S3 bucket specified by ``S3BucketName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-neptunesettings.html#cfn-dms-endpoint-neptunesettings-s3bucketfolder
            '''
            result = self._values.get("s3_bucket_folder")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def s3_bucket_name(self) -> typing.Optional[builtins.str]:
            '''The name of the Amazon S3 bucket where AWS DMS can temporarily store migrated graph data in .csv files before bulk-loading it to the Neptune target database. AWS DMS maps the SQL source data to graph data before storing it in these .csv files.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-neptunesettings.html#cfn-dms-endpoint-neptunesettings-s3bucketname
            '''
            result = self._values.get("s3_bucket_name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def service_access_role_arn(self) -> typing.Optional[builtins.str]:
            '''The Amazon Resource Name (ARN) of the service role that you created for the Neptune target endpoint.

            The role must allow the ``iam:PassRole`` action. For more information, see `Creating an IAM Service Role for Accessing Amazon Neptune as a Target <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.Neptune.html#CHAP_Target.Neptune.ServiceRole>`_ in the *AWS Database Migration Service User Guide.*

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-neptunesettings.html#cfn-dms-endpoint-neptunesettings-serviceaccessrolearn
            '''
            result = self._values.get("service_access_role_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "NeptuneSettingsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_dms.CfnEndpoint.OracleSettingsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "secrets_manager_access_role_arn": "secretsManagerAccessRoleArn",
            "secrets_manager_oracle_asm_access_role_arn": "secretsManagerOracleAsmAccessRoleArn",
            "secrets_manager_oracle_asm_secret_id": "secretsManagerOracleAsmSecretId",
            "secrets_manager_secret_id": "secretsManagerSecretId",
        },
    )
    class OracleSettingsProperty:
        def __init__(
            self,
            *,
            secrets_manager_access_role_arn: typing.Optional[builtins.str] = None,
            secrets_manager_oracle_asm_access_role_arn: typing.Optional[builtins.str] = None,
            secrets_manager_oracle_asm_secret_id: typing.Optional[builtins.str] = None,
            secrets_manager_secret_id: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Not currently supported by AWS CloudFormation .

            :param secrets_manager_access_role_arn: Not currently supported by AWS CloudFormation .
            :param secrets_manager_oracle_asm_access_role_arn: Not currently supported by AWS CloudFormation .
            :param secrets_manager_oracle_asm_secret_id: Not currently supported by AWS CloudFormation .
            :param secrets_manager_secret_id: Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-oraclesettings.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_dms as dms
                
                oracle_settings_property = dms.CfnEndpoint.OracleSettingsProperty(
                    secrets_manager_access_role_arn="secretsManagerAccessRoleArn",
                    secrets_manager_oracle_asm_access_role_arn="secretsManagerOracleAsmAccessRoleArn",
                    secrets_manager_oracle_asm_secret_id="secretsManagerOracleAsmSecretId",
                    secrets_manager_secret_id="secretsManagerSecretId"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if secrets_manager_access_role_arn is not None:
                self._values["secrets_manager_access_role_arn"] = secrets_manager_access_role_arn
            if secrets_manager_oracle_asm_access_role_arn is not None:
                self._values["secrets_manager_oracle_asm_access_role_arn"] = secrets_manager_oracle_asm_access_role_arn
            if secrets_manager_oracle_asm_secret_id is not None:
                self._values["secrets_manager_oracle_asm_secret_id"] = secrets_manager_oracle_asm_secret_id
            if secrets_manager_secret_id is not None:
                self._values["secrets_manager_secret_id"] = secrets_manager_secret_id

        @builtins.property
        def secrets_manager_access_role_arn(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-oraclesettings.html#cfn-dms-endpoint-oraclesettings-secretsmanageraccessrolearn
            '''
            result = self._values.get("secrets_manager_access_role_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def secrets_manager_oracle_asm_access_role_arn(
            self,
        ) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-oraclesettings.html#cfn-dms-endpoint-oraclesettings-secretsmanageroracleasmaccessrolearn
            '''
            result = self._values.get("secrets_manager_oracle_asm_access_role_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def secrets_manager_oracle_asm_secret_id(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-oraclesettings.html#cfn-dms-endpoint-oraclesettings-secretsmanageroracleasmsecretid
            '''
            result = self._values.get("secrets_manager_oracle_asm_secret_id")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def secrets_manager_secret_id(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-oraclesettings.html#cfn-dms-endpoint-oraclesettings-secretsmanagersecretid
            '''
            result = self._values.get("secrets_manager_secret_id")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "OracleSettingsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_dms.CfnEndpoint.PostgreSqlSettingsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "secrets_manager_access_role_arn": "secretsManagerAccessRoleArn",
            "secrets_manager_secret_id": "secretsManagerSecretId",
        },
    )
    class PostgreSqlSettingsProperty:
        def __init__(
            self,
            *,
            secrets_manager_access_role_arn: typing.Optional[builtins.str] = None,
            secrets_manager_secret_id: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Not currently supported by AWS CloudFormation .

            :param secrets_manager_access_role_arn: Not currently supported by AWS CloudFormation .
            :param secrets_manager_secret_id: Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-postgresqlsettings.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_dms as dms
                
                postgre_sql_settings_property = dms.CfnEndpoint.PostgreSqlSettingsProperty(
                    secrets_manager_access_role_arn="secretsManagerAccessRoleArn",
                    secrets_manager_secret_id="secretsManagerSecretId"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if secrets_manager_access_role_arn is not None:
                self._values["secrets_manager_access_role_arn"] = secrets_manager_access_role_arn
            if secrets_manager_secret_id is not None:
                self._values["secrets_manager_secret_id"] = secrets_manager_secret_id

        @builtins.property
        def secrets_manager_access_role_arn(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-postgresqlsettings.html#cfn-dms-endpoint-postgresqlsettings-secretsmanageraccessrolearn
            '''
            result = self._values.get("secrets_manager_access_role_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def secrets_manager_secret_id(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-postgresqlsettings.html#cfn-dms-endpoint-postgresqlsettings-secretsmanagersecretid
            '''
            result = self._values.get("secrets_manager_secret_id")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "PostgreSqlSettingsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_dms.CfnEndpoint.RedisSettingsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "auth_password": "authPassword",
            "auth_type": "authType",
            "auth_user_name": "authUserName",
            "port": "port",
            "server_name": "serverName",
            "ssl_ca_certificate_arn": "sslCaCertificateArn",
            "ssl_security_protocol": "sslSecurityProtocol",
        },
    )
    class RedisSettingsProperty:
        def __init__(
            self,
            *,
            auth_password: typing.Optional[builtins.str] = None,
            auth_type: typing.Optional[builtins.str] = None,
            auth_user_name: typing.Optional[builtins.str] = None,
            port: typing.Optional[jsii.Number] = None,
            server_name: typing.Optional[builtins.str] = None,
            ssl_ca_certificate_arn: typing.Optional[builtins.str] = None,
            ssl_security_protocol: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Provides information that defines a Redis target endpoint.

            :param auth_password: The password provided with the ``auth-role`` and ``auth-token`` options of the ``AuthType`` setting for a Redis target endpoint.
            :param auth_type: The type of authentication to perform when connecting to a Redis target. Options include ``none`` , ``auth-token`` , and ``auth-role`` . The ``auth-token`` option requires an ``AuthPassword`` value to be provided. The ``auth-role`` option requires ``AuthUserName`` and ``AuthPassword`` values to be provided.
            :param auth_user_name: The user name provided with the ``auth-role`` option of the ``AuthType`` setting for a Redis target endpoint.
            :param port: Transmission Control Protocol (TCP) port for the endpoint.
            :param server_name: Fully qualified domain name of the endpoint.
            :param ssl_ca_certificate_arn: The Amazon Resource Name (ARN) for the certificate authority (CA) that DMS uses to connect to your Redis target endpoint.
            :param ssl_security_protocol: The connection to a Redis target endpoint using Transport Layer Security (TLS). Valid values include ``plaintext`` and ``ssl-encryption`` . The default is ``ssl-encryption`` . The ``ssl-encryption`` option makes an encrypted connection. Optionally, you can identify an Amazon Resource Name (ARN) for an SSL certificate authority (CA) using the ``SslCaCertificateArn`` setting. If an ARN isn't given for a CA, DMS uses the Amazon root CA. The ``plaintext`` option doesn't provide Transport Layer Security (TLS) encryption for traffic between endpoint and database.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-redissettings.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_dms as dms
                
                redis_settings_property = dms.CfnEndpoint.RedisSettingsProperty(
                    auth_password="authPassword",
                    auth_type="authType",
                    auth_user_name="authUserName",
                    port=123,
                    server_name="serverName",
                    ssl_ca_certificate_arn="sslCaCertificateArn",
                    ssl_security_protocol="sslSecurityProtocol"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if auth_password is not None:
                self._values["auth_password"] = auth_password
            if auth_type is not None:
                self._values["auth_type"] = auth_type
            if auth_user_name is not None:
                self._values["auth_user_name"] = auth_user_name
            if port is not None:
                self._values["port"] = port
            if server_name is not None:
                self._values["server_name"] = server_name
            if ssl_ca_certificate_arn is not None:
                self._values["ssl_ca_certificate_arn"] = ssl_ca_certificate_arn
            if ssl_security_protocol is not None:
                self._values["ssl_security_protocol"] = ssl_security_protocol

        @builtins.property
        def auth_password(self) -> typing.Optional[builtins.str]:
            '''The password provided with the ``auth-role`` and ``auth-token`` options of the ``AuthType`` setting for a Redis target endpoint.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-redissettings.html#cfn-dms-endpoint-redissettings-authpassword
            '''
            result = self._values.get("auth_password")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def auth_type(self) -> typing.Optional[builtins.str]:
            '''The type of authentication to perform when connecting to a Redis target.

            Options include ``none`` , ``auth-token`` , and ``auth-role`` . The ``auth-token`` option requires an ``AuthPassword`` value to be provided. The ``auth-role`` option requires ``AuthUserName`` and ``AuthPassword`` values to be provided.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-redissettings.html#cfn-dms-endpoint-redissettings-authtype
            '''
            result = self._values.get("auth_type")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def auth_user_name(self) -> typing.Optional[builtins.str]:
            '''The user name provided with the ``auth-role`` option of the ``AuthType`` setting for a Redis target endpoint.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-redissettings.html#cfn-dms-endpoint-redissettings-authusername
            '''
            result = self._values.get("auth_user_name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def port(self) -> typing.Optional[jsii.Number]:
            '''Transmission Control Protocol (TCP) port for the endpoint.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-redissettings.html#cfn-dms-endpoint-redissettings-port
            '''
            result = self._values.get("port")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def server_name(self) -> typing.Optional[builtins.str]:
            '''Fully qualified domain name of the endpoint.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-redissettings.html#cfn-dms-endpoint-redissettings-servername
            '''
            result = self._values.get("server_name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def ssl_ca_certificate_arn(self) -> typing.Optional[builtins.str]:
            '''The Amazon Resource Name (ARN) for the certificate authority (CA) that DMS uses to connect to your Redis target endpoint.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-redissettings.html#cfn-dms-endpoint-redissettings-sslcacertificatearn
            '''
            result = self._values.get("ssl_ca_certificate_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def ssl_security_protocol(self) -> typing.Optional[builtins.str]:
            '''The connection to a Redis target endpoint using Transport Layer Security (TLS).

            Valid values include ``plaintext`` and ``ssl-encryption`` . The default is ``ssl-encryption`` . The ``ssl-encryption`` option makes an encrypted connection. Optionally, you can identify an Amazon Resource Name (ARN) for an SSL certificate authority (CA) using the ``SslCaCertificateArn`` setting. If an ARN isn't given for a CA, DMS uses the Amazon root CA.

            The ``plaintext`` option doesn't provide Transport Layer Security (TLS) encryption for traffic between endpoint and database.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-redissettings.html#cfn-dms-endpoint-redissettings-sslsecurityprotocol
            '''
            result = self._values.get("ssl_security_protocol")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "RedisSettingsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_dms.CfnEndpoint.RedshiftSettingsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "secrets_manager_access_role_arn": "secretsManagerAccessRoleArn",
            "secrets_manager_secret_id": "secretsManagerSecretId",
        },
    )
    class RedshiftSettingsProperty:
        def __init__(
            self,
            *,
            secrets_manager_access_role_arn: typing.Optional[builtins.str] = None,
            secrets_manager_secret_id: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Not currently supported by AWS CloudFormation .

            :param secrets_manager_access_role_arn: Not currently supported by AWS CloudFormation .
            :param secrets_manager_secret_id: Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-redshiftsettings.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_dms as dms
                
                redshift_settings_property = dms.CfnEndpoint.RedshiftSettingsProperty(
                    secrets_manager_access_role_arn="secretsManagerAccessRoleArn",
                    secrets_manager_secret_id="secretsManagerSecretId"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if secrets_manager_access_role_arn is not None:
                self._values["secrets_manager_access_role_arn"] = secrets_manager_access_role_arn
            if secrets_manager_secret_id is not None:
                self._values["secrets_manager_secret_id"] = secrets_manager_secret_id

        @builtins.property
        def secrets_manager_access_role_arn(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-redshiftsettings.html#cfn-dms-endpoint-redshiftsettings-secretsmanageraccessrolearn
            '''
            result = self._values.get("secrets_manager_access_role_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def secrets_manager_secret_id(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-redshiftsettings.html#cfn-dms-endpoint-redshiftsettings-secretsmanagersecretid
            '''
            result = self._values.get("secrets_manager_secret_id")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "RedshiftSettingsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_dms.CfnEndpoint.S3SettingsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "bucket_folder": "bucketFolder",
            "bucket_name": "bucketName",
            "compression_type": "compressionType",
            "csv_delimiter": "csvDelimiter",
            "csv_row_delimiter": "csvRowDelimiter",
            "external_table_definition": "externalTableDefinition",
            "service_access_role_arn": "serviceAccessRoleArn",
        },
    )
    class S3SettingsProperty:
        def __init__(
            self,
            *,
            bucket_folder: typing.Optional[builtins.str] = None,
            bucket_name: typing.Optional[builtins.str] = None,
            compression_type: typing.Optional[builtins.str] = None,
            csv_delimiter: typing.Optional[builtins.str] = None,
            csv_row_delimiter: typing.Optional[builtins.str] = None,
            external_table_definition: typing.Optional[builtins.str] = None,
            service_access_role_arn: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Not currently supported by AWS CloudFormation .

            :param bucket_folder: Not currently supported by AWS CloudFormation .
            :param bucket_name: Not currently supported by AWS CloudFormation .
            :param compression_type: Not currently supported by AWS CloudFormation .
            :param csv_delimiter: Not currently supported by AWS CloudFormation .
            :param csv_row_delimiter: Not currently supported by AWS CloudFormation .
            :param external_table_definition: Not currently supported by AWS CloudFormation .
            :param service_access_role_arn: Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-s3settings.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_dms as dms
                
                s3_settings_property = dms.CfnEndpoint.S3SettingsProperty(
                    bucket_folder="bucketFolder",
                    bucket_name="bucketName",
                    compression_type="compressionType",
                    csv_delimiter="csvDelimiter",
                    csv_row_delimiter="csvRowDelimiter",
                    external_table_definition="externalTableDefinition",
                    service_access_role_arn="serviceAccessRoleArn"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if bucket_folder is not None:
                self._values["bucket_folder"] = bucket_folder
            if bucket_name is not None:
                self._values["bucket_name"] = bucket_name
            if compression_type is not None:
                self._values["compression_type"] = compression_type
            if csv_delimiter is not None:
                self._values["csv_delimiter"] = csv_delimiter
            if csv_row_delimiter is not None:
                self._values["csv_row_delimiter"] = csv_row_delimiter
            if external_table_definition is not None:
                self._values["external_table_definition"] = external_table_definition
            if service_access_role_arn is not None:
                self._values["service_access_role_arn"] = service_access_role_arn

        @builtins.property
        def bucket_folder(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-s3settings.html#cfn-dms-endpoint-s3settings-bucketfolder
            '''
            result = self._values.get("bucket_folder")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def bucket_name(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-s3settings.html#cfn-dms-endpoint-s3settings-bucketname
            '''
            result = self._values.get("bucket_name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def compression_type(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-s3settings.html#cfn-dms-endpoint-s3settings-compressiontype
            '''
            result = self._values.get("compression_type")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def csv_delimiter(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-s3settings.html#cfn-dms-endpoint-s3settings-csvdelimiter
            '''
            result = self._values.get("csv_delimiter")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def csv_row_delimiter(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-s3settings.html#cfn-dms-endpoint-s3settings-csvrowdelimiter
            '''
            result = self._values.get("csv_row_delimiter")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def external_table_definition(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-s3settings.html#cfn-dms-endpoint-s3settings-externaltabledefinition
            '''
            result = self._values.get("external_table_definition")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def service_access_role_arn(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-s3settings.html#cfn-dms-endpoint-s3settings-serviceaccessrolearn
            '''
            result = self._values.get("service_access_role_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "S3SettingsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_dms.CfnEndpoint.SybaseSettingsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "secrets_manager_access_role_arn": "secretsManagerAccessRoleArn",
            "secrets_manager_secret_id": "secretsManagerSecretId",
        },
    )
    class SybaseSettingsProperty:
        def __init__(
            self,
            *,
            secrets_manager_access_role_arn: typing.Optional[builtins.str] = None,
            secrets_manager_secret_id: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Not currently supported by AWS CloudFormation .

            :param secrets_manager_access_role_arn: Not currently supported by AWS CloudFormation .
            :param secrets_manager_secret_id: Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-sybasesettings.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_dms as dms
                
                sybase_settings_property = dms.CfnEndpoint.SybaseSettingsProperty(
                    secrets_manager_access_role_arn="secretsManagerAccessRoleArn",
                    secrets_manager_secret_id="secretsManagerSecretId"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if secrets_manager_access_role_arn is not None:
                self._values["secrets_manager_access_role_arn"] = secrets_manager_access_role_arn
            if secrets_manager_secret_id is not None:
                self._values["secrets_manager_secret_id"] = secrets_manager_secret_id

        @builtins.property
        def secrets_manager_access_role_arn(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-sybasesettings.html#cfn-dms-endpoint-sybasesettings-secretsmanageraccessrolearn
            '''
            result = self._values.get("secrets_manager_access_role_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def secrets_manager_secret_id(self) -> typing.Optional[builtins.str]:
            '''Not currently supported by AWS CloudFormation .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-dms-endpoint-sybasesettings.html#cfn-dms-endpoint-sybasesettings-secretsmanagersecretid
            '''
            result = self._values.get("secrets_manager_secret_id")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SybaseSettingsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_dms.CfnEndpointProps",
    jsii_struct_bases=[],
    name_mapping={
        "endpoint_type": "endpointType",
        "engine_name": "engineName",
        "certificate_arn": "certificateArn",
        "database_name": "databaseName",
        "doc_db_settings": "docDbSettings",
        "dynamo_db_settings": "dynamoDbSettings",
        "elasticsearch_settings": "elasticsearchSettings",
        "endpoint_identifier": "endpointIdentifier",
        "extra_connection_attributes": "extraConnectionAttributes",
        "ibm_db2_settings": "ibmDb2Settings",
        "kafka_settings": "kafkaSettings",
        "kinesis_settings": "kinesisSettings",
        "kms_key_id": "kmsKeyId",
        "microsoft_sql_server_settings": "microsoftSqlServerSettings",
        "mongo_db_settings": "mongoDbSettings",
        "my_sql_settings": "mySqlSettings",
        "neptune_settings": "neptuneSettings",
        "oracle_settings": "oracleSettings",
        "password": "password",
        "port": "port",
        "postgre_sql_settings": "postgreSqlSettings",
        "redis_settings": "redisSettings",
        "redshift_settings": "redshiftSettings",
        "resource_identifier": "resourceIdentifier",
        "s3_settings": "s3Settings",
        "server_name": "serverName",
        "ssl_mode": "sslMode",
        "sybase_settings": "sybaseSettings",
        "tags": "tags",
        "username": "username",
    },
)
class CfnEndpointProps:
    def __init__(
        self,
        *,
        endpoint_type: builtins.str,
        engine_name: builtins.str,
        certificate_arn: typing.Optional[builtins.str] = None,
        database_name: typing.Optional[builtins.str] = None,
        doc_db_settings: typing.Optional[typing.Union[CfnEndpoint.DocDbSettingsProperty, _IResolvable_da3f097b]] = None,
        dynamo_db_settings: typing.Optional[typing.Union[CfnEndpoint.DynamoDbSettingsProperty, _IResolvable_da3f097b]] = None,
        elasticsearch_settings: typing.Optional[typing.Union[CfnEndpoint.ElasticsearchSettingsProperty, _IResolvable_da3f097b]] = None,
        endpoint_identifier: typing.Optional[builtins.str] = None,
        extra_connection_attributes: typing.Optional[builtins.str] = None,
        ibm_db2_settings: typing.Optional[typing.Union[CfnEndpoint.IbmDb2SettingsProperty, _IResolvable_da3f097b]] = None,
        kafka_settings: typing.Optional[typing.Union[CfnEndpoint.KafkaSettingsProperty, _IResolvable_da3f097b]] = None,
        kinesis_settings: typing.Optional[typing.Union[CfnEndpoint.KinesisSettingsProperty, _IResolvable_da3f097b]] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        microsoft_sql_server_settings: typing.Optional[typing.Union[CfnEndpoint.MicrosoftSqlServerSettingsProperty, _IResolvable_da3f097b]] = None,
        mongo_db_settings: typing.Optional[typing.Union[CfnEndpoint.MongoDbSettingsProperty, _IResolvable_da3f097b]] = None,
        my_sql_settings: typing.Optional[typing.Union[CfnEndpoint.MySqlSettingsProperty, _IResolvable_da3f097b]] = None,
        neptune_settings: typing.Optional[typing.Union[CfnEndpoint.NeptuneSettingsProperty, _IResolvable_da3f097b]] = None,
        oracle_settings: typing.Optional[typing.Union[CfnEndpoint.OracleSettingsProperty, _IResolvable_da3f097b]] = None,
        password: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        postgre_sql_settings: typing.Optional[typing.Union[CfnEndpoint.PostgreSqlSettingsProperty, _IResolvable_da3f097b]] = None,
        redis_settings: typing.Optional[typing.Union[CfnEndpoint.RedisSettingsProperty, _IResolvable_da3f097b]] = None,
        redshift_settings: typing.Optional[typing.Union[CfnEndpoint.RedshiftSettingsProperty, _IResolvable_da3f097b]] = None,
        resource_identifier: typing.Optional[builtins.str] = None,
        s3_settings: typing.Optional[typing.Union[CfnEndpoint.S3SettingsProperty, _IResolvable_da3f097b]] = None,
        server_name: typing.Optional[builtins.str] = None,
        ssl_mode: typing.Optional[builtins.str] = None,
        sybase_settings: typing.Optional[typing.Union[CfnEndpoint.SybaseSettingsProperty, _IResolvable_da3f097b]] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a ``CfnEndpoint``.

        :param endpoint_type: The type of endpoint. Valid values are ``source`` and ``target`` .
        :param engine_name: The type of engine for the endpoint. Valid values, depending on the ``EndpointType`` value, include ``"mysql"`` , ``"oracle"`` , ``"postgres"`` , ``"mariadb"`` , ``"aurora"`` , ``"aurora-postgresql"`` , ``"opensearch"`` , ``"redshift"`` , ``"s3"`` , ``"db2"`` , ``"azuredb"`` , ``"sybase"`` , ``"dynamodb"`` , ``"mongodb"`` , ``"kinesis"`` , ``"kafka"`` , ``"elasticsearch"`` , ``"docdb"`` , ``"sqlserver"`` , and ``"neptune"`` .
        :param certificate_arn: The Amazon Resource Name (ARN) for the certificate.
        :param database_name: The name of the endpoint database. For a MySQL source or target endpoint, do not specify DatabaseName. To migrate to a specific database, use this setting and ``targetDbType`` .
        :param doc_db_settings: Settings in JSON format for the source DocumentDB endpoint. For more information about the available settings, see the configuration properties section in `Using DocumentDB as a Target for AWS Database Migration Service <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Source.DocumentDB.html>`_ in the *AWS Database Migration Service User Guide.*
        :param dynamo_db_settings: Settings in JSON format for the target Amazon DynamoDB endpoint. For information about other available settings, see `Using Object Mapping to Migrate Data to DynamoDB <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.DynamoDB.html#CHAP_Target.DynamoDB.ObjectMapping>`_ in the *AWS Database Migration Service User Guide.*
        :param elasticsearch_settings: Settings in JSON format for the target OpenSearch endpoint. For more information about the available settings, see `Extra Connection Attributes When Using OpenSearch as a Target for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.Elasticsearch.html#CHAP_Target.Elasticsearch.Configuration>`_ in the *AWS Database Migration Service User Guide* .
        :param endpoint_identifier: The database endpoint identifier. Identifiers must begin with a letter and must contain only ASCII letters, digits, and hyphens. They can't end with a hyphen, or contain two consecutive hyphens.
        :param extra_connection_attributes: Additional attributes associated with the connection. Each attribute is specified as a name-value pair associated by an equal sign (=). Multiple attributes are separated by a semicolon (;) with no additional white space. For information on the attributes available for connecting your source or target endpoint, see `Working with AWS DMS Endpoints <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Endpoints.html>`_ in the *AWS Database Migration Service User Guide.*
        :param ibm_db2_settings: Not currently supported by AWS CloudFormation .
        :param kafka_settings: Settings in JSON format for the target Apache Kafka endpoint. For more information about the available settings, see `Using object mapping to migrate data to a Kafka topic <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.Kafka.html#CHAP_Target.Kafka.ObjectMapping>`_ in the *AWS Database Migration Service User Guide.*
        :param kinesis_settings: Settings in JSON format for the target endpoint for Amazon Kinesis Data Streams. For more information about the available settings, see `Using Amazon Kinesis Data Streams as a Target for AWS Database Migration Service <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.Kinesis.html>`_ in the *AWS Database Migration Service User Guide.*
        :param kms_key_id: An AWS KMS key identifier that is used to encrypt the connection parameters for the endpoint. If you don't specify a value for the ``KmsKeyId`` parameter, then AWS DMS uses your default encryption key. AWS KMS creates the default encryption key for your AWS account . Your AWS account has a different default encryption key for each AWS Region .
        :param microsoft_sql_server_settings: Not currently supported by AWS CloudFormation .
        :param mongo_db_settings: Not currently supported by AWS CloudFormation .
        :param my_sql_settings: Settings in JSON format for the source and target MySQL endpoint. For information about other available settings, see `Extra connection attributes when using MySQL as a source for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Source.MySQL.html#CHAP_Source.MySQL.ConnectionAttrib>`_ and `Extra connection attributes when using a MySQL-compatible database as a target for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.MySQL.html#CHAP_Target.MySQL.ConnectionAttrib>`_ in the *AWS Database Migration Service User Guide.*
        :param neptune_settings: ``AWS::DMS::Endpoint.NeptuneSettings``.
        :param oracle_settings: Settings in JSON format for the source and target Oracle endpoint. For information about other available settings, see `Extra connection attributes when using Oracle as a source for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Source.Oracle.html#CHAP_Source.Oracle.ConnectionAttrib>`_ and `Extra connection attributes when using Oracle as a target for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.Oracle.html#CHAP_Target.Oracle.ConnectionAttrib>`_ in the *AWS Database Migration Service User Guide.*
        :param password: The password to be used to log in to the endpoint database.
        :param port: The port used by the endpoint database.
        :param postgre_sql_settings: Not currently supported by AWS CloudFormation .
        :param redis_settings: Settings in JSON format for the target Redis endpoint.
        :param redshift_settings: Not currently supported by AWS CloudFormation .
        :param resource_identifier: A friendly name for the resource identifier at the end of the ``EndpointArn`` response parameter that is returned in the created ``Endpoint`` object. The value for this parameter can have up to 31 characters. It can contain only ASCII letters, digits, and hyphen ('-'). Also, it can't end with a hyphen or contain two consecutive hyphens, and can only begin with a letter, such as ``Example-App-ARN1`` . For example, this value might result in the ``EndpointArn`` value ``arn:aws:dms:eu-west-1:012345678901:rep:Example-App-ARN1`` . If you don't specify a ``ResourceIdentifier`` value, AWS DMS generates a default identifier value for the end of ``EndpointArn`` .
        :param s3_settings: Settings in JSON format for the target Amazon S3 endpoint. For more information about the available settings, see `Extra Connection Attributes When Using Amazon S3 as a Target for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.S3.html#CHAP_Target.S3.Configuring>`_ in the *AWS Database Migration Service User Guide.*
        :param server_name: The name of the server where the endpoint database resides.
        :param ssl_mode: The Secure Sockets Layer (SSL) mode to use for the SSL connection. The default is ``none`` . .. epigraph:: When ``engine_name`` is set to S3, then the only allowed value is ``none`` .
        :param sybase_settings: Settings in JSON format for the source and target SAP ASE endpoint. For information about other available settings, see `Extra connection attributes when using SAP ASE as a source for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Source.SAP.html#CHAP_Source.SAP.ConnectionAttrib>`_ and `Extra connection attributes when using SAP ASE as a target for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.SAP.html#CHAP_Target.SAP.ConnectionAttrib>`_ in the *AWS Database Migration Service User Guide.*
        :param tags: One or more tags to be assigned to the endpoint.
        :param username: The user name to be used to log in to the endpoint database.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_dms as dms
            
            cfn_endpoint_props = dms.CfnEndpointProps(
                endpoint_type="endpointType",
                engine_name="engineName",
            
                # the properties below are optional
                certificate_arn="certificateArn",
                database_name="databaseName",
                doc_db_settings=dms.CfnEndpoint.DocDbSettingsProperty(
                    secrets_manager_access_role_arn="secretsManagerAccessRoleArn",
                    secrets_manager_secret_id="secretsManagerSecretId"
                ),
                dynamo_db_settings=dms.CfnEndpoint.DynamoDbSettingsProperty(
                    service_access_role_arn="serviceAccessRoleArn"
                ),
                elasticsearch_settings=dms.CfnEndpoint.ElasticsearchSettingsProperty(
                    endpoint_uri="endpointUri",
                    error_retry_duration=123,
                    full_load_error_percentage=123,
                    service_access_role_arn="serviceAccessRoleArn"
                ),
                endpoint_identifier="endpointIdentifier",
                extra_connection_attributes="extraConnectionAttributes",
                ibm_db2_settings=dms.CfnEndpoint.IbmDb2SettingsProperty(
                    secrets_manager_access_role_arn="secretsManagerAccessRoleArn",
                    secrets_manager_secret_id="secretsManagerSecretId"
                ),
                kafka_settings=dms.CfnEndpoint.KafkaSettingsProperty(
                    broker="broker",
                    include_control_details=False,
                    include_null_and_empty=False,
                    include_table_alter_operations=False,
                    include_transaction_details=False,
                    no_hex_prefix=False,
                    partition_include_schema_table=False,
                    sasl_password="saslPassword",
                    sasl_user_name="saslUserName",
                    security_protocol="securityProtocol",
                    ssl_ca_certificate_arn="sslCaCertificateArn",
                    ssl_client_certificate_arn="sslClientCertificateArn",
                    ssl_client_key_arn="sslClientKeyArn",
                    ssl_client_key_password="sslClientKeyPassword",
                    topic="topic"
                ),
                kinesis_settings=dms.CfnEndpoint.KinesisSettingsProperty(
                    include_control_details=False,
                    include_null_and_empty=False,
                    include_table_alter_operations=False,
                    include_transaction_details=False,
                    message_format="messageFormat",
                    no_hex_prefix=False,
                    partition_include_schema_table=False,
                    service_access_role_arn="serviceAccessRoleArn",
                    stream_arn="streamArn"
                ),
                kms_key_id="kmsKeyId",
                microsoft_sql_server_settings=dms.CfnEndpoint.MicrosoftSqlServerSettingsProperty(
                    secrets_manager_access_role_arn="secretsManagerAccessRoleArn",
                    secrets_manager_secret_id="secretsManagerSecretId"
                ),
                mongo_db_settings=dms.CfnEndpoint.MongoDbSettingsProperty(
                    auth_mechanism="authMechanism",
                    auth_source="authSource",
                    auth_type="authType",
                    database_name="databaseName",
                    docs_to_investigate="docsToInvestigate",
                    extract_doc_id="extractDocId",
                    nesting_level="nestingLevel",
                    password="password",
                    port=123,
                    secrets_manager_access_role_arn="secretsManagerAccessRoleArn",
                    secrets_manager_secret_id="secretsManagerSecretId",
                    server_name="serverName",
                    username="username"
                ),
                my_sql_settings=dms.CfnEndpoint.MySqlSettingsProperty(
                    secrets_manager_access_role_arn="secretsManagerAccessRoleArn",
                    secrets_manager_secret_id="secretsManagerSecretId"
                ),
                neptune_settings=dms.CfnEndpoint.NeptuneSettingsProperty(
                    error_retry_duration=123,
                    iam_auth_enabled=False,
                    max_file_size=123,
                    max_retry_count=123,
                    s3_bucket_folder="s3BucketFolder",
                    s3_bucket_name="s3BucketName",
                    service_access_role_arn="serviceAccessRoleArn"
                ),
                oracle_settings=dms.CfnEndpoint.OracleSettingsProperty(
                    secrets_manager_access_role_arn="secretsManagerAccessRoleArn",
                    secrets_manager_oracle_asm_access_role_arn="secretsManagerOracleAsmAccessRoleArn",
                    secrets_manager_oracle_asm_secret_id="secretsManagerOracleAsmSecretId",
                    secrets_manager_secret_id="secretsManagerSecretId"
                ),
                password="password",
                port=123,
                postgre_sql_settings=dms.CfnEndpoint.PostgreSqlSettingsProperty(
                    secrets_manager_access_role_arn="secretsManagerAccessRoleArn",
                    secrets_manager_secret_id="secretsManagerSecretId"
                ),
                redis_settings=dms.CfnEndpoint.RedisSettingsProperty(
                    auth_password="authPassword",
                    auth_type="authType",
                    auth_user_name="authUserName",
                    port=123,
                    server_name="serverName",
                    ssl_ca_certificate_arn="sslCaCertificateArn",
                    ssl_security_protocol="sslSecurityProtocol"
                ),
                redshift_settings=dms.CfnEndpoint.RedshiftSettingsProperty(
                    secrets_manager_access_role_arn="secretsManagerAccessRoleArn",
                    secrets_manager_secret_id="secretsManagerSecretId"
                ),
                resource_identifier="resourceIdentifier",
                s3_settings=dms.CfnEndpoint.S3SettingsProperty(
                    bucket_folder="bucketFolder",
                    bucket_name="bucketName",
                    compression_type="compressionType",
                    csv_delimiter="csvDelimiter",
                    csv_row_delimiter="csvRowDelimiter",
                    external_table_definition="externalTableDefinition",
                    service_access_role_arn="serviceAccessRoleArn"
                ),
                server_name="serverName",
                ssl_mode="sslMode",
                sybase_settings=dms.CfnEndpoint.SybaseSettingsProperty(
                    secrets_manager_access_role_arn="secretsManagerAccessRoleArn",
                    secrets_manager_secret_id="secretsManagerSecretId"
                ),
                tags=[CfnTag(
                    key="key",
                    value="value"
                )],
                username="username"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "endpoint_type": endpoint_type,
            "engine_name": engine_name,
        }
        if certificate_arn is not None:
            self._values["certificate_arn"] = certificate_arn
        if database_name is not None:
            self._values["database_name"] = database_name
        if doc_db_settings is not None:
            self._values["doc_db_settings"] = doc_db_settings
        if dynamo_db_settings is not None:
            self._values["dynamo_db_settings"] = dynamo_db_settings
        if elasticsearch_settings is not None:
            self._values["elasticsearch_settings"] = elasticsearch_settings
        if endpoint_identifier is not None:
            self._values["endpoint_identifier"] = endpoint_identifier
        if extra_connection_attributes is not None:
            self._values["extra_connection_attributes"] = extra_connection_attributes
        if ibm_db2_settings is not None:
            self._values["ibm_db2_settings"] = ibm_db2_settings
        if kafka_settings is not None:
            self._values["kafka_settings"] = kafka_settings
        if kinesis_settings is not None:
            self._values["kinesis_settings"] = kinesis_settings
        if kms_key_id is not None:
            self._values["kms_key_id"] = kms_key_id
        if microsoft_sql_server_settings is not None:
            self._values["microsoft_sql_server_settings"] = microsoft_sql_server_settings
        if mongo_db_settings is not None:
            self._values["mongo_db_settings"] = mongo_db_settings
        if my_sql_settings is not None:
            self._values["my_sql_settings"] = my_sql_settings
        if neptune_settings is not None:
            self._values["neptune_settings"] = neptune_settings
        if oracle_settings is not None:
            self._values["oracle_settings"] = oracle_settings
        if password is not None:
            self._values["password"] = password
        if port is not None:
            self._values["port"] = port
        if postgre_sql_settings is not None:
            self._values["postgre_sql_settings"] = postgre_sql_settings
        if redis_settings is not None:
            self._values["redis_settings"] = redis_settings
        if redshift_settings is not None:
            self._values["redshift_settings"] = redshift_settings
        if resource_identifier is not None:
            self._values["resource_identifier"] = resource_identifier
        if s3_settings is not None:
            self._values["s3_settings"] = s3_settings
        if server_name is not None:
            self._values["server_name"] = server_name
        if ssl_mode is not None:
            self._values["ssl_mode"] = ssl_mode
        if sybase_settings is not None:
            self._values["sybase_settings"] = sybase_settings
        if tags is not None:
            self._values["tags"] = tags
        if username is not None:
            self._values["username"] = username

    @builtins.property
    def endpoint_type(self) -> builtins.str:
        '''The type of endpoint.

        Valid values are ``source`` and ``target`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-endpointtype
        '''
        result = self._values.get("endpoint_type")
        assert result is not None, "Required property 'endpoint_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def engine_name(self) -> builtins.str:
        '''The type of engine for the endpoint.

        Valid values, depending on the ``EndpointType`` value, include ``"mysql"`` , ``"oracle"`` , ``"postgres"`` , ``"mariadb"`` , ``"aurora"`` , ``"aurora-postgresql"`` , ``"opensearch"`` , ``"redshift"`` , ``"s3"`` , ``"db2"`` , ``"azuredb"`` , ``"sybase"`` , ``"dynamodb"`` , ``"mongodb"`` , ``"kinesis"`` , ``"kafka"`` , ``"elasticsearch"`` , ``"docdb"`` , ``"sqlserver"`` , and ``"neptune"`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-enginename
        '''
        result = self._values.get("engine_name")
        assert result is not None, "Required property 'engine_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def certificate_arn(self) -> typing.Optional[builtins.str]:
        '''The Amazon Resource Name (ARN) for the certificate.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-certificatearn
        '''
        result = self._values.get("certificate_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def database_name(self) -> typing.Optional[builtins.str]:
        '''The name of the endpoint database.

        For a MySQL source or target endpoint, do not specify DatabaseName. To migrate to a specific database, use this setting and ``targetDbType`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-databasename
        '''
        result = self._values.get("database_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def doc_db_settings(
        self,
    ) -> typing.Optional[typing.Union[CfnEndpoint.DocDbSettingsProperty, _IResolvable_da3f097b]]:
        '''Settings in JSON format for the source DocumentDB endpoint.

        For more information about the available settings, see the configuration properties section in `Using DocumentDB as a Target for AWS Database Migration Service <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Source.DocumentDB.html>`_ in the *AWS Database Migration Service User Guide.*

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-docdbsettings
        '''
        result = self._values.get("doc_db_settings")
        return typing.cast(typing.Optional[typing.Union[CfnEndpoint.DocDbSettingsProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def dynamo_db_settings(
        self,
    ) -> typing.Optional[typing.Union[CfnEndpoint.DynamoDbSettingsProperty, _IResolvable_da3f097b]]:
        '''Settings in JSON format for the target Amazon DynamoDB endpoint.

        For information about other available settings, see `Using Object Mapping to Migrate Data to DynamoDB <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.DynamoDB.html#CHAP_Target.DynamoDB.ObjectMapping>`_ in the *AWS Database Migration Service User Guide.*

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-dynamodbsettings
        '''
        result = self._values.get("dynamo_db_settings")
        return typing.cast(typing.Optional[typing.Union[CfnEndpoint.DynamoDbSettingsProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def elasticsearch_settings(
        self,
    ) -> typing.Optional[typing.Union[CfnEndpoint.ElasticsearchSettingsProperty, _IResolvable_da3f097b]]:
        '''Settings in JSON format for the target OpenSearch endpoint.

        For more information about the available settings, see `Extra Connection Attributes When Using OpenSearch as a Target for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.Elasticsearch.html#CHAP_Target.Elasticsearch.Configuration>`_ in the *AWS Database Migration Service User Guide* .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-elasticsearchsettings
        '''
        result = self._values.get("elasticsearch_settings")
        return typing.cast(typing.Optional[typing.Union[CfnEndpoint.ElasticsearchSettingsProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def endpoint_identifier(self) -> typing.Optional[builtins.str]:
        '''The database endpoint identifier.

        Identifiers must begin with a letter and must contain only ASCII letters, digits, and hyphens. They can't end with a hyphen, or contain two consecutive hyphens.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-endpointidentifier
        '''
        result = self._values.get("endpoint_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def extra_connection_attributes(self) -> typing.Optional[builtins.str]:
        '''Additional attributes associated with the connection.

        Each attribute is specified as a name-value pair associated by an equal sign (=). Multiple attributes are separated by a semicolon (;) with no additional white space. For information on the attributes available for connecting your source or target endpoint, see `Working with AWS DMS Endpoints <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Endpoints.html>`_ in the *AWS Database Migration Service User Guide.*

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-extraconnectionattributes
        '''
        result = self._values.get("extra_connection_attributes")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ibm_db2_settings(
        self,
    ) -> typing.Optional[typing.Union[CfnEndpoint.IbmDb2SettingsProperty, _IResolvable_da3f097b]]:
        '''Not currently supported by AWS CloudFormation .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-ibmdb2settings
        '''
        result = self._values.get("ibm_db2_settings")
        return typing.cast(typing.Optional[typing.Union[CfnEndpoint.IbmDb2SettingsProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def kafka_settings(
        self,
    ) -> typing.Optional[typing.Union[CfnEndpoint.KafkaSettingsProperty, _IResolvable_da3f097b]]:
        '''Settings in JSON format for the target Apache Kafka endpoint.

        For more information about the available settings, see `Using object mapping to migrate data to a Kafka topic <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.Kafka.html#CHAP_Target.Kafka.ObjectMapping>`_ in the *AWS Database Migration Service User Guide.*

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-kafkasettings
        '''
        result = self._values.get("kafka_settings")
        return typing.cast(typing.Optional[typing.Union[CfnEndpoint.KafkaSettingsProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def kinesis_settings(
        self,
    ) -> typing.Optional[typing.Union[CfnEndpoint.KinesisSettingsProperty, _IResolvable_da3f097b]]:
        '''Settings in JSON format for the target endpoint for Amazon Kinesis Data Streams.

        For more information about the available settings, see `Using Amazon Kinesis Data Streams as a Target for AWS Database Migration Service <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.Kinesis.html>`_ in the *AWS Database Migration Service User Guide.*

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-kinesissettings
        '''
        result = self._values.get("kinesis_settings")
        return typing.cast(typing.Optional[typing.Union[CfnEndpoint.KinesisSettingsProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''An AWS KMS key identifier that is used to encrypt the connection parameters for the endpoint.

        If you don't specify a value for the ``KmsKeyId`` parameter, then AWS DMS uses your default encryption key.

        AWS KMS creates the default encryption key for your AWS account . Your AWS account has a different default encryption key for each AWS Region .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-kmskeyid
        '''
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def microsoft_sql_server_settings(
        self,
    ) -> typing.Optional[typing.Union[CfnEndpoint.MicrosoftSqlServerSettingsProperty, _IResolvable_da3f097b]]:
        '''Not currently supported by AWS CloudFormation .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-microsoftsqlserversettings
        '''
        result = self._values.get("microsoft_sql_server_settings")
        return typing.cast(typing.Optional[typing.Union[CfnEndpoint.MicrosoftSqlServerSettingsProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def mongo_db_settings(
        self,
    ) -> typing.Optional[typing.Union[CfnEndpoint.MongoDbSettingsProperty, _IResolvable_da3f097b]]:
        '''Not currently supported by AWS CloudFormation .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-mongodbsettings
        '''
        result = self._values.get("mongo_db_settings")
        return typing.cast(typing.Optional[typing.Union[CfnEndpoint.MongoDbSettingsProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def my_sql_settings(
        self,
    ) -> typing.Optional[typing.Union[CfnEndpoint.MySqlSettingsProperty, _IResolvable_da3f097b]]:
        '''Settings in JSON format for the source and target MySQL endpoint.

        For information about other available settings, see `Extra connection attributes when using MySQL as a source for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Source.MySQL.html#CHAP_Source.MySQL.ConnectionAttrib>`_ and `Extra connection attributes when using a MySQL-compatible database as a target for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.MySQL.html#CHAP_Target.MySQL.ConnectionAttrib>`_ in the *AWS Database Migration Service User Guide.*

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-mysqlsettings
        '''
        result = self._values.get("my_sql_settings")
        return typing.cast(typing.Optional[typing.Union[CfnEndpoint.MySqlSettingsProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def neptune_settings(
        self,
    ) -> typing.Optional[typing.Union[CfnEndpoint.NeptuneSettingsProperty, _IResolvable_da3f097b]]:
        '''``AWS::DMS::Endpoint.NeptuneSettings``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-neptunesettings
        '''
        result = self._values.get("neptune_settings")
        return typing.cast(typing.Optional[typing.Union[CfnEndpoint.NeptuneSettingsProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def oracle_settings(
        self,
    ) -> typing.Optional[typing.Union[CfnEndpoint.OracleSettingsProperty, _IResolvable_da3f097b]]:
        '''Settings in JSON format for the source and target Oracle endpoint.

        For information about other available settings, see `Extra connection attributes when using Oracle as a source for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Source.Oracle.html#CHAP_Source.Oracle.ConnectionAttrib>`_ and `Extra connection attributes when using Oracle as a target for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.Oracle.html#CHAP_Target.Oracle.ConnectionAttrib>`_ in the *AWS Database Migration Service User Guide.*

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-oraclesettings
        '''
        result = self._values.get("oracle_settings")
        return typing.cast(typing.Optional[typing.Union[CfnEndpoint.OracleSettingsProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''The password to be used to log in to the endpoint database.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-password
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''The port used by the endpoint database.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-port
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def postgre_sql_settings(
        self,
    ) -> typing.Optional[typing.Union[CfnEndpoint.PostgreSqlSettingsProperty, _IResolvable_da3f097b]]:
        '''Not currently supported by AWS CloudFormation .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-postgresqlsettings
        '''
        result = self._values.get("postgre_sql_settings")
        return typing.cast(typing.Optional[typing.Union[CfnEndpoint.PostgreSqlSettingsProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def redis_settings(
        self,
    ) -> typing.Optional[typing.Union[CfnEndpoint.RedisSettingsProperty, _IResolvable_da3f097b]]:
        '''Settings in JSON format for the target Redis endpoint.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-redissettings
        '''
        result = self._values.get("redis_settings")
        return typing.cast(typing.Optional[typing.Union[CfnEndpoint.RedisSettingsProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def redshift_settings(
        self,
    ) -> typing.Optional[typing.Union[CfnEndpoint.RedshiftSettingsProperty, _IResolvable_da3f097b]]:
        '''Not currently supported by AWS CloudFormation .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-redshiftsettings
        '''
        result = self._values.get("redshift_settings")
        return typing.cast(typing.Optional[typing.Union[CfnEndpoint.RedshiftSettingsProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def resource_identifier(self) -> typing.Optional[builtins.str]:
        '''A friendly name for the resource identifier at the end of the ``EndpointArn`` response parameter that is returned in the created ``Endpoint`` object.

        The value for this parameter can have up to 31 characters. It can contain only ASCII letters, digits, and hyphen ('-'). Also, it can't end with a hyphen or contain two consecutive hyphens, and can only begin with a letter, such as ``Example-App-ARN1`` . For example, this value might result in the ``EndpointArn`` value ``arn:aws:dms:eu-west-1:012345678901:rep:Example-App-ARN1`` . If you don't specify a ``ResourceIdentifier`` value, AWS DMS generates a default identifier value for the end of ``EndpointArn`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-resourceidentifier
        '''
        result = self._values.get("resource_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_settings(
        self,
    ) -> typing.Optional[typing.Union[CfnEndpoint.S3SettingsProperty, _IResolvable_da3f097b]]:
        '''Settings in JSON format for the target Amazon S3 endpoint.

        For more information about the available settings, see `Extra Connection Attributes When Using Amazon S3 as a Target for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.S3.html#CHAP_Target.S3.Configuring>`_ in the *AWS Database Migration Service User Guide.*

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-s3settings
        '''
        result = self._values.get("s3_settings")
        return typing.cast(typing.Optional[typing.Union[CfnEndpoint.S3SettingsProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def server_name(self) -> typing.Optional[builtins.str]:
        '''The name of the server where the endpoint database resides.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-servername
        '''
        result = self._values.get("server_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssl_mode(self) -> typing.Optional[builtins.str]:
        '''The Secure Sockets Layer (SSL) mode to use for the SSL connection. The default is ``none`` .

        .. epigraph::

           When ``engine_name`` is set to S3, then the only allowed value is ``none`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-sslmode
        '''
        result = self._values.get("ssl_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sybase_settings(
        self,
    ) -> typing.Optional[typing.Union[CfnEndpoint.SybaseSettingsProperty, _IResolvable_da3f097b]]:
        '''Settings in JSON format for the source and target SAP ASE endpoint.

        For information about other available settings, see `Extra connection attributes when using SAP ASE as a source for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Source.SAP.html#CHAP_Source.SAP.ConnectionAttrib>`_ and `Extra connection attributes when using SAP ASE as a target for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.SAP.html#CHAP_Target.SAP.ConnectionAttrib>`_ in the *AWS Database Migration Service User Guide.*

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-sybasesettings
        '''
        result = self._values.get("sybase_settings")
        return typing.cast(typing.Optional[typing.Union[CfnEndpoint.SybaseSettingsProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''One or more tags to be assigned to the endpoint.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''The user name to be used to log in to the endpoint database.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-endpoint.html#cfn-dms-endpoint-username
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnEndpointProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnEventSubscription(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_dms.CfnEventSubscription",
):
    '''A CloudFormation ``AWS::DMS::EventSubscription``.

    Use the ``AWS::DMS::EventSubscription`` resource to get notifications for AWS Database Migration Service events through the Amazon Simple Notification Service. For more information, see `Using AWS DMS Event Notification <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Events.html>`_ in the *AWS Database Migration Service User Guide.*

    :cloudformationResource: AWS::DMS::EventSubscription
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_dms as dms
        
        cfn_event_subscription = dms.CfnEventSubscription(self, "MyCfnEventSubscription",
            sns_topic_arn="snsTopicArn",
        
            # the properties below are optional
            enabled=False,
            event_categories=["eventCategories"],
            source_ids=["sourceIds"],
            source_type="sourceType",
            subscription_name="subscriptionName",
            tags=[CfnTag(
                key="key",
                value="value"
            )]
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        sns_topic_arn: builtins.str,
        enabled: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        event_categories: typing.Optional[typing.Sequence[builtins.str]] = None,
        source_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        source_type: typing.Optional[builtins.str] = None,
        subscription_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Create a new ``AWS::DMS::EventSubscription``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param sns_topic_arn: The Amazon Resource Name (ARN) of the Amazon SNS topic created for event notification. The ARN is created by Amazon SNS when you create a topic and subscribe to it.
        :param enabled: Indicates whether to activate the subscription. If you don't specify this property, AWS CloudFormation activates the subscription.
        :param event_categories: A list of event categories for a source type that you want to subscribe to. If you don't specify this property, you are notified about all event categories. For more information, see `Working with Events and Notifications <https://docs.aws.amazon.com//dms/latest/userguide/CHAP_Events.html>`_ in the *AWS DMS User Guide* .
        :param source_ids: A list of identifiers for which AWS DMS provides notification events. If you don't specify a value, notifications are provided for all sources. If you specify multiple values, they must be of the same type. For example, if you specify a database instance ID, then all of the other values must be database instance IDs.
        :param source_type: The type of AWS DMS resource that generates the events. For example, if you want to be notified of events generated by a replication instance, you set this parameter to ``replication-instance`` . If this value isn't specified, all events are returned. Valid values: ``replication-instance`` | ``replication-task``
        :param subscription_name: The name of the AWS DMS event notification subscription. This name must be less than 255 characters.
        :param tags: One or more tags to be assigned to the event subscription.
        '''
        props = CfnEventSubscriptionProps(
            sns_topic_arn=sns_topic_arn,
            enabled=enabled,
            event_categories=event_categories,
            source_ids=source_ids,
            source_type=source_type,
            subscription_name=subscription_name,
            tags=tags,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _TreeInspector_488e0dd5) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''One or more tags to be assigned to the event subscription.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snsTopicArn")
    def sns_topic_arn(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of the Amazon SNS topic created for event notification.

        The ARN is created by Amazon SNS when you create a topic and subscribe to it.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-snstopicarn
        '''
        return typing.cast(builtins.str, jsii.get(self, "snsTopicArn"))

    @sns_topic_arn.setter
    def sns_topic_arn(self, value: builtins.str) -> None:
        jsii.set(self, "snsTopicArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''Indicates whether to activate the subscription.

        If you don't specify this property, AWS CloudFormation activates the subscription.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-enabled
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventCategories")
    def event_categories(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of event categories for a source type that you want to subscribe to.

        If you don't specify this property, you are notified about all event categories. For more information, see `Working with Events and Notifications <https://docs.aws.amazon.com//dms/latest/userguide/CHAP_Events.html>`_ in the *AWS DMS User Guide* .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-eventcategories
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "eventCategories"))

    @event_categories.setter
    def event_categories(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        jsii.set(self, "eventCategories", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceIds")
    def source_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of identifiers for which AWS DMS provides notification events.

        If you don't specify a value, notifications are provided for all sources.

        If you specify multiple values, they must be of the same type. For example, if you specify a database instance ID, then all of the other values must be database instance IDs.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-sourceids
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "sourceIds"))

    @source_ids.setter
    def source_ids(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        jsii.set(self, "sourceIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceType")
    def source_type(self) -> typing.Optional[builtins.str]:
        '''The type of AWS DMS resource that generates the events.

        For example, if you want to be notified of events generated by a replication instance, you set this parameter to ``replication-instance`` . If this value isn't specified, all events are returned.

        Valid values: ``replication-instance`` | ``replication-task``

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-sourcetype
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceType"))

    @source_type.setter
    def source_type(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "sourceType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subscriptionName")
    def subscription_name(self) -> typing.Optional[builtins.str]:
        '''The name of the AWS DMS event notification subscription.

        This name must be less than 255 characters.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-subscriptionname
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subscriptionName"))

    @subscription_name.setter
    def subscription_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "subscriptionName", value)


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_dms.CfnEventSubscriptionProps",
    jsii_struct_bases=[],
    name_mapping={
        "sns_topic_arn": "snsTopicArn",
        "enabled": "enabled",
        "event_categories": "eventCategories",
        "source_ids": "sourceIds",
        "source_type": "sourceType",
        "subscription_name": "subscriptionName",
        "tags": "tags",
    },
)
class CfnEventSubscriptionProps:
    def __init__(
        self,
        *,
        sns_topic_arn: builtins.str,
        enabled: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        event_categories: typing.Optional[typing.Sequence[builtins.str]] = None,
        source_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        source_type: typing.Optional[builtins.str] = None,
        subscription_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Properties for defining a ``CfnEventSubscription``.

        :param sns_topic_arn: The Amazon Resource Name (ARN) of the Amazon SNS topic created for event notification. The ARN is created by Amazon SNS when you create a topic and subscribe to it.
        :param enabled: Indicates whether to activate the subscription. If you don't specify this property, AWS CloudFormation activates the subscription.
        :param event_categories: A list of event categories for a source type that you want to subscribe to. If you don't specify this property, you are notified about all event categories. For more information, see `Working with Events and Notifications <https://docs.aws.amazon.com//dms/latest/userguide/CHAP_Events.html>`_ in the *AWS DMS User Guide* .
        :param source_ids: A list of identifiers for which AWS DMS provides notification events. If you don't specify a value, notifications are provided for all sources. If you specify multiple values, they must be of the same type. For example, if you specify a database instance ID, then all of the other values must be database instance IDs.
        :param source_type: The type of AWS DMS resource that generates the events. For example, if you want to be notified of events generated by a replication instance, you set this parameter to ``replication-instance`` . If this value isn't specified, all events are returned. Valid values: ``replication-instance`` | ``replication-task``
        :param subscription_name: The name of the AWS DMS event notification subscription. This name must be less than 255 characters.
        :param tags: One or more tags to be assigned to the event subscription.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_dms as dms
            
            cfn_event_subscription_props = dms.CfnEventSubscriptionProps(
                sns_topic_arn="snsTopicArn",
            
                # the properties below are optional
                enabled=False,
                event_categories=["eventCategories"],
                source_ids=["sourceIds"],
                source_type="sourceType",
                subscription_name="subscriptionName",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "sns_topic_arn": sns_topic_arn,
        }
        if enabled is not None:
            self._values["enabled"] = enabled
        if event_categories is not None:
            self._values["event_categories"] = event_categories
        if source_ids is not None:
            self._values["source_ids"] = source_ids
        if source_type is not None:
            self._values["source_type"] = source_type
        if subscription_name is not None:
            self._values["subscription_name"] = subscription_name
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def sns_topic_arn(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of the Amazon SNS topic created for event notification.

        The ARN is created by Amazon SNS when you create a topic and subscribe to it.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-snstopicarn
        '''
        result = self._values.get("sns_topic_arn")
        assert result is not None, "Required property 'sns_topic_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''Indicates whether to activate the subscription.

        If you don't specify this property, AWS CloudFormation activates the subscription.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-enabled
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    @builtins.property
    def event_categories(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of event categories for a source type that you want to subscribe to.

        If you don't specify this property, you are notified about all event categories. For more information, see `Working with Events and Notifications <https://docs.aws.amazon.com//dms/latest/userguide/CHAP_Events.html>`_ in the *AWS DMS User Guide* .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-eventcategories
        '''
        result = self._values.get("event_categories")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def source_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of identifiers for which AWS DMS provides notification events.

        If you don't specify a value, notifications are provided for all sources.

        If you specify multiple values, they must be of the same type. For example, if you specify a database instance ID, then all of the other values must be database instance IDs.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-sourceids
        '''
        result = self._values.get("source_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def source_type(self) -> typing.Optional[builtins.str]:
        '''The type of AWS DMS resource that generates the events.

        For example, if you want to be notified of events generated by a replication instance, you set this parameter to ``replication-instance`` . If this value isn't specified, all events are returned.

        Valid values: ``replication-instance`` | ``replication-task``

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-sourcetype
        '''
        result = self._values.get("source_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subscription_name(self) -> typing.Optional[builtins.str]:
        '''The name of the AWS DMS event notification subscription.

        This name must be less than 255 characters.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-subscriptionname
        '''
        result = self._values.get("subscription_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''One or more tags to be assigned to the event subscription.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-eventsubscription.html#cfn-dms-eventsubscription-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnEventSubscriptionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnReplicationInstance(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_dms.CfnReplicationInstance",
):
    '''A CloudFormation ``AWS::DMS::ReplicationInstance``.

    The ``AWS::DMS::ReplicationInstance`` resource creates an AWS DMS replication instance.

    :cloudformationResource: AWS::DMS::ReplicationInstance
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_dms as dms
        
        cfn_replication_instance = dms.CfnReplicationInstance(self, "MyCfnReplicationInstance",
            replication_instance_class="replicationInstanceClass",
        
            # the properties below are optional
            allocated_storage=123,
            allow_major_version_upgrade=False,
            auto_minor_version_upgrade=False,
            availability_zone="availabilityZone",
            engine_version="engineVersion",
            kms_key_id="kmsKeyId",
            multi_az=False,
            preferred_maintenance_window="preferredMaintenanceWindow",
            publicly_accessible=False,
            replication_instance_identifier="replicationInstanceIdentifier",
            replication_subnet_group_identifier="replicationSubnetGroupIdentifier",
            resource_identifier="resourceIdentifier",
            tags=[CfnTag(
                key="key",
                value="value"
            )],
            vpc_security_group_ids=["vpcSecurityGroupIds"]
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        replication_instance_class: builtins.str,
        allocated_storage: typing.Optional[jsii.Number] = None,
        allow_major_version_upgrade: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        auto_minor_version_upgrade: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        availability_zone: typing.Optional[builtins.str] = None,
        engine_version: typing.Optional[builtins.str] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        multi_az: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        preferred_maintenance_window: typing.Optional[builtins.str] = None,
        publicly_accessible: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        replication_instance_identifier: typing.Optional[builtins.str] = None,
        replication_subnet_group_identifier: typing.Optional[builtins.str] = None,
        resource_identifier: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        vpc_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Create a new ``AWS::DMS::ReplicationInstance``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param replication_instance_class: The compute and memory capacity of the replication instance as defined for the specified replication instance class. For example to specify the instance class dms.c4.large, set this parameter to ``"dms.c4.large"`` . For more information on the settings and capacities for the available replication instance classes, see `Selecting the right AWS DMS replication instance for your migration <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_ReplicationInstance.html#CHAP_ReplicationInstance.InDepth>`_ .
        :param allocated_storage: The amount of storage (in gigabytes) to be initially allocated for the replication instance.
        :param allow_major_version_upgrade: Indicates that major version upgrades are allowed. Changing this parameter does not result in an outage, and the change is asynchronously applied as soon as possible. This parameter must be set to ``true`` when specifying a value for the ``EngineVersion`` parameter that is a different major version than the replication instance's current version.
        :param auto_minor_version_upgrade: A value that indicates whether minor engine upgrades are applied automatically to the replication instance during the maintenance window. This parameter defaults to ``true`` . Default: ``true``
        :param availability_zone: The Availability Zone that the replication instance will be created in. The default value is a random, system-chosen Availability Zone in the endpoint's AWS Region , for example: ``us-east-1d``
        :param engine_version: The engine version number of the replication instance. If an engine version number is not specified when a replication instance is created, the default is the latest engine version available.
        :param kms_key_id: An AWS KMS key identifier that is used to encrypt the data on the replication instance. If you don't specify a value for the ``KmsKeyId`` parameter, then AWS DMS uses your default encryption key. AWS KMS creates the default encryption key for your AWS account . Your AWS account has a different default encryption key for each AWS Region .
        :param multi_az: Specifies whether the replication instance is a Multi-AZ deployment. You can't set the ``AvailabilityZone`` parameter if the Multi-AZ parameter is set to ``true`` .
        :param preferred_maintenance_window: The weekly time range during which system maintenance can occur, in Universal Coordinated Time (UTC). Format: ``ddd:hh24:mi-ddd:hh24:mi`` Default: A 30-minute window selected at random from an 8-hour block of time per AWS Region , occurring on a random day of the week. Valid Days: Mon, Tue, Wed, Thu, Fri, Sat, Sun Constraints: Minimum 30-minute window.
        :param publicly_accessible: Specifies the accessibility options for the replication instance. A value of ``true`` represents an instance with a public IP address. A value of ``false`` represents an instance with a private IP address. The default value is ``true`` .
        :param replication_instance_identifier: The replication instance identifier. This parameter is stored as a lowercase string. Constraints: - Must contain 1-63 alphanumeric characters or hyphens. - First character must be a letter. - Can't end with a hyphen or contain two consecutive hyphens. Example: ``myrepinstance``
        :param replication_subnet_group_identifier: A subnet group to associate with the replication instance.
        :param resource_identifier: A friendly name for the resource identifier at the end of the ``EndpointArn`` response parameter that is returned in the created ``Endpoint`` object. The value for this parameter can have up to 31 characters. It can contain only ASCII letters, digits, and hyphen ('-'). Also, it can't end with a hyphen or contain two consecutive hyphens, and can only begin with a letter, such as ``Example-App-ARN1`` . For example, this value might result in the ``EndpointArn`` value ``arn:aws:dms:eu-west-1:012345678901:rep:Example-App-ARN1`` . If you don't specify a ``ResourceIdentifier`` value, AWS DMS generates a default identifier value for the end of ``EndpointArn`` .
        :param tags: One or more tags to be assigned to the replication instance.
        :param vpc_security_group_ids: Specifies the VPC security group to be used with the replication instance. The VPC security group must work with the VPC containing the replication instance.
        '''
        props = CfnReplicationInstanceProps(
            replication_instance_class=replication_instance_class,
            allocated_storage=allocated_storage,
            allow_major_version_upgrade=allow_major_version_upgrade,
            auto_minor_version_upgrade=auto_minor_version_upgrade,
            availability_zone=availability_zone,
            engine_version=engine_version,
            kms_key_id=kms_key_id,
            multi_az=multi_az,
            preferred_maintenance_window=preferred_maintenance_window,
            publicly_accessible=publicly_accessible,
            replication_instance_identifier=replication_instance_identifier,
            replication_subnet_group_identifier=replication_subnet_group_identifier,
            resource_identifier=resource_identifier,
            tags=tags,
            vpc_security_group_ids=vpc_security_group_ids,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _TreeInspector_488e0dd5) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrReplicationInstancePrivateIpAddresses")
    def attr_replication_instance_private_ip_addresses(
        self,
    ) -> typing.List[builtins.str]:
        '''One or more private IP addresses for the replication instance.

        :cloudformationAttribute: ReplicationInstancePrivateIpAddresses
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "attrReplicationInstancePrivateIpAddresses"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrReplicationInstancePublicIpAddresses")
    def attr_replication_instance_public_ip_addresses(
        self,
    ) -> typing.List[builtins.str]:
        '''One or more public IP addresses for the replication instance.

        :cloudformationAttribute: ReplicationInstancePublicIpAddresses
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "attrReplicationInstancePublicIpAddresses"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''One or more tags to be assigned to the replication instance.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationInstanceClass")
    def replication_instance_class(self) -> builtins.str:
        '''The compute and memory capacity of the replication instance as defined for the specified replication instance class.

        For example to specify the instance class dms.c4.large, set this parameter to ``"dms.c4.large"`` .

        For more information on the settings and capacities for the available replication instance classes, see `Selecting the right AWS DMS replication instance for your migration <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_ReplicationInstance.html#CHAP_ReplicationInstance.InDepth>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-replicationinstanceclass
        '''
        return typing.cast(builtins.str, jsii.get(self, "replicationInstanceClass"))

    @replication_instance_class.setter
    def replication_instance_class(self, value: builtins.str) -> None:
        jsii.set(self, "replicationInstanceClass", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allocatedStorage")
    def allocated_storage(self) -> typing.Optional[jsii.Number]:
        '''The amount of storage (in gigabytes) to be initially allocated for the replication instance.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-allocatedstorage
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "allocatedStorage"))

    @allocated_storage.setter
    def allocated_storage(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "allocatedStorage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowMajorVersionUpgrade")
    def allow_major_version_upgrade(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''Indicates that major version upgrades are allowed.

        Changing this parameter does not result in an outage, and the change is asynchronously applied as soon as possible.

        This parameter must be set to ``true`` when specifying a value for the ``EngineVersion`` parameter that is a different major version than the replication instance's current version.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-allowmajorversionupgrade
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "allowMajorVersionUpgrade"))

    @allow_major_version_upgrade.setter
    def allow_major_version_upgrade(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "allowMajorVersionUpgrade", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoMinorVersionUpgrade")
    def auto_minor_version_upgrade(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''A value that indicates whether minor engine upgrades are applied automatically to the replication instance during the maintenance window.

        This parameter defaults to ``true`` .

        Default: ``true``

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-autominorversionupgrade
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "autoMinorVersionUpgrade"))

    @auto_minor_version_upgrade.setter
    def auto_minor_version_upgrade(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "autoMinorVersionUpgrade", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> typing.Optional[builtins.str]:
        '''The Availability Zone that the replication instance will be created in.

        The default value is a random, system-chosen Availability Zone in the endpoint's AWS Region , for example: ``us-east-1d``

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-availabilityzone
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "availabilityZone"))

    @availability_zone.setter
    def availability_zone(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "availabilityZone", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineVersion")
    def engine_version(self) -> typing.Optional[builtins.str]:
        '''The engine version number of the replication instance.

        If an engine version number is not specified when a replication instance is created, the default is the latest engine version available.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-engineversion
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "engineVersion"))

    @engine_version.setter
    def engine_version(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "engineVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''An AWS KMS key identifier that is used to encrypt the data on the replication instance.

        If you don't specify a value for the ``KmsKeyId`` parameter, then AWS DMS uses your default encryption key.

        AWS KMS creates the default encryption key for your AWS account . Your AWS account has a different default encryption key for each AWS Region .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-kmskeyid
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyId"))

    @kms_key_id.setter
    def kms_key_id(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "kmsKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="multiAz")
    def multi_az(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''Specifies whether the replication instance is a Multi-AZ deployment.

        You can't set the ``AvailabilityZone`` parameter if the Multi-AZ parameter is set to ``true`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-multiaz
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "multiAz"))

    @multi_az.setter
    def multi_az(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "multiAz", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredMaintenanceWindow")
    def preferred_maintenance_window(self) -> typing.Optional[builtins.str]:
        '''The weekly time range during which system maintenance can occur, in Universal Coordinated Time (UTC).

        Format: ``ddd:hh24:mi-ddd:hh24:mi``

        Default: A 30-minute window selected at random from an 8-hour block of time per AWS Region , occurring on a random day of the week.

        Valid Days: Mon, Tue, Wed, Thu, Fri, Sat, Sun

        Constraints: Minimum 30-minute window.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-preferredmaintenancewindow
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preferredMaintenanceWindow"))

    @preferred_maintenance_window.setter
    def preferred_maintenance_window(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        jsii.set(self, "preferredMaintenanceWindow", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publiclyAccessible")
    def publicly_accessible(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''Specifies the accessibility options for the replication instance.

        A value of ``true`` represents an instance with a public IP address. A value of ``false`` represents an instance with a private IP address. The default value is ``true`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-publiclyaccessible
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "publiclyAccessible"))

    @publicly_accessible.setter
    def publicly_accessible(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "publiclyAccessible", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationInstanceIdentifier")
    def replication_instance_identifier(self) -> typing.Optional[builtins.str]:
        '''The replication instance identifier. This parameter is stored as a lowercase string.

        Constraints:

        - Must contain 1-63 alphanumeric characters or hyphens.
        - First character must be a letter.
        - Can't end with a hyphen or contain two consecutive hyphens.

        Example: ``myrepinstance``

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-replicationinstanceidentifier
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "replicationInstanceIdentifier"))

    @replication_instance_identifier.setter
    def replication_instance_identifier(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        jsii.set(self, "replicationInstanceIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationSubnetGroupIdentifier")
    def replication_subnet_group_identifier(self) -> typing.Optional[builtins.str]:
        '''A subnet group to associate with the replication instance.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-replicationsubnetgroupidentifier
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "replicationSubnetGroupIdentifier"))

    @replication_subnet_group_identifier.setter
    def replication_subnet_group_identifier(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        jsii.set(self, "replicationSubnetGroupIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceIdentifier")
    def resource_identifier(self) -> typing.Optional[builtins.str]:
        '''A friendly name for the resource identifier at the end of the ``EndpointArn`` response parameter that is returned in the created ``Endpoint`` object.

        The value for this parameter can have up to 31 characters. It can contain only ASCII letters, digits, and hyphen ('-'). Also, it can't end with a hyphen or contain two consecutive hyphens, and can only begin with a letter, such as ``Example-App-ARN1`` . For example, this value might result in the ``EndpointArn`` value ``arn:aws:dms:eu-west-1:012345678901:rep:Example-App-ARN1`` . If you don't specify a ``ResourceIdentifier`` value, AWS DMS generates a default identifier value for the end of ``EndpointArn`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-resourceidentifier
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceIdentifier"))

    @resource_identifier.setter
    def resource_identifier(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "resourceIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcSecurityGroupIds")
    def vpc_security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the VPC security group to be used with the replication instance.

        The VPC security group must work with the VPC containing the replication instance.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-vpcsecuritygroupids
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "vpcSecurityGroupIds"))

    @vpc_security_group_ids.setter
    def vpc_security_group_ids(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        jsii.set(self, "vpcSecurityGroupIds", value)


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_dms.CfnReplicationInstanceProps",
    jsii_struct_bases=[],
    name_mapping={
        "replication_instance_class": "replicationInstanceClass",
        "allocated_storage": "allocatedStorage",
        "allow_major_version_upgrade": "allowMajorVersionUpgrade",
        "auto_minor_version_upgrade": "autoMinorVersionUpgrade",
        "availability_zone": "availabilityZone",
        "engine_version": "engineVersion",
        "kms_key_id": "kmsKeyId",
        "multi_az": "multiAz",
        "preferred_maintenance_window": "preferredMaintenanceWindow",
        "publicly_accessible": "publiclyAccessible",
        "replication_instance_identifier": "replicationInstanceIdentifier",
        "replication_subnet_group_identifier": "replicationSubnetGroupIdentifier",
        "resource_identifier": "resourceIdentifier",
        "tags": "tags",
        "vpc_security_group_ids": "vpcSecurityGroupIds",
    },
)
class CfnReplicationInstanceProps:
    def __init__(
        self,
        *,
        replication_instance_class: builtins.str,
        allocated_storage: typing.Optional[jsii.Number] = None,
        allow_major_version_upgrade: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        auto_minor_version_upgrade: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        availability_zone: typing.Optional[builtins.str] = None,
        engine_version: typing.Optional[builtins.str] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        multi_az: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        preferred_maintenance_window: typing.Optional[builtins.str] = None,
        publicly_accessible: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        replication_instance_identifier: typing.Optional[builtins.str] = None,
        replication_subnet_group_identifier: typing.Optional[builtins.str] = None,
        resource_identifier: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        vpc_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Properties for defining a ``CfnReplicationInstance``.

        :param replication_instance_class: The compute and memory capacity of the replication instance as defined for the specified replication instance class. For example to specify the instance class dms.c4.large, set this parameter to ``"dms.c4.large"`` . For more information on the settings and capacities for the available replication instance classes, see `Selecting the right AWS DMS replication instance for your migration <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_ReplicationInstance.html#CHAP_ReplicationInstance.InDepth>`_ .
        :param allocated_storage: The amount of storage (in gigabytes) to be initially allocated for the replication instance.
        :param allow_major_version_upgrade: Indicates that major version upgrades are allowed. Changing this parameter does not result in an outage, and the change is asynchronously applied as soon as possible. This parameter must be set to ``true`` when specifying a value for the ``EngineVersion`` parameter that is a different major version than the replication instance's current version.
        :param auto_minor_version_upgrade: A value that indicates whether minor engine upgrades are applied automatically to the replication instance during the maintenance window. This parameter defaults to ``true`` . Default: ``true``
        :param availability_zone: The Availability Zone that the replication instance will be created in. The default value is a random, system-chosen Availability Zone in the endpoint's AWS Region , for example: ``us-east-1d``
        :param engine_version: The engine version number of the replication instance. If an engine version number is not specified when a replication instance is created, the default is the latest engine version available.
        :param kms_key_id: An AWS KMS key identifier that is used to encrypt the data on the replication instance. If you don't specify a value for the ``KmsKeyId`` parameter, then AWS DMS uses your default encryption key. AWS KMS creates the default encryption key for your AWS account . Your AWS account has a different default encryption key for each AWS Region .
        :param multi_az: Specifies whether the replication instance is a Multi-AZ deployment. You can't set the ``AvailabilityZone`` parameter if the Multi-AZ parameter is set to ``true`` .
        :param preferred_maintenance_window: The weekly time range during which system maintenance can occur, in Universal Coordinated Time (UTC). Format: ``ddd:hh24:mi-ddd:hh24:mi`` Default: A 30-minute window selected at random from an 8-hour block of time per AWS Region , occurring on a random day of the week. Valid Days: Mon, Tue, Wed, Thu, Fri, Sat, Sun Constraints: Minimum 30-minute window.
        :param publicly_accessible: Specifies the accessibility options for the replication instance. A value of ``true`` represents an instance with a public IP address. A value of ``false`` represents an instance with a private IP address. The default value is ``true`` .
        :param replication_instance_identifier: The replication instance identifier. This parameter is stored as a lowercase string. Constraints: - Must contain 1-63 alphanumeric characters or hyphens. - First character must be a letter. - Can't end with a hyphen or contain two consecutive hyphens. Example: ``myrepinstance``
        :param replication_subnet_group_identifier: A subnet group to associate with the replication instance.
        :param resource_identifier: A friendly name for the resource identifier at the end of the ``EndpointArn`` response parameter that is returned in the created ``Endpoint`` object. The value for this parameter can have up to 31 characters. It can contain only ASCII letters, digits, and hyphen ('-'). Also, it can't end with a hyphen or contain two consecutive hyphens, and can only begin with a letter, such as ``Example-App-ARN1`` . For example, this value might result in the ``EndpointArn`` value ``arn:aws:dms:eu-west-1:012345678901:rep:Example-App-ARN1`` . If you don't specify a ``ResourceIdentifier`` value, AWS DMS generates a default identifier value for the end of ``EndpointArn`` .
        :param tags: One or more tags to be assigned to the replication instance.
        :param vpc_security_group_ids: Specifies the VPC security group to be used with the replication instance. The VPC security group must work with the VPC containing the replication instance.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_dms as dms
            
            cfn_replication_instance_props = dms.CfnReplicationInstanceProps(
                replication_instance_class="replicationInstanceClass",
            
                # the properties below are optional
                allocated_storage=123,
                allow_major_version_upgrade=False,
                auto_minor_version_upgrade=False,
                availability_zone="availabilityZone",
                engine_version="engineVersion",
                kms_key_id="kmsKeyId",
                multi_az=False,
                preferred_maintenance_window="preferredMaintenanceWindow",
                publicly_accessible=False,
                replication_instance_identifier="replicationInstanceIdentifier",
                replication_subnet_group_identifier="replicationSubnetGroupIdentifier",
                resource_identifier="resourceIdentifier",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )],
                vpc_security_group_ids=["vpcSecurityGroupIds"]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "replication_instance_class": replication_instance_class,
        }
        if allocated_storage is not None:
            self._values["allocated_storage"] = allocated_storage
        if allow_major_version_upgrade is not None:
            self._values["allow_major_version_upgrade"] = allow_major_version_upgrade
        if auto_minor_version_upgrade is not None:
            self._values["auto_minor_version_upgrade"] = auto_minor_version_upgrade
        if availability_zone is not None:
            self._values["availability_zone"] = availability_zone
        if engine_version is not None:
            self._values["engine_version"] = engine_version
        if kms_key_id is not None:
            self._values["kms_key_id"] = kms_key_id
        if multi_az is not None:
            self._values["multi_az"] = multi_az
        if preferred_maintenance_window is not None:
            self._values["preferred_maintenance_window"] = preferred_maintenance_window
        if publicly_accessible is not None:
            self._values["publicly_accessible"] = publicly_accessible
        if replication_instance_identifier is not None:
            self._values["replication_instance_identifier"] = replication_instance_identifier
        if replication_subnet_group_identifier is not None:
            self._values["replication_subnet_group_identifier"] = replication_subnet_group_identifier
        if resource_identifier is not None:
            self._values["resource_identifier"] = resource_identifier
        if tags is not None:
            self._values["tags"] = tags
        if vpc_security_group_ids is not None:
            self._values["vpc_security_group_ids"] = vpc_security_group_ids

    @builtins.property
    def replication_instance_class(self) -> builtins.str:
        '''The compute and memory capacity of the replication instance as defined for the specified replication instance class.

        For example to specify the instance class dms.c4.large, set this parameter to ``"dms.c4.large"`` .

        For more information on the settings and capacities for the available replication instance classes, see `Selecting the right AWS DMS replication instance for your migration <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_ReplicationInstance.html#CHAP_ReplicationInstance.InDepth>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-replicationinstanceclass
        '''
        result = self._values.get("replication_instance_class")
        assert result is not None, "Required property 'replication_instance_class' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allocated_storage(self) -> typing.Optional[jsii.Number]:
        '''The amount of storage (in gigabytes) to be initially allocated for the replication instance.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-allocatedstorage
        '''
        result = self._values.get("allocated_storage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def allow_major_version_upgrade(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''Indicates that major version upgrades are allowed.

        Changing this parameter does not result in an outage, and the change is asynchronously applied as soon as possible.

        This parameter must be set to ``true`` when specifying a value for the ``EngineVersion`` parameter that is a different major version than the replication instance's current version.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-allowmajorversionupgrade
        '''
        result = self._values.get("allow_major_version_upgrade")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    @builtins.property
    def auto_minor_version_upgrade(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''A value that indicates whether minor engine upgrades are applied automatically to the replication instance during the maintenance window.

        This parameter defaults to ``true`` .

        Default: ``true``

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-autominorversionupgrade
        '''
        result = self._values.get("auto_minor_version_upgrade")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    @builtins.property
    def availability_zone(self) -> typing.Optional[builtins.str]:
        '''The Availability Zone that the replication instance will be created in.

        The default value is a random, system-chosen Availability Zone in the endpoint's AWS Region , for example: ``us-east-1d``

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-availabilityzone
        '''
        result = self._values.get("availability_zone")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def engine_version(self) -> typing.Optional[builtins.str]:
        '''The engine version number of the replication instance.

        If an engine version number is not specified when a replication instance is created, the default is the latest engine version available.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-engineversion
        '''
        result = self._values.get("engine_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''An AWS KMS key identifier that is used to encrypt the data on the replication instance.

        If you don't specify a value for the ``KmsKeyId`` parameter, then AWS DMS uses your default encryption key.

        AWS KMS creates the default encryption key for your AWS account . Your AWS account has a different default encryption key for each AWS Region .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-kmskeyid
        '''
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def multi_az(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''Specifies whether the replication instance is a Multi-AZ deployment.

        You can't set the ``AvailabilityZone`` parameter if the Multi-AZ parameter is set to ``true`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-multiaz
        '''
        result = self._values.get("multi_az")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    @builtins.property
    def preferred_maintenance_window(self) -> typing.Optional[builtins.str]:
        '''The weekly time range during which system maintenance can occur, in Universal Coordinated Time (UTC).

        Format: ``ddd:hh24:mi-ddd:hh24:mi``

        Default: A 30-minute window selected at random from an 8-hour block of time per AWS Region , occurring on a random day of the week.

        Valid Days: Mon, Tue, Wed, Thu, Fri, Sat, Sun

        Constraints: Minimum 30-minute window.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-preferredmaintenancewindow
        '''
        result = self._values.get("preferred_maintenance_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def publicly_accessible(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''Specifies the accessibility options for the replication instance.

        A value of ``true`` represents an instance with a public IP address. A value of ``false`` represents an instance with a private IP address. The default value is ``true`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-publiclyaccessible
        '''
        result = self._values.get("publicly_accessible")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    @builtins.property
    def replication_instance_identifier(self) -> typing.Optional[builtins.str]:
        '''The replication instance identifier. This parameter is stored as a lowercase string.

        Constraints:

        - Must contain 1-63 alphanumeric characters or hyphens.
        - First character must be a letter.
        - Can't end with a hyphen or contain two consecutive hyphens.

        Example: ``myrepinstance``

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-replicationinstanceidentifier
        '''
        result = self._values.get("replication_instance_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def replication_subnet_group_identifier(self) -> typing.Optional[builtins.str]:
        '''A subnet group to associate with the replication instance.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-replicationsubnetgroupidentifier
        '''
        result = self._values.get("replication_subnet_group_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource_identifier(self) -> typing.Optional[builtins.str]:
        '''A friendly name for the resource identifier at the end of the ``EndpointArn`` response parameter that is returned in the created ``Endpoint`` object.

        The value for this parameter can have up to 31 characters. It can contain only ASCII letters, digits, and hyphen ('-'). Also, it can't end with a hyphen or contain two consecutive hyphens, and can only begin with a letter, such as ``Example-App-ARN1`` . For example, this value might result in the ``EndpointArn`` value ``arn:aws:dms:eu-west-1:012345678901:rep:Example-App-ARN1`` . If you don't specify a ``ResourceIdentifier`` value, AWS DMS generates a default identifier value for the end of ``EndpointArn`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-resourceidentifier
        '''
        result = self._values.get("resource_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''One or more tags to be assigned to the replication instance.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    @builtins.property
    def vpc_security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the VPC security group to be used with the replication instance.

        The VPC security group must work with the VPC containing the replication instance.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationinstance.html#cfn-dms-replicationinstance-vpcsecuritygroupids
        '''
        result = self._values.get("vpc_security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnReplicationInstanceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnReplicationSubnetGroup(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_dms.CfnReplicationSubnetGroup",
):
    '''A CloudFormation ``AWS::DMS::ReplicationSubnetGroup``.

    The ``AWS::DMS::ReplicationSubnetGroup`` resource creates an AWS DMS replication subnet group. Subnet groups must contain at least two subnets in two different Availability Zones in the same region.
    .. epigraph::

       Resource creation will fail if the ``dms-vpc-role`` IAM role doesn't already exist. For more information, see `Creating the IAM Roles to Use With the AWS CLI and AWS DMS API <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Security.APIRole.html>`_ in the *AWS Database Migration Service User Guide.*

    :cloudformationResource: AWS::DMS::ReplicationSubnetGroup
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationsubnetgroup.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_dms as dms
        
        cfn_replication_subnet_group = dms.CfnReplicationSubnetGroup(self, "MyCfnReplicationSubnetGroup",
            replication_subnet_group_description="replicationSubnetGroupDescription",
            subnet_ids=["subnetIds"],
        
            # the properties below are optional
            replication_subnet_group_identifier="replicationSubnetGroupIdentifier",
            tags=[CfnTag(
                key="key",
                value="value"
            )]
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        replication_subnet_group_description: builtins.str,
        subnet_ids: typing.Sequence[builtins.str],
        replication_subnet_group_identifier: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Create a new ``AWS::DMS::ReplicationSubnetGroup``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param replication_subnet_group_description: The description for the subnet group.
        :param subnet_ids: One or more subnet IDs to be assigned to the subnet group.
        :param replication_subnet_group_identifier: The identifier for the replication subnet group. If you don't specify a name, AWS CloudFormation generates a unique ID and uses that ID for the identifier.
        :param tags: One or more tags to be assigned to the subnet group.
        '''
        props = CfnReplicationSubnetGroupProps(
            replication_subnet_group_description=replication_subnet_group_description,
            subnet_ids=subnet_ids,
            replication_subnet_group_identifier=replication_subnet_group_identifier,
            tags=tags,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _TreeInspector_488e0dd5) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''One or more tags to be assigned to the subnet group.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationsubnetgroup.html#cfn-dms-replicationsubnetgroup-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationSubnetGroupDescription")
    def replication_subnet_group_description(self) -> builtins.str:
        '''The description for the subnet group.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationsubnetgroup.html#cfn-dms-replicationsubnetgroup-replicationsubnetgroupdescription
        '''
        return typing.cast(builtins.str, jsii.get(self, "replicationSubnetGroupDescription"))

    @replication_subnet_group_description.setter
    def replication_subnet_group_description(self, value: builtins.str) -> None:
        jsii.set(self, "replicationSubnetGroupDescription", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.List[builtins.str]:
        '''One or more subnet IDs to be assigned to the subnet group.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationsubnetgroup.html#cfn-dms-replicationsubnetgroup-subnetids
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "subnetIds"))

    @subnet_ids.setter
    def subnet_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "subnetIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationSubnetGroupIdentifier")
    def replication_subnet_group_identifier(self) -> typing.Optional[builtins.str]:
        '''The identifier for the replication subnet group.

        If you don't specify a name, AWS CloudFormation generates a unique ID and uses that ID for the identifier.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationsubnetgroup.html#cfn-dms-replicationsubnetgroup-replicationsubnetgroupidentifier
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "replicationSubnetGroupIdentifier"))

    @replication_subnet_group_identifier.setter
    def replication_subnet_group_identifier(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        jsii.set(self, "replicationSubnetGroupIdentifier", value)


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_dms.CfnReplicationSubnetGroupProps",
    jsii_struct_bases=[],
    name_mapping={
        "replication_subnet_group_description": "replicationSubnetGroupDescription",
        "subnet_ids": "subnetIds",
        "replication_subnet_group_identifier": "replicationSubnetGroupIdentifier",
        "tags": "tags",
    },
)
class CfnReplicationSubnetGroupProps:
    def __init__(
        self,
        *,
        replication_subnet_group_description: builtins.str,
        subnet_ids: typing.Sequence[builtins.str],
        replication_subnet_group_identifier: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Properties for defining a ``CfnReplicationSubnetGroup``.

        :param replication_subnet_group_description: The description for the subnet group.
        :param subnet_ids: One or more subnet IDs to be assigned to the subnet group.
        :param replication_subnet_group_identifier: The identifier for the replication subnet group. If you don't specify a name, AWS CloudFormation generates a unique ID and uses that ID for the identifier.
        :param tags: One or more tags to be assigned to the subnet group.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationsubnetgroup.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_dms as dms
            
            cfn_replication_subnet_group_props = dms.CfnReplicationSubnetGroupProps(
                replication_subnet_group_description="replicationSubnetGroupDescription",
                subnet_ids=["subnetIds"],
            
                # the properties below are optional
                replication_subnet_group_identifier="replicationSubnetGroupIdentifier",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "replication_subnet_group_description": replication_subnet_group_description,
            "subnet_ids": subnet_ids,
        }
        if replication_subnet_group_identifier is not None:
            self._values["replication_subnet_group_identifier"] = replication_subnet_group_identifier
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def replication_subnet_group_description(self) -> builtins.str:
        '''The description for the subnet group.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationsubnetgroup.html#cfn-dms-replicationsubnetgroup-replicationsubnetgroupdescription
        '''
        result = self._values.get("replication_subnet_group_description")
        assert result is not None, "Required property 'replication_subnet_group_description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subnet_ids(self) -> typing.List[builtins.str]:
        '''One or more subnet IDs to be assigned to the subnet group.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationsubnetgroup.html#cfn-dms-replicationsubnetgroup-subnetids
        '''
        result = self._values.get("subnet_ids")
        assert result is not None, "Required property 'subnet_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def replication_subnet_group_identifier(self) -> typing.Optional[builtins.str]:
        '''The identifier for the replication subnet group.

        If you don't specify a name, AWS CloudFormation generates a unique ID and uses that ID for the identifier.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationsubnetgroup.html#cfn-dms-replicationsubnetgroup-replicationsubnetgroupidentifier
        '''
        result = self._values.get("replication_subnet_group_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''One or more tags to be assigned to the subnet group.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationsubnetgroup.html#cfn-dms-replicationsubnetgroup-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnReplicationSubnetGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnReplicationTask(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_dms.CfnReplicationTask",
):
    '''A CloudFormation ``AWS::DMS::ReplicationTask``.

    The ``AWS::DMS::ReplicationTask`` resource creates an AWS DMS replication task.

    :cloudformationResource: AWS::DMS::ReplicationTask
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_dms as dms
        
        cfn_replication_task = dms.CfnReplicationTask(self, "MyCfnReplicationTask",
            migration_type="migrationType",
            replication_instance_arn="replicationInstanceArn",
            source_endpoint_arn="sourceEndpointArn",
            table_mappings="tableMappings",
            target_endpoint_arn="targetEndpointArn",
        
            # the properties below are optional
            cdc_start_position="cdcStartPosition",
            cdc_start_time=123,
            cdc_stop_position="cdcStopPosition",
            replication_task_identifier="replicationTaskIdentifier",
            replication_task_settings="replicationTaskSettings",
            resource_identifier="resourceIdentifier",
            tags=[CfnTag(
                key="key",
                value="value"
            )],
            task_data="taskData"
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        migration_type: builtins.str,
        replication_instance_arn: builtins.str,
        source_endpoint_arn: builtins.str,
        table_mappings: builtins.str,
        target_endpoint_arn: builtins.str,
        cdc_start_position: typing.Optional[builtins.str] = None,
        cdc_start_time: typing.Optional[jsii.Number] = None,
        cdc_stop_position: typing.Optional[builtins.str] = None,
        replication_task_identifier: typing.Optional[builtins.str] = None,
        replication_task_settings: typing.Optional[builtins.str] = None,
        resource_identifier: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        task_data: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AWS::DMS::ReplicationTask``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param migration_type: The migration type. Valid values: ``full-load`` | ``cdc`` | ``full-load-and-cdc``
        :param replication_instance_arn: The Amazon Resource Name (ARN) of a replication instance.
        :param source_endpoint_arn: An Amazon Resource Name (ARN) that uniquely identifies the source endpoint.
        :param table_mappings: The table mappings for the task, in JSON format. For more information, see `Using Table Mapping to Specify Task Settings <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Tasks.CustomizingTasks.TableMapping.html>`_ in the *AWS Database Migration Service User Guide.*
        :param target_endpoint_arn: An Amazon Resource Name (ARN) that uniquely identifies the target endpoint.
        :param cdc_start_position: Indicates when you want a change data capture (CDC) operation to start. Use either CdcStartPosition or CdcStartTime to specify when you want a CDC operation to start. Specifying both values results in an error. The value can be in date, checkpoint, or LSN/SCN format. Date Example: --cdc-start-position “2018-03-08T12:12:12” Checkpoint Example: --cdc-start-position "checkpoint:V1#27#mysql-bin-changelog.157832:1975:-1:2002:677883278264080:mysql-bin-changelog.157832:1876#0#0#*#0#93" LSN Example: --cdc-start-position “mysql-bin-changelog.000024:373” .. epigraph:: When you use this task setting with a source PostgreSQL database, a logical replication slot should already be created and associated with the source endpoint. You can verify this by setting the ``slotName`` extra connection attribute to the name of this logical replication slot. For more information, see `Extra Connection Attributes When Using PostgreSQL as a Source for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Source.PostgreSQL.html#CHAP_Source.PostgreSQL.ConnectionAttrib>`_ .
        :param cdc_start_time: Indicates the start time for a change data capture (CDC) operation.
        :param cdc_stop_position: Indicates when you want a change data capture (CDC) operation to stop. The value can be either server time or commit time. Server time example: --cdc-stop-position “server_time:2018-02-09T12:12:12” Commit time example: --cdc-stop-position “commit_time: 2018-02-09T12:12:12 “
        :param replication_task_identifier: An identifier for the replication task. Constraints: - Must contain 1-255 alphanumeric characters or hyphens. - First character must be a letter. - Cannot end with a hyphen or contain two consecutive hyphens.
        :param replication_task_settings: Overall settings for the task, in JSON format. For more information, see `Specifying Task Settings for AWS Database Migration Service Tasks <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Tasks.CustomizingTasks.TaskSettings.html>`_ in the *AWS Database Migration Service User Guide.*
        :param resource_identifier: A friendly name for the resource identifier at the end of the ``EndpointArn`` response parameter that is returned in the created ``Endpoint`` object. The value for this parameter can have up to 31 characters. It can contain only ASCII letters, digits, and hyphen ('-'). Also, it can't end with a hyphen or contain two consecutive hyphens, and can only begin with a letter, such as ``Example-App-ARN1`` . For example, this value might result in the ``EndpointArn`` value ``arn:aws:dms:eu-west-1:012345678901:rep:Example-App-ARN1`` . If you don't specify a ``ResourceIdentifier`` value, AWS DMS generates a default identifier value for the end of ``EndpointArn`` .
        :param tags: One or more tags to be assigned to the replication task.
        :param task_data: ``AWS::DMS::ReplicationTask.TaskData``.
        '''
        props = CfnReplicationTaskProps(
            migration_type=migration_type,
            replication_instance_arn=replication_instance_arn,
            source_endpoint_arn=source_endpoint_arn,
            table_mappings=table_mappings,
            target_endpoint_arn=target_endpoint_arn,
            cdc_start_position=cdc_start_position,
            cdc_start_time=cdc_start_time,
            cdc_stop_position=cdc_stop_position,
            replication_task_identifier=replication_task_identifier,
            replication_task_settings=replication_task_settings,
            resource_identifier=resource_identifier,
            tags=tags,
            task_data=task_data,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _TreeInspector_488e0dd5) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''One or more tags to be assigned to the replication task.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="migrationType")
    def migration_type(self) -> builtins.str:
        '''The migration type.

        Valid values: ``full-load`` | ``cdc`` | ``full-load-and-cdc``

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-migrationtype
        '''
        return typing.cast(builtins.str, jsii.get(self, "migrationType"))

    @migration_type.setter
    def migration_type(self, value: builtins.str) -> None:
        jsii.set(self, "migrationType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationInstanceArn")
    def replication_instance_arn(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of a replication instance.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-replicationinstancearn
        '''
        return typing.cast(builtins.str, jsii.get(self, "replicationInstanceArn"))

    @replication_instance_arn.setter
    def replication_instance_arn(self, value: builtins.str) -> None:
        jsii.set(self, "replicationInstanceArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceEndpointArn")
    def source_endpoint_arn(self) -> builtins.str:
        '''An Amazon Resource Name (ARN) that uniquely identifies the source endpoint.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-sourceendpointarn
        '''
        return typing.cast(builtins.str, jsii.get(self, "sourceEndpointArn"))

    @source_endpoint_arn.setter
    def source_endpoint_arn(self, value: builtins.str) -> None:
        jsii.set(self, "sourceEndpointArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tableMappings")
    def table_mappings(self) -> builtins.str:
        '''The table mappings for the task, in JSON format.

        For more information, see `Using Table Mapping to Specify Task Settings <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Tasks.CustomizingTasks.TableMapping.html>`_ in the *AWS Database Migration Service User Guide.*

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-tablemappings
        '''
        return typing.cast(builtins.str, jsii.get(self, "tableMappings"))

    @table_mappings.setter
    def table_mappings(self, value: builtins.str) -> None:
        jsii.set(self, "tableMappings", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetEndpointArn")
    def target_endpoint_arn(self) -> builtins.str:
        '''An Amazon Resource Name (ARN) that uniquely identifies the target endpoint.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-targetendpointarn
        '''
        return typing.cast(builtins.str, jsii.get(self, "targetEndpointArn"))

    @target_endpoint_arn.setter
    def target_endpoint_arn(self, value: builtins.str) -> None:
        jsii.set(self, "targetEndpointArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cdcStartPosition")
    def cdc_start_position(self) -> typing.Optional[builtins.str]:
        '''Indicates when you want a change data capture (CDC) operation to start.

        Use either CdcStartPosition or CdcStartTime to specify when you want a CDC operation to start. Specifying both values results in an error.

        The value can be in date, checkpoint, or LSN/SCN format.

        Date Example: --cdc-start-position “2018-03-08T12:12:12”

        Checkpoint Example: --cdc-start-position "checkpoint:V1#27#mysql-bin-changelog.157832:1975:-1:2002:677883278264080:mysql-bin-changelog.157832:1876#0#0#*#0#93"

        LSN Example: --cdc-start-position “mysql-bin-changelog.000024:373”
        .. epigraph::

           When you use this task setting with a source PostgreSQL database, a logical replication slot should already be created and associated with the source endpoint. You can verify this by setting the ``slotName`` extra connection attribute to the name of this logical replication slot. For more information, see `Extra Connection Attributes When Using PostgreSQL as a Source for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Source.PostgreSQL.html#CHAP_Source.PostgreSQL.ConnectionAttrib>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-cdcstartposition
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cdcStartPosition"))

    @cdc_start_position.setter
    def cdc_start_position(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "cdcStartPosition", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cdcStartTime")
    def cdc_start_time(self) -> typing.Optional[jsii.Number]:
        '''Indicates the start time for a change data capture (CDC) operation.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-cdcstarttime
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cdcStartTime"))

    @cdc_start_time.setter
    def cdc_start_time(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "cdcStartTime", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cdcStopPosition")
    def cdc_stop_position(self) -> typing.Optional[builtins.str]:
        '''Indicates when you want a change data capture (CDC) operation to stop.

        The value can be either server time or commit time.

        Server time example: --cdc-stop-position “server_time:2018-02-09T12:12:12”

        Commit time example: --cdc-stop-position “commit_time: 2018-02-09T12:12:12 “

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-cdcstopposition
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cdcStopPosition"))

    @cdc_stop_position.setter
    def cdc_stop_position(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "cdcStopPosition", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationTaskIdentifier")
    def replication_task_identifier(self) -> typing.Optional[builtins.str]:
        '''An identifier for the replication task.

        Constraints:

        - Must contain 1-255 alphanumeric characters or hyphens.
        - First character must be a letter.
        - Cannot end with a hyphen or contain two consecutive hyphens.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-replicationtaskidentifier
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "replicationTaskIdentifier"))

    @replication_task_identifier.setter
    def replication_task_identifier(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "replicationTaskIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationTaskSettings")
    def replication_task_settings(self) -> typing.Optional[builtins.str]:
        '''Overall settings for the task, in JSON format.

        For more information, see `Specifying Task Settings for AWS Database Migration Service Tasks <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Tasks.CustomizingTasks.TaskSettings.html>`_ in the *AWS Database Migration Service User Guide.*

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-replicationtasksettings
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "replicationTaskSettings"))

    @replication_task_settings.setter
    def replication_task_settings(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "replicationTaskSettings", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceIdentifier")
    def resource_identifier(self) -> typing.Optional[builtins.str]:
        '''A friendly name for the resource identifier at the end of the ``EndpointArn`` response parameter that is returned in the created ``Endpoint`` object.

        The value for this parameter can have up to 31 characters. It can contain only ASCII letters, digits, and hyphen ('-'). Also, it can't end with a hyphen or contain two consecutive hyphens, and can only begin with a letter, such as ``Example-App-ARN1`` . For example, this value might result in the ``EndpointArn`` value ``arn:aws:dms:eu-west-1:012345678901:rep:Example-App-ARN1`` . If you don't specify a ``ResourceIdentifier`` value, AWS DMS generates a default identifier value for the end of ``EndpointArn`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-resourceidentifier
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceIdentifier"))

    @resource_identifier.setter
    def resource_identifier(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "resourceIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="taskData")
    def task_data(self) -> typing.Optional[builtins.str]:
        '''``AWS::DMS::ReplicationTask.TaskData``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-taskdata
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "taskData"))

    @task_data.setter
    def task_data(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "taskData", value)


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_dms.CfnReplicationTaskProps",
    jsii_struct_bases=[],
    name_mapping={
        "migration_type": "migrationType",
        "replication_instance_arn": "replicationInstanceArn",
        "source_endpoint_arn": "sourceEndpointArn",
        "table_mappings": "tableMappings",
        "target_endpoint_arn": "targetEndpointArn",
        "cdc_start_position": "cdcStartPosition",
        "cdc_start_time": "cdcStartTime",
        "cdc_stop_position": "cdcStopPosition",
        "replication_task_identifier": "replicationTaskIdentifier",
        "replication_task_settings": "replicationTaskSettings",
        "resource_identifier": "resourceIdentifier",
        "tags": "tags",
        "task_data": "taskData",
    },
)
class CfnReplicationTaskProps:
    def __init__(
        self,
        *,
        migration_type: builtins.str,
        replication_instance_arn: builtins.str,
        source_endpoint_arn: builtins.str,
        table_mappings: builtins.str,
        target_endpoint_arn: builtins.str,
        cdc_start_position: typing.Optional[builtins.str] = None,
        cdc_start_time: typing.Optional[jsii.Number] = None,
        cdc_stop_position: typing.Optional[builtins.str] = None,
        replication_task_identifier: typing.Optional[builtins.str] = None,
        replication_task_settings: typing.Optional[builtins.str] = None,
        resource_identifier: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        task_data: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a ``CfnReplicationTask``.

        :param migration_type: The migration type. Valid values: ``full-load`` | ``cdc`` | ``full-load-and-cdc``
        :param replication_instance_arn: The Amazon Resource Name (ARN) of a replication instance.
        :param source_endpoint_arn: An Amazon Resource Name (ARN) that uniquely identifies the source endpoint.
        :param table_mappings: The table mappings for the task, in JSON format. For more information, see `Using Table Mapping to Specify Task Settings <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Tasks.CustomizingTasks.TableMapping.html>`_ in the *AWS Database Migration Service User Guide.*
        :param target_endpoint_arn: An Amazon Resource Name (ARN) that uniquely identifies the target endpoint.
        :param cdc_start_position: Indicates when you want a change data capture (CDC) operation to start. Use either CdcStartPosition or CdcStartTime to specify when you want a CDC operation to start. Specifying both values results in an error. The value can be in date, checkpoint, or LSN/SCN format. Date Example: --cdc-start-position “2018-03-08T12:12:12” Checkpoint Example: --cdc-start-position "checkpoint:V1#27#mysql-bin-changelog.157832:1975:-1:2002:677883278264080:mysql-bin-changelog.157832:1876#0#0#*#0#93" LSN Example: --cdc-start-position “mysql-bin-changelog.000024:373” .. epigraph:: When you use this task setting with a source PostgreSQL database, a logical replication slot should already be created and associated with the source endpoint. You can verify this by setting the ``slotName`` extra connection attribute to the name of this logical replication slot. For more information, see `Extra Connection Attributes When Using PostgreSQL as a Source for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Source.PostgreSQL.html#CHAP_Source.PostgreSQL.ConnectionAttrib>`_ .
        :param cdc_start_time: Indicates the start time for a change data capture (CDC) operation.
        :param cdc_stop_position: Indicates when you want a change data capture (CDC) operation to stop. The value can be either server time or commit time. Server time example: --cdc-stop-position “server_time:2018-02-09T12:12:12” Commit time example: --cdc-stop-position “commit_time: 2018-02-09T12:12:12 “
        :param replication_task_identifier: An identifier for the replication task. Constraints: - Must contain 1-255 alphanumeric characters or hyphens. - First character must be a letter. - Cannot end with a hyphen or contain two consecutive hyphens.
        :param replication_task_settings: Overall settings for the task, in JSON format. For more information, see `Specifying Task Settings for AWS Database Migration Service Tasks <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Tasks.CustomizingTasks.TaskSettings.html>`_ in the *AWS Database Migration Service User Guide.*
        :param resource_identifier: A friendly name for the resource identifier at the end of the ``EndpointArn`` response parameter that is returned in the created ``Endpoint`` object. The value for this parameter can have up to 31 characters. It can contain only ASCII letters, digits, and hyphen ('-'). Also, it can't end with a hyphen or contain two consecutive hyphens, and can only begin with a letter, such as ``Example-App-ARN1`` . For example, this value might result in the ``EndpointArn`` value ``arn:aws:dms:eu-west-1:012345678901:rep:Example-App-ARN1`` . If you don't specify a ``ResourceIdentifier`` value, AWS DMS generates a default identifier value for the end of ``EndpointArn`` .
        :param tags: One or more tags to be assigned to the replication task.
        :param task_data: ``AWS::DMS::ReplicationTask.TaskData``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_dms as dms
            
            cfn_replication_task_props = dms.CfnReplicationTaskProps(
                migration_type="migrationType",
                replication_instance_arn="replicationInstanceArn",
                source_endpoint_arn="sourceEndpointArn",
                table_mappings="tableMappings",
                target_endpoint_arn="targetEndpointArn",
            
                # the properties below are optional
                cdc_start_position="cdcStartPosition",
                cdc_start_time=123,
                cdc_stop_position="cdcStopPosition",
                replication_task_identifier="replicationTaskIdentifier",
                replication_task_settings="replicationTaskSettings",
                resource_identifier="resourceIdentifier",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )],
                task_data="taskData"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "migration_type": migration_type,
            "replication_instance_arn": replication_instance_arn,
            "source_endpoint_arn": source_endpoint_arn,
            "table_mappings": table_mappings,
            "target_endpoint_arn": target_endpoint_arn,
        }
        if cdc_start_position is not None:
            self._values["cdc_start_position"] = cdc_start_position
        if cdc_start_time is not None:
            self._values["cdc_start_time"] = cdc_start_time
        if cdc_stop_position is not None:
            self._values["cdc_stop_position"] = cdc_stop_position
        if replication_task_identifier is not None:
            self._values["replication_task_identifier"] = replication_task_identifier
        if replication_task_settings is not None:
            self._values["replication_task_settings"] = replication_task_settings
        if resource_identifier is not None:
            self._values["resource_identifier"] = resource_identifier
        if tags is not None:
            self._values["tags"] = tags
        if task_data is not None:
            self._values["task_data"] = task_data

    @builtins.property
    def migration_type(self) -> builtins.str:
        '''The migration type.

        Valid values: ``full-load`` | ``cdc`` | ``full-load-and-cdc``

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-migrationtype
        '''
        result = self._values.get("migration_type")
        assert result is not None, "Required property 'migration_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def replication_instance_arn(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of a replication instance.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-replicationinstancearn
        '''
        result = self._values.get("replication_instance_arn")
        assert result is not None, "Required property 'replication_instance_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def source_endpoint_arn(self) -> builtins.str:
        '''An Amazon Resource Name (ARN) that uniquely identifies the source endpoint.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-sourceendpointarn
        '''
        result = self._values.get("source_endpoint_arn")
        assert result is not None, "Required property 'source_endpoint_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def table_mappings(self) -> builtins.str:
        '''The table mappings for the task, in JSON format.

        For more information, see `Using Table Mapping to Specify Task Settings <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Tasks.CustomizingTasks.TableMapping.html>`_ in the *AWS Database Migration Service User Guide.*

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-tablemappings
        '''
        result = self._values.get("table_mappings")
        assert result is not None, "Required property 'table_mappings' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_endpoint_arn(self) -> builtins.str:
        '''An Amazon Resource Name (ARN) that uniquely identifies the target endpoint.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-targetendpointarn
        '''
        result = self._values.get("target_endpoint_arn")
        assert result is not None, "Required property 'target_endpoint_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cdc_start_position(self) -> typing.Optional[builtins.str]:
        '''Indicates when you want a change data capture (CDC) operation to start.

        Use either CdcStartPosition or CdcStartTime to specify when you want a CDC operation to start. Specifying both values results in an error.

        The value can be in date, checkpoint, or LSN/SCN format.

        Date Example: --cdc-start-position “2018-03-08T12:12:12”

        Checkpoint Example: --cdc-start-position "checkpoint:V1#27#mysql-bin-changelog.157832:1975:-1:2002:677883278264080:mysql-bin-changelog.157832:1876#0#0#*#0#93"

        LSN Example: --cdc-start-position “mysql-bin-changelog.000024:373”
        .. epigraph::

           When you use this task setting with a source PostgreSQL database, a logical replication slot should already be created and associated with the source endpoint. You can verify this by setting the ``slotName`` extra connection attribute to the name of this logical replication slot. For more information, see `Extra Connection Attributes When Using PostgreSQL as a Source for AWS DMS <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Source.PostgreSQL.html#CHAP_Source.PostgreSQL.ConnectionAttrib>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-cdcstartposition
        '''
        result = self._values.get("cdc_start_position")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cdc_start_time(self) -> typing.Optional[jsii.Number]:
        '''Indicates the start time for a change data capture (CDC) operation.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-cdcstarttime
        '''
        result = self._values.get("cdc_start_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cdc_stop_position(self) -> typing.Optional[builtins.str]:
        '''Indicates when you want a change data capture (CDC) operation to stop.

        The value can be either server time or commit time.

        Server time example: --cdc-stop-position “server_time:2018-02-09T12:12:12”

        Commit time example: --cdc-stop-position “commit_time: 2018-02-09T12:12:12 “

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-cdcstopposition
        '''
        result = self._values.get("cdc_stop_position")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def replication_task_identifier(self) -> typing.Optional[builtins.str]:
        '''An identifier for the replication task.

        Constraints:

        - Must contain 1-255 alphanumeric characters or hyphens.
        - First character must be a letter.
        - Cannot end with a hyphen or contain two consecutive hyphens.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-replicationtaskidentifier
        '''
        result = self._values.get("replication_task_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def replication_task_settings(self) -> typing.Optional[builtins.str]:
        '''Overall settings for the task, in JSON format.

        For more information, see `Specifying Task Settings for AWS Database Migration Service Tasks <https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Tasks.CustomizingTasks.TaskSettings.html>`_ in the *AWS Database Migration Service User Guide.*

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-replicationtasksettings
        '''
        result = self._values.get("replication_task_settings")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource_identifier(self) -> typing.Optional[builtins.str]:
        '''A friendly name for the resource identifier at the end of the ``EndpointArn`` response parameter that is returned in the created ``Endpoint`` object.

        The value for this parameter can have up to 31 characters. It can contain only ASCII letters, digits, and hyphen ('-'). Also, it can't end with a hyphen or contain two consecutive hyphens, and can only begin with a letter, such as ``Example-App-ARN1`` . For example, this value might result in the ``EndpointArn`` value ``arn:aws:dms:eu-west-1:012345678901:rep:Example-App-ARN1`` . If you don't specify a ``ResourceIdentifier`` value, AWS DMS generates a default identifier value for the end of ``EndpointArn`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-resourceidentifier
        '''
        result = self._values.get("resource_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''One or more tags to be assigned to the replication task.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    @builtins.property
    def task_data(self) -> typing.Optional[builtins.str]:
        '''``AWS::DMS::ReplicationTask.TaskData``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dms-replicationtask.html#cfn-dms-replicationtask-taskdata
        '''
        result = self._values.get("task_data")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnReplicationTaskProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnCertificate",
    "CfnCertificateProps",
    "CfnEndpoint",
    "CfnEndpointProps",
    "CfnEventSubscription",
    "CfnEventSubscriptionProps",
    "CfnReplicationInstance",
    "CfnReplicationInstanceProps",
    "CfnReplicationSubnetGroup",
    "CfnReplicationSubnetGroupProps",
    "CfnReplicationTask",
    "CfnReplicationTaskProps",
]

publication.publish()
