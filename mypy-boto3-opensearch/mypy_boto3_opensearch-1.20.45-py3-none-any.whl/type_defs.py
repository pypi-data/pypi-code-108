"""
Type annotations for opensearch service type definitions.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_opensearch/type_defs.html)

Usage::

    ```python
    from mypy_boto3_opensearch.type_defs import AWSDomainInformationTypeDef

    data: AWSDomainInformationTypeDef = {...}
    ```
"""
import sys
from datetime import datetime
from typing import Dict, List, Mapping, Sequence, Union

from .literals import (
    AutoTuneDesiredStateType,
    AutoTuneStateType,
    DeploymentStatusType,
    DescribePackagesFilterNameType,
    DomainPackageStatusType,
    EngineTypeType,
    InboundConnectionStatusCodeType,
    LogTypeType,
    OpenSearchPartitionInstanceTypeType,
    OpenSearchWarmPartitionInstanceTypeType,
    OptionStateType,
    OutboundConnectionStatusCodeType,
    OverallChangeStatusType,
    PackageStatusType,
    ReservedInstancePaymentOptionType,
    RollbackOnDisableType,
    ScheduledAutoTuneActionTypeType,
    ScheduledAutoTuneSeverityTypeType,
    TLSSecurityPolicyType,
    UpgradeStatusType,
    UpgradeStepType,
    VolumeTypeType,
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
    "AWSDomainInformationTypeDef",
    "AcceptInboundConnectionRequestRequestTypeDef",
    "AcceptInboundConnectionResponseTypeDef",
    "AccessPoliciesStatusTypeDef",
    "AddTagsRequestRequestTypeDef",
    "AdditionalLimitTypeDef",
    "AdvancedOptionsStatusTypeDef",
    "AdvancedSecurityOptionsInputTypeDef",
    "AdvancedSecurityOptionsStatusTypeDef",
    "AdvancedSecurityOptionsTypeDef",
    "AssociatePackageRequestRequestTypeDef",
    "AssociatePackageResponseTypeDef",
    "AutoTuneDetailsTypeDef",
    "AutoTuneMaintenanceScheduleTypeDef",
    "AutoTuneOptionsInputTypeDef",
    "AutoTuneOptionsOutputTypeDef",
    "AutoTuneOptionsStatusTypeDef",
    "AutoTuneOptionsTypeDef",
    "AutoTuneStatusTypeDef",
    "AutoTuneTypeDef",
    "CancelServiceSoftwareUpdateRequestRequestTypeDef",
    "CancelServiceSoftwareUpdateResponseTypeDef",
    "ChangeProgressDetailsTypeDef",
    "ChangeProgressStageTypeDef",
    "ChangeProgressStatusDetailsTypeDef",
    "ClusterConfigStatusTypeDef",
    "ClusterConfigTypeDef",
    "CognitoOptionsStatusTypeDef",
    "CognitoOptionsTypeDef",
    "ColdStorageOptionsTypeDef",
    "CompatibleVersionsMapTypeDef",
    "CreateDomainRequestRequestTypeDef",
    "CreateDomainResponseTypeDef",
    "CreateOutboundConnectionRequestRequestTypeDef",
    "CreateOutboundConnectionResponseTypeDef",
    "CreatePackageRequestRequestTypeDef",
    "CreatePackageResponseTypeDef",
    "DeleteDomainRequestRequestTypeDef",
    "DeleteDomainResponseTypeDef",
    "DeleteInboundConnectionRequestRequestTypeDef",
    "DeleteInboundConnectionResponseTypeDef",
    "DeleteOutboundConnectionRequestRequestTypeDef",
    "DeleteOutboundConnectionResponseTypeDef",
    "DeletePackageRequestRequestTypeDef",
    "DeletePackageResponseTypeDef",
    "DescribeDomainAutoTunesRequestRequestTypeDef",
    "DescribeDomainAutoTunesResponseTypeDef",
    "DescribeDomainChangeProgressRequestRequestTypeDef",
    "DescribeDomainChangeProgressResponseTypeDef",
    "DescribeDomainConfigRequestRequestTypeDef",
    "DescribeDomainConfigResponseTypeDef",
    "DescribeDomainRequestRequestTypeDef",
    "DescribeDomainResponseTypeDef",
    "DescribeDomainsRequestRequestTypeDef",
    "DescribeDomainsResponseTypeDef",
    "DescribeInboundConnectionsRequestRequestTypeDef",
    "DescribeInboundConnectionsResponseTypeDef",
    "DescribeInstanceTypeLimitsRequestRequestTypeDef",
    "DescribeInstanceTypeLimitsResponseTypeDef",
    "DescribeOutboundConnectionsRequestRequestTypeDef",
    "DescribeOutboundConnectionsResponseTypeDef",
    "DescribePackagesFilterTypeDef",
    "DescribePackagesRequestRequestTypeDef",
    "DescribePackagesResponseTypeDef",
    "DescribeReservedInstanceOfferingsRequestRequestTypeDef",
    "DescribeReservedInstanceOfferingsResponseTypeDef",
    "DescribeReservedInstancesRequestRequestTypeDef",
    "DescribeReservedInstancesResponseTypeDef",
    "DissociatePackageRequestRequestTypeDef",
    "DissociatePackageResponseTypeDef",
    "DomainConfigTypeDef",
    "DomainEndpointOptionsStatusTypeDef",
    "DomainEndpointOptionsTypeDef",
    "DomainInfoTypeDef",
    "DomainInformationContainerTypeDef",
    "DomainPackageDetailsTypeDef",
    "DomainStatusTypeDef",
    "DryRunResultsTypeDef",
    "DurationTypeDef",
    "EBSOptionsStatusTypeDef",
    "EBSOptionsTypeDef",
    "EncryptionAtRestOptionsStatusTypeDef",
    "EncryptionAtRestOptionsTypeDef",
    "ErrorDetailsTypeDef",
    "FilterTypeDef",
    "GetCompatibleVersionsRequestRequestTypeDef",
    "GetCompatibleVersionsResponseTypeDef",
    "GetPackageVersionHistoryRequestRequestTypeDef",
    "GetPackageVersionHistoryResponseTypeDef",
    "GetUpgradeHistoryRequestRequestTypeDef",
    "GetUpgradeHistoryResponseTypeDef",
    "GetUpgradeStatusRequestRequestTypeDef",
    "GetUpgradeStatusResponseTypeDef",
    "InboundConnectionStatusTypeDef",
    "InboundConnectionTypeDef",
    "InstanceCountLimitsTypeDef",
    "InstanceLimitsTypeDef",
    "InstanceTypeDetailsTypeDef",
    "LimitsTypeDef",
    "ListDomainNamesRequestRequestTypeDef",
    "ListDomainNamesResponseTypeDef",
    "ListDomainsForPackageRequestRequestTypeDef",
    "ListDomainsForPackageResponseTypeDef",
    "ListInstanceTypeDetailsRequestRequestTypeDef",
    "ListInstanceTypeDetailsResponseTypeDef",
    "ListPackagesForDomainRequestRequestTypeDef",
    "ListPackagesForDomainResponseTypeDef",
    "ListTagsRequestRequestTypeDef",
    "ListTagsResponseTypeDef",
    "ListVersionsRequestRequestTypeDef",
    "ListVersionsResponseTypeDef",
    "LogPublishingOptionTypeDef",
    "LogPublishingOptionsStatusTypeDef",
    "MasterUserOptionsTypeDef",
    "NodeToNodeEncryptionOptionsStatusTypeDef",
    "NodeToNodeEncryptionOptionsTypeDef",
    "OptionStatusTypeDef",
    "OutboundConnectionStatusTypeDef",
    "OutboundConnectionTypeDef",
    "PackageDetailsTypeDef",
    "PackageSourceTypeDef",
    "PackageVersionHistoryTypeDef",
    "PurchaseReservedInstanceOfferingRequestRequestTypeDef",
    "PurchaseReservedInstanceOfferingResponseTypeDef",
    "RecurringChargeTypeDef",
    "RejectInboundConnectionRequestRequestTypeDef",
    "RejectInboundConnectionResponseTypeDef",
    "RemoveTagsRequestRequestTypeDef",
    "ReservedInstanceOfferingTypeDef",
    "ReservedInstanceTypeDef",
    "ResponseMetadataTypeDef",
    "SAMLIdpTypeDef",
    "SAMLOptionsInputTypeDef",
    "SAMLOptionsOutputTypeDef",
    "ScheduledAutoTuneDetailsTypeDef",
    "ServiceSoftwareOptionsTypeDef",
    "SnapshotOptionsStatusTypeDef",
    "SnapshotOptionsTypeDef",
    "StartServiceSoftwareUpdateRequestRequestTypeDef",
    "StartServiceSoftwareUpdateResponseTypeDef",
    "StorageTypeLimitTypeDef",
    "StorageTypeTypeDef",
    "TagTypeDef",
    "UpdateDomainConfigRequestRequestTypeDef",
    "UpdateDomainConfigResponseTypeDef",
    "UpdatePackageRequestRequestTypeDef",
    "UpdatePackageResponseTypeDef",
    "UpgradeDomainRequestRequestTypeDef",
    "UpgradeDomainResponseTypeDef",
    "UpgradeHistoryTypeDef",
    "UpgradeStepItemTypeDef",
    "VPCDerivedInfoStatusTypeDef",
    "VPCDerivedInfoTypeDef",
    "VPCOptionsTypeDef",
    "VersionStatusTypeDef",
    "ZoneAwarenessConfigTypeDef",
)

_RequiredAWSDomainInformationTypeDef = TypedDict(
    "_RequiredAWSDomainInformationTypeDef",
    {
        "DomainName": str,
    },
)
_OptionalAWSDomainInformationTypeDef = TypedDict(
    "_OptionalAWSDomainInformationTypeDef",
    {
        "OwnerId": str,
        "Region": str,
    },
    total=False,
)


class AWSDomainInformationTypeDef(
    _RequiredAWSDomainInformationTypeDef, _OptionalAWSDomainInformationTypeDef
):
    pass


AcceptInboundConnectionRequestRequestTypeDef = TypedDict(
    "AcceptInboundConnectionRequestRequestTypeDef",
    {
        "ConnectionId": str,
    },
)

AcceptInboundConnectionResponseTypeDef = TypedDict(
    "AcceptInboundConnectionResponseTypeDef",
    {
        "Connection": "InboundConnectionTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

AccessPoliciesStatusTypeDef = TypedDict(
    "AccessPoliciesStatusTypeDef",
    {
        "Options": str,
        "Status": "OptionStatusTypeDef",
    },
)

AddTagsRequestRequestTypeDef = TypedDict(
    "AddTagsRequestRequestTypeDef",
    {
        "ARN": str,
        "TagList": Sequence["TagTypeDef"],
    },
)

AdditionalLimitTypeDef = TypedDict(
    "AdditionalLimitTypeDef",
    {
        "LimitName": str,
        "LimitValues": List[str],
    },
    total=False,
)

AdvancedOptionsStatusTypeDef = TypedDict(
    "AdvancedOptionsStatusTypeDef",
    {
        "Options": Dict[str, str],
        "Status": "OptionStatusTypeDef",
    },
)

AdvancedSecurityOptionsInputTypeDef = TypedDict(
    "AdvancedSecurityOptionsInputTypeDef",
    {
        "Enabled": bool,
        "InternalUserDatabaseEnabled": bool,
        "MasterUserOptions": "MasterUserOptionsTypeDef",
        "SAMLOptions": "SAMLOptionsInputTypeDef",
        "AnonymousAuthEnabled": bool,
    },
    total=False,
)

AdvancedSecurityOptionsStatusTypeDef = TypedDict(
    "AdvancedSecurityOptionsStatusTypeDef",
    {
        "Options": "AdvancedSecurityOptionsTypeDef",
        "Status": "OptionStatusTypeDef",
    },
)

AdvancedSecurityOptionsTypeDef = TypedDict(
    "AdvancedSecurityOptionsTypeDef",
    {
        "Enabled": bool,
        "InternalUserDatabaseEnabled": bool,
        "SAMLOptions": "SAMLOptionsOutputTypeDef",
        "AnonymousAuthDisableDate": datetime,
        "AnonymousAuthEnabled": bool,
    },
    total=False,
)

AssociatePackageRequestRequestTypeDef = TypedDict(
    "AssociatePackageRequestRequestTypeDef",
    {
        "PackageID": str,
        "DomainName": str,
    },
)

AssociatePackageResponseTypeDef = TypedDict(
    "AssociatePackageResponseTypeDef",
    {
        "DomainPackageDetails": "DomainPackageDetailsTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

AutoTuneDetailsTypeDef = TypedDict(
    "AutoTuneDetailsTypeDef",
    {
        "ScheduledAutoTuneDetails": "ScheduledAutoTuneDetailsTypeDef",
    },
    total=False,
)

AutoTuneMaintenanceScheduleTypeDef = TypedDict(
    "AutoTuneMaintenanceScheduleTypeDef",
    {
        "StartAt": Union[datetime, str],
        "Duration": "DurationTypeDef",
        "CronExpressionForRecurrence": str,
    },
    total=False,
)

AutoTuneOptionsInputTypeDef = TypedDict(
    "AutoTuneOptionsInputTypeDef",
    {
        "DesiredState": AutoTuneDesiredStateType,
        "MaintenanceSchedules": Sequence["AutoTuneMaintenanceScheduleTypeDef"],
    },
    total=False,
)

AutoTuneOptionsOutputTypeDef = TypedDict(
    "AutoTuneOptionsOutputTypeDef",
    {
        "State": AutoTuneStateType,
        "ErrorMessage": str,
    },
    total=False,
)

AutoTuneOptionsStatusTypeDef = TypedDict(
    "AutoTuneOptionsStatusTypeDef",
    {
        "Options": "AutoTuneOptionsTypeDef",
        "Status": "AutoTuneStatusTypeDef",
    },
    total=False,
)

AutoTuneOptionsTypeDef = TypedDict(
    "AutoTuneOptionsTypeDef",
    {
        "DesiredState": AutoTuneDesiredStateType,
        "RollbackOnDisable": RollbackOnDisableType,
        "MaintenanceSchedules": List["AutoTuneMaintenanceScheduleTypeDef"],
    },
    total=False,
)

_RequiredAutoTuneStatusTypeDef = TypedDict(
    "_RequiredAutoTuneStatusTypeDef",
    {
        "CreationDate": datetime,
        "UpdateDate": datetime,
        "State": AutoTuneStateType,
    },
)
_OptionalAutoTuneStatusTypeDef = TypedDict(
    "_OptionalAutoTuneStatusTypeDef",
    {
        "UpdateVersion": int,
        "ErrorMessage": str,
        "PendingDeletion": bool,
    },
    total=False,
)


class AutoTuneStatusTypeDef(_RequiredAutoTuneStatusTypeDef, _OptionalAutoTuneStatusTypeDef):
    pass


AutoTuneTypeDef = TypedDict(
    "AutoTuneTypeDef",
    {
        "AutoTuneType": Literal["SCHEDULED_ACTION"],
        "AutoTuneDetails": "AutoTuneDetailsTypeDef",
    },
    total=False,
)

CancelServiceSoftwareUpdateRequestRequestTypeDef = TypedDict(
    "CancelServiceSoftwareUpdateRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)

CancelServiceSoftwareUpdateResponseTypeDef = TypedDict(
    "CancelServiceSoftwareUpdateResponseTypeDef",
    {
        "ServiceSoftwareOptions": "ServiceSoftwareOptionsTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ChangeProgressDetailsTypeDef = TypedDict(
    "ChangeProgressDetailsTypeDef",
    {
        "ChangeId": str,
        "Message": str,
    },
    total=False,
)

ChangeProgressStageTypeDef = TypedDict(
    "ChangeProgressStageTypeDef",
    {
        "Name": str,
        "Status": str,
        "Description": str,
        "LastUpdated": datetime,
    },
    total=False,
)

ChangeProgressStatusDetailsTypeDef = TypedDict(
    "ChangeProgressStatusDetailsTypeDef",
    {
        "ChangeId": str,
        "StartTime": datetime,
        "Status": OverallChangeStatusType,
        "PendingProperties": List[str],
        "CompletedProperties": List[str],
        "TotalNumberOfStages": int,
        "ChangeProgressStages": List["ChangeProgressStageTypeDef"],
    },
    total=False,
)

ClusterConfigStatusTypeDef = TypedDict(
    "ClusterConfigStatusTypeDef",
    {
        "Options": "ClusterConfigTypeDef",
        "Status": "OptionStatusTypeDef",
    },
)

ClusterConfigTypeDef = TypedDict(
    "ClusterConfigTypeDef",
    {
        "InstanceType": OpenSearchPartitionInstanceTypeType,
        "InstanceCount": int,
        "DedicatedMasterEnabled": bool,
        "ZoneAwarenessEnabled": bool,
        "ZoneAwarenessConfig": "ZoneAwarenessConfigTypeDef",
        "DedicatedMasterType": OpenSearchPartitionInstanceTypeType,
        "DedicatedMasterCount": int,
        "WarmEnabled": bool,
        "WarmType": OpenSearchWarmPartitionInstanceTypeType,
        "WarmCount": int,
        "ColdStorageOptions": "ColdStorageOptionsTypeDef",
    },
    total=False,
)

CognitoOptionsStatusTypeDef = TypedDict(
    "CognitoOptionsStatusTypeDef",
    {
        "Options": "CognitoOptionsTypeDef",
        "Status": "OptionStatusTypeDef",
    },
)

CognitoOptionsTypeDef = TypedDict(
    "CognitoOptionsTypeDef",
    {
        "Enabled": bool,
        "UserPoolId": str,
        "IdentityPoolId": str,
        "RoleArn": str,
    },
    total=False,
)

ColdStorageOptionsTypeDef = TypedDict(
    "ColdStorageOptionsTypeDef",
    {
        "Enabled": bool,
    },
)

CompatibleVersionsMapTypeDef = TypedDict(
    "CompatibleVersionsMapTypeDef",
    {
        "SourceVersion": str,
        "TargetVersions": List[str],
    },
    total=False,
)

_RequiredCreateDomainRequestRequestTypeDef = TypedDict(
    "_RequiredCreateDomainRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)
_OptionalCreateDomainRequestRequestTypeDef = TypedDict(
    "_OptionalCreateDomainRequestRequestTypeDef",
    {
        "EngineVersion": str,
        "ClusterConfig": "ClusterConfigTypeDef",
        "EBSOptions": "EBSOptionsTypeDef",
        "AccessPolicies": str,
        "SnapshotOptions": "SnapshotOptionsTypeDef",
        "VPCOptions": "VPCOptionsTypeDef",
        "CognitoOptions": "CognitoOptionsTypeDef",
        "EncryptionAtRestOptions": "EncryptionAtRestOptionsTypeDef",
        "NodeToNodeEncryptionOptions": "NodeToNodeEncryptionOptionsTypeDef",
        "AdvancedOptions": Mapping[str, str],
        "LogPublishingOptions": Mapping[LogTypeType, "LogPublishingOptionTypeDef"],
        "DomainEndpointOptions": "DomainEndpointOptionsTypeDef",
        "AdvancedSecurityOptions": "AdvancedSecurityOptionsInputTypeDef",
        "TagList": Sequence["TagTypeDef"],
        "AutoTuneOptions": "AutoTuneOptionsInputTypeDef",
    },
    total=False,
)


class CreateDomainRequestRequestTypeDef(
    _RequiredCreateDomainRequestRequestTypeDef, _OptionalCreateDomainRequestRequestTypeDef
):
    pass


CreateDomainResponseTypeDef = TypedDict(
    "CreateDomainResponseTypeDef",
    {
        "DomainStatus": "DomainStatusTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

CreateOutboundConnectionRequestRequestTypeDef = TypedDict(
    "CreateOutboundConnectionRequestRequestTypeDef",
    {
        "LocalDomainInfo": "DomainInformationContainerTypeDef",
        "RemoteDomainInfo": "DomainInformationContainerTypeDef",
        "ConnectionAlias": str,
    },
)

CreateOutboundConnectionResponseTypeDef = TypedDict(
    "CreateOutboundConnectionResponseTypeDef",
    {
        "LocalDomainInfo": "DomainInformationContainerTypeDef",
        "RemoteDomainInfo": "DomainInformationContainerTypeDef",
        "ConnectionAlias": str,
        "ConnectionStatus": "OutboundConnectionStatusTypeDef",
        "ConnectionId": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredCreatePackageRequestRequestTypeDef = TypedDict(
    "_RequiredCreatePackageRequestRequestTypeDef",
    {
        "PackageName": str,
        "PackageType": Literal["TXT-DICTIONARY"],
        "PackageSource": "PackageSourceTypeDef",
    },
)
_OptionalCreatePackageRequestRequestTypeDef = TypedDict(
    "_OptionalCreatePackageRequestRequestTypeDef",
    {
        "PackageDescription": str,
    },
    total=False,
)


class CreatePackageRequestRequestTypeDef(
    _RequiredCreatePackageRequestRequestTypeDef, _OptionalCreatePackageRequestRequestTypeDef
):
    pass


CreatePackageResponseTypeDef = TypedDict(
    "CreatePackageResponseTypeDef",
    {
        "PackageDetails": "PackageDetailsTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DeleteDomainRequestRequestTypeDef = TypedDict(
    "DeleteDomainRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)

DeleteDomainResponseTypeDef = TypedDict(
    "DeleteDomainResponseTypeDef",
    {
        "DomainStatus": "DomainStatusTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DeleteInboundConnectionRequestRequestTypeDef = TypedDict(
    "DeleteInboundConnectionRequestRequestTypeDef",
    {
        "ConnectionId": str,
    },
)

DeleteInboundConnectionResponseTypeDef = TypedDict(
    "DeleteInboundConnectionResponseTypeDef",
    {
        "Connection": "InboundConnectionTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DeleteOutboundConnectionRequestRequestTypeDef = TypedDict(
    "DeleteOutboundConnectionRequestRequestTypeDef",
    {
        "ConnectionId": str,
    },
)

DeleteOutboundConnectionResponseTypeDef = TypedDict(
    "DeleteOutboundConnectionResponseTypeDef",
    {
        "Connection": "OutboundConnectionTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DeletePackageRequestRequestTypeDef = TypedDict(
    "DeletePackageRequestRequestTypeDef",
    {
        "PackageID": str,
    },
)

DeletePackageResponseTypeDef = TypedDict(
    "DeletePackageResponseTypeDef",
    {
        "PackageDetails": "PackageDetailsTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredDescribeDomainAutoTunesRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeDomainAutoTunesRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)
_OptionalDescribeDomainAutoTunesRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeDomainAutoTunesRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class DescribeDomainAutoTunesRequestRequestTypeDef(
    _RequiredDescribeDomainAutoTunesRequestRequestTypeDef,
    _OptionalDescribeDomainAutoTunesRequestRequestTypeDef,
):
    pass


DescribeDomainAutoTunesResponseTypeDef = TypedDict(
    "DescribeDomainAutoTunesResponseTypeDef",
    {
        "AutoTunes": List["AutoTuneTypeDef"],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredDescribeDomainChangeProgressRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeDomainChangeProgressRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)
_OptionalDescribeDomainChangeProgressRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeDomainChangeProgressRequestRequestTypeDef",
    {
        "ChangeId": str,
    },
    total=False,
)


class DescribeDomainChangeProgressRequestRequestTypeDef(
    _RequiredDescribeDomainChangeProgressRequestRequestTypeDef,
    _OptionalDescribeDomainChangeProgressRequestRequestTypeDef,
):
    pass


DescribeDomainChangeProgressResponseTypeDef = TypedDict(
    "DescribeDomainChangeProgressResponseTypeDef",
    {
        "ChangeProgressStatus": "ChangeProgressStatusDetailsTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeDomainConfigRequestRequestTypeDef = TypedDict(
    "DescribeDomainConfigRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)

DescribeDomainConfigResponseTypeDef = TypedDict(
    "DescribeDomainConfigResponseTypeDef",
    {
        "DomainConfig": "DomainConfigTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeDomainRequestRequestTypeDef = TypedDict(
    "DescribeDomainRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)

DescribeDomainResponseTypeDef = TypedDict(
    "DescribeDomainResponseTypeDef",
    {
        "DomainStatus": "DomainStatusTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeDomainsRequestRequestTypeDef = TypedDict(
    "DescribeDomainsRequestRequestTypeDef",
    {
        "DomainNames": Sequence[str],
    },
)

DescribeDomainsResponseTypeDef = TypedDict(
    "DescribeDomainsResponseTypeDef",
    {
        "DomainStatusList": List["DomainStatusTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeInboundConnectionsRequestRequestTypeDef = TypedDict(
    "DescribeInboundConnectionsRequestRequestTypeDef",
    {
        "Filters": Sequence["FilterTypeDef"],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

DescribeInboundConnectionsResponseTypeDef = TypedDict(
    "DescribeInboundConnectionsResponseTypeDef",
    {
        "Connections": List["InboundConnectionTypeDef"],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredDescribeInstanceTypeLimitsRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeInstanceTypeLimitsRequestRequestTypeDef",
    {
        "InstanceType": OpenSearchPartitionInstanceTypeType,
        "EngineVersion": str,
    },
)
_OptionalDescribeInstanceTypeLimitsRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeInstanceTypeLimitsRequestRequestTypeDef",
    {
        "DomainName": str,
    },
    total=False,
)


class DescribeInstanceTypeLimitsRequestRequestTypeDef(
    _RequiredDescribeInstanceTypeLimitsRequestRequestTypeDef,
    _OptionalDescribeInstanceTypeLimitsRequestRequestTypeDef,
):
    pass


DescribeInstanceTypeLimitsResponseTypeDef = TypedDict(
    "DescribeInstanceTypeLimitsResponseTypeDef",
    {
        "LimitsByRole": Dict[str, "LimitsTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeOutboundConnectionsRequestRequestTypeDef = TypedDict(
    "DescribeOutboundConnectionsRequestRequestTypeDef",
    {
        "Filters": Sequence["FilterTypeDef"],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

DescribeOutboundConnectionsResponseTypeDef = TypedDict(
    "DescribeOutboundConnectionsResponseTypeDef",
    {
        "Connections": List["OutboundConnectionTypeDef"],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribePackagesFilterTypeDef = TypedDict(
    "DescribePackagesFilterTypeDef",
    {
        "Name": DescribePackagesFilterNameType,
        "Value": Sequence[str],
    },
    total=False,
)

DescribePackagesRequestRequestTypeDef = TypedDict(
    "DescribePackagesRequestRequestTypeDef",
    {
        "Filters": Sequence["DescribePackagesFilterTypeDef"],
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

DescribePackagesResponseTypeDef = TypedDict(
    "DescribePackagesResponseTypeDef",
    {
        "PackageDetailsList": List["PackageDetailsTypeDef"],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeReservedInstanceOfferingsRequestRequestTypeDef = TypedDict(
    "DescribeReservedInstanceOfferingsRequestRequestTypeDef",
    {
        "ReservedInstanceOfferingId": str,
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

DescribeReservedInstanceOfferingsResponseTypeDef = TypedDict(
    "DescribeReservedInstanceOfferingsResponseTypeDef",
    {
        "NextToken": str,
        "ReservedInstanceOfferings": List["ReservedInstanceOfferingTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeReservedInstancesRequestRequestTypeDef = TypedDict(
    "DescribeReservedInstancesRequestRequestTypeDef",
    {
        "ReservedInstanceId": str,
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

DescribeReservedInstancesResponseTypeDef = TypedDict(
    "DescribeReservedInstancesResponseTypeDef",
    {
        "NextToken": str,
        "ReservedInstances": List["ReservedInstanceTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DissociatePackageRequestRequestTypeDef = TypedDict(
    "DissociatePackageRequestRequestTypeDef",
    {
        "PackageID": str,
        "DomainName": str,
    },
)

DissociatePackageResponseTypeDef = TypedDict(
    "DissociatePackageResponseTypeDef",
    {
        "DomainPackageDetails": "DomainPackageDetailsTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DomainConfigTypeDef = TypedDict(
    "DomainConfigTypeDef",
    {
        "EngineVersion": "VersionStatusTypeDef",
        "ClusterConfig": "ClusterConfigStatusTypeDef",
        "EBSOptions": "EBSOptionsStatusTypeDef",
        "AccessPolicies": "AccessPoliciesStatusTypeDef",
        "SnapshotOptions": "SnapshotOptionsStatusTypeDef",
        "VPCOptions": "VPCDerivedInfoStatusTypeDef",
        "CognitoOptions": "CognitoOptionsStatusTypeDef",
        "EncryptionAtRestOptions": "EncryptionAtRestOptionsStatusTypeDef",
        "NodeToNodeEncryptionOptions": "NodeToNodeEncryptionOptionsStatusTypeDef",
        "AdvancedOptions": "AdvancedOptionsStatusTypeDef",
        "LogPublishingOptions": "LogPublishingOptionsStatusTypeDef",
        "DomainEndpointOptions": "DomainEndpointOptionsStatusTypeDef",
        "AdvancedSecurityOptions": "AdvancedSecurityOptionsStatusTypeDef",
        "AutoTuneOptions": "AutoTuneOptionsStatusTypeDef",
        "ChangeProgressDetails": "ChangeProgressDetailsTypeDef",
    },
    total=False,
)

DomainEndpointOptionsStatusTypeDef = TypedDict(
    "DomainEndpointOptionsStatusTypeDef",
    {
        "Options": "DomainEndpointOptionsTypeDef",
        "Status": "OptionStatusTypeDef",
    },
)

DomainEndpointOptionsTypeDef = TypedDict(
    "DomainEndpointOptionsTypeDef",
    {
        "EnforceHTTPS": bool,
        "TLSSecurityPolicy": TLSSecurityPolicyType,
        "CustomEndpointEnabled": bool,
        "CustomEndpoint": str,
        "CustomEndpointCertificateArn": str,
    },
    total=False,
)

DomainInfoTypeDef = TypedDict(
    "DomainInfoTypeDef",
    {
        "DomainName": str,
        "EngineType": EngineTypeType,
    },
    total=False,
)

DomainInformationContainerTypeDef = TypedDict(
    "DomainInformationContainerTypeDef",
    {
        "AWSDomainInformation": "AWSDomainInformationTypeDef",
    },
    total=False,
)

DomainPackageDetailsTypeDef = TypedDict(
    "DomainPackageDetailsTypeDef",
    {
        "PackageID": str,
        "PackageName": str,
        "PackageType": Literal["TXT-DICTIONARY"],
        "LastUpdated": datetime,
        "DomainName": str,
        "DomainPackageStatus": DomainPackageStatusType,
        "PackageVersion": str,
        "ReferencePath": str,
        "ErrorDetails": "ErrorDetailsTypeDef",
    },
    total=False,
)

_RequiredDomainStatusTypeDef = TypedDict(
    "_RequiredDomainStatusTypeDef",
    {
        "DomainId": str,
        "DomainName": str,
        "ARN": str,
        "ClusterConfig": "ClusterConfigTypeDef",
    },
)
_OptionalDomainStatusTypeDef = TypedDict(
    "_OptionalDomainStatusTypeDef",
    {
        "Created": bool,
        "Deleted": bool,
        "Endpoint": str,
        "Endpoints": Dict[str, str],
        "Processing": bool,
        "UpgradeProcessing": bool,
        "EngineVersion": str,
        "EBSOptions": "EBSOptionsTypeDef",
        "AccessPolicies": str,
        "SnapshotOptions": "SnapshotOptionsTypeDef",
        "VPCOptions": "VPCDerivedInfoTypeDef",
        "CognitoOptions": "CognitoOptionsTypeDef",
        "EncryptionAtRestOptions": "EncryptionAtRestOptionsTypeDef",
        "NodeToNodeEncryptionOptions": "NodeToNodeEncryptionOptionsTypeDef",
        "AdvancedOptions": Dict[str, str],
        "LogPublishingOptions": Dict[LogTypeType, "LogPublishingOptionTypeDef"],
        "ServiceSoftwareOptions": "ServiceSoftwareOptionsTypeDef",
        "DomainEndpointOptions": "DomainEndpointOptionsTypeDef",
        "AdvancedSecurityOptions": "AdvancedSecurityOptionsTypeDef",
        "AutoTuneOptions": "AutoTuneOptionsOutputTypeDef",
        "ChangeProgressDetails": "ChangeProgressDetailsTypeDef",
    },
    total=False,
)


class DomainStatusTypeDef(_RequiredDomainStatusTypeDef, _OptionalDomainStatusTypeDef):
    pass


DryRunResultsTypeDef = TypedDict(
    "DryRunResultsTypeDef",
    {
        "DeploymentType": str,
        "Message": str,
    },
    total=False,
)

DurationTypeDef = TypedDict(
    "DurationTypeDef",
    {
        "Value": int,
        "Unit": Literal["HOURS"],
    },
    total=False,
)

EBSOptionsStatusTypeDef = TypedDict(
    "EBSOptionsStatusTypeDef",
    {
        "Options": "EBSOptionsTypeDef",
        "Status": "OptionStatusTypeDef",
    },
)

EBSOptionsTypeDef = TypedDict(
    "EBSOptionsTypeDef",
    {
        "EBSEnabled": bool,
        "VolumeType": VolumeTypeType,
        "VolumeSize": int,
        "Iops": int,
    },
    total=False,
)

EncryptionAtRestOptionsStatusTypeDef = TypedDict(
    "EncryptionAtRestOptionsStatusTypeDef",
    {
        "Options": "EncryptionAtRestOptionsTypeDef",
        "Status": "OptionStatusTypeDef",
    },
)

EncryptionAtRestOptionsTypeDef = TypedDict(
    "EncryptionAtRestOptionsTypeDef",
    {
        "Enabled": bool,
        "KmsKeyId": str,
    },
    total=False,
)

ErrorDetailsTypeDef = TypedDict(
    "ErrorDetailsTypeDef",
    {
        "ErrorType": str,
        "ErrorMessage": str,
    },
    total=False,
)

FilterTypeDef = TypedDict(
    "FilterTypeDef",
    {
        "Name": str,
        "Values": Sequence[str],
    },
    total=False,
)

GetCompatibleVersionsRequestRequestTypeDef = TypedDict(
    "GetCompatibleVersionsRequestRequestTypeDef",
    {
        "DomainName": str,
    },
    total=False,
)

GetCompatibleVersionsResponseTypeDef = TypedDict(
    "GetCompatibleVersionsResponseTypeDef",
    {
        "CompatibleVersions": List["CompatibleVersionsMapTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredGetPackageVersionHistoryRequestRequestTypeDef = TypedDict(
    "_RequiredGetPackageVersionHistoryRequestRequestTypeDef",
    {
        "PackageID": str,
    },
)
_OptionalGetPackageVersionHistoryRequestRequestTypeDef = TypedDict(
    "_OptionalGetPackageVersionHistoryRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class GetPackageVersionHistoryRequestRequestTypeDef(
    _RequiredGetPackageVersionHistoryRequestRequestTypeDef,
    _OptionalGetPackageVersionHistoryRequestRequestTypeDef,
):
    pass


GetPackageVersionHistoryResponseTypeDef = TypedDict(
    "GetPackageVersionHistoryResponseTypeDef",
    {
        "PackageID": str,
        "PackageVersionHistoryList": List["PackageVersionHistoryTypeDef"],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredGetUpgradeHistoryRequestRequestTypeDef = TypedDict(
    "_RequiredGetUpgradeHistoryRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)
_OptionalGetUpgradeHistoryRequestRequestTypeDef = TypedDict(
    "_OptionalGetUpgradeHistoryRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class GetUpgradeHistoryRequestRequestTypeDef(
    _RequiredGetUpgradeHistoryRequestRequestTypeDef, _OptionalGetUpgradeHistoryRequestRequestTypeDef
):
    pass


GetUpgradeHistoryResponseTypeDef = TypedDict(
    "GetUpgradeHistoryResponseTypeDef",
    {
        "UpgradeHistories": List["UpgradeHistoryTypeDef"],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetUpgradeStatusRequestRequestTypeDef = TypedDict(
    "GetUpgradeStatusRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)

GetUpgradeStatusResponseTypeDef = TypedDict(
    "GetUpgradeStatusResponseTypeDef",
    {
        "UpgradeStep": UpgradeStepType,
        "StepStatus": UpgradeStatusType,
        "UpgradeName": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

InboundConnectionStatusTypeDef = TypedDict(
    "InboundConnectionStatusTypeDef",
    {
        "StatusCode": InboundConnectionStatusCodeType,
        "Message": str,
    },
    total=False,
)

InboundConnectionTypeDef = TypedDict(
    "InboundConnectionTypeDef",
    {
        "LocalDomainInfo": "DomainInformationContainerTypeDef",
        "RemoteDomainInfo": "DomainInformationContainerTypeDef",
        "ConnectionId": str,
        "ConnectionStatus": "InboundConnectionStatusTypeDef",
    },
    total=False,
)

InstanceCountLimitsTypeDef = TypedDict(
    "InstanceCountLimitsTypeDef",
    {
        "MinimumInstanceCount": int,
        "MaximumInstanceCount": int,
    },
    total=False,
)

InstanceLimitsTypeDef = TypedDict(
    "InstanceLimitsTypeDef",
    {
        "InstanceCountLimits": "InstanceCountLimitsTypeDef",
    },
    total=False,
)

InstanceTypeDetailsTypeDef = TypedDict(
    "InstanceTypeDetailsTypeDef",
    {
        "InstanceType": OpenSearchPartitionInstanceTypeType,
        "EncryptionEnabled": bool,
        "CognitoEnabled": bool,
        "AppLogsEnabled": bool,
        "AdvancedSecurityEnabled": bool,
        "WarmEnabled": bool,
        "InstanceRole": List[str],
    },
    total=False,
)

LimitsTypeDef = TypedDict(
    "LimitsTypeDef",
    {
        "StorageTypes": List["StorageTypeTypeDef"],
        "InstanceLimits": "InstanceLimitsTypeDef",
        "AdditionalLimits": List["AdditionalLimitTypeDef"],
    },
    total=False,
)

ListDomainNamesRequestRequestTypeDef = TypedDict(
    "ListDomainNamesRequestRequestTypeDef",
    {
        "EngineType": EngineTypeType,
    },
    total=False,
)

ListDomainNamesResponseTypeDef = TypedDict(
    "ListDomainNamesResponseTypeDef",
    {
        "DomainNames": List["DomainInfoTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredListDomainsForPackageRequestRequestTypeDef = TypedDict(
    "_RequiredListDomainsForPackageRequestRequestTypeDef",
    {
        "PackageID": str,
    },
)
_OptionalListDomainsForPackageRequestRequestTypeDef = TypedDict(
    "_OptionalListDomainsForPackageRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class ListDomainsForPackageRequestRequestTypeDef(
    _RequiredListDomainsForPackageRequestRequestTypeDef,
    _OptionalListDomainsForPackageRequestRequestTypeDef,
):
    pass


ListDomainsForPackageResponseTypeDef = TypedDict(
    "ListDomainsForPackageResponseTypeDef",
    {
        "DomainPackageDetailsList": List["DomainPackageDetailsTypeDef"],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredListInstanceTypeDetailsRequestRequestTypeDef = TypedDict(
    "_RequiredListInstanceTypeDetailsRequestRequestTypeDef",
    {
        "EngineVersion": str,
    },
)
_OptionalListInstanceTypeDetailsRequestRequestTypeDef = TypedDict(
    "_OptionalListInstanceTypeDetailsRequestRequestTypeDef",
    {
        "DomainName": str,
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class ListInstanceTypeDetailsRequestRequestTypeDef(
    _RequiredListInstanceTypeDetailsRequestRequestTypeDef,
    _OptionalListInstanceTypeDetailsRequestRequestTypeDef,
):
    pass


ListInstanceTypeDetailsResponseTypeDef = TypedDict(
    "ListInstanceTypeDetailsResponseTypeDef",
    {
        "InstanceTypeDetails": List["InstanceTypeDetailsTypeDef"],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredListPackagesForDomainRequestRequestTypeDef = TypedDict(
    "_RequiredListPackagesForDomainRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)
_OptionalListPackagesForDomainRequestRequestTypeDef = TypedDict(
    "_OptionalListPackagesForDomainRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class ListPackagesForDomainRequestRequestTypeDef(
    _RequiredListPackagesForDomainRequestRequestTypeDef,
    _OptionalListPackagesForDomainRequestRequestTypeDef,
):
    pass


ListPackagesForDomainResponseTypeDef = TypedDict(
    "ListPackagesForDomainResponseTypeDef",
    {
        "DomainPackageDetailsList": List["DomainPackageDetailsTypeDef"],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListTagsRequestRequestTypeDef = TypedDict(
    "ListTagsRequestRequestTypeDef",
    {
        "ARN": str,
    },
)

ListTagsResponseTypeDef = TypedDict(
    "ListTagsResponseTypeDef",
    {
        "TagList": List["TagTypeDef"],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListVersionsRequestRequestTypeDef = TypedDict(
    "ListVersionsRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

ListVersionsResponseTypeDef = TypedDict(
    "ListVersionsResponseTypeDef",
    {
        "Versions": List[str],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

LogPublishingOptionTypeDef = TypedDict(
    "LogPublishingOptionTypeDef",
    {
        "CloudWatchLogsLogGroupArn": str,
        "Enabled": bool,
    },
    total=False,
)

LogPublishingOptionsStatusTypeDef = TypedDict(
    "LogPublishingOptionsStatusTypeDef",
    {
        "Options": Dict[LogTypeType, "LogPublishingOptionTypeDef"],
        "Status": "OptionStatusTypeDef",
    },
    total=False,
)

MasterUserOptionsTypeDef = TypedDict(
    "MasterUserOptionsTypeDef",
    {
        "MasterUserARN": str,
        "MasterUserName": str,
        "MasterUserPassword": str,
    },
    total=False,
)

NodeToNodeEncryptionOptionsStatusTypeDef = TypedDict(
    "NodeToNodeEncryptionOptionsStatusTypeDef",
    {
        "Options": "NodeToNodeEncryptionOptionsTypeDef",
        "Status": "OptionStatusTypeDef",
    },
)

NodeToNodeEncryptionOptionsTypeDef = TypedDict(
    "NodeToNodeEncryptionOptionsTypeDef",
    {
        "Enabled": bool,
    },
    total=False,
)

_RequiredOptionStatusTypeDef = TypedDict(
    "_RequiredOptionStatusTypeDef",
    {
        "CreationDate": datetime,
        "UpdateDate": datetime,
        "State": OptionStateType,
    },
)
_OptionalOptionStatusTypeDef = TypedDict(
    "_OptionalOptionStatusTypeDef",
    {
        "UpdateVersion": int,
        "PendingDeletion": bool,
    },
    total=False,
)


class OptionStatusTypeDef(_RequiredOptionStatusTypeDef, _OptionalOptionStatusTypeDef):
    pass


OutboundConnectionStatusTypeDef = TypedDict(
    "OutboundConnectionStatusTypeDef",
    {
        "StatusCode": OutboundConnectionStatusCodeType,
        "Message": str,
    },
    total=False,
)

OutboundConnectionTypeDef = TypedDict(
    "OutboundConnectionTypeDef",
    {
        "LocalDomainInfo": "DomainInformationContainerTypeDef",
        "RemoteDomainInfo": "DomainInformationContainerTypeDef",
        "ConnectionId": str,
        "ConnectionAlias": str,
        "ConnectionStatus": "OutboundConnectionStatusTypeDef",
    },
    total=False,
)

PackageDetailsTypeDef = TypedDict(
    "PackageDetailsTypeDef",
    {
        "PackageID": str,
        "PackageName": str,
        "PackageType": Literal["TXT-DICTIONARY"],
        "PackageDescription": str,
        "PackageStatus": PackageStatusType,
        "CreatedAt": datetime,
        "LastUpdatedAt": datetime,
        "AvailablePackageVersion": str,
        "ErrorDetails": "ErrorDetailsTypeDef",
    },
    total=False,
)

PackageSourceTypeDef = TypedDict(
    "PackageSourceTypeDef",
    {
        "S3BucketName": str,
        "S3Key": str,
    },
    total=False,
)

PackageVersionHistoryTypeDef = TypedDict(
    "PackageVersionHistoryTypeDef",
    {
        "PackageVersion": str,
        "CommitMessage": str,
        "CreatedAt": datetime,
    },
    total=False,
)

_RequiredPurchaseReservedInstanceOfferingRequestRequestTypeDef = TypedDict(
    "_RequiredPurchaseReservedInstanceOfferingRequestRequestTypeDef",
    {
        "ReservedInstanceOfferingId": str,
        "ReservationName": str,
    },
)
_OptionalPurchaseReservedInstanceOfferingRequestRequestTypeDef = TypedDict(
    "_OptionalPurchaseReservedInstanceOfferingRequestRequestTypeDef",
    {
        "InstanceCount": int,
    },
    total=False,
)


class PurchaseReservedInstanceOfferingRequestRequestTypeDef(
    _RequiredPurchaseReservedInstanceOfferingRequestRequestTypeDef,
    _OptionalPurchaseReservedInstanceOfferingRequestRequestTypeDef,
):
    pass


PurchaseReservedInstanceOfferingResponseTypeDef = TypedDict(
    "PurchaseReservedInstanceOfferingResponseTypeDef",
    {
        "ReservedInstanceId": str,
        "ReservationName": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

RecurringChargeTypeDef = TypedDict(
    "RecurringChargeTypeDef",
    {
        "RecurringChargeAmount": float,
        "RecurringChargeFrequency": str,
    },
    total=False,
)

RejectInboundConnectionRequestRequestTypeDef = TypedDict(
    "RejectInboundConnectionRequestRequestTypeDef",
    {
        "ConnectionId": str,
    },
)

RejectInboundConnectionResponseTypeDef = TypedDict(
    "RejectInboundConnectionResponseTypeDef",
    {
        "Connection": "InboundConnectionTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

RemoveTagsRequestRequestTypeDef = TypedDict(
    "RemoveTagsRequestRequestTypeDef",
    {
        "ARN": str,
        "TagKeys": Sequence[str],
    },
)

ReservedInstanceOfferingTypeDef = TypedDict(
    "ReservedInstanceOfferingTypeDef",
    {
        "ReservedInstanceOfferingId": str,
        "InstanceType": OpenSearchPartitionInstanceTypeType,
        "Duration": int,
        "FixedPrice": float,
        "UsagePrice": float,
        "CurrencyCode": str,
        "PaymentOption": ReservedInstancePaymentOptionType,
        "RecurringCharges": List["RecurringChargeTypeDef"],
    },
    total=False,
)

ReservedInstanceTypeDef = TypedDict(
    "ReservedInstanceTypeDef",
    {
        "ReservationName": str,
        "ReservedInstanceId": str,
        "BillingSubscriptionId": int,
        "ReservedInstanceOfferingId": str,
        "InstanceType": OpenSearchPartitionInstanceTypeType,
        "StartTime": datetime,
        "Duration": int,
        "FixedPrice": float,
        "UsagePrice": float,
        "CurrencyCode": str,
        "InstanceCount": int,
        "State": str,
        "PaymentOption": ReservedInstancePaymentOptionType,
        "RecurringCharges": List["RecurringChargeTypeDef"],
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

SAMLIdpTypeDef = TypedDict(
    "SAMLIdpTypeDef",
    {
        "MetadataContent": str,
        "EntityId": str,
    },
)

SAMLOptionsInputTypeDef = TypedDict(
    "SAMLOptionsInputTypeDef",
    {
        "Enabled": bool,
        "Idp": "SAMLIdpTypeDef",
        "MasterUserName": str,
        "MasterBackendRole": str,
        "SubjectKey": str,
        "RolesKey": str,
        "SessionTimeoutMinutes": int,
    },
    total=False,
)

SAMLOptionsOutputTypeDef = TypedDict(
    "SAMLOptionsOutputTypeDef",
    {
        "Enabled": bool,
        "Idp": "SAMLIdpTypeDef",
        "SubjectKey": str,
        "RolesKey": str,
        "SessionTimeoutMinutes": int,
    },
    total=False,
)

ScheduledAutoTuneDetailsTypeDef = TypedDict(
    "ScheduledAutoTuneDetailsTypeDef",
    {
        "Date": datetime,
        "ActionType": ScheduledAutoTuneActionTypeType,
        "Action": str,
        "Severity": ScheduledAutoTuneSeverityTypeType,
    },
    total=False,
)

ServiceSoftwareOptionsTypeDef = TypedDict(
    "ServiceSoftwareOptionsTypeDef",
    {
        "CurrentVersion": str,
        "NewVersion": str,
        "UpdateAvailable": bool,
        "Cancellable": bool,
        "UpdateStatus": DeploymentStatusType,
        "Description": str,
        "AutomatedUpdateDate": datetime,
        "OptionalDeployment": bool,
    },
    total=False,
)

SnapshotOptionsStatusTypeDef = TypedDict(
    "SnapshotOptionsStatusTypeDef",
    {
        "Options": "SnapshotOptionsTypeDef",
        "Status": "OptionStatusTypeDef",
    },
)

SnapshotOptionsTypeDef = TypedDict(
    "SnapshotOptionsTypeDef",
    {
        "AutomatedSnapshotStartHour": int,
    },
    total=False,
)

StartServiceSoftwareUpdateRequestRequestTypeDef = TypedDict(
    "StartServiceSoftwareUpdateRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)

StartServiceSoftwareUpdateResponseTypeDef = TypedDict(
    "StartServiceSoftwareUpdateResponseTypeDef",
    {
        "ServiceSoftwareOptions": "ServiceSoftwareOptionsTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

StorageTypeLimitTypeDef = TypedDict(
    "StorageTypeLimitTypeDef",
    {
        "LimitName": str,
        "LimitValues": List[str],
    },
    total=False,
)

StorageTypeTypeDef = TypedDict(
    "StorageTypeTypeDef",
    {
        "StorageTypeName": str,
        "StorageSubTypeName": str,
        "StorageTypeLimits": List["StorageTypeLimitTypeDef"],
    },
    total=False,
)

TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "Key": str,
        "Value": str,
    },
)

_RequiredUpdateDomainConfigRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateDomainConfigRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)
_OptionalUpdateDomainConfigRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateDomainConfigRequestRequestTypeDef",
    {
        "ClusterConfig": "ClusterConfigTypeDef",
        "EBSOptions": "EBSOptionsTypeDef",
        "SnapshotOptions": "SnapshotOptionsTypeDef",
        "VPCOptions": "VPCOptionsTypeDef",
        "CognitoOptions": "CognitoOptionsTypeDef",
        "AdvancedOptions": Mapping[str, str],
        "AccessPolicies": str,
        "LogPublishingOptions": Mapping[LogTypeType, "LogPublishingOptionTypeDef"],
        "EncryptionAtRestOptions": "EncryptionAtRestOptionsTypeDef",
        "DomainEndpointOptions": "DomainEndpointOptionsTypeDef",
        "NodeToNodeEncryptionOptions": "NodeToNodeEncryptionOptionsTypeDef",
        "AdvancedSecurityOptions": "AdvancedSecurityOptionsInputTypeDef",
        "AutoTuneOptions": "AutoTuneOptionsTypeDef",
        "DryRun": bool,
    },
    total=False,
)


class UpdateDomainConfigRequestRequestTypeDef(
    _RequiredUpdateDomainConfigRequestRequestTypeDef,
    _OptionalUpdateDomainConfigRequestRequestTypeDef,
):
    pass


UpdateDomainConfigResponseTypeDef = TypedDict(
    "UpdateDomainConfigResponseTypeDef",
    {
        "DomainConfig": "DomainConfigTypeDef",
        "DryRunResults": "DryRunResultsTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredUpdatePackageRequestRequestTypeDef = TypedDict(
    "_RequiredUpdatePackageRequestRequestTypeDef",
    {
        "PackageID": str,
        "PackageSource": "PackageSourceTypeDef",
    },
)
_OptionalUpdatePackageRequestRequestTypeDef = TypedDict(
    "_OptionalUpdatePackageRequestRequestTypeDef",
    {
        "PackageDescription": str,
        "CommitMessage": str,
    },
    total=False,
)


class UpdatePackageRequestRequestTypeDef(
    _RequiredUpdatePackageRequestRequestTypeDef, _OptionalUpdatePackageRequestRequestTypeDef
):
    pass


UpdatePackageResponseTypeDef = TypedDict(
    "UpdatePackageResponseTypeDef",
    {
        "PackageDetails": "PackageDetailsTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredUpgradeDomainRequestRequestTypeDef = TypedDict(
    "_RequiredUpgradeDomainRequestRequestTypeDef",
    {
        "DomainName": str,
        "TargetVersion": str,
    },
)
_OptionalUpgradeDomainRequestRequestTypeDef = TypedDict(
    "_OptionalUpgradeDomainRequestRequestTypeDef",
    {
        "PerformCheckOnly": bool,
        "AdvancedOptions": Mapping[str, str],
    },
    total=False,
)


class UpgradeDomainRequestRequestTypeDef(
    _RequiredUpgradeDomainRequestRequestTypeDef, _OptionalUpgradeDomainRequestRequestTypeDef
):
    pass


UpgradeDomainResponseTypeDef = TypedDict(
    "UpgradeDomainResponseTypeDef",
    {
        "UpgradeId": str,
        "DomainName": str,
        "TargetVersion": str,
        "PerformCheckOnly": bool,
        "AdvancedOptions": Dict[str, str],
        "ChangeProgressDetails": "ChangeProgressDetailsTypeDef",
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

UpgradeHistoryTypeDef = TypedDict(
    "UpgradeHistoryTypeDef",
    {
        "UpgradeName": str,
        "StartTimestamp": datetime,
        "UpgradeStatus": UpgradeStatusType,
        "StepsList": List["UpgradeStepItemTypeDef"],
    },
    total=False,
)

UpgradeStepItemTypeDef = TypedDict(
    "UpgradeStepItemTypeDef",
    {
        "UpgradeStep": UpgradeStepType,
        "UpgradeStepStatus": UpgradeStatusType,
        "Issues": List[str],
        "ProgressPercent": float,
    },
    total=False,
)

VPCDerivedInfoStatusTypeDef = TypedDict(
    "VPCDerivedInfoStatusTypeDef",
    {
        "Options": "VPCDerivedInfoTypeDef",
        "Status": "OptionStatusTypeDef",
    },
)

VPCDerivedInfoTypeDef = TypedDict(
    "VPCDerivedInfoTypeDef",
    {
        "VPCId": str,
        "SubnetIds": List[str],
        "AvailabilityZones": List[str],
        "SecurityGroupIds": List[str],
    },
    total=False,
)

VPCOptionsTypeDef = TypedDict(
    "VPCOptionsTypeDef",
    {
        "SubnetIds": Sequence[str],
        "SecurityGroupIds": Sequence[str],
    },
    total=False,
)

VersionStatusTypeDef = TypedDict(
    "VersionStatusTypeDef",
    {
        "Options": str,
        "Status": "OptionStatusTypeDef",
    },
)

ZoneAwarenessConfigTypeDef = TypedDict(
    "ZoneAwarenessConfigTypeDef",
    {
        "AvailabilityZoneCount": int,
    },
    total=False,
)
