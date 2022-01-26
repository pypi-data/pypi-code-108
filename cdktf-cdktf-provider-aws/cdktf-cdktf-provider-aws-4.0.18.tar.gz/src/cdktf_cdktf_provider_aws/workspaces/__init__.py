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


class DataAwsWorkspacesBundle(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.workspaces.DataAwsWorkspacesBundle",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/workspaces_bundle aws_workspaces_bundle}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        bundle_id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        owner: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/workspaces_bundle aws_workspaces_bundle} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param bundle_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/workspaces_bundle#bundle_id DataAwsWorkspacesBundle#bundle_id}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/workspaces_bundle#name DataAwsWorkspacesBundle#name}.
        :param owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/workspaces_bundle#owner DataAwsWorkspacesBundle#owner}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsWorkspacesBundleConfig(
            bundle_id=bundle_id,
            name=name,
            owner=owner,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="computeType")
    def compute_type(self, index: builtins.str) -> "DataAwsWorkspacesBundleComputeType":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsWorkspacesBundleComputeType", jsii.invoke(self, "computeType", [index]))

    @jsii.member(jsii_name="resetBundleId")
    def reset_bundle_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBundleId", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetOwner")
    def reset_owner(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOwner", []))

    @jsii.member(jsii_name="rootStorage")
    def root_storage(self, index: builtins.str) -> "DataAwsWorkspacesBundleRootStorage":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsWorkspacesBundleRootStorage", jsii.invoke(self, "rootStorage", [index]))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="userStorage")
    def user_storage(self, index: builtins.str) -> "DataAwsWorkspacesBundleUserStorage":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsWorkspacesBundleUserStorage", jsii.invoke(self, "userStorage", [index]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bundleIdInput")
    def bundle_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bundleIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerInput")
    def owner_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ownerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bundleId")
    def bundle_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bundleId"))

    @bundle_id.setter
    def bundle_id(self, value: builtins.str) -> None:
        jsii.set(self, "bundleId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @owner.setter
    def owner(self, value: builtins.str) -> None:
        jsii.set(self, "owner", value)


class DataAwsWorkspacesBundleComputeType(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.workspaces.DataAwsWorkspacesBundleComputeType",
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


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.workspaces.DataAwsWorkspacesBundleConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "bundle_id": "bundleId",
        "name": "name",
        "owner": "owner",
    },
)
class DataAwsWorkspacesBundleConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        bundle_id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        owner: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS WorkSpaces.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param bundle_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/workspaces_bundle#bundle_id DataAwsWorkspacesBundle#bundle_id}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/workspaces_bundle#name DataAwsWorkspacesBundle#name}.
        :param owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/workspaces_bundle#owner DataAwsWorkspacesBundle#owner}.
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
        if bundle_id is not None:
            self._values["bundle_id"] = bundle_id
        if name is not None:
            self._values["name"] = name
        if owner is not None:
            self._values["owner"] = owner

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
    def bundle_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/workspaces_bundle#bundle_id DataAwsWorkspacesBundle#bundle_id}.'''
        result = self._values.get("bundle_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/workspaces_bundle#name DataAwsWorkspacesBundle#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def owner(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/workspaces_bundle#owner DataAwsWorkspacesBundle#owner}.'''
        result = self._values.get("owner")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsWorkspacesBundleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsWorkspacesBundleRootStorage(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.workspaces.DataAwsWorkspacesBundleRootStorage",
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
    @jsii.member(jsii_name="capacity")
    def capacity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "capacity"))


class DataAwsWorkspacesBundleUserStorage(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.workspaces.DataAwsWorkspacesBundleUserStorage",
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
    @jsii.member(jsii_name="capacity")
    def capacity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "capacity"))


class DataAwsWorkspacesDirectory(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.workspaces.DataAwsWorkspacesDirectory",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/workspaces_directory aws_workspaces_directory}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        directory_id: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/workspaces_directory aws_workspaces_directory} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param directory_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/workspaces_directory#directory_id DataAwsWorkspacesDirectory#directory_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/workspaces_directory#tags DataAwsWorkspacesDirectory#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsWorkspacesDirectoryConfig(
            directory_id=directory_id,
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

    @jsii.member(jsii_name="selfServicePermissions")
    def self_service_permissions(
        self,
        index: builtins.str,
    ) -> "DataAwsWorkspacesDirectorySelfServicePermissions":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsWorkspacesDirectorySelfServicePermissions", jsii.invoke(self, "selfServicePermissions", [index]))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="workspaceAccessProperties")
    def workspace_access_properties(
        self,
        index: builtins.str,
    ) -> "DataAwsWorkspacesDirectoryWorkspaceAccessProperties":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsWorkspacesDirectoryWorkspaceAccessProperties", jsii.invoke(self, "workspaceAccessProperties", [index]))

    @jsii.member(jsii_name="workspaceCreationProperties")
    def workspace_creation_properties(
        self,
        index: builtins.str,
    ) -> "DataAwsWorkspacesDirectoryWorkspaceCreationProperties":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsWorkspacesDirectoryWorkspaceCreationProperties", jsii.invoke(self, "workspaceCreationProperties", [index]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alias")
    def alias(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alias"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customerUserName")
    def customer_user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customerUserName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="directoryName")
    def directory_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "directoryName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="directoryType")
    def directory_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "directoryType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsIpAddresses")
    def dns_ip_addresses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dnsIpAddresses"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamRoleId")
    def iam_role_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "iamRoleId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipGroupIds")
    def ip_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ipGroupIds"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="registrationCode")
    def registration_code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "registrationCode"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "subnetIds"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workspaceSecurityGroupId")
    def workspace_security_group_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workspaceSecurityGroupId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="directoryIdInput")
    def directory_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "directoryIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="directoryId")
    def directory_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "directoryId"))

    @directory_id.setter
    def directory_id(self, value: builtins.str) -> None:
        jsii.set(self, "directoryId", value)

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
    jsii_type="@cdktf/provider-aws.workspaces.DataAwsWorkspacesDirectoryConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "directory_id": "directoryId",
        "tags": "tags",
    },
)
class DataAwsWorkspacesDirectoryConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        directory_id: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS WorkSpaces.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param directory_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/workspaces_directory#directory_id DataAwsWorkspacesDirectory#directory_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/workspaces_directory#tags DataAwsWorkspacesDirectory#tags}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "directory_id": directory_id,
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
    def directory_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/workspaces_directory#directory_id DataAwsWorkspacesDirectory#directory_id}.'''
        result = self._values.get("directory_id")
        assert result is not None, "Required property 'directory_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/workspaces_directory#tags DataAwsWorkspacesDirectory#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsWorkspacesDirectoryConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsWorkspacesDirectorySelfServicePermissions(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.workspaces.DataAwsWorkspacesDirectorySelfServicePermissions",
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
    @jsii.member(jsii_name="changeComputeType")
    def change_compute_type(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "changeComputeType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="increaseVolumeSize")
    def increase_volume_size(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "increaseVolumeSize"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rebuildWorkspace")
    def rebuild_workspace(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "rebuildWorkspace"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restartWorkspace")
    def restart_workspace(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "restartWorkspace"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="switchRunningMode")
    def switch_running_mode(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "switchRunningMode"))


class DataAwsWorkspacesDirectoryWorkspaceAccessProperties(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.workspaces.DataAwsWorkspacesDirectoryWorkspaceAccessProperties",
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
    @jsii.member(jsii_name="deviceTypeAndroid")
    def device_type_android(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deviceTypeAndroid"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceTypeChromeos")
    def device_type_chromeos(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deviceTypeChromeos"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceTypeIos")
    def device_type_ios(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deviceTypeIos"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceTypeLinux")
    def device_type_linux(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deviceTypeLinux"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceTypeOsx")
    def device_type_osx(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deviceTypeOsx"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceTypeWeb")
    def device_type_web(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deviceTypeWeb"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceTypeWindows")
    def device_type_windows(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deviceTypeWindows"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceTypeZeroclient")
    def device_type_zeroclient(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deviceTypeZeroclient"))


class DataAwsWorkspacesDirectoryWorkspaceCreationProperties(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.workspaces.DataAwsWorkspacesDirectoryWorkspaceCreationProperties",
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
    @jsii.member(jsii_name="customSecurityGroupId")
    def custom_security_group_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customSecurityGroupId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultOu")
    def default_ou(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultOu"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableInternetAccess")
    def enable_internet_access(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "enableInternetAccess"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableMaintenanceMode")
    def enable_maintenance_mode(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "enableMaintenanceMode"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userEnabledAsLocalAdministrator")
    def user_enabled_as_local_administrator(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "userEnabledAsLocalAdministrator"))


class DataAwsWorkspacesImage(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.workspaces.DataAwsWorkspacesImage",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/workspaces_image aws_workspaces_image}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        image_id: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/workspaces_image aws_workspaces_image} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param image_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/workspaces_image#image_id DataAwsWorkspacesImage#image_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsWorkspacesImageConfig(
            image_id=image_id,
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
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="operatingSystemType")
    def operating_system_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operatingSystemType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requiredTenancy")
    def required_tenancy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "requiredTenancy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageIdInput")
    def image_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imageIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageId")
    def image_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imageId"))

    @image_id.setter
    def image_id(self, value: builtins.str) -> None:
        jsii.set(self, "imageId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.workspaces.DataAwsWorkspacesImageConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "image_id": "imageId",
    },
)
class DataAwsWorkspacesImageConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        image_id: builtins.str,
    ) -> None:
        '''AWS WorkSpaces.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param image_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/workspaces_image#image_id DataAwsWorkspacesImage#image_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "image_id": image_id,
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
    def image_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/workspaces_image#image_id DataAwsWorkspacesImage#image_id}.'''
        result = self._values.get("image_id")
        assert result is not None, "Required property 'image_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsWorkspacesImageConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsWorkspacesWorkspace(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.workspaces.DataAwsWorkspacesWorkspace",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/workspaces_workspace aws_workspaces_workspace}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        directory_id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        user_name: typing.Optional[builtins.str] = None,
        workspace_id: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/workspaces_workspace aws_workspaces_workspace} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param directory_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/workspaces_workspace#directory_id DataAwsWorkspacesWorkspace#directory_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/workspaces_workspace#tags DataAwsWorkspacesWorkspace#tags}.
        :param user_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/workspaces_workspace#user_name DataAwsWorkspacesWorkspace#user_name}.
        :param workspace_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/workspaces_workspace#workspace_id DataAwsWorkspacesWorkspace#workspace_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsWorkspacesWorkspaceConfig(
            directory_id=directory_id,
            tags=tags,
            user_name=user_name,
            workspace_id=workspace_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDirectoryId")
    def reset_directory_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDirectoryId", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetUserName")
    def reset_user_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserName", []))

    @jsii.member(jsii_name="resetWorkspaceId")
    def reset_workspace_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkspaceId", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="workspaceProperties")
    def workspace_properties(
        self,
        index: builtins.str,
    ) -> "DataAwsWorkspacesWorkspaceWorkspaceProperties":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsWorkspacesWorkspaceWorkspaceProperties", jsii.invoke(self, "workspaceProperties", [index]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bundleId")
    def bundle_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bundleId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computerName")
    def computer_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "computerName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipAddress")
    def ip_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipAddress"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rootVolumeEncryptionEnabled")
    def root_volume_encryption_enabled(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "rootVolumeEncryptionEnabled"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userVolumeEncryptionEnabled")
    def user_volume_encryption_enabled(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "userVolumeEncryptionEnabled"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeEncryptionKey")
    def volume_encryption_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "volumeEncryptionKey"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="directoryIdInput")
    def directory_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "directoryIdInput"))

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
    @jsii.member(jsii_name="workspaceIdInput")
    def workspace_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workspaceIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="directoryId")
    def directory_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "directoryId"))

    @directory_id.setter
    def directory_id(self, value: builtins.str) -> None:
        jsii.set(self, "directoryId", value)

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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workspaceId")
    def workspace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workspaceId"))

    @workspace_id.setter
    def workspace_id(self, value: builtins.str) -> None:
        jsii.set(self, "workspaceId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.workspaces.DataAwsWorkspacesWorkspaceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "directory_id": "directoryId",
        "tags": "tags",
        "user_name": "userName",
        "workspace_id": "workspaceId",
    },
)
class DataAwsWorkspacesWorkspaceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        directory_id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        user_name: typing.Optional[builtins.str] = None,
        workspace_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS WorkSpaces.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param directory_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/workspaces_workspace#directory_id DataAwsWorkspacesWorkspace#directory_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/workspaces_workspace#tags DataAwsWorkspacesWorkspace#tags}.
        :param user_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/workspaces_workspace#user_name DataAwsWorkspacesWorkspace#user_name}.
        :param workspace_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/workspaces_workspace#workspace_id DataAwsWorkspacesWorkspace#workspace_id}.
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
        if directory_id is not None:
            self._values["directory_id"] = directory_id
        if tags is not None:
            self._values["tags"] = tags
        if user_name is not None:
            self._values["user_name"] = user_name
        if workspace_id is not None:
            self._values["workspace_id"] = workspace_id

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
    def directory_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/workspaces_workspace#directory_id DataAwsWorkspacesWorkspace#directory_id}.'''
        result = self._values.get("directory_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/workspaces_workspace#tags DataAwsWorkspacesWorkspace#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def user_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/workspaces_workspace#user_name DataAwsWorkspacesWorkspace#user_name}.'''
        result = self._values.get("user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workspace_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/workspaces_workspace#workspace_id DataAwsWorkspacesWorkspace#workspace_id}.'''
        result = self._values.get("workspace_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsWorkspacesWorkspaceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsWorkspacesWorkspaceWorkspaceProperties(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.workspaces.DataAwsWorkspacesWorkspaceWorkspaceProperties",
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
    @jsii.member(jsii_name="computeTypeName")
    def compute_type_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "computeTypeName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rootVolumeSizeGib")
    def root_volume_size_gib(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "rootVolumeSizeGib"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runningMode")
    def running_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runningMode"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runningModeAutoStopTimeoutInMinutes")
    def running_mode_auto_stop_timeout_in_minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "runningModeAutoStopTimeoutInMinutes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userVolumeSizeGib")
    def user_volume_size_gib(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "userVolumeSizeGib"))


class WorkspacesDirectory(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.workspaces.WorkspacesDirectory",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory aws_workspaces_directory}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        directory_id: builtins.str,
        ip_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        self_service_permissions: typing.Optional["WorkspacesDirectorySelfServicePermissions"] = None,
        subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        workspace_access_properties: typing.Optional["WorkspacesDirectoryWorkspaceAccessProperties"] = None,
        workspace_creation_properties: typing.Optional["WorkspacesDirectoryWorkspaceCreationProperties"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory aws_workspaces_directory} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param directory_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#directory_id WorkspacesDirectory#directory_id}.
        :param ip_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#ip_group_ids WorkspacesDirectory#ip_group_ids}.
        :param self_service_permissions: self_service_permissions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#self_service_permissions WorkspacesDirectory#self_service_permissions}
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#subnet_ids WorkspacesDirectory#subnet_ids}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#tags WorkspacesDirectory#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#tags_all WorkspacesDirectory#tags_all}.
        :param workspace_access_properties: workspace_access_properties block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#workspace_access_properties WorkspacesDirectory#workspace_access_properties}
        :param workspace_creation_properties: workspace_creation_properties block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#workspace_creation_properties WorkspacesDirectory#workspace_creation_properties}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = WorkspacesDirectoryConfig(
            directory_id=directory_id,
            ip_group_ids=ip_group_ids,
            self_service_permissions=self_service_permissions,
            subnet_ids=subnet_ids,
            tags=tags,
            tags_all=tags_all,
            workspace_access_properties=workspace_access_properties,
            workspace_creation_properties=workspace_creation_properties,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putSelfServicePermissions")
    def put_self_service_permissions(
        self,
        *,
        change_compute_type: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        increase_volume_size: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        rebuild_workspace: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        restart_workspace: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        switch_running_mode: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param change_compute_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#change_compute_type WorkspacesDirectory#change_compute_type}.
        :param increase_volume_size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#increase_volume_size WorkspacesDirectory#increase_volume_size}.
        :param rebuild_workspace: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#rebuild_workspace WorkspacesDirectory#rebuild_workspace}.
        :param restart_workspace: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#restart_workspace WorkspacesDirectory#restart_workspace}.
        :param switch_running_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#switch_running_mode WorkspacesDirectory#switch_running_mode}.
        '''
        value = WorkspacesDirectorySelfServicePermissions(
            change_compute_type=change_compute_type,
            increase_volume_size=increase_volume_size,
            rebuild_workspace=rebuild_workspace,
            restart_workspace=restart_workspace,
            switch_running_mode=switch_running_mode,
        )

        return typing.cast(None, jsii.invoke(self, "putSelfServicePermissions", [value]))

    @jsii.member(jsii_name="putWorkspaceAccessProperties")
    def put_workspace_access_properties(
        self,
        *,
        device_type_android: typing.Optional[builtins.str] = None,
        device_type_chromeos: typing.Optional[builtins.str] = None,
        device_type_ios: typing.Optional[builtins.str] = None,
        device_type_linux: typing.Optional[builtins.str] = None,
        device_type_osx: typing.Optional[builtins.str] = None,
        device_type_web: typing.Optional[builtins.str] = None,
        device_type_windows: typing.Optional[builtins.str] = None,
        device_type_zeroclient: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param device_type_android: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#device_type_android WorkspacesDirectory#device_type_android}.
        :param device_type_chromeos: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#device_type_chromeos WorkspacesDirectory#device_type_chromeos}.
        :param device_type_ios: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#device_type_ios WorkspacesDirectory#device_type_ios}.
        :param device_type_linux: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#device_type_linux WorkspacesDirectory#device_type_linux}.
        :param device_type_osx: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#device_type_osx WorkspacesDirectory#device_type_osx}.
        :param device_type_web: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#device_type_web WorkspacesDirectory#device_type_web}.
        :param device_type_windows: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#device_type_windows WorkspacesDirectory#device_type_windows}.
        :param device_type_zeroclient: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#device_type_zeroclient WorkspacesDirectory#device_type_zeroclient}.
        '''
        value = WorkspacesDirectoryWorkspaceAccessProperties(
            device_type_android=device_type_android,
            device_type_chromeos=device_type_chromeos,
            device_type_ios=device_type_ios,
            device_type_linux=device_type_linux,
            device_type_osx=device_type_osx,
            device_type_web=device_type_web,
            device_type_windows=device_type_windows,
            device_type_zeroclient=device_type_zeroclient,
        )

        return typing.cast(None, jsii.invoke(self, "putWorkspaceAccessProperties", [value]))

    @jsii.member(jsii_name="putWorkspaceCreationProperties")
    def put_workspace_creation_properties(
        self,
        *,
        custom_security_group_id: typing.Optional[builtins.str] = None,
        default_ou: typing.Optional[builtins.str] = None,
        enable_internet_access: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_maintenance_mode: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        user_enabled_as_local_administrator: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param custom_security_group_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#custom_security_group_id WorkspacesDirectory#custom_security_group_id}.
        :param default_ou: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#default_ou WorkspacesDirectory#default_ou}.
        :param enable_internet_access: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#enable_internet_access WorkspacesDirectory#enable_internet_access}.
        :param enable_maintenance_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#enable_maintenance_mode WorkspacesDirectory#enable_maintenance_mode}.
        :param user_enabled_as_local_administrator: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#user_enabled_as_local_administrator WorkspacesDirectory#user_enabled_as_local_administrator}.
        '''
        value = WorkspacesDirectoryWorkspaceCreationProperties(
            custom_security_group_id=custom_security_group_id,
            default_ou=default_ou,
            enable_internet_access=enable_internet_access,
            enable_maintenance_mode=enable_maintenance_mode,
            user_enabled_as_local_administrator=user_enabled_as_local_administrator,
        )

        return typing.cast(None, jsii.invoke(self, "putWorkspaceCreationProperties", [value]))

    @jsii.member(jsii_name="resetIpGroupIds")
    def reset_ip_group_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpGroupIds", []))

    @jsii.member(jsii_name="resetSelfServicePermissions")
    def reset_self_service_permissions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSelfServicePermissions", []))

    @jsii.member(jsii_name="resetSubnetIds")
    def reset_subnet_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubnetIds", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetWorkspaceAccessProperties")
    def reset_workspace_access_properties(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkspaceAccessProperties", []))

    @jsii.member(jsii_name="resetWorkspaceCreationProperties")
    def reset_workspace_creation_properties(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkspaceCreationProperties", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alias")
    def alias(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alias"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customerUserName")
    def customer_user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customerUserName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="directoryName")
    def directory_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "directoryName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="directoryType")
    def directory_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "directoryType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsIpAddresses")
    def dns_ip_addresses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dnsIpAddresses"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamRoleId")
    def iam_role_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "iamRoleId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="registrationCode")
    def registration_code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "registrationCode"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="selfServicePermissions")
    def self_service_permissions(
        self,
    ) -> "WorkspacesDirectorySelfServicePermissionsOutputReference":
        return typing.cast("WorkspacesDirectorySelfServicePermissionsOutputReference", jsii.get(self, "selfServicePermissions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workspaceAccessProperties")
    def workspace_access_properties(
        self,
    ) -> "WorkspacesDirectoryWorkspaceAccessPropertiesOutputReference":
        return typing.cast("WorkspacesDirectoryWorkspaceAccessPropertiesOutputReference", jsii.get(self, "workspaceAccessProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workspaceCreationProperties")
    def workspace_creation_properties(
        self,
    ) -> "WorkspacesDirectoryWorkspaceCreationPropertiesOutputReference":
        return typing.cast("WorkspacesDirectoryWorkspaceCreationPropertiesOutputReference", jsii.get(self, "workspaceCreationProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workspaceSecurityGroupId")
    def workspace_security_group_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workspaceSecurityGroupId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="directoryIdInput")
    def directory_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "directoryIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipGroupIdsInput")
    def ip_group_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "ipGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="selfServicePermissionsInput")
    def self_service_permissions_input(
        self,
    ) -> typing.Optional["WorkspacesDirectorySelfServicePermissions"]:
        return typing.cast(typing.Optional["WorkspacesDirectorySelfServicePermissions"], jsii.get(self, "selfServicePermissionsInput"))

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
    @jsii.member(jsii_name="workspaceAccessPropertiesInput")
    def workspace_access_properties_input(
        self,
    ) -> typing.Optional["WorkspacesDirectoryWorkspaceAccessProperties"]:
        return typing.cast(typing.Optional["WorkspacesDirectoryWorkspaceAccessProperties"], jsii.get(self, "workspaceAccessPropertiesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workspaceCreationPropertiesInput")
    def workspace_creation_properties_input(
        self,
    ) -> typing.Optional["WorkspacesDirectoryWorkspaceCreationProperties"]:
        return typing.cast(typing.Optional["WorkspacesDirectoryWorkspaceCreationProperties"], jsii.get(self, "workspaceCreationPropertiesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="directoryId")
    def directory_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "directoryId"))

    @directory_id.setter
    def directory_id(self, value: builtins.str) -> None:
        jsii.set(self, "directoryId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipGroupIds")
    def ip_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ipGroupIds"))

    @ip_group_ids.setter
    def ip_group_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "ipGroupIds", value)

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
    jsii_type="@cdktf/provider-aws.workspaces.WorkspacesDirectoryConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "directory_id": "directoryId",
        "ip_group_ids": "ipGroupIds",
        "self_service_permissions": "selfServicePermissions",
        "subnet_ids": "subnetIds",
        "tags": "tags",
        "tags_all": "tagsAll",
        "workspace_access_properties": "workspaceAccessProperties",
        "workspace_creation_properties": "workspaceCreationProperties",
    },
)
class WorkspacesDirectoryConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        directory_id: builtins.str,
        ip_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        self_service_permissions: typing.Optional["WorkspacesDirectorySelfServicePermissions"] = None,
        subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        workspace_access_properties: typing.Optional["WorkspacesDirectoryWorkspaceAccessProperties"] = None,
        workspace_creation_properties: typing.Optional["WorkspacesDirectoryWorkspaceCreationProperties"] = None,
    ) -> None:
        '''AWS WorkSpaces.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param directory_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#directory_id WorkspacesDirectory#directory_id}.
        :param ip_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#ip_group_ids WorkspacesDirectory#ip_group_ids}.
        :param self_service_permissions: self_service_permissions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#self_service_permissions WorkspacesDirectory#self_service_permissions}
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#subnet_ids WorkspacesDirectory#subnet_ids}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#tags WorkspacesDirectory#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#tags_all WorkspacesDirectory#tags_all}.
        :param workspace_access_properties: workspace_access_properties block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#workspace_access_properties WorkspacesDirectory#workspace_access_properties}
        :param workspace_creation_properties: workspace_creation_properties block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#workspace_creation_properties WorkspacesDirectory#workspace_creation_properties}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(self_service_permissions, dict):
            self_service_permissions = WorkspacesDirectorySelfServicePermissions(**self_service_permissions)
        if isinstance(workspace_access_properties, dict):
            workspace_access_properties = WorkspacesDirectoryWorkspaceAccessProperties(**workspace_access_properties)
        if isinstance(workspace_creation_properties, dict):
            workspace_creation_properties = WorkspacesDirectoryWorkspaceCreationProperties(**workspace_creation_properties)
        self._values: typing.Dict[str, typing.Any] = {
            "directory_id": directory_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if ip_group_ids is not None:
            self._values["ip_group_ids"] = ip_group_ids
        if self_service_permissions is not None:
            self._values["self_service_permissions"] = self_service_permissions
        if subnet_ids is not None:
            self._values["subnet_ids"] = subnet_ids
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if workspace_access_properties is not None:
            self._values["workspace_access_properties"] = workspace_access_properties
        if workspace_creation_properties is not None:
            self._values["workspace_creation_properties"] = workspace_creation_properties

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
    def directory_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#directory_id WorkspacesDirectory#directory_id}.'''
        result = self._values.get("directory_id")
        assert result is not None, "Required property 'directory_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ip_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#ip_group_ids WorkspacesDirectory#ip_group_ids}.'''
        result = self._values.get("ip_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def self_service_permissions(
        self,
    ) -> typing.Optional["WorkspacesDirectorySelfServicePermissions"]:
        '''self_service_permissions block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#self_service_permissions WorkspacesDirectory#self_service_permissions}
        '''
        result = self._values.get("self_service_permissions")
        return typing.cast(typing.Optional["WorkspacesDirectorySelfServicePermissions"], result)

    @builtins.property
    def subnet_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#subnet_ids WorkspacesDirectory#subnet_ids}.'''
        result = self._values.get("subnet_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#tags WorkspacesDirectory#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#tags_all WorkspacesDirectory#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def workspace_access_properties(
        self,
    ) -> typing.Optional["WorkspacesDirectoryWorkspaceAccessProperties"]:
        '''workspace_access_properties block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#workspace_access_properties WorkspacesDirectory#workspace_access_properties}
        '''
        result = self._values.get("workspace_access_properties")
        return typing.cast(typing.Optional["WorkspacesDirectoryWorkspaceAccessProperties"], result)

    @builtins.property
    def workspace_creation_properties(
        self,
    ) -> typing.Optional["WorkspacesDirectoryWorkspaceCreationProperties"]:
        '''workspace_creation_properties block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#workspace_creation_properties WorkspacesDirectory#workspace_creation_properties}
        '''
        result = self._values.get("workspace_creation_properties")
        return typing.cast(typing.Optional["WorkspacesDirectoryWorkspaceCreationProperties"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspacesDirectoryConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.workspaces.WorkspacesDirectorySelfServicePermissions",
    jsii_struct_bases=[],
    name_mapping={
        "change_compute_type": "changeComputeType",
        "increase_volume_size": "increaseVolumeSize",
        "rebuild_workspace": "rebuildWorkspace",
        "restart_workspace": "restartWorkspace",
        "switch_running_mode": "switchRunningMode",
    },
)
class WorkspacesDirectorySelfServicePermissions:
    def __init__(
        self,
        *,
        change_compute_type: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        increase_volume_size: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        rebuild_workspace: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        restart_workspace: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        switch_running_mode: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param change_compute_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#change_compute_type WorkspacesDirectory#change_compute_type}.
        :param increase_volume_size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#increase_volume_size WorkspacesDirectory#increase_volume_size}.
        :param rebuild_workspace: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#rebuild_workspace WorkspacesDirectory#rebuild_workspace}.
        :param restart_workspace: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#restart_workspace WorkspacesDirectory#restart_workspace}.
        :param switch_running_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#switch_running_mode WorkspacesDirectory#switch_running_mode}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if change_compute_type is not None:
            self._values["change_compute_type"] = change_compute_type
        if increase_volume_size is not None:
            self._values["increase_volume_size"] = increase_volume_size
        if rebuild_workspace is not None:
            self._values["rebuild_workspace"] = rebuild_workspace
        if restart_workspace is not None:
            self._values["restart_workspace"] = restart_workspace
        if switch_running_mode is not None:
            self._values["switch_running_mode"] = switch_running_mode

    @builtins.property
    def change_compute_type(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#change_compute_type WorkspacesDirectory#change_compute_type}.'''
        result = self._values.get("change_compute_type")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def increase_volume_size(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#increase_volume_size WorkspacesDirectory#increase_volume_size}.'''
        result = self._values.get("increase_volume_size")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def rebuild_workspace(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#rebuild_workspace WorkspacesDirectory#rebuild_workspace}.'''
        result = self._values.get("rebuild_workspace")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def restart_workspace(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#restart_workspace WorkspacesDirectory#restart_workspace}.'''
        result = self._values.get("restart_workspace")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def switch_running_mode(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#switch_running_mode WorkspacesDirectory#switch_running_mode}.'''
        result = self._values.get("switch_running_mode")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspacesDirectorySelfServicePermissions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkspacesDirectorySelfServicePermissionsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.workspaces.WorkspacesDirectorySelfServicePermissionsOutputReference",
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

    @jsii.member(jsii_name="resetChangeComputeType")
    def reset_change_compute_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetChangeComputeType", []))

    @jsii.member(jsii_name="resetIncreaseVolumeSize")
    def reset_increase_volume_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncreaseVolumeSize", []))

    @jsii.member(jsii_name="resetRebuildWorkspace")
    def reset_rebuild_workspace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRebuildWorkspace", []))

    @jsii.member(jsii_name="resetRestartWorkspace")
    def reset_restart_workspace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRestartWorkspace", []))

    @jsii.member(jsii_name="resetSwitchRunningMode")
    def reset_switch_running_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSwitchRunningMode", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="changeComputeTypeInput")
    def change_compute_type_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "changeComputeTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="increaseVolumeSizeInput")
    def increase_volume_size_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "increaseVolumeSizeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rebuildWorkspaceInput")
    def rebuild_workspace_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "rebuildWorkspaceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restartWorkspaceInput")
    def restart_workspace_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "restartWorkspaceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="switchRunningModeInput")
    def switch_running_mode_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "switchRunningModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="changeComputeType")
    def change_compute_type(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "changeComputeType"))

    @change_compute_type.setter
    def change_compute_type(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "changeComputeType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="increaseVolumeSize")
    def increase_volume_size(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "increaseVolumeSize"))

    @increase_volume_size.setter
    def increase_volume_size(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "increaseVolumeSize", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rebuildWorkspace")
    def rebuild_workspace(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "rebuildWorkspace"))

    @rebuild_workspace.setter
    def rebuild_workspace(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "rebuildWorkspace", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restartWorkspace")
    def restart_workspace(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "restartWorkspace"))

    @restart_workspace.setter
    def restart_workspace(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "restartWorkspace", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="switchRunningMode")
    def switch_running_mode(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "switchRunningMode"))

    @switch_running_mode.setter
    def switch_running_mode(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "switchRunningMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[WorkspacesDirectorySelfServicePermissions]:
        return typing.cast(typing.Optional[WorkspacesDirectorySelfServicePermissions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[WorkspacesDirectorySelfServicePermissions],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.workspaces.WorkspacesDirectoryWorkspaceAccessProperties",
    jsii_struct_bases=[],
    name_mapping={
        "device_type_android": "deviceTypeAndroid",
        "device_type_chromeos": "deviceTypeChromeos",
        "device_type_ios": "deviceTypeIos",
        "device_type_linux": "deviceTypeLinux",
        "device_type_osx": "deviceTypeOsx",
        "device_type_web": "deviceTypeWeb",
        "device_type_windows": "deviceTypeWindows",
        "device_type_zeroclient": "deviceTypeZeroclient",
    },
)
class WorkspacesDirectoryWorkspaceAccessProperties:
    def __init__(
        self,
        *,
        device_type_android: typing.Optional[builtins.str] = None,
        device_type_chromeos: typing.Optional[builtins.str] = None,
        device_type_ios: typing.Optional[builtins.str] = None,
        device_type_linux: typing.Optional[builtins.str] = None,
        device_type_osx: typing.Optional[builtins.str] = None,
        device_type_web: typing.Optional[builtins.str] = None,
        device_type_windows: typing.Optional[builtins.str] = None,
        device_type_zeroclient: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param device_type_android: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#device_type_android WorkspacesDirectory#device_type_android}.
        :param device_type_chromeos: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#device_type_chromeos WorkspacesDirectory#device_type_chromeos}.
        :param device_type_ios: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#device_type_ios WorkspacesDirectory#device_type_ios}.
        :param device_type_linux: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#device_type_linux WorkspacesDirectory#device_type_linux}.
        :param device_type_osx: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#device_type_osx WorkspacesDirectory#device_type_osx}.
        :param device_type_web: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#device_type_web WorkspacesDirectory#device_type_web}.
        :param device_type_windows: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#device_type_windows WorkspacesDirectory#device_type_windows}.
        :param device_type_zeroclient: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#device_type_zeroclient WorkspacesDirectory#device_type_zeroclient}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if device_type_android is not None:
            self._values["device_type_android"] = device_type_android
        if device_type_chromeos is not None:
            self._values["device_type_chromeos"] = device_type_chromeos
        if device_type_ios is not None:
            self._values["device_type_ios"] = device_type_ios
        if device_type_linux is not None:
            self._values["device_type_linux"] = device_type_linux
        if device_type_osx is not None:
            self._values["device_type_osx"] = device_type_osx
        if device_type_web is not None:
            self._values["device_type_web"] = device_type_web
        if device_type_windows is not None:
            self._values["device_type_windows"] = device_type_windows
        if device_type_zeroclient is not None:
            self._values["device_type_zeroclient"] = device_type_zeroclient

    @builtins.property
    def device_type_android(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#device_type_android WorkspacesDirectory#device_type_android}.'''
        result = self._values.get("device_type_android")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def device_type_chromeos(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#device_type_chromeos WorkspacesDirectory#device_type_chromeos}.'''
        result = self._values.get("device_type_chromeos")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def device_type_ios(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#device_type_ios WorkspacesDirectory#device_type_ios}.'''
        result = self._values.get("device_type_ios")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def device_type_linux(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#device_type_linux WorkspacesDirectory#device_type_linux}.'''
        result = self._values.get("device_type_linux")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def device_type_osx(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#device_type_osx WorkspacesDirectory#device_type_osx}.'''
        result = self._values.get("device_type_osx")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def device_type_web(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#device_type_web WorkspacesDirectory#device_type_web}.'''
        result = self._values.get("device_type_web")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def device_type_windows(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#device_type_windows WorkspacesDirectory#device_type_windows}.'''
        result = self._values.get("device_type_windows")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def device_type_zeroclient(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#device_type_zeroclient WorkspacesDirectory#device_type_zeroclient}.'''
        result = self._values.get("device_type_zeroclient")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspacesDirectoryWorkspaceAccessProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkspacesDirectoryWorkspaceAccessPropertiesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.workspaces.WorkspacesDirectoryWorkspaceAccessPropertiesOutputReference",
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

    @jsii.member(jsii_name="resetDeviceTypeAndroid")
    def reset_device_type_android(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeviceTypeAndroid", []))

    @jsii.member(jsii_name="resetDeviceTypeChromeos")
    def reset_device_type_chromeos(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeviceTypeChromeos", []))

    @jsii.member(jsii_name="resetDeviceTypeIos")
    def reset_device_type_ios(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeviceTypeIos", []))

    @jsii.member(jsii_name="resetDeviceTypeLinux")
    def reset_device_type_linux(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeviceTypeLinux", []))

    @jsii.member(jsii_name="resetDeviceTypeOsx")
    def reset_device_type_osx(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeviceTypeOsx", []))

    @jsii.member(jsii_name="resetDeviceTypeWeb")
    def reset_device_type_web(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeviceTypeWeb", []))

    @jsii.member(jsii_name="resetDeviceTypeWindows")
    def reset_device_type_windows(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeviceTypeWindows", []))

    @jsii.member(jsii_name="resetDeviceTypeZeroclient")
    def reset_device_type_zeroclient(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeviceTypeZeroclient", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceTypeAndroidInput")
    def device_type_android_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deviceTypeAndroidInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceTypeChromeosInput")
    def device_type_chromeos_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deviceTypeChromeosInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceTypeIosInput")
    def device_type_ios_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deviceTypeIosInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceTypeLinuxInput")
    def device_type_linux_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deviceTypeLinuxInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceTypeOsxInput")
    def device_type_osx_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deviceTypeOsxInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceTypeWebInput")
    def device_type_web_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deviceTypeWebInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceTypeWindowsInput")
    def device_type_windows_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deviceTypeWindowsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceTypeZeroclientInput")
    def device_type_zeroclient_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deviceTypeZeroclientInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceTypeAndroid")
    def device_type_android(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deviceTypeAndroid"))

    @device_type_android.setter
    def device_type_android(self, value: builtins.str) -> None:
        jsii.set(self, "deviceTypeAndroid", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceTypeChromeos")
    def device_type_chromeos(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deviceTypeChromeos"))

    @device_type_chromeos.setter
    def device_type_chromeos(self, value: builtins.str) -> None:
        jsii.set(self, "deviceTypeChromeos", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceTypeIos")
    def device_type_ios(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deviceTypeIos"))

    @device_type_ios.setter
    def device_type_ios(self, value: builtins.str) -> None:
        jsii.set(self, "deviceTypeIos", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceTypeLinux")
    def device_type_linux(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deviceTypeLinux"))

    @device_type_linux.setter
    def device_type_linux(self, value: builtins.str) -> None:
        jsii.set(self, "deviceTypeLinux", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceTypeOsx")
    def device_type_osx(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deviceTypeOsx"))

    @device_type_osx.setter
    def device_type_osx(self, value: builtins.str) -> None:
        jsii.set(self, "deviceTypeOsx", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceTypeWeb")
    def device_type_web(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deviceTypeWeb"))

    @device_type_web.setter
    def device_type_web(self, value: builtins.str) -> None:
        jsii.set(self, "deviceTypeWeb", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceTypeWindows")
    def device_type_windows(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deviceTypeWindows"))

    @device_type_windows.setter
    def device_type_windows(self, value: builtins.str) -> None:
        jsii.set(self, "deviceTypeWindows", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceTypeZeroclient")
    def device_type_zeroclient(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deviceTypeZeroclient"))

    @device_type_zeroclient.setter
    def device_type_zeroclient(self, value: builtins.str) -> None:
        jsii.set(self, "deviceTypeZeroclient", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[WorkspacesDirectoryWorkspaceAccessProperties]:
        return typing.cast(typing.Optional[WorkspacesDirectoryWorkspaceAccessProperties], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[WorkspacesDirectoryWorkspaceAccessProperties],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.workspaces.WorkspacesDirectoryWorkspaceCreationProperties",
    jsii_struct_bases=[],
    name_mapping={
        "custom_security_group_id": "customSecurityGroupId",
        "default_ou": "defaultOu",
        "enable_internet_access": "enableInternetAccess",
        "enable_maintenance_mode": "enableMaintenanceMode",
        "user_enabled_as_local_administrator": "userEnabledAsLocalAdministrator",
    },
)
class WorkspacesDirectoryWorkspaceCreationProperties:
    def __init__(
        self,
        *,
        custom_security_group_id: typing.Optional[builtins.str] = None,
        default_ou: typing.Optional[builtins.str] = None,
        enable_internet_access: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_maintenance_mode: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        user_enabled_as_local_administrator: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param custom_security_group_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#custom_security_group_id WorkspacesDirectory#custom_security_group_id}.
        :param default_ou: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#default_ou WorkspacesDirectory#default_ou}.
        :param enable_internet_access: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#enable_internet_access WorkspacesDirectory#enable_internet_access}.
        :param enable_maintenance_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#enable_maintenance_mode WorkspacesDirectory#enable_maintenance_mode}.
        :param user_enabled_as_local_administrator: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#user_enabled_as_local_administrator WorkspacesDirectory#user_enabled_as_local_administrator}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if custom_security_group_id is not None:
            self._values["custom_security_group_id"] = custom_security_group_id
        if default_ou is not None:
            self._values["default_ou"] = default_ou
        if enable_internet_access is not None:
            self._values["enable_internet_access"] = enable_internet_access
        if enable_maintenance_mode is not None:
            self._values["enable_maintenance_mode"] = enable_maintenance_mode
        if user_enabled_as_local_administrator is not None:
            self._values["user_enabled_as_local_administrator"] = user_enabled_as_local_administrator

    @builtins.property
    def custom_security_group_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#custom_security_group_id WorkspacesDirectory#custom_security_group_id}.'''
        result = self._values.get("custom_security_group_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_ou(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#default_ou WorkspacesDirectory#default_ou}.'''
        result = self._values.get("default_ou")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_internet_access(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#enable_internet_access WorkspacesDirectory#enable_internet_access}.'''
        result = self._values.get("enable_internet_access")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def enable_maintenance_mode(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#enable_maintenance_mode WorkspacesDirectory#enable_maintenance_mode}.'''
        result = self._values.get("enable_maintenance_mode")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def user_enabled_as_local_administrator(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_directory#user_enabled_as_local_administrator WorkspacesDirectory#user_enabled_as_local_administrator}.'''
        result = self._values.get("user_enabled_as_local_administrator")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspacesDirectoryWorkspaceCreationProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkspacesDirectoryWorkspaceCreationPropertiesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.workspaces.WorkspacesDirectoryWorkspaceCreationPropertiesOutputReference",
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

    @jsii.member(jsii_name="resetCustomSecurityGroupId")
    def reset_custom_security_group_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomSecurityGroupId", []))

    @jsii.member(jsii_name="resetDefaultOu")
    def reset_default_ou(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultOu", []))

    @jsii.member(jsii_name="resetEnableInternetAccess")
    def reset_enable_internet_access(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableInternetAccess", []))

    @jsii.member(jsii_name="resetEnableMaintenanceMode")
    def reset_enable_maintenance_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableMaintenanceMode", []))

    @jsii.member(jsii_name="resetUserEnabledAsLocalAdministrator")
    def reset_user_enabled_as_local_administrator(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserEnabledAsLocalAdministrator", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSecurityGroupIdInput")
    def custom_security_group_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customSecurityGroupIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultOuInput")
    def default_ou_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultOuInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableInternetAccessInput")
    def enable_internet_access_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enableInternetAccessInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableMaintenanceModeInput")
    def enable_maintenance_mode_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enableMaintenanceModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userEnabledAsLocalAdministratorInput")
    def user_enabled_as_local_administrator_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "userEnabledAsLocalAdministratorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSecurityGroupId")
    def custom_security_group_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customSecurityGroupId"))

    @custom_security_group_id.setter
    def custom_security_group_id(self, value: builtins.str) -> None:
        jsii.set(self, "customSecurityGroupId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultOu")
    def default_ou(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultOu"))

    @default_ou.setter
    def default_ou(self, value: builtins.str) -> None:
        jsii.set(self, "defaultOu", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableInternetAccess")
    def enable_internet_access(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enableInternetAccess"))

    @enable_internet_access.setter
    def enable_internet_access(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enableInternetAccess", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableMaintenanceMode")
    def enable_maintenance_mode(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enableMaintenanceMode"))

    @enable_maintenance_mode.setter
    def enable_maintenance_mode(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enableMaintenanceMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userEnabledAsLocalAdministrator")
    def user_enabled_as_local_administrator(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "userEnabledAsLocalAdministrator"))

    @user_enabled_as_local_administrator.setter
    def user_enabled_as_local_administrator(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "userEnabledAsLocalAdministrator", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[WorkspacesDirectoryWorkspaceCreationProperties]:
        return typing.cast(typing.Optional[WorkspacesDirectoryWorkspaceCreationProperties], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[WorkspacesDirectoryWorkspaceCreationProperties],
    ) -> None:
        jsii.set(self, "internalValue", value)


class WorkspacesIpGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.workspaces.WorkspacesIpGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/workspaces_ip_group aws_workspaces_ip_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        rules: typing.Optional[typing.Sequence["WorkspacesIpGroupRules"]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/workspaces_ip_group aws_workspaces_ip_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_ip_group#name WorkspacesIpGroup#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_ip_group#description WorkspacesIpGroup#description}.
        :param rules: rules block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_ip_group#rules WorkspacesIpGroup#rules}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_ip_group#tags WorkspacesIpGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_ip_group#tags_all WorkspacesIpGroup#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = WorkspacesIpGroupConfig(
            name=name,
            description=description,
            rules=rules,
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

    @jsii.member(jsii_name="resetRules")
    def reset_rules(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRules", []))

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
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rulesInput")
    def rules_input(self) -> typing.Optional[typing.List["WorkspacesIpGroupRules"]]:
        return typing.cast(typing.Optional[typing.List["WorkspacesIpGroupRules"]], jsii.get(self, "rulesInput"))

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
    @jsii.member(jsii_name="rules")
    def rules(self) -> typing.List["WorkspacesIpGroupRules"]:
        return typing.cast(typing.List["WorkspacesIpGroupRules"], jsii.get(self, "rules"))

    @rules.setter
    def rules(self, value: typing.List["WorkspacesIpGroupRules"]) -> None:
        jsii.set(self, "rules", value)

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
    jsii_type="@cdktf/provider-aws.workspaces.WorkspacesIpGroupConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "description": "description",
        "rules": "rules",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class WorkspacesIpGroupConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        rules: typing.Optional[typing.Sequence["WorkspacesIpGroupRules"]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS WorkSpaces.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_ip_group#name WorkspacesIpGroup#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_ip_group#description WorkspacesIpGroup#description}.
        :param rules: rules block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_ip_group#rules WorkspacesIpGroup#rules}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_ip_group#tags WorkspacesIpGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_ip_group#tags_all WorkspacesIpGroup#tags_all}.
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
        if description is not None:
            self._values["description"] = description
        if rules is not None:
            self._values["rules"] = rules
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_ip_group#name WorkspacesIpGroup#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_ip_group#description WorkspacesIpGroup#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rules(self) -> typing.Optional[typing.List["WorkspacesIpGroupRules"]]:
        '''rules block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_ip_group#rules WorkspacesIpGroup#rules}
        '''
        result = self._values.get("rules")
        return typing.cast(typing.Optional[typing.List["WorkspacesIpGroupRules"]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_ip_group#tags WorkspacesIpGroup#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_ip_group#tags_all WorkspacesIpGroup#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspacesIpGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.workspaces.WorkspacesIpGroupRules",
    jsii_struct_bases=[],
    name_mapping={"source": "source", "description": "description"},
)
class WorkspacesIpGroupRules:
    def __init__(
        self,
        *,
        source: builtins.str,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param source: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_ip_group#source WorkspacesIpGroup#source}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_ip_group#description WorkspacesIpGroup#description}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "source": source,
        }
        if description is not None:
            self._values["description"] = description

    @builtins.property
    def source(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_ip_group#source WorkspacesIpGroup#source}.'''
        result = self._values.get("source")
        assert result is not None, "Required property 'source' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_ip_group#description WorkspacesIpGroup#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspacesIpGroupRules(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkspacesWorkspace(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.workspaces.WorkspacesWorkspace",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace aws_workspaces_workspace}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        bundle_id: builtins.str,
        directory_id: builtins.str,
        user_name: builtins.str,
        root_volume_encryption_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["WorkspacesWorkspaceTimeouts"] = None,
        user_volume_encryption_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        volume_encryption_key: typing.Optional[builtins.str] = None,
        workspace_properties: typing.Optional["WorkspacesWorkspaceWorkspaceProperties"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace aws_workspaces_workspace} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param bundle_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#bundle_id WorkspacesWorkspace#bundle_id}.
        :param directory_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#directory_id WorkspacesWorkspace#directory_id}.
        :param user_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#user_name WorkspacesWorkspace#user_name}.
        :param root_volume_encryption_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#root_volume_encryption_enabled WorkspacesWorkspace#root_volume_encryption_enabled}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#tags WorkspacesWorkspace#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#tags_all WorkspacesWorkspace#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#timeouts WorkspacesWorkspace#timeouts}
        :param user_volume_encryption_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#user_volume_encryption_enabled WorkspacesWorkspace#user_volume_encryption_enabled}.
        :param volume_encryption_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#volume_encryption_key WorkspacesWorkspace#volume_encryption_key}.
        :param workspace_properties: workspace_properties block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#workspace_properties WorkspacesWorkspace#workspace_properties}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = WorkspacesWorkspaceConfig(
            bundle_id=bundle_id,
            directory_id=directory_id,
            user_name=user_name,
            root_volume_encryption_enabled=root_volume_encryption_enabled,
            tags=tags,
            tags_all=tags_all,
            timeouts=timeouts,
            user_volume_encryption_enabled=user_volume_encryption_enabled,
            volume_encryption_key=volume_encryption_key,
            workspace_properties=workspace_properties,
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
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#create WorkspacesWorkspace#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#delete WorkspacesWorkspace#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#update WorkspacesWorkspace#update}.
        '''
        value = WorkspacesWorkspaceTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="putWorkspaceProperties")
    def put_workspace_properties(
        self,
        *,
        compute_type_name: typing.Optional[builtins.str] = None,
        root_volume_size_gib: typing.Optional[jsii.Number] = None,
        running_mode: typing.Optional[builtins.str] = None,
        running_mode_auto_stop_timeout_in_minutes: typing.Optional[jsii.Number] = None,
        user_volume_size_gib: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param compute_type_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#compute_type_name WorkspacesWorkspace#compute_type_name}.
        :param root_volume_size_gib: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#root_volume_size_gib WorkspacesWorkspace#root_volume_size_gib}.
        :param running_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#running_mode WorkspacesWorkspace#running_mode}.
        :param running_mode_auto_stop_timeout_in_minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#running_mode_auto_stop_timeout_in_minutes WorkspacesWorkspace#running_mode_auto_stop_timeout_in_minutes}.
        :param user_volume_size_gib: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#user_volume_size_gib WorkspacesWorkspace#user_volume_size_gib}.
        '''
        value = WorkspacesWorkspaceWorkspaceProperties(
            compute_type_name=compute_type_name,
            root_volume_size_gib=root_volume_size_gib,
            running_mode=running_mode,
            running_mode_auto_stop_timeout_in_minutes=running_mode_auto_stop_timeout_in_minutes,
            user_volume_size_gib=user_volume_size_gib,
        )

        return typing.cast(None, jsii.invoke(self, "putWorkspaceProperties", [value]))

    @jsii.member(jsii_name="resetRootVolumeEncryptionEnabled")
    def reset_root_volume_encryption_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRootVolumeEncryptionEnabled", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="resetUserVolumeEncryptionEnabled")
    def reset_user_volume_encryption_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserVolumeEncryptionEnabled", []))

    @jsii.member(jsii_name="resetVolumeEncryptionKey")
    def reset_volume_encryption_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVolumeEncryptionKey", []))

    @jsii.member(jsii_name="resetWorkspaceProperties")
    def reset_workspace_properties(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkspaceProperties", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computerName")
    def computer_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "computerName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipAddress")
    def ip_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipAddress"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "WorkspacesWorkspaceTimeoutsOutputReference":
        return typing.cast("WorkspacesWorkspaceTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workspaceProperties")
    def workspace_properties(
        self,
    ) -> "WorkspacesWorkspaceWorkspacePropertiesOutputReference":
        return typing.cast("WorkspacesWorkspaceWorkspacePropertiesOutputReference", jsii.get(self, "workspaceProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bundleIdInput")
    def bundle_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bundleIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="directoryIdInput")
    def directory_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "directoryIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rootVolumeEncryptionEnabledInput")
    def root_volume_encryption_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "rootVolumeEncryptionEnabledInput"))

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
    def timeouts_input(self) -> typing.Optional["WorkspacesWorkspaceTimeouts"]:
        return typing.cast(typing.Optional["WorkspacesWorkspaceTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userNameInput")
    def user_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userVolumeEncryptionEnabledInput")
    def user_volume_encryption_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "userVolumeEncryptionEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeEncryptionKeyInput")
    def volume_encryption_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "volumeEncryptionKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workspacePropertiesInput")
    def workspace_properties_input(
        self,
    ) -> typing.Optional["WorkspacesWorkspaceWorkspaceProperties"]:
        return typing.cast(typing.Optional["WorkspacesWorkspaceWorkspaceProperties"], jsii.get(self, "workspacePropertiesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bundleId")
    def bundle_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bundleId"))

    @bundle_id.setter
    def bundle_id(self, value: builtins.str) -> None:
        jsii.set(self, "bundleId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="directoryId")
    def directory_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "directoryId"))

    @directory_id.setter
    def directory_id(self, value: builtins.str) -> None:
        jsii.set(self, "directoryId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rootVolumeEncryptionEnabled")
    def root_volume_encryption_enabled(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "rootVolumeEncryptionEnabled"))

    @root_volume_encryption_enabled.setter
    def root_volume_encryption_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "rootVolumeEncryptionEnabled", value)

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
    @jsii.member(jsii_name="userName")
    def user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userName"))

    @user_name.setter
    def user_name(self, value: builtins.str) -> None:
        jsii.set(self, "userName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userVolumeEncryptionEnabled")
    def user_volume_encryption_enabled(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "userVolumeEncryptionEnabled"))

    @user_volume_encryption_enabled.setter
    def user_volume_encryption_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "userVolumeEncryptionEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeEncryptionKey")
    def volume_encryption_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "volumeEncryptionKey"))

    @volume_encryption_key.setter
    def volume_encryption_key(self, value: builtins.str) -> None:
        jsii.set(self, "volumeEncryptionKey", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.workspaces.WorkspacesWorkspaceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "bundle_id": "bundleId",
        "directory_id": "directoryId",
        "user_name": "userName",
        "root_volume_encryption_enabled": "rootVolumeEncryptionEnabled",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
        "user_volume_encryption_enabled": "userVolumeEncryptionEnabled",
        "volume_encryption_key": "volumeEncryptionKey",
        "workspace_properties": "workspaceProperties",
    },
)
class WorkspacesWorkspaceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        bundle_id: builtins.str,
        directory_id: builtins.str,
        user_name: builtins.str,
        root_volume_encryption_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["WorkspacesWorkspaceTimeouts"] = None,
        user_volume_encryption_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        volume_encryption_key: typing.Optional[builtins.str] = None,
        workspace_properties: typing.Optional["WorkspacesWorkspaceWorkspaceProperties"] = None,
    ) -> None:
        '''AWS WorkSpaces.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param bundle_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#bundle_id WorkspacesWorkspace#bundle_id}.
        :param directory_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#directory_id WorkspacesWorkspace#directory_id}.
        :param user_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#user_name WorkspacesWorkspace#user_name}.
        :param root_volume_encryption_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#root_volume_encryption_enabled WorkspacesWorkspace#root_volume_encryption_enabled}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#tags WorkspacesWorkspace#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#tags_all WorkspacesWorkspace#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#timeouts WorkspacesWorkspace#timeouts}
        :param user_volume_encryption_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#user_volume_encryption_enabled WorkspacesWorkspace#user_volume_encryption_enabled}.
        :param volume_encryption_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#volume_encryption_key WorkspacesWorkspace#volume_encryption_key}.
        :param workspace_properties: workspace_properties block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#workspace_properties WorkspacesWorkspace#workspace_properties}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = WorkspacesWorkspaceTimeouts(**timeouts)
        if isinstance(workspace_properties, dict):
            workspace_properties = WorkspacesWorkspaceWorkspaceProperties(**workspace_properties)
        self._values: typing.Dict[str, typing.Any] = {
            "bundle_id": bundle_id,
            "directory_id": directory_id,
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
        if root_volume_encryption_enabled is not None:
            self._values["root_volume_encryption_enabled"] = root_volume_encryption_enabled
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if timeouts is not None:
            self._values["timeouts"] = timeouts
        if user_volume_encryption_enabled is not None:
            self._values["user_volume_encryption_enabled"] = user_volume_encryption_enabled
        if volume_encryption_key is not None:
            self._values["volume_encryption_key"] = volume_encryption_key
        if workspace_properties is not None:
            self._values["workspace_properties"] = workspace_properties

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
    def bundle_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#bundle_id WorkspacesWorkspace#bundle_id}.'''
        result = self._values.get("bundle_id")
        assert result is not None, "Required property 'bundle_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def directory_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#directory_id WorkspacesWorkspace#directory_id}.'''
        result = self._values.get("directory_id")
        assert result is not None, "Required property 'directory_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#user_name WorkspacesWorkspace#user_name}.'''
        result = self._values.get("user_name")
        assert result is not None, "Required property 'user_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def root_volume_encryption_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#root_volume_encryption_enabled WorkspacesWorkspace#root_volume_encryption_enabled}.'''
        result = self._values.get("root_volume_encryption_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#tags WorkspacesWorkspace#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#tags_all WorkspacesWorkspace#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["WorkspacesWorkspaceTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#timeouts WorkspacesWorkspace#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["WorkspacesWorkspaceTimeouts"], result)

    @builtins.property
    def user_volume_encryption_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#user_volume_encryption_enabled WorkspacesWorkspace#user_volume_encryption_enabled}.'''
        result = self._values.get("user_volume_encryption_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def volume_encryption_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#volume_encryption_key WorkspacesWorkspace#volume_encryption_key}.'''
        result = self._values.get("volume_encryption_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workspace_properties(
        self,
    ) -> typing.Optional["WorkspacesWorkspaceWorkspaceProperties"]:
        '''workspace_properties block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#workspace_properties WorkspacesWorkspace#workspace_properties}
        '''
        result = self._values.get("workspace_properties")
        return typing.cast(typing.Optional["WorkspacesWorkspaceWorkspaceProperties"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspacesWorkspaceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.workspaces.WorkspacesWorkspaceTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class WorkspacesWorkspaceTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#create WorkspacesWorkspace#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#delete WorkspacesWorkspace#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#update WorkspacesWorkspace#update}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#create WorkspacesWorkspace#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#delete WorkspacesWorkspace#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#update WorkspacesWorkspace#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspacesWorkspaceTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkspacesWorkspaceTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.workspaces.WorkspacesWorkspaceTimeoutsOutputReference",
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
    def internal_value(self) -> typing.Optional[WorkspacesWorkspaceTimeouts]:
        return typing.cast(typing.Optional[WorkspacesWorkspaceTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[WorkspacesWorkspaceTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.workspaces.WorkspacesWorkspaceWorkspaceProperties",
    jsii_struct_bases=[],
    name_mapping={
        "compute_type_name": "computeTypeName",
        "root_volume_size_gib": "rootVolumeSizeGib",
        "running_mode": "runningMode",
        "running_mode_auto_stop_timeout_in_minutes": "runningModeAutoStopTimeoutInMinutes",
        "user_volume_size_gib": "userVolumeSizeGib",
    },
)
class WorkspacesWorkspaceWorkspaceProperties:
    def __init__(
        self,
        *,
        compute_type_name: typing.Optional[builtins.str] = None,
        root_volume_size_gib: typing.Optional[jsii.Number] = None,
        running_mode: typing.Optional[builtins.str] = None,
        running_mode_auto_stop_timeout_in_minutes: typing.Optional[jsii.Number] = None,
        user_volume_size_gib: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param compute_type_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#compute_type_name WorkspacesWorkspace#compute_type_name}.
        :param root_volume_size_gib: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#root_volume_size_gib WorkspacesWorkspace#root_volume_size_gib}.
        :param running_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#running_mode WorkspacesWorkspace#running_mode}.
        :param running_mode_auto_stop_timeout_in_minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#running_mode_auto_stop_timeout_in_minutes WorkspacesWorkspace#running_mode_auto_stop_timeout_in_minutes}.
        :param user_volume_size_gib: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#user_volume_size_gib WorkspacesWorkspace#user_volume_size_gib}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if compute_type_name is not None:
            self._values["compute_type_name"] = compute_type_name
        if root_volume_size_gib is not None:
            self._values["root_volume_size_gib"] = root_volume_size_gib
        if running_mode is not None:
            self._values["running_mode"] = running_mode
        if running_mode_auto_stop_timeout_in_minutes is not None:
            self._values["running_mode_auto_stop_timeout_in_minutes"] = running_mode_auto_stop_timeout_in_minutes
        if user_volume_size_gib is not None:
            self._values["user_volume_size_gib"] = user_volume_size_gib

    @builtins.property
    def compute_type_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#compute_type_name WorkspacesWorkspace#compute_type_name}.'''
        result = self._values.get("compute_type_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def root_volume_size_gib(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#root_volume_size_gib WorkspacesWorkspace#root_volume_size_gib}.'''
        result = self._values.get("root_volume_size_gib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def running_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#running_mode WorkspacesWorkspace#running_mode}.'''
        result = self._values.get("running_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def running_mode_auto_stop_timeout_in_minutes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#running_mode_auto_stop_timeout_in_minutes WorkspacesWorkspace#running_mode_auto_stop_timeout_in_minutes}.'''
        result = self._values.get("running_mode_auto_stop_timeout_in_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def user_volume_size_gib(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/workspaces_workspace#user_volume_size_gib WorkspacesWorkspace#user_volume_size_gib}.'''
        result = self._values.get("user_volume_size_gib")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspacesWorkspaceWorkspaceProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkspacesWorkspaceWorkspacePropertiesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.workspaces.WorkspacesWorkspaceWorkspacePropertiesOutputReference",
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

    @jsii.member(jsii_name="resetComputeTypeName")
    def reset_compute_type_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComputeTypeName", []))

    @jsii.member(jsii_name="resetRootVolumeSizeGib")
    def reset_root_volume_size_gib(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRootVolumeSizeGib", []))

    @jsii.member(jsii_name="resetRunningMode")
    def reset_running_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRunningMode", []))

    @jsii.member(jsii_name="resetRunningModeAutoStopTimeoutInMinutes")
    def reset_running_mode_auto_stop_timeout_in_minutes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRunningModeAutoStopTimeoutInMinutes", []))

    @jsii.member(jsii_name="resetUserVolumeSizeGib")
    def reset_user_volume_size_gib(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserVolumeSizeGib", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeTypeNameInput")
    def compute_type_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "computeTypeNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rootVolumeSizeGibInput")
    def root_volume_size_gib_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "rootVolumeSizeGibInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runningModeAutoStopTimeoutInMinutesInput")
    def running_mode_auto_stop_timeout_in_minutes_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "runningModeAutoStopTimeoutInMinutesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runningModeInput")
    def running_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "runningModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userVolumeSizeGibInput")
    def user_volume_size_gib_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "userVolumeSizeGibInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeTypeName")
    def compute_type_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "computeTypeName"))

    @compute_type_name.setter
    def compute_type_name(self, value: builtins.str) -> None:
        jsii.set(self, "computeTypeName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rootVolumeSizeGib")
    def root_volume_size_gib(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "rootVolumeSizeGib"))

    @root_volume_size_gib.setter
    def root_volume_size_gib(self, value: jsii.Number) -> None:
        jsii.set(self, "rootVolumeSizeGib", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runningMode")
    def running_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runningMode"))

    @running_mode.setter
    def running_mode(self, value: builtins.str) -> None:
        jsii.set(self, "runningMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runningModeAutoStopTimeoutInMinutes")
    def running_mode_auto_stop_timeout_in_minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "runningModeAutoStopTimeoutInMinutes"))

    @running_mode_auto_stop_timeout_in_minutes.setter
    def running_mode_auto_stop_timeout_in_minutes(self, value: jsii.Number) -> None:
        jsii.set(self, "runningModeAutoStopTimeoutInMinutes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userVolumeSizeGib")
    def user_volume_size_gib(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "userVolumeSizeGib"))

    @user_volume_size_gib.setter
    def user_volume_size_gib(self, value: jsii.Number) -> None:
        jsii.set(self, "userVolumeSizeGib", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[WorkspacesWorkspaceWorkspaceProperties]:
        return typing.cast(typing.Optional[WorkspacesWorkspaceWorkspaceProperties], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[WorkspacesWorkspaceWorkspaceProperties],
    ) -> None:
        jsii.set(self, "internalValue", value)


__all__ = [
    "DataAwsWorkspacesBundle",
    "DataAwsWorkspacesBundleComputeType",
    "DataAwsWorkspacesBundleConfig",
    "DataAwsWorkspacesBundleRootStorage",
    "DataAwsWorkspacesBundleUserStorage",
    "DataAwsWorkspacesDirectory",
    "DataAwsWorkspacesDirectoryConfig",
    "DataAwsWorkspacesDirectorySelfServicePermissions",
    "DataAwsWorkspacesDirectoryWorkspaceAccessProperties",
    "DataAwsWorkspacesDirectoryWorkspaceCreationProperties",
    "DataAwsWorkspacesImage",
    "DataAwsWorkspacesImageConfig",
    "DataAwsWorkspacesWorkspace",
    "DataAwsWorkspacesWorkspaceConfig",
    "DataAwsWorkspacesWorkspaceWorkspaceProperties",
    "WorkspacesDirectory",
    "WorkspacesDirectoryConfig",
    "WorkspacesDirectorySelfServicePermissions",
    "WorkspacesDirectorySelfServicePermissionsOutputReference",
    "WorkspacesDirectoryWorkspaceAccessProperties",
    "WorkspacesDirectoryWorkspaceAccessPropertiesOutputReference",
    "WorkspacesDirectoryWorkspaceCreationProperties",
    "WorkspacesDirectoryWorkspaceCreationPropertiesOutputReference",
    "WorkspacesIpGroup",
    "WorkspacesIpGroupConfig",
    "WorkspacesIpGroupRules",
    "WorkspacesWorkspace",
    "WorkspacesWorkspaceConfig",
    "WorkspacesWorkspaceTimeouts",
    "WorkspacesWorkspaceTimeoutsOutputReference",
    "WorkspacesWorkspaceWorkspaceProperties",
    "WorkspacesWorkspaceWorkspacePropertiesOutputReference",
]

publication.publish()
