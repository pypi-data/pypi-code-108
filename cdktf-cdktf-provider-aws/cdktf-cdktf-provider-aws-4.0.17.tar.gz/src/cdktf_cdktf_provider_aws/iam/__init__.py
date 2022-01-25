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


class DataAwsIamAccountAlias(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.DataAwsIamAccountAlias",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/iam_account_alias aws_iam_account_alias}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/iam_account_alias aws_iam_account_alias} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsIamAccountAliasConfig(
            count=count, depends_on=depends_on, lifecycle=lifecycle, provider=provider
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
    @jsii.member(jsii_name="accountAlias")
    def account_alias(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountAlias"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.DataAwsIamAccountAliasConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
    },
)
class DataAwsIamAccountAliasConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
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

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsIamAccountAliasConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsIamGroup(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.DataAwsIamGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/iam_group aws_iam_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        group_name: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/iam_group aws_iam_group} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_group#group_name DataAwsIamGroup#group_name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsIamGroupConfig(
            group_name=group_name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="users")
    def users(self, index: builtins.str) -> "DataAwsIamGroupUsers":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsIamGroupUsers", jsii.invoke(self, "users", [index]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="groupId")
    def group_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "groupId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="groupNameInput")
    def group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "groupNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="groupName")
    def group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "groupName"))

    @group_name.setter
    def group_name(self, value: builtins.str) -> None:
        jsii.set(self, "groupName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.DataAwsIamGroupConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "group_name": "groupName",
    },
)
class DataAwsIamGroupConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        group_name: builtins.str,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_group#group_name DataAwsIamGroup#group_name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "group_name": group_name,
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
    def group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_group#group_name DataAwsIamGroup#group_name}.'''
        result = self._values.get("group_name")
        assert result is not None, "Required property 'group_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsIamGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsIamGroupUsers(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.DataAwsIamGroupUsers",
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
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userId")
    def user_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userName")
    def user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userName"))


class DataAwsIamInstanceProfile(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.DataAwsIamInstanceProfile",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/iam_instance_profile aws_iam_instance_profile}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/iam_instance_profile aws_iam_instance_profile} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_instance_profile#name DataAwsIamInstanceProfile#name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsIamInstanceProfileConfig(
            name=name,
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
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createDate")
    def create_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleId")
    def role_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleName")
    def role_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.DataAwsIamInstanceProfileConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
    },
)
class DataAwsIamInstanceProfileConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_instance_profile#name DataAwsIamInstanceProfile#name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_instance_profile#name DataAwsIamInstanceProfile#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsIamInstanceProfileConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsIamPolicy(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.DataAwsIamPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/iam_policy aws_iam_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: typing.Optional[builtins.str] = None,
        path_prefix: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/iam_policy aws_iam_policy} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy#name DataAwsIamPolicy#name}.
        :param path_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy#path_prefix DataAwsIamPolicy#path_prefix}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy#tags DataAwsIamPolicy#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsIamPolicyConfig(
            name=name,
            path_prefix=path_prefix,
            tags=tags,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetPathPrefix")
    def reset_path_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPathPrefix", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

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
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyId")
    def policy_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pathPrefixInput")
    def path_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathPrefixInput"))

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
    @jsii.member(jsii_name="pathPrefix")
    def path_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pathPrefix"))

    @path_prefix.setter
    def path_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "pathPrefix", value)

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


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.DataAwsIamPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "path_prefix": "pathPrefix",
        "tags": "tags",
    },
)
class DataAwsIamPolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: typing.Optional[builtins.str] = None,
        path_prefix: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy#name DataAwsIamPolicy#name}.
        :param path_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy#path_prefix DataAwsIamPolicy#path_prefix}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy#tags DataAwsIamPolicy#tags}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if name is not None:
            self._values["name"] = name
        if path_prefix is not None:
            self._values["path_prefix"] = path_prefix
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
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy#name DataAwsIamPolicy#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def path_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy#path_prefix DataAwsIamPolicy#path_prefix}.'''
        result = self._values.get("path_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy#tags DataAwsIamPolicy#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsIamPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsIamPolicyDocument(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.DataAwsIamPolicyDocument",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document aws_iam_policy_document}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        override_json: typing.Optional[builtins.str] = None,
        override_policy_documents: typing.Optional[typing.Sequence[builtins.str]] = None,
        policy_id: typing.Optional[builtins.str] = None,
        source_json: typing.Optional[builtins.str] = None,
        source_policy_documents: typing.Optional[typing.Sequence[builtins.str]] = None,
        statement: typing.Optional[typing.Sequence["DataAwsIamPolicyDocumentStatement"]] = None,
        version: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document aws_iam_policy_document} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param override_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#override_json DataAwsIamPolicyDocument#override_json}.
        :param override_policy_documents: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#override_policy_documents DataAwsIamPolicyDocument#override_policy_documents}.
        :param policy_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#policy_id DataAwsIamPolicyDocument#policy_id}.
        :param source_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#source_json DataAwsIamPolicyDocument#source_json}.
        :param source_policy_documents: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#source_policy_documents DataAwsIamPolicyDocument#source_policy_documents}.
        :param statement: statement block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#statement DataAwsIamPolicyDocument#statement}
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#version DataAwsIamPolicyDocument#version}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsIamPolicyDocumentConfig(
            override_json=override_json,
            override_policy_documents=override_policy_documents,
            policy_id=policy_id,
            source_json=source_json,
            source_policy_documents=source_policy_documents,
            statement=statement,
            version=version,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetOverrideJson")
    def reset_override_json(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOverrideJson", []))

    @jsii.member(jsii_name="resetOverridePolicyDocuments")
    def reset_override_policy_documents(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOverridePolicyDocuments", []))

    @jsii.member(jsii_name="resetPolicyId")
    def reset_policy_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicyId", []))

    @jsii.member(jsii_name="resetSourceJson")
    def reset_source_json(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceJson", []))

    @jsii.member(jsii_name="resetSourcePolicyDocuments")
    def reset_source_policy_documents(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourcePolicyDocuments", []))

    @jsii.member(jsii_name="resetStatement")
    def reset_statement(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatement", []))

    @jsii.member(jsii_name="resetVersion")
    def reset_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersion", []))

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
    @jsii.member(jsii_name="json")
    def json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "json"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="overrideJsonInput")
    def override_json_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "overrideJsonInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="overridePolicyDocumentsInput")
    def override_policy_documents_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "overridePolicyDocumentsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyIdInput")
    def policy_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceJsonInput")
    def source_json_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceJsonInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourcePolicyDocumentsInput")
    def source_policy_documents_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "sourcePolicyDocumentsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statementInput")
    def statement_input(
        self,
    ) -> typing.Optional[typing.List["DataAwsIamPolicyDocumentStatement"]]:
        return typing.cast(typing.Optional[typing.List["DataAwsIamPolicyDocumentStatement"]], jsii.get(self, "statementInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="overrideJson")
    def override_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "overrideJson"))

    @override_json.setter
    def override_json(self, value: builtins.str) -> None:
        jsii.set(self, "overrideJson", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="overridePolicyDocuments")
    def override_policy_documents(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "overridePolicyDocuments"))

    @override_policy_documents.setter
    def override_policy_documents(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "overridePolicyDocuments", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyId")
    def policy_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyId"))

    @policy_id.setter
    def policy_id(self, value: builtins.str) -> None:
        jsii.set(self, "policyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceJson")
    def source_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceJson"))

    @source_json.setter
    def source_json(self, value: builtins.str) -> None:
        jsii.set(self, "sourceJson", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourcePolicyDocuments")
    def source_policy_documents(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "sourcePolicyDocuments"))

    @source_policy_documents.setter
    def source_policy_documents(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "sourcePolicyDocuments", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statement")
    def statement(self) -> typing.List["DataAwsIamPolicyDocumentStatement"]:
        return typing.cast(typing.List["DataAwsIamPolicyDocumentStatement"], jsii.get(self, "statement"))

    @statement.setter
    def statement(
        self,
        value: typing.List["DataAwsIamPolicyDocumentStatement"],
    ) -> None:
        jsii.set(self, "statement", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        jsii.set(self, "version", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.DataAwsIamPolicyDocumentConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "override_json": "overrideJson",
        "override_policy_documents": "overridePolicyDocuments",
        "policy_id": "policyId",
        "source_json": "sourceJson",
        "source_policy_documents": "sourcePolicyDocuments",
        "statement": "statement",
        "version": "version",
    },
)
class DataAwsIamPolicyDocumentConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        override_json: typing.Optional[builtins.str] = None,
        override_policy_documents: typing.Optional[typing.Sequence[builtins.str]] = None,
        policy_id: typing.Optional[builtins.str] = None,
        source_json: typing.Optional[builtins.str] = None,
        source_policy_documents: typing.Optional[typing.Sequence[builtins.str]] = None,
        statement: typing.Optional[typing.Sequence["DataAwsIamPolicyDocumentStatement"]] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param override_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#override_json DataAwsIamPolicyDocument#override_json}.
        :param override_policy_documents: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#override_policy_documents DataAwsIamPolicyDocument#override_policy_documents}.
        :param policy_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#policy_id DataAwsIamPolicyDocument#policy_id}.
        :param source_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#source_json DataAwsIamPolicyDocument#source_json}.
        :param source_policy_documents: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#source_policy_documents DataAwsIamPolicyDocument#source_policy_documents}.
        :param statement: statement block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#statement DataAwsIamPolicyDocument#statement}
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#version DataAwsIamPolicyDocument#version}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if override_json is not None:
            self._values["override_json"] = override_json
        if override_policy_documents is not None:
            self._values["override_policy_documents"] = override_policy_documents
        if policy_id is not None:
            self._values["policy_id"] = policy_id
        if source_json is not None:
            self._values["source_json"] = source_json
        if source_policy_documents is not None:
            self._values["source_policy_documents"] = source_policy_documents
        if statement is not None:
            self._values["statement"] = statement
        if version is not None:
            self._values["version"] = version

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
    def override_json(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#override_json DataAwsIamPolicyDocument#override_json}.'''
        result = self._values.get("override_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def override_policy_documents(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#override_policy_documents DataAwsIamPolicyDocument#override_policy_documents}.'''
        result = self._values.get("override_policy_documents")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def policy_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#policy_id DataAwsIamPolicyDocument#policy_id}.'''
        result = self._values.get("policy_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_json(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#source_json DataAwsIamPolicyDocument#source_json}.'''
        result = self._values.get("source_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_policy_documents(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#source_policy_documents DataAwsIamPolicyDocument#source_policy_documents}.'''
        result = self._values.get("source_policy_documents")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def statement(
        self,
    ) -> typing.Optional[typing.List["DataAwsIamPolicyDocumentStatement"]]:
        '''statement block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#statement DataAwsIamPolicyDocument#statement}
        '''
        result = self._values.get("statement")
        return typing.cast(typing.Optional[typing.List["DataAwsIamPolicyDocumentStatement"]], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#version DataAwsIamPolicyDocument#version}.'''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsIamPolicyDocumentConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.DataAwsIamPolicyDocumentStatement",
    jsii_struct_bases=[],
    name_mapping={
        "actions": "actions",
        "condition": "condition",
        "effect": "effect",
        "not_actions": "notActions",
        "not_principals": "notPrincipals",
        "not_resources": "notResources",
        "principals": "principals",
        "resources": "resources",
        "sid": "sid",
    },
)
class DataAwsIamPolicyDocumentStatement:
    def __init__(
        self,
        *,
        actions: typing.Optional[typing.Sequence[builtins.str]] = None,
        condition: typing.Optional[typing.Sequence["DataAwsIamPolicyDocumentStatementCondition"]] = None,
        effect: typing.Optional[builtins.str] = None,
        not_actions: typing.Optional[typing.Sequence[builtins.str]] = None,
        not_principals: typing.Optional[typing.Sequence["DataAwsIamPolicyDocumentStatementNotPrincipals"]] = None,
        not_resources: typing.Optional[typing.Sequence[builtins.str]] = None,
        principals: typing.Optional[typing.Sequence["DataAwsIamPolicyDocumentStatementPrincipals"]] = None,
        resources: typing.Optional[typing.Sequence[builtins.str]] = None,
        sid: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param actions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#actions DataAwsIamPolicyDocument#actions}.
        :param condition: condition block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#condition DataAwsIamPolicyDocument#condition}
        :param effect: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#effect DataAwsIamPolicyDocument#effect}.
        :param not_actions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#not_actions DataAwsIamPolicyDocument#not_actions}.
        :param not_principals: not_principals block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#not_principals DataAwsIamPolicyDocument#not_principals}
        :param not_resources: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#not_resources DataAwsIamPolicyDocument#not_resources}.
        :param principals: principals block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#principals DataAwsIamPolicyDocument#principals}
        :param resources: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#resources DataAwsIamPolicyDocument#resources}.
        :param sid: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#sid DataAwsIamPolicyDocument#sid}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if actions is not None:
            self._values["actions"] = actions
        if condition is not None:
            self._values["condition"] = condition
        if effect is not None:
            self._values["effect"] = effect
        if not_actions is not None:
            self._values["not_actions"] = not_actions
        if not_principals is not None:
            self._values["not_principals"] = not_principals
        if not_resources is not None:
            self._values["not_resources"] = not_resources
        if principals is not None:
            self._values["principals"] = principals
        if resources is not None:
            self._values["resources"] = resources
        if sid is not None:
            self._values["sid"] = sid

    @builtins.property
    def actions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#actions DataAwsIamPolicyDocument#actions}.'''
        result = self._values.get("actions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def condition(
        self,
    ) -> typing.Optional[typing.List["DataAwsIamPolicyDocumentStatementCondition"]]:
        '''condition block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#condition DataAwsIamPolicyDocument#condition}
        '''
        result = self._values.get("condition")
        return typing.cast(typing.Optional[typing.List["DataAwsIamPolicyDocumentStatementCondition"]], result)

    @builtins.property
    def effect(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#effect DataAwsIamPolicyDocument#effect}.'''
        result = self._values.get("effect")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def not_actions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#not_actions DataAwsIamPolicyDocument#not_actions}.'''
        result = self._values.get("not_actions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def not_principals(
        self,
    ) -> typing.Optional[typing.List["DataAwsIamPolicyDocumentStatementNotPrincipals"]]:
        '''not_principals block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#not_principals DataAwsIamPolicyDocument#not_principals}
        '''
        result = self._values.get("not_principals")
        return typing.cast(typing.Optional[typing.List["DataAwsIamPolicyDocumentStatementNotPrincipals"]], result)

    @builtins.property
    def not_resources(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#not_resources DataAwsIamPolicyDocument#not_resources}.'''
        result = self._values.get("not_resources")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def principals(
        self,
    ) -> typing.Optional[typing.List["DataAwsIamPolicyDocumentStatementPrincipals"]]:
        '''principals block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#principals DataAwsIamPolicyDocument#principals}
        '''
        result = self._values.get("principals")
        return typing.cast(typing.Optional[typing.List["DataAwsIamPolicyDocumentStatementPrincipals"]], result)

    @builtins.property
    def resources(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#resources DataAwsIamPolicyDocument#resources}.'''
        result = self._values.get("resources")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def sid(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#sid DataAwsIamPolicyDocument#sid}.'''
        result = self._values.get("sid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsIamPolicyDocumentStatement(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.DataAwsIamPolicyDocumentStatementCondition",
    jsii_struct_bases=[],
    name_mapping={"test": "test", "values": "values", "variable": "variable"},
)
class DataAwsIamPolicyDocumentStatementCondition:
    def __init__(
        self,
        *,
        test: builtins.str,
        values: typing.Sequence[builtins.str],
        variable: builtins.str,
    ) -> None:
        '''
        :param test: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#test DataAwsIamPolicyDocument#test}.
        :param values: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#values DataAwsIamPolicyDocument#values}.
        :param variable: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#variable DataAwsIamPolicyDocument#variable}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "test": test,
            "values": values,
            "variable": variable,
        }

    @builtins.property
    def test(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#test DataAwsIamPolicyDocument#test}.'''
        result = self._values.get("test")
        assert result is not None, "Required property 'test' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def values(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#values DataAwsIamPolicyDocument#values}.'''
        result = self._values.get("values")
        assert result is not None, "Required property 'values' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def variable(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#variable DataAwsIamPolicyDocument#variable}.'''
        result = self._values.get("variable")
        assert result is not None, "Required property 'variable' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsIamPolicyDocumentStatementCondition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.DataAwsIamPolicyDocumentStatementNotPrincipals",
    jsii_struct_bases=[],
    name_mapping={"identifiers": "identifiers", "type": "type"},
)
class DataAwsIamPolicyDocumentStatementNotPrincipals:
    def __init__(
        self,
        *,
        identifiers: typing.Sequence[builtins.str],
        type: builtins.str,
    ) -> None:
        '''
        :param identifiers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#identifiers DataAwsIamPolicyDocument#identifiers}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#type DataAwsIamPolicyDocument#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "identifiers": identifiers,
            "type": type,
        }

    @builtins.property
    def identifiers(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#identifiers DataAwsIamPolicyDocument#identifiers}.'''
        result = self._values.get("identifiers")
        assert result is not None, "Required property 'identifiers' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#type DataAwsIamPolicyDocument#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsIamPolicyDocumentStatementNotPrincipals(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.DataAwsIamPolicyDocumentStatementPrincipals",
    jsii_struct_bases=[],
    name_mapping={"identifiers": "identifiers", "type": "type"},
)
class DataAwsIamPolicyDocumentStatementPrincipals:
    def __init__(
        self,
        *,
        identifiers: typing.Sequence[builtins.str],
        type: builtins.str,
    ) -> None:
        '''
        :param identifiers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#identifiers DataAwsIamPolicyDocument#identifiers}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#type DataAwsIamPolicyDocument#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "identifiers": identifiers,
            "type": type,
        }

    @builtins.property
    def identifiers(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#identifiers DataAwsIamPolicyDocument#identifiers}.'''
        result = self._values.get("identifiers")
        assert result is not None, "Required property 'identifiers' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_policy_document#type DataAwsIamPolicyDocument#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsIamPolicyDocumentStatementPrincipals(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsIamRole(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.DataAwsIamRole",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/iam_role aws_iam_role}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/iam_role aws_iam_role} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_role#name DataAwsIamRole#name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_role#tags DataAwsIamRole#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsIamRoleConfig(
            name=name,
            tags=tags,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

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
    @jsii.member(jsii_name="assumeRolePolicy")
    def assume_role_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "assumeRolePolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createDate")
    def create_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxSessionDuration")
    def max_session_duration(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxSessionDuration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="permissionsBoundary")
    def permissions_boundary(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "permissionsBoundary"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uniqueId")
    def unique_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uniqueId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

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


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.DataAwsIamRoleConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "tags": "tags",
    },
)
class DataAwsIamRoleConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_role#name DataAwsIamRole#name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_role#tags DataAwsIamRole#tags}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_role#name DataAwsIamRole#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_role#tags DataAwsIamRole#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsIamRoleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsIamRoles(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.DataAwsIamRoles",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/iam_roles aws_iam_roles}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name_regex: typing.Optional[builtins.str] = None,
        path_prefix: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/iam_roles aws_iam_roles} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name_regex: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_roles#name_regex DataAwsIamRoles#name_regex}.
        :param path_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_roles#path_prefix DataAwsIamRoles#path_prefix}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsIamRolesConfig(
            name_regex=name_regex,
            path_prefix=path_prefix,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetNameRegex")
    def reset_name_regex(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNameRegex", []))

    @jsii.member(jsii_name="resetPathPrefix")
    def reset_path_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPathPrefix", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arns")
    def arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "arns"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="names")
    def names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "names"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameRegexInput")
    def name_regex_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameRegexInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pathPrefixInput")
    def path_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathPrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameRegex")
    def name_regex(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameRegex"))

    @name_regex.setter
    def name_regex(self, value: builtins.str) -> None:
        jsii.set(self, "nameRegex", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pathPrefix")
    def path_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pathPrefix"))

    @path_prefix.setter
    def path_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "pathPrefix", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.DataAwsIamRolesConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name_regex": "nameRegex",
        "path_prefix": "pathPrefix",
    },
)
class DataAwsIamRolesConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name_regex: typing.Optional[builtins.str] = None,
        path_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name_regex: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_roles#name_regex DataAwsIamRoles#name_regex}.
        :param path_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_roles#path_prefix DataAwsIamRoles#path_prefix}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if name_regex is not None:
            self._values["name_regex"] = name_regex
        if path_prefix is not None:
            self._values["path_prefix"] = path_prefix

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
    def name_regex(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_roles#name_regex DataAwsIamRoles#name_regex}.'''
        result = self._values.get("name_regex")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def path_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_roles#path_prefix DataAwsIamRoles#path_prefix}.'''
        result = self._values.get("path_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsIamRolesConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsIamServerCertificate(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.DataAwsIamServerCertificate",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/iam_server_certificate aws_iam_server_certificate}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        latest: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        path_prefix: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/iam_server_certificate aws_iam_server_certificate} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param latest: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_server_certificate#latest DataAwsIamServerCertificate#latest}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_server_certificate#name DataAwsIamServerCertificate#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_server_certificate#name_prefix DataAwsIamServerCertificate#name_prefix}.
        :param path_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_server_certificate#path_prefix DataAwsIamServerCertificate#path_prefix}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsIamServerCertificateConfig(
            latest=latest,
            name=name,
            name_prefix=name_prefix,
            path_prefix=path_prefix,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetLatest")
    def reset_latest(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLatest", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNamePrefix")
    def reset_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamePrefix", []))

    @jsii.member(jsii_name="resetPathPrefix")
    def reset_path_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPathPrefix", []))

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
    @jsii.member(jsii_name="certificateBody")
    def certificate_body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateBody"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateChain")
    def certificate_chain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateChain"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="expirationDate")
    def expiration_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "expirationDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uploadDate")
    def upload_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uploadDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="latestInput")
    def latest_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "latestInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefixInput")
    def name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namePrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pathPrefixInput")
    def path_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathPrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="latest")
    def latest(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "latest"))

    @latest.setter
    def latest(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "latest", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefix")
    def name_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namePrefix"))

    @name_prefix.setter
    def name_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "namePrefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pathPrefix")
    def path_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pathPrefix"))

    @path_prefix.setter
    def path_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "pathPrefix", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.DataAwsIamServerCertificateConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "latest": "latest",
        "name": "name",
        "name_prefix": "namePrefix",
        "path_prefix": "pathPrefix",
    },
)
class DataAwsIamServerCertificateConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        latest: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        path_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param latest: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_server_certificate#latest DataAwsIamServerCertificate#latest}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_server_certificate#name DataAwsIamServerCertificate#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_server_certificate#name_prefix DataAwsIamServerCertificate#name_prefix}.
        :param path_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_server_certificate#path_prefix DataAwsIamServerCertificate#path_prefix}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if latest is not None:
            self._values["latest"] = latest
        if name is not None:
            self._values["name"] = name
        if name_prefix is not None:
            self._values["name_prefix"] = name_prefix
        if path_prefix is not None:
            self._values["path_prefix"] = path_prefix

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
    def latest(self) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_server_certificate#latest DataAwsIamServerCertificate#latest}.'''
        result = self._values.get("latest")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_server_certificate#name DataAwsIamServerCertificate#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_server_certificate#name_prefix DataAwsIamServerCertificate#name_prefix}.'''
        result = self._values.get("name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def path_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_server_certificate#path_prefix DataAwsIamServerCertificate#path_prefix}.'''
        result = self._values.get("path_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsIamServerCertificateConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsIamSessionContext(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.DataAwsIamSessionContext",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/iam_session_context aws_iam_session_context}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        arn: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/iam_session_context aws_iam_session_context} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_session_context#arn DataAwsIamSessionContext#arn}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsIamSessionContextConfig(
            arn=arn,
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
    @jsii.member(jsii_name="issuerArn")
    def issuer_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "issuerArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="issuerId")
    def issuer_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "issuerId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="issuerName")
    def issuer_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "issuerName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sessionName")
    def session_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sessionName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arnInput")
    def arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "arnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @arn.setter
    def arn(self, value: builtins.str) -> None:
        jsii.set(self, "arn", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.DataAwsIamSessionContextConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "arn": "arn",
    },
)
class DataAwsIamSessionContextConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        arn: builtins.str,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_session_context#arn DataAwsIamSessionContext#arn}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "arn": arn,
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
    def arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_session_context#arn DataAwsIamSessionContext#arn}.'''
        result = self._values.get("arn")
        assert result is not None, "Required property 'arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsIamSessionContextConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsIamUser(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.DataAwsIamUser",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/iam_user aws_iam_user}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        user_name: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/iam_user aws_iam_user} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param user_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_user#user_name DataAwsIamUser#user_name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_user#tags DataAwsIamUser#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsIamUserConfig(
            user_name=user_name,
            tags=tags,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

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
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="permissionsBoundary")
    def permissions_boundary(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "permissionsBoundary"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userId")
    def user_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userNameInput")
    def user_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userNameInput"))

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
    @jsii.member(jsii_name="userName")
    def user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userName"))

    @user_name.setter
    def user_name(self, value: builtins.str) -> None:
        jsii.set(self, "userName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.DataAwsIamUserConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "user_name": "userName",
        "tags": "tags",
    },
)
class DataAwsIamUserConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        user_name: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param user_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_user#user_name DataAwsIamUser#user_name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_user#tags DataAwsIamUser#tags}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "user_name": user_name,
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
    def user_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_user#user_name DataAwsIamUser#user_name}.'''
        result = self._values.get("user_name")
        assert result is not None, "Required property 'user_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_user#tags DataAwsIamUser#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsIamUserConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsIamUserSshKey(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.DataAwsIamUserSshKey",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/iam_user_ssh_key aws_iam_user_ssh_key}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        encoding: builtins.str,
        ssh_public_key_id: builtins.str,
        username: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/iam_user_ssh_key aws_iam_user_ssh_key} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param encoding: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_user_ssh_key#encoding DataAwsIamUserSshKey#encoding}.
        :param ssh_public_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_user_ssh_key#ssh_public_key_id DataAwsIamUserSshKey#ssh_public_key_id}.
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_user_ssh_key#username DataAwsIamUserSshKey#username}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsIamUserSshKeyConfig(
            encoding=encoding,
            ssh_public_key_id=ssh_public_key_id,
            username=username,
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
    @jsii.member(jsii_name="fingerprint")
    def fingerprint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fingerprint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicKey")
    def public_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicKey"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encodingInput")
    def encoding_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encodingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sshPublicKeyIdInput")
    def ssh_public_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sshPublicKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encoding")
    def encoding(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encoding"))

    @encoding.setter
    def encoding(self, value: builtins.str) -> None:
        jsii.set(self, "encoding", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sshPublicKeyId")
    def ssh_public_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sshPublicKeyId"))

    @ssh_public_key_id.setter
    def ssh_public_key_id(self, value: builtins.str) -> None:
        jsii.set(self, "sshPublicKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        jsii.set(self, "username", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.DataAwsIamUserSshKeyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "encoding": "encoding",
        "ssh_public_key_id": "sshPublicKeyId",
        "username": "username",
    },
)
class DataAwsIamUserSshKeyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        encoding: builtins.str,
        ssh_public_key_id: builtins.str,
        username: builtins.str,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param encoding: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_user_ssh_key#encoding DataAwsIamUserSshKey#encoding}.
        :param ssh_public_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_user_ssh_key#ssh_public_key_id DataAwsIamUserSshKey#ssh_public_key_id}.
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_user_ssh_key#username DataAwsIamUserSshKey#username}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "encoding": encoding,
            "ssh_public_key_id": ssh_public_key_id,
            "username": username,
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
    def encoding(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_user_ssh_key#encoding DataAwsIamUserSshKey#encoding}.'''
        result = self._values.get("encoding")
        assert result is not None, "Required property 'encoding' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ssh_public_key_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_user_ssh_key#ssh_public_key_id DataAwsIamUserSshKey#ssh_public_key_id}.'''
        result = self._values.get("ssh_public_key_id")
        assert result is not None, "Required property 'ssh_public_key_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_user_ssh_key#username DataAwsIamUserSshKey#username}.'''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsIamUserSshKeyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsIamUsers(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.DataAwsIamUsers",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/iam_users aws_iam_users}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name_regex: typing.Optional[builtins.str] = None,
        path_prefix: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/iam_users aws_iam_users} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name_regex: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_users#name_regex DataAwsIamUsers#name_regex}.
        :param path_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_users#path_prefix DataAwsIamUsers#path_prefix}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsIamUsersConfig(
            name_regex=name_regex,
            path_prefix=path_prefix,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetNameRegex")
    def reset_name_regex(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNameRegex", []))

    @jsii.member(jsii_name="resetPathPrefix")
    def reset_path_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPathPrefix", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arns")
    def arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "arns"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="names")
    def names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "names"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameRegexInput")
    def name_regex_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameRegexInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pathPrefixInput")
    def path_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathPrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameRegex")
    def name_regex(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameRegex"))

    @name_regex.setter
    def name_regex(self, value: builtins.str) -> None:
        jsii.set(self, "nameRegex", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pathPrefix")
    def path_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pathPrefix"))

    @path_prefix.setter
    def path_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "pathPrefix", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.DataAwsIamUsersConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name_regex": "nameRegex",
        "path_prefix": "pathPrefix",
    },
)
class DataAwsIamUsersConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name_regex: typing.Optional[builtins.str] = None,
        path_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name_regex: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_users#name_regex DataAwsIamUsers#name_regex}.
        :param path_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_users#path_prefix DataAwsIamUsers#path_prefix}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if name_regex is not None:
            self._values["name_regex"] = name_regex
        if path_prefix is not None:
            self._values["path_prefix"] = path_prefix

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
    def name_regex(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_users#name_regex DataAwsIamUsers#name_regex}.'''
        result = self._values.get("name_regex")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def path_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/iam_users#path_prefix DataAwsIamUsers#path_prefix}.'''
        result = self._values.get("path_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsIamUsersConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IamAccessKey(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.IamAccessKey",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iam_access_key aws_iam_access_key}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        user: builtins.str,
        pgp_key: typing.Optional[builtins.str] = None,
        status: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iam_access_key aws_iam_access_key} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param user: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_access_key#user IamAccessKey#user}.
        :param pgp_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_access_key#pgp_key IamAccessKey#pgp_key}.
        :param status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_access_key#status IamAccessKey#status}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IamAccessKeyConfig(
            user=user,
            pgp_key=pgp_key,
            status=status,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetPgpKey")
    def reset_pgp_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPgpKey", []))

    @jsii.member(jsii_name="resetStatus")
    def reset_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatus", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createDate")
    def create_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptedSecret")
    def encrypted_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptedSecret"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptedSesSmtpPasswordV4")
    def encrypted_ses_smtp_password_v4(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptedSesSmtpPasswordV4"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyFingerprint")
    def key_fingerprint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyFingerprint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secret")
    def secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secret"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sesSmtpPasswordV4")
    def ses_smtp_password_v4(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sesSmtpPasswordV4"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pgpKeyInput")
    def pgp_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pgpKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statusInput")
    def status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userInput")
    def user_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pgpKey")
    def pgp_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pgpKey"))

    @pgp_key.setter
    def pgp_key(self, value: builtins.str) -> None:
        jsii.set(self, "pgpKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @status.setter
    def status(self, value: builtins.str) -> None:
        jsii.set(self, "status", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="user")
    def user(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "user"))

    @user.setter
    def user(self, value: builtins.str) -> None:
        jsii.set(self, "user", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.IamAccessKeyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "user": "user",
        "pgp_key": "pgpKey",
        "status": "status",
    },
)
class IamAccessKeyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        user: builtins.str,
        pgp_key: typing.Optional[builtins.str] = None,
        status: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param user: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_access_key#user IamAccessKey#user}.
        :param pgp_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_access_key#pgp_key IamAccessKey#pgp_key}.
        :param status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_access_key#status IamAccessKey#status}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "user": user,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if pgp_key is not None:
            self._values["pgp_key"] = pgp_key
        if status is not None:
            self._values["status"] = status

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
    def user(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_access_key#user IamAccessKey#user}.'''
        result = self._values.get("user")
        assert result is not None, "Required property 'user' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def pgp_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_access_key#pgp_key IamAccessKey#pgp_key}.'''
        result = self._values.get("pgp_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def status(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_access_key#status IamAccessKey#status}.'''
        result = self._values.get("status")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IamAccessKeyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IamAccountAlias(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.IamAccountAlias",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iam_account_alias aws_iam_account_alias}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        account_alias: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iam_account_alias aws_iam_account_alias} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_alias: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_account_alias#account_alias IamAccountAlias#account_alias}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IamAccountAliasConfig(
            account_alias=account_alias,
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
    @jsii.member(jsii_name="accountAliasInput")
    def account_alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountAliasInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountAlias")
    def account_alias(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountAlias"))

    @account_alias.setter
    def account_alias(self, value: builtins.str) -> None:
        jsii.set(self, "accountAlias", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.IamAccountAliasConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "account_alias": "accountAlias",
    },
)
class IamAccountAliasConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        account_alias: builtins.str,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param account_alias: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_account_alias#account_alias IamAccountAlias#account_alias}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "account_alias": account_alias,
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
    def account_alias(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_account_alias#account_alias IamAccountAlias#account_alias}.'''
        result = self._values.get("account_alias")
        assert result is not None, "Required property 'account_alias' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IamAccountAliasConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IamAccountPasswordPolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.IamAccountPasswordPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy aws_iam_account_password_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        allow_users_to_change_password: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        hard_expiry: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        max_password_age: typing.Optional[jsii.Number] = None,
        minimum_password_length: typing.Optional[jsii.Number] = None,
        password_reuse_prevention: typing.Optional[jsii.Number] = None,
        require_lowercase_characters: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        require_numbers: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        require_symbols: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        require_uppercase_characters: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy aws_iam_account_password_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param allow_users_to_change_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy#allow_users_to_change_password IamAccountPasswordPolicy#allow_users_to_change_password}.
        :param hard_expiry: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy#hard_expiry IamAccountPasswordPolicy#hard_expiry}.
        :param max_password_age: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy#max_password_age IamAccountPasswordPolicy#max_password_age}.
        :param minimum_password_length: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy#minimum_password_length IamAccountPasswordPolicy#minimum_password_length}.
        :param password_reuse_prevention: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy#password_reuse_prevention IamAccountPasswordPolicy#password_reuse_prevention}.
        :param require_lowercase_characters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy#require_lowercase_characters IamAccountPasswordPolicy#require_lowercase_characters}.
        :param require_numbers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy#require_numbers IamAccountPasswordPolicy#require_numbers}.
        :param require_symbols: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy#require_symbols IamAccountPasswordPolicy#require_symbols}.
        :param require_uppercase_characters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy#require_uppercase_characters IamAccountPasswordPolicy#require_uppercase_characters}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IamAccountPasswordPolicyConfig(
            allow_users_to_change_password=allow_users_to_change_password,
            hard_expiry=hard_expiry,
            max_password_age=max_password_age,
            minimum_password_length=minimum_password_length,
            password_reuse_prevention=password_reuse_prevention,
            require_lowercase_characters=require_lowercase_characters,
            require_numbers=require_numbers,
            require_symbols=require_symbols,
            require_uppercase_characters=require_uppercase_characters,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAllowUsersToChangePassword")
    def reset_allow_users_to_change_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowUsersToChangePassword", []))

    @jsii.member(jsii_name="resetHardExpiry")
    def reset_hard_expiry(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHardExpiry", []))

    @jsii.member(jsii_name="resetMaxPasswordAge")
    def reset_max_password_age(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxPasswordAge", []))

    @jsii.member(jsii_name="resetMinimumPasswordLength")
    def reset_minimum_password_length(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinimumPasswordLength", []))

    @jsii.member(jsii_name="resetPasswordReusePrevention")
    def reset_password_reuse_prevention(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordReusePrevention", []))

    @jsii.member(jsii_name="resetRequireLowercaseCharacters")
    def reset_require_lowercase_characters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequireLowercaseCharacters", []))

    @jsii.member(jsii_name="resetRequireNumbers")
    def reset_require_numbers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequireNumbers", []))

    @jsii.member(jsii_name="resetRequireSymbols")
    def reset_require_symbols(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequireSymbols", []))

    @jsii.member(jsii_name="resetRequireUppercaseCharacters")
    def reset_require_uppercase_characters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequireUppercaseCharacters", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="expirePasswords")
    def expire_passwords(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "expirePasswords"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowUsersToChangePasswordInput")
    def allow_users_to_change_password_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "allowUsersToChangePasswordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hardExpiryInput")
    def hard_expiry_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "hardExpiryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxPasswordAgeInput")
    def max_password_age_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxPasswordAgeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minimumPasswordLengthInput")
    def minimum_password_length_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minimumPasswordLengthInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwordReusePreventionInput")
    def password_reuse_prevention_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "passwordReusePreventionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requireLowercaseCharactersInput")
    def require_lowercase_characters_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "requireLowercaseCharactersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requireNumbersInput")
    def require_numbers_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "requireNumbersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requireSymbolsInput")
    def require_symbols_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "requireSymbolsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requireUppercaseCharactersInput")
    def require_uppercase_characters_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "requireUppercaseCharactersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowUsersToChangePassword")
    def allow_users_to_change_password(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "allowUsersToChangePassword"))

    @allow_users_to_change_password.setter
    def allow_users_to_change_password(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "allowUsersToChangePassword", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hardExpiry")
    def hard_expiry(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "hardExpiry"))

    @hard_expiry.setter
    def hard_expiry(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "hardExpiry", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxPasswordAge")
    def max_password_age(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxPasswordAge"))

    @max_password_age.setter
    def max_password_age(self, value: jsii.Number) -> None:
        jsii.set(self, "maxPasswordAge", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minimumPasswordLength")
    def minimum_password_length(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minimumPasswordLength"))

    @minimum_password_length.setter
    def minimum_password_length(self, value: jsii.Number) -> None:
        jsii.set(self, "minimumPasswordLength", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwordReusePrevention")
    def password_reuse_prevention(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "passwordReusePrevention"))

    @password_reuse_prevention.setter
    def password_reuse_prevention(self, value: jsii.Number) -> None:
        jsii.set(self, "passwordReusePrevention", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requireLowercaseCharacters")
    def require_lowercase_characters(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "requireLowercaseCharacters"))

    @require_lowercase_characters.setter
    def require_lowercase_characters(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "requireLowercaseCharacters", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requireNumbers")
    def require_numbers(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "requireNumbers"))

    @require_numbers.setter
    def require_numbers(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "requireNumbers", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requireSymbols")
    def require_symbols(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "requireSymbols"))

    @require_symbols.setter
    def require_symbols(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "requireSymbols", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requireUppercaseCharacters")
    def require_uppercase_characters(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "requireUppercaseCharacters"))

    @require_uppercase_characters.setter
    def require_uppercase_characters(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "requireUppercaseCharacters", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.IamAccountPasswordPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "allow_users_to_change_password": "allowUsersToChangePassword",
        "hard_expiry": "hardExpiry",
        "max_password_age": "maxPasswordAge",
        "minimum_password_length": "minimumPasswordLength",
        "password_reuse_prevention": "passwordReusePrevention",
        "require_lowercase_characters": "requireLowercaseCharacters",
        "require_numbers": "requireNumbers",
        "require_symbols": "requireSymbols",
        "require_uppercase_characters": "requireUppercaseCharacters",
    },
)
class IamAccountPasswordPolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        allow_users_to_change_password: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        hard_expiry: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        max_password_age: typing.Optional[jsii.Number] = None,
        minimum_password_length: typing.Optional[jsii.Number] = None,
        password_reuse_prevention: typing.Optional[jsii.Number] = None,
        require_lowercase_characters: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        require_numbers: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        require_symbols: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        require_uppercase_characters: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param allow_users_to_change_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy#allow_users_to_change_password IamAccountPasswordPolicy#allow_users_to_change_password}.
        :param hard_expiry: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy#hard_expiry IamAccountPasswordPolicy#hard_expiry}.
        :param max_password_age: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy#max_password_age IamAccountPasswordPolicy#max_password_age}.
        :param minimum_password_length: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy#minimum_password_length IamAccountPasswordPolicy#minimum_password_length}.
        :param password_reuse_prevention: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy#password_reuse_prevention IamAccountPasswordPolicy#password_reuse_prevention}.
        :param require_lowercase_characters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy#require_lowercase_characters IamAccountPasswordPolicy#require_lowercase_characters}.
        :param require_numbers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy#require_numbers IamAccountPasswordPolicy#require_numbers}.
        :param require_symbols: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy#require_symbols IamAccountPasswordPolicy#require_symbols}.
        :param require_uppercase_characters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy#require_uppercase_characters IamAccountPasswordPolicy#require_uppercase_characters}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if allow_users_to_change_password is not None:
            self._values["allow_users_to_change_password"] = allow_users_to_change_password
        if hard_expiry is not None:
            self._values["hard_expiry"] = hard_expiry
        if max_password_age is not None:
            self._values["max_password_age"] = max_password_age
        if minimum_password_length is not None:
            self._values["minimum_password_length"] = minimum_password_length
        if password_reuse_prevention is not None:
            self._values["password_reuse_prevention"] = password_reuse_prevention
        if require_lowercase_characters is not None:
            self._values["require_lowercase_characters"] = require_lowercase_characters
        if require_numbers is not None:
            self._values["require_numbers"] = require_numbers
        if require_symbols is not None:
            self._values["require_symbols"] = require_symbols
        if require_uppercase_characters is not None:
            self._values["require_uppercase_characters"] = require_uppercase_characters

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
    def allow_users_to_change_password(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy#allow_users_to_change_password IamAccountPasswordPolicy#allow_users_to_change_password}.'''
        result = self._values.get("allow_users_to_change_password")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def hard_expiry(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy#hard_expiry IamAccountPasswordPolicy#hard_expiry}.'''
        result = self._values.get("hard_expiry")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def max_password_age(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy#max_password_age IamAccountPasswordPolicy#max_password_age}.'''
        result = self._values.get("max_password_age")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def minimum_password_length(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy#minimum_password_length IamAccountPasswordPolicy#minimum_password_length}.'''
        result = self._values.get("minimum_password_length")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def password_reuse_prevention(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy#password_reuse_prevention IamAccountPasswordPolicy#password_reuse_prevention}.'''
        result = self._values.get("password_reuse_prevention")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def require_lowercase_characters(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy#require_lowercase_characters IamAccountPasswordPolicy#require_lowercase_characters}.'''
        result = self._values.get("require_lowercase_characters")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def require_numbers(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy#require_numbers IamAccountPasswordPolicy#require_numbers}.'''
        result = self._values.get("require_numbers")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def require_symbols(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy#require_symbols IamAccountPasswordPolicy#require_symbols}.'''
        result = self._values.get("require_symbols")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def require_uppercase_characters(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy#require_uppercase_characters IamAccountPasswordPolicy#require_uppercase_characters}.'''
        result = self._values.get("require_uppercase_characters")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IamAccountPasswordPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IamGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.IamGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iam_group aws_iam_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        path: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iam_group aws_iam_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_group#name IamGroup#name}.
        :param path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_group#path IamGroup#path}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IamGroupConfig(
            name=name,
            path=path,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetPath")
    def reset_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPath", []))

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
    @jsii.member(jsii_name="uniqueId")
    def unique_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uniqueId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        jsii.set(self, "path", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.IamGroupConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "path": "path",
    },
)
class IamGroupConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_group#name IamGroup#name}.
        :param path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_group#path IamGroup#path}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
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
        if path is not None:
            self._values["path"] = path

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_group#name IamGroup#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_group#path IamGroup#path}.'''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IamGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IamGroupMembership(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.IamGroupMembership",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iam_group_membership aws_iam_group_membership}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        group: builtins.str,
        name: builtins.str,
        users: typing.Sequence[builtins.str],
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iam_group_membership aws_iam_group_membership} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param group: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_group_membership#group IamGroupMembership#group}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_group_membership#name IamGroupMembership#name}.
        :param users: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_group_membership#users IamGroupMembership#users}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IamGroupMembershipConfig(
            group=group,
            name=name,
            users=users,
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
    @jsii.member(jsii_name="groupInput")
    def group_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "groupInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usersInput")
    def users_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "usersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="group")
    def group(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "group"))

    @group.setter
    def group(self, value: builtins.str) -> None:
        jsii.set(self, "group", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="users")
    def users(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "users"))

    @users.setter
    def users(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "users", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.IamGroupMembershipConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "group": "group",
        "name": "name",
        "users": "users",
    },
)
class IamGroupMembershipConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        group: builtins.str,
        name: builtins.str,
        users: typing.Sequence[builtins.str],
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param group: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_group_membership#group IamGroupMembership#group}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_group_membership#name IamGroupMembership#name}.
        :param users: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_group_membership#users IamGroupMembership#users}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "group": group,
            "name": name,
            "users": users,
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
    def group(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_group_membership#group IamGroupMembership#group}.'''
        result = self._values.get("group")
        assert result is not None, "Required property 'group' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_group_membership#name IamGroupMembership#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def users(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_group_membership#users IamGroupMembership#users}.'''
        result = self._values.get("users")
        assert result is not None, "Required property 'users' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IamGroupMembershipConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IamGroupPolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.IamGroupPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iam_group_policy aws_iam_group_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        group: builtins.str,
        policy: builtins.str,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iam_group_policy aws_iam_group_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param group: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_group_policy#group IamGroupPolicy#group}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_group_policy#policy IamGroupPolicy#policy}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_group_policy#name IamGroupPolicy#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_group_policy#name_prefix IamGroupPolicy#name_prefix}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IamGroupPolicyConfig(
            group=group,
            policy=policy,
            name=name,
            name_prefix=name_prefix,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNamePrefix")
    def reset_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamePrefix", []))

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
    @jsii.member(jsii_name="groupInput")
    def group_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "groupInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefixInput")
    def name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namePrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyInput")
    def policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="group")
    def group(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "group"))

    @group.setter
    def group(self, value: builtins.str) -> None:
        jsii.set(self, "group", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefix")
    def name_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namePrefix"))

    @name_prefix.setter
    def name_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "namePrefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: builtins.str) -> None:
        jsii.set(self, "policy", value)


class IamGroupPolicyAttachment(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.IamGroupPolicyAttachment",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iam_group_policy_attachment aws_iam_group_policy_attachment}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        group: builtins.str,
        policy_arn: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iam_group_policy_attachment aws_iam_group_policy_attachment} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param group: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_group_policy_attachment#group IamGroupPolicyAttachment#group}.
        :param policy_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_group_policy_attachment#policy_arn IamGroupPolicyAttachment#policy_arn}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IamGroupPolicyAttachmentConfig(
            group=group,
            policy_arn=policy_arn,
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
    @jsii.member(jsii_name="groupInput")
    def group_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "groupInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyArnInput")
    def policy_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="group")
    def group(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "group"))

    @group.setter
    def group(self, value: builtins.str) -> None:
        jsii.set(self, "group", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyArn")
    def policy_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyArn"))

    @policy_arn.setter
    def policy_arn(self, value: builtins.str) -> None:
        jsii.set(self, "policyArn", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.IamGroupPolicyAttachmentConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "group": "group",
        "policy_arn": "policyArn",
    },
)
class IamGroupPolicyAttachmentConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        group: builtins.str,
        policy_arn: builtins.str,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param group: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_group_policy_attachment#group IamGroupPolicyAttachment#group}.
        :param policy_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_group_policy_attachment#policy_arn IamGroupPolicyAttachment#policy_arn}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "group": group,
            "policy_arn": policy_arn,
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
    def group(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_group_policy_attachment#group IamGroupPolicyAttachment#group}.'''
        result = self._values.get("group")
        assert result is not None, "Required property 'group' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_group_policy_attachment#policy_arn IamGroupPolicyAttachment#policy_arn}.'''
        result = self._values.get("policy_arn")
        assert result is not None, "Required property 'policy_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IamGroupPolicyAttachmentConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.IamGroupPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "group": "group",
        "policy": "policy",
        "name": "name",
        "name_prefix": "namePrefix",
    },
)
class IamGroupPolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        group: builtins.str,
        policy: builtins.str,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param group: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_group_policy#group IamGroupPolicy#group}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_group_policy#policy IamGroupPolicy#policy}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_group_policy#name IamGroupPolicy#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_group_policy#name_prefix IamGroupPolicy#name_prefix}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "group": group,
            "policy": policy,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if name is not None:
            self._values["name"] = name
        if name_prefix is not None:
            self._values["name_prefix"] = name_prefix

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
    def group(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_group_policy#group IamGroupPolicy#group}.'''
        result = self._values.get("group")
        assert result is not None, "Required property 'group' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_group_policy#policy IamGroupPolicy#policy}.'''
        result = self._values.get("policy")
        assert result is not None, "Required property 'policy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_group_policy#name IamGroupPolicy#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_group_policy#name_prefix IamGroupPolicy#name_prefix}.'''
        result = self._values.get("name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IamGroupPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IamInstanceProfile(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.IamInstanceProfile",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iam_instance_profile aws_iam_instance_profile}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
        role: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iam_instance_profile aws_iam_instance_profile} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_instance_profile#name IamInstanceProfile#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_instance_profile#name_prefix IamInstanceProfile#name_prefix}.
        :param path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_instance_profile#path IamInstanceProfile#path}.
        :param role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_instance_profile#role IamInstanceProfile#role}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_instance_profile#tags IamInstanceProfile#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_instance_profile#tags_all IamInstanceProfile#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IamInstanceProfileConfig(
            name=name,
            name_prefix=name_prefix,
            path=path,
            role=role,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNamePrefix")
    def reset_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamePrefix", []))

    @jsii.member(jsii_name="resetPath")
    def reset_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPath", []))

    @jsii.member(jsii_name="resetRole")
    def reset_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRole", []))

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
    @jsii.member(jsii_name="createDate")
    def create_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uniqueId")
    def unique_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uniqueId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefixInput")
    def name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namePrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleInput")
    def role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleInput"))

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
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefix")
    def name_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namePrefix"))

    @name_prefix.setter
    def name_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "namePrefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        jsii.set(self, "path", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @role.setter
    def role(self, value: builtins.str) -> None:
        jsii.set(self, "role", value)

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
    jsii_type="@cdktf/provider-aws.iam.IamInstanceProfileConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "name_prefix": "namePrefix",
        "path": "path",
        "role": "role",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class IamInstanceProfileConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
        role: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_instance_profile#name IamInstanceProfile#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_instance_profile#name_prefix IamInstanceProfile#name_prefix}.
        :param path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_instance_profile#path IamInstanceProfile#path}.
        :param role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_instance_profile#role IamInstanceProfile#role}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_instance_profile#tags IamInstanceProfile#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_instance_profile#tags_all IamInstanceProfile#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if name is not None:
            self._values["name"] = name
        if name_prefix is not None:
            self._values["name_prefix"] = name_prefix
        if path is not None:
            self._values["path"] = path
        if role is not None:
            self._values["role"] = role
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
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_instance_profile#name IamInstanceProfile#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_instance_profile#name_prefix IamInstanceProfile#name_prefix}.'''
        result = self._values.get("name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_instance_profile#path IamInstanceProfile#path}.'''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_instance_profile#role IamInstanceProfile#role}.'''
        result = self._values.get("role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_instance_profile#tags IamInstanceProfile#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_instance_profile#tags_all IamInstanceProfile#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IamInstanceProfileConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IamOpenidConnectProvider(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.IamOpenidConnectProvider",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iam_openid_connect_provider aws_iam_openid_connect_provider}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        client_id_list: typing.Sequence[builtins.str],
        thumbprint_list: typing.Sequence[builtins.str],
        url: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iam_openid_connect_provider aws_iam_openid_connect_provider} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param client_id_list: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_openid_connect_provider#client_id_list IamOpenidConnectProvider#client_id_list}.
        :param thumbprint_list: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_openid_connect_provider#thumbprint_list IamOpenidConnectProvider#thumbprint_list}.
        :param url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_openid_connect_provider#url IamOpenidConnectProvider#url}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_openid_connect_provider#tags IamOpenidConnectProvider#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_openid_connect_provider#tags_all IamOpenidConnectProvider#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IamOpenidConnectProviderConfig(
            client_id_list=client_id_list,
            thumbprint_list=thumbprint_list,
            url=url,
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
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientIdListInput")
    def client_id_list_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "clientIdListInput"))

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
    @jsii.member(jsii_name="thumbprintListInput")
    def thumbprint_list_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "thumbprintListInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientIdList")
    def client_id_list(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "clientIdList"))

    @client_id_list.setter
    def client_id_list(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "clientIdList", value)

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
    @jsii.member(jsii_name="thumbprintList")
    def thumbprint_list(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "thumbprintList"))

    @thumbprint_list.setter
    def thumbprint_list(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "thumbprintList", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        jsii.set(self, "url", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.IamOpenidConnectProviderConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "client_id_list": "clientIdList",
        "thumbprint_list": "thumbprintList",
        "url": "url",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class IamOpenidConnectProviderConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        client_id_list: typing.Sequence[builtins.str],
        thumbprint_list: typing.Sequence[builtins.str],
        url: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param client_id_list: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_openid_connect_provider#client_id_list IamOpenidConnectProvider#client_id_list}.
        :param thumbprint_list: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_openid_connect_provider#thumbprint_list IamOpenidConnectProvider#thumbprint_list}.
        :param url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_openid_connect_provider#url IamOpenidConnectProvider#url}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_openid_connect_provider#tags IamOpenidConnectProvider#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_openid_connect_provider#tags_all IamOpenidConnectProvider#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "client_id_list": client_id_list,
            "thumbprint_list": thumbprint_list,
            "url": url,
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
    def client_id_list(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_openid_connect_provider#client_id_list IamOpenidConnectProvider#client_id_list}.'''
        result = self._values.get("client_id_list")
        assert result is not None, "Required property 'client_id_list' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def thumbprint_list(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_openid_connect_provider#thumbprint_list IamOpenidConnectProvider#thumbprint_list}.'''
        result = self._values.get("thumbprint_list")
        assert result is not None, "Required property 'thumbprint_list' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_openid_connect_provider#url IamOpenidConnectProvider#url}.'''
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_openid_connect_provider#tags IamOpenidConnectProvider#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_openid_connect_provider#tags_all IamOpenidConnectProvider#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IamOpenidConnectProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IamPolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.IamPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iam_policy aws_iam_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        policy: builtins.str,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iam_policy aws_iam_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy#policy IamPolicy#policy}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy#description IamPolicy#description}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy#name IamPolicy#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy#name_prefix IamPolicy#name_prefix}.
        :param path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy#path IamPolicy#path}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy#tags IamPolicy#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy#tags_all IamPolicy#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IamPolicyConfig(
            policy=policy,
            description=description,
            name=name,
            name_prefix=name_prefix,
            path=path,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNamePrefix")
    def reset_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamePrefix", []))

    @jsii.member(jsii_name="resetPath")
    def reset_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPath", []))

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
    @jsii.member(jsii_name="policyId")
    def policy_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefixInput")
    def name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namePrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyInput")
    def policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyInput"))

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
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefix")
    def name_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namePrefix"))

    @name_prefix.setter
    def name_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "namePrefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        jsii.set(self, "path", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: builtins.str) -> None:
        jsii.set(self, "policy", value)

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


class IamPolicyAttachment(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.IamPolicyAttachment",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iam_policy_attachment aws_iam_policy_attachment}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        policy_arn: builtins.str,
        groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        roles: typing.Optional[typing.Sequence[builtins.str]] = None,
        users: typing.Optional[typing.Sequence[builtins.str]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iam_policy_attachment aws_iam_policy_attachment} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy_attachment#name IamPolicyAttachment#name}.
        :param policy_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy_attachment#policy_arn IamPolicyAttachment#policy_arn}.
        :param groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy_attachment#groups IamPolicyAttachment#groups}.
        :param roles: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy_attachment#roles IamPolicyAttachment#roles}.
        :param users: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy_attachment#users IamPolicyAttachment#users}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IamPolicyAttachmentConfig(
            name=name,
            policy_arn=policy_arn,
            groups=groups,
            roles=roles,
            users=users,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetGroups")
    def reset_groups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGroups", []))

    @jsii.member(jsii_name="resetRoles")
    def reset_roles(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoles", []))

    @jsii.member(jsii_name="resetUsers")
    def reset_users(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsers", []))

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
    @jsii.member(jsii_name="groupsInput")
    def groups_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "groupsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyArnInput")
    def policy_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rolesInput")
    def roles_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "rolesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usersInput")
    def users_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "usersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="groups")
    def groups(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "groups"))

    @groups.setter
    def groups(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "groups", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyArn")
    def policy_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyArn"))

    @policy_arn.setter
    def policy_arn(self, value: builtins.str) -> None:
        jsii.set(self, "policyArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roles")
    def roles(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "roles"))

    @roles.setter
    def roles(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "roles", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="users")
    def users(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "users"))

    @users.setter
    def users(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "users", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.IamPolicyAttachmentConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "policy_arn": "policyArn",
        "groups": "groups",
        "roles": "roles",
        "users": "users",
    },
)
class IamPolicyAttachmentConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        policy_arn: builtins.str,
        groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        roles: typing.Optional[typing.Sequence[builtins.str]] = None,
        users: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy_attachment#name IamPolicyAttachment#name}.
        :param policy_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy_attachment#policy_arn IamPolicyAttachment#policy_arn}.
        :param groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy_attachment#groups IamPolicyAttachment#groups}.
        :param roles: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy_attachment#roles IamPolicyAttachment#roles}.
        :param users: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy_attachment#users IamPolicyAttachment#users}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "policy_arn": policy_arn,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if groups is not None:
            self._values["groups"] = groups
        if roles is not None:
            self._values["roles"] = roles
        if users is not None:
            self._values["users"] = users

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy_attachment#name IamPolicyAttachment#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy_attachment#policy_arn IamPolicyAttachment#policy_arn}.'''
        result = self._values.get("policy_arn")
        assert result is not None, "Required property 'policy_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def groups(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy_attachment#groups IamPolicyAttachment#groups}.'''
        result = self._values.get("groups")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def roles(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy_attachment#roles IamPolicyAttachment#roles}.'''
        result = self._values.get("roles")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def users(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy_attachment#users IamPolicyAttachment#users}.'''
        result = self._values.get("users")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IamPolicyAttachmentConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.IamPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "policy": "policy",
        "description": "description",
        "name": "name",
        "name_prefix": "namePrefix",
        "path": "path",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class IamPolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        policy: builtins.str,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy#policy IamPolicy#policy}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy#description IamPolicy#description}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy#name IamPolicy#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy#name_prefix IamPolicy#name_prefix}.
        :param path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy#path IamPolicy#path}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy#tags IamPolicy#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy#tags_all IamPolicy#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "policy": policy,
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
        if name is not None:
            self._values["name"] = name
        if name_prefix is not None:
            self._values["name_prefix"] = name_prefix
        if path is not None:
            self._values["path"] = path
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
    def policy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy#policy IamPolicy#policy}.'''
        result = self._values.get("policy")
        assert result is not None, "Required property 'policy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy#description IamPolicy#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy#name IamPolicy#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy#name_prefix IamPolicy#name_prefix}.'''
        result = self._values.get("name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy#path IamPolicy#path}.'''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy#tags IamPolicy#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_policy#tags_all IamPolicy#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IamPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IamRole(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.IamRole",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iam_role aws_iam_role}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        assume_role_policy: builtins.str,
        description: typing.Optional[builtins.str] = None,
        force_detach_policies: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        inline_policy: typing.Optional[typing.Sequence["IamRoleInlinePolicy"]] = None,
        managed_policy_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        max_session_duration: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
        permissions_boundary: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iam_role aws_iam_role} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param assume_role_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#assume_role_policy IamRole#assume_role_policy}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#description IamRole#description}.
        :param force_detach_policies: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#force_detach_policies IamRole#force_detach_policies}.
        :param inline_policy: inline_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#inline_policy IamRole#inline_policy}
        :param managed_policy_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#managed_policy_arns IamRole#managed_policy_arns}.
        :param max_session_duration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#max_session_duration IamRole#max_session_duration}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#name IamRole#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#name_prefix IamRole#name_prefix}.
        :param path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#path IamRole#path}.
        :param permissions_boundary: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#permissions_boundary IamRole#permissions_boundary}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#tags IamRole#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#tags_all IamRole#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IamRoleConfig(
            assume_role_policy=assume_role_policy,
            description=description,
            force_detach_policies=force_detach_policies,
            inline_policy=inline_policy,
            managed_policy_arns=managed_policy_arns,
            max_session_duration=max_session_duration,
            name=name,
            name_prefix=name_prefix,
            path=path,
            permissions_boundary=permissions_boundary,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetForceDetachPolicies")
    def reset_force_detach_policies(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceDetachPolicies", []))

    @jsii.member(jsii_name="resetInlinePolicy")
    def reset_inline_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInlinePolicy", []))

    @jsii.member(jsii_name="resetManagedPolicyArns")
    def reset_managed_policy_arns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManagedPolicyArns", []))

    @jsii.member(jsii_name="resetMaxSessionDuration")
    def reset_max_session_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxSessionDuration", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNamePrefix")
    def reset_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamePrefix", []))

    @jsii.member(jsii_name="resetPath")
    def reset_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPath", []))

    @jsii.member(jsii_name="resetPermissionsBoundary")
    def reset_permissions_boundary(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPermissionsBoundary", []))

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
    @jsii.member(jsii_name="createDate")
    def create_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uniqueId")
    def unique_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uniqueId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="assumeRolePolicyInput")
    def assume_role_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "assumeRolePolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceDetachPoliciesInput")
    def force_detach_policies_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "forceDetachPoliciesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inlinePolicyInput")
    def inline_policy_input(
        self,
    ) -> typing.Optional[typing.List["IamRoleInlinePolicy"]]:
        return typing.cast(typing.Optional[typing.List["IamRoleInlinePolicy"]], jsii.get(self, "inlinePolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="managedPolicyArnsInput")
    def managed_policy_arns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "managedPolicyArnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxSessionDurationInput")
    def max_session_duration_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxSessionDurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefixInput")
    def name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namePrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="permissionsBoundaryInput")
    def permissions_boundary_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "permissionsBoundaryInput"))

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
    @jsii.member(jsii_name="assumeRolePolicy")
    def assume_role_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "assumeRolePolicy"))

    @assume_role_policy.setter
    def assume_role_policy(self, value: builtins.str) -> None:
        jsii.set(self, "assumeRolePolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceDetachPolicies")
    def force_detach_policies(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "forceDetachPolicies"))

    @force_detach_policies.setter
    def force_detach_policies(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "forceDetachPolicies", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inlinePolicy")
    def inline_policy(self) -> typing.List["IamRoleInlinePolicy"]:
        return typing.cast(typing.List["IamRoleInlinePolicy"], jsii.get(self, "inlinePolicy"))

    @inline_policy.setter
    def inline_policy(self, value: typing.List["IamRoleInlinePolicy"]) -> None:
        jsii.set(self, "inlinePolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="managedPolicyArns")
    def managed_policy_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "managedPolicyArns"))

    @managed_policy_arns.setter
    def managed_policy_arns(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "managedPolicyArns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxSessionDuration")
    def max_session_duration(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxSessionDuration"))

    @max_session_duration.setter
    def max_session_duration(self, value: jsii.Number) -> None:
        jsii.set(self, "maxSessionDuration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefix")
    def name_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namePrefix"))

    @name_prefix.setter
    def name_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "namePrefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        jsii.set(self, "path", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="permissionsBoundary")
    def permissions_boundary(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "permissionsBoundary"))

    @permissions_boundary.setter
    def permissions_boundary(self, value: builtins.str) -> None:
        jsii.set(self, "permissionsBoundary", value)

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
    jsii_type="@cdktf/provider-aws.iam.IamRoleConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "assume_role_policy": "assumeRolePolicy",
        "description": "description",
        "force_detach_policies": "forceDetachPolicies",
        "inline_policy": "inlinePolicy",
        "managed_policy_arns": "managedPolicyArns",
        "max_session_duration": "maxSessionDuration",
        "name": "name",
        "name_prefix": "namePrefix",
        "path": "path",
        "permissions_boundary": "permissionsBoundary",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class IamRoleConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        assume_role_policy: builtins.str,
        description: typing.Optional[builtins.str] = None,
        force_detach_policies: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        inline_policy: typing.Optional[typing.Sequence["IamRoleInlinePolicy"]] = None,
        managed_policy_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        max_session_duration: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
        permissions_boundary: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param assume_role_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#assume_role_policy IamRole#assume_role_policy}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#description IamRole#description}.
        :param force_detach_policies: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#force_detach_policies IamRole#force_detach_policies}.
        :param inline_policy: inline_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#inline_policy IamRole#inline_policy}
        :param managed_policy_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#managed_policy_arns IamRole#managed_policy_arns}.
        :param max_session_duration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#max_session_duration IamRole#max_session_duration}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#name IamRole#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#name_prefix IamRole#name_prefix}.
        :param path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#path IamRole#path}.
        :param permissions_boundary: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#permissions_boundary IamRole#permissions_boundary}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#tags IamRole#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#tags_all IamRole#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "assume_role_policy": assume_role_policy,
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
        if force_detach_policies is not None:
            self._values["force_detach_policies"] = force_detach_policies
        if inline_policy is not None:
            self._values["inline_policy"] = inline_policy
        if managed_policy_arns is not None:
            self._values["managed_policy_arns"] = managed_policy_arns
        if max_session_duration is not None:
            self._values["max_session_duration"] = max_session_duration
        if name is not None:
            self._values["name"] = name
        if name_prefix is not None:
            self._values["name_prefix"] = name_prefix
        if path is not None:
            self._values["path"] = path
        if permissions_boundary is not None:
            self._values["permissions_boundary"] = permissions_boundary
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
    def assume_role_policy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#assume_role_policy IamRole#assume_role_policy}.'''
        result = self._values.get("assume_role_policy")
        assert result is not None, "Required property 'assume_role_policy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#description IamRole#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def force_detach_policies(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#force_detach_policies IamRole#force_detach_policies}.'''
        result = self._values.get("force_detach_policies")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def inline_policy(self) -> typing.Optional[typing.List["IamRoleInlinePolicy"]]:
        '''inline_policy block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#inline_policy IamRole#inline_policy}
        '''
        result = self._values.get("inline_policy")
        return typing.cast(typing.Optional[typing.List["IamRoleInlinePolicy"]], result)

    @builtins.property
    def managed_policy_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#managed_policy_arns IamRole#managed_policy_arns}.'''
        result = self._values.get("managed_policy_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def max_session_duration(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#max_session_duration IamRole#max_session_duration}.'''
        result = self._values.get("max_session_duration")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#name IamRole#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#name_prefix IamRole#name_prefix}.'''
        result = self._values.get("name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#path IamRole#path}.'''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def permissions_boundary(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#permissions_boundary IamRole#permissions_boundary}.'''
        result = self._values.get("permissions_boundary")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#tags IamRole#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#tags_all IamRole#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IamRoleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.IamRoleInlinePolicy",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "policy": "policy"},
)
class IamRoleInlinePolicy:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        policy: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#name IamRole#name}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#policy IamRole#policy}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if policy is not None:
            self._values["policy"] = policy

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#name IamRole#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def policy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role#policy IamRole#policy}.'''
        result = self._values.get("policy")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IamRoleInlinePolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IamRolePolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.IamRolePolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iam_role_policy aws_iam_role_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        policy: builtins.str,
        role: builtins.str,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iam_role_policy aws_iam_role_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role_policy#policy IamRolePolicy#policy}.
        :param role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role_policy#role IamRolePolicy#role}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role_policy#name IamRolePolicy#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role_policy#name_prefix IamRolePolicy#name_prefix}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IamRolePolicyConfig(
            policy=policy,
            role=role,
            name=name,
            name_prefix=name_prefix,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNamePrefix")
    def reset_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamePrefix", []))

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
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefixInput")
    def name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namePrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyInput")
    def policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleInput")
    def role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefix")
    def name_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namePrefix"))

    @name_prefix.setter
    def name_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "namePrefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: builtins.str) -> None:
        jsii.set(self, "policy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @role.setter
    def role(self, value: builtins.str) -> None:
        jsii.set(self, "role", value)


class IamRolePolicyAttachment(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.IamRolePolicyAttachment",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iam_role_policy_attachment aws_iam_role_policy_attachment}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        policy_arn: builtins.str,
        role: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iam_role_policy_attachment aws_iam_role_policy_attachment} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param policy_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role_policy_attachment#policy_arn IamRolePolicyAttachment#policy_arn}.
        :param role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role_policy_attachment#role IamRolePolicyAttachment#role}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IamRolePolicyAttachmentConfig(
            policy_arn=policy_arn,
            role=role,
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
    @jsii.member(jsii_name="policyArnInput")
    def policy_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleInput")
    def role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyArn")
    def policy_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyArn"))

    @policy_arn.setter
    def policy_arn(self, value: builtins.str) -> None:
        jsii.set(self, "policyArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @role.setter
    def role(self, value: builtins.str) -> None:
        jsii.set(self, "role", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.IamRolePolicyAttachmentConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "policy_arn": "policyArn",
        "role": "role",
    },
)
class IamRolePolicyAttachmentConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        policy_arn: builtins.str,
        role: builtins.str,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param policy_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role_policy_attachment#policy_arn IamRolePolicyAttachment#policy_arn}.
        :param role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role_policy_attachment#role IamRolePolicyAttachment#role}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "policy_arn": policy_arn,
            "role": role,
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
    def policy_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role_policy_attachment#policy_arn IamRolePolicyAttachment#policy_arn}.'''
        result = self._values.get("policy_arn")
        assert result is not None, "Required property 'policy_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role_policy_attachment#role IamRolePolicyAttachment#role}.'''
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IamRolePolicyAttachmentConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.IamRolePolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "policy": "policy",
        "role": "role",
        "name": "name",
        "name_prefix": "namePrefix",
    },
)
class IamRolePolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        policy: builtins.str,
        role: builtins.str,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role_policy#policy IamRolePolicy#policy}.
        :param role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role_policy#role IamRolePolicy#role}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role_policy#name IamRolePolicy#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role_policy#name_prefix IamRolePolicy#name_prefix}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "policy": policy,
            "role": role,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if name is not None:
            self._values["name"] = name
        if name_prefix is not None:
            self._values["name_prefix"] = name_prefix

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
    def policy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role_policy#policy IamRolePolicy#policy}.'''
        result = self._values.get("policy")
        assert result is not None, "Required property 'policy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role_policy#role IamRolePolicy#role}.'''
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role_policy#name IamRolePolicy#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_role_policy#name_prefix IamRolePolicy#name_prefix}.'''
        result = self._values.get("name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IamRolePolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IamSamlProvider(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.IamSamlProvider",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iam_saml_provider aws_iam_saml_provider}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        saml_metadata_document: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iam_saml_provider aws_iam_saml_provider} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_saml_provider#name IamSamlProvider#name}.
        :param saml_metadata_document: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_saml_provider#saml_metadata_document IamSamlProvider#saml_metadata_document}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_saml_provider#tags IamSamlProvider#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_saml_provider#tags_all IamSamlProvider#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IamSamlProviderConfig(
            name=name,
            saml_metadata_document=saml_metadata_document,
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
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="validUntil")
    def valid_until(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "validUntil"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="samlMetadataDocumentInput")
    def saml_metadata_document_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "samlMetadataDocumentInput"))

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
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="samlMetadataDocument")
    def saml_metadata_document(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "samlMetadataDocument"))

    @saml_metadata_document.setter
    def saml_metadata_document(self, value: builtins.str) -> None:
        jsii.set(self, "samlMetadataDocument", value)

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
    jsii_type="@cdktf/provider-aws.iam.IamSamlProviderConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "saml_metadata_document": "samlMetadataDocument",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class IamSamlProviderConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        saml_metadata_document: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_saml_provider#name IamSamlProvider#name}.
        :param saml_metadata_document: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_saml_provider#saml_metadata_document IamSamlProvider#saml_metadata_document}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_saml_provider#tags IamSamlProvider#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_saml_provider#tags_all IamSamlProvider#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "saml_metadata_document": saml_metadata_document,
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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_saml_provider#name IamSamlProvider#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def saml_metadata_document(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_saml_provider#saml_metadata_document IamSamlProvider#saml_metadata_document}.'''
        result = self._values.get("saml_metadata_document")
        assert result is not None, "Required property 'saml_metadata_document' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_saml_provider#tags IamSamlProvider#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_saml_provider#tags_all IamSamlProvider#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IamSamlProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IamServerCertificate(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.IamServerCertificate",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iam_server_certificate aws_iam_server_certificate}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        certificate_body: builtins.str,
        private_key: builtins.str,
        certificate_chain: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iam_server_certificate aws_iam_server_certificate} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param certificate_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_server_certificate#certificate_body IamServerCertificate#certificate_body}.
        :param private_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_server_certificate#private_key IamServerCertificate#private_key}.
        :param certificate_chain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_server_certificate#certificate_chain IamServerCertificate#certificate_chain}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_server_certificate#name IamServerCertificate#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_server_certificate#name_prefix IamServerCertificate#name_prefix}.
        :param path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_server_certificate#path IamServerCertificate#path}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_server_certificate#tags IamServerCertificate#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_server_certificate#tags_all IamServerCertificate#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IamServerCertificateConfig(
            certificate_body=certificate_body,
            private_key=private_key,
            certificate_chain=certificate_chain,
            name=name,
            name_prefix=name_prefix,
            path=path,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetCertificateChain")
    def reset_certificate_chain(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateChain", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNamePrefix")
    def reset_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamePrefix", []))

    @jsii.member(jsii_name="resetPath")
    def reset_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPath", []))

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
    @jsii.member(jsii_name="expiration")
    def expiration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "expiration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uploadDate")
    def upload_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uploadDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateBodyInput")
    def certificate_body_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateBodyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateChainInput")
    def certificate_chain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateChainInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefixInput")
    def name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namePrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateKeyInput")
    def private_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateKeyInput"))

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
    @jsii.member(jsii_name="certificateBody")
    def certificate_body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateBody"))

    @certificate_body.setter
    def certificate_body(self, value: builtins.str) -> None:
        jsii.set(self, "certificateBody", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateChain")
    def certificate_chain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateChain"))

    @certificate_chain.setter
    def certificate_chain(self, value: builtins.str) -> None:
        jsii.set(self, "certificateChain", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefix")
    def name_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namePrefix"))

    @name_prefix.setter
    def name_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "namePrefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        jsii.set(self, "path", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateKey")
    def private_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKey"))

    @private_key.setter
    def private_key(self, value: builtins.str) -> None:
        jsii.set(self, "privateKey", value)

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
    jsii_type="@cdktf/provider-aws.iam.IamServerCertificateConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "certificate_body": "certificateBody",
        "private_key": "privateKey",
        "certificate_chain": "certificateChain",
        "name": "name",
        "name_prefix": "namePrefix",
        "path": "path",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class IamServerCertificateConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        certificate_body: builtins.str,
        private_key: builtins.str,
        certificate_chain: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param certificate_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_server_certificate#certificate_body IamServerCertificate#certificate_body}.
        :param private_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_server_certificate#private_key IamServerCertificate#private_key}.
        :param certificate_chain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_server_certificate#certificate_chain IamServerCertificate#certificate_chain}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_server_certificate#name IamServerCertificate#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_server_certificate#name_prefix IamServerCertificate#name_prefix}.
        :param path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_server_certificate#path IamServerCertificate#path}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_server_certificate#tags IamServerCertificate#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_server_certificate#tags_all IamServerCertificate#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "certificate_body": certificate_body,
            "private_key": private_key,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if certificate_chain is not None:
            self._values["certificate_chain"] = certificate_chain
        if name is not None:
            self._values["name"] = name
        if name_prefix is not None:
            self._values["name_prefix"] = name_prefix
        if path is not None:
            self._values["path"] = path
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
    def certificate_body(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_server_certificate#certificate_body IamServerCertificate#certificate_body}.'''
        result = self._values.get("certificate_body")
        assert result is not None, "Required property 'certificate_body' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def private_key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_server_certificate#private_key IamServerCertificate#private_key}.'''
        result = self._values.get("private_key")
        assert result is not None, "Required property 'private_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def certificate_chain(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_server_certificate#certificate_chain IamServerCertificate#certificate_chain}.'''
        result = self._values.get("certificate_chain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_server_certificate#name IamServerCertificate#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_server_certificate#name_prefix IamServerCertificate#name_prefix}.'''
        result = self._values.get("name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_server_certificate#path IamServerCertificate#path}.'''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_server_certificate#tags IamServerCertificate#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_server_certificate#tags_all IamServerCertificate#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IamServerCertificateConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IamServiceLinkedRole(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.IamServiceLinkedRole",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iam_service_linked_role aws_iam_service_linked_role}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        aws_service_name: builtins.str,
        custom_suffix: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iam_service_linked_role aws_iam_service_linked_role} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param aws_service_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_service_linked_role#aws_service_name IamServiceLinkedRole#aws_service_name}.
        :param custom_suffix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_service_linked_role#custom_suffix IamServiceLinkedRole#custom_suffix}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_service_linked_role#description IamServiceLinkedRole#description}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_service_linked_role#tags IamServiceLinkedRole#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_service_linked_role#tags_all IamServiceLinkedRole#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IamServiceLinkedRoleConfig(
            aws_service_name=aws_service_name,
            custom_suffix=custom_suffix,
            description=description,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetCustomSuffix")
    def reset_custom_suffix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomSuffix", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

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
    @jsii.member(jsii_name="createDate")
    def create_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uniqueId")
    def unique_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uniqueId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="awsServiceNameInput")
    def aws_service_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsServiceNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSuffixInput")
    def custom_suffix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customSuffixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

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
    @jsii.member(jsii_name="awsServiceName")
    def aws_service_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsServiceName"))

    @aws_service_name.setter
    def aws_service_name(self, value: builtins.str) -> None:
        jsii.set(self, "awsServiceName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSuffix")
    def custom_suffix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customSuffix"))

    @custom_suffix.setter
    def custom_suffix(self, value: builtins.str) -> None:
        jsii.set(self, "customSuffix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

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
    jsii_type="@cdktf/provider-aws.iam.IamServiceLinkedRoleConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "aws_service_name": "awsServiceName",
        "custom_suffix": "customSuffix",
        "description": "description",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class IamServiceLinkedRoleConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        aws_service_name: builtins.str,
        custom_suffix: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param aws_service_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_service_linked_role#aws_service_name IamServiceLinkedRole#aws_service_name}.
        :param custom_suffix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_service_linked_role#custom_suffix IamServiceLinkedRole#custom_suffix}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_service_linked_role#description IamServiceLinkedRole#description}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_service_linked_role#tags IamServiceLinkedRole#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_service_linked_role#tags_all IamServiceLinkedRole#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "aws_service_name": aws_service_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if custom_suffix is not None:
            self._values["custom_suffix"] = custom_suffix
        if description is not None:
            self._values["description"] = description
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
    def aws_service_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_service_linked_role#aws_service_name IamServiceLinkedRole#aws_service_name}.'''
        result = self._values.get("aws_service_name")
        assert result is not None, "Required property 'aws_service_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def custom_suffix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_service_linked_role#custom_suffix IamServiceLinkedRole#custom_suffix}.'''
        result = self._values.get("custom_suffix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_service_linked_role#description IamServiceLinkedRole#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_service_linked_role#tags IamServiceLinkedRole#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_service_linked_role#tags_all IamServiceLinkedRole#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IamServiceLinkedRoleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IamUser(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.IamUser",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iam_user aws_iam_user}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        force_destroy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        path: typing.Optional[builtins.str] = None,
        permissions_boundary: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iam_user aws_iam_user} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user#name IamUser#name}.
        :param force_destroy: Delete user even if it has non-Terraform-managed IAM access keys, login profile or MFA devices. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user#force_destroy IamUser#force_destroy}
        :param path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user#path IamUser#path}.
        :param permissions_boundary: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user#permissions_boundary IamUser#permissions_boundary}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user#tags IamUser#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user#tags_all IamUser#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IamUserConfig(
            name=name,
            force_destroy=force_destroy,
            path=path,
            permissions_boundary=permissions_boundary,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetForceDestroy")
    def reset_force_destroy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceDestroy", []))

    @jsii.member(jsii_name="resetPath")
    def reset_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPath", []))

    @jsii.member(jsii_name="resetPermissionsBoundary")
    def reset_permissions_boundary(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPermissionsBoundary", []))

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
    @jsii.member(jsii_name="uniqueId")
    def unique_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uniqueId"))

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
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="permissionsBoundaryInput")
    def permissions_boundary_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "permissionsBoundaryInput"))

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
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        jsii.set(self, "path", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="permissionsBoundary")
    def permissions_boundary(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "permissionsBoundary"))

    @permissions_boundary.setter
    def permissions_boundary(self, value: builtins.str) -> None:
        jsii.set(self, "permissionsBoundary", value)

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
    jsii_type="@cdktf/provider-aws.iam.IamUserConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "force_destroy": "forceDestroy",
        "path": "path",
        "permissions_boundary": "permissionsBoundary",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class IamUserConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        force_destroy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        path: typing.Optional[builtins.str] = None,
        permissions_boundary: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user#name IamUser#name}.
        :param force_destroy: Delete user even if it has non-Terraform-managed IAM access keys, login profile or MFA devices. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user#force_destroy IamUser#force_destroy}
        :param path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user#path IamUser#path}.
        :param permissions_boundary: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user#permissions_boundary IamUser#permissions_boundary}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user#tags IamUser#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user#tags_all IamUser#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
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
        if force_destroy is not None:
            self._values["force_destroy"] = force_destroy
        if path is not None:
            self._values["path"] = path
        if permissions_boundary is not None:
            self._values["permissions_boundary"] = permissions_boundary
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user#name IamUser#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def force_destroy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Delete user even if it has non-Terraform-managed IAM access keys, login profile or MFA devices.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user#force_destroy IamUser#force_destroy}
        '''
        result = self._values.get("force_destroy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user#path IamUser#path}.'''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def permissions_boundary(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user#permissions_boundary IamUser#permissions_boundary}.'''
        result = self._values.get("permissions_boundary")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user#tags IamUser#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user#tags_all IamUser#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IamUserConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IamUserGroupMembership(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.IamUserGroupMembership",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iam_user_group_membership aws_iam_user_group_membership}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        groups: typing.Sequence[builtins.str],
        user: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iam_user_group_membership aws_iam_user_group_membership} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_group_membership#groups IamUserGroupMembership#groups}.
        :param user: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_group_membership#user IamUserGroupMembership#user}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IamUserGroupMembershipConfig(
            groups=groups,
            user=user,
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
    @jsii.member(jsii_name="groupsInput")
    def groups_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "groupsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userInput")
    def user_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="groups")
    def groups(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "groups"))

    @groups.setter
    def groups(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "groups", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="user")
    def user(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "user"))

    @user.setter
    def user(self, value: builtins.str) -> None:
        jsii.set(self, "user", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.IamUserGroupMembershipConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "groups": "groups",
        "user": "user",
    },
)
class IamUserGroupMembershipConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        groups: typing.Sequence[builtins.str],
        user: builtins.str,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_group_membership#groups IamUserGroupMembership#groups}.
        :param user: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_group_membership#user IamUserGroupMembership#user}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "groups": groups,
            "user": user,
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
    def groups(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_group_membership#groups IamUserGroupMembership#groups}.'''
        result = self._values.get("groups")
        assert result is not None, "Required property 'groups' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def user(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_group_membership#user IamUserGroupMembership#user}.'''
        result = self._values.get("user")
        assert result is not None, "Required property 'user' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IamUserGroupMembershipConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IamUserLoginProfile(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.IamUserLoginProfile",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iam_user_login_profile aws_iam_user_login_profile}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        pgp_key: builtins.str,
        user: builtins.str,
        password_length: typing.Optional[jsii.Number] = None,
        password_reset_required: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iam_user_login_profile aws_iam_user_login_profile} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param pgp_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_login_profile#pgp_key IamUserLoginProfile#pgp_key}.
        :param user: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_login_profile#user IamUserLoginProfile#user}.
        :param password_length: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_login_profile#password_length IamUserLoginProfile#password_length}.
        :param password_reset_required: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_login_profile#password_reset_required IamUserLoginProfile#password_reset_required}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IamUserLoginProfileConfig(
            pgp_key=pgp_key,
            user=user,
            password_length=password_length,
            password_reset_required=password_reset_required,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetPasswordLength")
    def reset_password_length(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordLength", []))

    @jsii.member(jsii_name="resetPasswordResetRequired")
    def reset_password_reset_required(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordResetRequired", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptedPassword")
    def encrypted_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptedPassword"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyFingerprint")
    def key_fingerprint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyFingerprint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwordLengthInput")
    def password_length_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "passwordLengthInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwordResetRequiredInput")
    def password_reset_required_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "passwordResetRequiredInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pgpKeyInput")
    def pgp_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pgpKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userInput")
    def user_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwordLength")
    def password_length(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "passwordLength"))

    @password_length.setter
    def password_length(self, value: jsii.Number) -> None:
        jsii.set(self, "passwordLength", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwordResetRequired")
    def password_reset_required(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "passwordResetRequired"))

    @password_reset_required.setter
    def password_reset_required(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "passwordResetRequired", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pgpKey")
    def pgp_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pgpKey"))

    @pgp_key.setter
    def pgp_key(self, value: builtins.str) -> None:
        jsii.set(self, "pgpKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="user")
    def user(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "user"))

    @user.setter
    def user(self, value: builtins.str) -> None:
        jsii.set(self, "user", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.IamUserLoginProfileConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "pgp_key": "pgpKey",
        "user": "user",
        "password_length": "passwordLength",
        "password_reset_required": "passwordResetRequired",
    },
)
class IamUserLoginProfileConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        pgp_key: builtins.str,
        user: builtins.str,
        password_length: typing.Optional[jsii.Number] = None,
        password_reset_required: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param pgp_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_login_profile#pgp_key IamUserLoginProfile#pgp_key}.
        :param user: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_login_profile#user IamUserLoginProfile#user}.
        :param password_length: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_login_profile#password_length IamUserLoginProfile#password_length}.
        :param password_reset_required: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_login_profile#password_reset_required IamUserLoginProfile#password_reset_required}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "pgp_key": pgp_key,
            "user": user,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if password_length is not None:
            self._values["password_length"] = password_length
        if password_reset_required is not None:
            self._values["password_reset_required"] = password_reset_required

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
    def pgp_key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_login_profile#pgp_key IamUserLoginProfile#pgp_key}.'''
        result = self._values.get("pgp_key")
        assert result is not None, "Required property 'pgp_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_login_profile#user IamUserLoginProfile#user}.'''
        result = self._values.get("user")
        assert result is not None, "Required property 'user' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def password_length(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_login_profile#password_length IamUserLoginProfile#password_length}.'''
        result = self._values.get("password_length")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def password_reset_required(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_login_profile#password_reset_required IamUserLoginProfile#password_reset_required}.'''
        result = self._values.get("password_reset_required")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IamUserLoginProfileConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IamUserPolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.IamUserPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iam_user_policy aws_iam_user_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        policy: builtins.str,
        user: builtins.str,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iam_user_policy aws_iam_user_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_policy#policy IamUserPolicy#policy}.
        :param user: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_policy#user IamUserPolicy#user}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_policy#name IamUserPolicy#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_policy#name_prefix IamUserPolicy#name_prefix}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IamUserPolicyConfig(
            policy=policy,
            user=user,
            name=name,
            name_prefix=name_prefix,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNamePrefix")
    def reset_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamePrefix", []))

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
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefixInput")
    def name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namePrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyInput")
    def policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userInput")
    def user_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefix")
    def name_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namePrefix"))

    @name_prefix.setter
    def name_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "namePrefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: builtins.str) -> None:
        jsii.set(self, "policy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="user")
    def user(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "user"))

    @user.setter
    def user(self, value: builtins.str) -> None:
        jsii.set(self, "user", value)


class IamUserPolicyAttachment(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.IamUserPolicyAttachment",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iam_user_policy_attachment aws_iam_user_policy_attachment}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        policy_arn: builtins.str,
        user: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iam_user_policy_attachment aws_iam_user_policy_attachment} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param policy_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_policy_attachment#policy_arn IamUserPolicyAttachment#policy_arn}.
        :param user: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_policy_attachment#user IamUserPolicyAttachment#user}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IamUserPolicyAttachmentConfig(
            policy_arn=policy_arn,
            user=user,
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
    @jsii.member(jsii_name="policyArnInput")
    def policy_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userInput")
    def user_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyArn")
    def policy_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyArn"))

    @policy_arn.setter
    def policy_arn(self, value: builtins.str) -> None:
        jsii.set(self, "policyArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="user")
    def user(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "user"))

    @user.setter
    def user(self, value: builtins.str) -> None:
        jsii.set(self, "user", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.IamUserPolicyAttachmentConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "policy_arn": "policyArn",
        "user": "user",
    },
)
class IamUserPolicyAttachmentConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        policy_arn: builtins.str,
        user: builtins.str,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param policy_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_policy_attachment#policy_arn IamUserPolicyAttachment#policy_arn}.
        :param user: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_policy_attachment#user IamUserPolicyAttachment#user}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "policy_arn": policy_arn,
            "user": user,
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
    def policy_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_policy_attachment#policy_arn IamUserPolicyAttachment#policy_arn}.'''
        result = self._values.get("policy_arn")
        assert result is not None, "Required property 'policy_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_policy_attachment#user IamUserPolicyAttachment#user}.'''
        result = self._values.get("user")
        assert result is not None, "Required property 'user' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IamUserPolicyAttachmentConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.IamUserPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "policy": "policy",
        "user": "user",
        "name": "name",
        "name_prefix": "namePrefix",
    },
)
class IamUserPolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        policy: builtins.str,
        user: builtins.str,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_policy#policy IamUserPolicy#policy}.
        :param user: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_policy#user IamUserPolicy#user}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_policy#name IamUserPolicy#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_policy#name_prefix IamUserPolicy#name_prefix}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "policy": policy,
            "user": user,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if name is not None:
            self._values["name"] = name
        if name_prefix is not None:
            self._values["name_prefix"] = name_prefix

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
    def policy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_policy#policy IamUserPolicy#policy}.'''
        result = self._values.get("policy")
        assert result is not None, "Required property 'policy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_policy#user IamUserPolicy#user}.'''
        result = self._values.get("user")
        assert result is not None, "Required property 'user' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_policy#name IamUserPolicy#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_policy#name_prefix IamUserPolicy#name_prefix}.'''
        result = self._values.get("name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IamUserPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IamUserSshKey(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.iam.IamUserSshKey",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/iam_user_ssh_key aws_iam_user_ssh_key}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        encoding: builtins.str,
        public_key: builtins.str,
        username: builtins.str,
        status: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/iam_user_ssh_key aws_iam_user_ssh_key} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param encoding: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_ssh_key#encoding IamUserSshKey#encoding}.
        :param public_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_ssh_key#public_key IamUserSshKey#public_key}.
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_ssh_key#username IamUserSshKey#username}.
        :param status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_ssh_key#status IamUserSshKey#status}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IamUserSshKeyConfig(
            encoding=encoding,
            public_key=public_key,
            username=username,
            status=status,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetStatus")
    def reset_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatus", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fingerprint")
    def fingerprint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fingerprint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sshPublicKeyId")
    def ssh_public_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sshPublicKeyId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encodingInput")
    def encoding_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encodingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicKeyInput")
    def public_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "publicKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statusInput")
    def status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encoding")
    def encoding(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encoding"))

    @encoding.setter
    def encoding(self, value: builtins.str) -> None:
        jsii.set(self, "encoding", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicKey")
    def public_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicKey"))

    @public_key.setter
    def public_key(self, value: builtins.str) -> None:
        jsii.set(self, "publicKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @status.setter
    def status(self, value: builtins.str) -> None:
        jsii.set(self, "status", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        jsii.set(self, "username", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.iam.IamUserSshKeyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "encoding": "encoding",
        "public_key": "publicKey",
        "username": "username",
        "status": "status",
    },
)
class IamUserSshKeyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        encoding: builtins.str,
        public_key: builtins.str,
        username: builtins.str,
        status: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Identity and Access Management.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param encoding: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_ssh_key#encoding IamUserSshKey#encoding}.
        :param public_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_ssh_key#public_key IamUserSshKey#public_key}.
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_ssh_key#username IamUserSshKey#username}.
        :param status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_ssh_key#status IamUserSshKey#status}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "encoding": encoding,
            "public_key": public_key,
            "username": username,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if status is not None:
            self._values["status"] = status

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
    def encoding(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_ssh_key#encoding IamUserSshKey#encoding}.'''
        result = self._values.get("encoding")
        assert result is not None, "Required property 'encoding' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def public_key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_ssh_key#public_key IamUserSshKey#public_key}.'''
        result = self._values.get("public_key")
        assert result is not None, "Required property 'public_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_ssh_key#username IamUserSshKey#username}.'''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def status(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/iam_user_ssh_key#status IamUserSshKey#status}.'''
        result = self._values.get("status")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IamUserSshKeyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataAwsIamAccountAlias",
    "DataAwsIamAccountAliasConfig",
    "DataAwsIamGroup",
    "DataAwsIamGroupConfig",
    "DataAwsIamGroupUsers",
    "DataAwsIamInstanceProfile",
    "DataAwsIamInstanceProfileConfig",
    "DataAwsIamPolicy",
    "DataAwsIamPolicyConfig",
    "DataAwsIamPolicyDocument",
    "DataAwsIamPolicyDocumentConfig",
    "DataAwsIamPolicyDocumentStatement",
    "DataAwsIamPolicyDocumentStatementCondition",
    "DataAwsIamPolicyDocumentStatementNotPrincipals",
    "DataAwsIamPolicyDocumentStatementPrincipals",
    "DataAwsIamRole",
    "DataAwsIamRoleConfig",
    "DataAwsIamRoles",
    "DataAwsIamRolesConfig",
    "DataAwsIamServerCertificate",
    "DataAwsIamServerCertificateConfig",
    "DataAwsIamSessionContext",
    "DataAwsIamSessionContextConfig",
    "DataAwsIamUser",
    "DataAwsIamUserConfig",
    "DataAwsIamUserSshKey",
    "DataAwsIamUserSshKeyConfig",
    "DataAwsIamUsers",
    "DataAwsIamUsersConfig",
    "IamAccessKey",
    "IamAccessKeyConfig",
    "IamAccountAlias",
    "IamAccountAliasConfig",
    "IamAccountPasswordPolicy",
    "IamAccountPasswordPolicyConfig",
    "IamGroup",
    "IamGroupConfig",
    "IamGroupMembership",
    "IamGroupMembershipConfig",
    "IamGroupPolicy",
    "IamGroupPolicyAttachment",
    "IamGroupPolicyAttachmentConfig",
    "IamGroupPolicyConfig",
    "IamInstanceProfile",
    "IamInstanceProfileConfig",
    "IamOpenidConnectProvider",
    "IamOpenidConnectProviderConfig",
    "IamPolicy",
    "IamPolicyAttachment",
    "IamPolicyAttachmentConfig",
    "IamPolicyConfig",
    "IamRole",
    "IamRoleConfig",
    "IamRoleInlinePolicy",
    "IamRolePolicy",
    "IamRolePolicyAttachment",
    "IamRolePolicyAttachmentConfig",
    "IamRolePolicyConfig",
    "IamSamlProvider",
    "IamSamlProviderConfig",
    "IamServerCertificate",
    "IamServerCertificateConfig",
    "IamServiceLinkedRole",
    "IamServiceLinkedRoleConfig",
    "IamUser",
    "IamUserConfig",
    "IamUserGroupMembership",
    "IamUserGroupMembershipConfig",
    "IamUserLoginProfile",
    "IamUserLoginProfileConfig",
    "IamUserPolicy",
    "IamUserPolicyAttachment",
    "IamUserPolicyAttachmentConfig",
    "IamUserPolicyConfig",
    "IamUserSshKey",
    "IamUserSshKeyConfig",
]

publication.publish()
