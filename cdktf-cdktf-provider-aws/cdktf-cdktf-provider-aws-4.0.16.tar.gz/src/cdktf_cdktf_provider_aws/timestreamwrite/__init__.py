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


class TimestreamwriteDatabase(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.timestreamwrite.TimestreamwriteDatabase",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_database aws_timestreamwrite_database}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        database_name: builtins.str,
        kms_key_id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_database aws_timestreamwrite_database} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param database_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_database#database_name TimestreamwriteDatabase#database_name}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_database#kms_key_id TimestreamwriteDatabase#kms_key_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_database#tags TimestreamwriteDatabase#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_database#tags_all TimestreamwriteDatabase#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = TimestreamwriteDatabaseConfig(
            database_name=database_name,
            kms_key_id=kms_key_id,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetKmsKeyId")
    def reset_kms_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyId", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tableCount")
    def table_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tableCount"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseNameInput")
    def database_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyIdInput")
    def kms_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyIdInput"))

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
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "databaseName"))

    @database_name.setter
    def database_name(self, value: builtins.str) -> None:
        jsii.set(self, "databaseName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @kms_key_id.setter
    def kms_key_id(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyId", value)

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
    jsii_type="@cdktf/provider-aws.timestreamwrite.TimestreamwriteDatabaseConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "database_name": "databaseName",
        "kms_key_id": "kmsKeyId",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class TimestreamwriteDatabaseConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        database_name: builtins.str,
        kms_key_id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Timestream Write.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param database_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_database#database_name TimestreamwriteDatabase#database_name}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_database#kms_key_id TimestreamwriteDatabase#kms_key_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_database#tags TimestreamwriteDatabase#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_database#tags_all TimestreamwriteDatabase#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "database_name": database_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if kms_key_id is not None:
            self._values["kms_key_id"] = kms_key_id
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
    def database_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_database#database_name TimestreamwriteDatabase#database_name}.'''
        result = self._values.get("database_name")
        assert result is not None, "Required property 'database_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_database#kms_key_id TimestreamwriteDatabase#kms_key_id}.'''
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_database#tags TimestreamwriteDatabase#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_database#tags_all TimestreamwriteDatabase#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TimestreamwriteDatabaseConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TimestreamwriteTable(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.timestreamwrite.TimestreamwriteTable",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table aws_timestreamwrite_table}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        database_name: builtins.str,
        table_name: builtins.str,
        magnetic_store_write_properties: typing.Optional["TimestreamwriteTableMagneticStoreWriteProperties"] = None,
        retention_properties: typing.Optional["TimestreamwriteTableRetentionProperties"] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table aws_timestreamwrite_table} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param database_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#database_name TimestreamwriteTable#database_name}.
        :param table_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#table_name TimestreamwriteTable#table_name}.
        :param magnetic_store_write_properties: magnetic_store_write_properties block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#magnetic_store_write_properties TimestreamwriteTable#magnetic_store_write_properties}
        :param retention_properties: retention_properties block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#retention_properties TimestreamwriteTable#retention_properties}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#tags TimestreamwriteTable#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#tags_all TimestreamwriteTable#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = TimestreamwriteTableConfig(
            database_name=database_name,
            table_name=table_name,
            magnetic_store_write_properties=magnetic_store_write_properties,
            retention_properties=retention_properties,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putMagneticStoreWriteProperties")
    def put_magnetic_store_write_properties(
        self,
        *,
        enable_magnetic_store_writes: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        magnetic_store_rejected_data_location: typing.Optional["TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocation"] = None,
    ) -> None:
        '''
        :param enable_magnetic_store_writes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#enable_magnetic_store_writes TimestreamwriteTable#enable_magnetic_store_writes}.
        :param magnetic_store_rejected_data_location: magnetic_store_rejected_data_location block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#magnetic_store_rejected_data_location TimestreamwriteTable#magnetic_store_rejected_data_location}
        '''
        value = TimestreamwriteTableMagneticStoreWriteProperties(
            enable_magnetic_store_writes=enable_magnetic_store_writes,
            magnetic_store_rejected_data_location=magnetic_store_rejected_data_location,
        )

        return typing.cast(None, jsii.invoke(self, "putMagneticStoreWriteProperties", [value]))

    @jsii.member(jsii_name="putRetentionProperties")
    def put_retention_properties(
        self,
        *,
        magnetic_store_retention_period_in_days: jsii.Number,
        memory_store_retention_period_in_hours: jsii.Number,
    ) -> None:
        '''
        :param magnetic_store_retention_period_in_days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#magnetic_store_retention_period_in_days TimestreamwriteTable#magnetic_store_retention_period_in_days}.
        :param memory_store_retention_period_in_hours: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#memory_store_retention_period_in_hours TimestreamwriteTable#memory_store_retention_period_in_hours}.
        '''
        value = TimestreamwriteTableRetentionProperties(
            magnetic_store_retention_period_in_days=magnetic_store_retention_period_in_days,
            memory_store_retention_period_in_hours=memory_store_retention_period_in_hours,
        )

        return typing.cast(None, jsii.invoke(self, "putRetentionProperties", [value]))

    @jsii.member(jsii_name="resetMagneticStoreWriteProperties")
    def reset_magnetic_store_write_properties(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMagneticStoreWriteProperties", []))

    @jsii.member(jsii_name="resetRetentionProperties")
    def reset_retention_properties(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetentionProperties", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="magneticStoreWriteProperties")
    def magnetic_store_write_properties(
        self,
    ) -> "TimestreamwriteTableMagneticStoreWritePropertiesOutputReference":
        return typing.cast("TimestreamwriteTableMagneticStoreWritePropertiesOutputReference", jsii.get(self, "magneticStoreWriteProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retentionProperties")
    def retention_properties(
        self,
    ) -> "TimestreamwriteTableRetentionPropertiesOutputReference":
        return typing.cast("TimestreamwriteTableRetentionPropertiesOutputReference", jsii.get(self, "retentionProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseNameInput")
    def database_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="magneticStoreWritePropertiesInput")
    def magnetic_store_write_properties_input(
        self,
    ) -> typing.Optional["TimestreamwriteTableMagneticStoreWriteProperties"]:
        return typing.cast(typing.Optional["TimestreamwriteTableMagneticStoreWriteProperties"], jsii.get(self, "magneticStoreWritePropertiesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retentionPropertiesInput")
    def retention_properties_input(
        self,
    ) -> typing.Optional["TimestreamwriteTableRetentionProperties"]:
        return typing.cast(typing.Optional["TimestreamwriteTableRetentionProperties"], jsii.get(self, "retentionPropertiesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tableNameInput")
    def table_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tableNameInput"))

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
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "databaseName"))

    @database_name.setter
    def database_name(self, value: builtins.str) -> None:
        jsii.set(self, "databaseName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tableName")
    def table_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tableName"))

    @table_name.setter
    def table_name(self, value: builtins.str) -> None:
        jsii.set(self, "tableName", value)

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
    jsii_type="@cdktf/provider-aws.timestreamwrite.TimestreamwriteTableConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "database_name": "databaseName",
        "table_name": "tableName",
        "magnetic_store_write_properties": "magneticStoreWriteProperties",
        "retention_properties": "retentionProperties",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class TimestreamwriteTableConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        database_name: builtins.str,
        table_name: builtins.str,
        magnetic_store_write_properties: typing.Optional["TimestreamwriteTableMagneticStoreWriteProperties"] = None,
        retention_properties: typing.Optional["TimestreamwriteTableRetentionProperties"] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Timestream Write.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param database_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#database_name TimestreamwriteTable#database_name}.
        :param table_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#table_name TimestreamwriteTable#table_name}.
        :param magnetic_store_write_properties: magnetic_store_write_properties block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#magnetic_store_write_properties TimestreamwriteTable#magnetic_store_write_properties}
        :param retention_properties: retention_properties block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#retention_properties TimestreamwriteTable#retention_properties}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#tags TimestreamwriteTable#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#tags_all TimestreamwriteTable#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(magnetic_store_write_properties, dict):
            magnetic_store_write_properties = TimestreamwriteTableMagneticStoreWriteProperties(**magnetic_store_write_properties)
        if isinstance(retention_properties, dict):
            retention_properties = TimestreamwriteTableRetentionProperties(**retention_properties)
        self._values: typing.Dict[str, typing.Any] = {
            "database_name": database_name,
            "table_name": table_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if magnetic_store_write_properties is not None:
            self._values["magnetic_store_write_properties"] = magnetic_store_write_properties
        if retention_properties is not None:
            self._values["retention_properties"] = retention_properties
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
    def database_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#database_name TimestreamwriteTable#database_name}.'''
        result = self._values.get("database_name")
        assert result is not None, "Required property 'database_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def table_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#table_name TimestreamwriteTable#table_name}.'''
        result = self._values.get("table_name")
        assert result is not None, "Required property 'table_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def magnetic_store_write_properties(
        self,
    ) -> typing.Optional["TimestreamwriteTableMagneticStoreWriteProperties"]:
        '''magnetic_store_write_properties block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#magnetic_store_write_properties TimestreamwriteTable#magnetic_store_write_properties}
        '''
        result = self._values.get("magnetic_store_write_properties")
        return typing.cast(typing.Optional["TimestreamwriteTableMagneticStoreWriteProperties"], result)

    @builtins.property
    def retention_properties(
        self,
    ) -> typing.Optional["TimestreamwriteTableRetentionProperties"]:
        '''retention_properties block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#retention_properties TimestreamwriteTable#retention_properties}
        '''
        result = self._values.get("retention_properties")
        return typing.cast(typing.Optional["TimestreamwriteTableRetentionProperties"], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#tags TimestreamwriteTable#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#tags_all TimestreamwriteTable#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TimestreamwriteTableConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.timestreamwrite.TimestreamwriteTableMagneticStoreWriteProperties",
    jsii_struct_bases=[],
    name_mapping={
        "enable_magnetic_store_writes": "enableMagneticStoreWrites",
        "magnetic_store_rejected_data_location": "magneticStoreRejectedDataLocation",
    },
)
class TimestreamwriteTableMagneticStoreWriteProperties:
    def __init__(
        self,
        *,
        enable_magnetic_store_writes: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        magnetic_store_rejected_data_location: typing.Optional["TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocation"] = None,
    ) -> None:
        '''
        :param enable_magnetic_store_writes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#enable_magnetic_store_writes TimestreamwriteTable#enable_magnetic_store_writes}.
        :param magnetic_store_rejected_data_location: magnetic_store_rejected_data_location block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#magnetic_store_rejected_data_location TimestreamwriteTable#magnetic_store_rejected_data_location}
        '''
        if isinstance(magnetic_store_rejected_data_location, dict):
            magnetic_store_rejected_data_location = TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocation(**magnetic_store_rejected_data_location)
        self._values: typing.Dict[str, typing.Any] = {}
        if enable_magnetic_store_writes is not None:
            self._values["enable_magnetic_store_writes"] = enable_magnetic_store_writes
        if magnetic_store_rejected_data_location is not None:
            self._values["magnetic_store_rejected_data_location"] = magnetic_store_rejected_data_location

    @builtins.property
    def enable_magnetic_store_writes(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#enable_magnetic_store_writes TimestreamwriteTable#enable_magnetic_store_writes}.'''
        result = self._values.get("enable_magnetic_store_writes")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def magnetic_store_rejected_data_location(
        self,
    ) -> typing.Optional["TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocation"]:
        '''magnetic_store_rejected_data_location block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#magnetic_store_rejected_data_location TimestreamwriteTable#magnetic_store_rejected_data_location}
        '''
        result = self._values.get("magnetic_store_rejected_data_location")
        return typing.cast(typing.Optional["TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocation"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TimestreamwriteTableMagneticStoreWriteProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.timestreamwrite.TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocation",
    jsii_struct_bases=[],
    name_mapping={"s3_configuration": "s3Configuration"},
)
class TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocation:
    def __init__(
        self,
        *,
        s3_configuration: typing.Optional["TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocationS3Configuration"] = None,
    ) -> None:
        '''
        :param s3_configuration: s3_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#s3_configuration TimestreamwriteTable#s3_configuration}
        '''
        if isinstance(s3_configuration, dict):
            s3_configuration = TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocationS3Configuration(**s3_configuration)
        self._values: typing.Dict[str, typing.Any] = {}
        if s3_configuration is not None:
            self._values["s3_configuration"] = s3_configuration

    @builtins.property
    def s3_configuration(
        self,
    ) -> typing.Optional["TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocationS3Configuration"]:
        '''s3_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#s3_configuration TimestreamwriteTable#s3_configuration}
        '''
        result = self._values.get("s3_configuration")
        return typing.cast(typing.Optional["TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocationS3Configuration"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.timestreamwrite.TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocationOutputReference",
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

    @jsii.member(jsii_name="putS3Configuration")
    def put_s3_configuration(
        self,
        *,
        bucket_name: typing.Optional[builtins.str] = None,
        encryption_option: typing.Optional[builtins.str] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        object_key_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#bucket_name TimestreamwriteTable#bucket_name}.
        :param encryption_option: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#encryption_option TimestreamwriteTable#encryption_option}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#kms_key_id TimestreamwriteTable#kms_key_id}.
        :param object_key_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#object_key_prefix TimestreamwriteTable#object_key_prefix}.
        '''
        value = TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocationS3Configuration(
            bucket_name=bucket_name,
            encryption_option=encryption_option,
            kms_key_id=kms_key_id,
            object_key_prefix=object_key_prefix,
        )

        return typing.cast(None, jsii.invoke(self, "putS3Configuration", [value]))

    @jsii.member(jsii_name="resetS3Configuration")
    def reset_s3_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3Configuration", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Configuration")
    def s3_configuration(
        self,
    ) -> "TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocationS3ConfigurationOutputReference":
        return typing.cast("TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocationS3ConfigurationOutputReference", jsii.get(self, "s3Configuration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3ConfigurationInput")
    def s3_configuration_input(
        self,
    ) -> typing.Optional["TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocationS3Configuration"]:
        return typing.cast(typing.Optional["TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocationS3Configuration"], jsii.get(self, "s3ConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocation]:
        return typing.cast(typing.Optional[TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocation],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.timestreamwrite.TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocationS3Configuration",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_name": "bucketName",
        "encryption_option": "encryptionOption",
        "kms_key_id": "kmsKeyId",
        "object_key_prefix": "objectKeyPrefix",
    },
)
class TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocationS3Configuration:
    def __init__(
        self,
        *,
        bucket_name: typing.Optional[builtins.str] = None,
        encryption_option: typing.Optional[builtins.str] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        object_key_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#bucket_name TimestreamwriteTable#bucket_name}.
        :param encryption_option: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#encryption_option TimestreamwriteTable#encryption_option}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#kms_key_id TimestreamwriteTable#kms_key_id}.
        :param object_key_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#object_key_prefix TimestreamwriteTable#object_key_prefix}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if bucket_name is not None:
            self._values["bucket_name"] = bucket_name
        if encryption_option is not None:
            self._values["encryption_option"] = encryption_option
        if kms_key_id is not None:
            self._values["kms_key_id"] = kms_key_id
        if object_key_prefix is not None:
            self._values["object_key_prefix"] = object_key_prefix

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#bucket_name TimestreamwriteTable#bucket_name}.'''
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption_option(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#encryption_option TimestreamwriteTable#encryption_option}.'''
        result = self._values.get("encryption_option")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#kms_key_id TimestreamwriteTable#kms_key_id}.'''
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def object_key_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#object_key_prefix TimestreamwriteTable#object_key_prefix}.'''
        result = self._values.get("object_key_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocationS3Configuration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocationS3ConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.timestreamwrite.TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocationS3ConfigurationOutputReference",
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

    @jsii.member(jsii_name="resetBucketName")
    def reset_bucket_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBucketName", []))

    @jsii.member(jsii_name="resetEncryptionOption")
    def reset_encryption_option(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionOption", []))

    @jsii.member(jsii_name="resetKmsKeyId")
    def reset_kms_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyId", []))

    @jsii.member(jsii_name="resetObjectKeyPrefix")
    def reset_object_key_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetObjectKeyPrefix", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketNameInput")
    def bucket_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionOptionInput")
    def encryption_option_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encryptionOptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyIdInput")
    def kms_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectKeyPrefixInput")
    def object_key_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "objectKeyPrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketName"))

    @bucket_name.setter
    def bucket_name(self, value: builtins.str) -> None:
        jsii.set(self, "bucketName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionOption")
    def encryption_option(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptionOption"))

    @encryption_option.setter
    def encryption_option(self, value: builtins.str) -> None:
        jsii.set(self, "encryptionOption", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @kms_key_id.setter
    def kms_key_id(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectKeyPrefix")
    def object_key_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "objectKeyPrefix"))

    @object_key_prefix.setter
    def object_key_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "objectKeyPrefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocationS3Configuration]:
        return typing.cast(typing.Optional[TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocationS3Configuration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocationS3Configuration],
    ) -> None:
        jsii.set(self, "internalValue", value)


class TimestreamwriteTableMagneticStoreWritePropertiesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.timestreamwrite.TimestreamwriteTableMagneticStoreWritePropertiesOutputReference",
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

    @jsii.member(jsii_name="putMagneticStoreRejectedDataLocation")
    def put_magnetic_store_rejected_data_location(
        self,
        *,
        s3_configuration: typing.Optional[TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocationS3Configuration] = None,
    ) -> None:
        '''
        :param s3_configuration: s3_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#s3_configuration TimestreamwriteTable#s3_configuration}
        '''
        value = TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocation(
            s3_configuration=s3_configuration
        )

        return typing.cast(None, jsii.invoke(self, "putMagneticStoreRejectedDataLocation", [value]))

    @jsii.member(jsii_name="resetEnableMagneticStoreWrites")
    def reset_enable_magnetic_store_writes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableMagneticStoreWrites", []))

    @jsii.member(jsii_name="resetMagneticStoreRejectedDataLocation")
    def reset_magnetic_store_rejected_data_location(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMagneticStoreRejectedDataLocation", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="magneticStoreRejectedDataLocation")
    def magnetic_store_rejected_data_location(
        self,
    ) -> TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocationOutputReference:
        return typing.cast(TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocationOutputReference, jsii.get(self, "magneticStoreRejectedDataLocation"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableMagneticStoreWritesInput")
    def enable_magnetic_store_writes_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enableMagneticStoreWritesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="magneticStoreRejectedDataLocationInput")
    def magnetic_store_rejected_data_location_input(
        self,
    ) -> typing.Optional[TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocation]:
        return typing.cast(typing.Optional[TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocation], jsii.get(self, "magneticStoreRejectedDataLocationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableMagneticStoreWrites")
    def enable_magnetic_store_writes(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enableMagneticStoreWrites"))

    @enable_magnetic_store_writes.setter
    def enable_magnetic_store_writes(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enableMagneticStoreWrites", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[TimestreamwriteTableMagneticStoreWriteProperties]:
        return typing.cast(typing.Optional[TimestreamwriteTableMagneticStoreWriteProperties], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[TimestreamwriteTableMagneticStoreWriteProperties],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.timestreamwrite.TimestreamwriteTableRetentionProperties",
    jsii_struct_bases=[],
    name_mapping={
        "magnetic_store_retention_period_in_days": "magneticStoreRetentionPeriodInDays",
        "memory_store_retention_period_in_hours": "memoryStoreRetentionPeriodInHours",
    },
)
class TimestreamwriteTableRetentionProperties:
    def __init__(
        self,
        *,
        magnetic_store_retention_period_in_days: jsii.Number,
        memory_store_retention_period_in_hours: jsii.Number,
    ) -> None:
        '''
        :param magnetic_store_retention_period_in_days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#magnetic_store_retention_period_in_days TimestreamwriteTable#magnetic_store_retention_period_in_days}.
        :param memory_store_retention_period_in_hours: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#memory_store_retention_period_in_hours TimestreamwriteTable#memory_store_retention_period_in_hours}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "magnetic_store_retention_period_in_days": magnetic_store_retention_period_in_days,
            "memory_store_retention_period_in_hours": memory_store_retention_period_in_hours,
        }

    @builtins.property
    def magnetic_store_retention_period_in_days(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#magnetic_store_retention_period_in_days TimestreamwriteTable#magnetic_store_retention_period_in_days}.'''
        result = self._values.get("magnetic_store_retention_period_in_days")
        assert result is not None, "Required property 'magnetic_store_retention_period_in_days' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def memory_store_retention_period_in_hours(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/timestreamwrite_table#memory_store_retention_period_in_hours TimestreamwriteTable#memory_store_retention_period_in_hours}.'''
        result = self._values.get("memory_store_retention_period_in_hours")
        assert result is not None, "Required property 'memory_store_retention_period_in_hours' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TimestreamwriteTableRetentionProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TimestreamwriteTableRetentionPropertiesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.timestreamwrite.TimestreamwriteTableRetentionPropertiesOutputReference",
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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="magneticStoreRetentionPeriodInDaysInput")
    def magnetic_store_retention_period_in_days_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "magneticStoreRetentionPeriodInDaysInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="memoryStoreRetentionPeriodInHoursInput")
    def memory_store_retention_period_in_hours_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "memoryStoreRetentionPeriodInHoursInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="magneticStoreRetentionPeriodInDays")
    def magnetic_store_retention_period_in_days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "magneticStoreRetentionPeriodInDays"))

    @magnetic_store_retention_period_in_days.setter
    def magnetic_store_retention_period_in_days(self, value: jsii.Number) -> None:
        jsii.set(self, "magneticStoreRetentionPeriodInDays", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="memoryStoreRetentionPeriodInHours")
    def memory_store_retention_period_in_hours(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memoryStoreRetentionPeriodInHours"))

    @memory_store_retention_period_in_hours.setter
    def memory_store_retention_period_in_hours(self, value: jsii.Number) -> None:
        jsii.set(self, "memoryStoreRetentionPeriodInHours", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[TimestreamwriteTableRetentionProperties]:
        return typing.cast(typing.Optional[TimestreamwriteTableRetentionProperties], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[TimestreamwriteTableRetentionProperties],
    ) -> None:
        jsii.set(self, "internalValue", value)


__all__ = [
    "TimestreamwriteDatabase",
    "TimestreamwriteDatabaseConfig",
    "TimestreamwriteTable",
    "TimestreamwriteTableConfig",
    "TimestreamwriteTableMagneticStoreWriteProperties",
    "TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocation",
    "TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocationOutputReference",
    "TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocationS3Configuration",
    "TimestreamwriteTableMagneticStoreWritePropertiesMagneticStoreRejectedDataLocationS3ConfigurationOutputReference",
    "TimestreamwriteTableMagneticStoreWritePropertiesOutputReference",
    "TimestreamwriteTableRetentionProperties",
    "TimestreamwriteTableRetentionPropertiesOutputReference",
]

publication.publish()
