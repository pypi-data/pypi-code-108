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


class DataAwsDynamodbTable(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dynamodb.DataAwsDynamodbTable",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/dynamodb_table aws_dynamodb_table}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        server_side_encryption: typing.Optional["DataAwsDynamodbTableServerSideEncryption"] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/dynamodb_table aws_dynamodb_table} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/dynamodb_table#name DataAwsDynamodbTable#name}.
        :param server_side_encryption: server_side_encryption block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/dynamodb_table#server_side_encryption DataAwsDynamodbTable#server_side_encryption}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/dynamodb_table#tags DataAwsDynamodbTable#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsDynamodbTableConfig(
            name=name,
            server_side_encryption=server_side_encryption,
            tags=tags,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="attribute")
    def attribute(self, index: builtins.str) -> "DataAwsDynamodbTableAttribute":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsDynamodbTableAttribute", jsii.invoke(self, "attribute", [index]))

    @jsii.member(jsii_name="globalSecondaryIndex")
    def global_secondary_index(
        self,
        index: builtins.str,
    ) -> "DataAwsDynamodbTableGlobalSecondaryIndex":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsDynamodbTableGlobalSecondaryIndex", jsii.invoke(self, "globalSecondaryIndex", [index]))

    @jsii.member(jsii_name="localSecondaryIndex")
    def local_secondary_index(
        self,
        index: builtins.str,
    ) -> "DataAwsDynamodbTableLocalSecondaryIndex":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsDynamodbTableLocalSecondaryIndex", jsii.invoke(self, "localSecondaryIndex", [index]))

    @jsii.member(jsii_name="pointInTimeRecovery")
    def point_in_time_recovery(
        self,
        index: builtins.str,
    ) -> "DataAwsDynamodbTablePointInTimeRecovery":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsDynamodbTablePointInTimeRecovery", jsii.invoke(self, "pointInTimeRecovery", [index]))

    @jsii.member(jsii_name="putServerSideEncryption")
    def put_server_side_encryption(self) -> None:
        value = DataAwsDynamodbTableServerSideEncryption()

        return typing.cast(None, jsii.invoke(self, "putServerSideEncryption", [value]))

    @jsii.member(jsii_name="replica")
    def replica(self, index: builtins.str) -> "DataAwsDynamodbTableReplica":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsDynamodbTableReplica", jsii.invoke(self, "replica", [index]))

    @jsii.member(jsii_name="resetServerSideEncryption")
    def reset_server_side_encryption(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServerSideEncryption", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="ttl")
    def ttl(self, index: builtins.str) -> "DataAwsDynamodbTableTtl":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsDynamodbTableTtl", jsii.invoke(self, "ttl", [index]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="billingMode")
    def billing_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "billingMode"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hashKey")
    def hash_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hashKey"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rangeKey")
    def range_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rangeKey"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readCapacity")
    def read_capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "readCapacity"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverSideEncryption")
    def server_side_encryption(
        self,
    ) -> "DataAwsDynamodbTableServerSideEncryptionOutputReference":
        return typing.cast("DataAwsDynamodbTableServerSideEncryptionOutputReference", jsii.get(self, "serverSideEncryption"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="streamArn")
    def stream_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "streamArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="streamEnabled")
    def stream_enabled(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "streamEnabled"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="streamLabel")
    def stream_label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "streamLabel"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="streamViewType")
    def stream_view_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "streamViewType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tableClass")
    def table_class(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tableClass"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="writeCapacity")
    def write_capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "writeCapacity"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverSideEncryptionInput")
    def server_side_encryption_input(
        self,
    ) -> typing.Optional["DataAwsDynamodbTableServerSideEncryption"]:
        return typing.cast(typing.Optional["DataAwsDynamodbTableServerSideEncryption"], jsii.get(self, "serverSideEncryptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

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


class DataAwsDynamodbTableAttribute(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dynamodb.DataAwsDynamodbTableAttribute",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        complex_computed_list_index: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: -
        :param terraform_attribute: -
        :param complex_computed_list_index: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_computed_list_index])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dynamodb.DataAwsDynamodbTableConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "server_side_encryption": "serverSideEncryption",
        "tags": "tags",
    },
)
class DataAwsDynamodbTableConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        server_side_encryption: typing.Optional["DataAwsDynamodbTableServerSideEncryption"] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS DynamoDB.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/dynamodb_table#name DataAwsDynamodbTable#name}.
        :param server_side_encryption: server_side_encryption block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/dynamodb_table#server_side_encryption DataAwsDynamodbTable#server_side_encryption}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/dynamodb_table#tags DataAwsDynamodbTable#tags}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(server_side_encryption, dict):
            server_side_encryption = DataAwsDynamodbTableServerSideEncryption(**server_side_encryption)
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
        if server_side_encryption is not None:
            self._values["server_side_encryption"] = server_side_encryption
        if tags is not None:
            self._values["tags"] = tags

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/dynamodb_table#name DataAwsDynamodbTable#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def server_side_encryption(
        self,
    ) -> typing.Optional["DataAwsDynamodbTableServerSideEncryption"]:
        '''server_side_encryption block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/dynamodb_table#server_side_encryption DataAwsDynamodbTable#server_side_encryption}
        '''
        result = self._values.get("server_side_encryption")
        return typing.cast(typing.Optional["DataAwsDynamodbTableServerSideEncryption"], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/dynamodb_table#tags DataAwsDynamodbTable#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsDynamodbTableConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsDynamodbTableGlobalSecondaryIndex(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dynamodb.DataAwsDynamodbTableGlobalSecondaryIndex",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        complex_computed_list_index: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: -
        :param terraform_attribute: -
        :param complex_computed_list_index: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_computed_list_index])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hashKey")
    def hash_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hashKey"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nonKeyAttributes")
    def non_key_attributes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "nonKeyAttributes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="projectionType")
    def projection_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectionType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rangeKey")
    def range_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rangeKey"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readCapacity")
    def read_capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "readCapacity"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="writeCapacity")
    def write_capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "writeCapacity"))


class DataAwsDynamodbTableLocalSecondaryIndex(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dynamodb.DataAwsDynamodbTableLocalSecondaryIndex",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        complex_computed_list_index: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: -
        :param terraform_attribute: -
        :param complex_computed_list_index: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_computed_list_index])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nonKeyAttributes")
    def non_key_attributes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "nonKeyAttributes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="projectionType")
    def projection_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectionType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rangeKey")
    def range_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rangeKey"))


class DataAwsDynamodbTablePointInTimeRecovery(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dynamodb.DataAwsDynamodbTablePointInTimeRecovery",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        complex_computed_list_index: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: -
        :param terraform_attribute: -
        :param complex_computed_list_index: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_computed_list_index])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "enabled"))


class DataAwsDynamodbTableReplica(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dynamodb.DataAwsDynamodbTableReplica",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        complex_computed_list_index: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: -
        :param terraform_attribute: -
        :param complex_computed_list_index: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_computed_list_index])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyArn")
    def kms_key_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regionName")
    def region_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "regionName"))


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dynamodb.DataAwsDynamodbTableServerSideEncryption",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsDynamodbTableServerSideEncryption:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsDynamodbTableServerSideEncryption(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsDynamodbTableServerSideEncryptionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dynamodb.DataAwsDynamodbTableServerSideEncryptionOutputReference",
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
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataAwsDynamodbTableServerSideEncryption]:
        return typing.cast(typing.Optional[DataAwsDynamodbTableServerSideEncryption], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataAwsDynamodbTableServerSideEncryption],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsDynamodbTableTtl(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dynamodb.DataAwsDynamodbTableTtl",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        complex_computed_list_index: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: -
        :param terraform_attribute: -
        :param complex_computed_list_index: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_computed_list_index])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attributeName")
    def attribute_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "attributeName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "enabled"))


class DynamodbGlobalTable(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dynamodb.DynamodbGlobalTable",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_global_table aws_dynamodb_global_table}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        replica: typing.Sequence["DynamodbGlobalTableReplica"],
        timeouts: typing.Optional["DynamodbGlobalTableTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_global_table aws_dynamodb_global_table} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_global_table#name DynamodbGlobalTable#name}.
        :param replica: replica block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_global_table#replica DynamodbGlobalTable#replica}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_global_table#timeouts DynamodbGlobalTable#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DynamodbGlobalTableConfig(
            name=name,
            replica=replica,
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
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_global_table#create DynamodbGlobalTable#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_global_table#delete DynamodbGlobalTable#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_global_table#update DynamodbGlobalTable#update}.
        '''
        value = DynamodbGlobalTableTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

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
    def timeouts(self) -> "DynamodbGlobalTableTimeoutsOutputReference":
        return typing.cast("DynamodbGlobalTableTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicaInput")
    def replica_input(
        self,
    ) -> typing.Optional[typing.List["DynamodbGlobalTableReplica"]]:
        return typing.cast(typing.Optional[typing.List["DynamodbGlobalTableReplica"]], jsii.get(self, "replicaInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["DynamodbGlobalTableTimeouts"]:
        return typing.cast(typing.Optional["DynamodbGlobalTableTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replica")
    def replica(self) -> typing.List["DynamodbGlobalTableReplica"]:
        return typing.cast(typing.List["DynamodbGlobalTableReplica"], jsii.get(self, "replica"))

    @replica.setter
    def replica(self, value: typing.List["DynamodbGlobalTableReplica"]) -> None:
        jsii.set(self, "replica", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dynamodb.DynamodbGlobalTableConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "replica": "replica",
        "timeouts": "timeouts",
    },
)
class DynamodbGlobalTableConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        replica: typing.Sequence["DynamodbGlobalTableReplica"],
        timeouts: typing.Optional["DynamodbGlobalTableTimeouts"] = None,
    ) -> None:
        '''AWS DynamoDB.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_global_table#name DynamodbGlobalTable#name}.
        :param replica: replica block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_global_table#replica DynamodbGlobalTable#replica}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_global_table#timeouts DynamodbGlobalTable#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = DynamodbGlobalTableTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "replica": replica,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_global_table#name DynamodbGlobalTable#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def replica(self) -> typing.List["DynamodbGlobalTableReplica"]:
        '''replica block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_global_table#replica DynamodbGlobalTable#replica}
        '''
        result = self._values.get("replica")
        assert result is not None, "Required property 'replica' is missing"
        return typing.cast(typing.List["DynamodbGlobalTableReplica"], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["DynamodbGlobalTableTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_global_table#timeouts DynamodbGlobalTable#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["DynamodbGlobalTableTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamodbGlobalTableConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dynamodb.DynamodbGlobalTableReplica",
    jsii_struct_bases=[],
    name_mapping={"region_name": "regionName"},
)
class DynamodbGlobalTableReplica:
    def __init__(self, *, region_name: builtins.str) -> None:
        '''
        :param region_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_global_table#region_name DynamodbGlobalTable#region_name}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "region_name": region_name,
        }

    @builtins.property
    def region_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_global_table#region_name DynamodbGlobalTable#region_name}.'''
        result = self._values.get("region_name")
        assert result is not None, "Required property 'region_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamodbGlobalTableReplica(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dynamodb.DynamodbGlobalTableTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class DynamodbGlobalTableTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_global_table#create DynamodbGlobalTable#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_global_table#delete DynamodbGlobalTable#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_global_table#update DynamodbGlobalTable#update}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_global_table#create DynamodbGlobalTable#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_global_table#delete DynamodbGlobalTable#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_global_table#update DynamodbGlobalTable#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamodbGlobalTableTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DynamodbGlobalTableTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dynamodb.DynamodbGlobalTableTimeoutsOutputReference",
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
    def internal_value(self) -> typing.Optional[DynamodbGlobalTableTimeouts]:
        return typing.cast(typing.Optional[DynamodbGlobalTableTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DynamodbGlobalTableTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DynamodbKinesisStreamingDestination(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dynamodb.DynamodbKinesisStreamingDestination",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_kinesis_streaming_destination aws_dynamodb_kinesis_streaming_destination}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        stream_arn: builtins.str,
        table_name: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_kinesis_streaming_destination aws_dynamodb_kinesis_streaming_destination} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param stream_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_kinesis_streaming_destination#stream_arn DynamodbKinesisStreamingDestination#stream_arn}.
        :param table_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_kinesis_streaming_destination#table_name DynamodbKinesisStreamingDestination#table_name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DynamodbKinesisStreamingDestinationConfig(
            stream_arn=stream_arn,
            table_name=table_name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

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
    @jsii.member(jsii_name="streamArnInput")
    def stream_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "streamArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tableNameInput")
    def table_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tableNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="streamArn")
    def stream_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "streamArn"))

    @stream_arn.setter
    def stream_arn(self, value: builtins.str) -> None:
        jsii.set(self, "streamArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tableName")
    def table_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tableName"))

    @table_name.setter
    def table_name(self, value: builtins.str) -> None:
        jsii.set(self, "tableName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dynamodb.DynamodbKinesisStreamingDestinationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "stream_arn": "streamArn",
        "table_name": "tableName",
    },
)
class DynamodbKinesisStreamingDestinationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        stream_arn: builtins.str,
        table_name: builtins.str,
    ) -> None:
        '''AWS DynamoDB.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param stream_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_kinesis_streaming_destination#stream_arn DynamodbKinesisStreamingDestination#stream_arn}.
        :param table_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_kinesis_streaming_destination#table_name DynamodbKinesisStreamingDestination#table_name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "stream_arn": stream_arn,
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
    def stream_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_kinesis_streaming_destination#stream_arn DynamodbKinesisStreamingDestination#stream_arn}.'''
        result = self._values.get("stream_arn")
        assert result is not None, "Required property 'stream_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def table_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_kinesis_streaming_destination#table_name DynamodbKinesisStreamingDestination#table_name}.'''
        result = self._values.get("table_name")
        assert result is not None, "Required property 'table_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamodbKinesisStreamingDestinationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DynamodbTable(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dynamodb.DynamodbTable",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table aws_dynamodb_table}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        attribute: typing.Optional[typing.Sequence["DynamodbTableAttribute"]] = None,
        billing_mode: typing.Optional[builtins.str] = None,
        global_secondary_index: typing.Optional[typing.Sequence["DynamodbTableGlobalSecondaryIndex"]] = None,
        hash_key: typing.Optional[builtins.str] = None,
        local_secondary_index: typing.Optional[typing.Sequence["DynamodbTableLocalSecondaryIndex"]] = None,
        point_in_time_recovery: typing.Optional["DynamodbTablePointInTimeRecovery"] = None,
        range_key: typing.Optional[builtins.str] = None,
        read_capacity: typing.Optional[jsii.Number] = None,
        replica: typing.Optional[typing.Sequence["DynamodbTableReplica"]] = None,
        restore_date_time: typing.Optional[builtins.str] = None,
        restore_source_name: typing.Optional[builtins.str] = None,
        restore_to_latest_time: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        server_side_encryption: typing.Optional["DynamodbTableServerSideEncryption"] = None,
        stream_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        stream_view_type: typing.Optional[builtins.str] = None,
        table_class: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["DynamodbTableTimeouts"] = None,
        ttl: typing.Optional["DynamodbTableTtl"] = None,
        write_capacity: typing.Optional[jsii.Number] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table aws_dynamodb_table} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#name DynamodbTable#name}.
        :param attribute: attribute block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#attribute DynamodbTable#attribute}
        :param billing_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#billing_mode DynamodbTable#billing_mode}.
        :param global_secondary_index: global_secondary_index block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#global_secondary_index DynamodbTable#global_secondary_index}
        :param hash_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#hash_key DynamodbTable#hash_key}.
        :param local_secondary_index: local_secondary_index block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#local_secondary_index DynamodbTable#local_secondary_index}
        :param point_in_time_recovery: point_in_time_recovery block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#point_in_time_recovery DynamodbTable#point_in_time_recovery}
        :param range_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#range_key DynamodbTable#range_key}.
        :param read_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#read_capacity DynamodbTable#read_capacity}.
        :param replica: replica block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#replica DynamodbTable#replica}
        :param restore_date_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#restore_date_time DynamodbTable#restore_date_time}.
        :param restore_source_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#restore_source_name DynamodbTable#restore_source_name}.
        :param restore_to_latest_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#restore_to_latest_time DynamodbTable#restore_to_latest_time}.
        :param server_side_encryption: server_side_encryption block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#server_side_encryption DynamodbTable#server_side_encryption}
        :param stream_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#stream_enabled DynamodbTable#stream_enabled}.
        :param stream_view_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#stream_view_type DynamodbTable#stream_view_type}.
        :param table_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#table_class DynamodbTable#table_class}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#tags DynamodbTable#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#tags_all DynamodbTable#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#timeouts DynamodbTable#timeouts}
        :param ttl: ttl block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#ttl DynamodbTable#ttl}
        :param write_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#write_capacity DynamodbTable#write_capacity}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DynamodbTableConfig(
            name=name,
            attribute=attribute,
            billing_mode=billing_mode,
            global_secondary_index=global_secondary_index,
            hash_key=hash_key,
            local_secondary_index=local_secondary_index,
            point_in_time_recovery=point_in_time_recovery,
            range_key=range_key,
            read_capacity=read_capacity,
            replica=replica,
            restore_date_time=restore_date_time,
            restore_source_name=restore_source_name,
            restore_to_latest_time=restore_to_latest_time,
            server_side_encryption=server_side_encryption,
            stream_enabled=stream_enabled,
            stream_view_type=stream_view_type,
            table_class=table_class,
            tags=tags,
            tags_all=tags_all,
            timeouts=timeouts,
            ttl=ttl,
            write_capacity=write_capacity,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putPointInTimeRecovery")
    def put_point_in_time_recovery(
        self,
        *,
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#enabled DynamodbTable#enabled}.
        '''
        value = DynamodbTablePointInTimeRecovery(enabled=enabled)

        return typing.cast(None, jsii.invoke(self, "putPointInTimeRecovery", [value]))

    @jsii.member(jsii_name="putServerSideEncryption")
    def put_server_side_encryption(
        self,
        *,
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        kms_key_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#enabled DynamodbTable#enabled}.
        :param kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#kms_key_arn DynamodbTable#kms_key_arn}.
        '''
        value = DynamodbTableServerSideEncryption(
            enabled=enabled, kms_key_arn=kms_key_arn
        )

        return typing.cast(None, jsii.invoke(self, "putServerSideEncryption", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#create DynamodbTable#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#delete DynamodbTable#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#update DynamodbTable#update}.
        '''
        value = DynamodbTableTimeouts(create=create, delete=delete, update=update)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="putTtl")
    def put_ttl(
        self,
        *,
        attribute_name: builtins.str,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param attribute_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#attribute_name DynamodbTable#attribute_name}.
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#enabled DynamodbTable#enabled}.
        '''
        value = DynamodbTableTtl(attribute_name=attribute_name, enabled=enabled)

        return typing.cast(None, jsii.invoke(self, "putTtl", [value]))

    @jsii.member(jsii_name="resetAttribute")
    def reset_attribute(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAttribute", []))

    @jsii.member(jsii_name="resetBillingMode")
    def reset_billing_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBillingMode", []))

    @jsii.member(jsii_name="resetGlobalSecondaryIndex")
    def reset_global_secondary_index(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGlobalSecondaryIndex", []))

    @jsii.member(jsii_name="resetHashKey")
    def reset_hash_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHashKey", []))

    @jsii.member(jsii_name="resetLocalSecondaryIndex")
    def reset_local_secondary_index(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocalSecondaryIndex", []))

    @jsii.member(jsii_name="resetPointInTimeRecovery")
    def reset_point_in_time_recovery(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPointInTimeRecovery", []))

    @jsii.member(jsii_name="resetRangeKey")
    def reset_range_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRangeKey", []))

    @jsii.member(jsii_name="resetReadCapacity")
    def reset_read_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReadCapacity", []))

    @jsii.member(jsii_name="resetReplica")
    def reset_replica(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReplica", []))

    @jsii.member(jsii_name="resetRestoreDateTime")
    def reset_restore_date_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRestoreDateTime", []))

    @jsii.member(jsii_name="resetRestoreSourceName")
    def reset_restore_source_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRestoreSourceName", []))

    @jsii.member(jsii_name="resetRestoreToLatestTime")
    def reset_restore_to_latest_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRestoreToLatestTime", []))

    @jsii.member(jsii_name="resetServerSideEncryption")
    def reset_server_side_encryption(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServerSideEncryption", []))

    @jsii.member(jsii_name="resetStreamEnabled")
    def reset_stream_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStreamEnabled", []))

    @jsii.member(jsii_name="resetStreamViewType")
    def reset_stream_view_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStreamViewType", []))

    @jsii.member(jsii_name="resetTableClass")
    def reset_table_class(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTableClass", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="resetTtl")
    def reset_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTtl", []))

    @jsii.member(jsii_name="resetWriteCapacity")
    def reset_write_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWriteCapacity", []))

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
    @jsii.member(jsii_name="pointInTimeRecovery")
    def point_in_time_recovery(
        self,
    ) -> "DynamodbTablePointInTimeRecoveryOutputReference":
        return typing.cast("DynamodbTablePointInTimeRecoveryOutputReference", jsii.get(self, "pointInTimeRecovery"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverSideEncryption")
    def server_side_encryption(
        self,
    ) -> "DynamodbTableServerSideEncryptionOutputReference":
        return typing.cast("DynamodbTableServerSideEncryptionOutputReference", jsii.get(self, "serverSideEncryption"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="streamArn")
    def stream_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "streamArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="streamLabel")
    def stream_label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "streamLabel"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "DynamodbTableTimeoutsOutputReference":
        return typing.cast("DynamodbTableTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> "DynamodbTableTtlOutputReference":
        return typing.cast("DynamodbTableTtlOutputReference", jsii.get(self, "ttl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attributeInput")
    def attribute_input(self) -> typing.Optional[typing.List["DynamodbTableAttribute"]]:
        return typing.cast(typing.Optional[typing.List["DynamodbTableAttribute"]], jsii.get(self, "attributeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="billingModeInput")
    def billing_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "billingModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="globalSecondaryIndexInput")
    def global_secondary_index_input(
        self,
    ) -> typing.Optional[typing.List["DynamodbTableGlobalSecondaryIndex"]]:
        return typing.cast(typing.Optional[typing.List["DynamodbTableGlobalSecondaryIndex"]], jsii.get(self, "globalSecondaryIndexInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hashKeyInput")
    def hash_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hashKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="localSecondaryIndexInput")
    def local_secondary_index_input(
        self,
    ) -> typing.Optional[typing.List["DynamodbTableLocalSecondaryIndex"]]:
        return typing.cast(typing.Optional[typing.List["DynamodbTableLocalSecondaryIndex"]], jsii.get(self, "localSecondaryIndexInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pointInTimeRecoveryInput")
    def point_in_time_recovery_input(
        self,
    ) -> typing.Optional["DynamodbTablePointInTimeRecovery"]:
        return typing.cast(typing.Optional["DynamodbTablePointInTimeRecovery"], jsii.get(self, "pointInTimeRecoveryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rangeKeyInput")
    def range_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rangeKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readCapacityInput")
    def read_capacity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "readCapacityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicaInput")
    def replica_input(self) -> typing.Optional[typing.List["DynamodbTableReplica"]]:
        return typing.cast(typing.Optional[typing.List["DynamodbTableReplica"]], jsii.get(self, "replicaInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restoreDateTimeInput")
    def restore_date_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "restoreDateTimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restoreSourceNameInput")
    def restore_source_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "restoreSourceNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restoreToLatestTimeInput")
    def restore_to_latest_time_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "restoreToLatestTimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverSideEncryptionInput")
    def server_side_encryption_input(
        self,
    ) -> typing.Optional["DynamodbTableServerSideEncryption"]:
        return typing.cast(typing.Optional["DynamodbTableServerSideEncryption"], jsii.get(self, "serverSideEncryptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="streamEnabledInput")
    def stream_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "streamEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="streamViewTypeInput")
    def stream_view_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "streamViewTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tableClassInput")
    def table_class_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tableClassInput"))

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
    def timeouts_input(self) -> typing.Optional["DynamodbTableTimeouts"]:
        return typing.cast(typing.Optional["DynamodbTableTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ttlInput")
    def ttl_input(self) -> typing.Optional["DynamodbTableTtl"]:
        return typing.cast(typing.Optional["DynamodbTableTtl"], jsii.get(self, "ttlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="writeCapacityInput")
    def write_capacity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "writeCapacityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attribute")
    def attribute(self) -> typing.List["DynamodbTableAttribute"]:
        return typing.cast(typing.List["DynamodbTableAttribute"], jsii.get(self, "attribute"))

    @attribute.setter
    def attribute(self, value: typing.List["DynamodbTableAttribute"]) -> None:
        jsii.set(self, "attribute", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="billingMode")
    def billing_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "billingMode"))

    @billing_mode.setter
    def billing_mode(self, value: builtins.str) -> None:
        jsii.set(self, "billingMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="globalSecondaryIndex")
    def global_secondary_index(
        self,
    ) -> typing.List["DynamodbTableGlobalSecondaryIndex"]:
        return typing.cast(typing.List["DynamodbTableGlobalSecondaryIndex"], jsii.get(self, "globalSecondaryIndex"))

    @global_secondary_index.setter
    def global_secondary_index(
        self,
        value: typing.List["DynamodbTableGlobalSecondaryIndex"],
    ) -> None:
        jsii.set(self, "globalSecondaryIndex", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hashKey")
    def hash_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hashKey"))

    @hash_key.setter
    def hash_key(self, value: builtins.str) -> None:
        jsii.set(self, "hashKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="localSecondaryIndex")
    def local_secondary_index(self) -> typing.List["DynamodbTableLocalSecondaryIndex"]:
        return typing.cast(typing.List["DynamodbTableLocalSecondaryIndex"], jsii.get(self, "localSecondaryIndex"))

    @local_secondary_index.setter
    def local_secondary_index(
        self,
        value: typing.List["DynamodbTableLocalSecondaryIndex"],
    ) -> None:
        jsii.set(self, "localSecondaryIndex", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rangeKey")
    def range_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rangeKey"))

    @range_key.setter
    def range_key(self, value: builtins.str) -> None:
        jsii.set(self, "rangeKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readCapacity")
    def read_capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "readCapacity"))

    @read_capacity.setter
    def read_capacity(self, value: jsii.Number) -> None:
        jsii.set(self, "readCapacity", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replica")
    def replica(self) -> typing.List["DynamodbTableReplica"]:
        return typing.cast(typing.List["DynamodbTableReplica"], jsii.get(self, "replica"))

    @replica.setter
    def replica(self, value: typing.List["DynamodbTableReplica"]) -> None:
        jsii.set(self, "replica", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restoreDateTime")
    def restore_date_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "restoreDateTime"))

    @restore_date_time.setter
    def restore_date_time(self, value: builtins.str) -> None:
        jsii.set(self, "restoreDateTime", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restoreSourceName")
    def restore_source_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "restoreSourceName"))

    @restore_source_name.setter
    def restore_source_name(self, value: builtins.str) -> None:
        jsii.set(self, "restoreSourceName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restoreToLatestTime")
    def restore_to_latest_time(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "restoreToLatestTime"))

    @restore_to_latest_time.setter
    def restore_to_latest_time(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "restoreToLatestTime", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="streamEnabled")
    def stream_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "streamEnabled"))

    @stream_enabled.setter
    def stream_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "streamEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="streamViewType")
    def stream_view_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "streamViewType"))

    @stream_view_type.setter
    def stream_view_type(self, value: builtins.str) -> None:
        jsii.set(self, "streamViewType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tableClass")
    def table_class(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tableClass"))

    @table_class.setter
    def table_class(self, value: builtins.str) -> None:
        jsii.set(self, "tableClass", value)

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
    @jsii.member(jsii_name="writeCapacity")
    def write_capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "writeCapacity"))

    @write_capacity.setter
    def write_capacity(self, value: jsii.Number) -> None:
        jsii.set(self, "writeCapacity", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dynamodb.DynamodbTableAttribute",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "type": "type"},
)
class DynamodbTableAttribute:
    def __init__(self, *, name: builtins.str, type: builtins.str) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#name DynamodbTable#name}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#type DynamodbTable#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "type": type,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#name DynamodbTable#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#type DynamodbTable#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamodbTableAttribute(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dynamodb.DynamodbTableConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "attribute": "attribute",
        "billing_mode": "billingMode",
        "global_secondary_index": "globalSecondaryIndex",
        "hash_key": "hashKey",
        "local_secondary_index": "localSecondaryIndex",
        "point_in_time_recovery": "pointInTimeRecovery",
        "range_key": "rangeKey",
        "read_capacity": "readCapacity",
        "replica": "replica",
        "restore_date_time": "restoreDateTime",
        "restore_source_name": "restoreSourceName",
        "restore_to_latest_time": "restoreToLatestTime",
        "server_side_encryption": "serverSideEncryption",
        "stream_enabled": "streamEnabled",
        "stream_view_type": "streamViewType",
        "table_class": "tableClass",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
        "ttl": "ttl",
        "write_capacity": "writeCapacity",
    },
)
class DynamodbTableConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        attribute: typing.Optional[typing.Sequence[DynamodbTableAttribute]] = None,
        billing_mode: typing.Optional[builtins.str] = None,
        global_secondary_index: typing.Optional[typing.Sequence["DynamodbTableGlobalSecondaryIndex"]] = None,
        hash_key: typing.Optional[builtins.str] = None,
        local_secondary_index: typing.Optional[typing.Sequence["DynamodbTableLocalSecondaryIndex"]] = None,
        point_in_time_recovery: typing.Optional["DynamodbTablePointInTimeRecovery"] = None,
        range_key: typing.Optional[builtins.str] = None,
        read_capacity: typing.Optional[jsii.Number] = None,
        replica: typing.Optional[typing.Sequence["DynamodbTableReplica"]] = None,
        restore_date_time: typing.Optional[builtins.str] = None,
        restore_source_name: typing.Optional[builtins.str] = None,
        restore_to_latest_time: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        server_side_encryption: typing.Optional["DynamodbTableServerSideEncryption"] = None,
        stream_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        stream_view_type: typing.Optional[builtins.str] = None,
        table_class: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["DynamodbTableTimeouts"] = None,
        ttl: typing.Optional["DynamodbTableTtl"] = None,
        write_capacity: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''AWS DynamoDB.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#name DynamodbTable#name}.
        :param attribute: attribute block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#attribute DynamodbTable#attribute}
        :param billing_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#billing_mode DynamodbTable#billing_mode}.
        :param global_secondary_index: global_secondary_index block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#global_secondary_index DynamodbTable#global_secondary_index}
        :param hash_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#hash_key DynamodbTable#hash_key}.
        :param local_secondary_index: local_secondary_index block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#local_secondary_index DynamodbTable#local_secondary_index}
        :param point_in_time_recovery: point_in_time_recovery block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#point_in_time_recovery DynamodbTable#point_in_time_recovery}
        :param range_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#range_key DynamodbTable#range_key}.
        :param read_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#read_capacity DynamodbTable#read_capacity}.
        :param replica: replica block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#replica DynamodbTable#replica}
        :param restore_date_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#restore_date_time DynamodbTable#restore_date_time}.
        :param restore_source_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#restore_source_name DynamodbTable#restore_source_name}.
        :param restore_to_latest_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#restore_to_latest_time DynamodbTable#restore_to_latest_time}.
        :param server_side_encryption: server_side_encryption block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#server_side_encryption DynamodbTable#server_side_encryption}
        :param stream_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#stream_enabled DynamodbTable#stream_enabled}.
        :param stream_view_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#stream_view_type DynamodbTable#stream_view_type}.
        :param table_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#table_class DynamodbTable#table_class}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#tags DynamodbTable#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#tags_all DynamodbTable#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#timeouts DynamodbTable#timeouts}
        :param ttl: ttl block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#ttl DynamodbTable#ttl}
        :param write_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#write_capacity DynamodbTable#write_capacity}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(point_in_time_recovery, dict):
            point_in_time_recovery = DynamodbTablePointInTimeRecovery(**point_in_time_recovery)
        if isinstance(server_side_encryption, dict):
            server_side_encryption = DynamodbTableServerSideEncryption(**server_side_encryption)
        if isinstance(timeouts, dict):
            timeouts = DynamodbTableTimeouts(**timeouts)
        if isinstance(ttl, dict):
            ttl = DynamodbTableTtl(**ttl)
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
        if attribute is not None:
            self._values["attribute"] = attribute
        if billing_mode is not None:
            self._values["billing_mode"] = billing_mode
        if global_secondary_index is not None:
            self._values["global_secondary_index"] = global_secondary_index
        if hash_key is not None:
            self._values["hash_key"] = hash_key
        if local_secondary_index is not None:
            self._values["local_secondary_index"] = local_secondary_index
        if point_in_time_recovery is not None:
            self._values["point_in_time_recovery"] = point_in_time_recovery
        if range_key is not None:
            self._values["range_key"] = range_key
        if read_capacity is not None:
            self._values["read_capacity"] = read_capacity
        if replica is not None:
            self._values["replica"] = replica
        if restore_date_time is not None:
            self._values["restore_date_time"] = restore_date_time
        if restore_source_name is not None:
            self._values["restore_source_name"] = restore_source_name
        if restore_to_latest_time is not None:
            self._values["restore_to_latest_time"] = restore_to_latest_time
        if server_side_encryption is not None:
            self._values["server_side_encryption"] = server_side_encryption
        if stream_enabled is not None:
            self._values["stream_enabled"] = stream_enabled
        if stream_view_type is not None:
            self._values["stream_view_type"] = stream_view_type
        if table_class is not None:
            self._values["table_class"] = table_class
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if timeouts is not None:
            self._values["timeouts"] = timeouts
        if ttl is not None:
            self._values["ttl"] = ttl
        if write_capacity is not None:
            self._values["write_capacity"] = write_capacity

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#name DynamodbTable#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def attribute(self) -> typing.Optional[typing.List[DynamodbTableAttribute]]:
        '''attribute block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#attribute DynamodbTable#attribute}
        '''
        result = self._values.get("attribute")
        return typing.cast(typing.Optional[typing.List[DynamodbTableAttribute]], result)

    @builtins.property
    def billing_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#billing_mode DynamodbTable#billing_mode}.'''
        result = self._values.get("billing_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def global_secondary_index(
        self,
    ) -> typing.Optional[typing.List["DynamodbTableGlobalSecondaryIndex"]]:
        '''global_secondary_index block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#global_secondary_index DynamodbTable#global_secondary_index}
        '''
        result = self._values.get("global_secondary_index")
        return typing.cast(typing.Optional[typing.List["DynamodbTableGlobalSecondaryIndex"]], result)

    @builtins.property
    def hash_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#hash_key DynamodbTable#hash_key}.'''
        result = self._values.get("hash_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def local_secondary_index(
        self,
    ) -> typing.Optional[typing.List["DynamodbTableLocalSecondaryIndex"]]:
        '''local_secondary_index block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#local_secondary_index DynamodbTable#local_secondary_index}
        '''
        result = self._values.get("local_secondary_index")
        return typing.cast(typing.Optional[typing.List["DynamodbTableLocalSecondaryIndex"]], result)

    @builtins.property
    def point_in_time_recovery(
        self,
    ) -> typing.Optional["DynamodbTablePointInTimeRecovery"]:
        '''point_in_time_recovery block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#point_in_time_recovery DynamodbTable#point_in_time_recovery}
        '''
        result = self._values.get("point_in_time_recovery")
        return typing.cast(typing.Optional["DynamodbTablePointInTimeRecovery"], result)

    @builtins.property
    def range_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#range_key DynamodbTable#range_key}.'''
        result = self._values.get("range_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def read_capacity(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#read_capacity DynamodbTable#read_capacity}.'''
        result = self._values.get("read_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def replica(self) -> typing.Optional[typing.List["DynamodbTableReplica"]]:
        '''replica block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#replica DynamodbTable#replica}
        '''
        result = self._values.get("replica")
        return typing.cast(typing.Optional[typing.List["DynamodbTableReplica"]], result)

    @builtins.property
    def restore_date_time(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#restore_date_time DynamodbTable#restore_date_time}.'''
        result = self._values.get("restore_date_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def restore_source_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#restore_source_name DynamodbTable#restore_source_name}.'''
        result = self._values.get("restore_source_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def restore_to_latest_time(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#restore_to_latest_time DynamodbTable#restore_to_latest_time}.'''
        result = self._values.get("restore_to_latest_time")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def server_side_encryption(
        self,
    ) -> typing.Optional["DynamodbTableServerSideEncryption"]:
        '''server_side_encryption block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#server_side_encryption DynamodbTable#server_side_encryption}
        '''
        result = self._values.get("server_side_encryption")
        return typing.cast(typing.Optional["DynamodbTableServerSideEncryption"], result)

    @builtins.property
    def stream_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#stream_enabled DynamodbTable#stream_enabled}.'''
        result = self._values.get("stream_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def stream_view_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#stream_view_type DynamodbTable#stream_view_type}.'''
        result = self._values.get("stream_view_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def table_class(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#table_class DynamodbTable#table_class}.'''
        result = self._values.get("table_class")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#tags DynamodbTable#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#tags_all DynamodbTable#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["DynamodbTableTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#timeouts DynamodbTable#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["DynamodbTableTimeouts"], result)

    @builtins.property
    def ttl(self) -> typing.Optional["DynamodbTableTtl"]:
        '''ttl block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#ttl DynamodbTable#ttl}
        '''
        result = self._values.get("ttl")
        return typing.cast(typing.Optional["DynamodbTableTtl"], result)

    @builtins.property
    def write_capacity(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#write_capacity DynamodbTable#write_capacity}.'''
        result = self._values.get("write_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamodbTableConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dynamodb.DynamodbTableGlobalSecondaryIndex",
    jsii_struct_bases=[],
    name_mapping={
        "hash_key": "hashKey",
        "name": "name",
        "projection_type": "projectionType",
        "non_key_attributes": "nonKeyAttributes",
        "range_key": "rangeKey",
        "read_capacity": "readCapacity",
        "write_capacity": "writeCapacity",
    },
)
class DynamodbTableGlobalSecondaryIndex:
    def __init__(
        self,
        *,
        hash_key: builtins.str,
        name: builtins.str,
        projection_type: builtins.str,
        non_key_attributes: typing.Optional[typing.Sequence[builtins.str]] = None,
        range_key: typing.Optional[builtins.str] = None,
        read_capacity: typing.Optional[jsii.Number] = None,
        write_capacity: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param hash_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#hash_key DynamodbTable#hash_key}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#name DynamodbTable#name}.
        :param projection_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#projection_type DynamodbTable#projection_type}.
        :param non_key_attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#non_key_attributes DynamodbTable#non_key_attributes}.
        :param range_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#range_key DynamodbTable#range_key}.
        :param read_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#read_capacity DynamodbTable#read_capacity}.
        :param write_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#write_capacity DynamodbTable#write_capacity}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "hash_key": hash_key,
            "name": name,
            "projection_type": projection_type,
        }
        if non_key_attributes is not None:
            self._values["non_key_attributes"] = non_key_attributes
        if range_key is not None:
            self._values["range_key"] = range_key
        if read_capacity is not None:
            self._values["read_capacity"] = read_capacity
        if write_capacity is not None:
            self._values["write_capacity"] = write_capacity

    @builtins.property
    def hash_key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#hash_key DynamodbTable#hash_key}.'''
        result = self._values.get("hash_key")
        assert result is not None, "Required property 'hash_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#name DynamodbTable#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def projection_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#projection_type DynamodbTable#projection_type}.'''
        result = self._values.get("projection_type")
        assert result is not None, "Required property 'projection_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def non_key_attributes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#non_key_attributes DynamodbTable#non_key_attributes}.'''
        result = self._values.get("non_key_attributes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def range_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#range_key DynamodbTable#range_key}.'''
        result = self._values.get("range_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def read_capacity(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#read_capacity DynamodbTable#read_capacity}.'''
        result = self._values.get("read_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def write_capacity(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#write_capacity DynamodbTable#write_capacity}.'''
        result = self._values.get("write_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamodbTableGlobalSecondaryIndex(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DynamodbTableItem(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dynamodb.DynamodbTableItem",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table_item aws_dynamodb_table_item}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        hash_key: builtins.str,
        item: builtins.str,
        table_name: builtins.str,
        range_key: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table_item aws_dynamodb_table_item} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param hash_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table_item#hash_key DynamodbTableItem#hash_key}.
        :param item: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table_item#item DynamodbTableItem#item}.
        :param table_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table_item#table_name DynamodbTableItem#table_name}.
        :param range_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table_item#range_key DynamodbTableItem#range_key}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DynamodbTableItemConfig(
            hash_key=hash_key,
            item=item,
            table_name=table_name,
            range_key=range_key,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetRangeKey")
    def reset_range_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRangeKey", []))

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
    @jsii.member(jsii_name="hashKeyInput")
    def hash_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hashKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="itemInput")
    def item_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "itemInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rangeKeyInput")
    def range_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rangeKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tableNameInput")
    def table_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tableNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hashKey")
    def hash_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hashKey"))

    @hash_key.setter
    def hash_key(self, value: builtins.str) -> None:
        jsii.set(self, "hashKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="item")
    def item(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "item"))

    @item.setter
    def item(self, value: builtins.str) -> None:
        jsii.set(self, "item", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rangeKey")
    def range_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rangeKey"))

    @range_key.setter
    def range_key(self, value: builtins.str) -> None:
        jsii.set(self, "rangeKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tableName")
    def table_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tableName"))

    @table_name.setter
    def table_name(self, value: builtins.str) -> None:
        jsii.set(self, "tableName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dynamodb.DynamodbTableItemConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "hash_key": "hashKey",
        "item": "item",
        "table_name": "tableName",
        "range_key": "rangeKey",
    },
)
class DynamodbTableItemConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        hash_key: builtins.str,
        item: builtins.str,
        table_name: builtins.str,
        range_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS DynamoDB.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param hash_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table_item#hash_key DynamodbTableItem#hash_key}.
        :param item: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table_item#item DynamodbTableItem#item}.
        :param table_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table_item#table_name DynamodbTableItem#table_name}.
        :param range_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table_item#range_key DynamodbTableItem#range_key}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "hash_key": hash_key,
            "item": item,
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
        if range_key is not None:
            self._values["range_key"] = range_key

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
    def hash_key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table_item#hash_key DynamodbTableItem#hash_key}.'''
        result = self._values.get("hash_key")
        assert result is not None, "Required property 'hash_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def item(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table_item#item DynamodbTableItem#item}.'''
        result = self._values.get("item")
        assert result is not None, "Required property 'item' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def table_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table_item#table_name DynamodbTableItem#table_name}.'''
        result = self._values.get("table_name")
        assert result is not None, "Required property 'table_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def range_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table_item#range_key DynamodbTableItem#range_key}.'''
        result = self._values.get("range_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamodbTableItemConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dynamodb.DynamodbTableLocalSecondaryIndex",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "projection_type": "projectionType",
        "range_key": "rangeKey",
        "non_key_attributes": "nonKeyAttributes",
    },
)
class DynamodbTableLocalSecondaryIndex:
    def __init__(
        self,
        *,
        name: builtins.str,
        projection_type: builtins.str,
        range_key: builtins.str,
        non_key_attributes: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#name DynamodbTable#name}.
        :param projection_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#projection_type DynamodbTable#projection_type}.
        :param range_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#range_key DynamodbTable#range_key}.
        :param non_key_attributes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#non_key_attributes DynamodbTable#non_key_attributes}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "projection_type": projection_type,
            "range_key": range_key,
        }
        if non_key_attributes is not None:
            self._values["non_key_attributes"] = non_key_attributes

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#name DynamodbTable#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def projection_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#projection_type DynamodbTable#projection_type}.'''
        result = self._values.get("projection_type")
        assert result is not None, "Required property 'projection_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def range_key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#range_key DynamodbTable#range_key}.'''
        result = self._values.get("range_key")
        assert result is not None, "Required property 'range_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def non_key_attributes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#non_key_attributes DynamodbTable#non_key_attributes}.'''
        result = self._values.get("non_key_attributes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamodbTableLocalSecondaryIndex(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dynamodb.DynamodbTablePointInTimeRecovery",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled"},
)
class DynamodbTablePointInTimeRecovery:
    def __init__(
        self,
        *,
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#enabled DynamodbTable#enabled}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "enabled": enabled,
        }

    @builtins.property
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#enabled DynamodbTable#enabled}.'''
        result = self._values.get("enabled")
        assert result is not None, "Required property 'enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamodbTablePointInTimeRecovery(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DynamodbTablePointInTimeRecoveryOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dynamodb.DynamodbTablePointInTimeRecoveryOutputReference",
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
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DynamodbTablePointInTimeRecovery]:
        return typing.cast(typing.Optional[DynamodbTablePointInTimeRecovery], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DynamodbTablePointInTimeRecovery],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dynamodb.DynamodbTableReplica",
    jsii_struct_bases=[],
    name_mapping={"region_name": "regionName", "kms_key_arn": "kmsKeyArn"},
)
class DynamodbTableReplica:
    def __init__(
        self,
        *,
        region_name: builtins.str,
        kms_key_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param region_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#region_name DynamodbTable#region_name}.
        :param kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#kms_key_arn DynamodbTable#kms_key_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "region_name": region_name,
        }
        if kms_key_arn is not None:
            self._values["kms_key_arn"] = kms_key_arn

    @builtins.property
    def region_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#region_name DynamodbTable#region_name}.'''
        result = self._values.get("region_name")
        assert result is not None, "Required property 'region_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def kms_key_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#kms_key_arn DynamodbTable#kms_key_arn}.'''
        result = self._values.get("kms_key_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamodbTableReplica(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dynamodb.DynamodbTableServerSideEncryption",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled", "kms_key_arn": "kmsKeyArn"},
)
class DynamodbTableServerSideEncryption:
    def __init__(
        self,
        *,
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        kms_key_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#enabled DynamodbTable#enabled}.
        :param kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#kms_key_arn DynamodbTable#kms_key_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "enabled": enabled,
        }
        if kms_key_arn is not None:
            self._values["kms_key_arn"] = kms_key_arn

    @builtins.property
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#enabled DynamodbTable#enabled}.'''
        result = self._values.get("enabled")
        assert result is not None, "Required property 'enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def kms_key_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#kms_key_arn DynamodbTable#kms_key_arn}.'''
        result = self._values.get("kms_key_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamodbTableServerSideEncryption(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DynamodbTableServerSideEncryptionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dynamodb.DynamodbTableServerSideEncryptionOutputReference",
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

    @jsii.member(jsii_name="resetKmsKeyArn")
    def reset_kms_key_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyArn", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyArnInput")
    def kms_key_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyArn")
    def kms_key_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyArn"))

    @kms_key_arn.setter
    def kms_key_arn(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DynamodbTableServerSideEncryption]:
        return typing.cast(typing.Optional[DynamodbTableServerSideEncryption], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DynamodbTableServerSideEncryption],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dynamodb.DynamodbTableTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class DynamodbTableTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#create DynamodbTable#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#delete DynamodbTable#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#update DynamodbTable#update}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#create DynamodbTable#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#delete DynamodbTable#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#update DynamodbTable#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamodbTableTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DynamodbTableTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dynamodb.DynamodbTableTimeoutsOutputReference",
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
    def internal_value(self) -> typing.Optional[DynamodbTableTimeouts]:
        return typing.cast(typing.Optional[DynamodbTableTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[DynamodbTableTimeouts]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dynamodb.DynamodbTableTtl",
    jsii_struct_bases=[],
    name_mapping={"attribute_name": "attributeName", "enabled": "enabled"},
)
class DynamodbTableTtl:
    def __init__(
        self,
        *,
        attribute_name: builtins.str,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param attribute_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#attribute_name DynamodbTable#attribute_name}.
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#enabled DynamodbTable#enabled}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "attribute_name": attribute_name,
        }
        if enabled is not None:
            self._values["enabled"] = enabled

    @builtins.property
    def attribute_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#attribute_name DynamodbTable#attribute_name}.'''
        result = self._values.get("attribute_name")
        assert result is not None, "Required property 'attribute_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_table#enabled DynamodbTable#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamodbTableTtl(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DynamodbTableTtlOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dynamodb.DynamodbTableTtlOutputReference",
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

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attributeNameInput")
    def attribute_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "attributeNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attributeName")
    def attribute_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "attributeName"))

    @attribute_name.setter
    def attribute_name(self, value: builtins.str) -> None:
        jsii.set(self, "attributeName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DynamodbTableTtl]:
        return typing.cast(typing.Optional[DynamodbTableTtl], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[DynamodbTableTtl]) -> None:
        jsii.set(self, "internalValue", value)


class DynamodbTag(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dynamodb.DynamodbTag",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_tag aws_dynamodb_tag}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        key: builtins.str,
        resource_arn: builtins.str,
        value: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_tag aws_dynamodb_tag} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_tag#key DynamodbTag#key}.
        :param resource_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_tag#resource_arn DynamodbTag#resource_arn}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_tag#value DynamodbTag#value}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DynamodbTagConfig(
            key=key,
            resource_arn=resource_arn,
            value=value,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

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
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceArnInput")
    def resource_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        jsii.set(self, "key", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceArn")
    def resource_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceArn"))

    @resource_arn.setter
    def resource_arn(self, value: builtins.str) -> None:
        jsii.set(self, "resourceArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        jsii.set(self, "value", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dynamodb.DynamodbTagConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "key": "key",
        "resource_arn": "resourceArn",
        "value": "value",
    },
)
class DynamodbTagConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        key: builtins.str,
        resource_arn: builtins.str,
        value: builtins.str,
    ) -> None:
        '''AWS DynamoDB.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_tag#key DynamodbTag#key}.
        :param resource_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_tag#resource_arn DynamodbTag#resource_arn}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_tag#value DynamodbTag#value}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "key": key,
            "resource_arn": resource_arn,
            "value": value,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

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
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_tag#key DynamodbTag#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_tag#resource_arn DynamodbTag#resource_arn}.'''
        result = self._values.get("resource_arn")
        assert result is not None, "Required property 'resource_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/dynamodb_tag#value DynamodbTag#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamodbTagConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataAwsDynamodbTable",
    "DataAwsDynamodbTableAttribute",
    "DataAwsDynamodbTableConfig",
    "DataAwsDynamodbTableGlobalSecondaryIndex",
    "DataAwsDynamodbTableLocalSecondaryIndex",
    "DataAwsDynamodbTablePointInTimeRecovery",
    "DataAwsDynamodbTableReplica",
    "DataAwsDynamodbTableServerSideEncryption",
    "DataAwsDynamodbTableServerSideEncryptionOutputReference",
    "DataAwsDynamodbTableTtl",
    "DynamodbGlobalTable",
    "DynamodbGlobalTableConfig",
    "DynamodbGlobalTableReplica",
    "DynamodbGlobalTableTimeouts",
    "DynamodbGlobalTableTimeoutsOutputReference",
    "DynamodbKinesisStreamingDestination",
    "DynamodbKinesisStreamingDestinationConfig",
    "DynamodbTable",
    "DynamodbTableAttribute",
    "DynamodbTableConfig",
    "DynamodbTableGlobalSecondaryIndex",
    "DynamodbTableItem",
    "DynamodbTableItemConfig",
    "DynamodbTableLocalSecondaryIndex",
    "DynamodbTablePointInTimeRecovery",
    "DynamodbTablePointInTimeRecoveryOutputReference",
    "DynamodbTableReplica",
    "DynamodbTableServerSideEncryption",
    "DynamodbTableServerSideEncryptionOutputReference",
    "DynamodbTableTimeouts",
    "DynamodbTableTimeoutsOutputReference",
    "DynamodbTableTtl",
    "DynamodbTableTtlOutputReference",
    "DynamodbTag",
    "DynamodbTagConfig",
]

publication.publish()
