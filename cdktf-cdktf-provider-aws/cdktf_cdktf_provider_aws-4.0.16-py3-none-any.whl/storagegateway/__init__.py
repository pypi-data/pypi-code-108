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


class DataAwsStoragegatewayLocalDisk(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.storagegateway.DataAwsStoragegatewayLocalDisk",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/storagegateway_local_disk aws_storagegateway_local_disk}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        gateway_arn: builtins.str,
        disk_node: typing.Optional[builtins.str] = None,
        disk_path: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/storagegateway_local_disk aws_storagegateway_local_disk} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param gateway_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/storagegateway_local_disk#gateway_arn DataAwsStoragegatewayLocalDisk#gateway_arn}.
        :param disk_node: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/storagegateway_local_disk#disk_node DataAwsStoragegatewayLocalDisk#disk_node}.
        :param disk_path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/storagegateway_local_disk#disk_path DataAwsStoragegatewayLocalDisk#disk_path}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsStoragegatewayLocalDiskConfig(
            gateway_arn=gateway_arn,
            disk_node=disk_node,
            disk_path=disk_path,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDiskNode")
    def reset_disk_node(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiskNode", []))

    @jsii.member(jsii_name="resetDiskPath")
    def reset_disk_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiskPath", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="diskId")
    def disk_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "diskId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="diskNodeInput")
    def disk_node_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "diskNodeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="diskPathInput")
    def disk_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "diskPathInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gatewayArnInput")
    def gateway_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gatewayArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="diskNode")
    def disk_node(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "diskNode"))

    @disk_node.setter
    def disk_node(self, value: builtins.str) -> None:
        jsii.set(self, "diskNode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="diskPath")
    def disk_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "diskPath"))

    @disk_path.setter
    def disk_path(self, value: builtins.str) -> None:
        jsii.set(self, "diskPath", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gatewayArn")
    def gateway_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gatewayArn"))

    @gateway_arn.setter
    def gateway_arn(self, value: builtins.str) -> None:
        jsii.set(self, "gatewayArn", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.storagegateway.DataAwsStoragegatewayLocalDiskConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "gateway_arn": "gatewayArn",
        "disk_node": "diskNode",
        "disk_path": "diskPath",
    },
)
class DataAwsStoragegatewayLocalDiskConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        gateway_arn: builtins.str,
        disk_node: typing.Optional[builtins.str] = None,
        disk_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Storage Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param gateway_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/storagegateway_local_disk#gateway_arn DataAwsStoragegatewayLocalDisk#gateway_arn}.
        :param disk_node: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/storagegateway_local_disk#disk_node DataAwsStoragegatewayLocalDisk#disk_node}.
        :param disk_path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/storagegateway_local_disk#disk_path DataAwsStoragegatewayLocalDisk#disk_path}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "gateway_arn": gateway_arn,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if disk_node is not None:
            self._values["disk_node"] = disk_node
        if disk_path is not None:
            self._values["disk_path"] = disk_path

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
    def gateway_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/storagegateway_local_disk#gateway_arn DataAwsStoragegatewayLocalDisk#gateway_arn}.'''
        result = self._values.get("gateway_arn")
        assert result is not None, "Required property 'gateway_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def disk_node(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/storagegateway_local_disk#disk_node DataAwsStoragegatewayLocalDisk#disk_node}.'''
        result = self._values.get("disk_node")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disk_path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/storagegateway_local_disk#disk_path DataAwsStoragegatewayLocalDisk#disk_path}.'''
        result = self._values.get("disk_path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsStoragegatewayLocalDiskConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StoragegatewayCache(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewayCache",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cache aws_storagegateway_cache}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        disk_id: builtins.str,
        gateway_arn: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cache aws_storagegateway_cache} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param disk_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cache#disk_id StoragegatewayCache#disk_id}.
        :param gateway_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cache#gateway_arn StoragegatewayCache#gateway_arn}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = StoragegatewayCacheConfig(
            disk_id=disk_id,
            gateway_arn=gateway_arn,
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
    @jsii.member(jsii_name="diskIdInput")
    def disk_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "diskIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gatewayArnInput")
    def gateway_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gatewayArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="diskId")
    def disk_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "diskId"))

    @disk_id.setter
    def disk_id(self, value: builtins.str) -> None:
        jsii.set(self, "diskId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gatewayArn")
    def gateway_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gatewayArn"))

    @gateway_arn.setter
    def gateway_arn(self, value: builtins.str) -> None:
        jsii.set(self, "gatewayArn", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewayCacheConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "disk_id": "diskId",
        "gateway_arn": "gatewayArn",
    },
)
class StoragegatewayCacheConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        disk_id: builtins.str,
        gateway_arn: builtins.str,
    ) -> None:
        '''AWS Storage Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param disk_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cache#disk_id StoragegatewayCache#disk_id}.
        :param gateway_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cache#gateway_arn StoragegatewayCache#gateway_arn}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "disk_id": disk_id,
            "gateway_arn": gateway_arn,
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
    def disk_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cache#disk_id StoragegatewayCache#disk_id}.'''
        result = self._values.get("disk_id")
        assert result is not None, "Required property 'disk_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def gateway_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cache#gateway_arn StoragegatewayCache#gateway_arn}.'''
        result = self._values.get("gateway_arn")
        assert result is not None, "Required property 'gateway_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StoragegatewayCacheConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StoragegatewayCachedIscsiVolume(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewayCachedIscsiVolume",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cached_iscsi_volume aws_storagegateway_cached_iscsi_volume}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        gateway_arn: builtins.str,
        network_interface_id: builtins.str,
        target_name: builtins.str,
        volume_size_in_bytes: jsii.Number,
        kms_encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        kms_key: typing.Optional[builtins.str] = None,
        snapshot_id: typing.Optional[builtins.str] = None,
        source_volume_arn: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cached_iscsi_volume aws_storagegateway_cached_iscsi_volume} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param gateway_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cached_iscsi_volume#gateway_arn StoragegatewayCachedIscsiVolume#gateway_arn}.
        :param network_interface_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cached_iscsi_volume#network_interface_id StoragegatewayCachedIscsiVolume#network_interface_id}.
        :param target_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cached_iscsi_volume#target_name StoragegatewayCachedIscsiVolume#target_name}.
        :param volume_size_in_bytes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cached_iscsi_volume#volume_size_in_bytes StoragegatewayCachedIscsiVolume#volume_size_in_bytes}.
        :param kms_encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cached_iscsi_volume#kms_encrypted StoragegatewayCachedIscsiVolume#kms_encrypted}.
        :param kms_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cached_iscsi_volume#kms_key StoragegatewayCachedIscsiVolume#kms_key}.
        :param snapshot_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cached_iscsi_volume#snapshot_id StoragegatewayCachedIscsiVolume#snapshot_id}.
        :param source_volume_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cached_iscsi_volume#source_volume_arn StoragegatewayCachedIscsiVolume#source_volume_arn}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cached_iscsi_volume#tags StoragegatewayCachedIscsiVolume#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cached_iscsi_volume#tags_all StoragegatewayCachedIscsiVolume#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = StoragegatewayCachedIscsiVolumeConfig(
            gateway_arn=gateway_arn,
            network_interface_id=network_interface_id,
            target_name=target_name,
            volume_size_in_bytes=volume_size_in_bytes,
            kms_encrypted=kms_encrypted,
            kms_key=kms_key,
            snapshot_id=snapshot_id,
            source_volume_arn=source_volume_arn,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetKmsEncrypted")
    def reset_kms_encrypted(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsEncrypted", []))

    @jsii.member(jsii_name="resetKmsKey")
    def reset_kms_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKey", []))

    @jsii.member(jsii_name="resetSnapshotId")
    def reset_snapshot_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnapshotId", []))

    @jsii.member(jsii_name="resetSourceVolumeArn")
    def reset_source_volume_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceVolumeArn", []))

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
    @jsii.member(jsii_name="chapEnabled")
    def chap_enabled(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "chapEnabled"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lunNumber")
    def lun_number(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lunNumber"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkInterfacePort")
    def network_interface_port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "networkInterfacePort"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetArn")
    def target_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeArn")
    def volume_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "volumeArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeId")
    def volume_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "volumeId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gatewayArnInput")
    def gateway_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gatewayArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsEncryptedInput")
    def kms_encrypted_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "kmsEncryptedInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyInput")
    def kms_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkInterfaceIdInput")
    def network_interface_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkInterfaceIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotIdInput")
    def snapshot_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snapshotIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceVolumeArnInput")
    def source_volume_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceVolumeArnInput"))

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
    @jsii.member(jsii_name="targetNameInput")
    def target_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeSizeInBytesInput")
    def volume_size_in_bytes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "volumeSizeInBytesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gatewayArn")
    def gateway_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gatewayArn"))

    @gateway_arn.setter
    def gateway_arn(self, value: builtins.str) -> None:
        jsii.set(self, "gatewayArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsEncrypted")
    def kms_encrypted(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "kmsEncrypted"))

    @kms_encrypted.setter
    def kms_encrypted(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "kmsEncrypted", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKey")
    def kms_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKey"))

    @kms_key.setter
    def kms_key(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkInterfaceId")
    def network_interface_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkInterfaceId"))

    @network_interface_id.setter
    def network_interface_id(self, value: builtins.str) -> None:
        jsii.set(self, "networkInterfaceId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotId")
    def snapshot_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snapshotId"))

    @snapshot_id.setter
    def snapshot_id(self, value: builtins.str) -> None:
        jsii.set(self, "snapshotId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceVolumeArn")
    def source_volume_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceVolumeArn"))

    @source_volume_arn.setter
    def source_volume_arn(self, value: builtins.str) -> None:
        jsii.set(self, "sourceVolumeArn", value)

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
    @jsii.member(jsii_name="targetName")
    def target_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetName"))

    @target_name.setter
    def target_name(self, value: builtins.str) -> None:
        jsii.set(self, "targetName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeSizeInBytes")
    def volume_size_in_bytes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "volumeSizeInBytes"))

    @volume_size_in_bytes.setter
    def volume_size_in_bytes(self, value: jsii.Number) -> None:
        jsii.set(self, "volumeSizeInBytes", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewayCachedIscsiVolumeConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "gateway_arn": "gatewayArn",
        "network_interface_id": "networkInterfaceId",
        "target_name": "targetName",
        "volume_size_in_bytes": "volumeSizeInBytes",
        "kms_encrypted": "kmsEncrypted",
        "kms_key": "kmsKey",
        "snapshot_id": "snapshotId",
        "source_volume_arn": "sourceVolumeArn",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class StoragegatewayCachedIscsiVolumeConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        gateway_arn: builtins.str,
        network_interface_id: builtins.str,
        target_name: builtins.str,
        volume_size_in_bytes: jsii.Number,
        kms_encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        kms_key: typing.Optional[builtins.str] = None,
        snapshot_id: typing.Optional[builtins.str] = None,
        source_volume_arn: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Storage Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param gateway_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cached_iscsi_volume#gateway_arn StoragegatewayCachedIscsiVolume#gateway_arn}.
        :param network_interface_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cached_iscsi_volume#network_interface_id StoragegatewayCachedIscsiVolume#network_interface_id}.
        :param target_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cached_iscsi_volume#target_name StoragegatewayCachedIscsiVolume#target_name}.
        :param volume_size_in_bytes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cached_iscsi_volume#volume_size_in_bytes StoragegatewayCachedIscsiVolume#volume_size_in_bytes}.
        :param kms_encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cached_iscsi_volume#kms_encrypted StoragegatewayCachedIscsiVolume#kms_encrypted}.
        :param kms_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cached_iscsi_volume#kms_key StoragegatewayCachedIscsiVolume#kms_key}.
        :param snapshot_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cached_iscsi_volume#snapshot_id StoragegatewayCachedIscsiVolume#snapshot_id}.
        :param source_volume_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cached_iscsi_volume#source_volume_arn StoragegatewayCachedIscsiVolume#source_volume_arn}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cached_iscsi_volume#tags StoragegatewayCachedIscsiVolume#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cached_iscsi_volume#tags_all StoragegatewayCachedIscsiVolume#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "gateway_arn": gateway_arn,
            "network_interface_id": network_interface_id,
            "target_name": target_name,
            "volume_size_in_bytes": volume_size_in_bytes,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if kms_encrypted is not None:
            self._values["kms_encrypted"] = kms_encrypted
        if kms_key is not None:
            self._values["kms_key"] = kms_key
        if snapshot_id is not None:
            self._values["snapshot_id"] = snapshot_id
        if source_volume_arn is not None:
            self._values["source_volume_arn"] = source_volume_arn
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
    def gateway_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cached_iscsi_volume#gateway_arn StoragegatewayCachedIscsiVolume#gateway_arn}.'''
        result = self._values.get("gateway_arn")
        assert result is not None, "Required property 'gateway_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def network_interface_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cached_iscsi_volume#network_interface_id StoragegatewayCachedIscsiVolume#network_interface_id}.'''
        result = self._values.get("network_interface_id")
        assert result is not None, "Required property 'network_interface_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cached_iscsi_volume#target_name StoragegatewayCachedIscsiVolume#target_name}.'''
        result = self._values.get("target_name")
        assert result is not None, "Required property 'target_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def volume_size_in_bytes(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cached_iscsi_volume#volume_size_in_bytes StoragegatewayCachedIscsiVolume#volume_size_in_bytes}.'''
        result = self._values.get("volume_size_in_bytes")
        assert result is not None, "Required property 'volume_size_in_bytes' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def kms_encrypted(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cached_iscsi_volume#kms_encrypted StoragegatewayCachedIscsiVolume#kms_encrypted}.'''
        result = self._values.get("kms_encrypted")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def kms_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cached_iscsi_volume#kms_key StoragegatewayCachedIscsiVolume#kms_key}.'''
        result = self._values.get("kms_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def snapshot_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cached_iscsi_volume#snapshot_id StoragegatewayCachedIscsiVolume#snapshot_id}.'''
        result = self._values.get("snapshot_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_volume_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cached_iscsi_volume#source_volume_arn StoragegatewayCachedIscsiVolume#source_volume_arn}.'''
        result = self._values.get("source_volume_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cached_iscsi_volume#tags StoragegatewayCachedIscsiVolume#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_cached_iscsi_volume#tags_all StoragegatewayCachedIscsiVolume#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StoragegatewayCachedIscsiVolumeConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StoragegatewayFileSystemAssociation(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewayFileSystemAssociation",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_file_system_association aws_storagegateway_file_system_association}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        gateway_arn: builtins.str,
        location_arn: builtins.str,
        password: builtins.str,
        username: builtins.str,
        audit_destination_arn: typing.Optional[builtins.str] = None,
        cache_attributes: typing.Optional["StoragegatewayFileSystemAssociationCacheAttributes"] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_file_system_association aws_storagegateway_file_system_association} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param gateway_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_file_system_association#gateway_arn StoragegatewayFileSystemAssociation#gateway_arn}.
        :param location_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_file_system_association#location_arn StoragegatewayFileSystemAssociation#location_arn}.
        :param password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_file_system_association#password StoragegatewayFileSystemAssociation#password}.
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_file_system_association#username StoragegatewayFileSystemAssociation#username}.
        :param audit_destination_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_file_system_association#audit_destination_arn StoragegatewayFileSystemAssociation#audit_destination_arn}.
        :param cache_attributes: cache_attributes block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_file_system_association#cache_attributes StoragegatewayFileSystemAssociation#cache_attributes}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_file_system_association#tags StoragegatewayFileSystemAssociation#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_file_system_association#tags_all StoragegatewayFileSystemAssociation#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = StoragegatewayFileSystemAssociationConfig(
            gateway_arn=gateway_arn,
            location_arn=location_arn,
            password=password,
            username=username,
            audit_destination_arn=audit_destination_arn,
            cache_attributes=cache_attributes,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putCacheAttributes")
    def put_cache_attributes(
        self,
        *,
        cache_stale_timeout_in_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cache_stale_timeout_in_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_file_system_association#cache_stale_timeout_in_seconds StoragegatewayFileSystemAssociation#cache_stale_timeout_in_seconds}.
        '''
        value = StoragegatewayFileSystemAssociationCacheAttributes(
            cache_stale_timeout_in_seconds=cache_stale_timeout_in_seconds
        )

        return typing.cast(None, jsii.invoke(self, "putCacheAttributes", [value]))

    @jsii.member(jsii_name="resetAuditDestinationArn")
    def reset_audit_destination_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuditDestinationArn", []))

    @jsii.member(jsii_name="resetCacheAttributes")
    def reset_cache_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCacheAttributes", []))

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
    @jsii.member(jsii_name="cacheAttributes")
    def cache_attributes(
        self,
    ) -> "StoragegatewayFileSystemAssociationCacheAttributesOutputReference":
        return typing.cast("StoragegatewayFileSystemAssociationCacheAttributesOutputReference", jsii.get(self, "cacheAttributes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="auditDestinationArnInput")
    def audit_destination_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "auditDestinationArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheAttributesInput")
    def cache_attributes_input(
        self,
    ) -> typing.Optional["StoragegatewayFileSystemAssociationCacheAttributes"]:
        return typing.cast(typing.Optional["StoragegatewayFileSystemAssociationCacheAttributes"], jsii.get(self, "cacheAttributesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gatewayArnInput")
    def gateway_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gatewayArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="locationArnInput")
    def location_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "locationArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

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
    @jsii.member(jsii_name="auditDestinationArn")
    def audit_destination_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "auditDestinationArn"))

    @audit_destination_arn.setter
    def audit_destination_arn(self, value: builtins.str) -> None:
        jsii.set(self, "auditDestinationArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gatewayArn")
    def gateway_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gatewayArn"))

    @gateway_arn.setter
    def gateway_arn(self, value: builtins.str) -> None:
        jsii.set(self, "gatewayArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="locationArn")
    def location_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "locationArn"))

    @location_arn.setter
    def location_arn(self, value: builtins.str) -> None:
        jsii.set(self, "locationArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        jsii.set(self, "password", value)

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
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewayFileSystemAssociationCacheAttributes",
    jsii_struct_bases=[],
    name_mapping={"cache_stale_timeout_in_seconds": "cacheStaleTimeoutInSeconds"},
)
class StoragegatewayFileSystemAssociationCacheAttributes:
    def __init__(
        self,
        *,
        cache_stale_timeout_in_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cache_stale_timeout_in_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_file_system_association#cache_stale_timeout_in_seconds StoragegatewayFileSystemAssociation#cache_stale_timeout_in_seconds}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if cache_stale_timeout_in_seconds is not None:
            self._values["cache_stale_timeout_in_seconds"] = cache_stale_timeout_in_seconds

    @builtins.property
    def cache_stale_timeout_in_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_file_system_association#cache_stale_timeout_in_seconds StoragegatewayFileSystemAssociation#cache_stale_timeout_in_seconds}.'''
        result = self._values.get("cache_stale_timeout_in_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StoragegatewayFileSystemAssociationCacheAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StoragegatewayFileSystemAssociationCacheAttributesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewayFileSystemAssociationCacheAttributesOutputReference",
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

    @jsii.member(jsii_name="resetCacheStaleTimeoutInSeconds")
    def reset_cache_stale_timeout_in_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCacheStaleTimeoutInSeconds", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheStaleTimeoutInSecondsInput")
    def cache_stale_timeout_in_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cacheStaleTimeoutInSecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheStaleTimeoutInSeconds")
    def cache_stale_timeout_in_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cacheStaleTimeoutInSeconds"))

    @cache_stale_timeout_in_seconds.setter
    def cache_stale_timeout_in_seconds(self, value: jsii.Number) -> None:
        jsii.set(self, "cacheStaleTimeoutInSeconds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[StoragegatewayFileSystemAssociationCacheAttributes]:
        return typing.cast(typing.Optional[StoragegatewayFileSystemAssociationCacheAttributes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[StoragegatewayFileSystemAssociationCacheAttributes],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewayFileSystemAssociationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "gateway_arn": "gatewayArn",
        "location_arn": "locationArn",
        "password": "password",
        "username": "username",
        "audit_destination_arn": "auditDestinationArn",
        "cache_attributes": "cacheAttributes",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class StoragegatewayFileSystemAssociationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        gateway_arn: builtins.str,
        location_arn: builtins.str,
        password: builtins.str,
        username: builtins.str,
        audit_destination_arn: typing.Optional[builtins.str] = None,
        cache_attributes: typing.Optional[StoragegatewayFileSystemAssociationCacheAttributes] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Storage Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param gateway_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_file_system_association#gateway_arn StoragegatewayFileSystemAssociation#gateway_arn}.
        :param location_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_file_system_association#location_arn StoragegatewayFileSystemAssociation#location_arn}.
        :param password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_file_system_association#password StoragegatewayFileSystemAssociation#password}.
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_file_system_association#username StoragegatewayFileSystemAssociation#username}.
        :param audit_destination_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_file_system_association#audit_destination_arn StoragegatewayFileSystemAssociation#audit_destination_arn}.
        :param cache_attributes: cache_attributes block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_file_system_association#cache_attributes StoragegatewayFileSystemAssociation#cache_attributes}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_file_system_association#tags StoragegatewayFileSystemAssociation#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_file_system_association#tags_all StoragegatewayFileSystemAssociation#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(cache_attributes, dict):
            cache_attributes = StoragegatewayFileSystemAssociationCacheAttributes(**cache_attributes)
        self._values: typing.Dict[str, typing.Any] = {
            "gateway_arn": gateway_arn,
            "location_arn": location_arn,
            "password": password,
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
        if audit_destination_arn is not None:
            self._values["audit_destination_arn"] = audit_destination_arn
        if cache_attributes is not None:
            self._values["cache_attributes"] = cache_attributes
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
    def gateway_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_file_system_association#gateway_arn StoragegatewayFileSystemAssociation#gateway_arn}.'''
        result = self._values.get("gateway_arn")
        assert result is not None, "Required property 'gateway_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def location_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_file_system_association#location_arn StoragegatewayFileSystemAssociation#location_arn}.'''
        result = self._values.get("location_arn")
        assert result is not None, "Required property 'location_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def password(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_file_system_association#password StoragegatewayFileSystemAssociation#password}.'''
        result = self._values.get("password")
        assert result is not None, "Required property 'password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_file_system_association#username StoragegatewayFileSystemAssociation#username}.'''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def audit_destination_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_file_system_association#audit_destination_arn StoragegatewayFileSystemAssociation#audit_destination_arn}.'''
        result = self._values.get("audit_destination_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cache_attributes(
        self,
    ) -> typing.Optional[StoragegatewayFileSystemAssociationCacheAttributes]:
        '''cache_attributes block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_file_system_association#cache_attributes StoragegatewayFileSystemAssociation#cache_attributes}
        '''
        result = self._values.get("cache_attributes")
        return typing.cast(typing.Optional[StoragegatewayFileSystemAssociationCacheAttributes], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_file_system_association#tags StoragegatewayFileSystemAssociation#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_file_system_association#tags_all StoragegatewayFileSystemAssociation#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StoragegatewayFileSystemAssociationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StoragegatewayGateway(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewayGateway",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway aws_storagegateway_gateway}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        gateway_name: builtins.str,
        gateway_timezone: builtins.str,
        activation_key: typing.Optional[builtins.str] = None,
        average_download_rate_limit_in_bits_per_sec: typing.Optional[jsii.Number] = None,
        average_upload_rate_limit_in_bits_per_sec: typing.Optional[jsii.Number] = None,
        cloudwatch_log_group_arn: typing.Optional[builtins.str] = None,
        gateway_ip_address: typing.Optional[builtins.str] = None,
        gateway_type: typing.Optional[builtins.str] = None,
        gateway_vpc_endpoint: typing.Optional[builtins.str] = None,
        medium_changer_type: typing.Optional[builtins.str] = None,
        smb_active_directory_settings: typing.Optional["StoragegatewayGatewaySmbActiveDirectorySettings"] = None,
        smb_file_share_visibility: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        smb_guest_password: typing.Optional[builtins.str] = None,
        smb_security_strategy: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tape_drive_type: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional["StoragegatewayGatewayTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway aws_storagegateway_gateway} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param gateway_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#gateway_name StoragegatewayGateway#gateway_name}.
        :param gateway_timezone: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#gateway_timezone StoragegatewayGateway#gateway_timezone}.
        :param activation_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#activation_key StoragegatewayGateway#activation_key}.
        :param average_download_rate_limit_in_bits_per_sec: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#average_download_rate_limit_in_bits_per_sec StoragegatewayGateway#average_download_rate_limit_in_bits_per_sec}.
        :param average_upload_rate_limit_in_bits_per_sec: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#average_upload_rate_limit_in_bits_per_sec StoragegatewayGateway#average_upload_rate_limit_in_bits_per_sec}.
        :param cloudwatch_log_group_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#cloudwatch_log_group_arn StoragegatewayGateway#cloudwatch_log_group_arn}.
        :param gateway_ip_address: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#gateway_ip_address StoragegatewayGateway#gateway_ip_address}.
        :param gateway_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#gateway_type StoragegatewayGateway#gateway_type}.
        :param gateway_vpc_endpoint: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#gateway_vpc_endpoint StoragegatewayGateway#gateway_vpc_endpoint}.
        :param medium_changer_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#medium_changer_type StoragegatewayGateway#medium_changer_type}.
        :param smb_active_directory_settings: smb_active_directory_settings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#smb_active_directory_settings StoragegatewayGateway#smb_active_directory_settings}
        :param smb_file_share_visibility: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#smb_file_share_visibility StoragegatewayGateway#smb_file_share_visibility}.
        :param smb_guest_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#smb_guest_password StoragegatewayGateway#smb_guest_password}.
        :param smb_security_strategy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#smb_security_strategy StoragegatewayGateway#smb_security_strategy}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#tags StoragegatewayGateway#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#tags_all StoragegatewayGateway#tags_all}.
        :param tape_drive_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#tape_drive_type StoragegatewayGateway#tape_drive_type}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#timeouts StoragegatewayGateway#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = StoragegatewayGatewayConfig(
            gateway_name=gateway_name,
            gateway_timezone=gateway_timezone,
            activation_key=activation_key,
            average_download_rate_limit_in_bits_per_sec=average_download_rate_limit_in_bits_per_sec,
            average_upload_rate_limit_in_bits_per_sec=average_upload_rate_limit_in_bits_per_sec,
            cloudwatch_log_group_arn=cloudwatch_log_group_arn,
            gateway_ip_address=gateway_ip_address,
            gateway_type=gateway_type,
            gateway_vpc_endpoint=gateway_vpc_endpoint,
            medium_changer_type=medium_changer_type,
            smb_active_directory_settings=smb_active_directory_settings,
            smb_file_share_visibility=smb_file_share_visibility,
            smb_guest_password=smb_guest_password,
            smb_security_strategy=smb_security_strategy,
            tags=tags,
            tags_all=tags_all,
            tape_drive_type=tape_drive_type,
            timeouts=timeouts,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="gatewayNetworkInterface")
    def gateway_network_interface(
        self,
        index: builtins.str,
    ) -> "StoragegatewayGatewayGatewayNetworkInterface":
        '''
        :param index: -
        '''
        return typing.cast("StoragegatewayGatewayGatewayNetworkInterface", jsii.invoke(self, "gatewayNetworkInterface", [index]))

    @jsii.member(jsii_name="putSmbActiveDirectorySettings")
    def put_smb_active_directory_settings(
        self,
        *,
        domain_name: builtins.str,
        password: builtins.str,
        username: builtins.str,
        domain_controllers: typing.Optional[typing.Sequence[builtins.str]] = None,
        organizational_unit: typing.Optional[builtins.str] = None,
        timeout_in_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param domain_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#domain_name StoragegatewayGateway#domain_name}.
        :param password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#password StoragegatewayGateway#password}.
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#username StoragegatewayGateway#username}.
        :param domain_controllers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#domain_controllers StoragegatewayGateway#domain_controllers}.
        :param organizational_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#organizational_unit StoragegatewayGateway#organizational_unit}.
        :param timeout_in_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#timeout_in_seconds StoragegatewayGateway#timeout_in_seconds}.
        '''
        value = StoragegatewayGatewaySmbActiveDirectorySettings(
            domain_name=domain_name,
            password=password,
            username=username,
            domain_controllers=domain_controllers,
            organizational_unit=organizational_unit,
            timeout_in_seconds=timeout_in_seconds,
        )

        return typing.cast(None, jsii.invoke(self, "putSmbActiveDirectorySettings", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(self, *, create: typing.Optional[builtins.str] = None) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#create StoragegatewayGateway#create}.
        '''
        value = StoragegatewayGatewayTimeouts(create=create)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetActivationKey")
    def reset_activation_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetActivationKey", []))

    @jsii.member(jsii_name="resetAverageDownloadRateLimitInBitsPerSec")
    def reset_average_download_rate_limit_in_bits_per_sec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAverageDownloadRateLimitInBitsPerSec", []))

    @jsii.member(jsii_name="resetAverageUploadRateLimitInBitsPerSec")
    def reset_average_upload_rate_limit_in_bits_per_sec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAverageUploadRateLimitInBitsPerSec", []))

    @jsii.member(jsii_name="resetCloudwatchLogGroupArn")
    def reset_cloudwatch_log_group_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloudwatchLogGroupArn", []))

    @jsii.member(jsii_name="resetGatewayIpAddress")
    def reset_gateway_ip_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGatewayIpAddress", []))

    @jsii.member(jsii_name="resetGatewayType")
    def reset_gateway_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGatewayType", []))

    @jsii.member(jsii_name="resetGatewayVpcEndpoint")
    def reset_gateway_vpc_endpoint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGatewayVpcEndpoint", []))

    @jsii.member(jsii_name="resetMediumChangerType")
    def reset_medium_changer_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMediumChangerType", []))

    @jsii.member(jsii_name="resetSmbActiveDirectorySettings")
    def reset_smb_active_directory_settings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSmbActiveDirectorySettings", []))

    @jsii.member(jsii_name="resetSmbFileShareVisibility")
    def reset_smb_file_share_visibility(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSmbFileShareVisibility", []))

    @jsii.member(jsii_name="resetSmbGuestPassword")
    def reset_smb_guest_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSmbGuestPassword", []))

    @jsii.member(jsii_name="resetSmbSecurityStrategy")
    def reset_smb_security_strategy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSmbSecurityStrategy", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTapeDriveType")
    def reset_tape_drive_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTapeDriveType", []))

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
    @jsii.member(jsii_name="ec2InstanceId")
    def ec2_instance_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ec2InstanceId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointType")
    def endpoint_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpointType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gatewayId")
    def gateway_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gatewayId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostEnvironment")
    def host_environment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostEnvironment"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="smbActiveDirectorySettings")
    def smb_active_directory_settings(
        self,
    ) -> "StoragegatewayGatewaySmbActiveDirectorySettingsOutputReference":
        return typing.cast("StoragegatewayGatewaySmbActiveDirectorySettingsOutputReference", jsii.get(self, "smbActiveDirectorySettings"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "StoragegatewayGatewayTimeoutsOutputReference":
        return typing.cast("StoragegatewayGatewayTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="activationKeyInput")
    def activation_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "activationKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="averageDownloadRateLimitInBitsPerSecInput")
    def average_download_rate_limit_in_bits_per_sec_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "averageDownloadRateLimitInBitsPerSecInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="averageUploadRateLimitInBitsPerSecInput")
    def average_upload_rate_limit_in_bits_per_sec_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "averageUploadRateLimitInBitsPerSecInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudwatchLogGroupArnInput")
    def cloudwatch_log_group_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cloudwatchLogGroupArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gatewayIpAddressInput")
    def gateway_ip_address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gatewayIpAddressInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gatewayNameInput")
    def gateway_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gatewayNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gatewayTimezoneInput")
    def gateway_timezone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gatewayTimezoneInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gatewayTypeInput")
    def gateway_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gatewayTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gatewayVpcEndpointInput")
    def gateway_vpc_endpoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gatewayVpcEndpointInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mediumChangerTypeInput")
    def medium_changer_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mediumChangerTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="smbActiveDirectorySettingsInput")
    def smb_active_directory_settings_input(
        self,
    ) -> typing.Optional["StoragegatewayGatewaySmbActiveDirectorySettings"]:
        return typing.cast(typing.Optional["StoragegatewayGatewaySmbActiveDirectorySettings"], jsii.get(self, "smbActiveDirectorySettingsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="smbFileShareVisibilityInput")
    def smb_file_share_visibility_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "smbFileShareVisibilityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="smbGuestPasswordInput")
    def smb_guest_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "smbGuestPasswordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="smbSecurityStrategyInput")
    def smb_security_strategy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "smbSecurityStrategyInput"))

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
    @jsii.member(jsii_name="tapeDriveTypeInput")
    def tape_drive_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tapeDriveTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["StoragegatewayGatewayTimeouts"]:
        return typing.cast(typing.Optional["StoragegatewayGatewayTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="activationKey")
    def activation_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "activationKey"))

    @activation_key.setter
    def activation_key(self, value: builtins.str) -> None:
        jsii.set(self, "activationKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="averageDownloadRateLimitInBitsPerSec")
    def average_download_rate_limit_in_bits_per_sec(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "averageDownloadRateLimitInBitsPerSec"))

    @average_download_rate_limit_in_bits_per_sec.setter
    def average_download_rate_limit_in_bits_per_sec(self, value: jsii.Number) -> None:
        jsii.set(self, "averageDownloadRateLimitInBitsPerSec", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="averageUploadRateLimitInBitsPerSec")
    def average_upload_rate_limit_in_bits_per_sec(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "averageUploadRateLimitInBitsPerSec"))

    @average_upload_rate_limit_in_bits_per_sec.setter
    def average_upload_rate_limit_in_bits_per_sec(self, value: jsii.Number) -> None:
        jsii.set(self, "averageUploadRateLimitInBitsPerSec", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudwatchLogGroupArn")
    def cloudwatch_log_group_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cloudwatchLogGroupArn"))

    @cloudwatch_log_group_arn.setter
    def cloudwatch_log_group_arn(self, value: builtins.str) -> None:
        jsii.set(self, "cloudwatchLogGroupArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gatewayIpAddress")
    def gateway_ip_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gatewayIpAddress"))

    @gateway_ip_address.setter
    def gateway_ip_address(self, value: builtins.str) -> None:
        jsii.set(self, "gatewayIpAddress", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gatewayName")
    def gateway_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gatewayName"))

    @gateway_name.setter
    def gateway_name(self, value: builtins.str) -> None:
        jsii.set(self, "gatewayName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gatewayTimezone")
    def gateway_timezone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gatewayTimezone"))

    @gateway_timezone.setter
    def gateway_timezone(self, value: builtins.str) -> None:
        jsii.set(self, "gatewayTimezone", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gatewayType")
    def gateway_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gatewayType"))

    @gateway_type.setter
    def gateway_type(self, value: builtins.str) -> None:
        jsii.set(self, "gatewayType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gatewayVpcEndpoint")
    def gateway_vpc_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gatewayVpcEndpoint"))

    @gateway_vpc_endpoint.setter
    def gateway_vpc_endpoint(self, value: builtins.str) -> None:
        jsii.set(self, "gatewayVpcEndpoint", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mediumChangerType")
    def medium_changer_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mediumChangerType"))

    @medium_changer_type.setter
    def medium_changer_type(self, value: builtins.str) -> None:
        jsii.set(self, "mediumChangerType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="smbFileShareVisibility")
    def smb_file_share_visibility(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "smbFileShareVisibility"))

    @smb_file_share_visibility.setter
    def smb_file_share_visibility(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "smbFileShareVisibility", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="smbGuestPassword")
    def smb_guest_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "smbGuestPassword"))

    @smb_guest_password.setter
    def smb_guest_password(self, value: builtins.str) -> None:
        jsii.set(self, "smbGuestPassword", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="smbSecurityStrategy")
    def smb_security_strategy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "smbSecurityStrategy"))

    @smb_security_strategy.setter
    def smb_security_strategy(self, value: builtins.str) -> None:
        jsii.set(self, "smbSecurityStrategy", value)

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
    @jsii.member(jsii_name="tapeDriveType")
    def tape_drive_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tapeDriveType"))

    @tape_drive_type.setter
    def tape_drive_type(self, value: builtins.str) -> None:
        jsii.set(self, "tapeDriveType", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewayGatewayConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "gateway_name": "gatewayName",
        "gateway_timezone": "gatewayTimezone",
        "activation_key": "activationKey",
        "average_download_rate_limit_in_bits_per_sec": "averageDownloadRateLimitInBitsPerSec",
        "average_upload_rate_limit_in_bits_per_sec": "averageUploadRateLimitInBitsPerSec",
        "cloudwatch_log_group_arn": "cloudwatchLogGroupArn",
        "gateway_ip_address": "gatewayIpAddress",
        "gateway_type": "gatewayType",
        "gateway_vpc_endpoint": "gatewayVpcEndpoint",
        "medium_changer_type": "mediumChangerType",
        "smb_active_directory_settings": "smbActiveDirectorySettings",
        "smb_file_share_visibility": "smbFileShareVisibility",
        "smb_guest_password": "smbGuestPassword",
        "smb_security_strategy": "smbSecurityStrategy",
        "tags": "tags",
        "tags_all": "tagsAll",
        "tape_drive_type": "tapeDriveType",
        "timeouts": "timeouts",
    },
)
class StoragegatewayGatewayConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        gateway_name: builtins.str,
        gateway_timezone: builtins.str,
        activation_key: typing.Optional[builtins.str] = None,
        average_download_rate_limit_in_bits_per_sec: typing.Optional[jsii.Number] = None,
        average_upload_rate_limit_in_bits_per_sec: typing.Optional[jsii.Number] = None,
        cloudwatch_log_group_arn: typing.Optional[builtins.str] = None,
        gateway_ip_address: typing.Optional[builtins.str] = None,
        gateway_type: typing.Optional[builtins.str] = None,
        gateway_vpc_endpoint: typing.Optional[builtins.str] = None,
        medium_changer_type: typing.Optional[builtins.str] = None,
        smb_active_directory_settings: typing.Optional["StoragegatewayGatewaySmbActiveDirectorySettings"] = None,
        smb_file_share_visibility: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        smb_guest_password: typing.Optional[builtins.str] = None,
        smb_security_strategy: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tape_drive_type: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional["StoragegatewayGatewayTimeouts"] = None,
    ) -> None:
        '''AWS Storage Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param gateway_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#gateway_name StoragegatewayGateway#gateway_name}.
        :param gateway_timezone: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#gateway_timezone StoragegatewayGateway#gateway_timezone}.
        :param activation_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#activation_key StoragegatewayGateway#activation_key}.
        :param average_download_rate_limit_in_bits_per_sec: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#average_download_rate_limit_in_bits_per_sec StoragegatewayGateway#average_download_rate_limit_in_bits_per_sec}.
        :param average_upload_rate_limit_in_bits_per_sec: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#average_upload_rate_limit_in_bits_per_sec StoragegatewayGateway#average_upload_rate_limit_in_bits_per_sec}.
        :param cloudwatch_log_group_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#cloudwatch_log_group_arn StoragegatewayGateway#cloudwatch_log_group_arn}.
        :param gateway_ip_address: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#gateway_ip_address StoragegatewayGateway#gateway_ip_address}.
        :param gateway_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#gateway_type StoragegatewayGateway#gateway_type}.
        :param gateway_vpc_endpoint: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#gateway_vpc_endpoint StoragegatewayGateway#gateway_vpc_endpoint}.
        :param medium_changer_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#medium_changer_type StoragegatewayGateway#medium_changer_type}.
        :param smb_active_directory_settings: smb_active_directory_settings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#smb_active_directory_settings StoragegatewayGateway#smb_active_directory_settings}
        :param smb_file_share_visibility: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#smb_file_share_visibility StoragegatewayGateway#smb_file_share_visibility}.
        :param smb_guest_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#smb_guest_password StoragegatewayGateway#smb_guest_password}.
        :param smb_security_strategy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#smb_security_strategy StoragegatewayGateway#smb_security_strategy}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#tags StoragegatewayGateway#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#tags_all StoragegatewayGateway#tags_all}.
        :param tape_drive_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#tape_drive_type StoragegatewayGateway#tape_drive_type}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#timeouts StoragegatewayGateway#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(smb_active_directory_settings, dict):
            smb_active_directory_settings = StoragegatewayGatewaySmbActiveDirectorySettings(**smb_active_directory_settings)
        if isinstance(timeouts, dict):
            timeouts = StoragegatewayGatewayTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "gateway_name": gateway_name,
            "gateway_timezone": gateway_timezone,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if activation_key is not None:
            self._values["activation_key"] = activation_key
        if average_download_rate_limit_in_bits_per_sec is not None:
            self._values["average_download_rate_limit_in_bits_per_sec"] = average_download_rate_limit_in_bits_per_sec
        if average_upload_rate_limit_in_bits_per_sec is not None:
            self._values["average_upload_rate_limit_in_bits_per_sec"] = average_upload_rate_limit_in_bits_per_sec
        if cloudwatch_log_group_arn is not None:
            self._values["cloudwatch_log_group_arn"] = cloudwatch_log_group_arn
        if gateway_ip_address is not None:
            self._values["gateway_ip_address"] = gateway_ip_address
        if gateway_type is not None:
            self._values["gateway_type"] = gateway_type
        if gateway_vpc_endpoint is not None:
            self._values["gateway_vpc_endpoint"] = gateway_vpc_endpoint
        if medium_changer_type is not None:
            self._values["medium_changer_type"] = medium_changer_type
        if smb_active_directory_settings is not None:
            self._values["smb_active_directory_settings"] = smb_active_directory_settings
        if smb_file_share_visibility is not None:
            self._values["smb_file_share_visibility"] = smb_file_share_visibility
        if smb_guest_password is not None:
            self._values["smb_guest_password"] = smb_guest_password
        if smb_security_strategy is not None:
            self._values["smb_security_strategy"] = smb_security_strategy
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if tape_drive_type is not None:
            self._values["tape_drive_type"] = tape_drive_type
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
    def gateway_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#gateway_name StoragegatewayGateway#gateway_name}.'''
        result = self._values.get("gateway_name")
        assert result is not None, "Required property 'gateway_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def gateway_timezone(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#gateway_timezone StoragegatewayGateway#gateway_timezone}.'''
        result = self._values.get("gateway_timezone")
        assert result is not None, "Required property 'gateway_timezone' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def activation_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#activation_key StoragegatewayGateway#activation_key}.'''
        result = self._values.get("activation_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def average_download_rate_limit_in_bits_per_sec(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#average_download_rate_limit_in_bits_per_sec StoragegatewayGateway#average_download_rate_limit_in_bits_per_sec}.'''
        result = self._values.get("average_download_rate_limit_in_bits_per_sec")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def average_upload_rate_limit_in_bits_per_sec(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#average_upload_rate_limit_in_bits_per_sec StoragegatewayGateway#average_upload_rate_limit_in_bits_per_sec}.'''
        result = self._values.get("average_upload_rate_limit_in_bits_per_sec")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cloudwatch_log_group_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#cloudwatch_log_group_arn StoragegatewayGateway#cloudwatch_log_group_arn}.'''
        result = self._values.get("cloudwatch_log_group_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gateway_ip_address(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#gateway_ip_address StoragegatewayGateway#gateway_ip_address}.'''
        result = self._values.get("gateway_ip_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gateway_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#gateway_type StoragegatewayGateway#gateway_type}.'''
        result = self._values.get("gateway_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gateway_vpc_endpoint(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#gateway_vpc_endpoint StoragegatewayGateway#gateway_vpc_endpoint}.'''
        result = self._values.get("gateway_vpc_endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def medium_changer_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#medium_changer_type StoragegatewayGateway#medium_changer_type}.'''
        result = self._values.get("medium_changer_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def smb_active_directory_settings(
        self,
    ) -> typing.Optional["StoragegatewayGatewaySmbActiveDirectorySettings"]:
        '''smb_active_directory_settings block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#smb_active_directory_settings StoragegatewayGateway#smb_active_directory_settings}
        '''
        result = self._values.get("smb_active_directory_settings")
        return typing.cast(typing.Optional["StoragegatewayGatewaySmbActiveDirectorySettings"], result)

    @builtins.property
    def smb_file_share_visibility(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#smb_file_share_visibility StoragegatewayGateway#smb_file_share_visibility}.'''
        result = self._values.get("smb_file_share_visibility")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def smb_guest_password(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#smb_guest_password StoragegatewayGateway#smb_guest_password}.'''
        result = self._values.get("smb_guest_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def smb_security_strategy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#smb_security_strategy StoragegatewayGateway#smb_security_strategy}.'''
        result = self._values.get("smb_security_strategy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#tags StoragegatewayGateway#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#tags_all StoragegatewayGateway#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tape_drive_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#tape_drive_type StoragegatewayGateway#tape_drive_type}.'''
        result = self._values.get("tape_drive_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["StoragegatewayGatewayTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#timeouts StoragegatewayGateway#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["StoragegatewayGatewayTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StoragegatewayGatewayConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StoragegatewayGatewayGatewayNetworkInterface(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewayGatewayGatewayNetworkInterface",
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
    @jsii.member(jsii_name="ipv4Address")
    def ipv4_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv4Address"))


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewayGatewaySmbActiveDirectorySettings",
    jsii_struct_bases=[],
    name_mapping={
        "domain_name": "domainName",
        "password": "password",
        "username": "username",
        "domain_controllers": "domainControllers",
        "organizational_unit": "organizationalUnit",
        "timeout_in_seconds": "timeoutInSeconds",
    },
)
class StoragegatewayGatewaySmbActiveDirectorySettings:
    def __init__(
        self,
        *,
        domain_name: builtins.str,
        password: builtins.str,
        username: builtins.str,
        domain_controllers: typing.Optional[typing.Sequence[builtins.str]] = None,
        organizational_unit: typing.Optional[builtins.str] = None,
        timeout_in_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param domain_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#domain_name StoragegatewayGateway#domain_name}.
        :param password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#password StoragegatewayGateway#password}.
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#username StoragegatewayGateway#username}.
        :param domain_controllers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#domain_controllers StoragegatewayGateway#domain_controllers}.
        :param organizational_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#organizational_unit StoragegatewayGateway#organizational_unit}.
        :param timeout_in_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#timeout_in_seconds StoragegatewayGateway#timeout_in_seconds}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "domain_name": domain_name,
            "password": password,
            "username": username,
        }
        if domain_controllers is not None:
            self._values["domain_controllers"] = domain_controllers
        if organizational_unit is not None:
            self._values["organizational_unit"] = organizational_unit
        if timeout_in_seconds is not None:
            self._values["timeout_in_seconds"] = timeout_in_seconds

    @builtins.property
    def domain_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#domain_name StoragegatewayGateway#domain_name}.'''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def password(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#password StoragegatewayGateway#password}.'''
        result = self._values.get("password")
        assert result is not None, "Required property 'password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#username StoragegatewayGateway#username}.'''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def domain_controllers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#domain_controllers StoragegatewayGateway#domain_controllers}.'''
        result = self._values.get("domain_controllers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def organizational_unit(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#organizational_unit StoragegatewayGateway#organizational_unit}.'''
        result = self._values.get("organizational_unit")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeout_in_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#timeout_in_seconds StoragegatewayGateway#timeout_in_seconds}.'''
        result = self._values.get("timeout_in_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StoragegatewayGatewaySmbActiveDirectorySettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StoragegatewayGatewaySmbActiveDirectorySettingsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewayGatewaySmbActiveDirectorySettingsOutputReference",
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

    @jsii.member(jsii_name="resetDomainControllers")
    def reset_domain_controllers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDomainControllers", []))

    @jsii.member(jsii_name="resetOrganizationalUnit")
    def reset_organizational_unit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrganizationalUnit", []))

    @jsii.member(jsii_name="resetTimeoutInSeconds")
    def reset_timeout_in_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeoutInSeconds", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainControllersInput")
    def domain_controllers_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "domainControllersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainNameInput")
    def domain_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitInput")
    def organizational_unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "organizationalUnitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutInSecondsInput")
    def timeout_in_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "timeoutInSecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainControllers")
    def domain_controllers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "domainControllers"))

    @domain_controllers.setter
    def domain_controllers(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "domainControllers", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @domain_name.setter
    def domain_name(self, value: builtins.str) -> None:
        jsii.set(self, "domainName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnit")
    def organizational_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "organizationalUnit"))

    @organizational_unit.setter
    def organizational_unit(self, value: builtins.str) -> None:
        jsii.set(self, "organizationalUnit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        jsii.set(self, "password", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutInSeconds")
    def timeout_in_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeoutInSeconds"))

    @timeout_in_seconds.setter
    def timeout_in_seconds(self, value: jsii.Number) -> None:
        jsii.set(self, "timeoutInSeconds", value)

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
    ) -> typing.Optional[StoragegatewayGatewaySmbActiveDirectorySettings]:
        return typing.cast(typing.Optional[StoragegatewayGatewaySmbActiveDirectorySettings], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[StoragegatewayGatewaySmbActiveDirectorySettings],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewayGatewayTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create"},
)
class StoragegatewayGatewayTimeouts:
    def __init__(self, *, create: typing.Optional[builtins.str] = None) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#create StoragegatewayGateway#create}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_gateway#create StoragegatewayGateway#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StoragegatewayGatewayTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StoragegatewayGatewayTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewayGatewayTimeoutsOutputReference",
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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        jsii.set(self, "create", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[StoragegatewayGatewayTimeouts]:
        return typing.cast(typing.Optional[StoragegatewayGatewayTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[StoragegatewayGatewayTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


class StoragegatewayNfsFileShare(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewayNfsFileShare",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share aws_storagegateway_nfs_file_share}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        client_list: typing.Sequence[builtins.str],
        gateway_arn: builtins.str,
        location_arn: builtins.str,
        role_arn: builtins.str,
        audit_destination_arn: typing.Optional[builtins.str] = None,
        cache_attributes: typing.Optional["StoragegatewayNfsFileShareCacheAttributes"] = None,
        default_storage_class: typing.Optional[builtins.str] = None,
        file_share_name: typing.Optional[builtins.str] = None,
        guess_mime_type_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        kms_encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        kms_key_arn: typing.Optional[builtins.str] = None,
        nfs_file_share_defaults: typing.Optional["StoragegatewayNfsFileShareNfsFileShareDefaults"] = None,
        notification_policy: typing.Optional[builtins.str] = None,
        object_acl: typing.Optional[builtins.str] = None,
        read_only: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        requester_pays: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        squash: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["StoragegatewayNfsFileShareTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share aws_storagegateway_nfs_file_share} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param client_list: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#client_list StoragegatewayNfsFileShare#client_list}.
        :param gateway_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#gateway_arn StoragegatewayNfsFileShare#gateway_arn}.
        :param location_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#location_arn StoragegatewayNfsFileShare#location_arn}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#role_arn StoragegatewayNfsFileShare#role_arn}.
        :param audit_destination_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#audit_destination_arn StoragegatewayNfsFileShare#audit_destination_arn}.
        :param cache_attributes: cache_attributes block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#cache_attributes StoragegatewayNfsFileShare#cache_attributes}
        :param default_storage_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#default_storage_class StoragegatewayNfsFileShare#default_storage_class}.
        :param file_share_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#file_share_name StoragegatewayNfsFileShare#file_share_name}.
        :param guess_mime_type_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#guess_mime_type_enabled StoragegatewayNfsFileShare#guess_mime_type_enabled}.
        :param kms_encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#kms_encrypted StoragegatewayNfsFileShare#kms_encrypted}.
        :param kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#kms_key_arn StoragegatewayNfsFileShare#kms_key_arn}.
        :param nfs_file_share_defaults: nfs_file_share_defaults block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#nfs_file_share_defaults StoragegatewayNfsFileShare#nfs_file_share_defaults}
        :param notification_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#notification_policy StoragegatewayNfsFileShare#notification_policy}.
        :param object_acl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#object_acl StoragegatewayNfsFileShare#object_acl}.
        :param read_only: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#read_only StoragegatewayNfsFileShare#read_only}.
        :param requester_pays: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#requester_pays StoragegatewayNfsFileShare#requester_pays}.
        :param squash: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#squash StoragegatewayNfsFileShare#squash}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#tags StoragegatewayNfsFileShare#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#tags_all StoragegatewayNfsFileShare#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#timeouts StoragegatewayNfsFileShare#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = StoragegatewayNfsFileShareConfig(
            client_list=client_list,
            gateway_arn=gateway_arn,
            location_arn=location_arn,
            role_arn=role_arn,
            audit_destination_arn=audit_destination_arn,
            cache_attributes=cache_attributes,
            default_storage_class=default_storage_class,
            file_share_name=file_share_name,
            guess_mime_type_enabled=guess_mime_type_enabled,
            kms_encrypted=kms_encrypted,
            kms_key_arn=kms_key_arn,
            nfs_file_share_defaults=nfs_file_share_defaults,
            notification_policy=notification_policy,
            object_acl=object_acl,
            read_only=read_only,
            requester_pays=requester_pays,
            squash=squash,
            tags=tags,
            tags_all=tags_all,
            timeouts=timeouts,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putCacheAttributes")
    def put_cache_attributes(
        self,
        *,
        cache_stale_timeout_in_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cache_stale_timeout_in_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#cache_stale_timeout_in_seconds StoragegatewayNfsFileShare#cache_stale_timeout_in_seconds}.
        '''
        value = StoragegatewayNfsFileShareCacheAttributes(
            cache_stale_timeout_in_seconds=cache_stale_timeout_in_seconds
        )

        return typing.cast(None, jsii.invoke(self, "putCacheAttributes", [value]))

    @jsii.member(jsii_name="putNfsFileShareDefaults")
    def put_nfs_file_share_defaults(
        self,
        *,
        directory_mode: typing.Optional[builtins.str] = None,
        file_mode: typing.Optional[builtins.str] = None,
        group_id: typing.Optional[builtins.str] = None,
        owner_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param directory_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#directory_mode StoragegatewayNfsFileShare#directory_mode}.
        :param file_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#file_mode StoragegatewayNfsFileShare#file_mode}.
        :param group_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#group_id StoragegatewayNfsFileShare#group_id}.
        :param owner_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#owner_id StoragegatewayNfsFileShare#owner_id}.
        '''
        value = StoragegatewayNfsFileShareNfsFileShareDefaults(
            directory_mode=directory_mode,
            file_mode=file_mode,
            group_id=group_id,
            owner_id=owner_id,
        )

        return typing.cast(None, jsii.invoke(self, "putNfsFileShareDefaults", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#create StoragegatewayNfsFileShare#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#delete StoragegatewayNfsFileShare#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#update StoragegatewayNfsFileShare#update}.
        '''
        value = StoragegatewayNfsFileShareTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetAuditDestinationArn")
    def reset_audit_destination_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuditDestinationArn", []))

    @jsii.member(jsii_name="resetCacheAttributes")
    def reset_cache_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCacheAttributes", []))

    @jsii.member(jsii_name="resetDefaultStorageClass")
    def reset_default_storage_class(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultStorageClass", []))

    @jsii.member(jsii_name="resetFileShareName")
    def reset_file_share_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFileShareName", []))

    @jsii.member(jsii_name="resetGuessMimeTypeEnabled")
    def reset_guess_mime_type_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGuessMimeTypeEnabled", []))

    @jsii.member(jsii_name="resetKmsEncrypted")
    def reset_kms_encrypted(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsEncrypted", []))

    @jsii.member(jsii_name="resetKmsKeyArn")
    def reset_kms_key_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyArn", []))

    @jsii.member(jsii_name="resetNfsFileShareDefaults")
    def reset_nfs_file_share_defaults(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNfsFileShareDefaults", []))

    @jsii.member(jsii_name="resetNotificationPolicy")
    def reset_notification_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotificationPolicy", []))

    @jsii.member(jsii_name="resetObjectAcl")
    def reset_object_acl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetObjectAcl", []))

    @jsii.member(jsii_name="resetReadOnly")
    def reset_read_only(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReadOnly", []))

    @jsii.member(jsii_name="resetRequesterPays")
    def reset_requester_pays(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequesterPays", []))

    @jsii.member(jsii_name="resetSquash")
    def reset_squash(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSquash", []))

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
    @jsii.member(jsii_name="cacheAttributes")
    def cache_attributes(
        self,
    ) -> "StoragegatewayNfsFileShareCacheAttributesOutputReference":
        return typing.cast("StoragegatewayNfsFileShareCacheAttributesOutputReference", jsii.get(self, "cacheAttributes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileshareId")
    def fileshare_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileshareId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nfsFileShareDefaults")
    def nfs_file_share_defaults(
        self,
    ) -> "StoragegatewayNfsFileShareNfsFileShareDefaultsOutputReference":
        return typing.cast("StoragegatewayNfsFileShareNfsFileShareDefaultsOutputReference", jsii.get(self, "nfsFileShareDefaults"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "StoragegatewayNfsFileShareTimeoutsOutputReference":
        return typing.cast("StoragegatewayNfsFileShareTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="auditDestinationArnInput")
    def audit_destination_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "auditDestinationArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheAttributesInput")
    def cache_attributes_input(
        self,
    ) -> typing.Optional["StoragegatewayNfsFileShareCacheAttributes"]:
        return typing.cast(typing.Optional["StoragegatewayNfsFileShareCacheAttributes"], jsii.get(self, "cacheAttributesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientListInput")
    def client_list_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "clientListInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultStorageClassInput")
    def default_storage_class_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultStorageClassInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileShareNameInput")
    def file_share_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fileShareNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gatewayArnInput")
    def gateway_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gatewayArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="guessMimeTypeEnabledInput")
    def guess_mime_type_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "guessMimeTypeEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsEncryptedInput")
    def kms_encrypted_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "kmsEncryptedInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyArnInput")
    def kms_key_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="locationArnInput")
    def location_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "locationArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nfsFileShareDefaultsInput")
    def nfs_file_share_defaults_input(
        self,
    ) -> typing.Optional["StoragegatewayNfsFileShareNfsFileShareDefaults"]:
        return typing.cast(typing.Optional["StoragegatewayNfsFileShareNfsFileShareDefaults"], jsii.get(self, "nfsFileShareDefaultsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notificationPolicyInput")
    def notification_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "notificationPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectAclInput")
    def object_acl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "objectAclInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readOnlyInput")
    def read_only_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "readOnlyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requesterPaysInput")
    def requester_pays_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "requesterPaysInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="squashInput")
    def squash_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "squashInput"))

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
    def timeouts_input(self) -> typing.Optional["StoragegatewayNfsFileShareTimeouts"]:
        return typing.cast(typing.Optional["StoragegatewayNfsFileShareTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="auditDestinationArn")
    def audit_destination_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "auditDestinationArn"))

    @audit_destination_arn.setter
    def audit_destination_arn(self, value: builtins.str) -> None:
        jsii.set(self, "auditDestinationArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientList")
    def client_list(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "clientList"))

    @client_list.setter
    def client_list(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "clientList", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultStorageClass")
    def default_storage_class(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultStorageClass"))

    @default_storage_class.setter
    def default_storage_class(self, value: builtins.str) -> None:
        jsii.set(self, "defaultStorageClass", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileShareName")
    def file_share_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileShareName"))

    @file_share_name.setter
    def file_share_name(self, value: builtins.str) -> None:
        jsii.set(self, "fileShareName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gatewayArn")
    def gateway_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gatewayArn"))

    @gateway_arn.setter
    def gateway_arn(self, value: builtins.str) -> None:
        jsii.set(self, "gatewayArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="guessMimeTypeEnabled")
    def guess_mime_type_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "guessMimeTypeEnabled"))

    @guess_mime_type_enabled.setter
    def guess_mime_type_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "guessMimeTypeEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsEncrypted")
    def kms_encrypted(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "kmsEncrypted"))

    @kms_encrypted.setter
    def kms_encrypted(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "kmsEncrypted", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyArn")
    def kms_key_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyArn"))

    @kms_key_arn.setter
    def kms_key_arn(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="locationArn")
    def location_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "locationArn"))

    @location_arn.setter
    def location_arn(self, value: builtins.str) -> None:
        jsii.set(self, "locationArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notificationPolicy")
    def notification_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notificationPolicy"))

    @notification_policy.setter
    def notification_policy(self, value: builtins.str) -> None:
        jsii.set(self, "notificationPolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectAcl")
    def object_acl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "objectAcl"))

    @object_acl.setter
    def object_acl(self, value: builtins.str) -> None:
        jsii.set(self, "objectAcl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readOnly")
    def read_only(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "readOnly"))

    @read_only.setter
    def read_only(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "readOnly", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requesterPays")
    def requester_pays(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "requesterPays"))

    @requester_pays.setter
    def requester_pays(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "requesterPays", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="squash")
    def squash(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "squash"))

    @squash.setter
    def squash(self, value: builtins.str) -> None:
        jsii.set(self, "squash", value)

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
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewayNfsFileShareCacheAttributes",
    jsii_struct_bases=[],
    name_mapping={"cache_stale_timeout_in_seconds": "cacheStaleTimeoutInSeconds"},
)
class StoragegatewayNfsFileShareCacheAttributes:
    def __init__(
        self,
        *,
        cache_stale_timeout_in_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cache_stale_timeout_in_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#cache_stale_timeout_in_seconds StoragegatewayNfsFileShare#cache_stale_timeout_in_seconds}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if cache_stale_timeout_in_seconds is not None:
            self._values["cache_stale_timeout_in_seconds"] = cache_stale_timeout_in_seconds

    @builtins.property
    def cache_stale_timeout_in_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#cache_stale_timeout_in_seconds StoragegatewayNfsFileShare#cache_stale_timeout_in_seconds}.'''
        result = self._values.get("cache_stale_timeout_in_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StoragegatewayNfsFileShareCacheAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StoragegatewayNfsFileShareCacheAttributesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewayNfsFileShareCacheAttributesOutputReference",
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

    @jsii.member(jsii_name="resetCacheStaleTimeoutInSeconds")
    def reset_cache_stale_timeout_in_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCacheStaleTimeoutInSeconds", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheStaleTimeoutInSecondsInput")
    def cache_stale_timeout_in_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cacheStaleTimeoutInSecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheStaleTimeoutInSeconds")
    def cache_stale_timeout_in_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cacheStaleTimeoutInSeconds"))

    @cache_stale_timeout_in_seconds.setter
    def cache_stale_timeout_in_seconds(self, value: jsii.Number) -> None:
        jsii.set(self, "cacheStaleTimeoutInSeconds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[StoragegatewayNfsFileShareCacheAttributes]:
        return typing.cast(typing.Optional[StoragegatewayNfsFileShareCacheAttributes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[StoragegatewayNfsFileShareCacheAttributes],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewayNfsFileShareConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "client_list": "clientList",
        "gateway_arn": "gatewayArn",
        "location_arn": "locationArn",
        "role_arn": "roleArn",
        "audit_destination_arn": "auditDestinationArn",
        "cache_attributes": "cacheAttributes",
        "default_storage_class": "defaultStorageClass",
        "file_share_name": "fileShareName",
        "guess_mime_type_enabled": "guessMimeTypeEnabled",
        "kms_encrypted": "kmsEncrypted",
        "kms_key_arn": "kmsKeyArn",
        "nfs_file_share_defaults": "nfsFileShareDefaults",
        "notification_policy": "notificationPolicy",
        "object_acl": "objectAcl",
        "read_only": "readOnly",
        "requester_pays": "requesterPays",
        "squash": "squash",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
    },
)
class StoragegatewayNfsFileShareConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        client_list: typing.Sequence[builtins.str],
        gateway_arn: builtins.str,
        location_arn: builtins.str,
        role_arn: builtins.str,
        audit_destination_arn: typing.Optional[builtins.str] = None,
        cache_attributes: typing.Optional[StoragegatewayNfsFileShareCacheAttributes] = None,
        default_storage_class: typing.Optional[builtins.str] = None,
        file_share_name: typing.Optional[builtins.str] = None,
        guess_mime_type_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        kms_encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        kms_key_arn: typing.Optional[builtins.str] = None,
        nfs_file_share_defaults: typing.Optional["StoragegatewayNfsFileShareNfsFileShareDefaults"] = None,
        notification_policy: typing.Optional[builtins.str] = None,
        object_acl: typing.Optional[builtins.str] = None,
        read_only: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        requester_pays: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        squash: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["StoragegatewayNfsFileShareTimeouts"] = None,
    ) -> None:
        '''AWS Storage Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param client_list: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#client_list StoragegatewayNfsFileShare#client_list}.
        :param gateway_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#gateway_arn StoragegatewayNfsFileShare#gateway_arn}.
        :param location_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#location_arn StoragegatewayNfsFileShare#location_arn}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#role_arn StoragegatewayNfsFileShare#role_arn}.
        :param audit_destination_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#audit_destination_arn StoragegatewayNfsFileShare#audit_destination_arn}.
        :param cache_attributes: cache_attributes block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#cache_attributes StoragegatewayNfsFileShare#cache_attributes}
        :param default_storage_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#default_storage_class StoragegatewayNfsFileShare#default_storage_class}.
        :param file_share_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#file_share_name StoragegatewayNfsFileShare#file_share_name}.
        :param guess_mime_type_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#guess_mime_type_enabled StoragegatewayNfsFileShare#guess_mime_type_enabled}.
        :param kms_encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#kms_encrypted StoragegatewayNfsFileShare#kms_encrypted}.
        :param kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#kms_key_arn StoragegatewayNfsFileShare#kms_key_arn}.
        :param nfs_file_share_defaults: nfs_file_share_defaults block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#nfs_file_share_defaults StoragegatewayNfsFileShare#nfs_file_share_defaults}
        :param notification_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#notification_policy StoragegatewayNfsFileShare#notification_policy}.
        :param object_acl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#object_acl StoragegatewayNfsFileShare#object_acl}.
        :param read_only: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#read_only StoragegatewayNfsFileShare#read_only}.
        :param requester_pays: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#requester_pays StoragegatewayNfsFileShare#requester_pays}.
        :param squash: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#squash StoragegatewayNfsFileShare#squash}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#tags StoragegatewayNfsFileShare#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#tags_all StoragegatewayNfsFileShare#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#timeouts StoragegatewayNfsFileShare#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(cache_attributes, dict):
            cache_attributes = StoragegatewayNfsFileShareCacheAttributes(**cache_attributes)
        if isinstance(nfs_file_share_defaults, dict):
            nfs_file_share_defaults = StoragegatewayNfsFileShareNfsFileShareDefaults(**nfs_file_share_defaults)
        if isinstance(timeouts, dict):
            timeouts = StoragegatewayNfsFileShareTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "client_list": client_list,
            "gateway_arn": gateway_arn,
            "location_arn": location_arn,
            "role_arn": role_arn,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if audit_destination_arn is not None:
            self._values["audit_destination_arn"] = audit_destination_arn
        if cache_attributes is not None:
            self._values["cache_attributes"] = cache_attributes
        if default_storage_class is not None:
            self._values["default_storage_class"] = default_storage_class
        if file_share_name is not None:
            self._values["file_share_name"] = file_share_name
        if guess_mime_type_enabled is not None:
            self._values["guess_mime_type_enabled"] = guess_mime_type_enabled
        if kms_encrypted is not None:
            self._values["kms_encrypted"] = kms_encrypted
        if kms_key_arn is not None:
            self._values["kms_key_arn"] = kms_key_arn
        if nfs_file_share_defaults is not None:
            self._values["nfs_file_share_defaults"] = nfs_file_share_defaults
        if notification_policy is not None:
            self._values["notification_policy"] = notification_policy
        if object_acl is not None:
            self._values["object_acl"] = object_acl
        if read_only is not None:
            self._values["read_only"] = read_only
        if requester_pays is not None:
            self._values["requester_pays"] = requester_pays
        if squash is not None:
            self._values["squash"] = squash
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
    def client_list(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#client_list StoragegatewayNfsFileShare#client_list}.'''
        result = self._values.get("client_list")
        assert result is not None, "Required property 'client_list' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def gateway_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#gateway_arn StoragegatewayNfsFileShare#gateway_arn}.'''
        result = self._values.get("gateway_arn")
        assert result is not None, "Required property 'gateway_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def location_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#location_arn StoragegatewayNfsFileShare#location_arn}.'''
        result = self._values.get("location_arn")
        assert result is not None, "Required property 'location_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#role_arn StoragegatewayNfsFileShare#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def audit_destination_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#audit_destination_arn StoragegatewayNfsFileShare#audit_destination_arn}.'''
        result = self._values.get("audit_destination_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cache_attributes(
        self,
    ) -> typing.Optional[StoragegatewayNfsFileShareCacheAttributes]:
        '''cache_attributes block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#cache_attributes StoragegatewayNfsFileShare#cache_attributes}
        '''
        result = self._values.get("cache_attributes")
        return typing.cast(typing.Optional[StoragegatewayNfsFileShareCacheAttributes], result)

    @builtins.property
    def default_storage_class(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#default_storage_class StoragegatewayNfsFileShare#default_storage_class}.'''
        result = self._values.get("default_storage_class")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def file_share_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#file_share_name StoragegatewayNfsFileShare#file_share_name}.'''
        result = self._values.get("file_share_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def guess_mime_type_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#guess_mime_type_enabled StoragegatewayNfsFileShare#guess_mime_type_enabled}.'''
        result = self._values.get("guess_mime_type_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def kms_encrypted(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#kms_encrypted StoragegatewayNfsFileShare#kms_encrypted}.'''
        result = self._values.get("kms_encrypted")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def kms_key_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#kms_key_arn StoragegatewayNfsFileShare#kms_key_arn}.'''
        result = self._values.get("kms_key_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nfs_file_share_defaults(
        self,
    ) -> typing.Optional["StoragegatewayNfsFileShareNfsFileShareDefaults"]:
        '''nfs_file_share_defaults block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#nfs_file_share_defaults StoragegatewayNfsFileShare#nfs_file_share_defaults}
        '''
        result = self._values.get("nfs_file_share_defaults")
        return typing.cast(typing.Optional["StoragegatewayNfsFileShareNfsFileShareDefaults"], result)

    @builtins.property
    def notification_policy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#notification_policy StoragegatewayNfsFileShare#notification_policy}.'''
        result = self._values.get("notification_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def object_acl(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#object_acl StoragegatewayNfsFileShare#object_acl}.'''
        result = self._values.get("object_acl")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def read_only(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#read_only StoragegatewayNfsFileShare#read_only}.'''
        result = self._values.get("read_only")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def requester_pays(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#requester_pays StoragegatewayNfsFileShare#requester_pays}.'''
        result = self._values.get("requester_pays")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def squash(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#squash StoragegatewayNfsFileShare#squash}.'''
        result = self._values.get("squash")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#tags StoragegatewayNfsFileShare#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#tags_all StoragegatewayNfsFileShare#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["StoragegatewayNfsFileShareTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#timeouts StoragegatewayNfsFileShare#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["StoragegatewayNfsFileShareTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StoragegatewayNfsFileShareConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewayNfsFileShareNfsFileShareDefaults",
    jsii_struct_bases=[],
    name_mapping={
        "directory_mode": "directoryMode",
        "file_mode": "fileMode",
        "group_id": "groupId",
        "owner_id": "ownerId",
    },
)
class StoragegatewayNfsFileShareNfsFileShareDefaults:
    def __init__(
        self,
        *,
        directory_mode: typing.Optional[builtins.str] = None,
        file_mode: typing.Optional[builtins.str] = None,
        group_id: typing.Optional[builtins.str] = None,
        owner_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param directory_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#directory_mode StoragegatewayNfsFileShare#directory_mode}.
        :param file_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#file_mode StoragegatewayNfsFileShare#file_mode}.
        :param group_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#group_id StoragegatewayNfsFileShare#group_id}.
        :param owner_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#owner_id StoragegatewayNfsFileShare#owner_id}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if directory_mode is not None:
            self._values["directory_mode"] = directory_mode
        if file_mode is not None:
            self._values["file_mode"] = file_mode
        if group_id is not None:
            self._values["group_id"] = group_id
        if owner_id is not None:
            self._values["owner_id"] = owner_id

    @builtins.property
    def directory_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#directory_mode StoragegatewayNfsFileShare#directory_mode}.'''
        result = self._values.get("directory_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def file_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#file_mode StoragegatewayNfsFileShare#file_mode}.'''
        result = self._values.get("file_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def group_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#group_id StoragegatewayNfsFileShare#group_id}.'''
        result = self._values.get("group_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def owner_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#owner_id StoragegatewayNfsFileShare#owner_id}.'''
        result = self._values.get("owner_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StoragegatewayNfsFileShareNfsFileShareDefaults(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StoragegatewayNfsFileShareNfsFileShareDefaultsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewayNfsFileShareNfsFileShareDefaultsOutputReference",
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

    @jsii.member(jsii_name="resetDirectoryMode")
    def reset_directory_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDirectoryMode", []))

    @jsii.member(jsii_name="resetFileMode")
    def reset_file_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFileMode", []))

    @jsii.member(jsii_name="resetGroupId")
    def reset_group_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGroupId", []))

    @jsii.member(jsii_name="resetOwnerId")
    def reset_owner_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOwnerId", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="directoryModeInput")
    def directory_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "directoryModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileModeInput")
    def file_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fileModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="groupIdInput")
    def group_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "groupIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerIdInput")
    def owner_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ownerIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="directoryMode")
    def directory_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "directoryMode"))

    @directory_mode.setter
    def directory_mode(self, value: builtins.str) -> None:
        jsii.set(self, "directoryMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileMode")
    def file_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileMode"))

    @file_mode.setter
    def file_mode(self, value: builtins.str) -> None:
        jsii.set(self, "fileMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="groupId")
    def group_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "groupId"))

    @group_id.setter
    def group_id(self, value: builtins.str) -> None:
        jsii.set(self, "groupId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerId")
    def owner_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ownerId"))

    @owner_id.setter
    def owner_id(self, value: builtins.str) -> None:
        jsii.set(self, "ownerId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[StoragegatewayNfsFileShareNfsFileShareDefaults]:
        return typing.cast(typing.Optional[StoragegatewayNfsFileShareNfsFileShareDefaults], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[StoragegatewayNfsFileShareNfsFileShareDefaults],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewayNfsFileShareTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class StoragegatewayNfsFileShareTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#create StoragegatewayNfsFileShare#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#delete StoragegatewayNfsFileShare#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#update StoragegatewayNfsFileShare#update}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#create StoragegatewayNfsFileShare#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#delete StoragegatewayNfsFileShare#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_nfs_file_share#update StoragegatewayNfsFileShare#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StoragegatewayNfsFileShareTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StoragegatewayNfsFileShareTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewayNfsFileShareTimeoutsOutputReference",
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
    def internal_value(self) -> typing.Optional[StoragegatewayNfsFileShareTimeouts]:
        return typing.cast(typing.Optional[StoragegatewayNfsFileShareTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[StoragegatewayNfsFileShareTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


class StoragegatewaySmbFileShare(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewaySmbFileShare",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share aws_storagegateway_smb_file_share}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        gateway_arn: builtins.str,
        location_arn: builtins.str,
        role_arn: builtins.str,
        access_based_enumeration: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        admin_user_list: typing.Optional[typing.Sequence[builtins.str]] = None,
        audit_destination_arn: typing.Optional[builtins.str] = None,
        authentication: typing.Optional[builtins.str] = None,
        bucket_region: typing.Optional[builtins.str] = None,
        cache_attributes: typing.Optional["StoragegatewaySmbFileShareCacheAttributes"] = None,
        case_sensitivity: typing.Optional[builtins.str] = None,
        default_storage_class: typing.Optional[builtins.str] = None,
        file_share_name: typing.Optional[builtins.str] = None,
        guess_mime_type_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        invalid_user_list: typing.Optional[typing.Sequence[builtins.str]] = None,
        kms_encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        kms_key_arn: typing.Optional[builtins.str] = None,
        notification_policy: typing.Optional[builtins.str] = None,
        object_acl: typing.Optional[builtins.str] = None,
        oplocks_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        read_only: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        requester_pays: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        smb_acl_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["StoragegatewaySmbFileShareTimeouts"] = None,
        valid_user_list: typing.Optional[typing.Sequence[builtins.str]] = None,
        vpc_endpoint_dns_name: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share aws_storagegateway_smb_file_share} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param gateway_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#gateway_arn StoragegatewaySmbFileShare#gateway_arn}.
        :param location_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#location_arn StoragegatewaySmbFileShare#location_arn}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#role_arn StoragegatewaySmbFileShare#role_arn}.
        :param access_based_enumeration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#access_based_enumeration StoragegatewaySmbFileShare#access_based_enumeration}.
        :param admin_user_list: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#admin_user_list StoragegatewaySmbFileShare#admin_user_list}.
        :param audit_destination_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#audit_destination_arn StoragegatewaySmbFileShare#audit_destination_arn}.
        :param authentication: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#authentication StoragegatewaySmbFileShare#authentication}.
        :param bucket_region: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#bucket_region StoragegatewaySmbFileShare#bucket_region}.
        :param cache_attributes: cache_attributes block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#cache_attributes StoragegatewaySmbFileShare#cache_attributes}
        :param case_sensitivity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#case_sensitivity StoragegatewaySmbFileShare#case_sensitivity}.
        :param default_storage_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#default_storage_class StoragegatewaySmbFileShare#default_storage_class}.
        :param file_share_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#file_share_name StoragegatewaySmbFileShare#file_share_name}.
        :param guess_mime_type_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#guess_mime_type_enabled StoragegatewaySmbFileShare#guess_mime_type_enabled}.
        :param invalid_user_list: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#invalid_user_list StoragegatewaySmbFileShare#invalid_user_list}.
        :param kms_encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#kms_encrypted StoragegatewaySmbFileShare#kms_encrypted}.
        :param kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#kms_key_arn StoragegatewaySmbFileShare#kms_key_arn}.
        :param notification_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#notification_policy StoragegatewaySmbFileShare#notification_policy}.
        :param object_acl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#object_acl StoragegatewaySmbFileShare#object_acl}.
        :param oplocks_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#oplocks_enabled StoragegatewaySmbFileShare#oplocks_enabled}.
        :param read_only: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#read_only StoragegatewaySmbFileShare#read_only}.
        :param requester_pays: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#requester_pays StoragegatewaySmbFileShare#requester_pays}.
        :param smb_acl_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#smb_acl_enabled StoragegatewaySmbFileShare#smb_acl_enabled}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#tags StoragegatewaySmbFileShare#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#tags_all StoragegatewaySmbFileShare#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#timeouts StoragegatewaySmbFileShare#timeouts}
        :param valid_user_list: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#valid_user_list StoragegatewaySmbFileShare#valid_user_list}.
        :param vpc_endpoint_dns_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#vpc_endpoint_dns_name StoragegatewaySmbFileShare#vpc_endpoint_dns_name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = StoragegatewaySmbFileShareConfig(
            gateway_arn=gateway_arn,
            location_arn=location_arn,
            role_arn=role_arn,
            access_based_enumeration=access_based_enumeration,
            admin_user_list=admin_user_list,
            audit_destination_arn=audit_destination_arn,
            authentication=authentication,
            bucket_region=bucket_region,
            cache_attributes=cache_attributes,
            case_sensitivity=case_sensitivity,
            default_storage_class=default_storage_class,
            file_share_name=file_share_name,
            guess_mime_type_enabled=guess_mime_type_enabled,
            invalid_user_list=invalid_user_list,
            kms_encrypted=kms_encrypted,
            kms_key_arn=kms_key_arn,
            notification_policy=notification_policy,
            object_acl=object_acl,
            oplocks_enabled=oplocks_enabled,
            read_only=read_only,
            requester_pays=requester_pays,
            smb_acl_enabled=smb_acl_enabled,
            tags=tags,
            tags_all=tags_all,
            timeouts=timeouts,
            valid_user_list=valid_user_list,
            vpc_endpoint_dns_name=vpc_endpoint_dns_name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putCacheAttributes")
    def put_cache_attributes(
        self,
        *,
        cache_stale_timeout_in_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cache_stale_timeout_in_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#cache_stale_timeout_in_seconds StoragegatewaySmbFileShare#cache_stale_timeout_in_seconds}.
        '''
        value = StoragegatewaySmbFileShareCacheAttributes(
            cache_stale_timeout_in_seconds=cache_stale_timeout_in_seconds
        )

        return typing.cast(None, jsii.invoke(self, "putCacheAttributes", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#create StoragegatewaySmbFileShare#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#delete StoragegatewaySmbFileShare#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#update StoragegatewaySmbFileShare#update}.
        '''
        value = StoragegatewaySmbFileShareTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetAccessBasedEnumeration")
    def reset_access_based_enumeration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessBasedEnumeration", []))

    @jsii.member(jsii_name="resetAdminUserList")
    def reset_admin_user_list(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdminUserList", []))

    @jsii.member(jsii_name="resetAuditDestinationArn")
    def reset_audit_destination_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuditDestinationArn", []))

    @jsii.member(jsii_name="resetAuthentication")
    def reset_authentication(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthentication", []))

    @jsii.member(jsii_name="resetBucketRegion")
    def reset_bucket_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBucketRegion", []))

    @jsii.member(jsii_name="resetCacheAttributes")
    def reset_cache_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCacheAttributes", []))

    @jsii.member(jsii_name="resetCaseSensitivity")
    def reset_case_sensitivity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCaseSensitivity", []))

    @jsii.member(jsii_name="resetDefaultStorageClass")
    def reset_default_storage_class(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultStorageClass", []))

    @jsii.member(jsii_name="resetFileShareName")
    def reset_file_share_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFileShareName", []))

    @jsii.member(jsii_name="resetGuessMimeTypeEnabled")
    def reset_guess_mime_type_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGuessMimeTypeEnabled", []))

    @jsii.member(jsii_name="resetInvalidUserList")
    def reset_invalid_user_list(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInvalidUserList", []))

    @jsii.member(jsii_name="resetKmsEncrypted")
    def reset_kms_encrypted(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsEncrypted", []))

    @jsii.member(jsii_name="resetKmsKeyArn")
    def reset_kms_key_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyArn", []))

    @jsii.member(jsii_name="resetNotificationPolicy")
    def reset_notification_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotificationPolicy", []))

    @jsii.member(jsii_name="resetObjectAcl")
    def reset_object_acl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetObjectAcl", []))

    @jsii.member(jsii_name="resetOplocksEnabled")
    def reset_oplocks_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOplocksEnabled", []))

    @jsii.member(jsii_name="resetReadOnly")
    def reset_read_only(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReadOnly", []))

    @jsii.member(jsii_name="resetRequesterPays")
    def reset_requester_pays(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequesterPays", []))

    @jsii.member(jsii_name="resetSmbAclEnabled")
    def reset_smb_acl_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSmbAclEnabled", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="resetValidUserList")
    def reset_valid_user_list(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValidUserList", []))

    @jsii.member(jsii_name="resetVpcEndpointDnsName")
    def reset_vpc_endpoint_dns_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVpcEndpointDnsName", []))

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
    @jsii.member(jsii_name="cacheAttributes")
    def cache_attributes(
        self,
    ) -> "StoragegatewaySmbFileShareCacheAttributesOutputReference":
        return typing.cast("StoragegatewaySmbFileShareCacheAttributesOutputReference", jsii.get(self, "cacheAttributes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileshareId")
    def fileshare_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileshareId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "StoragegatewaySmbFileShareTimeoutsOutputReference":
        return typing.cast("StoragegatewaySmbFileShareTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessBasedEnumerationInput")
    def access_based_enumeration_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "accessBasedEnumerationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="adminUserListInput")
    def admin_user_list_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "adminUserListInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="auditDestinationArnInput")
    def audit_destination_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "auditDestinationArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authenticationInput")
    def authentication_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authenticationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketRegionInput")
    def bucket_region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketRegionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheAttributesInput")
    def cache_attributes_input(
        self,
    ) -> typing.Optional["StoragegatewaySmbFileShareCacheAttributes"]:
        return typing.cast(typing.Optional["StoragegatewaySmbFileShareCacheAttributes"], jsii.get(self, "cacheAttributesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="caseSensitivityInput")
    def case_sensitivity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caseSensitivityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultStorageClassInput")
    def default_storage_class_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultStorageClassInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileShareNameInput")
    def file_share_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fileShareNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gatewayArnInput")
    def gateway_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gatewayArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="guessMimeTypeEnabledInput")
    def guess_mime_type_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "guessMimeTypeEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="invalidUserListInput")
    def invalid_user_list_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "invalidUserListInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsEncryptedInput")
    def kms_encrypted_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "kmsEncryptedInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyArnInput")
    def kms_key_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="locationArnInput")
    def location_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "locationArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notificationPolicyInput")
    def notification_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "notificationPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectAclInput")
    def object_acl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "objectAclInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="oplocksEnabledInput")
    def oplocks_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "oplocksEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readOnlyInput")
    def read_only_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "readOnlyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requesterPaysInput")
    def requester_pays_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "requesterPaysInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="smbAclEnabledInput")
    def smb_acl_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "smbAclEnabledInput"))

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
    def timeouts_input(self) -> typing.Optional["StoragegatewaySmbFileShareTimeouts"]:
        return typing.cast(typing.Optional["StoragegatewaySmbFileShareTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="validUserListInput")
    def valid_user_list_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "validUserListInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcEndpointDnsNameInput")
    def vpc_endpoint_dns_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vpcEndpointDnsNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessBasedEnumeration")
    def access_based_enumeration(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "accessBasedEnumeration"))

    @access_based_enumeration.setter
    def access_based_enumeration(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "accessBasedEnumeration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="adminUserList")
    def admin_user_list(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "adminUserList"))

    @admin_user_list.setter
    def admin_user_list(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "adminUserList", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="auditDestinationArn")
    def audit_destination_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "auditDestinationArn"))

    @audit_destination_arn.setter
    def audit_destination_arn(self, value: builtins.str) -> None:
        jsii.set(self, "auditDestinationArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authentication")
    def authentication(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authentication"))

    @authentication.setter
    def authentication(self, value: builtins.str) -> None:
        jsii.set(self, "authentication", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketRegion")
    def bucket_region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketRegion"))

    @bucket_region.setter
    def bucket_region(self, value: builtins.str) -> None:
        jsii.set(self, "bucketRegion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="caseSensitivity")
    def case_sensitivity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "caseSensitivity"))

    @case_sensitivity.setter
    def case_sensitivity(self, value: builtins.str) -> None:
        jsii.set(self, "caseSensitivity", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultStorageClass")
    def default_storage_class(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultStorageClass"))

    @default_storage_class.setter
    def default_storage_class(self, value: builtins.str) -> None:
        jsii.set(self, "defaultStorageClass", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileShareName")
    def file_share_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileShareName"))

    @file_share_name.setter
    def file_share_name(self, value: builtins.str) -> None:
        jsii.set(self, "fileShareName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gatewayArn")
    def gateway_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gatewayArn"))

    @gateway_arn.setter
    def gateway_arn(self, value: builtins.str) -> None:
        jsii.set(self, "gatewayArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="guessMimeTypeEnabled")
    def guess_mime_type_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "guessMimeTypeEnabled"))

    @guess_mime_type_enabled.setter
    def guess_mime_type_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "guessMimeTypeEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="invalidUserList")
    def invalid_user_list(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "invalidUserList"))

    @invalid_user_list.setter
    def invalid_user_list(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "invalidUserList", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsEncrypted")
    def kms_encrypted(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "kmsEncrypted"))

    @kms_encrypted.setter
    def kms_encrypted(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "kmsEncrypted", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyArn")
    def kms_key_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyArn"))

    @kms_key_arn.setter
    def kms_key_arn(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="locationArn")
    def location_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "locationArn"))

    @location_arn.setter
    def location_arn(self, value: builtins.str) -> None:
        jsii.set(self, "locationArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notificationPolicy")
    def notification_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notificationPolicy"))

    @notification_policy.setter
    def notification_policy(self, value: builtins.str) -> None:
        jsii.set(self, "notificationPolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectAcl")
    def object_acl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "objectAcl"))

    @object_acl.setter
    def object_acl(self, value: builtins.str) -> None:
        jsii.set(self, "objectAcl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="oplocksEnabled")
    def oplocks_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "oplocksEnabled"))

    @oplocks_enabled.setter
    def oplocks_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "oplocksEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readOnly")
    def read_only(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "readOnly"))

    @read_only.setter
    def read_only(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "readOnly", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requesterPays")
    def requester_pays(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "requesterPays"))

    @requester_pays.setter
    def requester_pays(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "requesterPays", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="smbAclEnabled")
    def smb_acl_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "smbAclEnabled"))

    @smb_acl_enabled.setter
    def smb_acl_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "smbAclEnabled", value)

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
    @jsii.member(jsii_name="validUserList")
    def valid_user_list(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "validUserList"))

    @valid_user_list.setter
    def valid_user_list(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "validUserList", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcEndpointDnsName")
    def vpc_endpoint_dns_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcEndpointDnsName"))

    @vpc_endpoint_dns_name.setter
    def vpc_endpoint_dns_name(self, value: builtins.str) -> None:
        jsii.set(self, "vpcEndpointDnsName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewaySmbFileShareCacheAttributes",
    jsii_struct_bases=[],
    name_mapping={"cache_stale_timeout_in_seconds": "cacheStaleTimeoutInSeconds"},
)
class StoragegatewaySmbFileShareCacheAttributes:
    def __init__(
        self,
        *,
        cache_stale_timeout_in_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cache_stale_timeout_in_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#cache_stale_timeout_in_seconds StoragegatewaySmbFileShare#cache_stale_timeout_in_seconds}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if cache_stale_timeout_in_seconds is not None:
            self._values["cache_stale_timeout_in_seconds"] = cache_stale_timeout_in_seconds

    @builtins.property
    def cache_stale_timeout_in_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#cache_stale_timeout_in_seconds StoragegatewaySmbFileShare#cache_stale_timeout_in_seconds}.'''
        result = self._values.get("cache_stale_timeout_in_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StoragegatewaySmbFileShareCacheAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StoragegatewaySmbFileShareCacheAttributesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewaySmbFileShareCacheAttributesOutputReference",
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

    @jsii.member(jsii_name="resetCacheStaleTimeoutInSeconds")
    def reset_cache_stale_timeout_in_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCacheStaleTimeoutInSeconds", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheStaleTimeoutInSecondsInput")
    def cache_stale_timeout_in_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cacheStaleTimeoutInSecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheStaleTimeoutInSeconds")
    def cache_stale_timeout_in_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cacheStaleTimeoutInSeconds"))

    @cache_stale_timeout_in_seconds.setter
    def cache_stale_timeout_in_seconds(self, value: jsii.Number) -> None:
        jsii.set(self, "cacheStaleTimeoutInSeconds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[StoragegatewaySmbFileShareCacheAttributes]:
        return typing.cast(typing.Optional[StoragegatewaySmbFileShareCacheAttributes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[StoragegatewaySmbFileShareCacheAttributes],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewaySmbFileShareConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "gateway_arn": "gatewayArn",
        "location_arn": "locationArn",
        "role_arn": "roleArn",
        "access_based_enumeration": "accessBasedEnumeration",
        "admin_user_list": "adminUserList",
        "audit_destination_arn": "auditDestinationArn",
        "authentication": "authentication",
        "bucket_region": "bucketRegion",
        "cache_attributes": "cacheAttributes",
        "case_sensitivity": "caseSensitivity",
        "default_storage_class": "defaultStorageClass",
        "file_share_name": "fileShareName",
        "guess_mime_type_enabled": "guessMimeTypeEnabled",
        "invalid_user_list": "invalidUserList",
        "kms_encrypted": "kmsEncrypted",
        "kms_key_arn": "kmsKeyArn",
        "notification_policy": "notificationPolicy",
        "object_acl": "objectAcl",
        "oplocks_enabled": "oplocksEnabled",
        "read_only": "readOnly",
        "requester_pays": "requesterPays",
        "smb_acl_enabled": "smbAclEnabled",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
        "valid_user_list": "validUserList",
        "vpc_endpoint_dns_name": "vpcEndpointDnsName",
    },
)
class StoragegatewaySmbFileShareConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        gateway_arn: builtins.str,
        location_arn: builtins.str,
        role_arn: builtins.str,
        access_based_enumeration: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        admin_user_list: typing.Optional[typing.Sequence[builtins.str]] = None,
        audit_destination_arn: typing.Optional[builtins.str] = None,
        authentication: typing.Optional[builtins.str] = None,
        bucket_region: typing.Optional[builtins.str] = None,
        cache_attributes: typing.Optional[StoragegatewaySmbFileShareCacheAttributes] = None,
        case_sensitivity: typing.Optional[builtins.str] = None,
        default_storage_class: typing.Optional[builtins.str] = None,
        file_share_name: typing.Optional[builtins.str] = None,
        guess_mime_type_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        invalid_user_list: typing.Optional[typing.Sequence[builtins.str]] = None,
        kms_encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        kms_key_arn: typing.Optional[builtins.str] = None,
        notification_policy: typing.Optional[builtins.str] = None,
        object_acl: typing.Optional[builtins.str] = None,
        oplocks_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        read_only: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        requester_pays: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        smb_acl_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["StoragegatewaySmbFileShareTimeouts"] = None,
        valid_user_list: typing.Optional[typing.Sequence[builtins.str]] = None,
        vpc_endpoint_dns_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Storage Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param gateway_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#gateway_arn StoragegatewaySmbFileShare#gateway_arn}.
        :param location_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#location_arn StoragegatewaySmbFileShare#location_arn}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#role_arn StoragegatewaySmbFileShare#role_arn}.
        :param access_based_enumeration: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#access_based_enumeration StoragegatewaySmbFileShare#access_based_enumeration}.
        :param admin_user_list: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#admin_user_list StoragegatewaySmbFileShare#admin_user_list}.
        :param audit_destination_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#audit_destination_arn StoragegatewaySmbFileShare#audit_destination_arn}.
        :param authentication: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#authentication StoragegatewaySmbFileShare#authentication}.
        :param bucket_region: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#bucket_region StoragegatewaySmbFileShare#bucket_region}.
        :param cache_attributes: cache_attributes block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#cache_attributes StoragegatewaySmbFileShare#cache_attributes}
        :param case_sensitivity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#case_sensitivity StoragegatewaySmbFileShare#case_sensitivity}.
        :param default_storage_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#default_storage_class StoragegatewaySmbFileShare#default_storage_class}.
        :param file_share_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#file_share_name StoragegatewaySmbFileShare#file_share_name}.
        :param guess_mime_type_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#guess_mime_type_enabled StoragegatewaySmbFileShare#guess_mime_type_enabled}.
        :param invalid_user_list: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#invalid_user_list StoragegatewaySmbFileShare#invalid_user_list}.
        :param kms_encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#kms_encrypted StoragegatewaySmbFileShare#kms_encrypted}.
        :param kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#kms_key_arn StoragegatewaySmbFileShare#kms_key_arn}.
        :param notification_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#notification_policy StoragegatewaySmbFileShare#notification_policy}.
        :param object_acl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#object_acl StoragegatewaySmbFileShare#object_acl}.
        :param oplocks_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#oplocks_enabled StoragegatewaySmbFileShare#oplocks_enabled}.
        :param read_only: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#read_only StoragegatewaySmbFileShare#read_only}.
        :param requester_pays: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#requester_pays StoragegatewaySmbFileShare#requester_pays}.
        :param smb_acl_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#smb_acl_enabled StoragegatewaySmbFileShare#smb_acl_enabled}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#tags StoragegatewaySmbFileShare#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#tags_all StoragegatewaySmbFileShare#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#timeouts StoragegatewaySmbFileShare#timeouts}
        :param valid_user_list: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#valid_user_list StoragegatewaySmbFileShare#valid_user_list}.
        :param vpc_endpoint_dns_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#vpc_endpoint_dns_name StoragegatewaySmbFileShare#vpc_endpoint_dns_name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(cache_attributes, dict):
            cache_attributes = StoragegatewaySmbFileShareCacheAttributes(**cache_attributes)
        if isinstance(timeouts, dict):
            timeouts = StoragegatewaySmbFileShareTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "gateway_arn": gateway_arn,
            "location_arn": location_arn,
            "role_arn": role_arn,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if access_based_enumeration is not None:
            self._values["access_based_enumeration"] = access_based_enumeration
        if admin_user_list is not None:
            self._values["admin_user_list"] = admin_user_list
        if audit_destination_arn is not None:
            self._values["audit_destination_arn"] = audit_destination_arn
        if authentication is not None:
            self._values["authentication"] = authentication
        if bucket_region is not None:
            self._values["bucket_region"] = bucket_region
        if cache_attributes is not None:
            self._values["cache_attributes"] = cache_attributes
        if case_sensitivity is not None:
            self._values["case_sensitivity"] = case_sensitivity
        if default_storage_class is not None:
            self._values["default_storage_class"] = default_storage_class
        if file_share_name is not None:
            self._values["file_share_name"] = file_share_name
        if guess_mime_type_enabled is not None:
            self._values["guess_mime_type_enabled"] = guess_mime_type_enabled
        if invalid_user_list is not None:
            self._values["invalid_user_list"] = invalid_user_list
        if kms_encrypted is not None:
            self._values["kms_encrypted"] = kms_encrypted
        if kms_key_arn is not None:
            self._values["kms_key_arn"] = kms_key_arn
        if notification_policy is not None:
            self._values["notification_policy"] = notification_policy
        if object_acl is not None:
            self._values["object_acl"] = object_acl
        if oplocks_enabled is not None:
            self._values["oplocks_enabled"] = oplocks_enabled
        if read_only is not None:
            self._values["read_only"] = read_only
        if requester_pays is not None:
            self._values["requester_pays"] = requester_pays
        if smb_acl_enabled is not None:
            self._values["smb_acl_enabled"] = smb_acl_enabled
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if timeouts is not None:
            self._values["timeouts"] = timeouts
        if valid_user_list is not None:
            self._values["valid_user_list"] = valid_user_list
        if vpc_endpoint_dns_name is not None:
            self._values["vpc_endpoint_dns_name"] = vpc_endpoint_dns_name

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
    def gateway_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#gateway_arn StoragegatewaySmbFileShare#gateway_arn}.'''
        result = self._values.get("gateway_arn")
        assert result is not None, "Required property 'gateway_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def location_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#location_arn StoragegatewaySmbFileShare#location_arn}.'''
        result = self._values.get("location_arn")
        assert result is not None, "Required property 'location_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#role_arn StoragegatewaySmbFileShare#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_based_enumeration(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#access_based_enumeration StoragegatewaySmbFileShare#access_based_enumeration}.'''
        result = self._values.get("access_based_enumeration")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def admin_user_list(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#admin_user_list StoragegatewaySmbFileShare#admin_user_list}.'''
        result = self._values.get("admin_user_list")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def audit_destination_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#audit_destination_arn StoragegatewaySmbFileShare#audit_destination_arn}.'''
        result = self._values.get("audit_destination_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def authentication(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#authentication StoragegatewaySmbFileShare#authentication}.'''
        result = self._values.get("authentication")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket_region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#bucket_region StoragegatewaySmbFileShare#bucket_region}.'''
        result = self._values.get("bucket_region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cache_attributes(
        self,
    ) -> typing.Optional[StoragegatewaySmbFileShareCacheAttributes]:
        '''cache_attributes block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#cache_attributes StoragegatewaySmbFileShare#cache_attributes}
        '''
        result = self._values.get("cache_attributes")
        return typing.cast(typing.Optional[StoragegatewaySmbFileShareCacheAttributes], result)

    @builtins.property
    def case_sensitivity(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#case_sensitivity StoragegatewaySmbFileShare#case_sensitivity}.'''
        result = self._values.get("case_sensitivity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_storage_class(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#default_storage_class StoragegatewaySmbFileShare#default_storage_class}.'''
        result = self._values.get("default_storage_class")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def file_share_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#file_share_name StoragegatewaySmbFileShare#file_share_name}.'''
        result = self._values.get("file_share_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def guess_mime_type_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#guess_mime_type_enabled StoragegatewaySmbFileShare#guess_mime_type_enabled}.'''
        result = self._values.get("guess_mime_type_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def invalid_user_list(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#invalid_user_list StoragegatewaySmbFileShare#invalid_user_list}.'''
        result = self._values.get("invalid_user_list")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def kms_encrypted(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#kms_encrypted StoragegatewaySmbFileShare#kms_encrypted}.'''
        result = self._values.get("kms_encrypted")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def kms_key_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#kms_key_arn StoragegatewaySmbFileShare#kms_key_arn}.'''
        result = self._values.get("kms_key_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def notification_policy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#notification_policy StoragegatewaySmbFileShare#notification_policy}.'''
        result = self._values.get("notification_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def object_acl(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#object_acl StoragegatewaySmbFileShare#object_acl}.'''
        result = self._values.get("object_acl")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oplocks_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#oplocks_enabled StoragegatewaySmbFileShare#oplocks_enabled}.'''
        result = self._values.get("oplocks_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def read_only(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#read_only StoragegatewaySmbFileShare#read_only}.'''
        result = self._values.get("read_only")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def requester_pays(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#requester_pays StoragegatewaySmbFileShare#requester_pays}.'''
        result = self._values.get("requester_pays")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def smb_acl_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#smb_acl_enabled StoragegatewaySmbFileShare#smb_acl_enabled}.'''
        result = self._values.get("smb_acl_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#tags StoragegatewaySmbFileShare#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#tags_all StoragegatewaySmbFileShare#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["StoragegatewaySmbFileShareTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#timeouts StoragegatewaySmbFileShare#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["StoragegatewaySmbFileShareTimeouts"], result)

    @builtins.property
    def valid_user_list(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#valid_user_list StoragegatewaySmbFileShare#valid_user_list}.'''
        result = self._values.get("valid_user_list")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def vpc_endpoint_dns_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#vpc_endpoint_dns_name StoragegatewaySmbFileShare#vpc_endpoint_dns_name}.'''
        result = self._values.get("vpc_endpoint_dns_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StoragegatewaySmbFileShareConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewaySmbFileShareTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class StoragegatewaySmbFileShareTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#create StoragegatewaySmbFileShare#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#delete StoragegatewaySmbFileShare#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#update StoragegatewaySmbFileShare#update}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#create StoragegatewaySmbFileShare#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#delete StoragegatewaySmbFileShare#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_smb_file_share#update StoragegatewaySmbFileShare#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StoragegatewaySmbFileShareTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StoragegatewaySmbFileShareTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewaySmbFileShareTimeoutsOutputReference",
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
    def internal_value(self) -> typing.Optional[StoragegatewaySmbFileShareTimeouts]:
        return typing.cast(typing.Optional[StoragegatewaySmbFileShareTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[StoragegatewaySmbFileShareTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


class StoragegatewayStoredIscsiVolume(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewayStoredIscsiVolume",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_stored_iscsi_volume aws_storagegateway_stored_iscsi_volume}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        disk_id: builtins.str,
        gateway_arn: builtins.str,
        network_interface_id: builtins.str,
        preserve_existing_data: typing.Union[builtins.bool, cdktf.IResolvable],
        target_name: builtins.str,
        kms_encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        kms_key: typing.Optional[builtins.str] = None,
        snapshot_id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_stored_iscsi_volume aws_storagegateway_stored_iscsi_volume} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param disk_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_stored_iscsi_volume#disk_id StoragegatewayStoredIscsiVolume#disk_id}.
        :param gateway_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_stored_iscsi_volume#gateway_arn StoragegatewayStoredIscsiVolume#gateway_arn}.
        :param network_interface_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_stored_iscsi_volume#network_interface_id StoragegatewayStoredIscsiVolume#network_interface_id}.
        :param preserve_existing_data: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_stored_iscsi_volume#preserve_existing_data StoragegatewayStoredIscsiVolume#preserve_existing_data}.
        :param target_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_stored_iscsi_volume#target_name StoragegatewayStoredIscsiVolume#target_name}.
        :param kms_encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_stored_iscsi_volume#kms_encrypted StoragegatewayStoredIscsiVolume#kms_encrypted}.
        :param kms_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_stored_iscsi_volume#kms_key StoragegatewayStoredIscsiVolume#kms_key}.
        :param snapshot_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_stored_iscsi_volume#snapshot_id StoragegatewayStoredIscsiVolume#snapshot_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_stored_iscsi_volume#tags StoragegatewayStoredIscsiVolume#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_stored_iscsi_volume#tags_all StoragegatewayStoredIscsiVolume#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = StoragegatewayStoredIscsiVolumeConfig(
            disk_id=disk_id,
            gateway_arn=gateway_arn,
            network_interface_id=network_interface_id,
            preserve_existing_data=preserve_existing_data,
            target_name=target_name,
            kms_encrypted=kms_encrypted,
            kms_key=kms_key,
            snapshot_id=snapshot_id,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetKmsEncrypted")
    def reset_kms_encrypted(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsEncrypted", []))

    @jsii.member(jsii_name="resetKmsKey")
    def reset_kms_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKey", []))

    @jsii.member(jsii_name="resetSnapshotId")
    def reset_snapshot_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnapshotId", []))

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
    @jsii.member(jsii_name="chapEnabled")
    def chap_enabled(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "chapEnabled"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lunNumber")
    def lun_number(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lunNumber"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkInterfacePort")
    def network_interface_port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "networkInterfacePort"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetArn")
    def target_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeAttachmentStatus")
    def volume_attachment_status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "volumeAttachmentStatus"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeId")
    def volume_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "volumeId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeSizeInBytes")
    def volume_size_in_bytes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "volumeSizeInBytes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeStatus")
    def volume_status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "volumeStatus"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumeType")
    def volume_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "volumeType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="diskIdInput")
    def disk_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "diskIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gatewayArnInput")
    def gateway_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gatewayArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsEncryptedInput")
    def kms_encrypted_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "kmsEncryptedInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyInput")
    def kms_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkInterfaceIdInput")
    def network_interface_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkInterfaceIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preserveExistingDataInput")
    def preserve_existing_data_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "preserveExistingDataInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotIdInput")
    def snapshot_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snapshotIdInput"))

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
    @jsii.member(jsii_name="targetNameInput")
    def target_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="diskId")
    def disk_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "diskId"))

    @disk_id.setter
    def disk_id(self, value: builtins.str) -> None:
        jsii.set(self, "diskId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gatewayArn")
    def gateway_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gatewayArn"))

    @gateway_arn.setter
    def gateway_arn(self, value: builtins.str) -> None:
        jsii.set(self, "gatewayArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsEncrypted")
    def kms_encrypted(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "kmsEncrypted"))

    @kms_encrypted.setter
    def kms_encrypted(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "kmsEncrypted", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKey")
    def kms_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKey"))

    @kms_key.setter
    def kms_key(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkInterfaceId")
    def network_interface_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkInterfaceId"))

    @network_interface_id.setter
    def network_interface_id(self, value: builtins.str) -> None:
        jsii.set(self, "networkInterfaceId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preserveExistingData")
    def preserve_existing_data(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "preserveExistingData"))

    @preserve_existing_data.setter
    def preserve_existing_data(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "preserveExistingData", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotId")
    def snapshot_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snapshotId"))

    @snapshot_id.setter
    def snapshot_id(self, value: builtins.str) -> None:
        jsii.set(self, "snapshotId", value)

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
    @jsii.member(jsii_name="targetName")
    def target_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetName"))

    @target_name.setter
    def target_name(self, value: builtins.str) -> None:
        jsii.set(self, "targetName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewayStoredIscsiVolumeConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "disk_id": "diskId",
        "gateway_arn": "gatewayArn",
        "network_interface_id": "networkInterfaceId",
        "preserve_existing_data": "preserveExistingData",
        "target_name": "targetName",
        "kms_encrypted": "kmsEncrypted",
        "kms_key": "kmsKey",
        "snapshot_id": "snapshotId",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class StoragegatewayStoredIscsiVolumeConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        disk_id: builtins.str,
        gateway_arn: builtins.str,
        network_interface_id: builtins.str,
        preserve_existing_data: typing.Union[builtins.bool, cdktf.IResolvable],
        target_name: builtins.str,
        kms_encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        kms_key: typing.Optional[builtins.str] = None,
        snapshot_id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Storage Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param disk_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_stored_iscsi_volume#disk_id StoragegatewayStoredIscsiVolume#disk_id}.
        :param gateway_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_stored_iscsi_volume#gateway_arn StoragegatewayStoredIscsiVolume#gateway_arn}.
        :param network_interface_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_stored_iscsi_volume#network_interface_id StoragegatewayStoredIscsiVolume#network_interface_id}.
        :param preserve_existing_data: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_stored_iscsi_volume#preserve_existing_data StoragegatewayStoredIscsiVolume#preserve_existing_data}.
        :param target_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_stored_iscsi_volume#target_name StoragegatewayStoredIscsiVolume#target_name}.
        :param kms_encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_stored_iscsi_volume#kms_encrypted StoragegatewayStoredIscsiVolume#kms_encrypted}.
        :param kms_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_stored_iscsi_volume#kms_key StoragegatewayStoredIscsiVolume#kms_key}.
        :param snapshot_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_stored_iscsi_volume#snapshot_id StoragegatewayStoredIscsiVolume#snapshot_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_stored_iscsi_volume#tags StoragegatewayStoredIscsiVolume#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_stored_iscsi_volume#tags_all StoragegatewayStoredIscsiVolume#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "disk_id": disk_id,
            "gateway_arn": gateway_arn,
            "network_interface_id": network_interface_id,
            "preserve_existing_data": preserve_existing_data,
            "target_name": target_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if kms_encrypted is not None:
            self._values["kms_encrypted"] = kms_encrypted
        if kms_key is not None:
            self._values["kms_key"] = kms_key
        if snapshot_id is not None:
            self._values["snapshot_id"] = snapshot_id
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
    def disk_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_stored_iscsi_volume#disk_id StoragegatewayStoredIscsiVolume#disk_id}.'''
        result = self._values.get("disk_id")
        assert result is not None, "Required property 'disk_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def gateway_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_stored_iscsi_volume#gateway_arn StoragegatewayStoredIscsiVolume#gateway_arn}.'''
        result = self._values.get("gateway_arn")
        assert result is not None, "Required property 'gateway_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def network_interface_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_stored_iscsi_volume#network_interface_id StoragegatewayStoredIscsiVolume#network_interface_id}.'''
        result = self._values.get("network_interface_id")
        assert result is not None, "Required property 'network_interface_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def preserve_existing_data(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_stored_iscsi_volume#preserve_existing_data StoragegatewayStoredIscsiVolume#preserve_existing_data}.'''
        result = self._values.get("preserve_existing_data")
        assert result is not None, "Required property 'preserve_existing_data' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def target_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_stored_iscsi_volume#target_name StoragegatewayStoredIscsiVolume#target_name}.'''
        result = self._values.get("target_name")
        assert result is not None, "Required property 'target_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def kms_encrypted(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_stored_iscsi_volume#kms_encrypted StoragegatewayStoredIscsiVolume#kms_encrypted}.'''
        result = self._values.get("kms_encrypted")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def kms_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_stored_iscsi_volume#kms_key StoragegatewayStoredIscsiVolume#kms_key}.'''
        result = self._values.get("kms_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def snapshot_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_stored_iscsi_volume#snapshot_id StoragegatewayStoredIscsiVolume#snapshot_id}.'''
        result = self._values.get("snapshot_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_stored_iscsi_volume#tags StoragegatewayStoredIscsiVolume#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_stored_iscsi_volume#tags_all StoragegatewayStoredIscsiVolume#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StoragegatewayStoredIscsiVolumeConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StoragegatewayTapePool(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewayTapePool",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_tape_pool aws_storagegateway_tape_pool}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        pool_name: builtins.str,
        storage_class: builtins.str,
        retention_lock_time_in_days: typing.Optional[jsii.Number] = None,
        retention_lock_type: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_tape_pool aws_storagegateway_tape_pool} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param pool_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_tape_pool#pool_name StoragegatewayTapePool#pool_name}.
        :param storage_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_tape_pool#storage_class StoragegatewayTapePool#storage_class}.
        :param retention_lock_time_in_days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_tape_pool#retention_lock_time_in_days StoragegatewayTapePool#retention_lock_time_in_days}.
        :param retention_lock_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_tape_pool#retention_lock_type StoragegatewayTapePool#retention_lock_type}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_tape_pool#tags StoragegatewayTapePool#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_tape_pool#tags_all StoragegatewayTapePool#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = StoragegatewayTapePoolConfig(
            pool_name=pool_name,
            storage_class=storage_class,
            retention_lock_time_in_days=retention_lock_time_in_days,
            retention_lock_type=retention_lock_type,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetRetentionLockTimeInDays")
    def reset_retention_lock_time_in_days(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetentionLockTimeInDays", []))

    @jsii.member(jsii_name="resetRetentionLockType")
    def reset_retention_lock_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetentionLockType", []))

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
    @jsii.member(jsii_name="poolNameInput")
    def pool_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "poolNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retentionLockTimeInDaysInput")
    def retention_lock_time_in_days_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retentionLockTimeInDaysInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retentionLockTypeInput")
    def retention_lock_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "retentionLockTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageClassInput")
    def storage_class_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageClassInput"))

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
    @jsii.member(jsii_name="poolName")
    def pool_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "poolName"))

    @pool_name.setter
    def pool_name(self, value: builtins.str) -> None:
        jsii.set(self, "poolName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retentionLockTimeInDays")
    def retention_lock_time_in_days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retentionLockTimeInDays"))

    @retention_lock_time_in_days.setter
    def retention_lock_time_in_days(self, value: jsii.Number) -> None:
        jsii.set(self, "retentionLockTimeInDays", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retentionLockType")
    def retention_lock_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "retentionLockType"))

    @retention_lock_type.setter
    def retention_lock_type(self, value: builtins.str) -> None:
        jsii.set(self, "retentionLockType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageClass")
    def storage_class(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageClass"))

    @storage_class.setter
    def storage_class(self, value: builtins.str) -> None:
        jsii.set(self, "storageClass", value)

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
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewayTapePoolConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "pool_name": "poolName",
        "storage_class": "storageClass",
        "retention_lock_time_in_days": "retentionLockTimeInDays",
        "retention_lock_type": "retentionLockType",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class StoragegatewayTapePoolConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        pool_name: builtins.str,
        storage_class: builtins.str,
        retention_lock_time_in_days: typing.Optional[jsii.Number] = None,
        retention_lock_type: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Storage Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param pool_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_tape_pool#pool_name StoragegatewayTapePool#pool_name}.
        :param storage_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_tape_pool#storage_class StoragegatewayTapePool#storage_class}.
        :param retention_lock_time_in_days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_tape_pool#retention_lock_time_in_days StoragegatewayTapePool#retention_lock_time_in_days}.
        :param retention_lock_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_tape_pool#retention_lock_type StoragegatewayTapePool#retention_lock_type}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_tape_pool#tags StoragegatewayTapePool#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_tape_pool#tags_all StoragegatewayTapePool#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "pool_name": pool_name,
            "storage_class": storage_class,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if retention_lock_time_in_days is not None:
            self._values["retention_lock_time_in_days"] = retention_lock_time_in_days
        if retention_lock_type is not None:
            self._values["retention_lock_type"] = retention_lock_type
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
    def pool_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_tape_pool#pool_name StoragegatewayTapePool#pool_name}.'''
        result = self._values.get("pool_name")
        assert result is not None, "Required property 'pool_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def storage_class(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_tape_pool#storage_class StoragegatewayTapePool#storage_class}.'''
        result = self._values.get("storage_class")
        assert result is not None, "Required property 'storage_class' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def retention_lock_time_in_days(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_tape_pool#retention_lock_time_in_days StoragegatewayTapePool#retention_lock_time_in_days}.'''
        result = self._values.get("retention_lock_time_in_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def retention_lock_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_tape_pool#retention_lock_type StoragegatewayTapePool#retention_lock_type}.'''
        result = self._values.get("retention_lock_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_tape_pool#tags StoragegatewayTapePool#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_tape_pool#tags_all StoragegatewayTapePool#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StoragegatewayTapePoolConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StoragegatewayUploadBuffer(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewayUploadBuffer",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_upload_buffer aws_storagegateway_upload_buffer}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        gateway_arn: builtins.str,
        disk_id: typing.Optional[builtins.str] = None,
        disk_path: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_upload_buffer aws_storagegateway_upload_buffer} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param gateway_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_upload_buffer#gateway_arn StoragegatewayUploadBuffer#gateway_arn}.
        :param disk_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_upload_buffer#disk_id StoragegatewayUploadBuffer#disk_id}.
        :param disk_path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_upload_buffer#disk_path StoragegatewayUploadBuffer#disk_path}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = StoragegatewayUploadBufferConfig(
            gateway_arn=gateway_arn,
            disk_id=disk_id,
            disk_path=disk_path,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDiskId")
    def reset_disk_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiskId", []))

    @jsii.member(jsii_name="resetDiskPath")
    def reset_disk_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiskPath", []))

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
    @jsii.member(jsii_name="diskIdInput")
    def disk_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "diskIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="diskPathInput")
    def disk_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "diskPathInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gatewayArnInput")
    def gateway_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gatewayArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="diskId")
    def disk_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "diskId"))

    @disk_id.setter
    def disk_id(self, value: builtins.str) -> None:
        jsii.set(self, "diskId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="diskPath")
    def disk_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "diskPath"))

    @disk_path.setter
    def disk_path(self, value: builtins.str) -> None:
        jsii.set(self, "diskPath", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gatewayArn")
    def gateway_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gatewayArn"))

    @gateway_arn.setter
    def gateway_arn(self, value: builtins.str) -> None:
        jsii.set(self, "gatewayArn", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewayUploadBufferConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "gateway_arn": "gatewayArn",
        "disk_id": "diskId",
        "disk_path": "diskPath",
    },
)
class StoragegatewayUploadBufferConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        gateway_arn: builtins.str,
        disk_id: typing.Optional[builtins.str] = None,
        disk_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Storage Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param gateway_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_upload_buffer#gateway_arn StoragegatewayUploadBuffer#gateway_arn}.
        :param disk_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_upload_buffer#disk_id StoragegatewayUploadBuffer#disk_id}.
        :param disk_path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_upload_buffer#disk_path StoragegatewayUploadBuffer#disk_path}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "gateway_arn": gateway_arn,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if disk_id is not None:
            self._values["disk_id"] = disk_id
        if disk_path is not None:
            self._values["disk_path"] = disk_path

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
    def gateway_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_upload_buffer#gateway_arn StoragegatewayUploadBuffer#gateway_arn}.'''
        result = self._values.get("gateway_arn")
        assert result is not None, "Required property 'gateway_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def disk_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_upload_buffer#disk_id StoragegatewayUploadBuffer#disk_id}.'''
        result = self._values.get("disk_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disk_path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_upload_buffer#disk_path StoragegatewayUploadBuffer#disk_path}.'''
        result = self._values.get("disk_path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StoragegatewayUploadBufferConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StoragegatewayWorkingStorage(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewayWorkingStorage",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_working_storage aws_storagegateway_working_storage}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        disk_id: builtins.str,
        gateway_arn: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_working_storage aws_storagegateway_working_storage} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param disk_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_working_storage#disk_id StoragegatewayWorkingStorage#disk_id}.
        :param gateway_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_working_storage#gateway_arn StoragegatewayWorkingStorage#gateway_arn}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = StoragegatewayWorkingStorageConfig(
            disk_id=disk_id,
            gateway_arn=gateway_arn,
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
    @jsii.member(jsii_name="diskIdInput")
    def disk_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "diskIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gatewayArnInput")
    def gateway_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gatewayArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="diskId")
    def disk_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "diskId"))

    @disk_id.setter
    def disk_id(self, value: builtins.str) -> None:
        jsii.set(self, "diskId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gatewayArn")
    def gateway_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gatewayArn"))

    @gateway_arn.setter
    def gateway_arn(self, value: builtins.str) -> None:
        jsii.set(self, "gatewayArn", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.storagegateway.StoragegatewayWorkingStorageConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "disk_id": "diskId",
        "gateway_arn": "gatewayArn",
    },
)
class StoragegatewayWorkingStorageConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        disk_id: builtins.str,
        gateway_arn: builtins.str,
    ) -> None:
        '''AWS Storage Gateway.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param disk_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_working_storage#disk_id StoragegatewayWorkingStorage#disk_id}.
        :param gateway_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_working_storage#gateway_arn StoragegatewayWorkingStorage#gateway_arn}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "disk_id": disk_id,
            "gateway_arn": gateway_arn,
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
    def disk_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_working_storage#disk_id StoragegatewayWorkingStorage#disk_id}.'''
        result = self._values.get("disk_id")
        assert result is not None, "Required property 'disk_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def gateway_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/storagegateway_working_storage#gateway_arn StoragegatewayWorkingStorage#gateway_arn}.'''
        result = self._values.get("gateway_arn")
        assert result is not None, "Required property 'gateway_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StoragegatewayWorkingStorageConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataAwsStoragegatewayLocalDisk",
    "DataAwsStoragegatewayLocalDiskConfig",
    "StoragegatewayCache",
    "StoragegatewayCacheConfig",
    "StoragegatewayCachedIscsiVolume",
    "StoragegatewayCachedIscsiVolumeConfig",
    "StoragegatewayFileSystemAssociation",
    "StoragegatewayFileSystemAssociationCacheAttributes",
    "StoragegatewayFileSystemAssociationCacheAttributesOutputReference",
    "StoragegatewayFileSystemAssociationConfig",
    "StoragegatewayGateway",
    "StoragegatewayGatewayConfig",
    "StoragegatewayGatewayGatewayNetworkInterface",
    "StoragegatewayGatewaySmbActiveDirectorySettings",
    "StoragegatewayGatewaySmbActiveDirectorySettingsOutputReference",
    "StoragegatewayGatewayTimeouts",
    "StoragegatewayGatewayTimeoutsOutputReference",
    "StoragegatewayNfsFileShare",
    "StoragegatewayNfsFileShareCacheAttributes",
    "StoragegatewayNfsFileShareCacheAttributesOutputReference",
    "StoragegatewayNfsFileShareConfig",
    "StoragegatewayNfsFileShareNfsFileShareDefaults",
    "StoragegatewayNfsFileShareNfsFileShareDefaultsOutputReference",
    "StoragegatewayNfsFileShareTimeouts",
    "StoragegatewayNfsFileShareTimeoutsOutputReference",
    "StoragegatewaySmbFileShare",
    "StoragegatewaySmbFileShareCacheAttributes",
    "StoragegatewaySmbFileShareCacheAttributesOutputReference",
    "StoragegatewaySmbFileShareConfig",
    "StoragegatewaySmbFileShareTimeouts",
    "StoragegatewaySmbFileShareTimeoutsOutputReference",
    "StoragegatewayStoredIscsiVolume",
    "StoragegatewayStoredIscsiVolumeConfig",
    "StoragegatewayTapePool",
    "StoragegatewayTapePoolConfig",
    "StoragegatewayUploadBuffer",
    "StoragegatewayUploadBufferConfig",
    "StoragegatewayWorkingStorage",
    "StoragegatewayWorkingStorageConfig",
]

publication.publish()
