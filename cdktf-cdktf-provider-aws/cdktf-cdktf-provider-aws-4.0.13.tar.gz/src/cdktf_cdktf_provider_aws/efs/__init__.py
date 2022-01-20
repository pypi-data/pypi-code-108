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


class DataAwsEfsAccessPoint(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.efs.DataAwsEfsAccessPoint",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/efs_access_point aws_efs_access_point}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        access_point_id: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/efs_access_point aws_efs_access_point} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param access_point_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/efs_access_point#access_point_id DataAwsEfsAccessPoint#access_point_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/efs_access_point#tags DataAwsEfsAccessPoint#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsEfsAccessPointConfig(
            access_point_id=access_point_id,
            tags=tags,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="posixUser")
    def posix_user(self, index: builtins.str) -> "DataAwsEfsAccessPointPosixUser":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsEfsAccessPointPosixUser", jsii.invoke(self, "posixUser", [index]))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="rootDirectory")
    def root_directory(
        self,
        index: builtins.str,
    ) -> "DataAwsEfsAccessPointRootDirectory":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsEfsAccessPointRootDirectory", jsii.invoke(self, "rootDirectory", [index]))

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
    @jsii.member(jsii_name="fileSystemArn")
    def file_system_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileSystemArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemId")
    def file_system_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileSystemId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerId")
    def owner_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ownerId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessPointIdInput")
    def access_point_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessPointIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessPointId")
    def access_point_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessPointId"))

    @access_point_id.setter
    def access_point_id(self, value: builtins.str) -> None:
        jsii.set(self, "accessPointId", value)

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
    jsii_type="@cdktf/provider-aws.efs.DataAwsEfsAccessPointConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "access_point_id": "accessPointId",
        "tags": "tags",
    },
)
class DataAwsEfsAccessPointConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        access_point_id: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS EFS.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param access_point_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/efs_access_point#access_point_id DataAwsEfsAccessPoint#access_point_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/efs_access_point#tags DataAwsEfsAccessPoint#tags}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "access_point_id": access_point_id,
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
    def access_point_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/efs_access_point#access_point_id DataAwsEfsAccessPoint#access_point_id}.'''
        result = self._values.get("access_point_id")
        assert result is not None, "Required property 'access_point_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/efs_access_point#tags DataAwsEfsAccessPoint#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsEfsAccessPointConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsEfsAccessPointPosixUser(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.efs.DataAwsEfsAccessPointPosixUser",
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
    @jsii.member(jsii_name="gid")
    def gid(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "gid"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secondaryGids")
    def secondary_gids(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "secondaryGids"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uid")
    def uid(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "uid"))


class DataAwsEfsAccessPointRootDirectory(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.efs.DataAwsEfsAccessPointRootDirectory",
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
    @jsii.member(jsii_name="creationInfo")
    def creation_info(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "creationInfo"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))


class DataAwsEfsAccessPointRootDirectoryCreationInfo(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.efs.DataAwsEfsAccessPointRootDirectoryCreationInfo",
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
    @jsii.member(jsii_name="ownerGid")
    def owner_gid(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ownerGid"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerUid")
    def owner_uid(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ownerUid"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="permissions")
    def permissions(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "permissions"))


class DataAwsEfsAccessPoints(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.efs.DataAwsEfsAccessPoints",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/efs_access_points aws_efs_access_points}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        file_system_id: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/efs_access_points aws_efs_access_points} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param file_system_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/efs_access_points#file_system_id DataAwsEfsAccessPoints#file_system_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsEfsAccessPointsConfig(
            file_system_id=file_system_id,
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
    @jsii.member(jsii_name="arns")
    def arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "arns"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ids")
    def ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ids"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemIdInput")
    def file_system_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fileSystemIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemId")
    def file_system_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileSystemId"))

    @file_system_id.setter
    def file_system_id(self, value: builtins.str) -> None:
        jsii.set(self, "fileSystemId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.efs.DataAwsEfsAccessPointsConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "file_system_id": "fileSystemId",
    },
)
class DataAwsEfsAccessPointsConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        file_system_id: builtins.str,
    ) -> None:
        '''AWS EFS.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param file_system_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/efs_access_points#file_system_id DataAwsEfsAccessPoints#file_system_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "file_system_id": file_system_id,
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
    def file_system_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/efs_access_points#file_system_id DataAwsEfsAccessPoints#file_system_id}.'''
        result = self._values.get("file_system_id")
        assert result is not None, "Required property 'file_system_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsEfsAccessPointsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsEfsFileSystem(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.efs.DataAwsEfsFileSystem",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/efs_file_system aws_efs_file_system}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        creation_token: typing.Optional[builtins.str] = None,
        file_system_id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/efs_file_system aws_efs_file_system} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param creation_token: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/efs_file_system#creation_token DataAwsEfsFileSystem#creation_token}.
        :param file_system_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/efs_file_system#file_system_id DataAwsEfsFileSystem#file_system_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/efs_file_system#tags DataAwsEfsFileSystem#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsEfsFileSystemConfig(
            creation_token=creation_token,
            file_system_id=file_system_id,
            tags=tags,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="lifecyclePolicy")
    def lifecycle_policy(
        self,
        index: builtins.str,
    ) -> "DataAwsEfsFileSystemLifecyclePolicy":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsEfsFileSystemLifecyclePolicy", jsii.invoke(self, "lifecyclePolicy", [index]))

    @jsii.member(jsii_name="resetCreationToken")
    def reset_creation_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreationToken", []))

    @jsii.member(jsii_name="resetFileSystemId")
    def reset_file_system_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFileSystemId", []))

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
    @jsii.member(jsii_name="availabilityZoneId")
    def availability_zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availabilityZoneId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZoneName")
    def availability_zone_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availabilityZoneName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsName")
    def dns_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dnsName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encrypted")
    def encrypted(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "encrypted"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="performanceMode")
    def performance_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "performanceMode"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="provisionedThroughputInMibps")
    def provisioned_throughput_in_mibps(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "provisionedThroughputInMibps"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sizeInBytes")
    def size_in_bytes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sizeInBytes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="throughputMode")
    def throughput_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "throughputMode"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="creationTokenInput")
    def creation_token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "creationTokenInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemIdInput")
    def file_system_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fileSystemIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="creationToken")
    def creation_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creationToken"))

    @creation_token.setter
    def creation_token(self, value: builtins.str) -> None:
        jsii.set(self, "creationToken", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemId")
    def file_system_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileSystemId"))

    @file_system_id.setter
    def file_system_id(self, value: builtins.str) -> None:
        jsii.set(self, "fileSystemId", value)

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
    jsii_type="@cdktf/provider-aws.efs.DataAwsEfsFileSystemConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "creation_token": "creationToken",
        "file_system_id": "fileSystemId",
        "tags": "tags",
    },
)
class DataAwsEfsFileSystemConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        creation_token: typing.Optional[builtins.str] = None,
        file_system_id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS EFS.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param creation_token: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/efs_file_system#creation_token DataAwsEfsFileSystem#creation_token}.
        :param file_system_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/efs_file_system#file_system_id DataAwsEfsFileSystem#file_system_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/efs_file_system#tags DataAwsEfsFileSystem#tags}.
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
        if creation_token is not None:
            self._values["creation_token"] = creation_token
        if file_system_id is not None:
            self._values["file_system_id"] = file_system_id
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
    def creation_token(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/efs_file_system#creation_token DataAwsEfsFileSystem#creation_token}.'''
        result = self._values.get("creation_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def file_system_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/efs_file_system#file_system_id DataAwsEfsFileSystem#file_system_id}.'''
        result = self._values.get("file_system_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/efs_file_system#tags DataAwsEfsFileSystem#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsEfsFileSystemConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsEfsFileSystemLifecyclePolicy(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.efs.DataAwsEfsFileSystemLifecyclePolicy",
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
    @jsii.member(jsii_name="transitionToIa")
    def transition_to_ia(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "transitionToIa"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="transitionToPrimaryStorageClass")
    def transition_to_primary_storage_class(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "transitionToPrimaryStorageClass"))


class DataAwsEfsMountTarget(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.efs.DataAwsEfsMountTarget",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/efs_mount_target aws_efs_mount_target}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        access_point_id: typing.Optional[builtins.str] = None,
        file_system_id: typing.Optional[builtins.str] = None,
        mount_target_id: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/efs_mount_target aws_efs_mount_target} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param access_point_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/efs_mount_target#access_point_id DataAwsEfsMountTarget#access_point_id}.
        :param file_system_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/efs_mount_target#file_system_id DataAwsEfsMountTarget#file_system_id}.
        :param mount_target_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/efs_mount_target#mount_target_id DataAwsEfsMountTarget#mount_target_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsEfsMountTargetConfig(
            access_point_id=access_point_id,
            file_system_id=file_system_id,
            mount_target_id=mount_target_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAccessPointId")
    def reset_access_point_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessPointId", []))

    @jsii.member(jsii_name="resetFileSystemId")
    def reset_file_system_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFileSystemId", []))

    @jsii.member(jsii_name="resetMountTargetId")
    def reset_mount_target_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMountTargetId", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZoneId")
    def availability_zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availabilityZoneId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZoneName")
    def availability_zone_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availabilityZoneName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsName")
    def dns_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dnsName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemArn")
    def file_system_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileSystemArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipAddress")
    def ip_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipAddress"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mountTargetDnsName")
    def mount_target_dns_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mountTargetDnsName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkInterfaceId")
    def network_interface_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkInterfaceId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerId")
    def owner_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ownerId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroups")
    def security_groups(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroups"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetId")
    def subnet_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subnetId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessPointIdInput")
    def access_point_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessPointIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemIdInput")
    def file_system_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fileSystemIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mountTargetIdInput")
    def mount_target_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mountTargetIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessPointId")
    def access_point_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessPointId"))

    @access_point_id.setter
    def access_point_id(self, value: builtins.str) -> None:
        jsii.set(self, "accessPointId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemId")
    def file_system_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileSystemId"))

    @file_system_id.setter
    def file_system_id(self, value: builtins.str) -> None:
        jsii.set(self, "fileSystemId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mountTargetId")
    def mount_target_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mountTargetId"))

    @mount_target_id.setter
    def mount_target_id(self, value: builtins.str) -> None:
        jsii.set(self, "mountTargetId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.efs.DataAwsEfsMountTargetConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "access_point_id": "accessPointId",
        "file_system_id": "fileSystemId",
        "mount_target_id": "mountTargetId",
    },
)
class DataAwsEfsMountTargetConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        access_point_id: typing.Optional[builtins.str] = None,
        file_system_id: typing.Optional[builtins.str] = None,
        mount_target_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS EFS.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param access_point_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/efs_mount_target#access_point_id DataAwsEfsMountTarget#access_point_id}.
        :param file_system_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/efs_mount_target#file_system_id DataAwsEfsMountTarget#file_system_id}.
        :param mount_target_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/efs_mount_target#mount_target_id DataAwsEfsMountTarget#mount_target_id}.
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
        if access_point_id is not None:
            self._values["access_point_id"] = access_point_id
        if file_system_id is not None:
            self._values["file_system_id"] = file_system_id
        if mount_target_id is not None:
            self._values["mount_target_id"] = mount_target_id

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
    def access_point_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/efs_mount_target#access_point_id DataAwsEfsMountTarget#access_point_id}.'''
        result = self._values.get("access_point_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def file_system_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/efs_mount_target#file_system_id DataAwsEfsMountTarget#file_system_id}.'''
        result = self._values.get("file_system_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mount_target_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/efs_mount_target#mount_target_id DataAwsEfsMountTarget#mount_target_id}.'''
        result = self._values.get("mount_target_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsEfsMountTargetConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EfsAccessPoint(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.efs.EfsAccessPoint",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point aws_efs_access_point}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        file_system_id: builtins.str,
        posix_user: typing.Optional["EfsAccessPointPosixUser"] = None,
        root_directory: typing.Optional["EfsAccessPointRootDirectory"] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point aws_efs_access_point} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param file_system_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#file_system_id EfsAccessPoint#file_system_id}.
        :param posix_user: posix_user block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#posix_user EfsAccessPoint#posix_user}
        :param root_directory: root_directory block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#root_directory EfsAccessPoint#root_directory}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#tags EfsAccessPoint#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#tags_all EfsAccessPoint#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = EfsAccessPointConfig(
            file_system_id=file_system_id,
            posix_user=posix_user,
            root_directory=root_directory,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putPosixUser")
    def put_posix_user(
        self,
        *,
        gid: jsii.Number,
        uid: jsii.Number,
        secondary_gids: typing.Optional[typing.Sequence[jsii.Number]] = None,
    ) -> None:
        '''
        :param gid: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#gid EfsAccessPoint#gid}.
        :param uid: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#uid EfsAccessPoint#uid}.
        :param secondary_gids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#secondary_gids EfsAccessPoint#secondary_gids}.
        '''
        value = EfsAccessPointPosixUser(
            gid=gid, uid=uid, secondary_gids=secondary_gids
        )

        return typing.cast(None, jsii.invoke(self, "putPosixUser", [value]))

    @jsii.member(jsii_name="putRootDirectory")
    def put_root_directory(
        self,
        *,
        creation_info: typing.Optional["EfsAccessPointRootDirectoryCreationInfo"] = None,
        path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param creation_info: creation_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#creation_info EfsAccessPoint#creation_info}
        :param path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#path EfsAccessPoint#path}.
        '''
        value = EfsAccessPointRootDirectory(creation_info=creation_info, path=path)

        return typing.cast(None, jsii.invoke(self, "putRootDirectory", [value]))

    @jsii.member(jsii_name="resetPosixUser")
    def reset_posix_user(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPosixUser", []))

    @jsii.member(jsii_name="resetRootDirectory")
    def reset_root_directory(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRootDirectory", []))

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
    @jsii.member(jsii_name="fileSystemArn")
    def file_system_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileSystemArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerId")
    def owner_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ownerId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="posixUser")
    def posix_user(self) -> "EfsAccessPointPosixUserOutputReference":
        return typing.cast("EfsAccessPointPosixUserOutputReference", jsii.get(self, "posixUser"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rootDirectory")
    def root_directory(self) -> "EfsAccessPointRootDirectoryOutputReference":
        return typing.cast("EfsAccessPointRootDirectoryOutputReference", jsii.get(self, "rootDirectory"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemIdInput")
    def file_system_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fileSystemIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="posixUserInput")
    def posix_user_input(self) -> typing.Optional["EfsAccessPointPosixUser"]:
        return typing.cast(typing.Optional["EfsAccessPointPosixUser"], jsii.get(self, "posixUserInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rootDirectoryInput")
    def root_directory_input(self) -> typing.Optional["EfsAccessPointRootDirectory"]:
        return typing.cast(typing.Optional["EfsAccessPointRootDirectory"], jsii.get(self, "rootDirectoryInput"))

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
    @jsii.member(jsii_name="fileSystemId")
    def file_system_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileSystemId"))

    @file_system_id.setter
    def file_system_id(self, value: builtins.str) -> None:
        jsii.set(self, "fileSystemId", value)

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
    jsii_type="@cdktf/provider-aws.efs.EfsAccessPointConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "file_system_id": "fileSystemId",
        "posix_user": "posixUser",
        "root_directory": "rootDirectory",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class EfsAccessPointConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        file_system_id: builtins.str,
        posix_user: typing.Optional["EfsAccessPointPosixUser"] = None,
        root_directory: typing.Optional["EfsAccessPointRootDirectory"] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS EFS.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param file_system_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#file_system_id EfsAccessPoint#file_system_id}.
        :param posix_user: posix_user block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#posix_user EfsAccessPoint#posix_user}
        :param root_directory: root_directory block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#root_directory EfsAccessPoint#root_directory}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#tags EfsAccessPoint#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#tags_all EfsAccessPoint#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(posix_user, dict):
            posix_user = EfsAccessPointPosixUser(**posix_user)
        if isinstance(root_directory, dict):
            root_directory = EfsAccessPointRootDirectory(**root_directory)
        self._values: typing.Dict[str, typing.Any] = {
            "file_system_id": file_system_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if posix_user is not None:
            self._values["posix_user"] = posix_user
        if root_directory is not None:
            self._values["root_directory"] = root_directory
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
    def file_system_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#file_system_id EfsAccessPoint#file_system_id}.'''
        result = self._values.get("file_system_id")
        assert result is not None, "Required property 'file_system_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def posix_user(self) -> typing.Optional["EfsAccessPointPosixUser"]:
        '''posix_user block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#posix_user EfsAccessPoint#posix_user}
        '''
        result = self._values.get("posix_user")
        return typing.cast(typing.Optional["EfsAccessPointPosixUser"], result)

    @builtins.property
    def root_directory(self) -> typing.Optional["EfsAccessPointRootDirectory"]:
        '''root_directory block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#root_directory EfsAccessPoint#root_directory}
        '''
        result = self._values.get("root_directory")
        return typing.cast(typing.Optional["EfsAccessPointRootDirectory"], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#tags EfsAccessPoint#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#tags_all EfsAccessPoint#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EfsAccessPointConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.efs.EfsAccessPointPosixUser",
    jsii_struct_bases=[],
    name_mapping={"gid": "gid", "uid": "uid", "secondary_gids": "secondaryGids"},
)
class EfsAccessPointPosixUser:
    def __init__(
        self,
        *,
        gid: jsii.Number,
        uid: jsii.Number,
        secondary_gids: typing.Optional[typing.Sequence[jsii.Number]] = None,
    ) -> None:
        '''
        :param gid: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#gid EfsAccessPoint#gid}.
        :param uid: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#uid EfsAccessPoint#uid}.
        :param secondary_gids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#secondary_gids EfsAccessPoint#secondary_gids}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "gid": gid,
            "uid": uid,
        }
        if secondary_gids is not None:
            self._values["secondary_gids"] = secondary_gids

    @builtins.property
    def gid(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#gid EfsAccessPoint#gid}.'''
        result = self._values.get("gid")
        assert result is not None, "Required property 'gid' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def uid(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#uid EfsAccessPoint#uid}.'''
        result = self._values.get("uid")
        assert result is not None, "Required property 'uid' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def secondary_gids(self) -> typing.Optional[typing.List[jsii.Number]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#secondary_gids EfsAccessPoint#secondary_gids}.'''
        result = self._values.get("secondary_gids")
        return typing.cast(typing.Optional[typing.List[jsii.Number]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EfsAccessPointPosixUser(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EfsAccessPointPosixUserOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.efs.EfsAccessPointPosixUserOutputReference",
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

    @jsii.member(jsii_name="resetSecondaryGids")
    def reset_secondary_gids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecondaryGids", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gidInput")
    def gid_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "gidInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secondaryGidsInput")
    def secondary_gids_input(self) -> typing.Optional[typing.List[jsii.Number]]:
        return typing.cast(typing.Optional[typing.List[jsii.Number]], jsii.get(self, "secondaryGidsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uidInput")
    def uid_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "uidInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gid")
    def gid(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "gid"))

    @gid.setter
    def gid(self, value: jsii.Number) -> None:
        jsii.set(self, "gid", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secondaryGids")
    def secondary_gids(self) -> typing.List[jsii.Number]:
        return typing.cast(typing.List[jsii.Number], jsii.get(self, "secondaryGids"))

    @secondary_gids.setter
    def secondary_gids(self, value: typing.List[jsii.Number]) -> None:
        jsii.set(self, "secondaryGids", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uid")
    def uid(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "uid"))

    @uid.setter
    def uid(self, value: jsii.Number) -> None:
        jsii.set(self, "uid", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[EfsAccessPointPosixUser]:
        return typing.cast(typing.Optional[EfsAccessPointPosixUser], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[EfsAccessPointPosixUser]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.efs.EfsAccessPointRootDirectory",
    jsii_struct_bases=[],
    name_mapping={"creation_info": "creationInfo", "path": "path"},
)
class EfsAccessPointRootDirectory:
    def __init__(
        self,
        *,
        creation_info: typing.Optional["EfsAccessPointRootDirectoryCreationInfo"] = None,
        path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param creation_info: creation_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#creation_info EfsAccessPoint#creation_info}
        :param path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#path EfsAccessPoint#path}.
        '''
        if isinstance(creation_info, dict):
            creation_info = EfsAccessPointRootDirectoryCreationInfo(**creation_info)
        self._values: typing.Dict[str, typing.Any] = {}
        if creation_info is not None:
            self._values["creation_info"] = creation_info
        if path is not None:
            self._values["path"] = path

    @builtins.property
    def creation_info(
        self,
    ) -> typing.Optional["EfsAccessPointRootDirectoryCreationInfo"]:
        '''creation_info block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#creation_info EfsAccessPoint#creation_info}
        '''
        result = self._values.get("creation_info")
        return typing.cast(typing.Optional["EfsAccessPointRootDirectoryCreationInfo"], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#path EfsAccessPoint#path}.'''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EfsAccessPointRootDirectory(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.efs.EfsAccessPointRootDirectoryCreationInfo",
    jsii_struct_bases=[],
    name_mapping={
        "owner_gid": "ownerGid",
        "owner_uid": "ownerUid",
        "permissions": "permissions",
    },
)
class EfsAccessPointRootDirectoryCreationInfo:
    def __init__(
        self,
        *,
        owner_gid: jsii.Number,
        owner_uid: jsii.Number,
        permissions: builtins.str,
    ) -> None:
        '''
        :param owner_gid: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#owner_gid EfsAccessPoint#owner_gid}.
        :param owner_uid: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#owner_uid EfsAccessPoint#owner_uid}.
        :param permissions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#permissions EfsAccessPoint#permissions}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "owner_gid": owner_gid,
            "owner_uid": owner_uid,
            "permissions": permissions,
        }

    @builtins.property
    def owner_gid(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#owner_gid EfsAccessPoint#owner_gid}.'''
        result = self._values.get("owner_gid")
        assert result is not None, "Required property 'owner_gid' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def owner_uid(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#owner_uid EfsAccessPoint#owner_uid}.'''
        result = self._values.get("owner_uid")
        assert result is not None, "Required property 'owner_uid' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def permissions(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#permissions EfsAccessPoint#permissions}.'''
        result = self._values.get("permissions")
        assert result is not None, "Required property 'permissions' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EfsAccessPointRootDirectoryCreationInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EfsAccessPointRootDirectoryCreationInfoOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.efs.EfsAccessPointRootDirectoryCreationInfoOutputReference",
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
    @jsii.member(jsii_name="ownerGidInput")
    def owner_gid_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ownerGidInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerUidInput")
    def owner_uid_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ownerUidInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="permissionsInput")
    def permissions_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "permissionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerGid")
    def owner_gid(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ownerGid"))

    @owner_gid.setter
    def owner_gid(self, value: jsii.Number) -> None:
        jsii.set(self, "ownerGid", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerUid")
    def owner_uid(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ownerUid"))

    @owner_uid.setter
    def owner_uid(self, value: jsii.Number) -> None:
        jsii.set(self, "ownerUid", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="permissions")
    def permissions(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "permissions"))

    @permissions.setter
    def permissions(self, value: builtins.str) -> None:
        jsii.set(self, "permissions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[EfsAccessPointRootDirectoryCreationInfo]:
        return typing.cast(typing.Optional[EfsAccessPointRootDirectoryCreationInfo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[EfsAccessPointRootDirectoryCreationInfo],
    ) -> None:
        jsii.set(self, "internalValue", value)


class EfsAccessPointRootDirectoryOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.efs.EfsAccessPointRootDirectoryOutputReference",
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

    @jsii.member(jsii_name="putCreationInfo")
    def put_creation_info(
        self,
        *,
        owner_gid: jsii.Number,
        owner_uid: jsii.Number,
        permissions: builtins.str,
    ) -> None:
        '''
        :param owner_gid: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#owner_gid EfsAccessPoint#owner_gid}.
        :param owner_uid: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#owner_uid EfsAccessPoint#owner_uid}.
        :param permissions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_access_point#permissions EfsAccessPoint#permissions}.
        '''
        value = EfsAccessPointRootDirectoryCreationInfo(
            owner_gid=owner_gid, owner_uid=owner_uid, permissions=permissions
        )

        return typing.cast(None, jsii.invoke(self, "putCreationInfo", [value]))

    @jsii.member(jsii_name="resetCreationInfo")
    def reset_creation_info(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreationInfo", []))

    @jsii.member(jsii_name="resetPath")
    def reset_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPath", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="creationInfo")
    def creation_info(self) -> EfsAccessPointRootDirectoryCreationInfoOutputReference:
        return typing.cast(EfsAccessPointRootDirectoryCreationInfoOutputReference, jsii.get(self, "creationInfo"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="creationInfoInput")
    def creation_info_input(
        self,
    ) -> typing.Optional[EfsAccessPointRootDirectoryCreationInfo]:
        return typing.cast(typing.Optional[EfsAccessPointRootDirectoryCreationInfo], jsii.get(self, "creationInfoInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        jsii.set(self, "path", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[EfsAccessPointRootDirectory]:
        return typing.cast(typing.Optional[EfsAccessPointRootDirectory], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[EfsAccessPointRootDirectory],
    ) -> None:
        jsii.set(self, "internalValue", value)


class EfsBackupPolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.efs.EfsBackupPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/efs_backup_policy aws_efs_backup_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        backup_policy: "EfsBackupPolicyBackupPolicy",
        file_system_id: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/efs_backup_policy aws_efs_backup_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param backup_policy: backup_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_backup_policy#backup_policy EfsBackupPolicy#backup_policy}
        :param file_system_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_backup_policy#file_system_id EfsBackupPolicy#file_system_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = EfsBackupPolicyConfig(
            backup_policy=backup_policy,
            file_system_id=file_system_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putBackupPolicy")
    def put_backup_policy(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_backup_policy#status EfsBackupPolicy#status}.
        '''
        value = EfsBackupPolicyBackupPolicy(status=status)

        return typing.cast(None, jsii.invoke(self, "putBackupPolicy", [value]))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupPolicy")
    def backup_policy(self) -> "EfsBackupPolicyBackupPolicyOutputReference":
        return typing.cast("EfsBackupPolicyBackupPolicyOutputReference", jsii.get(self, "backupPolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupPolicyInput")
    def backup_policy_input(self) -> typing.Optional["EfsBackupPolicyBackupPolicy"]:
        return typing.cast(typing.Optional["EfsBackupPolicyBackupPolicy"], jsii.get(self, "backupPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemIdInput")
    def file_system_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fileSystemIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemId")
    def file_system_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileSystemId"))

    @file_system_id.setter
    def file_system_id(self, value: builtins.str) -> None:
        jsii.set(self, "fileSystemId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.efs.EfsBackupPolicyBackupPolicy",
    jsii_struct_bases=[],
    name_mapping={"status": "status"},
)
class EfsBackupPolicyBackupPolicy:
    def __init__(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_backup_policy#status EfsBackupPolicy#status}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "status": status,
        }

    @builtins.property
    def status(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_backup_policy#status EfsBackupPolicy#status}.'''
        result = self._values.get("status")
        assert result is not None, "Required property 'status' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EfsBackupPolicyBackupPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EfsBackupPolicyBackupPolicyOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.efs.EfsBackupPolicyBackupPolicyOutputReference",
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
    @jsii.member(jsii_name="statusInput")
    def status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @status.setter
    def status(self, value: builtins.str) -> None:
        jsii.set(self, "status", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[EfsBackupPolicyBackupPolicy]:
        return typing.cast(typing.Optional[EfsBackupPolicyBackupPolicy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[EfsBackupPolicyBackupPolicy],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.efs.EfsBackupPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "backup_policy": "backupPolicy",
        "file_system_id": "fileSystemId",
    },
)
class EfsBackupPolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        backup_policy: EfsBackupPolicyBackupPolicy,
        file_system_id: builtins.str,
    ) -> None:
        '''AWS EFS.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param backup_policy: backup_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_backup_policy#backup_policy EfsBackupPolicy#backup_policy}
        :param file_system_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_backup_policy#file_system_id EfsBackupPolicy#file_system_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(backup_policy, dict):
            backup_policy = EfsBackupPolicyBackupPolicy(**backup_policy)
        self._values: typing.Dict[str, typing.Any] = {
            "backup_policy": backup_policy,
            "file_system_id": file_system_id,
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
    def backup_policy(self) -> EfsBackupPolicyBackupPolicy:
        '''backup_policy block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_backup_policy#backup_policy EfsBackupPolicy#backup_policy}
        '''
        result = self._values.get("backup_policy")
        assert result is not None, "Required property 'backup_policy' is missing"
        return typing.cast(EfsBackupPolicyBackupPolicy, result)

    @builtins.property
    def file_system_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_backup_policy#file_system_id EfsBackupPolicy#file_system_id}.'''
        result = self._values.get("file_system_id")
        assert result is not None, "Required property 'file_system_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EfsBackupPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EfsFileSystem(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.efs.EfsFileSystem",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system aws_efs_file_system}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        availability_zone_name: typing.Optional[builtins.str] = None,
        creation_token: typing.Optional[builtins.str] = None,
        encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        lifecycle_policy: typing.Optional[typing.Sequence["EfsFileSystemLifecyclePolicy"]] = None,
        performance_mode: typing.Optional[builtins.str] = None,
        provisioned_throughput_in_mibps: typing.Optional[jsii.Number] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        throughput_mode: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system aws_efs_file_system} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param availability_zone_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#availability_zone_name EfsFileSystem#availability_zone_name}.
        :param creation_token: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#creation_token EfsFileSystem#creation_token}.
        :param encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#encrypted EfsFileSystem#encrypted}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#kms_key_id EfsFileSystem#kms_key_id}.
        :param lifecycle_policy: lifecycle_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#lifecycle_policy EfsFileSystem#lifecycle_policy}
        :param performance_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#performance_mode EfsFileSystem#performance_mode}.
        :param provisioned_throughput_in_mibps: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#provisioned_throughput_in_mibps EfsFileSystem#provisioned_throughput_in_mibps}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#tags EfsFileSystem#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#tags_all EfsFileSystem#tags_all}.
        :param throughput_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#throughput_mode EfsFileSystem#throughput_mode}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = EfsFileSystemConfig(
            availability_zone_name=availability_zone_name,
            creation_token=creation_token,
            encrypted=encrypted,
            kms_key_id=kms_key_id,
            lifecycle_policy=lifecycle_policy,
            performance_mode=performance_mode,
            provisioned_throughput_in_mibps=provisioned_throughput_in_mibps,
            tags=tags,
            tags_all=tags_all,
            throughput_mode=throughput_mode,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAvailabilityZoneName")
    def reset_availability_zone_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAvailabilityZoneName", []))

    @jsii.member(jsii_name="resetCreationToken")
    def reset_creation_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreationToken", []))

    @jsii.member(jsii_name="resetEncrypted")
    def reset_encrypted(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncrypted", []))

    @jsii.member(jsii_name="resetKmsKeyId")
    def reset_kms_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyId", []))

    @jsii.member(jsii_name="resetLifecyclePolicy")
    def reset_lifecycle_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLifecyclePolicy", []))

    @jsii.member(jsii_name="resetPerformanceMode")
    def reset_performance_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPerformanceMode", []))

    @jsii.member(jsii_name="resetProvisionedThroughputInMibps")
    def reset_provisioned_throughput_in_mibps(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProvisionedThroughputInMibps", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetThroughputMode")
    def reset_throughput_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThroughputMode", []))

    @jsii.member(jsii_name="sizeInBytes")
    def size_in_bytes(self, index: builtins.str) -> "EfsFileSystemSizeInBytes":
        '''
        :param index: -
        '''
        return typing.cast("EfsFileSystemSizeInBytes", jsii.invoke(self, "sizeInBytes", [index]))

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
    @jsii.member(jsii_name="availabilityZoneId")
    def availability_zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availabilityZoneId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsName")
    def dns_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dnsName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numberOfMountTargets")
    def number_of_mount_targets(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numberOfMountTargets"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerId")
    def owner_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ownerId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZoneNameInput")
    def availability_zone_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "availabilityZoneNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="creationTokenInput")
    def creation_token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "creationTokenInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptedInput")
    def encrypted_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "encryptedInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyIdInput")
    def kms_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lifecyclePolicyInput")
    def lifecycle_policy_input(
        self,
    ) -> typing.Optional[typing.List["EfsFileSystemLifecyclePolicy"]]:
        return typing.cast(typing.Optional[typing.List["EfsFileSystemLifecyclePolicy"]], jsii.get(self, "lifecyclePolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="performanceModeInput")
    def performance_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "performanceModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="provisionedThroughputInMibpsInput")
    def provisioned_throughput_in_mibps_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "provisionedThroughputInMibpsInput"))

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
    @jsii.member(jsii_name="throughputModeInput")
    def throughput_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "throughputModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZoneName")
    def availability_zone_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availabilityZoneName"))

    @availability_zone_name.setter
    def availability_zone_name(self, value: builtins.str) -> None:
        jsii.set(self, "availabilityZoneName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="creationToken")
    def creation_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creationToken"))

    @creation_token.setter
    def creation_token(self, value: builtins.str) -> None:
        jsii.set(self, "creationToken", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encrypted")
    def encrypted(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "encrypted"))

    @encrypted.setter
    def encrypted(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "encrypted", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @kms_key_id.setter
    def kms_key_id(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lifecyclePolicy")
    def lifecycle_policy(self) -> typing.List["EfsFileSystemLifecyclePolicy"]:
        return typing.cast(typing.List["EfsFileSystemLifecyclePolicy"], jsii.get(self, "lifecyclePolicy"))

    @lifecycle_policy.setter
    def lifecycle_policy(
        self,
        value: typing.List["EfsFileSystemLifecyclePolicy"],
    ) -> None:
        jsii.set(self, "lifecyclePolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="performanceMode")
    def performance_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "performanceMode"))

    @performance_mode.setter
    def performance_mode(self, value: builtins.str) -> None:
        jsii.set(self, "performanceMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="provisionedThroughputInMibps")
    def provisioned_throughput_in_mibps(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "provisionedThroughputInMibps"))

    @provisioned_throughput_in_mibps.setter
    def provisioned_throughput_in_mibps(self, value: jsii.Number) -> None:
        jsii.set(self, "provisionedThroughputInMibps", value)

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
    @jsii.member(jsii_name="throughputMode")
    def throughput_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "throughputMode"))

    @throughput_mode.setter
    def throughput_mode(self, value: builtins.str) -> None:
        jsii.set(self, "throughputMode", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.efs.EfsFileSystemConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "availability_zone_name": "availabilityZoneName",
        "creation_token": "creationToken",
        "encrypted": "encrypted",
        "kms_key_id": "kmsKeyId",
        "lifecycle_policy": "lifecyclePolicy",
        "performance_mode": "performanceMode",
        "provisioned_throughput_in_mibps": "provisionedThroughputInMibps",
        "tags": "tags",
        "tags_all": "tagsAll",
        "throughput_mode": "throughputMode",
    },
)
class EfsFileSystemConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        availability_zone_name: typing.Optional[builtins.str] = None,
        creation_token: typing.Optional[builtins.str] = None,
        encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        lifecycle_policy: typing.Optional[typing.Sequence["EfsFileSystemLifecyclePolicy"]] = None,
        performance_mode: typing.Optional[builtins.str] = None,
        provisioned_throughput_in_mibps: typing.Optional[jsii.Number] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        throughput_mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS EFS.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param availability_zone_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#availability_zone_name EfsFileSystem#availability_zone_name}.
        :param creation_token: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#creation_token EfsFileSystem#creation_token}.
        :param encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#encrypted EfsFileSystem#encrypted}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#kms_key_id EfsFileSystem#kms_key_id}.
        :param lifecycle_policy: lifecycle_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#lifecycle_policy EfsFileSystem#lifecycle_policy}
        :param performance_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#performance_mode EfsFileSystem#performance_mode}.
        :param provisioned_throughput_in_mibps: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#provisioned_throughput_in_mibps EfsFileSystem#provisioned_throughput_in_mibps}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#tags EfsFileSystem#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#tags_all EfsFileSystem#tags_all}.
        :param throughput_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#throughput_mode EfsFileSystem#throughput_mode}.
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
        if availability_zone_name is not None:
            self._values["availability_zone_name"] = availability_zone_name
        if creation_token is not None:
            self._values["creation_token"] = creation_token
        if encrypted is not None:
            self._values["encrypted"] = encrypted
        if kms_key_id is not None:
            self._values["kms_key_id"] = kms_key_id
        if lifecycle_policy is not None:
            self._values["lifecycle_policy"] = lifecycle_policy
        if performance_mode is not None:
            self._values["performance_mode"] = performance_mode
        if provisioned_throughput_in_mibps is not None:
            self._values["provisioned_throughput_in_mibps"] = provisioned_throughput_in_mibps
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if throughput_mode is not None:
            self._values["throughput_mode"] = throughput_mode

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
    def availability_zone_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#availability_zone_name EfsFileSystem#availability_zone_name}.'''
        result = self._values.get("availability_zone_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def creation_token(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#creation_token EfsFileSystem#creation_token}.'''
        result = self._values.get("creation_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encrypted(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#encrypted EfsFileSystem#encrypted}.'''
        result = self._values.get("encrypted")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#kms_key_id EfsFileSystem#kms_key_id}.'''
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lifecycle_policy(
        self,
    ) -> typing.Optional[typing.List["EfsFileSystemLifecyclePolicy"]]:
        '''lifecycle_policy block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#lifecycle_policy EfsFileSystem#lifecycle_policy}
        '''
        result = self._values.get("lifecycle_policy")
        return typing.cast(typing.Optional[typing.List["EfsFileSystemLifecyclePolicy"]], result)

    @builtins.property
    def performance_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#performance_mode EfsFileSystem#performance_mode}.'''
        result = self._values.get("performance_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def provisioned_throughput_in_mibps(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#provisioned_throughput_in_mibps EfsFileSystem#provisioned_throughput_in_mibps}.'''
        result = self._values.get("provisioned_throughput_in_mibps")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#tags EfsFileSystem#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#tags_all EfsFileSystem#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def throughput_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#throughput_mode EfsFileSystem#throughput_mode}.'''
        result = self._values.get("throughput_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EfsFileSystemConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.efs.EfsFileSystemLifecyclePolicy",
    jsii_struct_bases=[],
    name_mapping={
        "transition_to_ia": "transitionToIa",
        "transition_to_primary_storage_class": "transitionToPrimaryStorageClass",
    },
)
class EfsFileSystemLifecyclePolicy:
    def __init__(
        self,
        *,
        transition_to_ia: typing.Optional[builtins.str] = None,
        transition_to_primary_storage_class: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param transition_to_ia: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#transition_to_ia EfsFileSystem#transition_to_ia}.
        :param transition_to_primary_storage_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#transition_to_primary_storage_class EfsFileSystem#transition_to_primary_storage_class}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if transition_to_ia is not None:
            self._values["transition_to_ia"] = transition_to_ia
        if transition_to_primary_storage_class is not None:
            self._values["transition_to_primary_storage_class"] = transition_to_primary_storage_class

    @builtins.property
    def transition_to_ia(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#transition_to_ia EfsFileSystem#transition_to_ia}.'''
        result = self._values.get("transition_to_ia")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def transition_to_primary_storage_class(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system#transition_to_primary_storage_class EfsFileSystem#transition_to_primary_storage_class}.'''
        result = self._values.get("transition_to_primary_storage_class")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EfsFileSystemLifecyclePolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EfsFileSystemPolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.efs.EfsFileSystemPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system_policy aws_efs_file_system_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        file_system_id: builtins.str,
        policy: builtins.str,
        bypass_policy_lockout_safety_check: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system_policy aws_efs_file_system_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param file_system_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system_policy#file_system_id EfsFileSystemPolicy#file_system_id}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system_policy#policy EfsFileSystemPolicy#policy}.
        :param bypass_policy_lockout_safety_check: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system_policy#bypass_policy_lockout_safety_check EfsFileSystemPolicy#bypass_policy_lockout_safety_check}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = EfsFileSystemPolicyConfig(
            file_system_id=file_system_id,
            policy=policy,
            bypass_policy_lockout_safety_check=bypass_policy_lockout_safety_check,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetBypassPolicyLockoutSafetyCheck")
    def reset_bypass_policy_lockout_safety_check(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBypassPolicyLockoutSafetyCheck", []))

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
    @jsii.member(jsii_name="bypassPolicyLockoutSafetyCheckInput")
    def bypass_policy_lockout_safety_check_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "bypassPolicyLockoutSafetyCheckInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemIdInput")
    def file_system_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fileSystemIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyInput")
    def policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bypassPolicyLockoutSafetyCheck")
    def bypass_policy_lockout_safety_check(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "bypassPolicyLockoutSafetyCheck"))

    @bypass_policy_lockout_safety_check.setter
    def bypass_policy_lockout_safety_check(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "bypassPolicyLockoutSafetyCheck", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemId")
    def file_system_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileSystemId"))

    @file_system_id.setter
    def file_system_id(self, value: builtins.str) -> None:
        jsii.set(self, "fileSystemId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: builtins.str) -> None:
        jsii.set(self, "policy", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.efs.EfsFileSystemPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "file_system_id": "fileSystemId",
        "policy": "policy",
        "bypass_policy_lockout_safety_check": "bypassPolicyLockoutSafetyCheck",
    },
)
class EfsFileSystemPolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        file_system_id: builtins.str,
        policy: builtins.str,
        bypass_policy_lockout_safety_check: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS EFS.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param file_system_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system_policy#file_system_id EfsFileSystemPolicy#file_system_id}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system_policy#policy EfsFileSystemPolicy#policy}.
        :param bypass_policy_lockout_safety_check: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system_policy#bypass_policy_lockout_safety_check EfsFileSystemPolicy#bypass_policy_lockout_safety_check}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "file_system_id": file_system_id,
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
        if bypass_policy_lockout_safety_check is not None:
            self._values["bypass_policy_lockout_safety_check"] = bypass_policy_lockout_safety_check

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
    def file_system_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system_policy#file_system_id EfsFileSystemPolicy#file_system_id}.'''
        result = self._values.get("file_system_id")
        assert result is not None, "Required property 'file_system_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system_policy#policy EfsFileSystemPolicy#policy}.'''
        result = self._values.get("policy")
        assert result is not None, "Required property 'policy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bypass_policy_lockout_safety_check(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_file_system_policy#bypass_policy_lockout_safety_check EfsFileSystemPolicy#bypass_policy_lockout_safety_check}.'''
        result = self._values.get("bypass_policy_lockout_safety_check")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EfsFileSystemPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EfsFileSystemSizeInBytes(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.efs.EfsFileSystemSizeInBytes",
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
    @jsii.member(jsii_name="value")
    def value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "value"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInIa")
    def value_in_ia(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "valueInIa"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInStandard")
    def value_in_standard(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "valueInStandard"))


class EfsMountTarget(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.efs.EfsMountTarget",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/efs_mount_target aws_efs_mount_target}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        file_system_id: builtins.str,
        subnet_id: builtins.str,
        ip_address: typing.Optional[builtins.str] = None,
        security_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/efs_mount_target aws_efs_mount_target} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param file_system_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_mount_target#file_system_id EfsMountTarget#file_system_id}.
        :param subnet_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_mount_target#subnet_id EfsMountTarget#subnet_id}.
        :param ip_address: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_mount_target#ip_address EfsMountTarget#ip_address}.
        :param security_groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_mount_target#security_groups EfsMountTarget#security_groups}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = EfsMountTargetConfig(
            file_system_id=file_system_id,
            subnet_id=subnet_id,
            ip_address=ip_address,
            security_groups=security_groups,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetIpAddress")
    def reset_ip_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpAddress", []))

    @jsii.member(jsii_name="resetSecurityGroups")
    def reset_security_groups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityGroups", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZoneId")
    def availability_zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availabilityZoneId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZoneName")
    def availability_zone_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availabilityZoneName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsName")
    def dns_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dnsName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemArn")
    def file_system_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileSystemArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mountTargetDnsName")
    def mount_target_dns_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mountTargetDnsName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkInterfaceId")
    def network_interface_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkInterfaceId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerId")
    def owner_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ownerId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemIdInput")
    def file_system_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fileSystemIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipAddressInput")
    def ip_address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipAddressInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupsInput")
    def security_groups_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetIdInput")
    def subnet_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subnetIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemId")
    def file_system_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileSystemId"))

    @file_system_id.setter
    def file_system_id(self, value: builtins.str) -> None:
        jsii.set(self, "fileSystemId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipAddress")
    def ip_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipAddress"))

    @ip_address.setter
    def ip_address(self, value: builtins.str) -> None:
        jsii.set(self, "ipAddress", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroups")
    def security_groups(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroups"))

    @security_groups.setter
    def security_groups(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "securityGroups", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetId")
    def subnet_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subnetId"))

    @subnet_id.setter
    def subnet_id(self, value: builtins.str) -> None:
        jsii.set(self, "subnetId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.efs.EfsMountTargetConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "file_system_id": "fileSystemId",
        "subnet_id": "subnetId",
        "ip_address": "ipAddress",
        "security_groups": "securityGroups",
    },
)
class EfsMountTargetConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        file_system_id: builtins.str,
        subnet_id: builtins.str,
        ip_address: typing.Optional[builtins.str] = None,
        security_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''AWS EFS.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param file_system_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_mount_target#file_system_id EfsMountTarget#file_system_id}.
        :param subnet_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_mount_target#subnet_id EfsMountTarget#subnet_id}.
        :param ip_address: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_mount_target#ip_address EfsMountTarget#ip_address}.
        :param security_groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_mount_target#security_groups EfsMountTarget#security_groups}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "file_system_id": file_system_id,
            "subnet_id": subnet_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if ip_address is not None:
            self._values["ip_address"] = ip_address
        if security_groups is not None:
            self._values["security_groups"] = security_groups

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
    def file_system_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_mount_target#file_system_id EfsMountTarget#file_system_id}.'''
        result = self._values.get("file_system_id")
        assert result is not None, "Required property 'file_system_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subnet_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_mount_target#subnet_id EfsMountTarget#subnet_id}.'''
        result = self._values.get("subnet_id")
        assert result is not None, "Required property 'subnet_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ip_address(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_mount_target#ip_address EfsMountTarget#ip_address}.'''
        result = self._values.get("ip_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_groups(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/efs_mount_target#security_groups EfsMountTarget#security_groups}.'''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EfsMountTargetConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataAwsEfsAccessPoint",
    "DataAwsEfsAccessPointConfig",
    "DataAwsEfsAccessPointPosixUser",
    "DataAwsEfsAccessPointRootDirectory",
    "DataAwsEfsAccessPointRootDirectoryCreationInfo",
    "DataAwsEfsAccessPoints",
    "DataAwsEfsAccessPointsConfig",
    "DataAwsEfsFileSystem",
    "DataAwsEfsFileSystemConfig",
    "DataAwsEfsFileSystemLifecyclePolicy",
    "DataAwsEfsMountTarget",
    "DataAwsEfsMountTargetConfig",
    "EfsAccessPoint",
    "EfsAccessPointConfig",
    "EfsAccessPointPosixUser",
    "EfsAccessPointPosixUserOutputReference",
    "EfsAccessPointRootDirectory",
    "EfsAccessPointRootDirectoryCreationInfo",
    "EfsAccessPointRootDirectoryCreationInfoOutputReference",
    "EfsAccessPointRootDirectoryOutputReference",
    "EfsBackupPolicy",
    "EfsBackupPolicyBackupPolicy",
    "EfsBackupPolicyBackupPolicyOutputReference",
    "EfsBackupPolicyConfig",
    "EfsFileSystem",
    "EfsFileSystemConfig",
    "EfsFileSystemLifecyclePolicy",
    "EfsFileSystemPolicy",
    "EfsFileSystemPolicyConfig",
    "EfsFileSystemSizeInBytes",
    "EfsMountTarget",
    "EfsMountTargetConfig",
]

publication.publish()
