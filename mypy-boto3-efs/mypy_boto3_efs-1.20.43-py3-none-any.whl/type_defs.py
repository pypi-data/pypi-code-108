"""
Type annotations for efs service type definitions.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_efs/type_defs.html)

Usage::

    ```python
    from mypy_boto3_efs.type_defs import AccessPointDescriptionResponseMetadataTypeDef

    data: AccessPointDescriptionResponseMetadataTypeDef = {...}
    ```
"""
import sys
from datetime import datetime
from typing import Dict, List, Sequence

from .literals import (
    LifeCycleStateType,
    PerformanceModeType,
    ReplicationStatusType,
    ResourceIdTypeType,
    ResourceType,
    StatusType,
    ThroughputModeType,
    TransitionToIARulesType,
)

if sys.version_info >= (3, 9):
    from typing import Literal
else:
    from typing_extensions import Literal
if sys.version_info >= (3, 9):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


__all__ = (
    "AccessPointDescriptionResponseMetadataTypeDef",
    "AccessPointDescriptionTypeDef",
    "BackupPolicyDescriptionTypeDef",
    "BackupPolicyTypeDef",
    "CreateAccessPointRequestRequestTypeDef",
    "CreateFileSystemRequestRequestTypeDef",
    "CreateMountTargetRequestRequestTypeDef",
    "CreateReplicationConfigurationRequestRequestTypeDef",
    "CreateTagsRequestRequestTypeDef",
    "CreationInfoTypeDef",
    "DeleteAccessPointRequestRequestTypeDef",
    "DeleteFileSystemPolicyRequestRequestTypeDef",
    "DeleteFileSystemRequestRequestTypeDef",
    "DeleteMountTargetRequestRequestTypeDef",
    "DeleteReplicationConfigurationRequestRequestTypeDef",
    "DeleteTagsRequestRequestTypeDef",
    "DescribeAccessPointsRequestRequestTypeDef",
    "DescribeAccessPointsResponseTypeDef",
    "DescribeAccountPreferencesRequestRequestTypeDef",
    "DescribeAccountPreferencesResponseTypeDef",
    "DescribeBackupPolicyRequestRequestTypeDef",
    "DescribeFileSystemPolicyRequestRequestTypeDef",
    "DescribeFileSystemsRequestRequestTypeDef",
    "DescribeFileSystemsResponseTypeDef",
    "DescribeLifecycleConfigurationRequestRequestTypeDef",
    "DescribeMountTargetSecurityGroupsRequestRequestTypeDef",
    "DescribeMountTargetSecurityGroupsResponseTypeDef",
    "DescribeMountTargetsRequestRequestTypeDef",
    "DescribeMountTargetsResponseTypeDef",
    "DescribeReplicationConfigurationsRequestRequestTypeDef",
    "DescribeReplicationConfigurationsResponseTypeDef",
    "DescribeTagsRequestRequestTypeDef",
    "DescribeTagsResponseTypeDef",
    "DestinationToCreateTypeDef",
    "DestinationTypeDef",
    "FileSystemDescriptionResponseMetadataTypeDef",
    "FileSystemDescriptionTypeDef",
    "FileSystemPolicyDescriptionTypeDef",
    "FileSystemSizeTypeDef",
    "LifecycleConfigurationDescriptionTypeDef",
    "LifecyclePolicyTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "ModifyMountTargetSecurityGroupsRequestRequestTypeDef",
    "MountTargetDescriptionResponseMetadataTypeDef",
    "MountTargetDescriptionTypeDef",
    "PaginatorConfigTypeDef",
    "PosixUserTypeDef",
    "PutAccountPreferencesRequestRequestTypeDef",
    "PutAccountPreferencesResponseTypeDef",
    "PutBackupPolicyRequestRequestTypeDef",
    "PutFileSystemPolicyRequestRequestTypeDef",
    "PutLifecycleConfigurationRequestRequestTypeDef",
    "ReplicationConfigurationDescriptionResponseMetadataTypeDef",
    "ReplicationConfigurationDescriptionTypeDef",
    "ResourceIdPreferenceTypeDef",
    "ResponseMetadataTypeDef",
    "RootDirectoryTypeDef",
    "TagResourceRequestRequestTypeDef",
    "TagTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdateFileSystemRequestRequestTypeDef",
)

AccessPointDescriptionResponseMetadataTypeDef = TypedDict(
    "AccessPointDescriptionResponseMetadataTypeDef",
    {
        "ClientToken": str,
        "Name": str,
        "Tags": List["TagTypeDef"],
        "AccessPointId": str,
        "AccessPointArn": str,
        "FileSystemId": str,
        "PosixUser": "PosixUserTypeDef",
        "RootDirectory": "RootDirectoryTypeDef",
        "OwnerId": str,
        "LifeCycleState": LifeCycleStateType,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

AccessPointDescriptionTypeDef = TypedDict(
    "AccessPointDescriptionTypeDef",
    {
        "ClientToken": str,
        "Name": str,
        "Tags": List["TagTypeDef"],
        "AccessPointId": str,
        "AccessPointArn": str,
        "FileSystemId": str,
        "PosixUser": "PosixUserTypeDef",
        "RootDirectory": "RootDirectoryTypeDef",
        "OwnerId": str,
        "LifeCycleState": LifeCycleStateType,
    },
    total=False,
)

BackupPolicyDescriptionTypeDef = TypedDict(
    "BackupPolicyDescriptionTypeDef",
    {
        "BackupPolicy": "BackupPolicyTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

BackupPolicyTypeDef = TypedDict(
    "BackupPolicyTypeDef",
    {
        "Status": StatusType,
    },
)

_RequiredCreateAccessPointRequestRequestTypeDef = TypedDict(
    "_RequiredCreateAccessPointRequestRequestTypeDef",
    {
        "ClientToken": str,
        "FileSystemId": str,
    },
)
_OptionalCreateAccessPointRequestRequestTypeDef = TypedDict(
    "_OptionalCreateAccessPointRequestRequestTypeDef",
    {
        "Tags": Sequence["TagTypeDef"],
        "PosixUser": "PosixUserTypeDef",
        "RootDirectory": "RootDirectoryTypeDef",
    },
    total=False,
)


class CreateAccessPointRequestRequestTypeDef(
    _RequiredCreateAccessPointRequestRequestTypeDef, _OptionalCreateAccessPointRequestRequestTypeDef
):
    pass


_RequiredCreateFileSystemRequestRequestTypeDef = TypedDict(
    "_RequiredCreateFileSystemRequestRequestTypeDef",
    {
        "CreationToken": str,
    },
)
_OptionalCreateFileSystemRequestRequestTypeDef = TypedDict(
    "_OptionalCreateFileSystemRequestRequestTypeDef",
    {
        "PerformanceMode": PerformanceModeType,
        "Encrypted": bool,
        "KmsKeyId": str,
        "ThroughputMode": ThroughputModeType,
        "ProvisionedThroughputInMibps": float,
        "AvailabilityZoneName": str,
        "Backup": bool,
        "Tags": Sequence["TagTypeDef"],
    },
    total=False,
)


class CreateFileSystemRequestRequestTypeDef(
    _RequiredCreateFileSystemRequestRequestTypeDef, _OptionalCreateFileSystemRequestRequestTypeDef
):
    pass


_RequiredCreateMountTargetRequestRequestTypeDef = TypedDict(
    "_RequiredCreateMountTargetRequestRequestTypeDef",
    {
        "FileSystemId": str,
        "SubnetId": str,
    },
)
_OptionalCreateMountTargetRequestRequestTypeDef = TypedDict(
    "_OptionalCreateMountTargetRequestRequestTypeDef",
    {
        "IpAddress": str,
        "SecurityGroups": Sequence[str],
    },
    total=False,
)


class CreateMountTargetRequestRequestTypeDef(
    _RequiredCreateMountTargetRequestRequestTypeDef, _OptionalCreateMountTargetRequestRequestTypeDef
):
    pass


CreateReplicationConfigurationRequestRequestTypeDef = TypedDict(
    "CreateReplicationConfigurationRequestRequestTypeDef",
    {
        "SourceFileSystemId": str,
        "Destinations": Sequence["DestinationToCreateTypeDef"],
    },
)

CreateTagsRequestRequestTypeDef = TypedDict(
    "CreateTagsRequestRequestTypeDef",
    {
        "FileSystemId": str,
        "Tags": Sequence["TagTypeDef"],
    },
)

CreationInfoTypeDef = TypedDict(
    "CreationInfoTypeDef",
    {
        "OwnerUid": int,
        "OwnerGid": int,
        "Permissions": str,
    },
)

DeleteAccessPointRequestRequestTypeDef = TypedDict(
    "DeleteAccessPointRequestRequestTypeDef",
    {
        "AccessPointId": str,
    },
)

DeleteFileSystemPolicyRequestRequestTypeDef = TypedDict(
    "DeleteFileSystemPolicyRequestRequestTypeDef",
    {
        "FileSystemId": str,
    },
)

DeleteFileSystemRequestRequestTypeDef = TypedDict(
    "DeleteFileSystemRequestRequestTypeDef",
    {
        "FileSystemId": str,
    },
)

DeleteMountTargetRequestRequestTypeDef = TypedDict(
    "DeleteMountTargetRequestRequestTypeDef",
    {
        "MountTargetId": str,
    },
)

DeleteReplicationConfigurationRequestRequestTypeDef = TypedDict(
    "DeleteReplicationConfigurationRequestRequestTypeDef",
    {
        "SourceFileSystemId": str,
    },
)

DeleteTagsRequestRequestTypeDef = TypedDict(
    "DeleteTagsRequestRequestTypeDef",
    {
        "FileSystemId": str,
        "TagKeys": Sequence[str],
    },
)

DescribeAccessPointsRequestRequestTypeDef = TypedDict(
    "DescribeAccessPointsRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
        "AccessPointId": str,
        "FileSystemId": str,
    },
    total=False,
)

DescribeAccessPointsResponseTypeDef = TypedDict(
    "DescribeAccessPointsResponseTypeDef",
    {
        "AccessPoints": List["AccessPointDescriptionTypeDef"],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeAccountPreferencesRequestRequestTypeDef = TypedDict(
    "DescribeAccountPreferencesRequestRequestTypeDef",
    {
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

DescribeAccountPreferencesResponseTypeDef = TypedDict(
    "DescribeAccountPreferencesResponseTypeDef",
    {
        "ResourceIdPreference": "ResourceIdPreferenceTypeDef",
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeBackupPolicyRequestRequestTypeDef = TypedDict(
    "DescribeBackupPolicyRequestRequestTypeDef",
    {
        "FileSystemId": str,
    },
)

DescribeFileSystemPolicyRequestRequestTypeDef = TypedDict(
    "DescribeFileSystemPolicyRequestRequestTypeDef",
    {
        "FileSystemId": str,
    },
)

DescribeFileSystemsRequestRequestTypeDef = TypedDict(
    "DescribeFileSystemsRequestRequestTypeDef",
    {
        "MaxItems": int,
        "Marker": str,
        "CreationToken": str,
        "FileSystemId": str,
    },
    total=False,
)

DescribeFileSystemsResponseTypeDef = TypedDict(
    "DescribeFileSystemsResponseTypeDef",
    {
        "Marker": str,
        "FileSystems": List["FileSystemDescriptionTypeDef"],
        "NextMarker": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeLifecycleConfigurationRequestRequestTypeDef = TypedDict(
    "DescribeLifecycleConfigurationRequestRequestTypeDef",
    {
        "FileSystemId": str,
    },
)

DescribeMountTargetSecurityGroupsRequestRequestTypeDef = TypedDict(
    "DescribeMountTargetSecurityGroupsRequestRequestTypeDef",
    {
        "MountTargetId": str,
    },
)

DescribeMountTargetSecurityGroupsResponseTypeDef = TypedDict(
    "DescribeMountTargetSecurityGroupsResponseTypeDef",
    {
        "SecurityGroups": List[str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeMountTargetsRequestRequestTypeDef = TypedDict(
    "DescribeMountTargetsRequestRequestTypeDef",
    {
        "MaxItems": int,
        "Marker": str,
        "FileSystemId": str,
        "MountTargetId": str,
        "AccessPointId": str,
    },
    total=False,
)

DescribeMountTargetsResponseTypeDef = TypedDict(
    "DescribeMountTargetsResponseTypeDef",
    {
        "Marker": str,
        "MountTargets": List["MountTargetDescriptionTypeDef"],
        "NextMarker": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeReplicationConfigurationsRequestRequestTypeDef = TypedDict(
    "DescribeReplicationConfigurationsRequestRequestTypeDef",
    {
        "FileSystemId": str,
        "NextToken": str,
        "MaxResults": int,
    },
    total=False,
)

DescribeReplicationConfigurationsResponseTypeDef = TypedDict(
    "DescribeReplicationConfigurationsResponseTypeDef",
    {
        "Replications": List["ReplicationConfigurationDescriptionTypeDef"],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredDescribeTagsRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeTagsRequestRequestTypeDef",
    {
        "FileSystemId": str,
    },
)
_OptionalDescribeTagsRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeTagsRequestRequestTypeDef",
    {
        "MaxItems": int,
        "Marker": str,
    },
    total=False,
)


class DescribeTagsRequestRequestTypeDef(
    _RequiredDescribeTagsRequestRequestTypeDef, _OptionalDescribeTagsRequestRequestTypeDef
):
    pass


DescribeTagsResponseTypeDef = TypedDict(
    "DescribeTagsResponseTypeDef",
    {
        "Marker": str,
        "Tags": List["TagTypeDef"],
        "NextMarker": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DestinationToCreateTypeDef = TypedDict(
    "DestinationToCreateTypeDef",
    {
        "Region": str,
        "AvailabilityZoneName": str,
        "KmsKeyId": str,
    },
    total=False,
)

_RequiredDestinationTypeDef = TypedDict(
    "_RequiredDestinationTypeDef",
    {
        "Status": ReplicationStatusType,
        "FileSystemId": str,
        "Region": str,
    },
)
_OptionalDestinationTypeDef = TypedDict(
    "_OptionalDestinationTypeDef",
    {
        "LastReplicatedTimestamp": datetime,
    },
    total=False,
)


class DestinationTypeDef(_RequiredDestinationTypeDef, _OptionalDestinationTypeDef):
    pass


FileSystemDescriptionResponseMetadataTypeDef = TypedDict(
    "FileSystemDescriptionResponseMetadataTypeDef",
    {
        "OwnerId": str,
        "CreationToken": str,
        "FileSystemId": str,
        "FileSystemArn": str,
        "CreationTime": datetime,
        "LifeCycleState": LifeCycleStateType,
        "Name": str,
        "NumberOfMountTargets": int,
        "SizeInBytes": "FileSystemSizeTypeDef",
        "PerformanceMode": PerformanceModeType,
        "Encrypted": bool,
        "KmsKeyId": str,
        "ThroughputMode": ThroughputModeType,
        "ProvisionedThroughputInMibps": float,
        "AvailabilityZoneName": str,
        "AvailabilityZoneId": str,
        "Tags": List["TagTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredFileSystemDescriptionTypeDef = TypedDict(
    "_RequiredFileSystemDescriptionTypeDef",
    {
        "OwnerId": str,
        "CreationToken": str,
        "FileSystemId": str,
        "CreationTime": datetime,
        "LifeCycleState": LifeCycleStateType,
        "NumberOfMountTargets": int,
        "SizeInBytes": "FileSystemSizeTypeDef",
        "PerformanceMode": PerformanceModeType,
        "Tags": List["TagTypeDef"],
    },
)
_OptionalFileSystemDescriptionTypeDef = TypedDict(
    "_OptionalFileSystemDescriptionTypeDef",
    {
        "FileSystemArn": str,
        "Name": str,
        "Encrypted": bool,
        "KmsKeyId": str,
        "ThroughputMode": ThroughputModeType,
        "ProvisionedThroughputInMibps": float,
        "AvailabilityZoneName": str,
        "AvailabilityZoneId": str,
    },
    total=False,
)


class FileSystemDescriptionTypeDef(
    _RequiredFileSystemDescriptionTypeDef, _OptionalFileSystemDescriptionTypeDef
):
    pass


FileSystemPolicyDescriptionTypeDef = TypedDict(
    "FileSystemPolicyDescriptionTypeDef",
    {
        "FileSystemId": str,
        "Policy": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredFileSystemSizeTypeDef = TypedDict(
    "_RequiredFileSystemSizeTypeDef",
    {
        "Value": int,
    },
)
_OptionalFileSystemSizeTypeDef = TypedDict(
    "_OptionalFileSystemSizeTypeDef",
    {
        "Timestamp": datetime,
        "ValueInIA": int,
        "ValueInStandard": int,
    },
    total=False,
)


class FileSystemSizeTypeDef(_RequiredFileSystemSizeTypeDef, _OptionalFileSystemSizeTypeDef):
    pass


LifecycleConfigurationDescriptionTypeDef = TypedDict(
    "LifecycleConfigurationDescriptionTypeDef",
    {
        "LifecyclePolicies": List["LifecyclePolicyTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

LifecyclePolicyTypeDef = TypedDict(
    "LifecyclePolicyTypeDef",
    {
        "TransitionToIA": TransitionToIARulesType,
        "TransitionToPrimaryStorageClass": Literal["AFTER_1_ACCESS"],
    },
    total=False,
)

_RequiredListTagsForResourceRequestRequestTypeDef = TypedDict(
    "_RequiredListTagsForResourceRequestRequestTypeDef",
    {
        "ResourceId": str,
    },
)
_OptionalListTagsForResourceRequestRequestTypeDef = TypedDict(
    "_OptionalListTagsForResourceRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class ListTagsForResourceRequestRequestTypeDef(
    _RequiredListTagsForResourceRequestRequestTypeDef,
    _OptionalListTagsForResourceRequestRequestTypeDef,
):
    pass


ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "Tags": List["TagTypeDef"],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredModifyMountTargetSecurityGroupsRequestRequestTypeDef = TypedDict(
    "_RequiredModifyMountTargetSecurityGroupsRequestRequestTypeDef",
    {
        "MountTargetId": str,
    },
)
_OptionalModifyMountTargetSecurityGroupsRequestRequestTypeDef = TypedDict(
    "_OptionalModifyMountTargetSecurityGroupsRequestRequestTypeDef",
    {
        "SecurityGroups": Sequence[str],
    },
    total=False,
)


class ModifyMountTargetSecurityGroupsRequestRequestTypeDef(
    _RequiredModifyMountTargetSecurityGroupsRequestRequestTypeDef,
    _OptionalModifyMountTargetSecurityGroupsRequestRequestTypeDef,
):
    pass


MountTargetDescriptionResponseMetadataTypeDef = TypedDict(
    "MountTargetDescriptionResponseMetadataTypeDef",
    {
        "OwnerId": str,
        "MountTargetId": str,
        "FileSystemId": str,
        "SubnetId": str,
        "LifeCycleState": LifeCycleStateType,
        "IpAddress": str,
        "NetworkInterfaceId": str,
        "AvailabilityZoneId": str,
        "AvailabilityZoneName": str,
        "VpcId": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredMountTargetDescriptionTypeDef = TypedDict(
    "_RequiredMountTargetDescriptionTypeDef",
    {
        "MountTargetId": str,
        "FileSystemId": str,
        "SubnetId": str,
        "LifeCycleState": LifeCycleStateType,
    },
)
_OptionalMountTargetDescriptionTypeDef = TypedDict(
    "_OptionalMountTargetDescriptionTypeDef",
    {
        "OwnerId": str,
        "IpAddress": str,
        "NetworkInterfaceId": str,
        "AvailabilityZoneId": str,
        "AvailabilityZoneName": str,
        "VpcId": str,
    },
    total=False,
)


class MountTargetDescriptionTypeDef(
    _RequiredMountTargetDescriptionTypeDef, _OptionalMountTargetDescriptionTypeDef
):
    pass


PaginatorConfigTypeDef = TypedDict(
    "PaginatorConfigTypeDef",
    {
        "MaxItems": int,
        "PageSize": int,
        "StartingToken": str,
    },
    total=False,
)

_RequiredPosixUserTypeDef = TypedDict(
    "_RequiredPosixUserTypeDef",
    {
        "Uid": int,
        "Gid": int,
    },
)
_OptionalPosixUserTypeDef = TypedDict(
    "_OptionalPosixUserTypeDef",
    {
        "SecondaryGids": Sequence[int],
    },
    total=False,
)


class PosixUserTypeDef(_RequiredPosixUserTypeDef, _OptionalPosixUserTypeDef):
    pass


PutAccountPreferencesRequestRequestTypeDef = TypedDict(
    "PutAccountPreferencesRequestRequestTypeDef",
    {
        "ResourceIdType": ResourceIdTypeType,
    },
)

PutAccountPreferencesResponseTypeDef = TypedDict(
    "PutAccountPreferencesResponseTypeDef",
    {
        "ResourceIdPreference": "ResourceIdPreferenceTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

PutBackupPolicyRequestRequestTypeDef = TypedDict(
    "PutBackupPolicyRequestRequestTypeDef",
    {
        "FileSystemId": str,
        "BackupPolicy": "BackupPolicyTypeDef",
    },
)

_RequiredPutFileSystemPolicyRequestRequestTypeDef = TypedDict(
    "_RequiredPutFileSystemPolicyRequestRequestTypeDef",
    {
        "FileSystemId": str,
        "Policy": str,
    },
)
_OptionalPutFileSystemPolicyRequestRequestTypeDef = TypedDict(
    "_OptionalPutFileSystemPolicyRequestRequestTypeDef",
    {
        "BypassPolicyLockoutSafetyCheck": bool,
    },
    total=False,
)


class PutFileSystemPolicyRequestRequestTypeDef(
    _RequiredPutFileSystemPolicyRequestRequestTypeDef,
    _OptionalPutFileSystemPolicyRequestRequestTypeDef,
):
    pass


PutLifecycleConfigurationRequestRequestTypeDef = TypedDict(
    "PutLifecycleConfigurationRequestRequestTypeDef",
    {
        "FileSystemId": str,
        "LifecyclePolicies": Sequence["LifecyclePolicyTypeDef"],
    },
)

ReplicationConfigurationDescriptionResponseMetadataTypeDef = TypedDict(
    "ReplicationConfigurationDescriptionResponseMetadataTypeDef",
    {
        "SourceFileSystemId": str,
        "SourceFileSystemRegion": str,
        "SourceFileSystemArn": str,
        "OriginalSourceFileSystemArn": str,
        "CreationTime": datetime,
        "Destinations": List["DestinationTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ReplicationConfigurationDescriptionTypeDef = TypedDict(
    "ReplicationConfigurationDescriptionTypeDef",
    {
        "SourceFileSystemId": str,
        "SourceFileSystemRegion": str,
        "SourceFileSystemArn": str,
        "OriginalSourceFileSystemArn": str,
        "CreationTime": datetime,
        "Destinations": List["DestinationTypeDef"],
    },
)

ResourceIdPreferenceTypeDef = TypedDict(
    "ResourceIdPreferenceTypeDef",
    {
        "ResourceIdType": ResourceIdTypeType,
        "Resources": List[ResourceType],
    },
    total=False,
)

ResponseMetadataTypeDef = TypedDict(
    "ResponseMetadataTypeDef",
    {
        "RequestId": str,
        "HostId": str,
        "HTTPStatusCode": int,
        "HTTPHeaders": Dict[str, str],
        "RetryAttempts": int,
    },
)

RootDirectoryTypeDef = TypedDict(
    "RootDirectoryTypeDef",
    {
        "Path": str,
        "CreationInfo": "CreationInfoTypeDef",
    },
    total=False,
)

TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "ResourceId": str,
        "Tags": Sequence["TagTypeDef"],
    },
)

TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "Key": str,
        "Value": str,
    },
)

UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "ResourceId": str,
        "TagKeys": Sequence[str],
    },
)

_RequiredUpdateFileSystemRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateFileSystemRequestRequestTypeDef",
    {
        "FileSystemId": str,
    },
)
_OptionalUpdateFileSystemRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateFileSystemRequestRequestTypeDef",
    {
        "ThroughputMode": ThroughputModeType,
        "ProvisionedThroughputInMibps": float,
    },
    total=False,
)


class UpdateFileSystemRequestRequestTypeDef(
    _RequiredUpdateFileSystemRequestRequestTypeDef, _OptionalUpdateFileSystemRequestRequestTypeDef
):
    pass
