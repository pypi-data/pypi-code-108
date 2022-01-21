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


class FsxBackup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxBackup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/fsx_backup aws_fsx_backup}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        file_system_id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["FsxBackupTimeouts"] = None,
        volume_id: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/fsx_backup aws_fsx_backup} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param file_system_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_backup#file_system_id FsxBackup#file_system_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_backup#tags FsxBackup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_backup#tags_all FsxBackup#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_backup#timeouts FsxBackup#timeouts}
        :param volume_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_backup#volume_id FsxBackup#volume_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = FsxBackupConfig(
            file_system_id=file_system_id,
            tags=tags,
            tags_all=tags_all,
            timeouts=timeouts,
            volume_id=volume_id,
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
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_backup#create FsxBackup#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_backup#delete FsxBackup#delete}.
        '''
        value = FsxBackupTimeouts(create=create, delete=delete)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetFileSystemId")
    def reset_file_system_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFileSystemId", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="resetVolumeId")
    def reset_volume_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVolumeId", []))

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
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerId")
    def owner_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ownerId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "FsxBackupTimeoutsOutputReference":
        return typing.cast("FsxBackupTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemIdInput")
    def file_system_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fileSystemIdInput"))

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
    def timeouts_input(self) -> typing.Optional["FsxBackupTimeouts"]:
        return typing.cast(typing.Optional["FsxBackupTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeIdInput")
    def volume_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "volumeIdInput"))

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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeId")
    def volume_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "volumeId"))

    @volume_id.setter
    def volume_id(self, value: builtins.str) -> None:
        jsii.set(self, "volumeId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fsx.FsxBackupConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "file_system_id": "fileSystemId",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
        "volume_id": "volumeId",
    },
)
class FsxBackupConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        file_system_id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["FsxBackupTimeouts"] = None,
        volume_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS File System FSx.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param file_system_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_backup#file_system_id FsxBackup#file_system_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_backup#tags FsxBackup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_backup#tags_all FsxBackup#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_backup#timeouts FsxBackup#timeouts}
        :param volume_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_backup#volume_id FsxBackup#volume_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = FsxBackupTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if file_system_id is not None:
            self._values["file_system_id"] = file_system_id
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if timeouts is not None:
            self._values["timeouts"] = timeouts
        if volume_id is not None:
            self._values["volume_id"] = volume_id

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
    def file_system_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_backup#file_system_id FsxBackup#file_system_id}.'''
        result = self._values.get("file_system_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_backup#tags FsxBackup#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_backup#tags_all FsxBackup#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["FsxBackupTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_backup#timeouts FsxBackup#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["FsxBackupTimeouts"], result)

    @builtins.property
    def volume_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_backup#volume_id FsxBackup#volume_id}.'''
        result = self._values.get("volume_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxBackupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fsx.FsxBackupTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete"},
)
class FsxBackupTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_backup#create FsxBackup#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_backup#delete FsxBackup#delete}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_backup#create FsxBackup#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_backup#delete FsxBackup#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxBackupTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FsxBackupTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxBackupTimeoutsOutputReference",
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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

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
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[FsxBackupTimeouts]:
        return typing.cast(typing.Optional[FsxBackupTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[FsxBackupTimeouts]) -> None:
        jsii.set(self, "internalValue", value)


class FsxLustreFileSystem(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxLustreFileSystem",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system aws_fsx_lustre_file_system}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        subnet_ids: typing.Sequence[builtins.str],
        auto_import_policy: typing.Optional[builtins.str] = None,
        automatic_backup_retention_days: typing.Optional[jsii.Number] = None,
        backup_id: typing.Optional[builtins.str] = None,
        copy_tags_to_backups: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        daily_automatic_backup_start_time: typing.Optional[builtins.str] = None,
        data_compression_type: typing.Optional[builtins.str] = None,
        deployment_type: typing.Optional[builtins.str] = None,
        drive_cache_type: typing.Optional[builtins.str] = None,
        export_path: typing.Optional[builtins.str] = None,
        imported_file_chunk_size: typing.Optional[jsii.Number] = None,
        import_path: typing.Optional[builtins.str] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        per_unit_storage_throughput: typing.Optional[jsii.Number] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        storage_capacity: typing.Optional[jsii.Number] = None,
        storage_type: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["FsxLustreFileSystemTimeouts"] = None,
        weekly_maintenance_start_time: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system aws_fsx_lustre_file_system} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#subnet_ids FsxLustreFileSystem#subnet_ids}.
        :param auto_import_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#auto_import_policy FsxLustreFileSystem#auto_import_policy}.
        :param automatic_backup_retention_days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#automatic_backup_retention_days FsxLustreFileSystem#automatic_backup_retention_days}.
        :param backup_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#backup_id FsxLustreFileSystem#backup_id}.
        :param copy_tags_to_backups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#copy_tags_to_backups FsxLustreFileSystem#copy_tags_to_backups}.
        :param daily_automatic_backup_start_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#daily_automatic_backup_start_time FsxLustreFileSystem#daily_automatic_backup_start_time}.
        :param data_compression_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#data_compression_type FsxLustreFileSystem#data_compression_type}.
        :param deployment_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#deployment_type FsxLustreFileSystem#deployment_type}.
        :param drive_cache_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#drive_cache_type FsxLustreFileSystem#drive_cache_type}.
        :param export_path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#export_path FsxLustreFileSystem#export_path}.
        :param imported_file_chunk_size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#imported_file_chunk_size FsxLustreFileSystem#imported_file_chunk_size}.
        :param import_path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#import_path FsxLustreFileSystem#import_path}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#kms_key_id FsxLustreFileSystem#kms_key_id}.
        :param per_unit_storage_throughput: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#per_unit_storage_throughput FsxLustreFileSystem#per_unit_storage_throughput}.
        :param security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#security_group_ids FsxLustreFileSystem#security_group_ids}.
        :param storage_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#storage_capacity FsxLustreFileSystem#storage_capacity}.
        :param storage_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#storage_type FsxLustreFileSystem#storage_type}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#tags FsxLustreFileSystem#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#tags_all FsxLustreFileSystem#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#timeouts FsxLustreFileSystem#timeouts}
        :param weekly_maintenance_start_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#weekly_maintenance_start_time FsxLustreFileSystem#weekly_maintenance_start_time}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = FsxLustreFileSystemConfig(
            subnet_ids=subnet_ids,
            auto_import_policy=auto_import_policy,
            automatic_backup_retention_days=automatic_backup_retention_days,
            backup_id=backup_id,
            copy_tags_to_backups=copy_tags_to_backups,
            daily_automatic_backup_start_time=daily_automatic_backup_start_time,
            data_compression_type=data_compression_type,
            deployment_type=deployment_type,
            drive_cache_type=drive_cache_type,
            export_path=export_path,
            imported_file_chunk_size=imported_file_chunk_size,
            import_path=import_path,
            kms_key_id=kms_key_id,
            per_unit_storage_throughput=per_unit_storage_throughput,
            security_group_ids=security_group_ids,
            storage_capacity=storage_capacity,
            storage_type=storage_type,
            tags=tags,
            tags_all=tags_all,
            timeouts=timeouts,
            weekly_maintenance_start_time=weekly_maintenance_start_time,
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
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#create FsxLustreFileSystem#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#delete FsxLustreFileSystem#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#update FsxLustreFileSystem#update}.
        '''
        value = FsxLustreFileSystemTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetAutoImportPolicy")
    def reset_auto_import_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoImportPolicy", []))

    @jsii.member(jsii_name="resetAutomaticBackupRetentionDays")
    def reset_automatic_backup_retention_days(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutomaticBackupRetentionDays", []))

    @jsii.member(jsii_name="resetBackupId")
    def reset_backup_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackupId", []))

    @jsii.member(jsii_name="resetCopyTagsToBackups")
    def reset_copy_tags_to_backups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCopyTagsToBackups", []))

    @jsii.member(jsii_name="resetDailyAutomaticBackupStartTime")
    def reset_daily_automatic_backup_start_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDailyAutomaticBackupStartTime", []))

    @jsii.member(jsii_name="resetDataCompressionType")
    def reset_data_compression_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataCompressionType", []))

    @jsii.member(jsii_name="resetDeploymentType")
    def reset_deployment_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeploymentType", []))

    @jsii.member(jsii_name="resetDriveCacheType")
    def reset_drive_cache_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDriveCacheType", []))

    @jsii.member(jsii_name="resetExportPath")
    def reset_export_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExportPath", []))

    @jsii.member(jsii_name="resetImportedFileChunkSize")
    def reset_imported_file_chunk_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImportedFileChunkSize", []))

    @jsii.member(jsii_name="resetImportPath")
    def reset_import_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImportPath", []))

    @jsii.member(jsii_name="resetKmsKeyId")
    def reset_kms_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyId", []))

    @jsii.member(jsii_name="resetPerUnitStorageThroughput")
    def reset_per_unit_storage_throughput(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPerUnitStorageThroughput", []))

    @jsii.member(jsii_name="resetSecurityGroupIds")
    def reset_security_group_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityGroupIds", []))

    @jsii.member(jsii_name="resetStorageCapacity")
    def reset_storage_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageCapacity", []))

    @jsii.member(jsii_name="resetStorageType")
    def reset_storage_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageType", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="resetWeeklyMaintenanceStartTime")
    def reset_weekly_maintenance_start_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWeeklyMaintenanceStartTime", []))

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
    @jsii.member(jsii_name="dnsName")
    def dns_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dnsName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mountName")
    def mount_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mountName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkInterfaceIds")
    def network_interface_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "networkInterfaceIds"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerId")
    def owner_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ownerId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "FsxLustreFileSystemTimeoutsOutputReference":
        return typing.cast("FsxLustreFileSystemTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoImportPolicyInput")
    def auto_import_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "autoImportPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="automaticBackupRetentionDaysInput")
    def automatic_backup_retention_days_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "automaticBackupRetentionDaysInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupIdInput")
    def backup_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backupIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyTagsToBackupsInput")
    def copy_tags_to_backups_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "copyTagsToBackupsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dailyAutomaticBackupStartTimeInput")
    def daily_automatic_backup_start_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dailyAutomaticBackupStartTimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataCompressionTypeInput")
    def data_compression_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dataCompressionTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentTypeInput")
    def deployment_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deploymentTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="driveCacheTypeInput")
    def drive_cache_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "driveCacheTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="exportPathInput")
    def export_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "exportPathInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="importedFileChunkSizeInput")
    def imported_file_chunk_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "importedFileChunkSizeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="importPathInput")
    def import_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "importPathInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyIdInput")
    def kms_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="perUnitStorageThroughputInput")
    def per_unit_storage_throughput_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "perUnitStorageThroughputInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIdsInput")
    def security_group_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageCapacityInput")
    def storage_capacity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "storageCapacityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageTypeInput")
    def storage_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageTypeInput"))

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
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["FsxLustreFileSystemTimeouts"]:
        return typing.cast(typing.Optional["FsxLustreFileSystemTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="weeklyMaintenanceStartTimeInput")
    def weekly_maintenance_start_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "weeklyMaintenanceStartTimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoImportPolicy")
    def auto_import_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "autoImportPolicy"))

    @auto_import_policy.setter
    def auto_import_policy(self, value: builtins.str) -> None:
        jsii.set(self, "autoImportPolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="automaticBackupRetentionDays")
    def automatic_backup_retention_days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "automaticBackupRetentionDays"))

    @automatic_backup_retention_days.setter
    def automatic_backup_retention_days(self, value: jsii.Number) -> None:
        jsii.set(self, "automaticBackupRetentionDays", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupId")
    def backup_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backupId"))

    @backup_id.setter
    def backup_id(self, value: builtins.str) -> None:
        jsii.set(self, "backupId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyTagsToBackups")
    def copy_tags_to_backups(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "copyTagsToBackups"))

    @copy_tags_to_backups.setter
    def copy_tags_to_backups(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "copyTagsToBackups", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dailyAutomaticBackupStartTime")
    def daily_automatic_backup_start_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dailyAutomaticBackupStartTime"))

    @daily_automatic_backup_start_time.setter
    def daily_automatic_backup_start_time(self, value: builtins.str) -> None:
        jsii.set(self, "dailyAutomaticBackupStartTime", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataCompressionType")
    def data_compression_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataCompressionType"))

    @data_compression_type.setter
    def data_compression_type(self, value: builtins.str) -> None:
        jsii.set(self, "dataCompressionType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentType")
    def deployment_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deploymentType"))

    @deployment_type.setter
    def deployment_type(self, value: builtins.str) -> None:
        jsii.set(self, "deploymentType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="driveCacheType")
    def drive_cache_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "driveCacheType"))

    @drive_cache_type.setter
    def drive_cache_type(self, value: builtins.str) -> None:
        jsii.set(self, "driveCacheType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="exportPath")
    def export_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "exportPath"))

    @export_path.setter
    def export_path(self, value: builtins.str) -> None:
        jsii.set(self, "exportPath", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="importedFileChunkSize")
    def imported_file_chunk_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "importedFileChunkSize"))

    @imported_file_chunk_size.setter
    def imported_file_chunk_size(self, value: jsii.Number) -> None:
        jsii.set(self, "importedFileChunkSize", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="importPath")
    def import_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "importPath"))

    @import_path.setter
    def import_path(self, value: builtins.str) -> None:
        jsii.set(self, "importPath", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @kms_key_id.setter
    def kms_key_id(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="perUnitStorageThroughput")
    def per_unit_storage_throughput(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "perUnitStorageThroughput"))

    @per_unit_storage_throughput.setter
    def per_unit_storage_throughput(self, value: jsii.Number) -> None:
        jsii.set(self, "perUnitStorageThroughput", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroupIds"))

    @security_group_ids.setter
    def security_group_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "securityGroupIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageCapacity")
    def storage_capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "storageCapacity"))

    @storage_capacity.setter
    def storage_capacity(self, value: jsii.Number) -> None:
        jsii.set(self, "storageCapacity", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageType")
    def storage_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageType"))

    @storage_type.setter
    def storage_type(self, value: builtins.str) -> None:
        jsii.set(self, "storageType", value)

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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="weeklyMaintenanceStartTime")
    def weekly_maintenance_start_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "weeklyMaintenanceStartTime"))

    @weekly_maintenance_start_time.setter
    def weekly_maintenance_start_time(self, value: builtins.str) -> None:
        jsii.set(self, "weeklyMaintenanceStartTime", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fsx.FsxLustreFileSystemConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "subnet_ids": "subnetIds",
        "auto_import_policy": "autoImportPolicy",
        "automatic_backup_retention_days": "automaticBackupRetentionDays",
        "backup_id": "backupId",
        "copy_tags_to_backups": "copyTagsToBackups",
        "daily_automatic_backup_start_time": "dailyAutomaticBackupStartTime",
        "data_compression_type": "dataCompressionType",
        "deployment_type": "deploymentType",
        "drive_cache_type": "driveCacheType",
        "export_path": "exportPath",
        "imported_file_chunk_size": "importedFileChunkSize",
        "import_path": "importPath",
        "kms_key_id": "kmsKeyId",
        "per_unit_storage_throughput": "perUnitStorageThroughput",
        "security_group_ids": "securityGroupIds",
        "storage_capacity": "storageCapacity",
        "storage_type": "storageType",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
        "weekly_maintenance_start_time": "weeklyMaintenanceStartTime",
    },
)
class FsxLustreFileSystemConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        subnet_ids: typing.Sequence[builtins.str],
        auto_import_policy: typing.Optional[builtins.str] = None,
        automatic_backup_retention_days: typing.Optional[jsii.Number] = None,
        backup_id: typing.Optional[builtins.str] = None,
        copy_tags_to_backups: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        daily_automatic_backup_start_time: typing.Optional[builtins.str] = None,
        data_compression_type: typing.Optional[builtins.str] = None,
        deployment_type: typing.Optional[builtins.str] = None,
        drive_cache_type: typing.Optional[builtins.str] = None,
        export_path: typing.Optional[builtins.str] = None,
        imported_file_chunk_size: typing.Optional[jsii.Number] = None,
        import_path: typing.Optional[builtins.str] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        per_unit_storage_throughput: typing.Optional[jsii.Number] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        storage_capacity: typing.Optional[jsii.Number] = None,
        storage_type: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["FsxLustreFileSystemTimeouts"] = None,
        weekly_maintenance_start_time: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS File System FSx.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#subnet_ids FsxLustreFileSystem#subnet_ids}.
        :param auto_import_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#auto_import_policy FsxLustreFileSystem#auto_import_policy}.
        :param automatic_backup_retention_days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#automatic_backup_retention_days FsxLustreFileSystem#automatic_backup_retention_days}.
        :param backup_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#backup_id FsxLustreFileSystem#backup_id}.
        :param copy_tags_to_backups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#copy_tags_to_backups FsxLustreFileSystem#copy_tags_to_backups}.
        :param daily_automatic_backup_start_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#daily_automatic_backup_start_time FsxLustreFileSystem#daily_automatic_backup_start_time}.
        :param data_compression_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#data_compression_type FsxLustreFileSystem#data_compression_type}.
        :param deployment_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#deployment_type FsxLustreFileSystem#deployment_type}.
        :param drive_cache_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#drive_cache_type FsxLustreFileSystem#drive_cache_type}.
        :param export_path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#export_path FsxLustreFileSystem#export_path}.
        :param imported_file_chunk_size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#imported_file_chunk_size FsxLustreFileSystem#imported_file_chunk_size}.
        :param import_path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#import_path FsxLustreFileSystem#import_path}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#kms_key_id FsxLustreFileSystem#kms_key_id}.
        :param per_unit_storage_throughput: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#per_unit_storage_throughput FsxLustreFileSystem#per_unit_storage_throughput}.
        :param security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#security_group_ids FsxLustreFileSystem#security_group_ids}.
        :param storage_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#storage_capacity FsxLustreFileSystem#storage_capacity}.
        :param storage_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#storage_type FsxLustreFileSystem#storage_type}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#tags FsxLustreFileSystem#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#tags_all FsxLustreFileSystem#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#timeouts FsxLustreFileSystem#timeouts}
        :param weekly_maintenance_start_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#weekly_maintenance_start_time FsxLustreFileSystem#weekly_maintenance_start_time}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = FsxLustreFileSystemTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
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
        if auto_import_policy is not None:
            self._values["auto_import_policy"] = auto_import_policy
        if automatic_backup_retention_days is not None:
            self._values["automatic_backup_retention_days"] = automatic_backup_retention_days
        if backup_id is not None:
            self._values["backup_id"] = backup_id
        if copy_tags_to_backups is not None:
            self._values["copy_tags_to_backups"] = copy_tags_to_backups
        if daily_automatic_backup_start_time is not None:
            self._values["daily_automatic_backup_start_time"] = daily_automatic_backup_start_time
        if data_compression_type is not None:
            self._values["data_compression_type"] = data_compression_type
        if deployment_type is not None:
            self._values["deployment_type"] = deployment_type
        if drive_cache_type is not None:
            self._values["drive_cache_type"] = drive_cache_type
        if export_path is not None:
            self._values["export_path"] = export_path
        if imported_file_chunk_size is not None:
            self._values["imported_file_chunk_size"] = imported_file_chunk_size
        if import_path is not None:
            self._values["import_path"] = import_path
        if kms_key_id is not None:
            self._values["kms_key_id"] = kms_key_id
        if per_unit_storage_throughput is not None:
            self._values["per_unit_storage_throughput"] = per_unit_storage_throughput
        if security_group_ids is not None:
            self._values["security_group_ids"] = security_group_ids
        if storage_capacity is not None:
            self._values["storage_capacity"] = storage_capacity
        if storage_type is not None:
            self._values["storage_type"] = storage_type
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if timeouts is not None:
            self._values["timeouts"] = timeouts
        if weekly_maintenance_start_time is not None:
            self._values["weekly_maintenance_start_time"] = weekly_maintenance_start_time

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
    def subnet_ids(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#subnet_ids FsxLustreFileSystem#subnet_ids}.'''
        result = self._values.get("subnet_ids")
        assert result is not None, "Required property 'subnet_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def auto_import_policy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#auto_import_policy FsxLustreFileSystem#auto_import_policy}.'''
        result = self._values.get("auto_import_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def automatic_backup_retention_days(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#automatic_backup_retention_days FsxLustreFileSystem#automatic_backup_retention_days}.'''
        result = self._values.get("automatic_backup_retention_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def backup_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#backup_id FsxLustreFileSystem#backup_id}.'''
        result = self._values.get("backup_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def copy_tags_to_backups(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#copy_tags_to_backups FsxLustreFileSystem#copy_tags_to_backups}.'''
        result = self._values.get("copy_tags_to_backups")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def daily_automatic_backup_start_time(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#daily_automatic_backup_start_time FsxLustreFileSystem#daily_automatic_backup_start_time}.'''
        result = self._values.get("daily_automatic_backup_start_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def data_compression_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#data_compression_type FsxLustreFileSystem#data_compression_type}.'''
        result = self._values.get("data_compression_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def deployment_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#deployment_type FsxLustreFileSystem#deployment_type}.'''
        result = self._values.get("deployment_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def drive_cache_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#drive_cache_type FsxLustreFileSystem#drive_cache_type}.'''
        result = self._values.get("drive_cache_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def export_path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#export_path FsxLustreFileSystem#export_path}.'''
        result = self._values.get("export_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def imported_file_chunk_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#imported_file_chunk_size FsxLustreFileSystem#imported_file_chunk_size}.'''
        result = self._values.get("imported_file_chunk_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def import_path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#import_path FsxLustreFileSystem#import_path}.'''
        result = self._values.get("import_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#kms_key_id FsxLustreFileSystem#kms_key_id}.'''
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def per_unit_storage_throughput(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#per_unit_storage_throughput FsxLustreFileSystem#per_unit_storage_throughput}.'''
        result = self._values.get("per_unit_storage_throughput")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#security_group_ids FsxLustreFileSystem#security_group_ids}.'''
        result = self._values.get("security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def storage_capacity(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#storage_capacity FsxLustreFileSystem#storage_capacity}.'''
        result = self._values.get("storage_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def storage_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#storage_type FsxLustreFileSystem#storage_type}.'''
        result = self._values.get("storage_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#tags FsxLustreFileSystem#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#tags_all FsxLustreFileSystem#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["FsxLustreFileSystemTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#timeouts FsxLustreFileSystem#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["FsxLustreFileSystemTimeouts"], result)

    @builtins.property
    def weekly_maintenance_start_time(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#weekly_maintenance_start_time FsxLustreFileSystem#weekly_maintenance_start_time}.'''
        result = self._values.get("weekly_maintenance_start_time")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxLustreFileSystemConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fsx.FsxLustreFileSystemTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class FsxLustreFileSystemTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#create FsxLustreFileSystem#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#delete FsxLustreFileSystem#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#update FsxLustreFileSystem#update}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#create FsxLustreFileSystem#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#delete FsxLustreFileSystem#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_lustre_file_system#update FsxLustreFileSystem#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxLustreFileSystemTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FsxLustreFileSystemTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxLustreFileSystemTimeoutsOutputReference",
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
    def internal_value(self) -> typing.Optional[FsxLustreFileSystemTimeouts]:
        return typing.cast(typing.Optional[FsxLustreFileSystemTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[FsxLustreFileSystemTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


class FsxOntapFileSystem(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxOntapFileSystem",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system aws_fsx_ontap_file_system}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        deployment_type: builtins.str,
        preferred_subnet_id: builtins.str,
        subnet_ids: typing.Sequence[builtins.str],
        throughput_capacity: jsii.Number,
        automatic_backup_retention_days: typing.Optional[jsii.Number] = None,
        daily_automatic_backup_start_time: typing.Optional[builtins.str] = None,
        disk_iops_configuration: typing.Optional["FsxOntapFileSystemDiskIopsConfiguration"] = None,
        endpoint_ip_address_range: typing.Optional[builtins.str] = None,
        fsx_admin_password: typing.Optional[builtins.str] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        route_table_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        storage_capacity: typing.Optional[jsii.Number] = None,
        storage_type: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["FsxOntapFileSystemTimeouts"] = None,
        weekly_maintenance_start_time: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system aws_fsx_ontap_file_system} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param deployment_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#deployment_type FsxOntapFileSystem#deployment_type}.
        :param preferred_subnet_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#preferred_subnet_id FsxOntapFileSystem#preferred_subnet_id}.
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#subnet_ids FsxOntapFileSystem#subnet_ids}.
        :param throughput_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#throughput_capacity FsxOntapFileSystem#throughput_capacity}.
        :param automatic_backup_retention_days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#automatic_backup_retention_days FsxOntapFileSystem#automatic_backup_retention_days}.
        :param daily_automatic_backup_start_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#daily_automatic_backup_start_time FsxOntapFileSystem#daily_automatic_backup_start_time}.
        :param disk_iops_configuration: disk_iops_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#disk_iops_configuration FsxOntapFileSystem#disk_iops_configuration}
        :param endpoint_ip_address_range: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#endpoint_ip_address_range FsxOntapFileSystem#endpoint_ip_address_range}.
        :param fsx_admin_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#fsx_admin_password FsxOntapFileSystem#fsx_admin_password}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#kms_key_id FsxOntapFileSystem#kms_key_id}.
        :param route_table_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#route_table_ids FsxOntapFileSystem#route_table_ids}.
        :param security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#security_group_ids FsxOntapFileSystem#security_group_ids}.
        :param storage_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#storage_capacity FsxOntapFileSystem#storage_capacity}.
        :param storage_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#storage_type FsxOntapFileSystem#storage_type}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#tags FsxOntapFileSystem#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#tags_all FsxOntapFileSystem#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#timeouts FsxOntapFileSystem#timeouts}
        :param weekly_maintenance_start_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#weekly_maintenance_start_time FsxOntapFileSystem#weekly_maintenance_start_time}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = FsxOntapFileSystemConfig(
            deployment_type=deployment_type,
            preferred_subnet_id=preferred_subnet_id,
            subnet_ids=subnet_ids,
            throughput_capacity=throughput_capacity,
            automatic_backup_retention_days=automatic_backup_retention_days,
            daily_automatic_backup_start_time=daily_automatic_backup_start_time,
            disk_iops_configuration=disk_iops_configuration,
            endpoint_ip_address_range=endpoint_ip_address_range,
            fsx_admin_password=fsx_admin_password,
            kms_key_id=kms_key_id,
            route_table_ids=route_table_ids,
            security_group_ids=security_group_ids,
            storage_capacity=storage_capacity,
            storage_type=storage_type,
            tags=tags,
            tags_all=tags_all,
            timeouts=timeouts,
            weekly_maintenance_start_time=weekly_maintenance_start_time,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="endpoints")
    def endpoints(self, index: builtins.str) -> "FsxOntapFileSystemEndpoints":
        '''
        :param index: -
        '''
        return typing.cast("FsxOntapFileSystemEndpoints", jsii.invoke(self, "endpoints", [index]))

    @jsii.member(jsii_name="putDiskIopsConfiguration")
    def put_disk_iops_configuration(
        self,
        *,
        iops: typing.Optional[jsii.Number] = None,
        mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param iops: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#iops FsxOntapFileSystem#iops}.
        :param mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#mode FsxOntapFileSystem#mode}.
        '''
        value = FsxOntapFileSystemDiskIopsConfiguration(iops=iops, mode=mode)

        return typing.cast(None, jsii.invoke(self, "putDiskIopsConfiguration", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#create FsxOntapFileSystem#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#delete FsxOntapFileSystem#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#update FsxOntapFileSystem#update}.
        '''
        value = FsxOntapFileSystemTimeouts(create=create, delete=delete, update=update)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetAutomaticBackupRetentionDays")
    def reset_automatic_backup_retention_days(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutomaticBackupRetentionDays", []))

    @jsii.member(jsii_name="resetDailyAutomaticBackupStartTime")
    def reset_daily_automatic_backup_start_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDailyAutomaticBackupStartTime", []))

    @jsii.member(jsii_name="resetDiskIopsConfiguration")
    def reset_disk_iops_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiskIopsConfiguration", []))

    @jsii.member(jsii_name="resetEndpointIpAddressRange")
    def reset_endpoint_ip_address_range(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndpointIpAddressRange", []))

    @jsii.member(jsii_name="resetFsxAdminPassword")
    def reset_fsx_admin_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFsxAdminPassword", []))

    @jsii.member(jsii_name="resetKmsKeyId")
    def reset_kms_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyId", []))

    @jsii.member(jsii_name="resetRouteTableIds")
    def reset_route_table_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRouteTableIds", []))

    @jsii.member(jsii_name="resetSecurityGroupIds")
    def reset_security_group_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityGroupIds", []))

    @jsii.member(jsii_name="resetStorageCapacity")
    def reset_storage_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageCapacity", []))

    @jsii.member(jsii_name="resetStorageType")
    def reset_storage_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageType", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="resetWeeklyMaintenanceStartTime")
    def reset_weekly_maintenance_start_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWeeklyMaintenanceStartTime", []))

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
    @jsii.member(jsii_name="diskIopsConfiguration")
    def disk_iops_configuration(
        self,
    ) -> "FsxOntapFileSystemDiskIopsConfigurationOutputReference":
        return typing.cast("FsxOntapFileSystemDiskIopsConfigurationOutputReference", jsii.get(self, "diskIopsConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsName")
    def dns_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dnsName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkInterfaceIds")
    def network_interface_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "networkInterfaceIds"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerId")
    def owner_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ownerId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "FsxOntapFileSystemTimeoutsOutputReference":
        return typing.cast("FsxOntapFileSystemTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="automaticBackupRetentionDaysInput")
    def automatic_backup_retention_days_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "automaticBackupRetentionDaysInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dailyAutomaticBackupStartTimeInput")
    def daily_automatic_backup_start_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dailyAutomaticBackupStartTimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentTypeInput")
    def deployment_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deploymentTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="diskIopsConfigurationInput")
    def disk_iops_configuration_input(
        self,
    ) -> typing.Optional["FsxOntapFileSystemDiskIopsConfiguration"]:
        return typing.cast(typing.Optional["FsxOntapFileSystemDiskIopsConfiguration"], jsii.get(self, "diskIopsConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointIpAddressRangeInput")
    def endpoint_ip_address_range_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpointIpAddressRangeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fsxAdminPasswordInput")
    def fsx_admin_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fsxAdminPasswordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyIdInput")
    def kms_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredSubnetIdInput")
    def preferred_subnet_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preferredSubnetIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="routeTableIdsInput")
    def route_table_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "routeTableIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIdsInput")
    def security_group_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageCapacityInput")
    def storage_capacity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "storageCapacityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageTypeInput")
    def storage_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageTypeInput"))

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
    @jsii.member(jsii_name="throughputCapacityInput")
    def throughput_capacity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "throughputCapacityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["FsxOntapFileSystemTimeouts"]:
        return typing.cast(typing.Optional["FsxOntapFileSystemTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="weeklyMaintenanceStartTimeInput")
    def weekly_maintenance_start_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "weeklyMaintenanceStartTimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="automaticBackupRetentionDays")
    def automatic_backup_retention_days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "automaticBackupRetentionDays"))

    @automatic_backup_retention_days.setter
    def automatic_backup_retention_days(self, value: jsii.Number) -> None:
        jsii.set(self, "automaticBackupRetentionDays", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dailyAutomaticBackupStartTime")
    def daily_automatic_backup_start_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dailyAutomaticBackupStartTime"))

    @daily_automatic_backup_start_time.setter
    def daily_automatic_backup_start_time(self, value: builtins.str) -> None:
        jsii.set(self, "dailyAutomaticBackupStartTime", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentType")
    def deployment_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deploymentType"))

    @deployment_type.setter
    def deployment_type(self, value: builtins.str) -> None:
        jsii.set(self, "deploymentType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointIpAddressRange")
    def endpoint_ip_address_range(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpointIpAddressRange"))

    @endpoint_ip_address_range.setter
    def endpoint_ip_address_range(self, value: builtins.str) -> None:
        jsii.set(self, "endpointIpAddressRange", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fsxAdminPassword")
    def fsx_admin_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fsxAdminPassword"))

    @fsx_admin_password.setter
    def fsx_admin_password(self, value: builtins.str) -> None:
        jsii.set(self, "fsxAdminPassword", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @kms_key_id.setter
    def kms_key_id(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredSubnetId")
    def preferred_subnet_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preferredSubnetId"))

    @preferred_subnet_id.setter
    def preferred_subnet_id(self, value: builtins.str) -> None:
        jsii.set(self, "preferredSubnetId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="routeTableIds")
    def route_table_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "routeTableIds"))

    @route_table_ids.setter
    def route_table_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "routeTableIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroupIds"))

    @security_group_ids.setter
    def security_group_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "securityGroupIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageCapacity")
    def storage_capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "storageCapacity"))

    @storage_capacity.setter
    def storage_capacity(self, value: jsii.Number) -> None:
        jsii.set(self, "storageCapacity", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageType")
    def storage_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageType"))

    @storage_type.setter
    def storage_type(self, value: builtins.str) -> None:
        jsii.set(self, "storageType", value)

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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="throughputCapacity")
    def throughput_capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "throughputCapacity"))

    @throughput_capacity.setter
    def throughput_capacity(self, value: jsii.Number) -> None:
        jsii.set(self, "throughputCapacity", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="weeklyMaintenanceStartTime")
    def weekly_maintenance_start_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "weeklyMaintenanceStartTime"))

    @weekly_maintenance_start_time.setter
    def weekly_maintenance_start_time(self, value: builtins.str) -> None:
        jsii.set(self, "weeklyMaintenanceStartTime", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fsx.FsxOntapFileSystemConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "deployment_type": "deploymentType",
        "preferred_subnet_id": "preferredSubnetId",
        "subnet_ids": "subnetIds",
        "throughput_capacity": "throughputCapacity",
        "automatic_backup_retention_days": "automaticBackupRetentionDays",
        "daily_automatic_backup_start_time": "dailyAutomaticBackupStartTime",
        "disk_iops_configuration": "diskIopsConfiguration",
        "endpoint_ip_address_range": "endpointIpAddressRange",
        "fsx_admin_password": "fsxAdminPassword",
        "kms_key_id": "kmsKeyId",
        "route_table_ids": "routeTableIds",
        "security_group_ids": "securityGroupIds",
        "storage_capacity": "storageCapacity",
        "storage_type": "storageType",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
        "weekly_maintenance_start_time": "weeklyMaintenanceStartTime",
    },
)
class FsxOntapFileSystemConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        deployment_type: builtins.str,
        preferred_subnet_id: builtins.str,
        subnet_ids: typing.Sequence[builtins.str],
        throughput_capacity: jsii.Number,
        automatic_backup_retention_days: typing.Optional[jsii.Number] = None,
        daily_automatic_backup_start_time: typing.Optional[builtins.str] = None,
        disk_iops_configuration: typing.Optional["FsxOntapFileSystemDiskIopsConfiguration"] = None,
        endpoint_ip_address_range: typing.Optional[builtins.str] = None,
        fsx_admin_password: typing.Optional[builtins.str] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        route_table_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        storage_capacity: typing.Optional[jsii.Number] = None,
        storage_type: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["FsxOntapFileSystemTimeouts"] = None,
        weekly_maintenance_start_time: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS File System FSx.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param deployment_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#deployment_type FsxOntapFileSystem#deployment_type}.
        :param preferred_subnet_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#preferred_subnet_id FsxOntapFileSystem#preferred_subnet_id}.
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#subnet_ids FsxOntapFileSystem#subnet_ids}.
        :param throughput_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#throughput_capacity FsxOntapFileSystem#throughput_capacity}.
        :param automatic_backup_retention_days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#automatic_backup_retention_days FsxOntapFileSystem#automatic_backup_retention_days}.
        :param daily_automatic_backup_start_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#daily_automatic_backup_start_time FsxOntapFileSystem#daily_automatic_backup_start_time}.
        :param disk_iops_configuration: disk_iops_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#disk_iops_configuration FsxOntapFileSystem#disk_iops_configuration}
        :param endpoint_ip_address_range: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#endpoint_ip_address_range FsxOntapFileSystem#endpoint_ip_address_range}.
        :param fsx_admin_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#fsx_admin_password FsxOntapFileSystem#fsx_admin_password}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#kms_key_id FsxOntapFileSystem#kms_key_id}.
        :param route_table_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#route_table_ids FsxOntapFileSystem#route_table_ids}.
        :param security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#security_group_ids FsxOntapFileSystem#security_group_ids}.
        :param storage_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#storage_capacity FsxOntapFileSystem#storage_capacity}.
        :param storage_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#storage_type FsxOntapFileSystem#storage_type}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#tags FsxOntapFileSystem#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#tags_all FsxOntapFileSystem#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#timeouts FsxOntapFileSystem#timeouts}
        :param weekly_maintenance_start_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#weekly_maintenance_start_time FsxOntapFileSystem#weekly_maintenance_start_time}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(disk_iops_configuration, dict):
            disk_iops_configuration = FsxOntapFileSystemDiskIopsConfiguration(**disk_iops_configuration)
        if isinstance(timeouts, dict):
            timeouts = FsxOntapFileSystemTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "deployment_type": deployment_type,
            "preferred_subnet_id": preferred_subnet_id,
            "subnet_ids": subnet_ids,
            "throughput_capacity": throughput_capacity,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if automatic_backup_retention_days is not None:
            self._values["automatic_backup_retention_days"] = automatic_backup_retention_days
        if daily_automatic_backup_start_time is not None:
            self._values["daily_automatic_backup_start_time"] = daily_automatic_backup_start_time
        if disk_iops_configuration is not None:
            self._values["disk_iops_configuration"] = disk_iops_configuration
        if endpoint_ip_address_range is not None:
            self._values["endpoint_ip_address_range"] = endpoint_ip_address_range
        if fsx_admin_password is not None:
            self._values["fsx_admin_password"] = fsx_admin_password
        if kms_key_id is not None:
            self._values["kms_key_id"] = kms_key_id
        if route_table_ids is not None:
            self._values["route_table_ids"] = route_table_ids
        if security_group_ids is not None:
            self._values["security_group_ids"] = security_group_ids
        if storage_capacity is not None:
            self._values["storage_capacity"] = storage_capacity
        if storage_type is not None:
            self._values["storage_type"] = storage_type
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if timeouts is not None:
            self._values["timeouts"] = timeouts
        if weekly_maintenance_start_time is not None:
            self._values["weekly_maintenance_start_time"] = weekly_maintenance_start_time

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
    def deployment_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#deployment_type FsxOntapFileSystem#deployment_type}.'''
        result = self._values.get("deployment_type")
        assert result is not None, "Required property 'deployment_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def preferred_subnet_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#preferred_subnet_id FsxOntapFileSystem#preferred_subnet_id}.'''
        result = self._values.get("preferred_subnet_id")
        assert result is not None, "Required property 'preferred_subnet_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subnet_ids(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#subnet_ids FsxOntapFileSystem#subnet_ids}.'''
        result = self._values.get("subnet_ids")
        assert result is not None, "Required property 'subnet_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def throughput_capacity(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#throughput_capacity FsxOntapFileSystem#throughput_capacity}.'''
        result = self._values.get("throughput_capacity")
        assert result is not None, "Required property 'throughput_capacity' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def automatic_backup_retention_days(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#automatic_backup_retention_days FsxOntapFileSystem#automatic_backup_retention_days}.'''
        result = self._values.get("automatic_backup_retention_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def daily_automatic_backup_start_time(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#daily_automatic_backup_start_time FsxOntapFileSystem#daily_automatic_backup_start_time}.'''
        result = self._values.get("daily_automatic_backup_start_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disk_iops_configuration(
        self,
    ) -> typing.Optional["FsxOntapFileSystemDiskIopsConfiguration"]:
        '''disk_iops_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#disk_iops_configuration FsxOntapFileSystem#disk_iops_configuration}
        '''
        result = self._values.get("disk_iops_configuration")
        return typing.cast(typing.Optional["FsxOntapFileSystemDiskIopsConfiguration"], result)

    @builtins.property
    def endpoint_ip_address_range(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#endpoint_ip_address_range FsxOntapFileSystem#endpoint_ip_address_range}.'''
        result = self._values.get("endpoint_ip_address_range")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def fsx_admin_password(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#fsx_admin_password FsxOntapFileSystem#fsx_admin_password}.'''
        result = self._values.get("fsx_admin_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#kms_key_id FsxOntapFileSystem#kms_key_id}.'''
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def route_table_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#route_table_ids FsxOntapFileSystem#route_table_ids}.'''
        result = self._values.get("route_table_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#security_group_ids FsxOntapFileSystem#security_group_ids}.'''
        result = self._values.get("security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def storage_capacity(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#storage_capacity FsxOntapFileSystem#storage_capacity}.'''
        result = self._values.get("storage_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def storage_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#storage_type FsxOntapFileSystem#storage_type}.'''
        result = self._values.get("storage_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#tags FsxOntapFileSystem#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#tags_all FsxOntapFileSystem#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["FsxOntapFileSystemTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#timeouts FsxOntapFileSystem#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["FsxOntapFileSystemTimeouts"], result)

    @builtins.property
    def weekly_maintenance_start_time(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#weekly_maintenance_start_time FsxOntapFileSystem#weekly_maintenance_start_time}.'''
        result = self._values.get("weekly_maintenance_start_time")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxOntapFileSystemConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fsx.FsxOntapFileSystemDiskIopsConfiguration",
    jsii_struct_bases=[],
    name_mapping={"iops": "iops", "mode": "mode"},
)
class FsxOntapFileSystemDiskIopsConfiguration:
    def __init__(
        self,
        *,
        iops: typing.Optional[jsii.Number] = None,
        mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param iops: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#iops FsxOntapFileSystem#iops}.
        :param mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#mode FsxOntapFileSystem#mode}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if iops is not None:
            self._values["iops"] = iops
        if mode is not None:
            self._values["mode"] = mode

    @builtins.property
    def iops(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#iops FsxOntapFileSystem#iops}.'''
        result = self._values.get("iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#mode FsxOntapFileSystem#mode}.'''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxOntapFileSystemDiskIopsConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FsxOntapFileSystemDiskIopsConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxOntapFileSystemDiskIopsConfigurationOutputReference",
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

    @jsii.member(jsii_name="resetIops")
    def reset_iops(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIops", []))

    @jsii.member(jsii_name="resetMode")
    def reset_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMode", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iopsInput")
    def iops_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "iopsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="modeInput")
    def mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iops")
    def iops(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "iops"))

    @iops.setter
    def iops(self, value: jsii.Number) -> None:
        jsii.set(self, "iops", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @mode.setter
    def mode(self, value: builtins.str) -> None:
        jsii.set(self, "mode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[FsxOntapFileSystemDiskIopsConfiguration]:
        return typing.cast(typing.Optional[FsxOntapFileSystemDiskIopsConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[FsxOntapFileSystemDiskIopsConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


class FsxOntapFileSystemEndpoints(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxOntapFileSystemEndpoints",
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
    @jsii.member(jsii_name="intercluster")
    def intercluster(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "intercluster"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="management")
    def management(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "management"))


class FsxOntapFileSystemEndpointsIntercluster(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxOntapFileSystemEndpointsIntercluster",
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
    @jsii.member(jsii_name="dnsName")
    def dns_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dnsName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipAddresses")
    def ip_addresses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ipAddresses"))


class FsxOntapFileSystemEndpointsManagement(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxOntapFileSystemEndpointsManagement",
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
    @jsii.member(jsii_name="dnsName")
    def dns_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dnsName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipAddresses")
    def ip_addresses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ipAddresses"))


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fsx.FsxOntapFileSystemTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class FsxOntapFileSystemTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#create FsxOntapFileSystem#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#delete FsxOntapFileSystem#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#update FsxOntapFileSystem#update}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#create FsxOntapFileSystem#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#delete FsxOntapFileSystem#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_file_system#update FsxOntapFileSystem#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxOntapFileSystemTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FsxOntapFileSystemTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxOntapFileSystemTimeoutsOutputReference",
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
    def internal_value(self) -> typing.Optional[FsxOntapFileSystemTimeouts]:
        return typing.cast(typing.Optional[FsxOntapFileSystemTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[FsxOntapFileSystemTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


class FsxOntapStorageVirtualMachine(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxOntapStorageVirtualMachine",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine aws_fsx_ontap_storage_virtual_machine}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        file_system_id: builtins.str,
        name: builtins.str,
        active_directory_configuration: typing.Optional["FsxOntapStorageVirtualMachineActiveDirectoryConfiguration"] = None,
        root_volume_security_style: typing.Optional[builtins.str] = None,
        svm_admin_password: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["FsxOntapStorageVirtualMachineTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine aws_fsx_ontap_storage_virtual_machine} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param file_system_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#file_system_id FsxOntapStorageVirtualMachine#file_system_id}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#name FsxOntapStorageVirtualMachine#name}.
        :param active_directory_configuration: active_directory_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#active_directory_configuration FsxOntapStorageVirtualMachine#active_directory_configuration}
        :param root_volume_security_style: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#root_volume_security_style FsxOntapStorageVirtualMachine#root_volume_security_style}.
        :param svm_admin_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#svm_admin_password FsxOntapStorageVirtualMachine#svm_admin_password}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#tags FsxOntapStorageVirtualMachine#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#tags_all FsxOntapStorageVirtualMachine#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#timeouts FsxOntapStorageVirtualMachine#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = FsxOntapStorageVirtualMachineConfig(
            file_system_id=file_system_id,
            name=name,
            active_directory_configuration=active_directory_configuration,
            root_volume_security_style=root_volume_security_style,
            svm_admin_password=svm_admin_password,
            tags=tags,
            tags_all=tags_all,
            timeouts=timeouts,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="endpoints")
    def endpoints(
        self,
        index: builtins.str,
    ) -> "FsxOntapStorageVirtualMachineEndpoints":
        '''
        :param index: -
        '''
        return typing.cast("FsxOntapStorageVirtualMachineEndpoints", jsii.invoke(self, "endpoints", [index]))

    @jsii.member(jsii_name="putActiveDirectoryConfiguration")
    def put_active_directory_configuration(
        self,
        *,
        netbios_name: typing.Optional[builtins.str] = None,
        self_managed_active_directory_configuration: typing.Optional["FsxOntapStorageVirtualMachineActiveDirectoryConfigurationSelfManagedActiveDirectoryConfiguration"] = None,
    ) -> None:
        '''
        :param netbios_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#netbios_name FsxOntapStorageVirtualMachine#netbios_name}.
        :param self_managed_active_directory_configuration: self_managed_active_directory_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#self_managed_active_directory_configuration FsxOntapStorageVirtualMachine#self_managed_active_directory_configuration}
        '''
        value = FsxOntapStorageVirtualMachineActiveDirectoryConfiguration(
            netbios_name=netbios_name,
            self_managed_active_directory_configuration=self_managed_active_directory_configuration,
        )

        return typing.cast(None, jsii.invoke(self, "putActiveDirectoryConfiguration", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#create FsxOntapStorageVirtualMachine#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#delete FsxOntapStorageVirtualMachine#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#update FsxOntapStorageVirtualMachine#update}.
        '''
        value = FsxOntapStorageVirtualMachineTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetActiveDirectoryConfiguration")
    def reset_active_directory_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetActiveDirectoryConfiguration", []))

    @jsii.member(jsii_name="resetRootVolumeSecurityStyle")
    def reset_root_volume_security_style(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRootVolumeSecurityStyle", []))

    @jsii.member(jsii_name="resetSvmAdminPassword")
    def reset_svm_admin_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSvmAdminPassword", []))

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
    @jsii.member(jsii_name="activeDirectoryConfiguration")
    def active_directory_configuration(
        self,
    ) -> "FsxOntapStorageVirtualMachineActiveDirectoryConfigurationOutputReference":
        return typing.cast("FsxOntapStorageVirtualMachineActiveDirectoryConfigurationOutputReference", jsii.get(self, "activeDirectoryConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subtype")
    def subtype(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subtype"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "FsxOntapStorageVirtualMachineTimeoutsOutputReference":
        return typing.cast("FsxOntapStorageVirtualMachineTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="activeDirectoryConfigurationInput")
    def active_directory_configuration_input(
        self,
    ) -> typing.Optional["FsxOntapStorageVirtualMachineActiveDirectoryConfiguration"]:
        return typing.cast(typing.Optional["FsxOntapStorageVirtualMachineActiveDirectoryConfiguration"], jsii.get(self, "activeDirectoryConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemIdInput")
    def file_system_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fileSystemIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rootVolumeSecurityStyleInput")
    def root_volume_security_style_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rootVolumeSecurityStyleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="svmAdminPasswordInput")
    def svm_admin_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "svmAdminPasswordInput"))

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
    def timeouts_input(
        self,
    ) -> typing.Optional["FsxOntapStorageVirtualMachineTimeouts"]:
        return typing.cast(typing.Optional["FsxOntapStorageVirtualMachineTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemId")
    def file_system_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileSystemId"))

    @file_system_id.setter
    def file_system_id(self, value: builtins.str) -> None:
        jsii.set(self, "fileSystemId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rootVolumeSecurityStyle")
    def root_volume_security_style(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rootVolumeSecurityStyle"))

    @root_volume_security_style.setter
    def root_volume_security_style(self, value: builtins.str) -> None:
        jsii.set(self, "rootVolumeSecurityStyle", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="svmAdminPassword")
    def svm_admin_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "svmAdminPassword"))

    @svm_admin_password.setter
    def svm_admin_password(self, value: builtins.str) -> None:
        jsii.set(self, "svmAdminPassword", value)

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
    jsii_type="@cdktf/provider-aws.fsx.FsxOntapStorageVirtualMachineActiveDirectoryConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "netbios_name": "netbiosName",
        "self_managed_active_directory_configuration": "selfManagedActiveDirectoryConfiguration",
    },
)
class FsxOntapStorageVirtualMachineActiveDirectoryConfiguration:
    def __init__(
        self,
        *,
        netbios_name: typing.Optional[builtins.str] = None,
        self_managed_active_directory_configuration: typing.Optional["FsxOntapStorageVirtualMachineActiveDirectoryConfigurationSelfManagedActiveDirectoryConfiguration"] = None,
    ) -> None:
        '''
        :param netbios_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#netbios_name FsxOntapStorageVirtualMachine#netbios_name}.
        :param self_managed_active_directory_configuration: self_managed_active_directory_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#self_managed_active_directory_configuration FsxOntapStorageVirtualMachine#self_managed_active_directory_configuration}
        '''
        if isinstance(self_managed_active_directory_configuration, dict):
            self_managed_active_directory_configuration = FsxOntapStorageVirtualMachineActiveDirectoryConfigurationSelfManagedActiveDirectoryConfiguration(**self_managed_active_directory_configuration)
        self._values: typing.Dict[str, typing.Any] = {}
        if netbios_name is not None:
            self._values["netbios_name"] = netbios_name
        if self_managed_active_directory_configuration is not None:
            self._values["self_managed_active_directory_configuration"] = self_managed_active_directory_configuration

    @builtins.property
    def netbios_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#netbios_name FsxOntapStorageVirtualMachine#netbios_name}.'''
        result = self._values.get("netbios_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def self_managed_active_directory_configuration(
        self,
    ) -> typing.Optional["FsxOntapStorageVirtualMachineActiveDirectoryConfigurationSelfManagedActiveDirectoryConfiguration"]:
        '''self_managed_active_directory_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#self_managed_active_directory_configuration FsxOntapStorageVirtualMachine#self_managed_active_directory_configuration}
        '''
        result = self._values.get("self_managed_active_directory_configuration")
        return typing.cast(typing.Optional["FsxOntapStorageVirtualMachineActiveDirectoryConfigurationSelfManagedActiveDirectoryConfiguration"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxOntapStorageVirtualMachineActiveDirectoryConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FsxOntapStorageVirtualMachineActiveDirectoryConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxOntapStorageVirtualMachineActiveDirectoryConfigurationOutputReference",
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

    @jsii.member(jsii_name="putSelfManagedActiveDirectoryConfiguration")
    def put_self_managed_active_directory_configuration(
        self,
        *,
        dns_ips: typing.Sequence[builtins.str],
        domain_name: builtins.str,
        password: builtins.str,
        username: builtins.str,
        file_system_administrators_group: typing.Optional[builtins.str] = None,
        organizational_unit_distinguidshed_name: typing.Optional[builtins.str] = None,
        organizational_unit_distinguished_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dns_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#dns_ips FsxOntapStorageVirtualMachine#dns_ips}.
        :param domain_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#domain_name FsxOntapStorageVirtualMachine#domain_name}.
        :param password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#password FsxOntapStorageVirtualMachine#password}.
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#username FsxOntapStorageVirtualMachine#username}.
        :param file_system_administrators_group: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#file_system_administrators_group FsxOntapStorageVirtualMachine#file_system_administrators_group}.
        :param organizational_unit_distinguidshed_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#organizational_unit_distinguidshed_name FsxOntapStorageVirtualMachine#organizational_unit_distinguidshed_name}.
        :param organizational_unit_distinguished_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#organizational_unit_distinguished_name FsxOntapStorageVirtualMachine#organizational_unit_distinguished_name}.
        '''
        value = FsxOntapStorageVirtualMachineActiveDirectoryConfigurationSelfManagedActiveDirectoryConfiguration(
            dns_ips=dns_ips,
            domain_name=domain_name,
            password=password,
            username=username,
            file_system_administrators_group=file_system_administrators_group,
            organizational_unit_distinguidshed_name=organizational_unit_distinguidshed_name,
            organizational_unit_distinguished_name=organizational_unit_distinguished_name,
        )

        return typing.cast(None, jsii.invoke(self, "putSelfManagedActiveDirectoryConfiguration", [value]))

    @jsii.member(jsii_name="resetNetbiosName")
    def reset_netbios_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetbiosName", []))

    @jsii.member(jsii_name="resetSelfManagedActiveDirectoryConfiguration")
    def reset_self_managed_active_directory_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSelfManagedActiveDirectoryConfiguration", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="selfManagedActiveDirectoryConfiguration")
    def self_managed_active_directory_configuration(
        self,
    ) -> "FsxOntapStorageVirtualMachineActiveDirectoryConfigurationSelfManagedActiveDirectoryConfigurationOutputReference":
        return typing.cast("FsxOntapStorageVirtualMachineActiveDirectoryConfigurationSelfManagedActiveDirectoryConfigurationOutputReference", jsii.get(self, "selfManagedActiveDirectoryConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="netbiosNameInput")
    def netbios_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "netbiosNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="selfManagedActiveDirectoryConfigurationInput")
    def self_managed_active_directory_configuration_input(
        self,
    ) -> typing.Optional["FsxOntapStorageVirtualMachineActiveDirectoryConfigurationSelfManagedActiveDirectoryConfiguration"]:
        return typing.cast(typing.Optional["FsxOntapStorageVirtualMachineActiveDirectoryConfigurationSelfManagedActiveDirectoryConfiguration"], jsii.get(self, "selfManagedActiveDirectoryConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="netbiosName")
    def netbios_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "netbiosName"))

    @netbios_name.setter
    def netbios_name(self, value: builtins.str) -> None:
        jsii.set(self, "netbiosName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[FsxOntapStorageVirtualMachineActiveDirectoryConfiguration]:
        return typing.cast(typing.Optional[FsxOntapStorageVirtualMachineActiveDirectoryConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[FsxOntapStorageVirtualMachineActiveDirectoryConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fsx.FsxOntapStorageVirtualMachineActiveDirectoryConfigurationSelfManagedActiveDirectoryConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "dns_ips": "dnsIps",
        "domain_name": "domainName",
        "password": "password",
        "username": "username",
        "file_system_administrators_group": "fileSystemAdministratorsGroup",
        "organizational_unit_distinguidshed_name": "organizationalUnitDistinguidshedName",
        "organizational_unit_distinguished_name": "organizationalUnitDistinguishedName",
    },
)
class FsxOntapStorageVirtualMachineActiveDirectoryConfigurationSelfManagedActiveDirectoryConfiguration:
    def __init__(
        self,
        *,
        dns_ips: typing.Sequence[builtins.str],
        domain_name: builtins.str,
        password: builtins.str,
        username: builtins.str,
        file_system_administrators_group: typing.Optional[builtins.str] = None,
        organizational_unit_distinguidshed_name: typing.Optional[builtins.str] = None,
        organizational_unit_distinguished_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dns_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#dns_ips FsxOntapStorageVirtualMachine#dns_ips}.
        :param domain_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#domain_name FsxOntapStorageVirtualMachine#domain_name}.
        :param password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#password FsxOntapStorageVirtualMachine#password}.
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#username FsxOntapStorageVirtualMachine#username}.
        :param file_system_administrators_group: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#file_system_administrators_group FsxOntapStorageVirtualMachine#file_system_administrators_group}.
        :param organizational_unit_distinguidshed_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#organizational_unit_distinguidshed_name FsxOntapStorageVirtualMachine#organizational_unit_distinguidshed_name}.
        :param organizational_unit_distinguished_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#organizational_unit_distinguished_name FsxOntapStorageVirtualMachine#organizational_unit_distinguished_name}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "dns_ips": dns_ips,
            "domain_name": domain_name,
            "password": password,
            "username": username,
        }
        if file_system_administrators_group is not None:
            self._values["file_system_administrators_group"] = file_system_administrators_group
        if organizational_unit_distinguidshed_name is not None:
            self._values["organizational_unit_distinguidshed_name"] = organizational_unit_distinguidshed_name
        if organizational_unit_distinguished_name is not None:
            self._values["organizational_unit_distinguished_name"] = organizational_unit_distinguished_name

    @builtins.property
    def dns_ips(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#dns_ips FsxOntapStorageVirtualMachine#dns_ips}.'''
        result = self._values.get("dns_ips")
        assert result is not None, "Required property 'dns_ips' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def domain_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#domain_name FsxOntapStorageVirtualMachine#domain_name}.'''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def password(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#password FsxOntapStorageVirtualMachine#password}.'''
        result = self._values.get("password")
        assert result is not None, "Required property 'password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#username FsxOntapStorageVirtualMachine#username}.'''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def file_system_administrators_group(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#file_system_administrators_group FsxOntapStorageVirtualMachine#file_system_administrators_group}.'''
        result = self._values.get("file_system_administrators_group")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def organizational_unit_distinguidshed_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#organizational_unit_distinguidshed_name FsxOntapStorageVirtualMachine#organizational_unit_distinguidshed_name}.'''
        result = self._values.get("organizational_unit_distinguidshed_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def organizational_unit_distinguished_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#organizational_unit_distinguished_name FsxOntapStorageVirtualMachine#organizational_unit_distinguished_name}.'''
        result = self._values.get("organizational_unit_distinguished_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxOntapStorageVirtualMachineActiveDirectoryConfigurationSelfManagedActiveDirectoryConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FsxOntapStorageVirtualMachineActiveDirectoryConfigurationSelfManagedActiveDirectoryConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxOntapStorageVirtualMachineActiveDirectoryConfigurationSelfManagedActiveDirectoryConfigurationOutputReference",
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

    @jsii.member(jsii_name="resetFileSystemAdministratorsGroup")
    def reset_file_system_administrators_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFileSystemAdministratorsGroup", []))

    @jsii.member(jsii_name="resetOrganizationalUnitDistinguidshedName")
    def reset_organizational_unit_distinguidshed_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrganizationalUnitDistinguidshedName", []))

    @jsii.member(jsii_name="resetOrganizationalUnitDistinguishedName")
    def reset_organizational_unit_distinguished_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrganizationalUnitDistinguishedName", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsIpsInput")
    def dns_ips_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "dnsIpsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainNameInput")
    def domain_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemAdministratorsGroupInput")
    def file_system_administrators_group_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fileSystemAdministratorsGroupInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitDistinguidshedNameInput")
    def organizational_unit_distinguidshed_name_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "organizationalUnitDistinguidshedNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitDistinguishedNameInput")
    def organizational_unit_distinguished_name_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "organizationalUnitDistinguishedNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsIps")
    def dns_ips(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dnsIps"))

    @dns_ips.setter
    def dns_ips(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "dnsIps", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @domain_name.setter
    def domain_name(self, value: builtins.str) -> None:
        jsii.set(self, "domainName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemAdministratorsGroup")
    def file_system_administrators_group(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileSystemAdministratorsGroup"))

    @file_system_administrators_group.setter
    def file_system_administrators_group(self, value: builtins.str) -> None:
        jsii.set(self, "fileSystemAdministratorsGroup", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitDistinguidshedName")
    def organizational_unit_distinguidshed_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "organizationalUnitDistinguidshedName"))

    @organizational_unit_distinguidshed_name.setter
    def organizational_unit_distinguidshed_name(self, value: builtins.str) -> None:
        jsii.set(self, "organizationalUnitDistinguidshedName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitDistinguishedName")
    def organizational_unit_distinguished_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "organizationalUnitDistinguishedName"))

    @organizational_unit_distinguished_name.setter
    def organizational_unit_distinguished_name(self, value: builtins.str) -> None:
        jsii.set(self, "organizationalUnitDistinguishedName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        jsii.set(self, "password", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        jsii.set(self, "username", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[FsxOntapStorageVirtualMachineActiveDirectoryConfigurationSelfManagedActiveDirectoryConfiguration]:
        return typing.cast(typing.Optional[FsxOntapStorageVirtualMachineActiveDirectoryConfigurationSelfManagedActiveDirectoryConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[FsxOntapStorageVirtualMachineActiveDirectoryConfigurationSelfManagedActiveDirectoryConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fsx.FsxOntapStorageVirtualMachineConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "file_system_id": "fileSystemId",
        "name": "name",
        "active_directory_configuration": "activeDirectoryConfiguration",
        "root_volume_security_style": "rootVolumeSecurityStyle",
        "svm_admin_password": "svmAdminPassword",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
    },
)
class FsxOntapStorageVirtualMachineConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        file_system_id: builtins.str,
        name: builtins.str,
        active_directory_configuration: typing.Optional[FsxOntapStorageVirtualMachineActiveDirectoryConfiguration] = None,
        root_volume_security_style: typing.Optional[builtins.str] = None,
        svm_admin_password: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["FsxOntapStorageVirtualMachineTimeouts"] = None,
    ) -> None:
        '''AWS File System FSx.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param file_system_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#file_system_id FsxOntapStorageVirtualMachine#file_system_id}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#name FsxOntapStorageVirtualMachine#name}.
        :param active_directory_configuration: active_directory_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#active_directory_configuration FsxOntapStorageVirtualMachine#active_directory_configuration}
        :param root_volume_security_style: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#root_volume_security_style FsxOntapStorageVirtualMachine#root_volume_security_style}.
        :param svm_admin_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#svm_admin_password FsxOntapStorageVirtualMachine#svm_admin_password}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#tags FsxOntapStorageVirtualMachine#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#tags_all FsxOntapStorageVirtualMachine#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#timeouts FsxOntapStorageVirtualMachine#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(active_directory_configuration, dict):
            active_directory_configuration = FsxOntapStorageVirtualMachineActiveDirectoryConfiguration(**active_directory_configuration)
        if isinstance(timeouts, dict):
            timeouts = FsxOntapStorageVirtualMachineTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "file_system_id": file_system_id,
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
        if active_directory_configuration is not None:
            self._values["active_directory_configuration"] = active_directory_configuration
        if root_volume_security_style is not None:
            self._values["root_volume_security_style"] = root_volume_security_style
        if svm_admin_password is not None:
            self._values["svm_admin_password"] = svm_admin_password
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
    def file_system_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#file_system_id FsxOntapStorageVirtualMachine#file_system_id}.'''
        result = self._values.get("file_system_id")
        assert result is not None, "Required property 'file_system_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#name FsxOntapStorageVirtualMachine#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def active_directory_configuration(
        self,
    ) -> typing.Optional[FsxOntapStorageVirtualMachineActiveDirectoryConfiguration]:
        '''active_directory_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#active_directory_configuration FsxOntapStorageVirtualMachine#active_directory_configuration}
        '''
        result = self._values.get("active_directory_configuration")
        return typing.cast(typing.Optional[FsxOntapStorageVirtualMachineActiveDirectoryConfiguration], result)

    @builtins.property
    def root_volume_security_style(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#root_volume_security_style FsxOntapStorageVirtualMachine#root_volume_security_style}.'''
        result = self._values.get("root_volume_security_style")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def svm_admin_password(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#svm_admin_password FsxOntapStorageVirtualMachine#svm_admin_password}.'''
        result = self._values.get("svm_admin_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#tags FsxOntapStorageVirtualMachine#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#tags_all FsxOntapStorageVirtualMachine#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["FsxOntapStorageVirtualMachineTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#timeouts FsxOntapStorageVirtualMachine#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["FsxOntapStorageVirtualMachineTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxOntapStorageVirtualMachineConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FsxOntapStorageVirtualMachineEndpoints(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxOntapStorageVirtualMachineEndpoints",
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
    @jsii.member(jsii_name="iscsi")
    def iscsi(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "iscsi"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="management")
    def management(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "management"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nfs")
    def nfs(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "nfs"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="smb")
    def smb(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "smb"))


class FsxOntapStorageVirtualMachineEndpointsIscsi(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxOntapStorageVirtualMachineEndpointsIscsi",
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
    @jsii.member(jsii_name="dnsName")
    def dns_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dnsName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipAddresses")
    def ip_addresses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ipAddresses"))


class FsxOntapStorageVirtualMachineEndpointsManagement(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxOntapStorageVirtualMachineEndpointsManagement",
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
    @jsii.member(jsii_name="dnsName")
    def dns_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dnsName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipAddresses")
    def ip_addresses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ipAddresses"))


class FsxOntapStorageVirtualMachineEndpointsNfs(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxOntapStorageVirtualMachineEndpointsNfs",
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
    @jsii.member(jsii_name="dnsName")
    def dns_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dnsName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipAddresses")
    def ip_addresses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ipAddresses"))


class FsxOntapStorageVirtualMachineEndpointsSmb(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxOntapStorageVirtualMachineEndpointsSmb",
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
    @jsii.member(jsii_name="dnsName")
    def dns_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dnsName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipAddresses")
    def ip_addresses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ipAddresses"))


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fsx.FsxOntapStorageVirtualMachineTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class FsxOntapStorageVirtualMachineTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#create FsxOntapStorageVirtualMachine#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#delete FsxOntapStorageVirtualMachine#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#update FsxOntapStorageVirtualMachine#update}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#create FsxOntapStorageVirtualMachine#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#delete FsxOntapStorageVirtualMachine#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_storage_virtual_machine#update FsxOntapStorageVirtualMachine#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxOntapStorageVirtualMachineTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FsxOntapStorageVirtualMachineTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxOntapStorageVirtualMachineTimeoutsOutputReference",
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
    def internal_value(self) -> typing.Optional[FsxOntapStorageVirtualMachineTimeouts]:
        return typing.cast(typing.Optional[FsxOntapStorageVirtualMachineTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[FsxOntapStorageVirtualMachineTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


class FsxOntapVolume(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxOntapVolume",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume aws_fsx_ontap_volume}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        junction_path: builtins.str,
        name: builtins.str,
        size_in_megabytes: jsii.Number,
        storage_efficiency_enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        storage_virtual_machine_id: builtins.str,
        security_style: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tiering_policy: typing.Optional["FsxOntapVolumeTieringPolicy"] = None,
        timeouts: typing.Optional["FsxOntapVolumeTimeouts"] = None,
        volume_type: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume aws_fsx_ontap_volume} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param junction_path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#junction_path FsxOntapVolume#junction_path}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#name FsxOntapVolume#name}.
        :param size_in_megabytes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#size_in_megabytes FsxOntapVolume#size_in_megabytes}.
        :param storage_efficiency_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#storage_efficiency_enabled FsxOntapVolume#storage_efficiency_enabled}.
        :param storage_virtual_machine_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#storage_virtual_machine_id FsxOntapVolume#storage_virtual_machine_id}.
        :param security_style: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#security_style FsxOntapVolume#security_style}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#tags FsxOntapVolume#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#tags_all FsxOntapVolume#tags_all}.
        :param tiering_policy: tiering_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#tiering_policy FsxOntapVolume#tiering_policy}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#timeouts FsxOntapVolume#timeouts}
        :param volume_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#volume_type FsxOntapVolume#volume_type}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = FsxOntapVolumeConfig(
            junction_path=junction_path,
            name=name,
            size_in_megabytes=size_in_megabytes,
            storage_efficiency_enabled=storage_efficiency_enabled,
            storage_virtual_machine_id=storage_virtual_machine_id,
            security_style=security_style,
            tags=tags,
            tags_all=tags_all,
            tiering_policy=tiering_policy,
            timeouts=timeouts,
            volume_type=volume_type,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putTieringPolicy")
    def put_tiering_policy(
        self,
        *,
        cooling_period: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cooling_period: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#cooling_period FsxOntapVolume#cooling_period}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#name FsxOntapVolume#name}.
        '''
        value = FsxOntapVolumeTieringPolicy(cooling_period=cooling_period, name=name)

        return typing.cast(None, jsii.invoke(self, "putTieringPolicy", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#create FsxOntapVolume#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#delete FsxOntapVolume#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#update FsxOntapVolume#update}.
        '''
        value = FsxOntapVolumeTimeouts(create=create, delete=delete, update=update)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetSecurityStyle")
    def reset_security_style(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityStyle", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTieringPolicy")
    def reset_tiering_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTieringPolicy", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="resetVolumeType")
    def reset_volume_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVolumeType", []))

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
    @jsii.member(jsii_name="fileSystemId")
    def file_system_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileSystemId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="flexcacheEndpointType")
    def flexcache_endpoint_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "flexcacheEndpointType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ontapVolumeType")
    def ontap_volume_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ontapVolumeType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tieringPolicy")
    def tiering_policy(self) -> "FsxOntapVolumeTieringPolicyOutputReference":
        return typing.cast("FsxOntapVolumeTieringPolicyOutputReference", jsii.get(self, "tieringPolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "FsxOntapVolumeTimeoutsOutputReference":
        return typing.cast("FsxOntapVolumeTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="junctionPathInput")
    def junction_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "junctionPathInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityStyleInput")
    def security_style_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "securityStyleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sizeInMegabytesInput")
    def size_in_megabytes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sizeInMegabytesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageEfficiencyEnabledInput")
    def storage_efficiency_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "storageEfficiencyEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageVirtualMachineIdInput")
    def storage_virtual_machine_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageVirtualMachineIdInput"))

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
    @jsii.member(jsii_name="tieringPolicyInput")
    def tiering_policy_input(self) -> typing.Optional["FsxOntapVolumeTieringPolicy"]:
        return typing.cast(typing.Optional["FsxOntapVolumeTieringPolicy"], jsii.get(self, "tieringPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["FsxOntapVolumeTimeouts"]:
        return typing.cast(typing.Optional["FsxOntapVolumeTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeTypeInput")
    def volume_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "volumeTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="junctionPath")
    def junction_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "junctionPath"))

    @junction_path.setter
    def junction_path(self, value: builtins.str) -> None:
        jsii.set(self, "junctionPath", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityStyle")
    def security_style(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "securityStyle"))

    @security_style.setter
    def security_style(self, value: builtins.str) -> None:
        jsii.set(self, "securityStyle", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sizeInMegabytes")
    def size_in_megabytes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sizeInMegabytes"))

    @size_in_megabytes.setter
    def size_in_megabytes(self, value: jsii.Number) -> None:
        jsii.set(self, "sizeInMegabytes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageEfficiencyEnabled")
    def storage_efficiency_enabled(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "storageEfficiencyEnabled"))

    @storage_efficiency_enabled.setter
    def storage_efficiency_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "storageEfficiencyEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageVirtualMachineId")
    def storage_virtual_machine_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageVirtualMachineId"))

    @storage_virtual_machine_id.setter
    def storage_virtual_machine_id(self, value: builtins.str) -> None:
        jsii.set(self, "storageVirtualMachineId", value)

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
    @jsii.member(jsii_name="volumeType")
    def volume_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "volumeType"))

    @volume_type.setter
    def volume_type(self, value: builtins.str) -> None:
        jsii.set(self, "volumeType", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fsx.FsxOntapVolumeConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "junction_path": "junctionPath",
        "name": "name",
        "size_in_megabytes": "sizeInMegabytes",
        "storage_efficiency_enabled": "storageEfficiencyEnabled",
        "storage_virtual_machine_id": "storageVirtualMachineId",
        "security_style": "securityStyle",
        "tags": "tags",
        "tags_all": "tagsAll",
        "tiering_policy": "tieringPolicy",
        "timeouts": "timeouts",
        "volume_type": "volumeType",
    },
)
class FsxOntapVolumeConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        junction_path: builtins.str,
        name: builtins.str,
        size_in_megabytes: jsii.Number,
        storage_efficiency_enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        storage_virtual_machine_id: builtins.str,
        security_style: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tiering_policy: typing.Optional["FsxOntapVolumeTieringPolicy"] = None,
        timeouts: typing.Optional["FsxOntapVolumeTimeouts"] = None,
        volume_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS File System FSx.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param junction_path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#junction_path FsxOntapVolume#junction_path}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#name FsxOntapVolume#name}.
        :param size_in_megabytes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#size_in_megabytes FsxOntapVolume#size_in_megabytes}.
        :param storage_efficiency_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#storage_efficiency_enabled FsxOntapVolume#storage_efficiency_enabled}.
        :param storage_virtual_machine_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#storage_virtual_machine_id FsxOntapVolume#storage_virtual_machine_id}.
        :param security_style: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#security_style FsxOntapVolume#security_style}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#tags FsxOntapVolume#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#tags_all FsxOntapVolume#tags_all}.
        :param tiering_policy: tiering_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#tiering_policy FsxOntapVolume#tiering_policy}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#timeouts FsxOntapVolume#timeouts}
        :param volume_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#volume_type FsxOntapVolume#volume_type}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(tiering_policy, dict):
            tiering_policy = FsxOntapVolumeTieringPolicy(**tiering_policy)
        if isinstance(timeouts, dict):
            timeouts = FsxOntapVolumeTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "junction_path": junction_path,
            "name": name,
            "size_in_megabytes": size_in_megabytes,
            "storage_efficiency_enabled": storage_efficiency_enabled,
            "storage_virtual_machine_id": storage_virtual_machine_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if security_style is not None:
            self._values["security_style"] = security_style
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if tiering_policy is not None:
            self._values["tiering_policy"] = tiering_policy
        if timeouts is not None:
            self._values["timeouts"] = timeouts
        if volume_type is not None:
            self._values["volume_type"] = volume_type

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
    def junction_path(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#junction_path FsxOntapVolume#junction_path}.'''
        result = self._values.get("junction_path")
        assert result is not None, "Required property 'junction_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#name FsxOntapVolume#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def size_in_megabytes(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#size_in_megabytes FsxOntapVolume#size_in_megabytes}.'''
        result = self._values.get("size_in_megabytes")
        assert result is not None, "Required property 'size_in_megabytes' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def storage_efficiency_enabled(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#storage_efficiency_enabled FsxOntapVolume#storage_efficiency_enabled}.'''
        result = self._values.get("storage_efficiency_enabled")
        assert result is not None, "Required property 'storage_efficiency_enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def storage_virtual_machine_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#storage_virtual_machine_id FsxOntapVolume#storage_virtual_machine_id}.'''
        result = self._values.get("storage_virtual_machine_id")
        assert result is not None, "Required property 'storage_virtual_machine_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def security_style(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#security_style FsxOntapVolume#security_style}.'''
        result = self._values.get("security_style")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#tags FsxOntapVolume#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#tags_all FsxOntapVolume#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tiering_policy(self) -> typing.Optional["FsxOntapVolumeTieringPolicy"]:
        '''tiering_policy block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#tiering_policy FsxOntapVolume#tiering_policy}
        '''
        result = self._values.get("tiering_policy")
        return typing.cast(typing.Optional["FsxOntapVolumeTieringPolicy"], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["FsxOntapVolumeTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#timeouts FsxOntapVolume#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["FsxOntapVolumeTimeouts"], result)

    @builtins.property
    def volume_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#volume_type FsxOntapVolume#volume_type}.'''
        result = self._values.get("volume_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxOntapVolumeConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fsx.FsxOntapVolumeTieringPolicy",
    jsii_struct_bases=[],
    name_mapping={"cooling_period": "coolingPeriod", "name": "name"},
)
class FsxOntapVolumeTieringPolicy:
    def __init__(
        self,
        *,
        cooling_period: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cooling_period: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#cooling_period FsxOntapVolume#cooling_period}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#name FsxOntapVolume#name}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if cooling_period is not None:
            self._values["cooling_period"] = cooling_period
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def cooling_period(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#cooling_period FsxOntapVolume#cooling_period}.'''
        result = self._values.get("cooling_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#name FsxOntapVolume#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxOntapVolumeTieringPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FsxOntapVolumeTieringPolicyOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxOntapVolumeTieringPolicyOutputReference",
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

    @jsii.member(jsii_name="resetCoolingPeriod")
    def reset_cooling_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCoolingPeriod", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="coolingPeriodInput")
    def cooling_period_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "coolingPeriodInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="coolingPeriod")
    def cooling_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "coolingPeriod"))

    @cooling_period.setter
    def cooling_period(self, value: jsii.Number) -> None:
        jsii.set(self, "coolingPeriod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[FsxOntapVolumeTieringPolicy]:
        return typing.cast(typing.Optional[FsxOntapVolumeTieringPolicy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[FsxOntapVolumeTieringPolicy],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fsx.FsxOntapVolumeTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class FsxOntapVolumeTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#create FsxOntapVolume#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#delete FsxOntapVolume#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#update FsxOntapVolume#update}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#create FsxOntapVolume#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#delete FsxOntapVolume#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_ontap_volume#update FsxOntapVolume#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxOntapVolumeTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FsxOntapVolumeTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxOntapVolumeTimeoutsOutputReference",
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
    def internal_value(self) -> typing.Optional[FsxOntapVolumeTimeouts]:
        return typing.cast(typing.Optional[FsxOntapVolumeTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[FsxOntapVolumeTimeouts]) -> None:
        jsii.set(self, "internalValue", value)


class FsxOpenzfsFileSystem(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxOpenzfsFileSystem",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system aws_fsx_openzfs_file_system}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        deployment_type: builtins.str,
        subnet_ids: typing.Sequence[builtins.str],
        throughput_capacity: jsii.Number,
        automatic_backup_retention_days: typing.Optional[jsii.Number] = None,
        backup_id: typing.Optional[builtins.str] = None,
        copy_tags_to_backups: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        copy_tags_to_volumes: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        daily_automatic_backup_start_time: typing.Optional[builtins.str] = None,
        disk_iops_configuration: typing.Optional["FsxOpenzfsFileSystemDiskIopsConfiguration"] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        root_volume_configuration: typing.Optional["FsxOpenzfsFileSystemRootVolumeConfiguration"] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        storage_capacity: typing.Optional[jsii.Number] = None,
        storage_type: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["FsxOpenzfsFileSystemTimeouts"] = None,
        weekly_maintenance_start_time: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system aws_fsx_openzfs_file_system} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param deployment_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#deployment_type FsxOpenzfsFileSystem#deployment_type}.
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#subnet_ids FsxOpenzfsFileSystem#subnet_ids}.
        :param throughput_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#throughput_capacity FsxOpenzfsFileSystem#throughput_capacity}.
        :param automatic_backup_retention_days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#automatic_backup_retention_days FsxOpenzfsFileSystem#automatic_backup_retention_days}.
        :param backup_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#backup_id FsxOpenzfsFileSystem#backup_id}.
        :param copy_tags_to_backups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#copy_tags_to_backups FsxOpenzfsFileSystem#copy_tags_to_backups}.
        :param copy_tags_to_volumes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#copy_tags_to_volumes FsxOpenzfsFileSystem#copy_tags_to_volumes}.
        :param daily_automatic_backup_start_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#daily_automatic_backup_start_time FsxOpenzfsFileSystem#daily_automatic_backup_start_time}.
        :param disk_iops_configuration: disk_iops_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#disk_iops_configuration FsxOpenzfsFileSystem#disk_iops_configuration}
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#kms_key_id FsxOpenzfsFileSystem#kms_key_id}.
        :param root_volume_configuration: root_volume_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#root_volume_configuration FsxOpenzfsFileSystem#root_volume_configuration}
        :param security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#security_group_ids FsxOpenzfsFileSystem#security_group_ids}.
        :param storage_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#storage_capacity FsxOpenzfsFileSystem#storage_capacity}.
        :param storage_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#storage_type FsxOpenzfsFileSystem#storage_type}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#tags FsxOpenzfsFileSystem#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#tags_all FsxOpenzfsFileSystem#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#timeouts FsxOpenzfsFileSystem#timeouts}
        :param weekly_maintenance_start_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#weekly_maintenance_start_time FsxOpenzfsFileSystem#weekly_maintenance_start_time}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = FsxOpenzfsFileSystemConfig(
            deployment_type=deployment_type,
            subnet_ids=subnet_ids,
            throughput_capacity=throughput_capacity,
            automatic_backup_retention_days=automatic_backup_retention_days,
            backup_id=backup_id,
            copy_tags_to_backups=copy_tags_to_backups,
            copy_tags_to_volumes=copy_tags_to_volumes,
            daily_automatic_backup_start_time=daily_automatic_backup_start_time,
            disk_iops_configuration=disk_iops_configuration,
            kms_key_id=kms_key_id,
            root_volume_configuration=root_volume_configuration,
            security_group_ids=security_group_ids,
            storage_capacity=storage_capacity,
            storage_type=storage_type,
            tags=tags,
            tags_all=tags_all,
            timeouts=timeouts,
            weekly_maintenance_start_time=weekly_maintenance_start_time,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putDiskIopsConfiguration")
    def put_disk_iops_configuration(
        self,
        *,
        iops: typing.Optional[jsii.Number] = None,
        mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param iops: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#iops FsxOpenzfsFileSystem#iops}.
        :param mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#mode FsxOpenzfsFileSystem#mode}.
        '''
        value = FsxOpenzfsFileSystemDiskIopsConfiguration(iops=iops, mode=mode)

        return typing.cast(None, jsii.invoke(self, "putDiskIopsConfiguration", [value]))

    @jsii.member(jsii_name="putRootVolumeConfiguration")
    def put_root_volume_configuration(
        self,
        *,
        copy_tags_to_snapshots: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        data_compression_type: typing.Optional[builtins.str] = None,
        nfs_exports: typing.Optional["FsxOpenzfsFileSystemRootVolumeConfigurationNfsExports"] = None,
        read_only: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        user_and_group_quotas: typing.Optional[typing.Sequence["FsxOpenzfsFileSystemRootVolumeConfigurationUserAndGroupQuotas"]] = None,
    ) -> None:
        '''
        :param copy_tags_to_snapshots: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#copy_tags_to_snapshots FsxOpenzfsFileSystem#copy_tags_to_snapshots}.
        :param data_compression_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#data_compression_type FsxOpenzfsFileSystem#data_compression_type}.
        :param nfs_exports: nfs_exports block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#nfs_exports FsxOpenzfsFileSystem#nfs_exports}
        :param read_only: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#read_only FsxOpenzfsFileSystem#read_only}.
        :param user_and_group_quotas: user_and_group_quotas block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#user_and_group_quotas FsxOpenzfsFileSystem#user_and_group_quotas}
        '''
        value = FsxOpenzfsFileSystemRootVolumeConfiguration(
            copy_tags_to_snapshots=copy_tags_to_snapshots,
            data_compression_type=data_compression_type,
            nfs_exports=nfs_exports,
            read_only=read_only,
            user_and_group_quotas=user_and_group_quotas,
        )

        return typing.cast(None, jsii.invoke(self, "putRootVolumeConfiguration", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#create FsxOpenzfsFileSystem#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#delete FsxOpenzfsFileSystem#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#update FsxOpenzfsFileSystem#update}.
        '''
        value = FsxOpenzfsFileSystemTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetAutomaticBackupRetentionDays")
    def reset_automatic_backup_retention_days(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutomaticBackupRetentionDays", []))

    @jsii.member(jsii_name="resetBackupId")
    def reset_backup_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackupId", []))

    @jsii.member(jsii_name="resetCopyTagsToBackups")
    def reset_copy_tags_to_backups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCopyTagsToBackups", []))

    @jsii.member(jsii_name="resetCopyTagsToVolumes")
    def reset_copy_tags_to_volumes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCopyTagsToVolumes", []))

    @jsii.member(jsii_name="resetDailyAutomaticBackupStartTime")
    def reset_daily_automatic_backup_start_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDailyAutomaticBackupStartTime", []))

    @jsii.member(jsii_name="resetDiskIopsConfiguration")
    def reset_disk_iops_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiskIopsConfiguration", []))

    @jsii.member(jsii_name="resetKmsKeyId")
    def reset_kms_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyId", []))

    @jsii.member(jsii_name="resetRootVolumeConfiguration")
    def reset_root_volume_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRootVolumeConfiguration", []))

    @jsii.member(jsii_name="resetSecurityGroupIds")
    def reset_security_group_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityGroupIds", []))

    @jsii.member(jsii_name="resetStorageCapacity")
    def reset_storage_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageCapacity", []))

    @jsii.member(jsii_name="resetStorageType")
    def reset_storage_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageType", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="resetWeeklyMaintenanceStartTime")
    def reset_weekly_maintenance_start_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWeeklyMaintenanceStartTime", []))

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
    @jsii.member(jsii_name="diskIopsConfiguration")
    def disk_iops_configuration(
        self,
    ) -> "FsxOpenzfsFileSystemDiskIopsConfigurationOutputReference":
        return typing.cast("FsxOpenzfsFileSystemDiskIopsConfigurationOutputReference", jsii.get(self, "diskIopsConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsName")
    def dns_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dnsName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkInterfaceIds")
    def network_interface_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "networkInterfaceIds"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerId")
    def owner_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ownerId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rootVolumeConfiguration")
    def root_volume_configuration(
        self,
    ) -> "FsxOpenzfsFileSystemRootVolumeConfigurationOutputReference":
        return typing.cast("FsxOpenzfsFileSystemRootVolumeConfigurationOutputReference", jsii.get(self, "rootVolumeConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rootVolumeId")
    def root_volume_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rootVolumeId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "FsxOpenzfsFileSystemTimeoutsOutputReference":
        return typing.cast("FsxOpenzfsFileSystemTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="automaticBackupRetentionDaysInput")
    def automatic_backup_retention_days_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "automaticBackupRetentionDaysInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupIdInput")
    def backup_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backupIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyTagsToBackupsInput")
    def copy_tags_to_backups_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "copyTagsToBackupsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyTagsToVolumesInput")
    def copy_tags_to_volumes_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "copyTagsToVolumesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dailyAutomaticBackupStartTimeInput")
    def daily_automatic_backup_start_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dailyAutomaticBackupStartTimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentTypeInput")
    def deployment_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deploymentTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="diskIopsConfigurationInput")
    def disk_iops_configuration_input(
        self,
    ) -> typing.Optional["FsxOpenzfsFileSystemDiskIopsConfiguration"]:
        return typing.cast(typing.Optional["FsxOpenzfsFileSystemDiskIopsConfiguration"], jsii.get(self, "diskIopsConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyIdInput")
    def kms_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rootVolumeConfigurationInput")
    def root_volume_configuration_input(
        self,
    ) -> typing.Optional["FsxOpenzfsFileSystemRootVolumeConfiguration"]:
        return typing.cast(typing.Optional["FsxOpenzfsFileSystemRootVolumeConfiguration"], jsii.get(self, "rootVolumeConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIdsInput")
    def security_group_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageCapacityInput")
    def storage_capacity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "storageCapacityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageTypeInput")
    def storage_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageTypeInput"))

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
    @jsii.member(jsii_name="throughputCapacityInput")
    def throughput_capacity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "throughputCapacityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["FsxOpenzfsFileSystemTimeouts"]:
        return typing.cast(typing.Optional["FsxOpenzfsFileSystemTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="weeklyMaintenanceStartTimeInput")
    def weekly_maintenance_start_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "weeklyMaintenanceStartTimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="automaticBackupRetentionDays")
    def automatic_backup_retention_days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "automaticBackupRetentionDays"))

    @automatic_backup_retention_days.setter
    def automatic_backup_retention_days(self, value: jsii.Number) -> None:
        jsii.set(self, "automaticBackupRetentionDays", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupId")
    def backup_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backupId"))

    @backup_id.setter
    def backup_id(self, value: builtins.str) -> None:
        jsii.set(self, "backupId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyTagsToBackups")
    def copy_tags_to_backups(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "copyTagsToBackups"))

    @copy_tags_to_backups.setter
    def copy_tags_to_backups(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "copyTagsToBackups", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyTagsToVolumes")
    def copy_tags_to_volumes(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "copyTagsToVolumes"))

    @copy_tags_to_volumes.setter
    def copy_tags_to_volumes(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "copyTagsToVolumes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dailyAutomaticBackupStartTime")
    def daily_automatic_backup_start_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dailyAutomaticBackupStartTime"))

    @daily_automatic_backup_start_time.setter
    def daily_automatic_backup_start_time(self, value: builtins.str) -> None:
        jsii.set(self, "dailyAutomaticBackupStartTime", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentType")
    def deployment_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deploymentType"))

    @deployment_type.setter
    def deployment_type(self, value: builtins.str) -> None:
        jsii.set(self, "deploymentType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @kms_key_id.setter
    def kms_key_id(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroupIds"))

    @security_group_ids.setter
    def security_group_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "securityGroupIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageCapacity")
    def storage_capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "storageCapacity"))

    @storage_capacity.setter
    def storage_capacity(self, value: jsii.Number) -> None:
        jsii.set(self, "storageCapacity", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageType")
    def storage_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageType"))

    @storage_type.setter
    def storage_type(self, value: builtins.str) -> None:
        jsii.set(self, "storageType", value)

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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="throughputCapacity")
    def throughput_capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "throughputCapacity"))

    @throughput_capacity.setter
    def throughput_capacity(self, value: jsii.Number) -> None:
        jsii.set(self, "throughputCapacity", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="weeklyMaintenanceStartTime")
    def weekly_maintenance_start_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "weeklyMaintenanceStartTime"))

    @weekly_maintenance_start_time.setter
    def weekly_maintenance_start_time(self, value: builtins.str) -> None:
        jsii.set(self, "weeklyMaintenanceStartTime", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fsx.FsxOpenzfsFileSystemConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "deployment_type": "deploymentType",
        "subnet_ids": "subnetIds",
        "throughput_capacity": "throughputCapacity",
        "automatic_backup_retention_days": "automaticBackupRetentionDays",
        "backup_id": "backupId",
        "copy_tags_to_backups": "copyTagsToBackups",
        "copy_tags_to_volumes": "copyTagsToVolumes",
        "daily_automatic_backup_start_time": "dailyAutomaticBackupStartTime",
        "disk_iops_configuration": "diskIopsConfiguration",
        "kms_key_id": "kmsKeyId",
        "root_volume_configuration": "rootVolumeConfiguration",
        "security_group_ids": "securityGroupIds",
        "storage_capacity": "storageCapacity",
        "storage_type": "storageType",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
        "weekly_maintenance_start_time": "weeklyMaintenanceStartTime",
    },
)
class FsxOpenzfsFileSystemConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        deployment_type: builtins.str,
        subnet_ids: typing.Sequence[builtins.str],
        throughput_capacity: jsii.Number,
        automatic_backup_retention_days: typing.Optional[jsii.Number] = None,
        backup_id: typing.Optional[builtins.str] = None,
        copy_tags_to_backups: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        copy_tags_to_volumes: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        daily_automatic_backup_start_time: typing.Optional[builtins.str] = None,
        disk_iops_configuration: typing.Optional["FsxOpenzfsFileSystemDiskIopsConfiguration"] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        root_volume_configuration: typing.Optional["FsxOpenzfsFileSystemRootVolumeConfiguration"] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        storage_capacity: typing.Optional[jsii.Number] = None,
        storage_type: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["FsxOpenzfsFileSystemTimeouts"] = None,
        weekly_maintenance_start_time: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS File System FSx.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param deployment_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#deployment_type FsxOpenzfsFileSystem#deployment_type}.
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#subnet_ids FsxOpenzfsFileSystem#subnet_ids}.
        :param throughput_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#throughput_capacity FsxOpenzfsFileSystem#throughput_capacity}.
        :param automatic_backup_retention_days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#automatic_backup_retention_days FsxOpenzfsFileSystem#automatic_backup_retention_days}.
        :param backup_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#backup_id FsxOpenzfsFileSystem#backup_id}.
        :param copy_tags_to_backups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#copy_tags_to_backups FsxOpenzfsFileSystem#copy_tags_to_backups}.
        :param copy_tags_to_volumes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#copy_tags_to_volumes FsxOpenzfsFileSystem#copy_tags_to_volumes}.
        :param daily_automatic_backup_start_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#daily_automatic_backup_start_time FsxOpenzfsFileSystem#daily_automatic_backup_start_time}.
        :param disk_iops_configuration: disk_iops_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#disk_iops_configuration FsxOpenzfsFileSystem#disk_iops_configuration}
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#kms_key_id FsxOpenzfsFileSystem#kms_key_id}.
        :param root_volume_configuration: root_volume_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#root_volume_configuration FsxOpenzfsFileSystem#root_volume_configuration}
        :param security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#security_group_ids FsxOpenzfsFileSystem#security_group_ids}.
        :param storage_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#storage_capacity FsxOpenzfsFileSystem#storage_capacity}.
        :param storage_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#storage_type FsxOpenzfsFileSystem#storage_type}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#tags FsxOpenzfsFileSystem#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#tags_all FsxOpenzfsFileSystem#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#timeouts FsxOpenzfsFileSystem#timeouts}
        :param weekly_maintenance_start_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#weekly_maintenance_start_time FsxOpenzfsFileSystem#weekly_maintenance_start_time}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(disk_iops_configuration, dict):
            disk_iops_configuration = FsxOpenzfsFileSystemDiskIopsConfiguration(**disk_iops_configuration)
        if isinstance(root_volume_configuration, dict):
            root_volume_configuration = FsxOpenzfsFileSystemRootVolumeConfiguration(**root_volume_configuration)
        if isinstance(timeouts, dict):
            timeouts = FsxOpenzfsFileSystemTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "deployment_type": deployment_type,
            "subnet_ids": subnet_ids,
            "throughput_capacity": throughput_capacity,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if automatic_backup_retention_days is not None:
            self._values["automatic_backup_retention_days"] = automatic_backup_retention_days
        if backup_id is not None:
            self._values["backup_id"] = backup_id
        if copy_tags_to_backups is not None:
            self._values["copy_tags_to_backups"] = copy_tags_to_backups
        if copy_tags_to_volumes is not None:
            self._values["copy_tags_to_volumes"] = copy_tags_to_volumes
        if daily_automatic_backup_start_time is not None:
            self._values["daily_automatic_backup_start_time"] = daily_automatic_backup_start_time
        if disk_iops_configuration is not None:
            self._values["disk_iops_configuration"] = disk_iops_configuration
        if kms_key_id is not None:
            self._values["kms_key_id"] = kms_key_id
        if root_volume_configuration is not None:
            self._values["root_volume_configuration"] = root_volume_configuration
        if security_group_ids is not None:
            self._values["security_group_ids"] = security_group_ids
        if storage_capacity is not None:
            self._values["storage_capacity"] = storage_capacity
        if storage_type is not None:
            self._values["storage_type"] = storage_type
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if timeouts is not None:
            self._values["timeouts"] = timeouts
        if weekly_maintenance_start_time is not None:
            self._values["weekly_maintenance_start_time"] = weekly_maintenance_start_time

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
    def deployment_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#deployment_type FsxOpenzfsFileSystem#deployment_type}.'''
        result = self._values.get("deployment_type")
        assert result is not None, "Required property 'deployment_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subnet_ids(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#subnet_ids FsxOpenzfsFileSystem#subnet_ids}.'''
        result = self._values.get("subnet_ids")
        assert result is not None, "Required property 'subnet_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def throughput_capacity(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#throughput_capacity FsxOpenzfsFileSystem#throughput_capacity}.'''
        result = self._values.get("throughput_capacity")
        assert result is not None, "Required property 'throughput_capacity' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def automatic_backup_retention_days(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#automatic_backup_retention_days FsxOpenzfsFileSystem#automatic_backup_retention_days}.'''
        result = self._values.get("automatic_backup_retention_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def backup_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#backup_id FsxOpenzfsFileSystem#backup_id}.'''
        result = self._values.get("backup_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def copy_tags_to_backups(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#copy_tags_to_backups FsxOpenzfsFileSystem#copy_tags_to_backups}.'''
        result = self._values.get("copy_tags_to_backups")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def copy_tags_to_volumes(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#copy_tags_to_volumes FsxOpenzfsFileSystem#copy_tags_to_volumes}.'''
        result = self._values.get("copy_tags_to_volumes")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def daily_automatic_backup_start_time(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#daily_automatic_backup_start_time FsxOpenzfsFileSystem#daily_automatic_backup_start_time}.'''
        result = self._values.get("daily_automatic_backup_start_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disk_iops_configuration(
        self,
    ) -> typing.Optional["FsxOpenzfsFileSystemDiskIopsConfiguration"]:
        '''disk_iops_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#disk_iops_configuration FsxOpenzfsFileSystem#disk_iops_configuration}
        '''
        result = self._values.get("disk_iops_configuration")
        return typing.cast(typing.Optional["FsxOpenzfsFileSystemDiskIopsConfiguration"], result)

    @builtins.property
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#kms_key_id FsxOpenzfsFileSystem#kms_key_id}.'''
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def root_volume_configuration(
        self,
    ) -> typing.Optional["FsxOpenzfsFileSystemRootVolumeConfiguration"]:
        '''root_volume_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#root_volume_configuration FsxOpenzfsFileSystem#root_volume_configuration}
        '''
        result = self._values.get("root_volume_configuration")
        return typing.cast(typing.Optional["FsxOpenzfsFileSystemRootVolumeConfiguration"], result)

    @builtins.property
    def security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#security_group_ids FsxOpenzfsFileSystem#security_group_ids}.'''
        result = self._values.get("security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def storage_capacity(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#storage_capacity FsxOpenzfsFileSystem#storage_capacity}.'''
        result = self._values.get("storage_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def storage_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#storage_type FsxOpenzfsFileSystem#storage_type}.'''
        result = self._values.get("storage_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#tags FsxOpenzfsFileSystem#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#tags_all FsxOpenzfsFileSystem#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["FsxOpenzfsFileSystemTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#timeouts FsxOpenzfsFileSystem#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["FsxOpenzfsFileSystemTimeouts"], result)

    @builtins.property
    def weekly_maintenance_start_time(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#weekly_maintenance_start_time FsxOpenzfsFileSystem#weekly_maintenance_start_time}.'''
        result = self._values.get("weekly_maintenance_start_time")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxOpenzfsFileSystemConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fsx.FsxOpenzfsFileSystemDiskIopsConfiguration",
    jsii_struct_bases=[],
    name_mapping={"iops": "iops", "mode": "mode"},
)
class FsxOpenzfsFileSystemDiskIopsConfiguration:
    def __init__(
        self,
        *,
        iops: typing.Optional[jsii.Number] = None,
        mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param iops: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#iops FsxOpenzfsFileSystem#iops}.
        :param mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#mode FsxOpenzfsFileSystem#mode}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if iops is not None:
            self._values["iops"] = iops
        if mode is not None:
            self._values["mode"] = mode

    @builtins.property
    def iops(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#iops FsxOpenzfsFileSystem#iops}.'''
        result = self._values.get("iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#mode FsxOpenzfsFileSystem#mode}.'''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxOpenzfsFileSystemDiskIopsConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FsxOpenzfsFileSystemDiskIopsConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxOpenzfsFileSystemDiskIopsConfigurationOutputReference",
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

    @jsii.member(jsii_name="resetIops")
    def reset_iops(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIops", []))

    @jsii.member(jsii_name="resetMode")
    def reset_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMode", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iopsInput")
    def iops_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "iopsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="modeInput")
    def mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iops")
    def iops(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "iops"))

    @iops.setter
    def iops(self, value: jsii.Number) -> None:
        jsii.set(self, "iops", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @mode.setter
    def mode(self, value: builtins.str) -> None:
        jsii.set(self, "mode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[FsxOpenzfsFileSystemDiskIopsConfiguration]:
        return typing.cast(typing.Optional[FsxOpenzfsFileSystemDiskIopsConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[FsxOpenzfsFileSystemDiskIopsConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fsx.FsxOpenzfsFileSystemRootVolumeConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "copy_tags_to_snapshots": "copyTagsToSnapshots",
        "data_compression_type": "dataCompressionType",
        "nfs_exports": "nfsExports",
        "read_only": "readOnly",
        "user_and_group_quotas": "userAndGroupQuotas",
    },
)
class FsxOpenzfsFileSystemRootVolumeConfiguration:
    def __init__(
        self,
        *,
        copy_tags_to_snapshots: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        data_compression_type: typing.Optional[builtins.str] = None,
        nfs_exports: typing.Optional["FsxOpenzfsFileSystemRootVolumeConfigurationNfsExports"] = None,
        read_only: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        user_and_group_quotas: typing.Optional[typing.Sequence["FsxOpenzfsFileSystemRootVolumeConfigurationUserAndGroupQuotas"]] = None,
    ) -> None:
        '''
        :param copy_tags_to_snapshots: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#copy_tags_to_snapshots FsxOpenzfsFileSystem#copy_tags_to_snapshots}.
        :param data_compression_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#data_compression_type FsxOpenzfsFileSystem#data_compression_type}.
        :param nfs_exports: nfs_exports block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#nfs_exports FsxOpenzfsFileSystem#nfs_exports}
        :param read_only: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#read_only FsxOpenzfsFileSystem#read_only}.
        :param user_and_group_quotas: user_and_group_quotas block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#user_and_group_quotas FsxOpenzfsFileSystem#user_and_group_quotas}
        '''
        if isinstance(nfs_exports, dict):
            nfs_exports = FsxOpenzfsFileSystemRootVolumeConfigurationNfsExports(**nfs_exports)
        self._values: typing.Dict[str, typing.Any] = {}
        if copy_tags_to_snapshots is not None:
            self._values["copy_tags_to_snapshots"] = copy_tags_to_snapshots
        if data_compression_type is not None:
            self._values["data_compression_type"] = data_compression_type
        if nfs_exports is not None:
            self._values["nfs_exports"] = nfs_exports
        if read_only is not None:
            self._values["read_only"] = read_only
        if user_and_group_quotas is not None:
            self._values["user_and_group_quotas"] = user_and_group_quotas

    @builtins.property
    def copy_tags_to_snapshots(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#copy_tags_to_snapshots FsxOpenzfsFileSystem#copy_tags_to_snapshots}.'''
        result = self._values.get("copy_tags_to_snapshots")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def data_compression_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#data_compression_type FsxOpenzfsFileSystem#data_compression_type}.'''
        result = self._values.get("data_compression_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nfs_exports(
        self,
    ) -> typing.Optional["FsxOpenzfsFileSystemRootVolumeConfigurationNfsExports"]:
        '''nfs_exports block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#nfs_exports FsxOpenzfsFileSystem#nfs_exports}
        '''
        result = self._values.get("nfs_exports")
        return typing.cast(typing.Optional["FsxOpenzfsFileSystemRootVolumeConfigurationNfsExports"], result)

    @builtins.property
    def read_only(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#read_only FsxOpenzfsFileSystem#read_only}.'''
        result = self._values.get("read_only")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def user_and_group_quotas(
        self,
    ) -> typing.Optional[typing.List["FsxOpenzfsFileSystemRootVolumeConfigurationUserAndGroupQuotas"]]:
        '''user_and_group_quotas block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#user_and_group_quotas FsxOpenzfsFileSystem#user_and_group_quotas}
        '''
        result = self._values.get("user_and_group_quotas")
        return typing.cast(typing.Optional[typing.List["FsxOpenzfsFileSystemRootVolumeConfigurationUserAndGroupQuotas"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxOpenzfsFileSystemRootVolumeConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fsx.FsxOpenzfsFileSystemRootVolumeConfigurationNfsExports",
    jsii_struct_bases=[],
    name_mapping={"client_configurations": "clientConfigurations"},
)
class FsxOpenzfsFileSystemRootVolumeConfigurationNfsExports:
    def __init__(
        self,
        *,
        client_configurations: typing.Sequence["FsxOpenzfsFileSystemRootVolumeConfigurationNfsExportsClientConfigurations"],
    ) -> None:
        '''
        :param client_configurations: client_configurations block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#client_configurations FsxOpenzfsFileSystem#client_configurations}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "client_configurations": client_configurations,
        }

    @builtins.property
    def client_configurations(
        self,
    ) -> typing.List["FsxOpenzfsFileSystemRootVolumeConfigurationNfsExportsClientConfigurations"]:
        '''client_configurations block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#client_configurations FsxOpenzfsFileSystem#client_configurations}
        '''
        result = self._values.get("client_configurations")
        assert result is not None, "Required property 'client_configurations' is missing"
        return typing.cast(typing.List["FsxOpenzfsFileSystemRootVolumeConfigurationNfsExportsClientConfigurations"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxOpenzfsFileSystemRootVolumeConfigurationNfsExports(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fsx.FsxOpenzfsFileSystemRootVolumeConfigurationNfsExportsClientConfigurations",
    jsii_struct_bases=[],
    name_mapping={"clients": "clients", "options": "options"},
)
class FsxOpenzfsFileSystemRootVolumeConfigurationNfsExportsClientConfigurations:
    def __init__(
        self,
        *,
        clients: builtins.str,
        options: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param clients: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#clients FsxOpenzfsFileSystem#clients}.
        :param options: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#options FsxOpenzfsFileSystem#options}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "clients": clients,
            "options": options,
        }

    @builtins.property
    def clients(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#clients FsxOpenzfsFileSystem#clients}.'''
        result = self._values.get("clients")
        assert result is not None, "Required property 'clients' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def options(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#options FsxOpenzfsFileSystem#options}.'''
        result = self._values.get("options")
        assert result is not None, "Required property 'options' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxOpenzfsFileSystemRootVolumeConfigurationNfsExportsClientConfigurations(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FsxOpenzfsFileSystemRootVolumeConfigurationNfsExportsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxOpenzfsFileSystemRootVolumeConfigurationNfsExportsOutputReference",
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
    @jsii.member(jsii_name="clientConfigurationsInput")
    def client_configurations_input(
        self,
    ) -> typing.Optional[typing.List[FsxOpenzfsFileSystemRootVolumeConfigurationNfsExportsClientConfigurations]]:
        return typing.cast(typing.Optional[typing.List[FsxOpenzfsFileSystemRootVolumeConfigurationNfsExportsClientConfigurations]], jsii.get(self, "clientConfigurationsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientConfigurations")
    def client_configurations(
        self,
    ) -> typing.List[FsxOpenzfsFileSystemRootVolumeConfigurationNfsExportsClientConfigurations]:
        return typing.cast(typing.List[FsxOpenzfsFileSystemRootVolumeConfigurationNfsExportsClientConfigurations], jsii.get(self, "clientConfigurations"))

    @client_configurations.setter
    def client_configurations(
        self,
        value: typing.List[FsxOpenzfsFileSystemRootVolumeConfigurationNfsExportsClientConfigurations],
    ) -> None:
        jsii.set(self, "clientConfigurations", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[FsxOpenzfsFileSystemRootVolumeConfigurationNfsExports]:
        return typing.cast(typing.Optional[FsxOpenzfsFileSystemRootVolumeConfigurationNfsExports], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[FsxOpenzfsFileSystemRootVolumeConfigurationNfsExports],
    ) -> None:
        jsii.set(self, "internalValue", value)


class FsxOpenzfsFileSystemRootVolumeConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxOpenzfsFileSystemRootVolumeConfigurationOutputReference",
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

    @jsii.member(jsii_name="putNfsExports")
    def put_nfs_exports(
        self,
        *,
        client_configurations: typing.Sequence[FsxOpenzfsFileSystemRootVolumeConfigurationNfsExportsClientConfigurations],
    ) -> None:
        '''
        :param client_configurations: client_configurations block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#client_configurations FsxOpenzfsFileSystem#client_configurations}
        '''
        value = FsxOpenzfsFileSystemRootVolumeConfigurationNfsExports(
            client_configurations=client_configurations
        )

        return typing.cast(None, jsii.invoke(self, "putNfsExports", [value]))

    @jsii.member(jsii_name="resetCopyTagsToSnapshots")
    def reset_copy_tags_to_snapshots(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCopyTagsToSnapshots", []))

    @jsii.member(jsii_name="resetDataCompressionType")
    def reset_data_compression_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataCompressionType", []))

    @jsii.member(jsii_name="resetNfsExports")
    def reset_nfs_exports(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNfsExports", []))

    @jsii.member(jsii_name="resetReadOnly")
    def reset_read_only(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReadOnly", []))

    @jsii.member(jsii_name="resetUserAndGroupQuotas")
    def reset_user_and_group_quotas(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserAndGroupQuotas", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nfsExports")
    def nfs_exports(
        self,
    ) -> FsxOpenzfsFileSystemRootVolumeConfigurationNfsExportsOutputReference:
        return typing.cast(FsxOpenzfsFileSystemRootVolumeConfigurationNfsExportsOutputReference, jsii.get(self, "nfsExports"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyTagsToSnapshotsInput")
    def copy_tags_to_snapshots_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "copyTagsToSnapshotsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataCompressionTypeInput")
    def data_compression_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dataCompressionTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nfsExportsInput")
    def nfs_exports_input(
        self,
    ) -> typing.Optional[FsxOpenzfsFileSystemRootVolumeConfigurationNfsExports]:
        return typing.cast(typing.Optional[FsxOpenzfsFileSystemRootVolumeConfigurationNfsExports], jsii.get(self, "nfsExportsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readOnlyInput")
    def read_only_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "readOnlyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userAndGroupQuotasInput")
    def user_and_group_quotas_input(
        self,
    ) -> typing.Optional[typing.List["FsxOpenzfsFileSystemRootVolumeConfigurationUserAndGroupQuotas"]]:
        return typing.cast(typing.Optional[typing.List["FsxOpenzfsFileSystemRootVolumeConfigurationUserAndGroupQuotas"]], jsii.get(self, "userAndGroupQuotasInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyTagsToSnapshots")
    def copy_tags_to_snapshots(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "copyTagsToSnapshots"))

    @copy_tags_to_snapshots.setter
    def copy_tags_to_snapshots(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "copyTagsToSnapshots", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataCompressionType")
    def data_compression_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataCompressionType"))

    @data_compression_type.setter
    def data_compression_type(self, value: builtins.str) -> None:
        jsii.set(self, "dataCompressionType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readOnly")
    def read_only(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "readOnly"))

    @read_only.setter
    def read_only(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "readOnly", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userAndGroupQuotas")
    def user_and_group_quotas(
        self,
    ) -> typing.List["FsxOpenzfsFileSystemRootVolumeConfigurationUserAndGroupQuotas"]:
        return typing.cast(typing.List["FsxOpenzfsFileSystemRootVolumeConfigurationUserAndGroupQuotas"], jsii.get(self, "userAndGroupQuotas"))

    @user_and_group_quotas.setter
    def user_and_group_quotas(
        self,
        value: typing.List["FsxOpenzfsFileSystemRootVolumeConfigurationUserAndGroupQuotas"],
    ) -> None:
        jsii.set(self, "userAndGroupQuotas", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[FsxOpenzfsFileSystemRootVolumeConfiguration]:
        return typing.cast(typing.Optional[FsxOpenzfsFileSystemRootVolumeConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[FsxOpenzfsFileSystemRootVolumeConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fsx.FsxOpenzfsFileSystemRootVolumeConfigurationUserAndGroupQuotas",
    jsii_struct_bases=[],
    name_mapping={
        "id": "id",
        "storage_capacity_quota_gib": "storageCapacityQuotaGib",
        "type": "type",
    },
)
class FsxOpenzfsFileSystemRootVolumeConfigurationUserAndGroupQuotas:
    def __init__(
        self,
        *,
        id: jsii.Number,
        storage_capacity_quota_gib: jsii.Number,
        type: builtins.str,
    ) -> None:
        '''
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#id FsxOpenzfsFileSystem#id}.
        :param storage_capacity_quota_gib: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#storage_capacity_quota_gib FsxOpenzfsFileSystem#storage_capacity_quota_gib}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#type FsxOpenzfsFileSystem#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "id": id,
            "storage_capacity_quota_gib": storage_capacity_quota_gib,
            "type": type,
        }

    @builtins.property
    def id(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#id FsxOpenzfsFileSystem#id}.'''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def storage_capacity_quota_gib(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#storage_capacity_quota_gib FsxOpenzfsFileSystem#storage_capacity_quota_gib}.'''
        result = self._values.get("storage_capacity_quota_gib")
        assert result is not None, "Required property 'storage_capacity_quota_gib' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#type FsxOpenzfsFileSystem#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxOpenzfsFileSystemRootVolumeConfigurationUserAndGroupQuotas(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fsx.FsxOpenzfsFileSystemTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class FsxOpenzfsFileSystemTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#create FsxOpenzfsFileSystem#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#delete FsxOpenzfsFileSystem#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#update FsxOpenzfsFileSystem#update}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#create FsxOpenzfsFileSystem#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#delete FsxOpenzfsFileSystem#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_file_system#update FsxOpenzfsFileSystem#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxOpenzfsFileSystemTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FsxOpenzfsFileSystemTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxOpenzfsFileSystemTimeoutsOutputReference",
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
    def internal_value(self) -> typing.Optional[FsxOpenzfsFileSystemTimeouts]:
        return typing.cast(typing.Optional[FsxOpenzfsFileSystemTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[FsxOpenzfsFileSystemTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


class FsxOpenzfsSnapshot(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxOpenzfsSnapshot",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_snapshot aws_fsx_openzfs_snapshot}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        volume_id: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["FsxOpenzfsSnapshotTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_snapshot aws_fsx_openzfs_snapshot} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_snapshot#name FsxOpenzfsSnapshot#name}.
        :param volume_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_snapshot#volume_id FsxOpenzfsSnapshot#volume_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_snapshot#tags FsxOpenzfsSnapshot#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_snapshot#tags_all FsxOpenzfsSnapshot#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_snapshot#timeouts FsxOpenzfsSnapshot#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = FsxOpenzfsSnapshotConfig(
            name=name,
            volume_id=volume_id,
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
        read: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_snapshot#create FsxOpenzfsSnapshot#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_snapshot#delete FsxOpenzfsSnapshot#delete}.
        :param read: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_snapshot#read FsxOpenzfsSnapshot#read}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_snapshot#update FsxOpenzfsSnapshot#update}.
        '''
        value = FsxOpenzfsSnapshotTimeouts(
            create=create, delete=delete, read=read, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

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
    @jsii.member(jsii_name="creationTime")
    def creation_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creationTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "FsxOpenzfsSnapshotTimeoutsOutputReference":
        return typing.cast("FsxOpenzfsSnapshotTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

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
    def timeouts_input(self) -> typing.Optional["FsxOpenzfsSnapshotTimeouts"]:
        return typing.cast(typing.Optional["FsxOpenzfsSnapshotTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeIdInput")
    def volume_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "volumeIdInput"))

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
    @jsii.member(jsii_name="volumeId")
    def volume_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "volumeId"))

    @volume_id.setter
    def volume_id(self, value: builtins.str) -> None:
        jsii.set(self, "volumeId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fsx.FsxOpenzfsSnapshotConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "volume_id": "volumeId",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
    },
)
class FsxOpenzfsSnapshotConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        volume_id: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["FsxOpenzfsSnapshotTimeouts"] = None,
    ) -> None:
        '''AWS File System FSx.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_snapshot#name FsxOpenzfsSnapshot#name}.
        :param volume_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_snapshot#volume_id FsxOpenzfsSnapshot#volume_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_snapshot#tags FsxOpenzfsSnapshot#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_snapshot#tags_all FsxOpenzfsSnapshot#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_snapshot#timeouts FsxOpenzfsSnapshot#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = FsxOpenzfsSnapshotTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "volume_id": volume_id,
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_snapshot#name FsxOpenzfsSnapshot#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def volume_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_snapshot#volume_id FsxOpenzfsSnapshot#volume_id}.'''
        result = self._values.get("volume_id")
        assert result is not None, "Required property 'volume_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_snapshot#tags FsxOpenzfsSnapshot#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_snapshot#tags_all FsxOpenzfsSnapshot#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["FsxOpenzfsSnapshotTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_snapshot#timeouts FsxOpenzfsSnapshot#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["FsxOpenzfsSnapshotTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxOpenzfsSnapshotConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fsx.FsxOpenzfsSnapshotTimeouts",
    jsii_struct_bases=[],
    name_mapping={
        "create": "create",
        "delete": "delete",
        "read": "read",
        "update": "update",
    },
)
class FsxOpenzfsSnapshotTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        read: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_snapshot#create FsxOpenzfsSnapshot#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_snapshot#delete FsxOpenzfsSnapshot#delete}.
        :param read: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_snapshot#read FsxOpenzfsSnapshot#read}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_snapshot#update FsxOpenzfsSnapshot#update}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete
        if read is not None:
            self._values["read"] = read
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_snapshot#create FsxOpenzfsSnapshot#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_snapshot#delete FsxOpenzfsSnapshot#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def read(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_snapshot#read FsxOpenzfsSnapshot#read}.'''
        result = self._values.get("read")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_snapshot#update FsxOpenzfsSnapshot#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxOpenzfsSnapshotTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FsxOpenzfsSnapshotTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxOpenzfsSnapshotTimeoutsOutputReference",
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

    @jsii.member(jsii_name="resetRead")
    def reset_read(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRead", []))

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
    @jsii.member(jsii_name="readInput")
    def read_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "readInput"))

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
    @jsii.member(jsii_name="read")
    def read(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "read"))

    @read.setter
    def read(self, value: builtins.str) -> None:
        jsii.set(self, "read", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        jsii.set(self, "update", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[FsxOpenzfsSnapshotTimeouts]:
        return typing.cast(typing.Optional[FsxOpenzfsSnapshotTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[FsxOpenzfsSnapshotTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


class FsxOpenzfsVolume(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxOpenzfsVolume",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume aws_fsx_openzfs_volume}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        parent_volume_id: builtins.str,
        copy_tags_to_snapshots: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        data_compression_type: typing.Optional[builtins.str] = None,
        nfs_exports: typing.Optional["FsxOpenzfsVolumeNfsExports"] = None,
        origin_snapshot: typing.Optional["FsxOpenzfsVolumeOriginSnapshot"] = None,
        read_only: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        storage_capacity_quota_gib: typing.Optional[jsii.Number] = None,
        storage_capacity_reservation_gib: typing.Optional[jsii.Number] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["FsxOpenzfsVolumeTimeouts"] = None,
        user_and_group_quotas: typing.Optional[typing.Sequence["FsxOpenzfsVolumeUserAndGroupQuotas"]] = None,
        volume_type: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume aws_fsx_openzfs_volume} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#name FsxOpenzfsVolume#name}.
        :param parent_volume_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#parent_volume_id FsxOpenzfsVolume#parent_volume_id}.
        :param copy_tags_to_snapshots: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#copy_tags_to_snapshots FsxOpenzfsVolume#copy_tags_to_snapshots}.
        :param data_compression_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#data_compression_type FsxOpenzfsVolume#data_compression_type}.
        :param nfs_exports: nfs_exports block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#nfs_exports FsxOpenzfsVolume#nfs_exports}
        :param origin_snapshot: origin_snapshot block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#origin_snapshot FsxOpenzfsVolume#origin_snapshot}
        :param read_only: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#read_only FsxOpenzfsVolume#read_only}.
        :param storage_capacity_quota_gib: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#storage_capacity_quota_gib FsxOpenzfsVolume#storage_capacity_quota_gib}.
        :param storage_capacity_reservation_gib: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#storage_capacity_reservation_gib FsxOpenzfsVolume#storage_capacity_reservation_gib}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#tags FsxOpenzfsVolume#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#tags_all FsxOpenzfsVolume#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#timeouts FsxOpenzfsVolume#timeouts}
        :param user_and_group_quotas: user_and_group_quotas block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#user_and_group_quotas FsxOpenzfsVolume#user_and_group_quotas}
        :param volume_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#volume_type FsxOpenzfsVolume#volume_type}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = FsxOpenzfsVolumeConfig(
            name=name,
            parent_volume_id=parent_volume_id,
            copy_tags_to_snapshots=copy_tags_to_snapshots,
            data_compression_type=data_compression_type,
            nfs_exports=nfs_exports,
            origin_snapshot=origin_snapshot,
            read_only=read_only,
            storage_capacity_quota_gib=storage_capacity_quota_gib,
            storage_capacity_reservation_gib=storage_capacity_reservation_gib,
            tags=tags,
            tags_all=tags_all,
            timeouts=timeouts,
            user_and_group_quotas=user_and_group_quotas,
            volume_type=volume_type,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putNfsExports")
    def put_nfs_exports(
        self,
        *,
        client_configurations: typing.Sequence["FsxOpenzfsVolumeNfsExportsClientConfigurations"],
    ) -> None:
        '''
        :param client_configurations: client_configurations block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#client_configurations FsxOpenzfsVolume#client_configurations}
        '''
        value = FsxOpenzfsVolumeNfsExports(client_configurations=client_configurations)

        return typing.cast(None, jsii.invoke(self, "putNfsExports", [value]))

    @jsii.member(jsii_name="putOriginSnapshot")
    def put_origin_snapshot(
        self,
        *,
        copy_strategy: builtins.str,
        snapshot_arn: builtins.str,
    ) -> None:
        '''
        :param copy_strategy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#copy_strategy FsxOpenzfsVolume#copy_strategy}.
        :param snapshot_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#snapshot_arn FsxOpenzfsVolume#snapshot_arn}.
        '''
        value = FsxOpenzfsVolumeOriginSnapshot(
            copy_strategy=copy_strategy, snapshot_arn=snapshot_arn
        )

        return typing.cast(None, jsii.invoke(self, "putOriginSnapshot", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#create FsxOpenzfsVolume#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#delete FsxOpenzfsVolume#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#update FsxOpenzfsVolume#update}.
        '''
        value = FsxOpenzfsVolumeTimeouts(create=create, delete=delete, update=update)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetCopyTagsToSnapshots")
    def reset_copy_tags_to_snapshots(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCopyTagsToSnapshots", []))

    @jsii.member(jsii_name="resetDataCompressionType")
    def reset_data_compression_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataCompressionType", []))

    @jsii.member(jsii_name="resetNfsExports")
    def reset_nfs_exports(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNfsExports", []))

    @jsii.member(jsii_name="resetOriginSnapshot")
    def reset_origin_snapshot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOriginSnapshot", []))

    @jsii.member(jsii_name="resetReadOnly")
    def reset_read_only(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReadOnly", []))

    @jsii.member(jsii_name="resetStorageCapacityQuotaGib")
    def reset_storage_capacity_quota_gib(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageCapacityQuotaGib", []))

    @jsii.member(jsii_name="resetStorageCapacityReservationGib")
    def reset_storage_capacity_reservation_gib(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageCapacityReservationGib", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="resetUserAndGroupQuotas")
    def reset_user_and_group_quotas(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserAndGroupQuotas", []))

    @jsii.member(jsii_name="resetVolumeType")
    def reset_volume_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVolumeType", []))

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
    @jsii.member(jsii_name="nfsExports")
    def nfs_exports(self) -> "FsxOpenzfsVolumeNfsExportsOutputReference":
        return typing.cast("FsxOpenzfsVolumeNfsExportsOutputReference", jsii.get(self, "nfsExports"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="originSnapshot")
    def origin_snapshot(self) -> "FsxOpenzfsVolumeOriginSnapshotOutputReference":
        return typing.cast("FsxOpenzfsVolumeOriginSnapshotOutputReference", jsii.get(self, "originSnapshot"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "FsxOpenzfsVolumeTimeoutsOutputReference":
        return typing.cast("FsxOpenzfsVolumeTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyTagsToSnapshotsInput")
    def copy_tags_to_snapshots_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "copyTagsToSnapshotsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataCompressionTypeInput")
    def data_compression_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dataCompressionTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nfsExportsInput")
    def nfs_exports_input(self) -> typing.Optional["FsxOpenzfsVolumeNfsExports"]:
        return typing.cast(typing.Optional["FsxOpenzfsVolumeNfsExports"], jsii.get(self, "nfsExportsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="originSnapshotInput")
    def origin_snapshot_input(
        self,
    ) -> typing.Optional["FsxOpenzfsVolumeOriginSnapshot"]:
        return typing.cast(typing.Optional["FsxOpenzfsVolumeOriginSnapshot"], jsii.get(self, "originSnapshotInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parentVolumeIdInput")
    def parent_volume_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parentVolumeIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readOnlyInput")
    def read_only_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "readOnlyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageCapacityQuotaGibInput")
    def storage_capacity_quota_gib_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "storageCapacityQuotaGibInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageCapacityReservationGibInput")
    def storage_capacity_reservation_gib_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "storageCapacityReservationGibInput"))

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
    def timeouts_input(self) -> typing.Optional["FsxOpenzfsVolumeTimeouts"]:
        return typing.cast(typing.Optional["FsxOpenzfsVolumeTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userAndGroupQuotasInput")
    def user_and_group_quotas_input(
        self,
    ) -> typing.Optional[typing.List["FsxOpenzfsVolumeUserAndGroupQuotas"]]:
        return typing.cast(typing.Optional[typing.List["FsxOpenzfsVolumeUserAndGroupQuotas"]], jsii.get(self, "userAndGroupQuotasInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeTypeInput")
    def volume_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "volumeTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyTagsToSnapshots")
    def copy_tags_to_snapshots(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "copyTagsToSnapshots"))

    @copy_tags_to_snapshots.setter
    def copy_tags_to_snapshots(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "copyTagsToSnapshots", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataCompressionType")
    def data_compression_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataCompressionType"))

    @data_compression_type.setter
    def data_compression_type(self, value: builtins.str) -> None:
        jsii.set(self, "dataCompressionType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parentVolumeId")
    def parent_volume_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parentVolumeId"))

    @parent_volume_id.setter
    def parent_volume_id(self, value: builtins.str) -> None:
        jsii.set(self, "parentVolumeId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readOnly")
    def read_only(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "readOnly"))

    @read_only.setter
    def read_only(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "readOnly", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageCapacityQuotaGib")
    def storage_capacity_quota_gib(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "storageCapacityQuotaGib"))

    @storage_capacity_quota_gib.setter
    def storage_capacity_quota_gib(self, value: jsii.Number) -> None:
        jsii.set(self, "storageCapacityQuotaGib", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageCapacityReservationGib")
    def storage_capacity_reservation_gib(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "storageCapacityReservationGib"))

    @storage_capacity_reservation_gib.setter
    def storage_capacity_reservation_gib(self, value: jsii.Number) -> None:
        jsii.set(self, "storageCapacityReservationGib", value)

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
    @jsii.member(jsii_name="userAndGroupQuotas")
    def user_and_group_quotas(
        self,
    ) -> typing.List["FsxOpenzfsVolumeUserAndGroupQuotas"]:
        return typing.cast(typing.List["FsxOpenzfsVolumeUserAndGroupQuotas"], jsii.get(self, "userAndGroupQuotas"))

    @user_and_group_quotas.setter
    def user_and_group_quotas(
        self,
        value: typing.List["FsxOpenzfsVolumeUserAndGroupQuotas"],
    ) -> None:
        jsii.set(self, "userAndGroupQuotas", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeType")
    def volume_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "volumeType"))

    @volume_type.setter
    def volume_type(self, value: builtins.str) -> None:
        jsii.set(self, "volumeType", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fsx.FsxOpenzfsVolumeConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "parent_volume_id": "parentVolumeId",
        "copy_tags_to_snapshots": "copyTagsToSnapshots",
        "data_compression_type": "dataCompressionType",
        "nfs_exports": "nfsExports",
        "origin_snapshot": "originSnapshot",
        "read_only": "readOnly",
        "storage_capacity_quota_gib": "storageCapacityQuotaGib",
        "storage_capacity_reservation_gib": "storageCapacityReservationGib",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
        "user_and_group_quotas": "userAndGroupQuotas",
        "volume_type": "volumeType",
    },
)
class FsxOpenzfsVolumeConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        parent_volume_id: builtins.str,
        copy_tags_to_snapshots: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        data_compression_type: typing.Optional[builtins.str] = None,
        nfs_exports: typing.Optional["FsxOpenzfsVolumeNfsExports"] = None,
        origin_snapshot: typing.Optional["FsxOpenzfsVolumeOriginSnapshot"] = None,
        read_only: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        storage_capacity_quota_gib: typing.Optional[jsii.Number] = None,
        storage_capacity_reservation_gib: typing.Optional[jsii.Number] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["FsxOpenzfsVolumeTimeouts"] = None,
        user_and_group_quotas: typing.Optional[typing.Sequence["FsxOpenzfsVolumeUserAndGroupQuotas"]] = None,
        volume_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS File System FSx.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#name FsxOpenzfsVolume#name}.
        :param parent_volume_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#parent_volume_id FsxOpenzfsVolume#parent_volume_id}.
        :param copy_tags_to_snapshots: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#copy_tags_to_snapshots FsxOpenzfsVolume#copy_tags_to_snapshots}.
        :param data_compression_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#data_compression_type FsxOpenzfsVolume#data_compression_type}.
        :param nfs_exports: nfs_exports block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#nfs_exports FsxOpenzfsVolume#nfs_exports}
        :param origin_snapshot: origin_snapshot block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#origin_snapshot FsxOpenzfsVolume#origin_snapshot}
        :param read_only: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#read_only FsxOpenzfsVolume#read_only}.
        :param storage_capacity_quota_gib: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#storage_capacity_quota_gib FsxOpenzfsVolume#storage_capacity_quota_gib}.
        :param storage_capacity_reservation_gib: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#storage_capacity_reservation_gib FsxOpenzfsVolume#storage_capacity_reservation_gib}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#tags FsxOpenzfsVolume#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#tags_all FsxOpenzfsVolume#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#timeouts FsxOpenzfsVolume#timeouts}
        :param user_and_group_quotas: user_and_group_quotas block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#user_and_group_quotas FsxOpenzfsVolume#user_and_group_quotas}
        :param volume_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#volume_type FsxOpenzfsVolume#volume_type}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(nfs_exports, dict):
            nfs_exports = FsxOpenzfsVolumeNfsExports(**nfs_exports)
        if isinstance(origin_snapshot, dict):
            origin_snapshot = FsxOpenzfsVolumeOriginSnapshot(**origin_snapshot)
        if isinstance(timeouts, dict):
            timeouts = FsxOpenzfsVolumeTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "parent_volume_id": parent_volume_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if copy_tags_to_snapshots is not None:
            self._values["copy_tags_to_snapshots"] = copy_tags_to_snapshots
        if data_compression_type is not None:
            self._values["data_compression_type"] = data_compression_type
        if nfs_exports is not None:
            self._values["nfs_exports"] = nfs_exports
        if origin_snapshot is not None:
            self._values["origin_snapshot"] = origin_snapshot
        if read_only is not None:
            self._values["read_only"] = read_only
        if storage_capacity_quota_gib is not None:
            self._values["storage_capacity_quota_gib"] = storage_capacity_quota_gib
        if storage_capacity_reservation_gib is not None:
            self._values["storage_capacity_reservation_gib"] = storage_capacity_reservation_gib
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if timeouts is not None:
            self._values["timeouts"] = timeouts
        if user_and_group_quotas is not None:
            self._values["user_and_group_quotas"] = user_and_group_quotas
        if volume_type is not None:
            self._values["volume_type"] = volume_type

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#name FsxOpenzfsVolume#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parent_volume_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#parent_volume_id FsxOpenzfsVolume#parent_volume_id}.'''
        result = self._values.get("parent_volume_id")
        assert result is not None, "Required property 'parent_volume_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def copy_tags_to_snapshots(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#copy_tags_to_snapshots FsxOpenzfsVolume#copy_tags_to_snapshots}.'''
        result = self._values.get("copy_tags_to_snapshots")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def data_compression_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#data_compression_type FsxOpenzfsVolume#data_compression_type}.'''
        result = self._values.get("data_compression_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nfs_exports(self) -> typing.Optional["FsxOpenzfsVolumeNfsExports"]:
        '''nfs_exports block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#nfs_exports FsxOpenzfsVolume#nfs_exports}
        '''
        result = self._values.get("nfs_exports")
        return typing.cast(typing.Optional["FsxOpenzfsVolumeNfsExports"], result)

    @builtins.property
    def origin_snapshot(self) -> typing.Optional["FsxOpenzfsVolumeOriginSnapshot"]:
        '''origin_snapshot block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#origin_snapshot FsxOpenzfsVolume#origin_snapshot}
        '''
        result = self._values.get("origin_snapshot")
        return typing.cast(typing.Optional["FsxOpenzfsVolumeOriginSnapshot"], result)

    @builtins.property
    def read_only(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#read_only FsxOpenzfsVolume#read_only}.'''
        result = self._values.get("read_only")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def storage_capacity_quota_gib(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#storage_capacity_quota_gib FsxOpenzfsVolume#storage_capacity_quota_gib}.'''
        result = self._values.get("storage_capacity_quota_gib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def storage_capacity_reservation_gib(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#storage_capacity_reservation_gib FsxOpenzfsVolume#storage_capacity_reservation_gib}.'''
        result = self._values.get("storage_capacity_reservation_gib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#tags FsxOpenzfsVolume#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#tags_all FsxOpenzfsVolume#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["FsxOpenzfsVolumeTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#timeouts FsxOpenzfsVolume#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["FsxOpenzfsVolumeTimeouts"], result)

    @builtins.property
    def user_and_group_quotas(
        self,
    ) -> typing.Optional[typing.List["FsxOpenzfsVolumeUserAndGroupQuotas"]]:
        '''user_and_group_quotas block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#user_and_group_quotas FsxOpenzfsVolume#user_and_group_quotas}
        '''
        result = self._values.get("user_and_group_quotas")
        return typing.cast(typing.Optional[typing.List["FsxOpenzfsVolumeUserAndGroupQuotas"]], result)

    @builtins.property
    def volume_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#volume_type FsxOpenzfsVolume#volume_type}.'''
        result = self._values.get("volume_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxOpenzfsVolumeConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fsx.FsxOpenzfsVolumeNfsExports",
    jsii_struct_bases=[],
    name_mapping={"client_configurations": "clientConfigurations"},
)
class FsxOpenzfsVolumeNfsExports:
    def __init__(
        self,
        *,
        client_configurations: typing.Sequence["FsxOpenzfsVolumeNfsExportsClientConfigurations"],
    ) -> None:
        '''
        :param client_configurations: client_configurations block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#client_configurations FsxOpenzfsVolume#client_configurations}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "client_configurations": client_configurations,
        }

    @builtins.property
    def client_configurations(
        self,
    ) -> typing.List["FsxOpenzfsVolumeNfsExportsClientConfigurations"]:
        '''client_configurations block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#client_configurations FsxOpenzfsVolume#client_configurations}
        '''
        result = self._values.get("client_configurations")
        assert result is not None, "Required property 'client_configurations' is missing"
        return typing.cast(typing.List["FsxOpenzfsVolumeNfsExportsClientConfigurations"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxOpenzfsVolumeNfsExports(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fsx.FsxOpenzfsVolumeNfsExportsClientConfigurations",
    jsii_struct_bases=[],
    name_mapping={"clients": "clients", "options": "options"},
)
class FsxOpenzfsVolumeNfsExportsClientConfigurations:
    def __init__(
        self,
        *,
        clients: builtins.str,
        options: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param clients: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#clients FsxOpenzfsVolume#clients}.
        :param options: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#options FsxOpenzfsVolume#options}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "clients": clients,
            "options": options,
        }

    @builtins.property
    def clients(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#clients FsxOpenzfsVolume#clients}.'''
        result = self._values.get("clients")
        assert result is not None, "Required property 'clients' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def options(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#options FsxOpenzfsVolume#options}.'''
        result = self._values.get("options")
        assert result is not None, "Required property 'options' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxOpenzfsVolumeNfsExportsClientConfigurations(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FsxOpenzfsVolumeNfsExportsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxOpenzfsVolumeNfsExportsOutputReference",
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
    @jsii.member(jsii_name="clientConfigurationsInput")
    def client_configurations_input(
        self,
    ) -> typing.Optional[typing.List[FsxOpenzfsVolumeNfsExportsClientConfigurations]]:
        return typing.cast(typing.Optional[typing.List[FsxOpenzfsVolumeNfsExportsClientConfigurations]], jsii.get(self, "clientConfigurationsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientConfigurations")
    def client_configurations(
        self,
    ) -> typing.List[FsxOpenzfsVolumeNfsExportsClientConfigurations]:
        return typing.cast(typing.List[FsxOpenzfsVolumeNfsExportsClientConfigurations], jsii.get(self, "clientConfigurations"))

    @client_configurations.setter
    def client_configurations(
        self,
        value: typing.List[FsxOpenzfsVolumeNfsExportsClientConfigurations],
    ) -> None:
        jsii.set(self, "clientConfigurations", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[FsxOpenzfsVolumeNfsExports]:
        return typing.cast(typing.Optional[FsxOpenzfsVolumeNfsExports], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[FsxOpenzfsVolumeNfsExports],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fsx.FsxOpenzfsVolumeOriginSnapshot",
    jsii_struct_bases=[],
    name_mapping={"copy_strategy": "copyStrategy", "snapshot_arn": "snapshotArn"},
)
class FsxOpenzfsVolumeOriginSnapshot:
    def __init__(
        self,
        *,
        copy_strategy: builtins.str,
        snapshot_arn: builtins.str,
    ) -> None:
        '''
        :param copy_strategy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#copy_strategy FsxOpenzfsVolume#copy_strategy}.
        :param snapshot_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#snapshot_arn FsxOpenzfsVolume#snapshot_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "copy_strategy": copy_strategy,
            "snapshot_arn": snapshot_arn,
        }

    @builtins.property
    def copy_strategy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#copy_strategy FsxOpenzfsVolume#copy_strategy}.'''
        result = self._values.get("copy_strategy")
        assert result is not None, "Required property 'copy_strategy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def snapshot_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#snapshot_arn FsxOpenzfsVolume#snapshot_arn}.'''
        result = self._values.get("snapshot_arn")
        assert result is not None, "Required property 'snapshot_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxOpenzfsVolumeOriginSnapshot(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FsxOpenzfsVolumeOriginSnapshotOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxOpenzfsVolumeOriginSnapshotOutputReference",
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
    @jsii.member(jsii_name="copyStrategyInput")
    def copy_strategy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "copyStrategyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotArnInput")
    def snapshot_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snapshotArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyStrategy")
    def copy_strategy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "copyStrategy"))

    @copy_strategy.setter
    def copy_strategy(self, value: builtins.str) -> None:
        jsii.set(self, "copyStrategy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotArn")
    def snapshot_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snapshotArn"))

    @snapshot_arn.setter
    def snapshot_arn(self, value: builtins.str) -> None:
        jsii.set(self, "snapshotArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[FsxOpenzfsVolumeOriginSnapshot]:
        return typing.cast(typing.Optional[FsxOpenzfsVolumeOriginSnapshot], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[FsxOpenzfsVolumeOriginSnapshot],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fsx.FsxOpenzfsVolumeTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class FsxOpenzfsVolumeTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#create FsxOpenzfsVolume#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#delete FsxOpenzfsVolume#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#update FsxOpenzfsVolume#update}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#create FsxOpenzfsVolume#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#delete FsxOpenzfsVolume#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#update FsxOpenzfsVolume#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxOpenzfsVolumeTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FsxOpenzfsVolumeTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxOpenzfsVolumeTimeoutsOutputReference",
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
    def internal_value(self) -> typing.Optional[FsxOpenzfsVolumeTimeouts]:
        return typing.cast(typing.Optional[FsxOpenzfsVolumeTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[FsxOpenzfsVolumeTimeouts]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fsx.FsxOpenzfsVolumeUserAndGroupQuotas",
    jsii_struct_bases=[],
    name_mapping={
        "id": "id",
        "storage_capacity_quota_gib": "storageCapacityQuotaGib",
        "type": "type",
    },
)
class FsxOpenzfsVolumeUserAndGroupQuotas:
    def __init__(
        self,
        *,
        id: jsii.Number,
        storage_capacity_quota_gib: jsii.Number,
        type: builtins.str,
    ) -> None:
        '''
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#id FsxOpenzfsVolume#id}.
        :param storage_capacity_quota_gib: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#storage_capacity_quota_gib FsxOpenzfsVolume#storage_capacity_quota_gib}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#type FsxOpenzfsVolume#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "id": id,
            "storage_capacity_quota_gib": storage_capacity_quota_gib,
            "type": type,
        }

    @builtins.property
    def id(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#id FsxOpenzfsVolume#id}.'''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def storage_capacity_quota_gib(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#storage_capacity_quota_gib FsxOpenzfsVolume#storage_capacity_quota_gib}.'''
        result = self._values.get("storage_capacity_quota_gib")
        assert result is not None, "Required property 'storage_capacity_quota_gib' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_openzfs_volume#type FsxOpenzfsVolume#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxOpenzfsVolumeUserAndGroupQuotas(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FsxWindowsFileSystem(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxWindowsFileSystem",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system aws_fsx_windows_file_system}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        subnet_ids: typing.Sequence[builtins.str],
        throughput_capacity: jsii.Number,
        active_directory_id: typing.Optional[builtins.str] = None,
        aliases: typing.Optional[typing.Sequence[builtins.str]] = None,
        audit_log_configuration: typing.Optional["FsxWindowsFileSystemAuditLogConfiguration"] = None,
        automatic_backup_retention_days: typing.Optional[jsii.Number] = None,
        backup_id: typing.Optional[builtins.str] = None,
        copy_tags_to_backups: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        daily_automatic_backup_start_time: typing.Optional[builtins.str] = None,
        deployment_type: typing.Optional[builtins.str] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        preferred_subnet_id: typing.Optional[builtins.str] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        self_managed_active_directory: typing.Optional["FsxWindowsFileSystemSelfManagedActiveDirectory"] = None,
        skip_final_backup: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        storage_capacity: typing.Optional[jsii.Number] = None,
        storage_type: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["FsxWindowsFileSystemTimeouts"] = None,
        weekly_maintenance_start_time: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system aws_fsx_windows_file_system} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#subnet_ids FsxWindowsFileSystem#subnet_ids}.
        :param throughput_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#throughput_capacity FsxWindowsFileSystem#throughput_capacity}.
        :param active_directory_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#active_directory_id FsxWindowsFileSystem#active_directory_id}.
        :param aliases: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#aliases FsxWindowsFileSystem#aliases}.
        :param audit_log_configuration: audit_log_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#audit_log_configuration FsxWindowsFileSystem#audit_log_configuration}
        :param automatic_backup_retention_days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#automatic_backup_retention_days FsxWindowsFileSystem#automatic_backup_retention_days}.
        :param backup_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#backup_id FsxWindowsFileSystem#backup_id}.
        :param copy_tags_to_backups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#copy_tags_to_backups FsxWindowsFileSystem#copy_tags_to_backups}.
        :param daily_automatic_backup_start_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#daily_automatic_backup_start_time FsxWindowsFileSystem#daily_automatic_backup_start_time}.
        :param deployment_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#deployment_type FsxWindowsFileSystem#deployment_type}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#kms_key_id FsxWindowsFileSystem#kms_key_id}.
        :param preferred_subnet_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#preferred_subnet_id FsxWindowsFileSystem#preferred_subnet_id}.
        :param security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#security_group_ids FsxWindowsFileSystem#security_group_ids}.
        :param self_managed_active_directory: self_managed_active_directory block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#self_managed_active_directory FsxWindowsFileSystem#self_managed_active_directory}
        :param skip_final_backup: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#skip_final_backup FsxWindowsFileSystem#skip_final_backup}.
        :param storage_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#storage_capacity FsxWindowsFileSystem#storage_capacity}.
        :param storage_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#storage_type FsxWindowsFileSystem#storage_type}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#tags FsxWindowsFileSystem#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#tags_all FsxWindowsFileSystem#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#timeouts FsxWindowsFileSystem#timeouts}
        :param weekly_maintenance_start_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#weekly_maintenance_start_time FsxWindowsFileSystem#weekly_maintenance_start_time}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = FsxWindowsFileSystemConfig(
            subnet_ids=subnet_ids,
            throughput_capacity=throughput_capacity,
            active_directory_id=active_directory_id,
            aliases=aliases,
            audit_log_configuration=audit_log_configuration,
            automatic_backup_retention_days=automatic_backup_retention_days,
            backup_id=backup_id,
            copy_tags_to_backups=copy_tags_to_backups,
            daily_automatic_backup_start_time=daily_automatic_backup_start_time,
            deployment_type=deployment_type,
            kms_key_id=kms_key_id,
            preferred_subnet_id=preferred_subnet_id,
            security_group_ids=security_group_ids,
            self_managed_active_directory=self_managed_active_directory,
            skip_final_backup=skip_final_backup,
            storage_capacity=storage_capacity,
            storage_type=storage_type,
            tags=tags,
            tags_all=tags_all,
            timeouts=timeouts,
            weekly_maintenance_start_time=weekly_maintenance_start_time,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putAuditLogConfiguration")
    def put_audit_log_configuration(
        self,
        *,
        audit_log_destination: typing.Optional[builtins.str] = None,
        file_access_audit_log_level: typing.Optional[builtins.str] = None,
        file_share_access_audit_log_level: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param audit_log_destination: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#audit_log_destination FsxWindowsFileSystem#audit_log_destination}.
        :param file_access_audit_log_level: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#file_access_audit_log_level FsxWindowsFileSystem#file_access_audit_log_level}.
        :param file_share_access_audit_log_level: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#file_share_access_audit_log_level FsxWindowsFileSystem#file_share_access_audit_log_level}.
        '''
        value = FsxWindowsFileSystemAuditLogConfiguration(
            audit_log_destination=audit_log_destination,
            file_access_audit_log_level=file_access_audit_log_level,
            file_share_access_audit_log_level=file_share_access_audit_log_level,
        )

        return typing.cast(None, jsii.invoke(self, "putAuditLogConfiguration", [value]))

    @jsii.member(jsii_name="putSelfManagedActiveDirectory")
    def put_self_managed_active_directory(
        self,
        *,
        dns_ips: typing.Sequence[builtins.str],
        domain_name: builtins.str,
        password: builtins.str,
        username: builtins.str,
        file_system_administrators_group: typing.Optional[builtins.str] = None,
        organizational_unit_distinguished_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dns_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#dns_ips FsxWindowsFileSystem#dns_ips}.
        :param domain_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#domain_name FsxWindowsFileSystem#domain_name}.
        :param password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#password FsxWindowsFileSystem#password}.
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#username FsxWindowsFileSystem#username}.
        :param file_system_administrators_group: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#file_system_administrators_group FsxWindowsFileSystem#file_system_administrators_group}.
        :param organizational_unit_distinguished_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#organizational_unit_distinguished_name FsxWindowsFileSystem#organizational_unit_distinguished_name}.
        '''
        value = FsxWindowsFileSystemSelfManagedActiveDirectory(
            dns_ips=dns_ips,
            domain_name=domain_name,
            password=password,
            username=username,
            file_system_administrators_group=file_system_administrators_group,
            organizational_unit_distinguished_name=organizational_unit_distinguished_name,
        )

        return typing.cast(None, jsii.invoke(self, "putSelfManagedActiveDirectory", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#create FsxWindowsFileSystem#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#delete FsxWindowsFileSystem#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#update FsxWindowsFileSystem#update}.
        '''
        value = FsxWindowsFileSystemTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetActiveDirectoryId")
    def reset_active_directory_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetActiveDirectoryId", []))

    @jsii.member(jsii_name="resetAliases")
    def reset_aliases(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAliases", []))

    @jsii.member(jsii_name="resetAuditLogConfiguration")
    def reset_audit_log_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuditLogConfiguration", []))

    @jsii.member(jsii_name="resetAutomaticBackupRetentionDays")
    def reset_automatic_backup_retention_days(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutomaticBackupRetentionDays", []))

    @jsii.member(jsii_name="resetBackupId")
    def reset_backup_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackupId", []))

    @jsii.member(jsii_name="resetCopyTagsToBackups")
    def reset_copy_tags_to_backups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCopyTagsToBackups", []))

    @jsii.member(jsii_name="resetDailyAutomaticBackupStartTime")
    def reset_daily_automatic_backup_start_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDailyAutomaticBackupStartTime", []))

    @jsii.member(jsii_name="resetDeploymentType")
    def reset_deployment_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeploymentType", []))

    @jsii.member(jsii_name="resetKmsKeyId")
    def reset_kms_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyId", []))

    @jsii.member(jsii_name="resetPreferredSubnetId")
    def reset_preferred_subnet_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreferredSubnetId", []))

    @jsii.member(jsii_name="resetSecurityGroupIds")
    def reset_security_group_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityGroupIds", []))

    @jsii.member(jsii_name="resetSelfManagedActiveDirectory")
    def reset_self_managed_active_directory(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSelfManagedActiveDirectory", []))

    @jsii.member(jsii_name="resetSkipFinalBackup")
    def reset_skip_final_backup(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSkipFinalBackup", []))

    @jsii.member(jsii_name="resetStorageCapacity")
    def reset_storage_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageCapacity", []))

    @jsii.member(jsii_name="resetStorageType")
    def reset_storage_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageType", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="resetWeeklyMaintenanceStartTime")
    def reset_weekly_maintenance_start_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWeeklyMaintenanceStartTime", []))

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
    @jsii.member(jsii_name="auditLogConfiguration")
    def audit_log_configuration(
        self,
    ) -> "FsxWindowsFileSystemAuditLogConfigurationOutputReference":
        return typing.cast("FsxWindowsFileSystemAuditLogConfigurationOutputReference", jsii.get(self, "auditLogConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsName")
    def dns_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dnsName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkInterfaceIds")
    def network_interface_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "networkInterfaceIds"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerId")
    def owner_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ownerId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredFileServerIp")
    def preferred_file_server_ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preferredFileServerIp"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="remoteAdministrationEndpoint")
    def remote_administration_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "remoteAdministrationEndpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="selfManagedActiveDirectory")
    def self_managed_active_directory(
        self,
    ) -> "FsxWindowsFileSystemSelfManagedActiveDirectoryOutputReference":
        return typing.cast("FsxWindowsFileSystemSelfManagedActiveDirectoryOutputReference", jsii.get(self, "selfManagedActiveDirectory"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "FsxWindowsFileSystemTimeoutsOutputReference":
        return typing.cast("FsxWindowsFileSystemTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="activeDirectoryIdInput")
    def active_directory_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "activeDirectoryIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aliasesInput")
    def aliases_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "aliasesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="auditLogConfigurationInput")
    def audit_log_configuration_input(
        self,
    ) -> typing.Optional["FsxWindowsFileSystemAuditLogConfiguration"]:
        return typing.cast(typing.Optional["FsxWindowsFileSystemAuditLogConfiguration"], jsii.get(self, "auditLogConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="automaticBackupRetentionDaysInput")
    def automatic_backup_retention_days_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "automaticBackupRetentionDaysInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupIdInput")
    def backup_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backupIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyTagsToBackupsInput")
    def copy_tags_to_backups_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "copyTagsToBackupsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dailyAutomaticBackupStartTimeInput")
    def daily_automatic_backup_start_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dailyAutomaticBackupStartTimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentTypeInput")
    def deployment_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deploymentTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyIdInput")
    def kms_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredSubnetIdInput")
    def preferred_subnet_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preferredSubnetIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIdsInput")
    def security_group_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="selfManagedActiveDirectoryInput")
    def self_managed_active_directory_input(
        self,
    ) -> typing.Optional["FsxWindowsFileSystemSelfManagedActiveDirectory"]:
        return typing.cast(typing.Optional["FsxWindowsFileSystemSelfManagedActiveDirectory"], jsii.get(self, "selfManagedActiveDirectoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="skipFinalBackupInput")
    def skip_final_backup_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "skipFinalBackupInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageCapacityInput")
    def storage_capacity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "storageCapacityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageTypeInput")
    def storage_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageTypeInput"))

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
    @jsii.member(jsii_name="throughputCapacityInput")
    def throughput_capacity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "throughputCapacityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["FsxWindowsFileSystemTimeouts"]:
        return typing.cast(typing.Optional["FsxWindowsFileSystemTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="weeklyMaintenanceStartTimeInput")
    def weekly_maintenance_start_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "weeklyMaintenanceStartTimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="activeDirectoryId")
    def active_directory_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "activeDirectoryId"))

    @active_directory_id.setter
    def active_directory_id(self, value: builtins.str) -> None:
        jsii.set(self, "activeDirectoryId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aliases")
    def aliases(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "aliases"))

    @aliases.setter
    def aliases(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "aliases", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="automaticBackupRetentionDays")
    def automatic_backup_retention_days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "automaticBackupRetentionDays"))

    @automatic_backup_retention_days.setter
    def automatic_backup_retention_days(self, value: jsii.Number) -> None:
        jsii.set(self, "automaticBackupRetentionDays", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupId")
    def backup_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backupId"))

    @backup_id.setter
    def backup_id(self, value: builtins.str) -> None:
        jsii.set(self, "backupId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyTagsToBackups")
    def copy_tags_to_backups(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "copyTagsToBackups"))

    @copy_tags_to_backups.setter
    def copy_tags_to_backups(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "copyTagsToBackups", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dailyAutomaticBackupStartTime")
    def daily_automatic_backup_start_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dailyAutomaticBackupStartTime"))

    @daily_automatic_backup_start_time.setter
    def daily_automatic_backup_start_time(self, value: builtins.str) -> None:
        jsii.set(self, "dailyAutomaticBackupStartTime", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentType")
    def deployment_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deploymentType"))

    @deployment_type.setter
    def deployment_type(self, value: builtins.str) -> None:
        jsii.set(self, "deploymentType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @kms_key_id.setter
    def kms_key_id(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredSubnetId")
    def preferred_subnet_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preferredSubnetId"))

    @preferred_subnet_id.setter
    def preferred_subnet_id(self, value: builtins.str) -> None:
        jsii.set(self, "preferredSubnetId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroupIds"))

    @security_group_ids.setter
    def security_group_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "securityGroupIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="skipFinalBackup")
    def skip_final_backup(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "skipFinalBackup"))

    @skip_final_backup.setter
    def skip_final_backup(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "skipFinalBackup", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageCapacity")
    def storage_capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "storageCapacity"))

    @storage_capacity.setter
    def storage_capacity(self, value: jsii.Number) -> None:
        jsii.set(self, "storageCapacity", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageType")
    def storage_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageType"))

    @storage_type.setter
    def storage_type(self, value: builtins.str) -> None:
        jsii.set(self, "storageType", value)

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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="throughputCapacity")
    def throughput_capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "throughputCapacity"))

    @throughput_capacity.setter
    def throughput_capacity(self, value: jsii.Number) -> None:
        jsii.set(self, "throughputCapacity", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="weeklyMaintenanceStartTime")
    def weekly_maintenance_start_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "weeklyMaintenanceStartTime"))

    @weekly_maintenance_start_time.setter
    def weekly_maintenance_start_time(self, value: builtins.str) -> None:
        jsii.set(self, "weeklyMaintenanceStartTime", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fsx.FsxWindowsFileSystemAuditLogConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "audit_log_destination": "auditLogDestination",
        "file_access_audit_log_level": "fileAccessAuditLogLevel",
        "file_share_access_audit_log_level": "fileShareAccessAuditLogLevel",
    },
)
class FsxWindowsFileSystemAuditLogConfiguration:
    def __init__(
        self,
        *,
        audit_log_destination: typing.Optional[builtins.str] = None,
        file_access_audit_log_level: typing.Optional[builtins.str] = None,
        file_share_access_audit_log_level: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param audit_log_destination: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#audit_log_destination FsxWindowsFileSystem#audit_log_destination}.
        :param file_access_audit_log_level: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#file_access_audit_log_level FsxWindowsFileSystem#file_access_audit_log_level}.
        :param file_share_access_audit_log_level: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#file_share_access_audit_log_level FsxWindowsFileSystem#file_share_access_audit_log_level}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if audit_log_destination is not None:
            self._values["audit_log_destination"] = audit_log_destination
        if file_access_audit_log_level is not None:
            self._values["file_access_audit_log_level"] = file_access_audit_log_level
        if file_share_access_audit_log_level is not None:
            self._values["file_share_access_audit_log_level"] = file_share_access_audit_log_level

    @builtins.property
    def audit_log_destination(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#audit_log_destination FsxWindowsFileSystem#audit_log_destination}.'''
        result = self._values.get("audit_log_destination")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def file_access_audit_log_level(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#file_access_audit_log_level FsxWindowsFileSystem#file_access_audit_log_level}.'''
        result = self._values.get("file_access_audit_log_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def file_share_access_audit_log_level(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#file_share_access_audit_log_level FsxWindowsFileSystem#file_share_access_audit_log_level}.'''
        result = self._values.get("file_share_access_audit_log_level")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxWindowsFileSystemAuditLogConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FsxWindowsFileSystemAuditLogConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxWindowsFileSystemAuditLogConfigurationOutputReference",
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

    @jsii.member(jsii_name="resetAuditLogDestination")
    def reset_audit_log_destination(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuditLogDestination", []))

    @jsii.member(jsii_name="resetFileAccessAuditLogLevel")
    def reset_file_access_audit_log_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFileAccessAuditLogLevel", []))

    @jsii.member(jsii_name="resetFileShareAccessAuditLogLevel")
    def reset_file_share_access_audit_log_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFileShareAccessAuditLogLevel", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="auditLogDestinationInput")
    def audit_log_destination_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "auditLogDestinationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileAccessAuditLogLevelInput")
    def file_access_audit_log_level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fileAccessAuditLogLevelInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileShareAccessAuditLogLevelInput")
    def file_share_access_audit_log_level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fileShareAccessAuditLogLevelInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="auditLogDestination")
    def audit_log_destination(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "auditLogDestination"))

    @audit_log_destination.setter
    def audit_log_destination(self, value: builtins.str) -> None:
        jsii.set(self, "auditLogDestination", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileAccessAuditLogLevel")
    def file_access_audit_log_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileAccessAuditLogLevel"))

    @file_access_audit_log_level.setter
    def file_access_audit_log_level(self, value: builtins.str) -> None:
        jsii.set(self, "fileAccessAuditLogLevel", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileShareAccessAuditLogLevel")
    def file_share_access_audit_log_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileShareAccessAuditLogLevel"))

    @file_share_access_audit_log_level.setter
    def file_share_access_audit_log_level(self, value: builtins.str) -> None:
        jsii.set(self, "fileShareAccessAuditLogLevel", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[FsxWindowsFileSystemAuditLogConfiguration]:
        return typing.cast(typing.Optional[FsxWindowsFileSystemAuditLogConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[FsxWindowsFileSystemAuditLogConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fsx.FsxWindowsFileSystemConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "subnet_ids": "subnetIds",
        "throughput_capacity": "throughputCapacity",
        "active_directory_id": "activeDirectoryId",
        "aliases": "aliases",
        "audit_log_configuration": "auditLogConfiguration",
        "automatic_backup_retention_days": "automaticBackupRetentionDays",
        "backup_id": "backupId",
        "copy_tags_to_backups": "copyTagsToBackups",
        "daily_automatic_backup_start_time": "dailyAutomaticBackupStartTime",
        "deployment_type": "deploymentType",
        "kms_key_id": "kmsKeyId",
        "preferred_subnet_id": "preferredSubnetId",
        "security_group_ids": "securityGroupIds",
        "self_managed_active_directory": "selfManagedActiveDirectory",
        "skip_final_backup": "skipFinalBackup",
        "storage_capacity": "storageCapacity",
        "storage_type": "storageType",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
        "weekly_maintenance_start_time": "weeklyMaintenanceStartTime",
    },
)
class FsxWindowsFileSystemConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        subnet_ids: typing.Sequence[builtins.str],
        throughput_capacity: jsii.Number,
        active_directory_id: typing.Optional[builtins.str] = None,
        aliases: typing.Optional[typing.Sequence[builtins.str]] = None,
        audit_log_configuration: typing.Optional[FsxWindowsFileSystemAuditLogConfiguration] = None,
        automatic_backup_retention_days: typing.Optional[jsii.Number] = None,
        backup_id: typing.Optional[builtins.str] = None,
        copy_tags_to_backups: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        daily_automatic_backup_start_time: typing.Optional[builtins.str] = None,
        deployment_type: typing.Optional[builtins.str] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        preferred_subnet_id: typing.Optional[builtins.str] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        self_managed_active_directory: typing.Optional["FsxWindowsFileSystemSelfManagedActiveDirectory"] = None,
        skip_final_backup: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        storage_capacity: typing.Optional[jsii.Number] = None,
        storage_type: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["FsxWindowsFileSystemTimeouts"] = None,
        weekly_maintenance_start_time: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS File System FSx.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#subnet_ids FsxWindowsFileSystem#subnet_ids}.
        :param throughput_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#throughput_capacity FsxWindowsFileSystem#throughput_capacity}.
        :param active_directory_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#active_directory_id FsxWindowsFileSystem#active_directory_id}.
        :param aliases: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#aliases FsxWindowsFileSystem#aliases}.
        :param audit_log_configuration: audit_log_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#audit_log_configuration FsxWindowsFileSystem#audit_log_configuration}
        :param automatic_backup_retention_days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#automatic_backup_retention_days FsxWindowsFileSystem#automatic_backup_retention_days}.
        :param backup_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#backup_id FsxWindowsFileSystem#backup_id}.
        :param copy_tags_to_backups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#copy_tags_to_backups FsxWindowsFileSystem#copy_tags_to_backups}.
        :param daily_automatic_backup_start_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#daily_automatic_backup_start_time FsxWindowsFileSystem#daily_automatic_backup_start_time}.
        :param deployment_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#deployment_type FsxWindowsFileSystem#deployment_type}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#kms_key_id FsxWindowsFileSystem#kms_key_id}.
        :param preferred_subnet_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#preferred_subnet_id FsxWindowsFileSystem#preferred_subnet_id}.
        :param security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#security_group_ids FsxWindowsFileSystem#security_group_ids}.
        :param self_managed_active_directory: self_managed_active_directory block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#self_managed_active_directory FsxWindowsFileSystem#self_managed_active_directory}
        :param skip_final_backup: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#skip_final_backup FsxWindowsFileSystem#skip_final_backup}.
        :param storage_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#storage_capacity FsxWindowsFileSystem#storage_capacity}.
        :param storage_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#storage_type FsxWindowsFileSystem#storage_type}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#tags FsxWindowsFileSystem#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#tags_all FsxWindowsFileSystem#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#timeouts FsxWindowsFileSystem#timeouts}
        :param weekly_maintenance_start_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#weekly_maintenance_start_time FsxWindowsFileSystem#weekly_maintenance_start_time}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(audit_log_configuration, dict):
            audit_log_configuration = FsxWindowsFileSystemAuditLogConfiguration(**audit_log_configuration)
        if isinstance(self_managed_active_directory, dict):
            self_managed_active_directory = FsxWindowsFileSystemSelfManagedActiveDirectory(**self_managed_active_directory)
        if isinstance(timeouts, dict):
            timeouts = FsxWindowsFileSystemTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "subnet_ids": subnet_ids,
            "throughput_capacity": throughput_capacity,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if active_directory_id is not None:
            self._values["active_directory_id"] = active_directory_id
        if aliases is not None:
            self._values["aliases"] = aliases
        if audit_log_configuration is not None:
            self._values["audit_log_configuration"] = audit_log_configuration
        if automatic_backup_retention_days is not None:
            self._values["automatic_backup_retention_days"] = automatic_backup_retention_days
        if backup_id is not None:
            self._values["backup_id"] = backup_id
        if copy_tags_to_backups is not None:
            self._values["copy_tags_to_backups"] = copy_tags_to_backups
        if daily_automatic_backup_start_time is not None:
            self._values["daily_automatic_backup_start_time"] = daily_automatic_backup_start_time
        if deployment_type is not None:
            self._values["deployment_type"] = deployment_type
        if kms_key_id is not None:
            self._values["kms_key_id"] = kms_key_id
        if preferred_subnet_id is not None:
            self._values["preferred_subnet_id"] = preferred_subnet_id
        if security_group_ids is not None:
            self._values["security_group_ids"] = security_group_ids
        if self_managed_active_directory is not None:
            self._values["self_managed_active_directory"] = self_managed_active_directory
        if skip_final_backup is not None:
            self._values["skip_final_backup"] = skip_final_backup
        if storage_capacity is not None:
            self._values["storage_capacity"] = storage_capacity
        if storage_type is not None:
            self._values["storage_type"] = storage_type
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if timeouts is not None:
            self._values["timeouts"] = timeouts
        if weekly_maintenance_start_time is not None:
            self._values["weekly_maintenance_start_time"] = weekly_maintenance_start_time

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
    def subnet_ids(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#subnet_ids FsxWindowsFileSystem#subnet_ids}.'''
        result = self._values.get("subnet_ids")
        assert result is not None, "Required property 'subnet_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def throughput_capacity(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#throughput_capacity FsxWindowsFileSystem#throughput_capacity}.'''
        result = self._values.get("throughput_capacity")
        assert result is not None, "Required property 'throughput_capacity' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def active_directory_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#active_directory_id FsxWindowsFileSystem#active_directory_id}.'''
        result = self._values.get("active_directory_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aliases(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#aliases FsxWindowsFileSystem#aliases}.'''
        result = self._values.get("aliases")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def audit_log_configuration(
        self,
    ) -> typing.Optional[FsxWindowsFileSystemAuditLogConfiguration]:
        '''audit_log_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#audit_log_configuration FsxWindowsFileSystem#audit_log_configuration}
        '''
        result = self._values.get("audit_log_configuration")
        return typing.cast(typing.Optional[FsxWindowsFileSystemAuditLogConfiguration], result)

    @builtins.property
    def automatic_backup_retention_days(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#automatic_backup_retention_days FsxWindowsFileSystem#automatic_backup_retention_days}.'''
        result = self._values.get("automatic_backup_retention_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def backup_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#backup_id FsxWindowsFileSystem#backup_id}.'''
        result = self._values.get("backup_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def copy_tags_to_backups(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#copy_tags_to_backups FsxWindowsFileSystem#copy_tags_to_backups}.'''
        result = self._values.get("copy_tags_to_backups")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def daily_automatic_backup_start_time(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#daily_automatic_backup_start_time FsxWindowsFileSystem#daily_automatic_backup_start_time}.'''
        result = self._values.get("daily_automatic_backup_start_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def deployment_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#deployment_type FsxWindowsFileSystem#deployment_type}.'''
        result = self._values.get("deployment_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#kms_key_id FsxWindowsFileSystem#kms_key_id}.'''
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def preferred_subnet_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#preferred_subnet_id FsxWindowsFileSystem#preferred_subnet_id}.'''
        result = self._values.get("preferred_subnet_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#security_group_ids FsxWindowsFileSystem#security_group_ids}.'''
        result = self._values.get("security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def self_managed_active_directory(
        self,
    ) -> typing.Optional["FsxWindowsFileSystemSelfManagedActiveDirectory"]:
        '''self_managed_active_directory block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#self_managed_active_directory FsxWindowsFileSystem#self_managed_active_directory}
        '''
        result = self._values.get("self_managed_active_directory")
        return typing.cast(typing.Optional["FsxWindowsFileSystemSelfManagedActiveDirectory"], result)

    @builtins.property
    def skip_final_backup(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#skip_final_backup FsxWindowsFileSystem#skip_final_backup}.'''
        result = self._values.get("skip_final_backup")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def storage_capacity(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#storage_capacity FsxWindowsFileSystem#storage_capacity}.'''
        result = self._values.get("storage_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def storage_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#storage_type FsxWindowsFileSystem#storage_type}.'''
        result = self._values.get("storage_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#tags FsxWindowsFileSystem#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#tags_all FsxWindowsFileSystem#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["FsxWindowsFileSystemTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#timeouts FsxWindowsFileSystem#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["FsxWindowsFileSystemTimeouts"], result)

    @builtins.property
    def weekly_maintenance_start_time(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#weekly_maintenance_start_time FsxWindowsFileSystem#weekly_maintenance_start_time}.'''
        result = self._values.get("weekly_maintenance_start_time")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxWindowsFileSystemConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fsx.FsxWindowsFileSystemSelfManagedActiveDirectory",
    jsii_struct_bases=[],
    name_mapping={
        "dns_ips": "dnsIps",
        "domain_name": "domainName",
        "password": "password",
        "username": "username",
        "file_system_administrators_group": "fileSystemAdministratorsGroup",
        "organizational_unit_distinguished_name": "organizationalUnitDistinguishedName",
    },
)
class FsxWindowsFileSystemSelfManagedActiveDirectory:
    def __init__(
        self,
        *,
        dns_ips: typing.Sequence[builtins.str],
        domain_name: builtins.str,
        password: builtins.str,
        username: builtins.str,
        file_system_administrators_group: typing.Optional[builtins.str] = None,
        organizational_unit_distinguished_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dns_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#dns_ips FsxWindowsFileSystem#dns_ips}.
        :param domain_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#domain_name FsxWindowsFileSystem#domain_name}.
        :param password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#password FsxWindowsFileSystem#password}.
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#username FsxWindowsFileSystem#username}.
        :param file_system_administrators_group: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#file_system_administrators_group FsxWindowsFileSystem#file_system_administrators_group}.
        :param organizational_unit_distinguished_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#organizational_unit_distinguished_name FsxWindowsFileSystem#organizational_unit_distinguished_name}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "dns_ips": dns_ips,
            "domain_name": domain_name,
            "password": password,
            "username": username,
        }
        if file_system_administrators_group is not None:
            self._values["file_system_administrators_group"] = file_system_administrators_group
        if organizational_unit_distinguished_name is not None:
            self._values["organizational_unit_distinguished_name"] = organizational_unit_distinguished_name

    @builtins.property
    def dns_ips(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#dns_ips FsxWindowsFileSystem#dns_ips}.'''
        result = self._values.get("dns_ips")
        assert result is not None, "Required property 'dns_ips' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def domain_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#domain_name FsxWindowsFileSystem#domain_name}.'''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def password(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#password FsxWindowsFileSystem#password}.'''
        result = self._values.get("password")
        assert result is not None, "Required property 'password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#username FsxWindowsFileSystem#username}.'''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def file_system_administrators_group(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#file_system_administrators_group FsxWindowsFileSystem#file_system_administrators_group}.'''
        result = self._values.get("file_system_administrators_group")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def organizational_unit_distinguished_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#organizational_unit_distinguished_name FsxWindowsFileSystem#organizational_unit_distinguished_name}.'''
        result = self._values.get("organizational_unit_distinguished_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxWindowsFileSystemSelfManagedActiveDirectory(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FsxWindowsFileSystemSelfManagedActiveDirectoryOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxWindowsFileSystemSelfManagedActiveDirectoryOutputReference",
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

    @jsii.member(jsii_name="resetFileSystemAdministratorsGroup")
    def reset_file_system_administrators_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFileSystemAdministratorsGroup", []))

    @jsii.member(jsii_name="resetOrganizationalUnitDistinguishedName")
    def reset_organizational_unit_distinguished_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrganizationalUnitDistinguishedName", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsIpsInput")
    def dns_ips_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "dnsIpsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainNameInput")
    def domain_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemAdministratorsGroupInput")
    def file_system_administrators_group_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fileSystemAdministratorsGroupInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitDistinguishedNameInput")
    def organizational_unit_distinguished_name_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "organizationalUnitDistinguishedNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsIps")
    def dns_ips(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dnsIps"))

    @dns_ips.setter
    def dns_ips(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "dnsIps", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @domain_name.setter
    def domain_name(self, value: builtins.str) -> None:
        jsii.set(self, "domainName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemAdministratorsGroup")
    def file_system_administrators_group(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileSystemAdministratorsGroup"))

    @file_system_administrators_group.setter
    def file_system_administrators_group(self, value: builtins.str) -> None:
        jsii.set(self, "fileSystemAdministratorsGroup", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitDistinguishedName")
    def organizational_unit_distinguished_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "organizationalUnitDistinguishedName"))

    @organizational_unit_distinguished_name.setter
    def organizational_unit_distinguished_name(self, value: builtins.str) -> None:
        jsii.set(self, "organizationalUnitDistinguishedName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        jsii.set(self, "password", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        jsii.set(self, "username", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[FsxWindowsFileSystemSelfManagedActiveDirectory]:
        return typing.cast(typing.Optional[FsxWindowsFileSystemSelfManagedActiveDirectory], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[FsxWindowsFileSystemSelfManagedActiveDirectory],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.fsx.FsxWindowsFileSystemTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class FsxWindowsFileSystemTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#create FsxWindowsFileSystem#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#delete FsxWindowsFileSystem#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#update FsxWindowsFileSystem#update}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#create FsxWindowsFileSystem#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#delete FsxWindowsFileSystem#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/fsx_windows_file_system#update FsxWindowsFileSystem#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FsxWindowsFileSystemTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FsxWindowsFileSystemTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.fsx.FsxWindowsFileSystemTimeoutsOutputReference",
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
    def internal_value(self) -> typing.Optional[FsxWindowsFileSystemTimeouts]:
        return typing.cast(typing.Optional[FsxWindowsFileSystemTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[FsxWindowsFileSystemTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


__all__ = [
    "FsxBackup",
    "FsxBackupConfig",
    "FsxBackupTimeouts",
    "FsxBackupTimeoutsOutputReference",
    "FsxLustreFileSystem",
    "FsxLustreFileSystemConfig",
    "FsxLustreFileSystemTimeouts",
    "FsxLustreFileSystemTimeoutsOutputReference",
    "FsxOntapFileSystem",
    "FsxOntapFileSystemConfig",
    "FsxOntapFileSystemDiskIopsConfiguration",
    "FsxOntapFileSystemDiskIopsConfigurationOutputReference",
    "FsxOntapFileSystemEndpoints",
    "FsxOntapFileSystemEndpointsIntercluster",
    "FsxOntapFileSystemEndpointsManagement",
    "FsxOntapFileSystemTimeouts",
    "FsxOntapFileSystemTimeoutsOutputReference",
    "FsxOntapStorageVirtualMachine",
    "FsxOntapStorageVirtualMachineActiveDirectoryConfiguration",
    "FsxOntapStorageVirtualMachineActiveDirectoryConfigurationOutputReference",
    "FsxOntapStorageVirtualMachineActiveDirectoryConfigurationSelfManagedActiveDirectoryConfiguration",
    "FsxOntapStorageVirtualMachineActiveDirectoryConfigurationSelfManagedActiveDirectoryConfigurationOutputReference",
    "FsxOntapStorageVirtualMachineConfig",
    "FsxOntapStorageVirtualMachineEndpoints",
    "FsxOntapStorageVirtualMachineEndpointsIscsi",
    "FsxOntapStorageVirtualMachineEndpointsManagement",
    "FsxOntapStorageVirtualMachineEndpointsNfs",
    "FsxOntapStorageVirtualMachineEndpointsSmb",
    "FsxOntapStorageVirtualMachineTimeouts",
    "FsxOntapStorageVirtualMachineTimeoutsOutputReference",
    "FsxOntapVolume",
    "FsxOntapVolumeConfig",
    "FsxOntapVolumeTieringPolicy",
    "FsxOntapVolumeTieringPolicyOutputReference",
    "FsxOntapVolumeTimeouts",
    "FsxOntapVolumeTimeoutsOutputReference",
    "FsxOpenzfsFileSystem",
    "FsxOpenzfsFileSystemConfig",
    "FsxOpenzfsFileSystemDiskIopsConfiguration",
    "FsxOpenzfsFileSystemDiskIopsConfigurationOutputReference",
    "FsxOpenzfsFileSystemRootVolumeConfiguration",
    "FsxOpenzfsFileSystemRootVolumeConfigurationNfsExports",
    "FsxOpenzfsFileSystemRootVolumeConfigurationNfsExportsClientConfigurations",
    "FsxOpenzfsFileSystemRootVolumeConfigurationNfsExportsOutputReference",
    "FsxOpenzfsFileSystemRootVolumeConfigurationOutputReference",
    "FsxOpenzfsFileSystemRootVolumeConfigurationUserAndGroupQuotas",
    "FsxOpenzfsFileSystemTimeouts",
    "FsxOpenzfsFileSystemTimeoutsOutputReference",
    "FsxOpenzfsSnapshot",
    "FsxOpenzfsSnapshotConfig",
    "FsxOpenzfsSnapshotTimeouts",
    "FsxOpenzfsSnapshotTimeoutsOutputReference",
    "FsxOpenzfsVolume",
    "FsxOpenzfsVolumeConfig",
    "FsxOpenzfsVolumeNfsExports",
    "FsxOpenzfsVolumeNfsExportsClientConfigurations",
    "FsxOpenzfsVolumeNfsExportsOutputReference",
    "FsxOpenzfsVolumeOriginSnapshot",
    "FsxOpenzfsVolumeOriginSnapshotOutputReference",
    "FsxOpenzfsVolumeTimeouts",
    "FsxOpenzfsVolumeTimeoutsOutputReference",
    "FsxOpenzfsVolumeUserAndGroupQuotas",
    "FsxWindowsFileSystem",
    "FsxWindowsFileSystemAuditLogConfiguration",
    "FsxWindowsFileSystemAuditLogConfigurationOutputReference",
    "FsxWindowsFileSystemConfig",
    "FsxWindowsFileSystemSelfManagedActiveDirectory",
    "FsxWindowsFileSystemSelfManagedActiveDirectoryOutputReference",
    "FsxWindowsFileSystemTimeouts",
    "FsxWindowsFileSystemTimeoutsOutputReference",
]

publication.publish()
