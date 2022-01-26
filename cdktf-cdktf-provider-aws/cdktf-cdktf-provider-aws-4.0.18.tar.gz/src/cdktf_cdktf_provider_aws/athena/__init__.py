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


class AthenaDatabase(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.athena.AthenaDatabase",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/athena_database aws_athena_database}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        bucket: builtins.str,
        name: builtins.str,
        encryption_configuration: typing.Optional["AthenaDatabaseEncryptionConfiguration"] = None,
        force_destroy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/athena_database aws_athena_database} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#bucket AthenaDatabase#bucket}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#name AthenaDatabase#name}.
        :param encryption_configuration: encryption_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#encryption_configuration AthenaDatabase#encryption_configuration}
        :param force_destroy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#force_destroy AthenaDatabase#force_destroy}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = AthenaDatabaseConfig(
            bucket=bucket,
            name=name,
            encryption_configuration=encryption_configuration,
            force_destroy=force_destroy,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putEncryptionConfiguration")
    def put_encryption_configuration(
        self,
        *,
        encryption_option: builtins.str,
        kms_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param encryption_option: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#encryption_option AthenaDatabase#encryption_option}.
        :param kms_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#kms_key AthenaDatabase#kms_key}.
        '''
        value = AthenaDatabaseEncryptionConfiguration(
            encryption_option=encryption_option, kms_key=kms_key
        )

        return typing.cast(None, jsii.invoke(self, "putEncryptionConfiguration", [value]))

    @jsii.member(jsii_name="resetEncryptionConfiguration")
    def reset_encryption_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionConfiguration", []))

    @jsii.member(jsii_name="resetForceDestroy")
    def reset_force_destroy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceDestroy", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionConfiguration")
    def encryption_configuration(
        self,
    ) -> "AthenaDatabaseEncryptionConfigurationOutputReference":
        return typing.cast("AthenaDatabaseEncryptionConfigurationOutputReference", jsii.get(self, "encryptionConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionConfigurationInput")
    def encryption_configuration_input(
        self,
    ) -> typing.Optional["AthenaDatabaseEncryptionConfiguration"]:
        return typing.cast(typing.Optional["AthenaDatabaseEncryptionConfiguration"], jsii.get(self, "encryptionConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceDestroyInput")
    def force_destroy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "forceDestroyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        jsii.set(self, "bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceDestroy")
    def force_destroy(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "forceDestroy"))

    @force_destroy.setter
    def force_destroy(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "forceDestroy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.athena.AthenaDatabaseConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "bucket": "bucket",
        "name": "name",
        "encryption_configuration": "encryptionConfiguration",
        "force_destroy": "forceDestroy",
    },
)
class AthenaDatabaseConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        bucket: builtins.str,
        name: builtins.str,
        encryption_configuration: typing.Optional["AthenaDatabaseEncryptionConfiguration"] = None,
        force_destroy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''Amazon Athena.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#bucket AthenaDatabase#bucket}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#name AthenaDatabase#name}.
        :param encryption_configuration: encryption_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#encryption_configuration AthenaDatabase#encryption_configuration}
        :param force_destroy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#force_destroy AthenaDatabase#force_destroy}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(encryption_configuration, dict):
            encryption_configuration = AthenaDatabaseEncryptionConfiguration(**encryption_configuration)
        self._values: typing.Dict[str, typing.Any] = {
            "bucket": bucket,
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if encryption_configuration is not None:
            self._values["encryption_configuration"] = encryption_configuration
        if force_destroy is not None:
            self._values["force_destroy"] = force_destroy

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
    def bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#bucket AthenaDatabase#bucket}.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#name AthenaDatabase#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def encryption_configuration(
        self,
    ) -> typing.Optional["AthenaDatabaseEncryptionConfiguration"]:
        '''encryption_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#encryption_configuration AthenaDatabase#encryption_configuration}
        '''
        result = self._values.get("encryption_configuration")
        return typing.cast(typing.Optional["AthenaDatabaseEncryptionConfiguration"], result)

    @builtins.property
    def force_destroy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#force_destroy AthenaDatabase#force_destroy}.'''
        result = self._values.get("force_destroy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AthenaDatabaseConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.athena.AthenaDatabaseEncryptionConfiguration",
    jsii_struct_bases=[],
    name_mapping={"encryption_option": "encryptionOption", "kms_key": "kmsKey"},
)
class AthenaDatabaseEncryptionConfiguration:
    def __init__(
        self,
        *,
        encryption_option: builtins.str,
        kms_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param encryption_option: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#encryption_option AthenaDatabase#encryption_option}.
        :param kms_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#kms_key AthenaDatabase#kms_key}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "encryption_option": encryption_option,
        }
        if kms_key is not None:
            self._values["kms_key"] = kms_key

    @builtins.property
    def encryption_option(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#encryption_option AthenaDatabase#encryption_option}.'''
        result = self._values.get("encryption_option")
        assert result is not None, "Required property 'encryption_option' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def kms_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_database#kms_key AthenaDatabase#kms_key}.'''
        result = self._values.get("kms_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AthenaDatabaseEncryptionConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AthenaDatabaseEncryptionConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.athena.AthenaDatabaseEncryptionConfigurationOutputReference",
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

    @jsii.member(jsii_name="resetKmsKey")
    def reset_kms_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKey", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionOptionInput")
    def encryption_option_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encryptionOptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyInput")
    def kms_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionOption")
    def encryption_option(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptionOption"))

    @encryption_option.setter
    def encryption_option(self, value: builtins.str) -> None:
        jsii.set(self, "encryptionOption", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKey")
    def kms_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKey"))

    @kms_key.setter
    def kms_key(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AthenaDatabaseEncryptionConfiguration]:
        return typing.cast(typing.Optional[AthenaDatabaseEncryptionConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AthenaDatabaseEncryptionConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


class AthenaNamedQuery(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.athena.AthenaNamedQuery",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query aws_athena_named_query}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        database: builtins.str,
        name: builtins.str,
        query: builtins.str,
        description: typing.Optional[builtins.str] = None,
        workgroup: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query aws_athena_named_query} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param database: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query#database AthenaNamedQuery#database}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query#name AthenaNamedQuery#name}.
        :param query: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query#query AthenaNamedQuery#query}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query#description AthenaNamedQuery#description}.
        :param workgroup: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query#workgroup AthenaNamedQuery#workgroup}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = AthenaNamedQueryConfig(
            database=database,
            name=name,
            query=query,
            description=description,
            workgroup=workgroup,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetWorkgroup")
    def reset_workgroup(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkgroup", []))

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
    @jsii.member(jsii_name="databaseInput")
    def database_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryInput")
    def query_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "queryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workgroupInput")
    def workgroup_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workgroupInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="database")
    def database(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "database"))

    @database.setter
    def database(self, value: builtins.str) -> None:
        jsii.set(self, "database", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="query")
    def query(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "query"))

    @query.setter
    def query(self, value: builtins.str) -> None:
        jsii.set(self, "query", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workgroup")
    def workgroup(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workgroup"))

    @workgroup.setter
    def workgroup(self, value: builtins.str) -> None:
        jsii.set(self, "workgroup", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.athena.AthenaNamedQueryConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "database": "database",
        "name": "name",
        "query": "query",
        "description": "description",
        "workgroup": "workgroup",
    },
)
class AthenaNamedQueryConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        database: builtins.str,
        name: builtins.str,
        query: builtins.str,
        description: typing.Optional[builtins.str] = None,
        workgroup: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Amazon Athena.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param database: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query#database AthenaNamedQuery#database}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query#name AthenaNamedQuery#name}.
        :param query: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query#query AthenaNamedQuery#query}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query#description AthenaNamedQuery#description}.
        :param workgroup: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query#workgroup AthenaNamedQuery#workgroup}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "database": database,
            "name": name,
            "query": query,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if description is not None:
            self._values["description"] = description
        if workgroup is not None:
            self._values["workgroup"] = workgroup

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
    def database(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query#database AthenaNamedQuery#database}.'''
        result = self._values.get("database")
        assert result is not None, "Required property 'database' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query#name AthenaNamedQuery#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def query(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query#query AthenaNamedQuery#query}.'''
        result = self._values.get("query")
        assert result is not None, "Required property 'query' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query#description AthenaNamedQuery#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workgroup(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_named_query#workgroup AthenaNamedQuery#workgroup}.'''
        result = self._values.get("workgroup")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AthenaNamedQueryConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AthenaWorkgroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.athena.AthenaWorkgroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup aws_athena_workgroup}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        configuration: typing.Optional["AthenaWorkgroupConfiguration"] = None,
        description: typing.Optional[builtins.str] = None,
        force_destroy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        state: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup aws_athena_workgroup} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#name AthenaWorkgroup#name}.
        :param configuration: configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#configuration AthenaWorkgroup#configuration}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#description AthenaWorkgroup#description}.
        :param force_destroy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#force_destroy AthenaWorkgroup#force_destroy}.
        :param state: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#state AthenaWorkgroup#state}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#tags AthenaWorkgroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#tags_all AthenaWorkgroup#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = AthenaWorkgroupConfig(
            name=name,
            configuration=configuration,
            description=description,
            force_destroy=force_destroy,
            state=state,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putConfiguration")
    def put_configuration(
        self,
        *,
        bytes_scanned_cutoff_per_query: typing.Optional[jsii.Number] = None,
        enforce_workgroup_configuration: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        engine_version: typing.Optional["AthenaWorkgroupConfigurationEngineVersion"] = None,
        publish_cloudwatch_metrics_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        requester_pays_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        result_configuration: typing.Optional["AthenaWorkgroupConfigurationResultConfiguration"] = None,
    ) -> None:
        '''
        :param bytes_scanned_cutoff_per_query: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#bytes_scanned_cutoff_per_query AthenaWorkgroup#bytes_scanned_cutoff_per_query}.
        :param enforce_workgroup_configuration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#enforce_workgroup_configuration AthenaWorkgroup#enforce_workgroup_configuration}.
        :param engine_version: engine_version block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#engine_version AthenaWorkgroup#engine_version}
        :param publish_cloudwatch_metrics_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#publish_cloudwatch_metrics_enabled AthenaWorkgroup#publish_cloudwatch_metrics_enabled}.
        :param requester_pays_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#requester_pays_enabled AthenaWorkgroup#requester_pays_enabled}.
        :param result_configuration: result_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#result_configuration AthenaWorkgroup#result_configuration}
        '''
        value = AthenaWorkgroupConfiguration(
            bytes_scanned_cutoff_per_query=bytes_scanned_cutoff_per_query,
            enforce_workgroup_configuration=enforce_workgroup_configuration,
            engine_version=engine_version,
            publish_cloudwatch_metrics_enabled=publish_cloudwatch_metrics_enabled,
            requester_pays_enabled=requester_pays_enabled,
            result_configuration=result_configuration,
        )

        return typing.cast(None, jsii.invoke(self, "putConfiguration", [value]))

    @jsii.member(jsii_name="resetConfiguration")
    def reset_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfiguration", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetForceDestroy")
    def reset_force_destroy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceDestroy", []))

    @jsii.member(jsii_name="resetState")
    def reset_state(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetState", []))

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
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configuration")
    def configuration(self) -> "AthenaWorkgroupConfigurationOutputReference":
        return typing.cast("AthenaWorkgroupConfigurationOutputReference", jsii.get(self, "configuration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationInput")
    def configuration_input(self) -> typing.Optional["AthenaWorkgroupConfiguration"]:
        return typing.cast(typing.Optional["AthenaWorkgroupConfiguration"], jsii.get(self, "configurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceDestroyInput")
    def force_destroy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "forceDestroyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stateInput")
    def state_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stateInput"))

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
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceDestroy")
    def force_destroy(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "forceDestroy"))

    @force_destroy.setter
    def force_destroy(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "forceDestroy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @state.setter
    def state(self, value: builtins.str) -> None:
        jsii.set(self, "state", value)

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
    jsii_type="@cdktf/provider-aws.athena.AthenaWorkgroupConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "configuration": "configuration",
        "description": "description",
        "force_destroy": "forceDestroy",
        "state": "state",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class AthenaWorkgroupConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        configuration: typing.Optional["AthenaWorkgroupConfiguration"] = None,
        description: typing.Optional[builtins.str] = None,
        force_destroy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        state: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''Amazon Athena.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#name AthenaWorkgroup#name}.
        :param configuration: configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#configuration AthenaWorkgroup#configuration}
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#description AthenaWorkgroup#description}.
        :param force_destroy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#force_destroy AthenaWorkgroup#force_destroy}.
        :param state: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#state AthenaWorkgroup#state}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#tags AthenaWorkgroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#tags_all AthenaWorkgroup#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(configuration, dict):
            configuration = AthenaWorkgroupConfiguration(**configuration)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if configuration is not None:
            self._values["configuration"] = configuration
        if description is not None:
            self._values["description"] = description
        if force_destroy is not None:
            self._values["force_destroy"] = force_destroy
        if state is not None:
            self._values["state"] = state
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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#name AthenaWorkgroup#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def configuration(self) -> typing.Optional["AthenaWorkgroupConfiguration"]:
        '''configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#configuration AthenaWorkgroup#configuration}
        '''
        result = self._values.get("configuration")
        return typing.cast(typing.Optional["AthenaWorkgroupConfiguration"], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#description AthenaWorkgroup#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def force_destroy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#force_destroy AthenaWorkgroup#force_destroy}.'''
        result = self._values.get("force_destroy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def state(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#state AthenaWorkgroup#state}.'''
        result = self._values.get("state")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#tags AthenaWorkgroup#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#tags_all AthenaWorkgroup#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AthenaWorkgroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.athena.AthenaWorkgroupConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "bytes_scanned_cutoff_per_query": "bytesScannedCutoffPerQuery",
        "enforce_workgroup_configuration": "enforceWorkgroupConfiguration",
        "engine_version": "engineVersion",
        "publish_cloudwatch_metrics_enabled": "publishCloudwatchMetricsEnabled",
        "requester_pays_enabled": "requesterPaysEnabled",
        "result_configuration": "resultConfiguration",
    },
)
class AthenaWorkgroupConfiguration:
    def __init__(
        self,
        *,
        bytes_scanned_cutoff_per_query: typing.Optional[jsii.Number] = None,
        enforce_workgroup_configuration: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        engine_version: typing.Optional["AthenaWorkgroupConfigurationEngineVersion"] = None,
        publish_cloudwatch_metrics_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        requester_pays_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        result_configuration: typing.Optional["AthenaWorkgroupConfigurationResultConfiguration"] = None,
    ) -> None:
        '''
        :param bytes_scanned_cutoff_per_query: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#bytes_scanned_cutoff_per_query AthenaWorkgroup#bytes_scanned_cutoff_per_query}.
        :param enforce_workgroup_configuration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#enforce_workgroup_configuration AthenaWorkgroup#enforce_workgroup_configuration}.
        :param engine_version: engine_version block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#engine_version AthenaWorkgroup#engine_version}
        :param publish_cloudwatch_metrics_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#publish_cloudwatch_metrics_enabled AthenaWorkgroup#publish_cloudwatch_metrics_enabled}.
        :param requester_pays_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#requester_pays_enabled AthenaWorkgroup#requester_pays_enabled}.
        :param result_configuration: result_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#result_configuration AthenaWorkgroup#result_configuration}
        '''
        if isinstance(engine_version, dict):
            engine_version = AthenaWorkgroupConfigurationEngineVersion(**engine_version)
        if isinstance(result_configuration, dict):
            result_configuration = AthenaWorkgroupConfigurationResultConfiguration(**result_configuration)
        self._values: typing.Dict[str, typing.Any] = {}
        if bytes_scanned_cutoff_per_query is not None:
            self._values["bytes_scanned_cutoff_per_query"] = bytes_scanned_cutoff_per_query
        if enforce_workgroup_configuration is not None:
            self._values["enforce_workgroup_configuration"] = enforce_workgroup_configuration
        if engine_version is not None:
            self._values["engine_version"] = engine_version
        if publish_cloudwatch_metrics_enabled is not None:
            self._values["publish_cloudwatch_metrics_enabled"] = publish_cloudwatch_metrics_enabled
        if requester_pays_enabled is not None:
            self._values["requester_pays_enabled"] = requester_pays_enabled
        if result_configuration is not None:
            self._values["result_configuration"] = result_configuration

    @builtins.property
    def bytes_scanned_cutoff_per_query(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#bytes_scanned_cutoff_per_query AthenaWorkgroup#bytes_scanned_cutoff_per_query}.'''
        result = self._values.get("bytes_scanned_cutoff_per_query")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def enforce_workgroup_configuration(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#enforce_workgroup_configuration AthenaWorkgroup#enforce_workgroup_configuration}.'''
        result = self._values.get("enforce_workgroup_configuration")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def engine_version(
        self,
    ) -> typing.Optional["AthenaWorkgroupConfigurationEngineVersion"]:
        '''engine_version block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#engine_version AthenaWorkgroup#engine_version}
        '''
        result = self._values.get("engine_version")
        return typing.cast(typing.Optional["AthenaWorkgroupConfigurationEngineVersion"], result)

    @builtins.property
    def publish_cloudwatch_metrics_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#publish_cloudwatch_metrics_enabled AthenaWorkgroup#publish_cloudwatch_metrics_enabled}.'''
        result = self._values.get("publish_cloudwatch_metrics_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def requester_pays_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#requester_pays_enabled AthenaWorkgroup#requester_pays_enabled}.'''
        result = self._values.get("requester_pays_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def result_configuration(
        self,
    ) -> typing.Optional["AthenaWorkgroupConfigurationResultConfiguration"]:
        '''result_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#result_configuration AthenaWorkgroup#result_configuration}
        '''
        result = self._values.get("result_configuration")
        return typing.cast(typing.Optional["AthenaWorkgroupConfigurationResultConfiguration"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AthenaWorkgroupConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.athena.AthenaWorkgroupConfigurationEngineVersion",
    jsii_struct_bases=[],
    name_mapping={"selected_engine_version": "selectedEngineVersion"},
)
class AthenaWorkgroupConfigurationEngineVersion:
    def __init__(
        self,
        *,
        selected_engine_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param selected_engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#selected_engine_version AthenaWorkgroup#selected_engine_version}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if selected_engine_version is not None:
            self._values["selected_engine_version"] = selected_engine_version

    @builtins.property
    def selected_engine_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#selected_engine_version AthenaWorkgroup#selected_engine_version}.'''
        result = self._values.get("selected_engine_version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AthenaWorkgroupConfigurationEngineVersion(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AthenaWorkgroupConfigurationEngineVersionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.athena.AthenaWorkgroupConfigurationEngineVersionOutputReference",
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

    @jsii.member(jsii_name="resetSelectedEngineVersion")
    def reset_selected_engine_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSelectedEngineVersion", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="selectedEngineVersionInput")
    def selected_engine_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "selectedEngineVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="selectedEngineVersion")
    def selected_engine_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "selectedEngineVersion"))

    @selected_engine_version.setter
    def selected_engine_version(self, value: builtins.str) -> None:
        jsii.set(self, "selectedEngineVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[AthenaWorkgroupConfigurationEngineVersion]:
        return typing.cast(typing.Optional[AthenaWorkgroupConfigurationEngineVersion], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AthenaWorkgroupConfigurationEngineVersion],
    ) -> None:
        jsii.set(self, "internalValue", value)


class AthenaWorkgroupConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.athena.AthenaWorkgroupConfigurationOutputReference",
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

    @jsii.member(jsii_name="putEngineVersion")
    def put_engine_version(
        self,
        *,
        selected_engine_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param selected_engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#selected_engine_version AthenaWorkgroup#selected_engine_version}.
        '''
        value = AthenaWorkgroupConfigurationEngineVersion(
            selected_engine_version=selected_engine_version
        )

        return typing.cast(None, jsii.invoke(self, "putEngineVersion", [value]))

    @jsii.member(jsii_name="putResultConfiguration")
    def put_result_configuration(
        self,
        *,
        encryption_configuration: typing.Optional["AthenaWorkgroupConfigurationResultConfigurationEncryptionConfiguration"] = None,
        output_location: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param encryption_configuration: encryption_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#encryption_configuration AthenaWorkgroup#encryption_configuration}
        :param output_location: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#output_location AthenaWorkgroup#output_location}.
        '''
        value = AthenaWorkgroupConfigurationResultConfiguration(
            encryption_configuration=encryption_configuration,
            output_location=output_location,
        )

        return typing.cast(None, jsii.invoke(self, "putResultConfiguration", [value]))

    @jsii.member(jsii_name="resetBytesScannedCutoffPerQuery")
    def reset_bytes_scanned_cutoff_per_query(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBytesScannedCutoffPerQuery", []))

    @jsii.member(jsii_name="resetEnforceWorkgroupConfiguration")
    def reset_enforce_workgroup_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnforceWorkgroupConfiguration", []))

    @jsii.member(jsii_name="resetEngineVersion")
    def reset_engine_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEngineVersion", []))

    @jsii.member(jsii_name="resetPublishCloudwatchMetricsEnabled")
    def reset_publish_cloudwatch_metrics_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublishCloudwatchMetricsEnabled", []))

    @jsii.member(jsii_name="resetRequesterPaysEnabled")
    def reset_requester_pays_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequesterPaysEnabled", []))

    @jsii.member(jsii_name="resetResultConfiguration")
    def reset_result_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResultConfiguration", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineVersion")
    def engine_version(
        self,
    ) -> AthenaWorkgroupConfigurationEngineVersionOutputReference:
        return typing.cast(AthenaWorkgroupConfigurationEngineVersionOutputReference, jsii.get(self, "engineVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resultConfiguration")
    def result_configuration(
        self,
    ) -> "AthenaWorkgroupConfigurationResultConfigurationOutputReference":
        return typing.cast("AthenaWorkgroupConfigurationResultConfigurationOutputReference", jsii.get(self, "resultConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bytesScannedCutoffPerQueryInput")
    def bytes_scanned_cutoff_per_query_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "bytesScannedCutoffPerQueryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enforceWorkgroupConfigurationInput")
    def enforce_workgroup_configuration_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enforceWorkgroupConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineVersionInput")
    def engine_version_input(
        self,
    ) -> typing.Optional[AthenaWorkgroupConfigurationEngineVersion]:
        return typing.cast(typing.Optional[AthenaWorkgroupConfigurationEngineVersion], jsii.get(self, "engineVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publishCloudwatchMetricsEnabledInput")
    def publish_cloudwatch_metrics_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "publishCloudwatchMetricsEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requesterPaysEnabledInput")
    def requester_pays_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "requesterPaysEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resultConfigurationInput")
    def result_configuration_input(
        self,
    ) -> typing.Optional["AthenaWorkgroupConfigurationResultConfiguration"]:
        return typing.cast(typing.Optional["AthenaWorkgroupConfigurationResultConfiguration"], jsii.get(self, "resultConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bytesScannedCutoffPerQuery")
    def bytes_scanned_cutoff_per_query(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bytesScannedCutoffPerQuery"))

    @bytes_scanned_cutoff_per_query.setter
    def bytes_scanned_cutoff_per_query(self, value: jsii.Number) -> None:
        jsii.set(self, "bytesScannedCutoffPerQuery", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enforceWorkgroupConfiguration")
    def enforce_workgroup_configuration(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enforceWorkgroupConfiguration"))

    @enforce_workgroup_configuration.setter
    def enforce_workgroup_configuration(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enforceWorkgroupConfiguration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publishCloudwatchMetricsEnabled")
    def publish_cloudwatch_metrics_enabled(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "publishCloudwatchMetricsEnabled"))

    @publish_cloudwatch_metrics_enabled.setter
    def publish_cloudwatch_metrics_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "publishCloudwatchMetricsEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requesterPaysEnabled")
    def requester_pays_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "requesterPaysEnabled"))

    @requester_pays_enabled.setter
    def requester_pays_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "requesterPaysEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AthenaWorkgroupConfiguration]:
        return typing.cast(typing.Optional[AthenaWorkgroupConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AthenaWorkgroupConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.athena.AthenaWorkgroupConfigurationResultConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "encryption_configuration": "encryptionConfiguration",
        "output_location": "outputLocation",
    },
)
class AthenaWorkgroupConfigurationResultConfiguration:
    def __init__(
        self,
        *,
        encryption_configuration: typing.Optional["AthenaWorkgroupConfigurationResultConfigurationEncryptionConfiguration"] = None,
        output_location: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param encryption_configuration: encryption_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#encryption_configuration AthenaWorkgroup#encryption_configuration}
        :param output_location: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#output_location AthenaWorkgroup#output_location}.
        '''
        if isinstance(encryption_configuration, dict):
            encryption_configuration = AthenaWorkgroupConfigurationResultConfigurationEncryptionConfiguration(**encryption_configuration)
        self._values: typing.Dict[str, typing.Any] = {}
        if encryption_configuration is not None:
            self._values["encryption_configuration"] = encryption_configuration
        if output_location is not None:
            self._values["output_location"] = output_location

    @builtins.property
    def encryption_configuration(
        self,
    ) -> typing.Optional["AthenaWorkgroupConfigurationResultConfigurationEncryptionConfiguration"]:
        '''encryption_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#encryption_configuration AthenaWorkgroup#encryption_configuration}
        '''
        result = self._values.get("encryption_configuration")
        return typing.cast(typing.Optional["AthenaWorkgroupConfigurationResultConfigurationEncryptionConfiguration"], result)

    @builtins.property
    def output_location(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#output_location AthenaWorkgroup#output_location}.'''
        result = self._values.get("output_location")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AthenaWorkgroupConfigurationResultConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.athena.AthenaWorkgroupConfigurationResultConfigurationEncryptionConfiguration",
    jsii_struct_bases=[],
    name_mapping={"encryption_option": "encryptionOption", "kms_key_arn": "kmsKeyArn"},
)
class AthenaWorkgroupConfigurationResultConfigurationEncryptionConfiguration:
    def __init__(
        self,
        *,
        encryption_option: typing.Optional[builtins.str] = None,
        kms_key_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param encryption_option: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#encryption_option AthenaWorkgroup#encryption_option}.
        :param kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#kms_key_arn AthenaWorkgroup#kms_key_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if encryption_option is not None:
            self._values["encryption_option"] = encryption_option
        if kms_key_arn is not None:
            self._values["kms_key_arn"] = kms_key_arn

    @builtins.property
    def encryption_option(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#encryption_option AthenaWorkgroup#encryption_option}.'''
        result = self._values.get("encryption_option")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#kms_key_arn AthenaWorkgroup#kms_key_arn}.'''
        result = self._values.get("kms_key_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AthenaWorkgroupConfigurationResultConfigurationEncryptionConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AthenaWorkgroupConfigurationResultConfigurationEncryptionConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.athena.AthenaWorkgroupConfigurationResultConfigurationEncryptionConfigurationOutputReference",
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

    @jsii.member(jsii_name="resetEncryptionOption")
    def reset_encryption_option(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionOption", []))

    @jsii.member(jsii_name="resetKmsKeyArn")
    def reset_kms_key_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyArn", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionOptionInput")
    def encryption_option_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encryptionOptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyArnInput")
    def kms_key_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionOption")
    def encryption_option(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptionOption"))

    @encryption_option.setter
    def encryption_option(self, value: builtins.str) -> None:
        jsii.set(self, "encryptionOption", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyArn")
    def kms_key_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyArn"))

    @kms_key_arn.setter
    def kms_key_arn(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[AthenaWorkgroupConfigurationResultConfigurationEncryptionConfiguration]:
        return typing.cast(typing.Optional[AthenaWorkgroupConfigurationResultConfigurationEncryptionConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AthenaWorkgroupConfigurationResultConfigurationEncryptionConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


class AthenaWorkgroupConfigurationResultConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.athena.AthenaWorkgroupConfigurationResultConfigurationOutputReference",
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

    @jsii.member(jsii_name="putEncryptionConfiguration")
    def put_encryption_configuration(
        self,
        *,
        encryption_option: typing.Optional[builtins.str] = None,
        kms_key_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param encryption_option: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#encryption_option AthenaWorkgroup#encryption_option}.
        :param kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/athena_workgroup#kms_key_arn AthenaWorkgroup#kms_key_arn}.
        '''
        value = AthenaWorkgroupConfigurationResultConfigurationEncryptionConfiguration(
            encryption_option=encryption_option, kms_key_arn=kms_key_arn
        )

        return typing.cast(None, jsii.invoke(self, "putEncryptionConfiguration", [value]))

    @jsii.member(jsii_name="resetEncryptionConfiguration")
    def reset_encryption_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionConfiguration", []))

    @jsii.member(jsii_name="resetOutputLocation")
    def reset_output_location(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOutputLocation", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionConfiguration")
    def encryption_configuration(
        self,
    ) -> AthenaWorkgroupConfigurationResultConfigurationEncryptionConfigurationOutputReference:
        return typing.cast(AthenaWorkgroupConfigurationResultConfigurationEncryptionConfigurationOutputReference, jsii.get(self, "encryptionConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionConfigurationInput")
    def encryption_configuration_input(
        self,
    ) -> typing.Optional[AthenaWorkgroupConfigurationResultConfigurationEncryptionConfiguration]:
        return typing.cast(typing.Optional[AthenaWorkgroupConfigurationResultConfigurationEncryptionConfiguration], jsii.get(self, "encryptionConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputLocationInput")
    def output_location_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "outputLocationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputLocation")
    def output_location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outputLocation"))

    @output_location.setter
    def output_location(self, value: builtins.str) -> None:
        jsii.set(self, "outputLocation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[AthenaWorkgroupConfigurationResultConfiguration]:
        return typing.cast(typing.Optional[AthenaWorkgroupConfigurationResultConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AthenaWorkgroupConfigurationResultConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


__all__ = [
    "AthenaDatabase",
    "AthenaDatabaseConfig",
    "AthenaDatabaseEncryptionConfiguration",
    "AthenaDatabaseEncryptionConfigurationOutputReference",
    "AthenaNamedQuery",
    "AthenaNamedQueryConfig",
    "AthenaWorkgroup",
    "AthenaWorkgroupConfig",
    "AthenaWorkgroupConfiguration",
    "AthenaWorkgroupConfigurationEngineVersion",
    "AthenaWorkgroupConfigurationEngineVersionOutputReference",
    "AthenaWorkgroupConfigurationOutputReference",
    "AthenaWorkgroupConfigurationResultConfiguration",
    "AthenaWorkgroupConfigurationResultConfigurationEncryptionConfiguration",
    "AthenaWorkgroupConfigurationResultConfigurationEncryptionConfigurationOutputReference",
    "AthenaWorkgroupConfigurationResultConfigurationOutputReference",
]

publication.publish()
