import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

import cdktf
import constructs


class DmsCertificate(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dms.DmsCertificate",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/dms_certificate aws_dms_certificate}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        certificate_id: builtins.str,
        certificate_pem: typing.Optional[builtins.str] = None,
        certificate_wallet: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/dms_certificate aws_dms_certificate} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param certificate_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_certificate#certificate_id DmsCertificate#certificate_id}.
        :param certificate_pem: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_certificate#certificate_pem DmsCertificate#certificate_pem}.
        :param certificate_wallet: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_certificate#certificate_wallet DmsCertificate#certificate_wallet}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_certificate#tags DmsCertificate#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_certificate#tags_all DmsCertificate#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DmsCertificateConfig(
            certificate_id=certificate_id,
            certificate_pem=certificate_pem,
            certificate_wallet=certificate_wallet,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetCertificatePem")
    def reset_certificate_pem(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificatePem", []))

    @jsii.member(jsii_name="resetCertificateWallet")
    def reset_certificate_wallet(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateWallet", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateArn")
    def certificate_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateIdInput")
    def certificate_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificatePemInput")
    def certificate_pem_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificatePemInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateWalletInput")
    def certificate_wallet_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateWalletInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateId")
    def certificate_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateId"))

    @certificate_id.setter
    def certificate_id(self, value: builtins.str) -> None:
        jsii.set(self, "certificateId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificatePem")
    def certificate_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificatePem"))

    @certificate_pem.setter
    def certificate_pem(self, value: builtins.str) -> None:
        jsii.set(self, "certificatePem", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateWallet")
    def certificate_wallet(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateWallet"))

    @certificate_wallet.setter
    def certificate_wallet(self, value: builtins.str) -> None:
        jsii.set(self, "certificateWallet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tags"))

    @tags.setter
    def tags(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tagsAll", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dms.DmsCertificateConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "certificate_id": "certificateId",
        "certificate_pem": "certificatePem",
        "certificate_wallet": "certificateWallet",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class DmsCertificateConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        certificate_id: builtins.str,
        certificate_pem: typing.Optional[builtins.str] = None,
        certificate_wallet: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Database Migration Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param certificate_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_certificate#certificate_id DmsCertificate#certificate_id}.
        :param certificate_pem: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_certificate#certificate_pem DmsCertificate#certificate_pem}.
        :param certificate_wallet: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_certificate#certificate_wallet DmsCertificate#certificate_wallet}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_certificate#tags DmsCertificate#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_certificate#tags_all DmsCertificate#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "certificate_id": certificate_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if certificate_pem is not None:
            self._values["certificate_pem"] = certificate_pem
        if certificate_wallet is not None:
            self._values["certificate_wallet"] = certificate_wallet
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def certificate_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_certificate#certificate_id DmsCertificate#certificate_id}.'''
        result = self._values.get("certificate_id")
        assert result is not None, "Required property 'certificate_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def certificate_pem(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_certificate#certificate_pem DmsCertificate#certificate_pem}.'''
        result = self._values.get("certificate_pem")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_wallet(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_certificate#certificate_wallet DmsCertificate#certificate_wallet}.'''
        result = self._values.get("certificate_wallet")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_certificate#tags DmsCertificate#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_certificate#tags_all DmsCertificate#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DmsCertificateConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DmsEndpoint(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dms.DmsEndpoint",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint aws_dms_endpoint}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        endpoint_id: builtins.str,
        endpoint_type: builtins.str,
        engine_name: builtins.str,
        certificate_arn: typing.Optional[builtins.str] = None,
        database_name: typing.Optional[builtins.str] = None,
        elasticsearch_settings: typing.Optional["DmsEndpointElasticsearchSettings"] = None,
        extra_connection_attributes: typing.Optional[builtins.str] = None,
        kafka_settings: typing.Optional["DmsEndpointKafkaSettings"] = None,
        kinesis_settings: typing.Optional["DmsEndpointKinesisSettings"] = None,
        kms_key_arn: typing.Optional[builtins.str] = None,
        mongodb_settings: typing.Optional["DmsEndpointMongodbSettings"] = None,
        password: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        s3_settings: typing.Optional["DmsEndpointS3Settings"] = None,
        secrets_manager_access_role_arn: typing.Optional[builtins.str] = None,
        secrets_manager_arn: typing.Optional[builtins.str] = None,
        server_name: typing.Optional[builtins.str] = None,
        service_access_role: typing.Optional[builtins.str] = None,
        ssl_mode: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        username: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint aws_dms_endpoint} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param endpoint_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#endpoint_id DmsEndpoint#endpoint_id}.
        :param endpoint_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#endpoint_type DmsEndpoint#endpoint_type}.
        :param engine_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#engine_name DmsEndpoint#engine_name}.
        :param certificate_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#certificate_arn DmsEndpoint#certificate_arn}.
        :param database_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#database_name DmsEndpoint#database_name}.
        :param elasticsearch_settings: elasticsearch_settings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#elasticsearch_settings DmsEndpoint#elasticsearch_settings}
        :param extra_connection_attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#extra_connection_attributes DmsEndpoint#extra_connection_attributes}.
        :param kafka_settings: kafka_settings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#kafka_settings DmsEndpoint#kafka_settings}
        :param kinesis_settings: kinesis_settings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#kinesis_settings DmsEndpoint#kinesis_settings}
        :param kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#kms_key_arn DmsEndpoint#kms_key_arn}.
        :param mongodb_settings: mongodb_settings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#mongodb_settings DmsEndpoint#mongodb_settings}
        :param password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#password DmsEndpoint#password}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#port DmsEndpoint#port}.
        :param s3_settings: s3_settings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#s3_settings DmsEndpoint#s3_settings}
        :param secrets_manager_access_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#secrets_manager_access_role_arn DmsEndpoint#secrets_manager_access_role_arn}.
        :param secrets_manager_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#secrets_manager_arn DmsEndpoint#secrets_manager_arn}.
        :param server_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#server_name DmsEndpoint#server_name}.
        :param service_access_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#service_access_role DmsEndpoint#service_access_role}.
        :param ssl_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#ssl_mode DmsEndpoint#ssl_mode}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#tags DmsEndpoint#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#tags_all DmsEndpoint#tags_all}.
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#username DmsEndpoint#username}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DmsEndpointConfig(
            endpoint_id=endpoint_id,
            endpoint_type=endpoint_type,
            engine_name=engine_name,
            certificate_arn=certificate_arn,
            database_name=database_name,
            elasticsearch_settings=elasticsearch_settings,
            extra_connection_attributes=extra_connection_attributes,
            kafka_settings=kafka_settings,
            kinesis_settings=kinesis_settings,
            kms_key_arn=kms_key_arn,
            mongodb_settings=mongodb_settings,
            password=password,
            port=port,
            s3_settings=s3_settings,
            secrets_manager_access_role_arn=secrets_manager_access_role_arn,
            secrets_manager_arn=secrets_manager_arn,
            server_name=server_name,
            service_access_role=service_access_role,
            ssl_mode=ssl_mode,
            tags=tags,
            tags_all=tags_all,
            username=username,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putElasticsearchSettings")
    def put_elasticsearch_settings(
        self,
        *,
        endpoint_uri: builtins.str,
        service_access_role_arn: builtins.str,
        error_retry_duration: typing.Optional[jsii.Number] = None,
        full_load_error_percentage: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param endpoint_uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#endpoint_uri DmsEndpoint#endpoint_uri}.
        :param service_access_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#service_access_role_arn DmsEndpoint#service_access_role_arn}.
        :param error_retry_duration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#error_retry_duration DmsEndpoint#error_retry_duration}.
        :param full_load_error_percentage: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#full_load_error_percentage DmsEndpoint#full_load_error_percentage}.
        '''
        value = DmsEndpointElasticsearchSettings(
            endpoint_uri=endpoint_uri,
            service_access_role_arn=service_access_role_arn,
            error_retry_duration=error_retry_duration,
            full_load_error_percentage=full_load_error_percentage,
        )

        return typing.cast(None, jsii.invoke(self, "putElasticsearchSettings", [value]))

    @jsii.member(jsii_name="putKafkaSettings")
    def put_kafka_settings(
        self,
        *,
        broker: builtins.str,
        include_control_details: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_null_and_empty: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_partition_value: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_table_alter_operations: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_transaction_details: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        message_format: typing.Optional[builtins.str] = None,
        message_max_bytes: typing.Optional[jsii.Number] = None,
        no_hex_prefix: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        partition_include_schema_table: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        sasl_password: typing.Optional[builtins.str] = None,
        sasl_username: typing.Optional[builtins.str] = None,
        security_protocol: typing.Optional[builtins.str] = None,
        ssl_ca_certificate_arn: typing.Optional[builtins.str] = None,
        ssl_client_certificate_arn: typing.Optional[builtins.str] = None,
        ssl_client_key_arn: typing.Optional[builtins.str] = None,
        ssl_client_key_password: typing.Optional[builtins.str] = None,
        topic: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param broker: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#broker DmsEndpoint#broker}.
        :param include_control_details: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#include_control_details DmsEndpoint#include_control_details}.
        :param include_null_and_empty: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#include_null_and_empty DmsEndpoint#include_null_and_empty}.
        :param include_partition_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#include_partition_value DmsEndpoint#include_partition_value}.
        :param include_table_alter_operations: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#include_table_alter_operations DmsEndpoint#include_table_alter_operations}.
        :param include_transaction_details: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#include_transaction_details DmsEndpoint#include_transaction_details}.
        :param message_format: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#message_format DmsEndpoint#message_format}.
        :param message_max_bytes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#message_max_bytes DmsEndpoint#message_max_bytes}.
        :param no_hex_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#no_hex_prefix DmsEndpoint#no_hex_prefix}.
        :param partition_include_schema_table: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#partition_include_schema_table DmsEndpoint#partition_include_schema_table}.
        :param sasl_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#sasl_password DmsEndpoint#sasl_password}.
        :param sasl_username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#sasl_username DmsEndpoint#sasl_username}.
        :param security_protocol: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#security_protocol DmsEndpoint#security_protocol}.
        :param ssl_ca_certificate_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#ssl_ca_certificate_arn DmsEndpoint#ssl_ca_certificate_arn}.
        :param ssl_client_certificate_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#ssl_client_certificate_arn DmsEndpoint#ssl_client_certificate_arn}.
        :param ssl_client_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#ssl_client_key_arn DmsEndpoint#ssl_client_key_arn}.
        :param ssl_client_key_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#ssl_client_key_password DmsEndpoint#ssl_client_key_password}.
        :param topic: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#topic DmsEndpoint#topic}.
        '''
        value = DmsEndpointKafkaSettings(
            broker=broker,
            include_control_details=include_control_details,
            include_null_and_empty=include_null_and_empty,
            include_partition_value=include_partition_value,
            include_table_alter_operations=include_table_alter_operations,
            include_transaction_details=include_transaction_details,
            message_format=message_format,
            message_max_bytes=message_max_bytes,
            no_hex_prefix=no_hex_prefix,
            partition_include_schema_table=partition_include_schema_table,
            sasl_password=sasl_password,
            sasl_username=sasl_username,
            security_protocol=security_protocol,
            ssl_ca_certificate_arn=ssl_ca_certificate_arn,
            ssl_client_certificate_arn=ssl_client_certificate_arn,
            ssl_client_key_arn=ssl_client_key_arn,
            ssl_client_key_password=ssl_client_key_password,
            topic=topic,
        )

        return typing.cast(None, jsii.invoke(self, "putKafkaSettings", [value]))

    @jsii.member(jsii_name="putKinesisSettings")
    def put_kinesis_settings(
        self,
        *,
        include_control_details: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_null_and_empty: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_partition_value: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_table_alter_operations: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_transaction_details: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        message_format: typing.Optional[builtins.str] = None,
        partition_include_schema_table: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        service_access_role_arn: typing.Optional[builtins.str] = None,
        stream_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param include_control_details: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#include_control_details DmsEndpoint#include_control_details}.
        :param include_null_and_empty: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#include_null_and_empty DmsEndpoint#include_null_and_empty}.
        :param include_partition_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#include_partition_value DmsEndpoint#include_partition_value}.
        :param include_table_alter_operations: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#include_table_alter_operations DmsEndpoint#include_table_alter_operations}.
        :param include_transaction_details: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#include_transaction_details DmsEndpoint#include_transaction_details}.
        :param message_format: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#message_format DmsEndpoint#message_format}.
        :param partition_include_schema_table: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#partition_include_schema_table DmsEndpoint#partition_include_schema_table}.
        :param service_access_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#service_access_role_arn DmsEndpoint#service_access_role_arn}.
        :param stream_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#stream_arn DmsEndpoint#stream_arn}.
        '''
        value = DmsEndpointKinesisSettings(
            include_control_details=include_control_details,
            include_null_and_empty=include_null_and_empty,
            include_partition_value=include_partition_value,
            include_table_alter_operations=include_table_alter_operations,
            include_transaction_details=include_transaction_details,
            message_format=message_format,
            partition_include_schema_table=partition_include_schema_table,
            service_access_role_arn=service_access_role_arn,
            stream_arn=stream_arn,
        )

        return typing.cast(None, jsii.invoke(self, "putKinesisSettings", [value]))

    @jsii.member(jsii_name="putMongodbSettings")
    def put_mongodb_settings(
        self,
        *,
        auth_mechanism: typing.Optional[builtins.str] = None,
        auth_source: typing.Optional[builtins.str] = None,
        auth_type: typing.Optional[builtins.str] = None,
        docs_to_investigate: typing.Optional[builtins.str] = None,
        extract_doc_id: typing.Optional[builtins.str] = None,
        nesting_level: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param auth_mechanism: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#auth_mechanism DmsEndpoint#auth_mechanism}.
        :param auth_source: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#auth_source DmsEndpoint#auth_source}.
        :param auth_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#auth_type DmsEndpoint#auth_type}.
        :param docs_to_investigate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#docs_to_investigate DmsEndpoint#docs_to_investigate}.
        :param extract_doc_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#extract_doc_id DmsEndpoint#extract_doc_id}.
        :param nesting_level: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#nesting_level DmsEndpoint#nesting_level}.
        '''
        value = DmsEndpointMongodbSettings(
            auth_mechanism=auth_mechanism,
            auth_source=auth_source,
            auth_type=auth_type,
            docs_to_investigate=docs_to_investigate,
            extract_doc_id=extract_doc_id,
            nesting_level=nesting_level,
        )

        return typing.cast(None, jsii.invoke(self, "putMongodbSettings", [value]))

    @jsii.member(jsii_name="putS3Settings")
    def put_s3_settings(
        self,
        *,
        bucket_folder: typing.Optional[builtins.str] = None,
        bucket_name: typing.Optional[builtins.str] = None,
        compression_type: typing.Optional[builtins.str] = None,
        csv_delimiter: typing.Optional[builtins.str] = None,
        csv_row_delimiter: typing.Optional[builtins.str] = None,
        data_format: typing.Optional[builtins.str] = None,
        date_partition_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        encryption_mode: typing.Optional[builtins.str] = None,
        external_table_definition: typing.Optional[builtins.str] = None,
        parquet_timestamp_in_millisecond: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        parquet_version: typing.Optional[builtins.str] = None,
        server_side_encryption_kms_key_id: typing.Optional[builtins.str] = None,
        service_access_role_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket_folder: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#bucket_folder DmsEndpoint#bucket_folder}.
        :param bucket_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#bucket_name DmsEndpoint#bucket_name}.
        :param compression_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#compression_type DmsEndpoint#compression_type}.
        :param csv_delimiter: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#csv_delimiter DmsEndpoint#csv_delimiter}.
        :param csv_row_delimiter: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#csv_row_delimiter DmsEndpoint#csv_row_delimiter}.
        :param data_format: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#data_format DmsEndpoint#data_format}.
        :param date_partition_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#date_partition_enabled DmsEndpoint#date_partition_enabled}.
        :param encryption_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#encryption_mode DmsEndpoint#encryption_mode}.
        :param external_table_definition: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#external_table_definition DmsEndpoint#external_table_definition}.
        :param parquet_timestamp_in_millisecond: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#parquet_timestamp_in_millisecond DmsEndpoint#parquet_timestamp_in_millisecond}.
        :param parquet_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#parquet_version DmsEndpoint#parquet_version}.
        :param server_side_encryption_kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#server_side_encryption_kms_key_id DmsEndpoint#server_side_encryption_kms_key_id}.
        :param service_access_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#service_access_role_arn DmsEndpoint#service_access_role_arn}.
        '''
        value = DmsEndpointS3Settings(
            bucket_folder=bucket_folder,
            bucket_name=bucket_name,
            compression_type=compression_type,
            csv_delimiter=csv_delimiter,
            csv_row_delimiter=csv_row_delimiter,
            data_format=data_format,
            date_partition_enabled=date_partition_enabled,
            encryption_mode=encryption_mode,
            external_table_definition=external_table_definition,
            parquet_timestamp_in_millisecond=parquet_timestamp_in_millisecond,
            parquet_version=parquet_version,
            server_side_encryption_kms_key_id=server_side_encryption_kms_key_id,
            service_access_role_arn=service_access_role_arn,
        )

        return typing.cast(None, jsii.invoke(self, "putS3Settings", [value]))

    @jsii.member(jsii_name="resetCertificateArn")
    def reset_certificate_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateArn", []))

    @jsii.member(jsii_name="resetDatabaseName")
    def reset_database_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatabaseName", []))

    @jsii.member(jsii_name="resetElasticsearchSettings")
    def reset_elasticsearch_settings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetElasticsearchSettings", []))

    @jsii.member(jsii_name="resetExtraConnectionAttributes")
    def reset_extra_connection_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExtraConnectionAttributes", []))

    @jsii.member(jsii_name="resetKafkaSettings")
    def reset_kafka_settings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKafkaSettings", []))

    @jsii.member(jsii_name="resetKinesisSettings")
    def reset_kinesis_settings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKinesisSettings", []))

    @jsii.member(jsii_name="resetKmsKeyArn")
    def reset_kms_key_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyArn", []))

    @jsii.member(jsii_name="resetMongodbSettings")
    def reset_mongodb_settings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMongodbSettings", []))

    @jsii.member(jsii_name="resetPassword")
    def reset_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassword", []))

    @jsii.member(jsii_name="resetPort")
    def reset_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPort", []))

    @jsii.member(jsii_name="resetS3Settings")
    def reset_s3_settings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3Settings", []))

    @jsii.member(jsii_name="resetSecretsManagerAccessRoleArn")
    def reset_secrets_manager_access_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecretsManagerAccessRoleArn", []))

    @jsii.member(jsii_name="resetSecretsManagerArn")
    def reset_secrets_manager_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecretsManagerArn", []))

    @jsii.member(jsii_name="resetServerName")
    def reset_server_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServerName", []))

    @jsii.member(jsii_name="resetServiceAccessRole")
    def reset_service_access_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceAccessRole", []))

    @jsii.member(jsii_name="resetSslMode")
    def reset_ssl_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSslMode", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetUsername")
    def reset_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsername", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticsearchSettings")
    def elasticsearch_settings(
        self,
    ) -> "DmsEndpointElasticsearchSettingsOutputReference":
        return typing.cast("DmsEndpointElasticsearchSettingsOutputReference", jsii.get(self, "elasticsearchSettings"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointArn")
    def endpoint_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpointArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kafkaSettings")
    def kafka_settings(self) -> "DmsEndpointKafkaSettingsOutputReference":
        return typing.cast("DmsEndpointKafkaSettingsOutputReference", jsii.get(self, "kafkaSettings"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kinesisSettings")
    def kinesis_settings(self) -> "DmsEndpointKinesisSettingsOutputReference":
        return typing.cast("DmsEndpointKinesisSettingsOutputReference", jsii.get(self, "kinesisSettings"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mongodbSettings")
    def mongodb_settings(self) -> "DmsEndpointMongodbSettingsOutputReference":
        return typing.cast("DmsEndpointMongodbSettingsOutputReference", jsii.get(self, "mongodbSettings"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Settings")
    def s3_settings(self) -> "DmsEndpointS3SettingsOutputReference":
        return typing.cast("DmsEndpointS3SettingsOutputReference", jsii.get(self, "s3Settings"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateArnInput")
    def certificate_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseNameInput")
    def database_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticsearchSettingsInput")
    def elasticsearch_settings_input(
        self,
    ) -> typing.Optional["DmsEndpointElasticsearchSettings"]:
        return typing.cast(typing.Optional["DmsEndpointElasticsearchSettings"], jsii.get(self, "elasticsearchSettingsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointIdInput")
    def endpoint_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpointIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointTypeInput")
    def endpoint_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpointTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineNameInput")
    def engine_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "engineNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="extraConnectionAttributesInput")
    def extra_connection_attributes_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "extraConnectionAttributesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kafkaSettingsInput")
    def kafka_settings_input(self) -> typing.Optional["DmsEndpointKafkaSettings"]:
        return typing.cast(typing.Optional["DmsEndpointKafkaSettings"], jsii.get(self, "kafkaSettingsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kinesisSettingsInput")
    def kinesis_settings_input(self) -> typing.Optional["DmsEndpointKinesisSettings"]:
        return typing.cast(typing.Optional["DmsEndpointKinesisSettings"], jsii.get(self, "kinesisSettingsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyArnInput")
    def kms_key_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mongodbSettingsInput")
    def mongodb_settings_input(self) -> typing.Optional["DmsEndpointMongodbSettings"]:
        return typing.cast(typing.Optional["DmsEndpointMongodbSettings"], jsii.get(self, "mongodbSettingsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3SettingsInput")
    def s3_settings_input(self) -> typing.Optional["DmsEndpointS3Settings"]:
        return typing.cast(typing.Optional["DmsEndpointS3Settings"], jsii.get(self, "s3SettingsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretsManagerAccessRoleArnInput")
    def secrets_manager_access_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretsManagerAccessRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretsManagerArnInput")
    def secrets_manager_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretsManagerArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverNameInput")
    def server_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serverNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceAccessRoleInput")
    def service_access_role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceAccessRoleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sslModeInput")
    def ssl_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sslModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateArn")
    def certificate_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateArn"))

    @certificate_arn.setter
    def certificate_arn(self, value: builtins.str) -> None:
        jsii.set(self, "certificateArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "databaseName"))

    @database_name.setter
    def database_name(self, value: builtins.str) -> None:
        jsii.set(self, "databaseName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointId")
    def endpoint_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpointId"))

    @endpoint_id.setter
    def endpoint_id(self, value: builtins.str) -> None:
        jsii.set(self, "endpointId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointType")
    def endpoint_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpointType"))

    @endpoint_type.setter
    def endpoint_type(self, value: builtins.str) -> None:
        jsii.set(self, "endpointType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineName")
    def engine_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engineName"))

    @engine_name.setter
    def engine_name(self, value: builtins.str) -> None:
        jsii.set(self, "engineName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="extraConnectionAttributes")
    def extra_connection_attributes(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "extraConnectionAttributes"))

    @extra_connection_attributes.setter
    def extra_connection_attributes(self, value: builtins.str) -> None:
        jsii.set(self, "extraConnectionAttributes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyArn")
    def kms_key_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyArn"))

    @kms_key_arn.setter
    def kms_key_arn(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        jsii.set(self, "password", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        jsii.set(self, "port", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretsManagerAccessRoleArn")
    def secrets_manager_access_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretsManagerAccessRoleArn"))

    @secrets_manager_access_role_arn.setter
    def secrets_manager_access_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "secretsManagerAccessRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretsManagerArn")
    def secrets_manager_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretsManagerArn"))

    @secrets_manager_arn.setter
    def secrets_manager_arn(self, value: builtins.str) -> None:
        jsii.set(self, "secretsManagerArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverName")
    def server_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serverName"))

    @server_name.setter
    def server_name(self, value: builtins.str) -> None:
        jsii.set(self, "serverName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceAccessRole")
    def service_access_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceAccessRole"))

    @service_access_role.setter
    def service_access_role(self, value: builtins.str) -> None:
        jsii.set(self, "serviceAccessRole", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sslMode")
    def ssl_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sslMode"))

    @ssl_mode.setter
    def ssl_mode(self, value: builtins.str) -> None:
        jsii.set(self, "sslMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tags"))

    @tags.setter
    def tags(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tagsAll", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        jsii.set(self, "username", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dms.DmsEndpointConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "endpoint_id": "endpointId",
        "endpoint_type": "endpointType",
        "engine_name": "engineName",
        "certificate_arn": "certificateArn",
        "database_name": "databaseName",
        "elasticsearch_settings": "elasticsearchSettings",
        "extra_connection_attributes": "extraConnectionAttributes",
        "kafka_settings": "kafkaSettings",
        "kinesis_settings": "kinesisSettings",
        "kms_key_arn": "kmsKeyArn",
        "mongodb_settings": "mongodbSettings",
        "password": "password",
        "port": "port",
        "s3_settings": "s3Settings",
        "secrets_manager_access_role_arn": "secretsManagerAccessRoleArn",
        "secrets_manager_arn": "secretsManagerArn",
        "server_name": "serverName",
        "service_access_role": "serviceAccessRole",
        "ssl_mode": "sslMode",
        "tags": "tags",
        "tags_all": "tagsAll",
        "username": "username",
    },
)
class DmsEndpointConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        endpoint_id: builtins.str,
        endpoint_type: builtins.str,
        engine_name: builtins.str,
        certificate_arn: typing.Optional[builtins.str] = None,
        database_name: typing.Optional[builtins.str] = None,
        elasticsearch_settings: typing.Optional["DmsEndpointElasticsearchSettings"] = None,
        extra_connection_attributes: typing.Optional[builtins.str] = None,
        kafka_settings: typing.Optional["DmsEndpointKafkaSettings"] = None,
        kinesis_settings: typing.Optional["DmsEndpointKinesisSettings"] = None,
        kms_key_arn: typing.Optional[builtins.str] = None,
        mongodb_settings: typing.Optional["DmsEndpointMongodbSettings"] = None,
        password: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        s3_settings: typing.Optional["DmsEndpointS3Settings"] = None,
        secrets_manager_access_role_arn: typing.Optional[builtins.str] = None,
        secrets_manager_arn: typing.Optional[builtins.str] = None,
        server_name: typing.Optional[builtins.str] = None,
        service_access_role: typing.Optional[builtins.str] = None,
        ssl_mode: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Database Migration Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param endpoint_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#endpoint_id DmsEndpoint#endpoint_id}.
        :param endpoint_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#endpoint_type DmsEndpoint#endpoint_type}.
        :param engine_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#engine_name DmsEndpoint#engine_name}.
        :param certificate_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#certificate_arn DmsEndpoint#certificate_arn}.
        :param database_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#database_name DmsEndpoint#database_name}.
        :param elasticsearch_settings: elasticsearch_settings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#elasticsearch_settings DmsEndpoint#elasticsearch_settings}
        :param extra_connection_attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#extra_connection_attributes DmsEndpoint#extra_connection_attributes}.
        :param kafka_settings: kafka_settings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#kafka_settings DmsEndpoint#kafka_settings}
        :param kinesis_settings: kinesis_settings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#kinesis_settings DmsEndpoint#kinesis_settings}
        :param kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#kms_key_arn DmsEndpoint#kms_key_arn}.
        :param mongodb_settings: mongodb_settings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#mongodb_settings DmsEndpoint#mongodb_settings}
        :param password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#password DmsEndpoint#password}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#port DmsEndpoint#port}.
        :param s3_settings: s3_settings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#s3_settings DmsEndpoint#s3_settings}
        :param secrets_manager_access_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#secrets_manager_access_role_arn DmsEndpoint#secrets_manager_access_role_arn}.
        :param secrets_manager_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#secrets_manager_arn DmsEndpoint#secrets_manager_arn}.
        :param server_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#server_name DmsEndpoint#server_name}.
        :param service_access_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#service_access_role DmsEndpoint#service_access_role}.
        :param ssl_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#ssl_mode DmsEndpoint#ssl_mode}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#tags DmsEndpoint#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#tags_all DmsEndpoint#tags_all}.
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#username DmsEndpoint#username}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(elasticsearch_settings, dict):
            elasticsearch_settings = DmsEndpointElasticsearchSettings(**elasticsearch_settings)
        if isinstance(kafka_settings, dict):
            kafka_settings = DmsEndpointKafkaSettings(**kafka_settings)
        if isinstance(kinesis_settings, dict):
            kinesis_settings = DmsEndpointKinesisSettings(**kinesis_settings)
        if isinstance(mongodb_settings, dict):
            mongodb_settings = DmsEndpointMongodbSettings(**mongodb_settings)
        if isinstance(s3_settings, dict):
            s3_settings = DmsEndpointS3Settings(**s3_settings)
        self._values: typing.Dict[str, typing.Any] = {
            "endpoint_id": endpoint_id,
            "endpoint_type": endpoint_type,
            "engine_name": engine_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if certificate_arn is not None:
            self._values["certificate_arn"] = certificate_arn
        if database_name is not None:
            self._values["database_name"] = database_name
        if elasticsearch_settings is not None:
            self._values["elasticsearch_settings"] = elasticsearch_settings
        if extra_connection_attributes is not None:
            self._values["extra_connection_attributes"] = extra_connection_attributes
        if kafka_settings is not None:
            self._values["kafka_settings"] = kafka_settings
        if kinesis_settings is not None:
            self._values["kinesis_settings"] = kinesis_settings
        if kms_key_arn is not None:
            self._values["kms_key_arn"] = kms_key_arn
        if mongodb_settings is not None:
            self._values["mongodb_settings"] = mongodb_settings
        if password is not None:
            self._values["password"] = password
        if port is not None:
            self._values["port"] = port
        if s3_settings is not None:
            self._values["s3_settings"] = s3_settings
        if secrets_manager_access_role_arn is not None:
            self._values["secrets_manager_access_role_arn"] = secrets_manager_access_role_arn
        if secrets_manager_arn is not None:
            self._values["secrets_manager_arn"] = secrets_manager_arn
        if server_name is not None:
            self._values["server_name"] = server_name
        if service_access_role is not None:
            self._values["service_access_role"] = service_access_role
        if ssl_mode is not None:
            self._values["ssl_mode"] = ssl_mode
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if username is not None:
            self._values["username"] = username

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def endpoint_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#endpoint_id DmsEndpoint#endpoint_id}.'''
        result = self._values.get("endpoint_id")
        assert result is not None, "Required property 'endpoint_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def endpoint_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#endpoint_type DmsEndpoint#endpoint_type}.'''
        result = self._values.get("endpoint_type")
        assert result is not None, "Required property 'endpoint_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def engine_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#engine_name DmsEndpoint#engine_name}.'''
        result = self._values.get("engine_name")
        assert result is not None, "Required property 'engine_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def certificate_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#certificate_arn DmsEndpoint#certificate_arn}.'''
        result = self._values.get("certificate_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def database_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#database_name DmsEndpoint#database_name}.'''
        result = self._values.get("database_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def elasticsearch_settings(
        self,
    ) -> typing.Optional["DmsEndpointElasticsearchSettings"]:
        '''elasticsearch_settings block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#elasticsearch_settings DmsEndpoint#elasticsearch_settings}
        '''
        result = self._values.get("elasticsearch_settings")
        return typing.cast(typing.Optional["DmsEndpointElasticsearchSettings"], result)

    @builtins.property
    def extra_connection_attributes(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#extra_connection_attributes DmsEndpoint#extra_connection_attributes}.'''
        result = self._values.get("extra_connection_attributes")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kafka_settings(self) -> typing.Optional["DmsEndpointKafkaSettings"]:
        '''kafka_settings block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#kafka_settings DmsEndpoint#kafka_settings}
        '''
        result = self._values.get("kafka_settings")
        return typing.cast(typing.Optional["DmsEndpointKafkaSettings"], result)

    @builtins.property
    def kinesis_settings(self) -> typing.Optional["DmsEndpointKinesisSettings"]:
        '''kinesis_settings block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#kinesis_settings DmsEndpoint#kinesis_settings}
        '''
        result = self._values.get("kinesis_settings")
        return typing.cast(typing.Optional["DmsEndpointKinesisSettings"], result)

    @builtins.property
    def kms_key_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#kms_key_arn DmsEndpoint#kms_key_arn}.'''
        result = self._values.get("kms_key_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mongodb_settings(self) -> typing.Optional["DmsEndpointMongodbSettings"]:
        '''mongodb_settings block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#mongodb_settings DmsEndpoint#mongodb_settings}
        '''
        result = self._values.get("mongodb_settings")
        return typing.cast(typing.Optional["DmsEndpointMongodbSettings"], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#password DmsEndpoint#password}.'''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#port DmsEndpoint#port}.'''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def s3_settings(self) -> typing.Optional["DmsEndpointS3Settings"]:
        '''s3_settings block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#s3_settings DmsEndpoint#s3_settings}
        '''
        result = self._values.get("s3_settings")
        return typing.cast(typing.Optional["DmsEndpointS3Settings"], result)

    @builtins.property
    def secrets_manager_access_role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#secrets_manager_access_role_arn DmsEndpoint#secrets_manager_access_role_arn}.'''
        result = self._values.get("secrets_manager_access_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secrets_manager_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#secrets_manager_arn DmsEndpoint#secrets_manager_arn}.'''
        result = self._values.get("secrets_manager_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def server_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#server_name DmsEndpoint#server_name}.'''
        result = self._values.get("server_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service_access_role(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#service_access_role DmsEndpoint#service_access_role}.'''
        result = self._values.get("service_access_role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssl_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#ssl_mode DmsEndpoint#ssl_mode}.'''
        result = self._values.get("ssl_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#tags DmsEndpoint#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#tags_all DmsEndpoint#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#username DmsEndpoint#username}.'''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DmsEndpointConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dms.DmsEndpointElasticsearchSettings",
    jsii_struct_bases=[],
    name_mapping={
        "endpoint_uri": "endpointUri",
        "service_access_role_arn": "serviceAccessRoleArn",
        "error_retry_duration": "errorRetryDuration",
        "full_load_error_percentage": "fullLoadErrorPercentage",
    },
)
class DmsEndpointElasticsearchSettings:
    def __init__(
        self,
        *,
        endpoint_uri: builtins.str,
        service_access_role_arn: builtins.str,
        error_retry_duration: typing.Optional[jsii.Number] = None,
        full_load_error_percentage: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param endpoint_uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#endpoint_uri DmsEndpoint#endpoint_uri}.
        :param service_access_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#service_access_role_arn DmsEndpoint#service_access_role_arn}.
        :param error_retry_duration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#error_retry_duration DmsEndpoint#error_retry_duration}.
        :param full_load_error_percentage: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#full_load_error_percentage DmsEndpoint#full_load_error_percentage}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "endpoint_uri": endpoint_uri,
            "service_access_role_arn": service_access_role_arn,
        }
        if error_retry_duration is not None:
            self._values["error_retry_duration"] = error_retry_duration
        if full_load_error_percentage is not None:
            self._values["full_load_error_percentage"] = full_load_error_percentage

    @builtins.property
    def endpoint_uri(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#endpoint_uri DmsEndpoint#endpoint_uri}.'''
        result = self._values.get("endpoint_uri")
        assert result is not None, "Required property 'endpoint_uri' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def service_access_role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#service_access_role_arn DmsEndpoint#service_access_role_arn}.'''
        result = self._values.get("service_access_role_arn")
        assert result is not None, "Required property 'service_access_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def error_retry_duration(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#error_retry_duration DmsEndpoint#error_retry_duration}.'''
        result = self._values.get("error_retry_duration")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def full_load_error_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#full_load_error_percentage DmsEndpoint#full_load_error_percentage}.'''
        result = self._values.get("full_load_error_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DmsEndpointElasticsearchSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DmsEndpointElasticsearchSettingsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dms.DmsEndpointElasticsearchSettingsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetErrorRetryDuration")
    def reset_error_retry_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetErrorRetryDuration", []))

    @jsii.member(jsii_name="resetFullLoadErrorPercentage")
    def reset_full_load_error_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFullLoadErrorPercentage", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointUriInput")
    def endpoint_uri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpointUriInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="errorRetryDurationInput")
    def error_retry_duration_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "errorRetryDurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fullLoadErrorPercentageInput")
    def full_load_error_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "fullLoadErrorPercentageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceAccessRoleArnInput")
    def service_access_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceAccessRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointUri")
    def endpoint_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpointUri"))

    @endpoint_uri.setter
    def endpoint_uri(self, value: builtins.str) -> None:
        jsii.set(self, "endpointUri", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="errorRetryDuration")
    def error_retry_duration(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "errorRetryDuration"))

    @error_retry_duration.setter
    def error_retry_duration(self, value: jsii.Number) -> None:
        jsii.set(self, "errorRetryDuration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fullLoadErrorPercentage")
    def full_load_error_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "fullLoadErrorPercentage"))

    @full_load_error_percentage.setter
    def full_load_error_percentage(self, value: jsii.Number) -> None:
        jsii.set(self, "fullLoadErrorPercentage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceAccessRoleArn")
    def service_access_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceAccessRoleArn"))

    @service_access_role_arn.setter
    def service_access_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "serviceAccessRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DmsEndpointElasticsearchSettings]:
        return typing.cast(typing.Optional[DmsEndpointElasticsearchSettings], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DmsEndpointElasticsearchSettings],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dms.DmsEndpointKafkaSettings",
    jsii_struct_bases=[],
    name_mapping={
        "broker": "broker",
        "include_control_details": "includeControlDetails",
        "include_null_and_empty": "includeNullAndEmpty",
        "include_partition_value": "includePartitionValue",
        "include_table_alter_operations": "includeTableAlterOperations",
        "include_transaction_details": "includeTransactionDetails",
        "message_format": "messageFormat",
        "message_max_bytes": "messageMaxBytes",
        "no_hex_prefix": "noHexPrefix",
        "partition_include_schema_table": "partitionIncludeSchemaTable",
        "sasl_password": "saslPassword",
        "sasl_username": "saslUsername",
        "security_protocol": "securityProtocol",
        "ssl_ca_certificate_arn": "sslCaCertificateArn",
        "ssl_client_certificate_arn": "sslClientCertificateArn",
        "ssl_client_key_arn": "sslClientKeyArn",
        "ssl_client_key_password": "sslClientKeyPassword",
        "topic": "topic",
    },
)
class DmsEndpointKafkaSettings:
    def __init__(
        self,
        *,
        broker: builtins.str,
        include_control_details: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_null_and_empty: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_partition_value: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_table_alter_operations: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_transaction_details: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        message_format: typing.Optional[builtins.str] = None,
        message_max_bytes: typing.Optional[jsii.Number] = None,
        no_hex_prefix: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        partition_include_schema_table: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        sasl_password: typing.Optional[builtins.str] = None,
        sasl_username: typing.Optional[builtins.str] = None,
        security_protocol: typing.Optional[builtins.str] = None,
        ssl_ca_certificate_arn: typing.Optional[builtins.str] = None,
        ssl_client_certificate_arn: typing.Optional[builtins.str] = None,
        ssl_client_key_arn: typing.Optional[builtins.str] = None,
        ssl_client_key_password: typing.Optional[builtins.str] = None,
        topic: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param broker: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#broker DmsEndpoint#broker}.
        :param include_control_details: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#include_control_details DmsEndpoint#include_control_details}.
        :param include_null_and_empty: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#include_null_and_empty DmsEndpoint#include_null_and_empty}.
        :param include_partition_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#include_partition_value DmsEndpoint#include_partition_value}.
        :param include_table_alter_operations: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#include_table_alter_operations DmsEndpoint#include_table_alter_operations}.
        :param include_transaction_details: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#include_transaction_details DmsEndpoint#include_transaction_details}.
        :param message_format: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#message_format DmsEndpoint#message_format}.
        :param message_max_bytes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#message_max_bytes DmsEndpoint#message_max_bytes}.
        :param no_hex_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#no_hex_prefix DmsEndpoint#no_hex_prefix}.
        :param partition_include_schema_table: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#partition_include_schema_table DmsEndpoint#partition_include_schema_table}.
        :param sasl_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#sasl_password DmsEndpoint#sasl_password}.
        :param sasl_username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#sasl_username DmsEndpoint#sasl_username}.
        :param security_protocol: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#security_protocol DmsEndpoint#security_protocol}.
        :param ssl_ca_certificate_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#ssl_ca_certificate_arn DmsEndpoint#ssl_ca_certificate_arn}.
        :param ssl_client_certificate_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#ssl_client_certificate_arn DmsEndpoint#ssl_client_certificate_arn}.
        :param ssl_client_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#ssl_client_key_arn DmsEndpoint#ssl_client_key_arn}.
        :param ssl_client_key_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#ssl_client_key_password DmsEndpoint#ssl_client_key_password}.
        :param topic: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#topic DmsEndpoint#topic}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "broker": broker,
        }
        if include_control_details is not None:
            self._values["include_control_details"] = include_control_details
        if include_null_and_empty is not None:
            self._values["include_null_and_empty"] = include_null_and_empty
        if include_partition_value is not None:
            self._values["include_partition_value"] = include_partition_value
        if include_table_alter_operations is not None:
            self._values["include_table_alter_operations"] = include_table_alter_operations
        if include_transaction_details is not None:
            self._values["include_transaction_details"] = include_transaction_details
        if message_format is not None:
            self._values["message_format"] = message_format
        if message_max_bytes is not None:
            self._values["message_max_bytes"] = message_max_bytes
        if no_hex_prefix is not None:
            self._values["no_hex_prefix"] = no_hex_prefix
        if partition_include_schema_table is not None:
            self._values["partition_include_schema_table"] = partition_include_schema_table
        if sasl_password is not None:
            self._values["sasl_password"] = sasl_password
        if sasl_username is not None:
            self._values["sasl_username"] = sasl_username
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
    def broker(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#broker DmsEndpoint#broker}.'''
        result = self._values.get("broker")
        assert result is not None, "Required property 'broker' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def include_control_details(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#include_control_details DmsEndpoint#include_control_details}.'''
        result = self._values.get("include_control_details")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def include_null_and_empty(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#include_null_and_empty DmsEndpoint#include_null_and_empty}.'''
        result = self._values.get("include_null_and_empty")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def include_partition_value(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#include_partition_value DmsEndpoint#include_partition_value}.'''
        result = self._values.get("include_partition_value")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def include_table_alter_operations(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#include_table_alter_operations DmsEndpoint#include_table_alter_operations}.'''
        result = self._values.get("include_table_alter_operations")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def include_transaction_details(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#include_transaction_details DmsEndpoint#include_transaction_details}.'''
        result = self._values.get("include_transaction_details")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def message_format(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#message_format DmsEndpoint#message_format}.'''
        result = self._values.get("message_format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def message_max_bytes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#message_max_bytes DmsEndpoint#message_max_bytes}.'''
        result = self._values.get("message_max_bytes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def no_hex_prefix(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#no_hex_prefix DmsEndpoint#no_hex_prefix}.'''
        result = self._values.get("no_hex_prefix")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def partition_include_schema_table(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#partition_include_schema_table DmsEndpoint#partition_include_schema_table}.'''
        result = self._values.get("partition_include_schema_table")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def sasl_password(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#sasl_password DmsEndpoint#sasl_password}.'''
        result = self._values.get("sasl_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sasl_username(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#sasl_username DmsEndpoint#sasl_username}.'''
        result = self._values.get("sasl_username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_protocol(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#security_protocol DmsEndpoint#security_protocol}.'''
        result = self._values.get("security_protocol")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssl_ca_certificate_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#ssl_ca_certificate_arn DmsEndpoint#ssl_ca_certificate_arn}.'''
        result = self._values.get("ssl_ca_certificate_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssl_client_certificate_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#ssl_client_certificate_arn DmsEndpoint#ssl_client_certificate_arn}.'''
        result = self._values.get("ssl_client_certificate_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssl_client_key_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#ssl_client_key_arn DmsEndpoint#ssl_client_key_arn}.'''
        result = self._values.get("ssl_client_key_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssl_client_key_password(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#ssl_client_key_password DmsEndpoint#ssl_client_key_password}.'''
        result = self._values.get("ssl_client_key_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def topic(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#topic DmsEndpoint#topic}.'''
        result = self._values.get("topic")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DmsEndpointKafkaSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DmsEndpointKafkaSettingsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dms.DmsEndpointKafkaSettingsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetIncludeControlDetails")
    def reset_include_control_details(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeControlDetails", []))

    @jsii.member(jsii_name="resetIncludeNullAndEmpty")
    def reset_include_null_and_empty(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeNullAndEmpty", []))

    @jsii.member(jsii_name="resetIncludePartitionValue")
    def reset_include_partition_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludePartitionValue", []))

    @jsii.member(jsii_name="resetIncludeTableAlterOperations")
    def reset_include_table_alter_operations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeTableAlterOperations", []))

    @jsii.member(jsii_name="resetIncludeTransactionDetails")
    def reset_include_transaction_details(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeTransactionDetails", []))

    @jsii.member(jsii_name="resetMessageFormat")
    def reset_message_format(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMessageFormat", []))

    @jsii.member(jsii_name="resetMessageMaxBytes")
    def reset_message_max_bytes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMessageMaxBytes", []))

    @jsii.member(jsii_name="resetNoHexPrefix")
    def reset_no_hex_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNoHexPrefix", []))

    @jsii.member(jsii_name="resetPartitionIncludeSchemaTable")
    def reset_partition_include_schema_table(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPartitionIncludeSchemaTable", []))

    @jsii.member(jsii_name="resetSaslPassword")
    def reset_sasl_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSaslPassword", []))

    @jsii.member(jsii_name="resetSaslUsername")
    def reset_sasl_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSaslUsername", []))

    @jsii.member(jsii_name="resetSecurityProtocol")
    def reset_security_protocol(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityProtocol", []))

    @jsii.member(jsii_name="resetSslCaCertificateArn")
    def reset_ssl_ca_certificate_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSslCaCertificateArn", []))

    @jsii.member(jsii_name="resetSslClientCertificateArn")
    def reset_ssl_client_certificate_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSslClientCertificateArn", []))

    @jsii.member(jsii_name="resetSslClientKeyArn")
    def reset_ssl_client_key_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSslClientKeyArn", []))

    @jsii.member(jsii_name="resetSslClientKeyPassword")
    def reset_ssl_client_key_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSslClientKeyPassword", []))

    @jsii.member(jsii_name="resetTopic")
    def reset_topic(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTopic", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="brokerInput")
    def broker_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "brokerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeControlDetailsInput")
    def include_control_details_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "includeControlDetailsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeNullAndEmptyInput")
    def include_null_and_empty_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "includeNullAndEmptyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includePartitionValueInput")
    def include_partition_value_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "includePartitionValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeTableAlterOperationsInput")
    def include_table_alter_operations_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "includeTableAlterOperationsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeTransactionDetailsInput")
    def include_transaction_details_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "includeTransactionDetailsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="messageFormatInput")
    def message_format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "messageFormatInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="messageMaxBytesInput")
    def message_max_bytes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "messageMaxBytesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="noHexPrefixInput")
    def no_hex_prefix_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "noHexPrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="partitionIncludeSchemaTableInput")
    def partition_include_schema_table_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "partitionIncludeSchemaTableInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="saslPasswordInput")
    def sasl_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "saslPasswordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="saslUsernameInput")
    def sasl_username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "saslUsernameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityProtocolInput")
    def security_protocol_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "securityProtocolInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sslCaCertificateArnInput")
    def ssl_ca_certificate_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sslCaCertificateArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sslClientCertificateArnInput")
    def ssl_client_certificate_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sslClientCertificateArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sslClientKeyArnInput")
    def ssl_client_key_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sslClientKeyArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sslClientKeyPasswordInput")
    def ssl_client_key_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sslClientKeyPasswordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="topicInput")
    def topic_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "topicInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="broker")
    def broker(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "broker"))

    @broker.setter
    def broker(self, value: builtins.str) -> None:
        jsii.set(self, "broker", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeControlDetails")
    def include_control_details(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "includeControlDetails"))

    @include_control_details.setter
    def include_control_details(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "includeControlDetails", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeNullAndEmpty")
    def include_null_and_empty(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "includeNullAndEmpty"))

    @include_null_and_empty.setter
    def include_null_and_empty(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "includeNullAndEmpty", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includePartitionValue")
    def include_partition_value(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "includePartitionValue"))

    @include_partition_value.setter
    def include_partition_value(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "includePartitionValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeTableAlterOperations")
    def include_table_alter_operations(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "includeTableAlterOperations"))

    @include_table_alter_operations.setter
    def include_table_alter_operations(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "includeTableAlterOperations", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeTransactionDetails")
    def include_transaction_details(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "includeTransactionDetails"))

    @include_transaction_details.setter
    def include_transaction_details(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "includeTransactionDetails", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="messageFormat")
    def message_format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "messageFormat"))

    @message_format.setter
    def message_format(self, value: builtins.str) -> None:
        jsii.set(self, "messageFormat", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="messageMaxBytes")
    def message_max_bytes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "messageMaxBytes"))

    @message_max_bytes.setter
    def message_max_bytes(self, value: jsii.Number) -> None:
        jsii.set(self, "messageMaxBytes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="noHexPrefix")
    def no_hex_prefix(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "noHexPrefix"))

    @no_hex_prefix.setter
    def no_hex_prefix(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "noHexPrefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="partitionIncludeSchemaTable")
    def partition_include_schema_table(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "partitionIncludeSchemaTable"))

    @partition_include_schema_table.setter
    def partition_include_schema_table(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "partitionIncludeSchemaTable", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="saslPassword")
    def sasl_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "saslPassword"))

    @sasl_password.setter
    def sasl_password(self, value: builtins.str) -> None:
        jsii.set(self, "saslPassword", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="saslUsername")
    def sasl_username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "saslUsername"))

    @sasl_username.setter
    def sasl_username(self, value: builtins.str) -> None:
        jsii.set(self, "saslUsername", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityProtocol")
    def security_protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "securityProtocol"))

    @security_protocol.setter
    def security_protocol(self, value: builtins.str) -> None:
        jsii.set(self, "securityProtocol", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sslCaCertificateArn")
    def ssl_ca_certificate_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sslCaCertificateArn"))

    @ssl_ca_certificate_arn.setter
    def ssl_ca_certificate_arn(self, value: builtins.str) -> None:
        jsii.set(self, "sslCaCertificateArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sslClientCertificateArn")
    def ssl_client_certificate_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sslClientCertificateArn"))

    @ssl_client_certificate_arn.setter
    def ssl_client_certificate_arn(self, value: builtins.str) -> None:
        jsii.set(self, "sslClientCertificateArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sslClientKeyArn")
    def ssl_client_key_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sslClientKeyArn"))

    @ssl_client_key_arn.setter
    def ssl_client_key_arn(self, value: builtins.str) -> None:
        jsii.set(self, "sslClientKeyArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sslClientKeyPassword")
    def ssl_client_key_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sslClientKeyPassword"))

    @ssl_client_key_password.setter
    def ssl_client_key_password(self, value: builtins.str) -> None:
        jsii.set(self, "sslClientKeyPassword", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="topic")
    def topic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "topic"))

    @topic.setter
    def topic(self, value: builtins.str) -> None:
        jsii.set(self, "topic", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DmsEndpointKafkaSettings]:
        return typing.cast(typing.Optional[DmsEndpointKafkaSettings], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[DmsEndpointKafkaSettings]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dms.DmsEndpointKinesisSettings",
    jsii_struct_bases=[],
    name_mapping={
        "include_control_details": "includeControlDetails",
        "include_null_and_empty": "includeNullAndEmpty",
        "include_partition_value": "includePartitionValue",
        "include_table_alter_operations": "includeTableAlterOperations",
        "include_transaction_details": "includeTransactionDetails",
        "message_format": "messageFormat",
        "partition_include_schema_table": "partitionIncludeSchemaTable",
        "service_access_role_arn": "serviceAccessRoleArn",
        "stream_arn": "streamArn",
    },
)
class DmsEndpointKinesisSettings:
    def __init__(
        self,
        *,
        include_control_details: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_null_and_empty: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_partition_value: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_table_alter_operations: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_transaction_details: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        message_format: typing.Optional[builtins.str] = None,
        partition_include_schema_table: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        service_access_role_arn: typing.Optional[builtins.str] = None,
        stream_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param include_control_details: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#include_control_details DmsEndpoint#include_control_details}.
        :param include_null_and_empty: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#include_null_and_empty DmsEndpoint#include_null_and_empty}.
        :param include_partition_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#include_partition_value DmsEndpoint#include_partition_value}.
        :param include_table_alter_operations: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#include_table_alter_operations DmsEndpoint#include_table_alter_operations}.
        :param include_transaction_details: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#include_transaction_details DmsEndpoint#include_transaction_details}.
        :param message_format: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#message_format DmsEndpoint#message_format}.
        :param partition_include_schema_table: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#partition_include_schema_table DmsEndpoint#partition_include_schema_table}.
        :param service_access_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#service_access_role_arn DmsEndpoint#service_access_role_arn}.
        :param stream_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#stream_arn DmsEndpoint#stream_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if include_control_details is not None:
            self._values["include_control_details"] = include_control_details
        if include_null_and_empty is not None:
            self._values["include_null_and_empty"] = include_null_and_empty
        if include_partition_value is not None:
            self._values["include_partition_value"] = include_partition_value
        if include_table_alter_operations is not None:
            self._values["include_table_alter_operations"] = include_table_alter_operations
        if include_transaction_details is not None:
            self._values["include_transaction_details"] = include_transaction_details
        if message_format is not None:
            self._values["message_format"] = message_format
        if partition_include_schema_table is not None:
            self._values["partition_include_schema_table"] = partition_include_schema_table
        if service_access_role_arn is not None:
            self._values["service_access_role_arn"] = service_access_role_arn
        if stream_arn is not None:
            self._values["stream_arn"] = stream_arn

    @builtins.property
    def include_control_details(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#include_control_details DmsEndpoint#include_control_details}.'''
        result = self._values.get("include_control_details")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def include_null_and_empty(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#include_null_and_empty DmsEndpoint#include_null_and_empty}.'''
        result = self._values.get("include_null_and_empty")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def include_partition_value(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#include_partition_value DmsEndpoint#include_partition_value}.'''
        result = self._values.get("include_partition_value")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def include_table_alter_operations(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#include_table_alter_operations DmsEndpoint#include_table_alter_operations}.'''
        result = self._values.get("include_table_alter_operations")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def include_transaction_details(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#include_transaction_details DmsEndpoint#include_transaction_details}.'''
        result = self._values.get("include_transaction_details")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def message_format(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#message_format DmsEndpoint#message_format}.'''
        result = self._values.get("message_format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def partition_include_schema_table(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#partition_include_schema_table DmsEndpoint#partition_include_schema_table}.'''
        result = self._values.get("partition_include_schema_table")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def service_access_role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#service_access_role_arn DmsEndpoint#service_access_role_arn}.'''
        result = self._values.get("service_access_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stream_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#stream_arn DmsEndpoint#stream_arn}.'''
        result = self._values.get("stream_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DmsEndpointKinesisSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DmsEndpointKinesisSettingsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dms.DmsEndpointKinesisSettingsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetIncludeControlDetails")
    def reset_include_control_details(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeControlDetails", []))

    @jsii.member(jsii_name="resetIncludeNullAndEmpty")
    def reset_include_null_and_empty(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeNullAndEmpty", []))

    @jsii.member(jsii_name="resetIncludePartitionValue")
    def reset_include_partition_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludePartitionValue", []))

    @jsii.member(jsii_name="resetIncludeTableAlterOperations")
    def reset_include_table_alter_operations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeTableAlterOperations", []))

    @jsii.member(jsii_name="resetIncludeTransactionDetails")
    def reset_include_transaction_details(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeTransactionDetails", []))

    @jsii.member(jsii_name="resetMessageFormat")
    def reset_message_format(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMessageFormat", []))

    @jsii.member(jsii_name="resetPartitionIncludeSchemaTable")
    def reset_partition_include_schema_table(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPartitionIncludeSchemaTable", []))

    @jsii.member(jsii_name="resetServiceAccessRoleArn")
    def reset_service_access_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceAccessRoleArn", []))

    @jsii.member(jsii_name="resetStreamArn")
    def reset_stream_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStreamArn", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeControlDetailsInput")
    def include_control_details_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "includeControlDetailsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeNullAndEmptyInput")
    def include_null_and_empty_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "includeNullAndEmptyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includePartitionValueInput")
    def include_partition_value_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "includePartitionValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeTableAlterOperationsInput")
    def include_table_alter_operations_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "includeTableAlterOperationsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeTransactionDetailsInput")
    def include_transaction_details_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "includeTransactionDetailsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="messageFormatInput")
    def message_format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "messageFormatInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="partitionIncludeSchemaTableInput")
    def partition_include_schema_table_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "partitionIncludeSchemaTableInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceAccessRoleArnInput")
    def service_access_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceAccessRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="streamArnInput")
    def stream_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "streamArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeControlDetails")
    def include_control_details(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "includeControlDetails"))

    @include_control_details.setter
    def include_control_details(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "includeControlDetails", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeNullAndEmpty")
    def include_null_and_empty(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "includeNullAndEmpty"))

    @include_null_and_empty.setter
    def include_null_and_empty(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "includeNullAndEmpty", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includePartitionValue")
    def include_partition_value(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "includePartitionValue"))

    @include_partition_value.setter
    def include_partition_value(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "includePartitionValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeTableAlterOperations")
    def include_table_alter_operations(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "includeTableAlterOperations"))

    @include_table_alter_operations.setter
    def include_table_alter_operations(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "includeTableAlterOperations", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeTransactionDetails")
    def include_transaction_details(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "includeTransactionDetails"))

    @include_transaction_details.setter
    def include_transaction_details(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "includeTransactionDetails", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="messageFormat")
    def message_format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "messageFormat"))

    @message_format.setter
    def message_format(self, value: builtins.str) -> None:
        jsii.set(self, "messageFormat", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="partitionIncludeSchemaTable")
    def partition_include_schema_table(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "partitionIncludeSchemaTable"))

    @partition_include_schema_table.setter
    def partition_include_schema_table(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "partitionIncludeSchemaTable", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceAccessRoleArn")
    def service_access_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceAccessRoleArn"))

    @service_access_role_arn.setter
    def service_access_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "serviceAccessRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="streamArn")
    def stream_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "streamArn"))

    @stream_arn.setter
    def stream_arn(self, value: builtins.str) -> None:
        jsii.set(self, "streamArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DmsEndpointKinesisSettings]:
        return typing.cast(typing.Optional[DmsEndpointKinesisSettings], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DmsEndpointKinesisSettings],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dms.DmsEndpointMongodbSettings",
    jsii_struct_bases=[],
    name_mapping={
        "auth_mechanism": "authMechanism",
        "auth_source": "authSource",
        "auth_type": "authType",
        "docs_to_investigate": "docsToInvestigate",
        "extract_doc_id": "extractDocId",
        "nesting_level": "nestingLevel",
    },
)
class DmsEndpointMongodbSettings:
    def __init__(
        self,
        *,
        auth_mechanism: typing.Optional[builtins.str] = None,
        auth_source: typing.Optional[builtins.str] = None,
        auth_type: typing.Optional[builtins.str] = None,
        docs_to_investigate: typing.Optional[builtins.str] = None,
        extract_doc_id: typing.Optional[builtins.str] = None,
        nesting_level: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param auth_mechanism: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#auth_mechanism DmsEndpoint#auth_mechanism}.
        :param auth_source: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#auth_source DmsEndpoint#auth_source}.
        :param auth_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#auth_type DmsEndpoint#auth_type}.
        :param docs_to_investigate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#docs_to_investigate DmsEndpoint#docs_to_investigate}.
        :param extract_doc_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#extract_doc_id DmsEndpoint#extract_doc_id}.
        :param nesting_level: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#nesting_level DmsEndpoint#nesting_level}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if auth_mechanism is not None:
            self._values["auth_mechanism"] = auth_mechanism
        if auth_source is not None:
            self._values["auth_source"] = auth_source
        if auth_type is not None:
            self._values["auth_type"] = auth_type
        if docs_to_investigate is not None:
            self._values["docs_to_investigate"] = docs_to_investigate
        if extract_doc_id is not None:
            self._values["extract_doc_id"] = extract_doc_id
        if nesting_level is not None:
            self._values["nesting_level"] = nesting_level

    @builtins.property
    def auth_mechanism(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#auth_mechanism DmsEndpoint#auth_mechanism}.'''
        result = self._values.get("auth_mechanism")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auth_source(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#auth_source DmsEndpoint#auth_source}.'''
        result = self._values.get("auth_source")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auth_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#auth_type DmsEndpoint#auth_type}.'''
        result = self._values.get("auth_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def docs_to_investigate(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#docs_to_investigate DmsEndpoint#docs_to_investigate}.'''
        result = self._values.get("docs_to_investigate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def extract_doc_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#extract_doc_id DmsEndpoint#extract_doc_id}.'''
        result = self._values.get("extract_doc_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nesting_level(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#nesting_level DmsEndpoint#nesting_level}.'''
        result = self._values.get("nesting_level")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DmsEndpointMongodbSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DmsEndpointMongodbSettingsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dms.DmsEndpointMongodbSettingsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetAuthMechanism")
    def reset_auth_mechanism(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthMechanism", []))

    @jsii.member(jsii_name="resetAuthSource")
    def reset_auth_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthSource", []))

    @jsii.member(jsii_name="resetAuthType")
    def reset_auth_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthType", []))

    @jsii.member(jsii_name="resetDocsToInvestigate")
    def reset_docs_to_investigate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDocsToInvestigate", []))

    @jsii.member(jsii_name="resetExtractDocId")
    def reset_extract_doc_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExtractDocId", []))

    @jsii.member(jsii_name="resetNestingLevel")
    def reset_nesting_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNestingLevel", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authMechanismInput")
    def auth_mechanism_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authMechanismInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authSourceInput")
    def auth_source_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authSourceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authTypeInput")
    def auth_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="docsToInvestigateInput")
    def docs_to_investigate_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "docsToInvestigateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="extractDocIdInput")
    def extract_doc_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "extractDocIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nestingLevelInput")
    def nesting_level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nestingLevelInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authMechanism")
    def auth_mechanism(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authMechanism"))

    @auth_mechanism.setter
    def auth_mechanism(self, value: builtins.str) -> None:
        jsii.set(self, "authMechanism", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authSource")
    def auth_source(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authSource"))

    @auth_source.setter
    def auth_source(self, value: builtins.str) -> None:
        jsii.set(self, "authSource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authType")
    def auth_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authType"))

    @auth_type.setter
    def auth_type(self, value: builtins.str) -> None:
        jsii.set(self, "authType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="docsToInvestigate")
    def docs_to_investigate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "docsToInvestigate"))

    @docs_to_investigate.setter
    def docs_to_investigate(self, value: builtins.str) -> None:
        jsii.set(self, "docsToInvestigate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="extractDocId")
    def extract_doc_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "extractDocId"))

    @extract_doc_id.setter
    def extract_doc_id(self, value: builtins.str) -> None:
        jsii.set(self, "extractDocId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nestingLevel")
    def nesting_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nestingLevel"))

    @nesting_level.setter
    def nesting_level(self, value: builtins.str) -> None:
        jsii.set(self, "nestingLevel", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DmsEndpointMongodbSettings]:
        return typing.cast(typing.Optional[DmsEndpointMongodbSettings], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DmsEndpointMongodbSettings],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dms.DmsEndpointS3Settings",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_folder": "bucketFolder",
        "bucket_name": "bucketName",
        "compression_type": "compressionType",
        "csv_delimiter": "csvDelimiter",
        "csv_row_delimiter": "csvRowDelimiter",
        "data_format": "dataFormat",
        "date_partition_enabled": "datePartitionEnabled",
        "encryption_mode": "encryptionMode",
        "external_table_definition": "externalTableDefinition",
        "parquet_timestamp_in_millisecond": "parquetTimestampInMillisecond",
        "parquet_version": "parquetVersion",
        "server_side_encryption_kms_key_id": "serverSideEncryptionKmsKeyId",
        "service_access_role_arn": "serviceAccessRoleArn",
    },
)
class DmsEndpointS3Settings:
    def __init__(
        self,
        *,
        bucket_folder: typing.Optional[builtins.str] = None,
        bucket_name: typing.Optional[builtins.str] = None,
        compression_type: typing.Optional[builtins.str] = None,
        csv_delimiter: typing.Optional[builtins.str] = None,
        csv_row_delimiter: typing.Optional[builtins.str] = None,
        data_format: typing.Optional[builtins.str] = None,
        date_partition_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        encryption_mode: typing.Optional[builtins.str] = None,
        external_table_definition: typing.Optional[builtins.str] = None,
        parquet_timestamp_in_millisecond: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        parquet_version: typing.Optional[builtins.str] = None,
        server_side_encryption_kms_key_id: typing.Optional[builtins.str] = None,
        service_access_role_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket_folder: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#bucket_folder DmsEndpoint#bucket_folder}.
        :param bucket_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#bucket_name DmsEndpoint#bucket_name}.
        :param compression_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#compression_type DmsEndpoint#compression_type}.
        :param csv_delimiter: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#csv_delimiter DmsEndpoint#csv_delimiter}.
        :param csv_row_delimiter: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#csv_row_delimiter DmsEndpoint#csv_row_delimiter}.
        :param data_format: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#data_format DmsEndpoint#data_format}.
        :param date_partition_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#date_partition_enabled DmsEndpoint#date_partition_enabled}.
        :param encryption_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#encryption_mode DmsEndpoint#encryption_mode}.
        :param external_table_definition: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#external_table_definition DmsEndpoint#external_table_definition}.
        :param parquet_timestamp_in_millisecond: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#parquet_timestamp_in_millisecond DmsEndpoint#parquet_timestamp_in_millisecond}.
        :param parquet_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#parquet_version DmsEndpoint#parquet_version}.
        :param server_side_encryption_kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#server_side_encryption_kms_key_id DmsEndpoint#server_side_encryption_kms_key_id}.
        :param service_access_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#service_access_role_arn DmsEndpoint#service_access_role_arn}.
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
        if data_format is not None:
            self._values["data_format"] = data_format
        if date_partition_enabled is not None:
            self._values["date_partition_enabled"] = date_partition_enabled
        if encryption_mode is not None:
            self._values["encryption_mode"] = encryption_mode
        if external_table_definition is not None:
            self._values["external_table_definition"] = external_table_definition
        if parquet_timestamp_in_millisecond is not None:
            self._values["parquet_timestamp_in_millisecond"] = parquet_timestamp_in_millisecond
        if parquet_version is not None:
            self._values["parquet_version"] = parquet_version
        if server_side_encryption_kms_key_id is not None:
            self._values["server_side_encryption_kms_key_id"] = server_side_encryption_kms_key_id
        if service_access_role_arn is not None:
            self._values["service_access_role_arn"] = service_access_role_arn

    @builtins.property
    def bucket_folder(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#bucket_folder DmsEndpoint#bucket_folder}.'''
        result = self._values.get("bucket_folder")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#bucket_name DmsEndpoint#bucket_name}.'''
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def compression_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#compression_type DmsEndpoint#compression_type}.'''
        result = self._values.get("compression_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def csv_delimiter(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#csv_delimiter DmsEndpoint#csv_delimiter}.'''
        result = self._values.get("csv_delimiter")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def csv_row_delimiter(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#csv_row_delimiter DmsEndpoint#csv_row_delimiter}.'''
        result = self._values.get("csv_row_delimiter")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def data_format(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#data_format DmsEndpoint#data_format}.'''
        result = self._values.get("data_format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def date_partition_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#date_partition_enabled DmsEndpoint#date_partition_enabled}.'''
        result = self._values.get("date_partition_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def encryption_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#encryption_mode DmsEndpoint#encryption_mode}.'''
        result = self._values.get("encryption_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def external_table_definition(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#external_table_definition DmsEndpoint#external_table_definition}.'''
        result = self._values.get("external_table_definition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parquet_timestamp_in_millisecond(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#parquet_timestamp_in_millisecond DmsEndpoint#parquet_timestamp_in_millisecond}.'''
        result = self._values.get("parquet_timestamp_in_millisecond")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def parquet_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#parquet_version DmsEndpoint#parquet_version}.'''
        result = self._values.get("parquet_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def server_side_encryption_kms_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#server_side_encryption_kms_key_id DmsEndpoint#server_side_encryption_kms_key_id}.'''
        result = self._values.get("server_side_encryption_kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service_access_role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_endpoint#service_access_role_arn DmsEndpoint#service_access_role_arn}.'''
        result = self._values.get("service_access_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DmsEndpointS3Settings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DmsEndpointS3SettingsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dms.DmsEndpointS3SettingsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetBucketFolder")
    def reset_bucket_folder(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBucketFolder", []))

    @jsii.member(jsii_name="resetBucketName")
    def reset_bucket_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBucketName", []))

    @jsii.member(jsii_name="resetCompressionType")
    def reset_compression_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCompressionType", []))

    @jsii.member(jsii_name="resetCsvDelimiter")
    def reset_csv_delimiter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCsvDelimiter", []))

    @jsii.member(jsii_name="resetCsvRowDelimiter")
    def reset_csv_row_delimiter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCsvRowDelimiter", []))

    @jsii.member(jsii_name="resetDataFormat")
    def reset_data_format(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataFormat", []))

    @jsii.member(jsii_name="resetDatePartitionEnabled")
    def reset_date_partition_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatePartitionEnabled", []))

    @jsii.member(jsii_name="resetEncryptionMode")
    def reset_encryption_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionMode", []))

    @jsii.member(jsii_name="resetExternalTableDefinition")
    def reset_external_table_definition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExternalTableDefinition", []))

    @jsii.member(jsii_name="resetParquetTimestampInMillisecond")
    def reset_parquet_timestamp_in_millisecond(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParquetTimestampInMillisecond", []))

    @jsii.member(jsii_name="resetParquetVersion")
    def reset_parquet_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParquetVersion", []))

    @jsii.member(jsii_name="resetServerSideEncryptionKmsKeyId")
    def reset_server_side_encryption_kms_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServerSideEncryptionKmsKeyId", []))

    @jsii.member(jsii_name="resetServiceAccessRoleArn")
    def reset_service_access_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceAccessRoleArn", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketFolderInput")
    def bucket_folder_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketFolderInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketNameInput")
    def bucket_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="compressionTypeInput")
    def compression_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "compressionTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="csvDelimiterInput")
    def csv_delimiter_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "csvDelimiterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="csvRowDelimiterInput")
    def csv_row_delimiter_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "csvRowDelimiterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataFormatInput")
    def data_format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dataFormatInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="datePartitionEnabledInput")
    def date_partition_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "datePartitionEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionModeInput")
    def encryption_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encryptionModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="externalTableDefinitionInput")
    def external_table_definition_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "externalTableDefinitionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parquetTimestampInMillisecondInput")
    def parquet_timestamp_in_millisecond_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "parquetTimestampInMillisecondInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parquetVersionInput")
    def parquet_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parquetVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverSideEncryptionKmsKeyIdInput")
    def server_side_encryption_kms_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serverSideEncryptionKmsKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceAccessRoleArnInput")
    def service_access_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceAccessRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketFolder")
    def bucket_folder(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketFolder"))

    @bucket_folder.setter
    def bucket_folder(self, value: builtins.str) -> None:
        jsii.set(self, "bucketFolder", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketName"))

    @bucket_name.setter
    def bucket_name(self, value: builtins.str) -> None:
        jsii.set(self, "bucketName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="compressionType")
    def compression_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "compressionType"))

    @compression_type.setter
    def compression_type(self, value: builtins.str) -> None:
        jsii.set(self, "compressionType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="csvDelimiter")
    def csv_delimiter(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "csvDelimiter"))

    @csv_delimiter.setter
    def csv_delimiter(self, value: builtins.str) -> None:
        jsii.set(self, "csvDelimiter", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="csvRowDelimiter")
    def csv_row_delimiter(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "csvRowDelimiter"))

    @csv_row_delimiter.setter
    def csv_row_delimiter(self, value: builtins.str) -> None:
        jsii.set(self, "csvRowDelimiter", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataFormat")
    def data_format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataFormat"))

    @data_format.setter
    def data_format(self, value: builtins.str) -> None:
        jsii.set(self, "dataFormat", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="datePartitionEnabled")
    def date_partition_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "datePartitionEnabled"))

    @date_partition_enabled.setter
    def date_partition_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "datePartitionEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionMode")
    def encryption_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptionMode"))

    @encryption_mode.setter
    def encryption_mode(self, value: builtins.str) -> None:
        jsii.set(self, "encryptionMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="externalTableDefinition")
    def external_table_definition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "externalTableDefinition"))

    @external_table_definition.setter
    def external_table_definition(self, value: builtins.str) -> None:
        jsii.set(self, "externalTableDefinition", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parquetTimestampInMillisecond")
    def parquet_timestamp_in_millisecond(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "parquetTimestampInMillisecond"))

    @parquet_timestamp_in_millisecond.setter
    def parquet_timestamp_in_millisecond(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "parquetTimestampInMillisecond", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parquetVersion")
    def parquet_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parquetVersion"))

    @parquet_version.setter
    def parquet_version(self, value: builtins.str) -> None:
        jsii.set(self, "parquetVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverSideEncryptionKmsKeyId")
    def server_side_encryption_kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serverSideEncryptionKmsKeyId"))

    @server_side_encryption_kms_key_id.setter
    def server_side_encryption_kms_key_id(self, value: builtins.str) -> None:
        jsii.set(self, "serverSideEncryptionKmsKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceAccessRoleArn")
    def service_access_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceAccessRoleArn"))

    @service_access_role_arn.setter
    def service_access_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "serviceAccessRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DmsEndpointS3Settings]:
        return typing.cast(typing.Optional[DmsEndpointS3Settings], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[DmsEndpointS3Settings]) -> None:
        jsii.set(self, "internalValue", value)


class DmsEventSubscription(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dms.DmsEventSubscription",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription aws_dms_event_subscription}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        event_categories: typing.Sequence[builtins.str],
        name: builtins.str,
        sns_topic_arn: builtins.str,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        source_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        source_type: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["DmsEventSubscriptionTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription aws_dms_event_subscription} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param event_categories: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#event_categories DmsEventSubscription#event_categories}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#name DmsEventSubscription#name}.
        :param sns_topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#sns_topic_arn DmsEventSubscription#sns_topic_arn}.
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#enabled DmsEventSubscription#enabled}.
        :param source_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#source_ids DmsEventSubscription#source_ids}.
        :param source_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#source_type DmsEventSubscription#source_type}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#tags DmsEventSubscription#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#tags_all DmsEventSubscription#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#timeouts DmsEventSubscription#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DmsEventSubscriptionConfig(
            event_categories=event_categories,
            name=name,
            sns_topic_arn=sns_topic_arn,
            enabled=enabled,
            source_ids=source_ids,
            source_type=source_type,
            tags=tags,
            tags_all=tags_all,
            timeouts=timeouts,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#create DmsEventSubscription#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#delete DmsEventSubscription#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#update DmsEventSubscription#update}.
        '''
        value = DmsEventSubscriptionTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetSourceIds")
    def reset_source_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceIds", []))

    @jsii.member(jsii_name="resetSourceType")
    def reset_source_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceType", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "DmsEventSubscriptionTimeoutsOutputReference":
        return typing.cast("DmsEventSubscriptionTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventCategoriesInput")
    def event_categories_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "eventCategoriesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snsTopicArnInput")
    def sns_topic_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snsTopicArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceIdsInput")
    def source_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "sourceIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceTypeInput")
    def source_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["DmsEventSubscriptionTimeouts"]:
        return typing.cast(typing.Optional["DmsEventSubscriptionTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventCategories")
    def event_categories(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "eventCategories"))

    @event_categories.setter
    def event_categories(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "eventCategories", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snsTopicArn")
    def sns_topic_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snsTopicArn"))

    @sns_topic_arn.setter
    def sns_topic_arn(self, value: builtins.str) -> None:
        jsii.set(self, "snsTopicArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceIds")
    def source_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "sourceIds"))

    @source_ids.setter
    def source_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "sourceIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceType")
    def source_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceType"))

    @source_type.setter
    def source_type(self, value: builtins.str) -> None:
        jsii.set(self, "sourceType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tags"))

    @tags.setter
    def tags(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tagsAll", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dms.DmsEventSubscriptionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "event_categories": "eventCategories",
        "name": "name",
        "sns_topic_arn": "snsTopicArn",
        "enabled": "enabled",
        "source_ids": "sourceIds",
        "source_type": "sourceType",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
    },
)
class DmsEventSubscriptionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        event_categories: typing.Sequence[builtins.str],
        name: builtins.str,
        sns_topic_arn: builtins.str,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        source_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        source_type: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["DmsEventSubscriptionTimeouts"] = None,
    ) -> None:
        '''AWS Database Migration Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param event_categories: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#event_categories DmsEventSubscription#event_categories}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#name DmsEventSubscription#name}.
        :param sns_topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#sns_topic_arn DmsEventSubscription#sns_topic_arn}.
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#enabled DmsEventSubscription#enabled}.
        :param source_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#source_ids DmsEventSubscription#source_ids}.
        :param source_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#source_type DmsEventSubscription#source_type}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#tags DmsEventSubscription#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#tags_all DmsEventSubscription#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#timeouts DmsEventSubscription#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = DmsEventSubscriptionTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "event_categories": event_categories,
            "name": name,
            "sns_topic_arn": sns_topic_arn,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if enabled is not None:
            self._values["enabled"] = enabled
        if source_ids is not None:
            self._values["source_ids"] = source_ids
        if source_type is not None:
            self._values["source_type"] = source_type
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if timeouts is not None:
            self._values["timeouts"] = timeouts

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def event_categories(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#event_categories DmsEventSubscription#event_categories}.'''
        result = self._values.get("event_categories")
        assert result is not None, "Required property 'event_categories' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#name DmsEventSubscription#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def sns_topic_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#sns_topic_arn DmsEventSubscription#sns_topic_arn}.'''
        result = self._values.get("sns_topic_arn")
        assert result is not None, "Required property 'sns_topic_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#enabled DmsEventSubscription#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def source_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#source_ids DmsEventSubscription#source_ids}.'''
        result = self._values.get("source_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def source_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#source_type DmsEventSubscription#source_type}.'''
        result = self._values.get("source_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#tags DmsEventSubscription#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#tags_all DmsEventSubscription#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["DmsEventSubscriptionTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#timeouts DmsEventSubscription#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["DmsEventSubscriptionTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DmsEventSubscriptionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dms.DmsEventSubscriptionTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class DmsEventSubscriptionTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#create DmsEventSubscription#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#delete DmsEventSubscription#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#update DmsEventSubscription#update}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#create DmsEventSubscription#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#delete DmsEventSubscription#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_event_subscription#update DmsEventSubscription#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DmsEventSubscriptionTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DmsEventSubscriptionTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dms.DmsEventSubscriptionTimeoutsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updateInput")
    def update_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        jsii.set(self, "create", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        jsii.set(self, "delete", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        jsii.set(self, "update", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DmsEventSubscriptionTimeouts]:
        return typing.cast(typing.Optional[DmsEventSubscriptionTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DmsEventSubscriptionTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DmsReplicationInstance(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dms.DmsReplicationInstance",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance aws_dms_replication_instance}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        replication_instance_class: builtins.str,
        replication_instance_id: builtins.str,
        allocated_storage: typing.Optional[jsii.Number] = None,
        allow_major_version_upgrade: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        apply_immediately: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_minor_version_upgrade: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        availability_zone: typing.Optional[builtins.str] = None,
        engine_version: typing.Optional[builtins.str] = None,
        kms_key_arn: typing.Optional[builtins.str] = None,
        multi_az: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        preferred_maintenance_window: typing.Optional[builtins.str] = None,
        publicly_accessible: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        replication_subnet_group_id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["DmsReplicationInstanceTimeouts"] = None,
        vpc_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance aws_dms_replication_instance} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param replication_instance_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#replication_instance_class DmsReplicationInstance#replication_instance_class}.
        :param replication_instance_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#replication_instance_id DmsReplicationInstance#replication_instance_id}.
        :param allocated_storage: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#allocated_storage DmsReplicationInstance#allocated_storage}.
        :param allow_major_version_upgrade: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#allow_major_version_upgrade DmsReplicationInstance#allow_major_version_upgrade}.
        :param apply_immediately: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#apply_immediately DmsReplicationInstance#apply_immediately}.
        :param auto_minor_version_upgrade: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#auto_minor_version_upgrade DmsReplicationInstance#auto_minor_version_upgrade}.
        :param availability_zone: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#availability_zone DmsReplicationInstance#availability_zone}.
        :param engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#engine_version DmsReplicationInstance#engine_version}.
        :param kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#kms_key_arn DmsReplicationInstance#kms_key_arn}.
        :param multi_az: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#multi_az DmsReplicationInstance#multi_az}.
        :param preferred_maintenance_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#preferred_maintenance_window DmsReplicationInstance#preferred_maintenance_window}.
        :param publicly_accessible: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#publicly_accessible DmsReplicationInstance#publicly_accessible}.
        :param replication_subnet_group_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#replication_subnet_group_id DmsReplicationInstance#replication_subnet_group_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#tags DmsReplicationInstance#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#tags_all DmsReplicationInstance#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#timeouts DmsReplicationInstance#timeouts}
        :param vpc_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#vpc_security_group_ids DmsReplicationInstance#vpc_security_group_ids}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DmsReplicationInstanceConfig(
            replication_instance_class=replication_instance_class,
            replication_instance_id=replication_instance_id,
            allocated_storage=allocated_storage,
            allow_major_version_upgrade=allow_major_version_upgrade,
            apply_immediately=apply_immediately,
            auto_minor_version_upgrade=auto_minor_version_upgrade,
            availability_zone=availability_zone,
            engine_version=engine_version,
            kms_key_arn=kms_key_arn,
            multi_az=multi_az,
            preferred_maintenance_window=preferred_maintenance_window,
            publicly_accessible=publicly_accessible,
            replication_subnet_group_id=replication_subnet_group_id,
            tags=tags,
            tags_all=tags_all,
            timeouts=timeouts,
            vpc_security_group_ids=vpc_security_group_ids,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#create DmsReplicationInstance#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#delete DmsReplicationInstance#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#update DmsReplicationInstance#update}.
        '''
        value = DmsReplicationInstanceTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetAllocatedStorage")
    def reset_allocated_storage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllocatedStorage", []))

    @jsii.member(jsii_name="resetAllowMajorVersionUpgrade")
    def reset_allow_major_version_upgrade(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowMajorVersionUpgrade", []))

    @jsii.member(jsii_name="resetApplyImmediately")
    def reset_apply_immediately(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApplyImmediately", []))

    @jsii.member(jsii_name="resetAutoMinorVersionUpgrade")
    def reset_auto_minor_version_upgrade(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoMinorVersionUpgrade", []))

    @jsii.member(jsii_name="resetAvailabilityZone")
    def reset_availability_zone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAvailabilityZone", []))

    @jsii.member(jsii_name="resetEngineVersion")
    def reset_engine_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEngineVersion", []))

    @jsii.member(jsii_name="resetKmsKeyArn")
    def reset_kms_key_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyArn", []))

    @jsii.member(jsii_name="resetMultiAz")
    def reset_multi_az(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMultiAz", []))

    @jsii.member(jsii_name="resetPreferredMaintenanceWindow")
    def reset_preferred_maintenance_window(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreferredMaintenanceWindow", []))

    @jsii.member(jsii_name="resetPubliclyAccessible")
    def reset_publicly_accessible(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPubliclyAccessible", []))

    @jsii.member(jsii_name="resetReplicationSubnetGroupId")
    def reset_replication_subnet_group_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReplicationSubnetGroupId", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="resetVpcSecurityGroupIds")
    def reset_vpc_security_group_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVpcSecurityGroupIds", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationInstanceArn")
    def replication_instance_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replicationInstanceArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationInstancePrivateIps")
    def replication_instance_private_ips(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "replicationInstancePrivateIps"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationInstancePublicIps")
    def replication_instance_public_ips(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "replicationInstancePublicIps"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "DmsReplicationInstanceTimeoutsOutputReference":
        return typing.cast("DmsReplicationInstanceTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allocatedStorageInput")
    def allocated_storage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "allocatedStorageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowMajorVersionUpgradeInput")
    def allow_major_version_upgrade_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "allowMajorVersionUpgradeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applyImmediatelyInput")
    def apply_immediately_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "applyImmediatelyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoMinorVersionUpgradeInput")
    def auto_minor_version_upgrade_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoMinorVersionUpgradeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZoneInput")
    def availability_zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "availabilityZoneInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineVersionInput")
    def engine_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "engineVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyArnInput")
    def kms_key_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="multiAzInput")
    def multi_az_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "multiAzInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredMaintenanceWindowInput")
    def preferred_maintenance_window_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preferredMaintenanceWindowInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publiclyAccessibleInput")
    def publicly_accessible_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "publiclyAccessibleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationInstanceClassInput")
    def replication_instance_class_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "replicationInstanceClassInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationInstanceIdInput")
    def replication_instance_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "replicationInstanceIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationSubnetGroupIdInput")
    def replication_subnet_group_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "replicationSubnetGroupIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["DmsReplicationInstanceTimeouts"]:
        return typing.cast(typing.Optional["DmsReplicationInstanceTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcSecurityGroupIdsInput")
    def vpc_security_group_ids_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "vpcSecurityGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allocatedStorage")
    def allocated_storage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "allocatedStorage"))

    @allocated_storage.setter
    def allocated_storage(self, value: jsii.Number) -> None:
        jsii.set(self, "allocatedStorage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowMajorVersionUpgrade")
    def allow_major_version_upgrade(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "allowMajorVersionUpgrade"))

    @allow_major_version_upgrade.setter
    def allow_major_version_upgrade(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "allowMajorVersionUpgrade", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applyImmediately")
    def apply_immediately(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "applyImmediately"))

    @apply_immediately.setter
    def apply_immediately(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "applyImmediately", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoMinorVersionUpgrade")
    def auto_minor_version_upgrade(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoMinorVersionUpgrade"))

    @auto_minor_version_upgrade.setter
    def auto_minor_version_upgrade(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoMinorVersionUpgrade", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availabilityZone"))

    @availability_zone.setter
    def availability_zone(self, value: builtins.str) -> None:
        jsii.set(self, "availabilityZone", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineVersion")
    def engine_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engineVersion"))

    @engine_version.setter
    def engine_version(self, value: builtins.str) -> None:
        jsii.set(self, "engineVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyArn")
    def kms_key_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyArn"))

    @kms_key_arn.setter
    def kms_key_arn(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="multiAz")
    def multi_az(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "multiAz"))

    @multi_az.setter
    def multi_az(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "multiAz", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredMaintenanceWindow")
    def preferred_maintenance_window(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preferredMaintenanceWindow"))

    @preferred_maintenance_window.setter
    def preferred_maintenance_window(self, value: builtins.str) -> None:
        jsii.set(self, "preferredMaintenanceWindow", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publiclyAccessible")
    def publicly_accessible(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "publiclyAccessible"))

    @publicly_accessible.setter
    def publicly_accessible(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "publiclyAccessible", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationInstanceClass")
    def replication_instance_class(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replicationInstanceClass"))

    @replication_instance_class.setter
    def replication_instance_class(self, value: builtins.str) -> None:
        jsii.set(self, "replicationInstanceClass", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationInstanceId")
    def replication_instance_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replicationInstanceId"))

    @replication_instance_id.setter
    def replication_instance_id(self, value: builtins.str) -> None:
        jsii.set(self, "replicationInstanceId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationSubnetGroupId")
    def replication_subnet_group_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replicationSubnetGroupId"))

    @replication_subnet_group_id.setter
    def replication_subnet_group_id(self, value: builtins.str) -> None:
        jsii.set(self, "replicationSubnetGroupId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tags"))

    @tags.setter
    def tags(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tagsAll", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcSecurityGroupIds")
    def vpc_security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "vpcSecurityGroupIds"))

    @vpc_security_group_ids.setter
    def vpc_security_group_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "vpcSecurityGroupIds", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dms.DmsReplicationInstanceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "replication_instance_class": "replicationInstanceClass",
        "replication_instance_id": "replicationInstanceId",
        "allocated_storage": "allocatedStorage",
        "allow_major_version_upgrade": "allowMajorVersionUpgrade",
        "apply_immediately": "applyImmediately",
        "auto_minor_version_upgrade": "autoMinorVersionUpgrade",
        "availability_zone": "availabilityZone",
        "engine_version": "engineVersion",
        "kms_key_arn": "kmsKeyArn",
        "multi_az": "multiAz",
        "preferred_maintenance_window": "preferredMaintenanceWindow",
        "publicly_accessible": "publiclyAccessible",
        "replication_subnet_group_id": "replicationSubnetGroupId",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
        "vpc_security_group_ids": "vpcSecurityGroupIds",
    },
)
class DmsReplicationInstanceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        replication_instance_class: builtins.str,
        replication_instance_id: builtins.str,
        allocated_storage: typing.Optional[jsii.Number] = None,
        allow_major_version_upgrade: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        apply_immediately: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_minor_version_upgrade: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        availability_zone: typing.Optional[builtins.str] = None,
        engine_version: typing.Optional[builtins.str] = None,
        kms_key_arn: typing.Optional[builtins.str] = None,
        multi_az: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        preferred_maintenance_window: typing.Optional[builtins.str] = None,
        publicly_accessible: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        replication_subnet_group_id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["DmsReplicationInstanceTimeouts"] = None,
        vpc_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''AWS Database Migration Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param replication_instance_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#replication_instance_class DmsReplicationInstance#replication_instance_class}.
        :param replication_instance_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#replication_instance_id DmsReplicationInstance#replication_instance_id}.
        :param allocated_storage: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#allocated_storage DmsReplicationInstance#allocated_storage}.
        :param allow_major_version_upgrade: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#allow_major_version_upgrade DmsReplicationInstance#allow_major_version_upgrade}.
        :param apply_immediately: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#apply_immediately DmsReplicationInstance#apply_immediately}.
        :param auto_minor_version_upgrade: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#auto_minor_version_upgrade DmsReplicationInstance#auto_minor_version_upgrade}.
        :param availability_zone: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#availability_zone DmsReplicationInstance#availability_zone}.
        :param engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#engine_version DmsReplicationInstance#engine_version}.
        :param kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#kms_key_arn DmsReplicationInstance#kms_key_arn}.
        :param multi_az: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#multi_az DmsReplicationInstance#multi_az}.
        :param preferred_maintenance_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#preferred_maintenance_window DmsReplicationInstance#preferred_maintenance_window}.
        :param publicly_accessible: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#publicly_accessible DmsReplicationInstance#publicly_accessible}.
        :param replication_subnet_group_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#replication_subnet_group_id DmsReplicationInstance#replication_subnet_group_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#tags DmsReplicationInstance#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#tags_all DmsReplicationInstance#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#timeouts DmsReplicationInstance#timeouts}
        :param vpc_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#vpc_security_group_ids DmsReplicationInstance#vpc_security_group_ids}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = DmsReplicationInstanceTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "replication_instance_class": replication_instance_class,
            "replication_instance_id": replication_instance_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if allocated_storage is not None:
            self._values["allocated_storage"] = allocated_storage
        if allow_major_version_upgrade is not None:
            self._values["allow_major_version_upgrade"] = allow_major_version_upgrade
        if apply_immediately is not None:
            self._values["apply_immediately"] = apply_immediately
        if auto_minor_version_upgrade is not None:
            self._values["auto_minor_version_upgrade"] = auto_minor_version_upgrade
        if availability_zone is not None:
            self._values["availability_zone"] = availability_zone
        if engine_version is not None:
            self._values["engine_version"] = engine_version
        if kms_key_arn is not None:
            self._values["kms_key_arn"] = kms_key_arn
        if multi_az is not None:
            self._values["multi_az"] = multi_az
        if preferred_maintenance_window is not None:
            self._values["preferred_maintenance_window"] = preferred_maintenance_window
        if publicly_accessible is not None:
            self._values["publicly_accessible"] = publicly_accessible
        if replication_subnet_group_id is not None:
            self._values["replication_subnet_group_id"] = replication_subnet_group_id
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if timeouts is not None:
            self._values["timeouts"] = timeouts
        if vpc_security_group_ids is not None:
            self._values["vpc_security_group_ids"] = vpc_security_group_ids

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def replication_instance_class(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#replication_instance_class DmsReplicationInstance#replication_instance_class}.'''
        result = self._values.get("replication_instance_class")
        assert result is not None, "Required property 'replication_instance_class' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def replication_instance_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#replication_instance_id DmsReplicationInstance#replication_instance_id}.'''
        result = self._values.get("replication_instance_id")
        assert result is not None, "Required property 'replication_instance_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allocated_storage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#allocated_storage DmsReplicationInstance#allocated_storage}.'''
        result = self._values.get("allocated_storage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def allow_major_version_upgrade(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#allow_major_version_upgrade DmsReplicationInstance#allow_major_version_upgrade}.'''
        result = self._values.get("allow_major_version_upgrade")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def apply_immediately(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#apply_immediately DmsReplicationInstance#apply_immediately}.'''
        result = self._values.get("apply_immediately")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def auto_minor_version_upgrade(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#auto_minor_version_upgrade DmsReplicationInstance#auto_minor_version_upgrade}.'''
        result = self._values.get("auto_minor_version_upgrade")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def availability_zone(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#availability_zone DmsReplicationInstance#availability_zone}.'''
        result = self._values.get("availability_zone")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def engine_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#engine_version DmsReplicationInstance#engine_version}.'''
        result = self._values.get("engine_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#kms_key_arn DmsReplicationInstance#kms_key_arn}.'''
        result = self._values.get("kms_key_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def multi_az(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#multi_az DmsReplicationInstance#multi_az}.'''
        result = self._values.get("multi_az")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def preferred_maintenance_window(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#preferred_maintenance_window DmsReplicationInstance#preferred_maintenance_window}.'''
        result = self._values.get("preferred_maintenance_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def publicly_accessible(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#publicly_accessible DmsReplicationInstance#publicly_accessible}.'''
        result = self._values.get("publicly_accessible")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def replication_subnet_group_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#replication_subnet_group_id DmsReplicationInstance#replication_subnet_group_id}.'''
        result = self._values.get("replication_subnet_group_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#tags DmsReplicationInstance#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#tags_all DmsReplicationInstance#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["DmsReplicationInstanceTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#timeouts DmsReplicationInstance#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["DmsReplicationInstanceTimeouts"], result)

    @builtins.property
    def vpc_security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#vpc_security_group_ids DmsReplicationInstance#vpc_security_group_ids}.'''
        result = self._values.get("vpc_security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DmsReplicationInstanceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dms.DmsReplicationInstanceTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class DmsReplicationInstanceTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#create DmsReplicationInstance#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#delete DmsReplicationInstance#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#update DmsReplicationInstance#update}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#create DmsReplicationInstance#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#delete DmsReplicationInstance#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_instance#update DmsReplicationInstance#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DmsReplicationInstanceTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DmsReplicationInstanceTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dms.DmsReplicationInstanceTimeoutsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updateInput")
    def update_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        jsii.set(self, "create", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        jsii.set(self, "delete", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        jsii.set(self, "update", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DmsReplicationInstanceTimeouts]:
        return typing.cast(typing.Optional[DmsReplicationInstanceTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DmsReplicationInstanceTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DmsReplicationSubnetGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dms.DmsReplicationSubnetGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_subnet_group aws_dms_replication_subnet_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        replication_subnet_group_description: builtins.str,
        replication_subnet_group_id: builtins.str,
        subnet_ids: typing.Sequence[builtins.str],
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_subnet_group aws_dms_replication_subnet_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param replication_subnet_group_description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_subnet_group#replication_subnet_group_description DmsReplicationSubnetGroup#replication_subnet_group_description}.
        :param replication_subnet_group_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_subnet_group#replication_subnet_group_id DmsReplicationSubnetGroup#replication_subnet_group_id}.
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_subnet_group#subnet_ids DmsReplicationSubnetGroup#subnet_ids}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_subnet_group#tags DmsReplicationSubnetGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_subnet_group#tags_all DmsReplicationSubnetGroup#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DmsReplicationSubnetGroupConfig(
            replication_subnet_group_description=replication_subnet_group_description,
            replication_subnet_group_id=replication_subnet_group_id,
            subnet_ids=subnet_ids,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationSubnetGroupArn")
    def replication_subnet_group_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replicationSubnetGroupArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationSubnetGroupDescriptionInput")
    def replication_subnet_group_description_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "replicationSubnetGroupDescriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationSubnetGroupIdInput")
    def replication_subnet_group_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "replicationSubnetGroupIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetIdsInput")
    def subnet_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "subnetIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationSubnetGroupDescription")
    def replication_subnet_group_description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replicationSubnetGroupDescription"))

    @replication_subnet_group_description.setter
    def replication_subnet_group_description(self, value: builtins.str) -> None:
        jsii.set(self, "replicationSubnetGroupDescription", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationSubnetGroupId")
    def replication_subnet_group_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replicationSubnetGroupId"))

    @replication_subnet_group_id.setter
    def replication_subnet_group_id(self, value: builtins.str) -> None:
        jsii.set(self, "replicationSubnetGroupId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "subnetIds"))

    @subnet_ids.setter
    def subnet_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "subnetIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tags"))

    @tags.setter
    def tags(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tagsAll", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dms.DmsReplicationSubnetGroupConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "replication_subnet_group_description": "replicationSubnetGroupDescription",
        "replication_subnet_group_id": "replicationSubnetGroupId",
        "subnet_ids": "subnetIds",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class DmsReplicationSubnetGroupConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        replication_subnet_group_description: builtins.str,
        replication_subnet_group_id: builtins.str,
        subnet_ids: typing.Sequence[builtins.str],
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Database Migration Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param replication_subnet_group_description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_subnet_group#replication_subnet_group_description DmsReplicationSubnetGroup#replication_subnet_group_description}.
        :param replication_subnet_group_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_subnet_group#replication_subnet_group_id DmsReplicationSubnetGroup#replication_subnet_group_id}.
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_subnet_group#subnet_ids DmsReplicationSubnetGroup#subnet_ids}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_subnet_group#tags DmsReplicationSubnetGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_subnet_group#tags_all DmsReplicationSubnetGroup#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "replication_subnet_group_description": replication_subnet_group_description,
            "replication_subnet_group_id": replication_subnet_group_id,
            "subnet_ids": subnet_ids,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def replication_subnet_group_description(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_subnet_group#replication_subnet_group_description DmsReplicationSubnetGroup#replication_subnet_group_description}.'''
        result = self._values.get("replication_subnet_group_description")
        assert result is not None, "Required property 'replication_subnet_group_description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def replication_subnet_group_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_subnet_group#replication_subnet_group_id DmsReplicationSubnetGroup#replication_subnet_group_id}.'''
        result = self._values.get("replication_subnet_group_id")
        assert result is not None, "Required property 'replication_subnet_group_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subnet_ids(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_subnet_group#subnet_ids DmsReplicationSubnetGroup#subnet_ids}.'''
        result = self._values.get("subnet_ids")
        assert result is not None, "Required property 'subnet_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_subnet_group#tags DmsReplicationSubnetGroup#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_subnet_group#tags_all DmsReplicationSubnetGroup#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DmsReplicationSubnetGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DmsReplicationTask(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dms.DmsReplicationTask",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task aws_dms_replication_task}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        migration_type: builtins.str,
        replication_instance_arn: builtins.str,
        replication_task_id: builtins.str,
        source_endpoint_arn: builtins.str,
        table_mappings: builtins.str,
        target_endpoint_arn: builtins.str,
        cdc_start_position: typing.Optional[builtins.str] = None,
        cdc_start_time: typing.Optional[builtins.str] = None,
        replication_task_settings: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task aws_dms_replication_task} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param migration_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task#migration_type DmsReplicationTask#migration_type}.
        :param replication_instance_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task#replication_instance_arn DmsReplicationTask#replication_instance_arn}.
        :param replication_task_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task#replication_task_id DmsReplicationTask#replication_task_id}.
        :param source_endpoint_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task#source_endpoint_arn DmsReplicationTask#source_endpoint_arn}.
        :param table_mappings: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task#table_mappings DmsReplicationTask#table_mappings}.
        :param target_endpoint_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task#target_endpoint_arn DmsReplicationTask#target_endpoint_arn}.
        :param cdc_start_position: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task#cdc_start_position DmsReplicationTask#cdc_start_position}.
        :param cdc_start_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task#cdc_start_time DmsReplicationTask#cdc_start_time}.
        :param replication_task_settings: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task#replication_task_settings DmsReplicationTask#replication_task_settings}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task#tags DmsReplicationTask#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task#tags_all DmsReplicationTask#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DmsReplicationTaskConfig(
            migration_type=migration_type,
            replication_instance_arn=replication_instance_arn,
            replication_task_id=replication_task_id,
            source_endpoint_arn=source_endpoint_arn,
            table_mappings=table_mappings,
            target_endpoint_arn=target_endpoint_arn,
            cdc_start_position=cdc_start_position,
            cdc_start_time=cdc_start_time,
            replication_task_settings=replication_task_settings,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetCdcStartPosition")
    def reset_cdc_start_position(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCdcStartPosition", []))

    @jsii.member(jsii_name="resetCdcStartTime")
    def reset_cdc_start_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCdcStartTime", []))

    @jsii.member(jsii_name="resetReplicationTaskSettings")
    def reset_replication_task_settings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReplicationTaskSettings", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationTaskArn")
    def replication_task_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replicationTaskArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cdcStartPositionInput")
    def cdc_start_position_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cdcStartPositionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cdcStartTimeInput")
    def cdc_start_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cdcStartTimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="migrationTypeInput")
    def migration_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "migrationTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationInstanceArnInput")
    def replication_instance_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "replicationInstanceArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationTaskIdInput")
    def replication_task_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "replicationTaskIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationTaskSettingsInput")
    def replication_task_settings_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "replicationTaskSettingsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceEndpointArnInput")
    def source_endpoint_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceEndpointArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tableMappingsInput")
    def table_mappings_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tableMappingsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetEndpointArnInput")
    def target_endpoint_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetEndpointArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cdcStartPosition")
    def cdc_start_position(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cdcStartPosition"))

    @cdc_start_position.setter
    def cdc_start_position(self, value: builtins.str) -> None:
        jsii.set(self, "cdcStartPosition", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cdcStartTime")
    def cdc_start_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cdcStartTime"))

    @cdc_start_time.setter
    def cdc_start_time(self, value: builtins.str) -> None:
        jsii.set(self, "cdcStartTime", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="migrationType")
    def migration_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "migrationType"))

    @migration_type.setter
    def migration_type(self, value: builtins.str) -> None:
        jsii.set(self, "migrationType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationInstanceArn")
    def replication_instance_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replicationInstanceArn"))

    @replication_instance_arn.setter
    def replication_instance_arn(self, value: builtins.str) -> None:
        jsii.set(self, "replicationInstanceArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationTaskId")
    def replication_task_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replicationTaskId"))

    @replication_task_id.setter
    def replication_task_id(self, value: builtins.str) -> None:
        jsii.set(self, "replicationTaskId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationTaskSettings")
    def replication_task_settings(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replicationTaskSettings"))

    @replication_task_settings.setter
    def replication_task_settings(self, value: builtins.str) -> None:
        jsii.set(self, "replicationTaskSettings", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceEndpointArn")
    def source_endpoint_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceEndpointArn"))

    @source_endpoint_arn.setter
    def source_endpoint_arn(self, value: builtins.str) -> None:
        jsii.set(self, "sourceEndpointArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tableMappings")
    def table_mappings(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tableMappings"))

    @table_mappings.setter
    def table_mappings(self, value: builtins.str) -> None:
        jsii.set(self, "tableMappings", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tags"))

    @tags.setter
    def tags(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tagsAll", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetEndpointArn")
    def target_endpoint_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetEndpointArn"))

    @target_endpoint_arn.setter
    def target_endpoint_arn(self, value: builtins.str) -> None:
        jsii.set(self, "targetEndpointArn", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dms.DmsReplicationTaskConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "migration_type": "migrationType",
        "replication_instance_arn": "replicationInstanceArn",
        "replication_task_id": "replicationTaskId",
        "source_endpoint_arn": "sourceEndpointArn",
        "table_mappings": "tableMappings",
        "target_endpoint_arn": "targetEndpointArn",
        "cdc_start_position": "cdcStartPosition",
        "cdc_start_time": "cdcStartTime",
        "replication_task_settings": "replicationTaskSettings",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class DmsReplicationTaskConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        migration_type: builtins.str,
        replication_instance_arn: builtins.str,
        replication_task_id: builtins.str,
        source_endpoint_arn: builtins.str,
        table_mappings: builtins.str,
        target_endpoint_arn: builtins.str,
        cdc_start_position: typing.Optional[builtins.str] = None,
        cdc_start_time: typing.Optional[builtins.str] = None,
        replication_task_settings: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Database Migration Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param migration_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task#migration_type DmsReplicationTask#migration_type}.
        :param replication_instance_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task#replication_instance_arn DmsReplicationTask#replication_instance_arn}.
        :param replication_task_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task#replication_task_id DmsReplicationTask#replication_task_id}.
        :param source_endpoint_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task#source_endpoint_arn DmsReplicationTask#source_endpoint_arn}.
        :param table_mappings: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task#table_mappings DmsReplicationTask#table_mappings}.
        :param target_endpoint_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task#target_endpoint_arn DmsReplicationTask#target_endpoint_arn}.
        :param cdc_start_position: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task#cdc_start_position DmsReplicationTask#cdc_start_position}.
        :param cdc_start_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task#cdc_start_time DmsReplicationTask#cdc_start_time}.
        :param replication_task_settings: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task#replication_task_settings DmsReplicationTask#replication_task_settings}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task#tags DmsReplicationTask#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task#tags_all DmsReplicationTask#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "migration_type": migration_type,
            "replication_instance_arn": replication_instance_arn,
            "replication_task_id": replication_task_id,
            "source_endpoint_arn": source_endpoint_arn,
            "table_mappings": table_mappings,
            "target_endpoint_arn": target_endpoint_arn,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if cdc_start_position is not None:
            self._values["cdc_start_position"] = cdc_start_position
        if cdc_start_time is not None:
            self._values["cdc_start_time"] = cdc_start_time
        if replication_task_settings is not None:
            self._values["replication_task_settings"] = replication_task_settings
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def migration_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task#migration_type DmsReplicationTask#migration_type}.'''
        result = self._values.get("migration_type")
        assert result is not None, "Required property 'migration_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def replication_instance_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task#replication_instance_arn DmsReplicationTask#replication_instance_arn}.'''
        result = self._values.get("replication_instance_arn")
        assert result is not None, "Required property 'replication_instance_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def replication_task_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task#replication_task_id DmsReplicationTask#replication_task_id}.'''
        result = self._values.get("replication_task_id")
        assert result is not None, "Required property 'replication_task_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def source_endpoint_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task#source_endpoint_arn DmsReplicationTask#source_endpoint_arn}.'''
        result = self._values.get("source_endpoint_arn")
        assert result is not None, "Required property 'source_endpoint_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def table_mappings(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task#table_mappings DmsReplicationTask#table_mappings}.'''
        result = self._values.get("table_mappings")
        assert result is not None, "Required property 'table_mappings' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_endpoint_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task#target_endpoint_arn DmsReplicationTask#target_endpoint_arn}.'''
        result = self._values.get("target_endpoint_arn")
        assert result is not None, "Required property 'target_endpoint_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cdc_start_position(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task#cdc_start_position DmsReplicationTask#cdc_start_position}.'''
        result = self._values.get("cdc_start_position")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cdc_start_time(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task#cdc_start_time DmsReplicationTask#cdc_start_time}.'''
        result = self._values.get("cdc_start_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def replication_task_settings(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task#replication_task_settings DmsReplicationTask#replication_task_settings}.'''
        result = self._values.get("replication_task_settings")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task#tags DmsReplicationTask#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dms_replication_task#tags_all DmsReplicationTask#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DmsReplicationTaskConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DmsCertificate",
    "DmsCertificateConfig",
    "DmsEndpoint",
    "DmsEndpointConfig",
    "DmsEndpointElasticsearchSettings",
    "DmsEndpointElasticsearchSettingsOutputReference",
    "DmsEndpointKafkaSettings",
    "DmsEndpointKafkaSettingsOutputReference",
    "DmsEndpointKinesisSettings",
    "DmsEndpointKinesisSettingsOutputReference",
    "DmsEndpointMongodbSettings",
    "DmsEndpointMongodbSettingsOutputReference",
    "DmsEndpointS3Settings",
    "DmsEndpointS3SettingsOutputReference",
    "DmsEventSubscription",
    "DmsEventSubscriptionConfig",
    "DmsEventSubscriptionTimeouts",
    "DmsEventSubscriptionTimeoutsOutputReference",
    "DmsReplicationInstance",
    "DmsReplicationInstanceConfig",
    "DmsReplicationInstanceTimeouts",
    "DmsReplicationInstanceTimeoutsOutputReference",
    "DmsReplicationSubnetGroup",
    "DmsReplicationSubnetGroupConfig",
    "DmsReplicationTask",
    "DmsReplicationTaskConfig",
]

publication.publish()
