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


class MacieMemberAccountAssociation(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.macie.MacieMemberAccountAssociation",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/macie_member_account_association aws_macie_member_account_association}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        member_account_id: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/macie_member_account_association aws_macie_member_account_association} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param member_account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/macie_member_account_association#member_account_id MacieMemberAccountAssociation#member_account_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = MacieMemberAccountAssociationConfig(
            member_account_id=member_account_id,
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
    @jsii.member(jsii_name="memberAccountIdInput")
    def member_account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "memberAccountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="memberAccountId")
    def member_account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "memberAccountId"))

    @member_account_id.setter
    def member_account_id(self, value: builtins.str) -> None:
        jsii.set(self, "memberAccountId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.macie.MacieMemberAccountAssociationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "member_account_id": "memberAccountId",
    },
)
class MacieMemberAccountAssociationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        member_account_id: builtins.str,
    ) -> None:
        '''AWS Macie.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param member_account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/macie_member_account_association#member_account_id MacieMemberAccountAssociation#member_account_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "member_account_id": member_account_id,
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
    def member_account_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/macie_member_account_association#member_account_id MacieMemberAccountAssociation#member_account_id}.'''
        result = self._values.get("member_account_id")
        assert result is not None, "Required property 'member_account_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MacieMemberAccountAssociationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MacieS3BucketAssociation(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.macie.MacieS3BucketAssociation",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/macie_s3_bucket_association aws_macie_s3_bucket_association}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        bucket_name: builtins.str,
        classification_type: typing.Optional["MacieS3BucketAssociationClassificationType"] = None,
        member_account_id: typing.Optional[builtins.str] = None,
        prefix: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/macie_s3_bucket_association aws_macie_s3_bucket_association} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param bucket_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/macie_s3_bucket_association#bucket_name MacieS3BucketAssociation#bucket_name}.
        :param classification_type: classification_type block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/macie_s3_bucket_association#classification_type MacieS3BucketAssociation#classification_type}
        :param member_account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/macie_s3_bucket_association#member_account_id MacieS3BucketAssociation#member_account_id}.
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/macie_s3_bucket_association#prefix MacieS3BucketAssociation#prefix}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = MacieS3BucketAssociationConfig(
            bucket_name=bucket_name,
            classification_type=classification_type,
            member_account_id=member_account_id,
            prefix=prefix,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putClassificationType")
    def put_classification_type(
        self,
        *,
        continuous: typing.Optional[builtins.str] = None,
        one_time: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param continuous: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/macie_s3_bucket_association#continuous MacieS3BucketAssociation#continuous}.
        :param one_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/macie_s3_bucket_association#one_time MacieS3BucketAssociation#one_time}.
        '''
        value = MacieS3BucketAssociationClassificationType(
            continuous=continuous, one_time=one_time
        )

        return typing.cast(None, jsii.invoke(self, "putClassificationType", [value]))

    @jsii.member(jsii_name="resetClassificationType")
    def reset_classification_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClassificationType", []))

    @jsii.member(jsii_name="resetMemberAccountId")
    def reset_member_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMemberAccountId", []))

    @jsii.member(jsii_name="resetPrefix")
    def reset_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrefix", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="classificationType")
    def classification_type(
        self,
    ) -> "MacieS3BucketAssociationClassificationTypeOutputReference":
        return typing.cast("MacieS3BucketAssociationClassificationTypeOutputReference", jsii.get(self, "classificationType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketNameInput")
    def bucket_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="classificationTypeInput")
    def classification_type_input(
        self,
    ) -> typing.Optional["MacieS3BucketAssociationClassificationType"]:
        return typing.cast(typing.Optional["MacieS3BucketAssociationClassificationType"], jsii.get(self, "classificationTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="memberAccountIdInput")
    def member_account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "memberAccountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefixInput")
    def prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "prefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketName"))

    @bucket_name.setter
    def bucket_name(self, value: builtins.str) -> None:
        jsii.set(self, "bucketName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="memberAccountId")
    def member_account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "memberAccountId"))

    @member_account_id.setter
    def member_account_id(self, value: builtins.str) -> None:
        jsii.set(self, "memberAccountId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prefix"))

    @prefix.setter
    def prefix(self, value: builtins.str) -> None:
        jsii.set(self, "prefix", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.macie.MacieS3BucketAssociationClassificationType",
    jsii_struct_bases=[],
    name_mapping={"continuous": "continuous", "one_time": "oneTime"},
)
class MacieS3BucketAssociationClassificationType:
    def __init__(
        self,
        *,
        continuous: typing.Optional[builtins.str] = None,
        one_time: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param continuous: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/macie_s3_bucket_association#continuous MacieS3BucketAssociation#continuous}.
        :param one_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/macie_s3_bucket_association#one_time MacieS3BucketAssociation#one_time}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if continuous is not None:
            self._values["continuous"] = continuous
        if one_time is not None:
            self._values["one_time"] = one_time

    @builtins.property
    def continuous(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/macie_s3_bucket_association#continuous MacieS3BucketAssociation#continuous}.'''
        result = self._values.get("continuous")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def one_time(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/macie_s3_bucket_association#one_time MacieS3BucketAssociation#one_time}.'''
        result = self._values.get("one_time")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MacieS3BucketAssociationClassificationType(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MacieS3BucketAssociationClassificationTypeOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.macie.MacieS3BucketAssociationClassificationTypeOutputReference",
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

    @jsii.member(jsii_name="resetContinuous")
    def reset_continuous(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContinuous", []))

    @jsii.member(jsii_name="resetOneTime")
    def reset_one_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOneTime", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="continuousInput")
    def continuous_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "continuousInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="oneTimeInput")
    def one_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oneTimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="continuous")
    def continuous(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "continuous"))

    @continuous.setter
    def continuous(self, value: builtins.str) -> None:
        jsii.set(self, "continuous", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="oneTime")
    def one_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oneTime"))

    @one_time.setter
    def one_time(self, value: builtins.str) -> None:
        jsii.set(self, "oneTime", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[MacieS3BucketAssociationClassificationType]:
        return typing.cast(typing.Optional[MacieS3BucketAssociationClassificationType], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MacieS3BucketAssociationClassificationType],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.macie.MacieS3BucketAssociationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "bucket_name": "bucketName",
        "classification_type": "classificationType",
        "member_account_id": "memberAccountId",
        "prefix": "prefix",
    },
)
class MacieS3BucketAssociationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        bucket_name: builtins.str,
        classification_type: typing.Optional[MacieS3BucketAssociationClassificationType] = None,
        member_account_id: typing.Optional[builtins.str] = None,
        prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Macie.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param bucket_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/macie_s3_bucket_association#bucket_name MacieS3BucketAssociation#bucket_name}.
        :param classification_type: classification_type block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/macie_s3_bucket_association#classification_type MacieS3BucketAssociation#classification_type}
        :param member_account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/macie_s3_bucket_association#member_account_id MacieS3BucketAssociation#member_account_id}.
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/macie_s3_bucket_association#prefix MacieS3BucketAssociation#prefix}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(classification_type, dict):
            classification_type = MacieS3BucketAssociationClassificationType(**classification_type)
        self._values: typing.Dict[str, typing.Any] = {
            "bucket_name": bucket_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if classification_type is not None:
            self._values["classification_type"] = classification_type
        if member_account_id is not None:
            self._values["member_account_id"] = member_account_id
        if prefix is not None:
            self._values["prefix"] = prefix

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
    def bucket_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/macie_s3_bucket_association#bucket_name MacieS3BucketAssociation#bucket_name}.'''
        result = self._values.get("bucket_name")
        assert result is not None, "Required property 'bucket_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def classification_type(
        self,
    ) -> typing.Optional[MacieS3BucketAssociationClassificationType]:
        '''classification_type block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/macie_s3_bucket_association#classification_type MacieS3BucketAssociation#classification_type}
        '''
        result = self._values.get("classification_type")
        return typing.cast(typing.Optional[MacieS3BucketAssociationClassificationType], result)

    @builtins.property
    def member_account_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/macie_s3_bucket_association#member_account_id MacieS3BucketAssociation#member_account_id}.'''
        result = self._values.get("member_account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/macie_s3_bucket_association#prefix MacieS3BucketAssociation#prefix}.'''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MacieS3BucketAssociationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "MacieMemberAccountAssociation",
    "MacieMemberAccountAssociationConfig",
    "MacieS3BucketAssociation",
    "MacieS3BucketAssociationClassificationType",
    "MacieS3BucketAssociationClassificationTypeOutputReference",
    "MacieS3BucketAssociationConfig",
]

publication.publish()
