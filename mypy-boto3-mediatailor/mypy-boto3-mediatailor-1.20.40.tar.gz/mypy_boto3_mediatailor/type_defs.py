"""
Type annotations for mediatailor service type definitions.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/type_defs.html)

Usage::

    ```python
    from mypy_boto3_mediatailor.type_defs import AccessConfigurationTypeDef

    data: AccessConfigurationTypeDef = {...}
    ```
"""
import sys
from datetime import datetime
from typing import Dict, List, Mapping, Sequence, Union

from .literals import (
    AccessTypeType,
    ChannelStateType,
    ModeType,
    OriginManifestTypeType,
    PlaybackModeType,
    RelativePositionType,
    ScheduleEntryTypeType,
    TypeType,
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
    "AccessConfigurationTypeDef",
    "AdBreakTypeDef",
    "AdMarkerPassthroughTypeDef",
    "AlertTypeDef",
    "AvailMatchingCriteriaTypeDef",
    "AvailSuppressionTypeDef",
    "BumperTypeDef",
    "CdnConfigurationTypeDef",
    "ChannelTypeDef",
    "ConfigureLogsForPlaybackConfigurationRequestRequestTypeDef",
    "ConfigureLogsForPlaybackConfigurationResponseTypeDef",
    "CreateChannelRequestRequestTypeDef",
    "CreateChannelResponseTypeDef",
    "CreatePrefetchScheduleRequestRequestTypeDef",
    "CreatePrefetchScheduleResponseTypeDef",
    "CreateProgramRequestRequestTypeDef",
    "CreateProgramResponseTypeDef",
    "CreateSourceLocationRequestRequestTypeDef",
    "CreateSourceLocationResponseTypeDef",
    "CreateVodSourceRequestRequestTypeDef",
    "CreateVodSourceResponseTypeDef",
    "DashConfigurationForPutTypeDef",
    "DashConfigurationTypeDef",
    "DashPlaylistSettingsTypeDef",
    "DefaultSegmentDeliveryConfigurationTypeDef",
    "DeleteChannelPolicyRequestRequestTypeDef",
    "DeleteChannelRequestRequestTypeDef",
    "DeletePlaybackConfigurationRequestRequestTypeDef",
    "DeletePrefetchScheduleRequestRequestTypeDef",
    "DeleteProgramRequestRequestTypeDef",
    "DeleteSourceLocationRequestRequestTypeDef",
    "DeleteVodSourceRequestRequestTypeDef",
    "DescribeChannelRequestRequestTypeDef",
    "DescribeChannelResponseTypeDef",
    "DescribeProgramRequestRequestTypeDef",
    "DescribeProgramResponseTypeDef",
    "DescribeSourceLocationRequestRequestTypeDef",
    "DescribeSourceLocationResponseTypeDef",
    "DescribeVodSourceRequestRequestTypeDef",
    "DescribeVodSourceResponseTypeDef",
    "GetChannelPolicyRequestRequestTypeDef",
    "GetChannelPolicyResponseTypeDef",
    "GetChannelScheduleRequestRequestTypeDef",
    "GetChannelScheduleResponseTypeDef",
    "GetPlaybackConfigurationRequestRequestTypeDef",
    "GetPlaybackConfigurationResponseTypeDef",
    "GetPrefetchScheduleRequestRequestTypeDef",
    "GetPrefetchScheduleResponseTypeDef",
    "HlsConfigurationTypeDef",
    "HlsPlaylistSettingsTypeDef",
    "HttpConfigurationTypeDef",
    "HttpPackageConfigurationTypeDef",
    "ListAlertsRequestRequestTypeDef",
    "ListAlertsResponseTypeDef",
    "ListChannelsRequestRequestTypeDef",
    "ListChannelsResponseTypeDef",
    "ListPlaybackConfigurationsRequestRequestTypeDef",
    "ListPlaybackConfigurationsResponseTypeDef",
    "ListPrefetchSchedulesRequestRequestTypeDef",
    "ListPrefetchSchedulesResponseTypeDef",
    "ListSourceLocationsRequestRequestTypeDef",
    "ListSourceLocationsResponseTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "ListVodSourcesRequestRequestTypeDef",
    "ListVodSourcesResponseTypeDef",
    "LivePreRollConfigurationTypeDef",
    "LogConfigurationTypeDef",
    "ManifestProcessingRulesTypeDef",
    "PaginatorConfigTypeDef",
    "PlaybackConfigurationTypeDef",
    "PrefetchConsumptionTypeDef",
    "PrefetchRetrievalTypeDef",
    "PrefetchScheduleTypeDef",
    "PutChannelPolicyRequestRequestTypeDef",
    "PutPlaybackConfigurationRequestRequestTypeDef",
    "PutPlaybackConfigurationResponseTypeDef",
    "RequestOutputItemTypeDef",
    "ResponseMetadataTypeDef",
    "ResponseOutputItemTypeDef",
    "ScheduleAdBreakTypeDef",
    "ScheduleConfigurationTypeDef",
    "ScheduleEntryTypeDef",
    "SecretsManagerAccessTokenConfigurationTypeDef",
    "SegmentDeliveryConfigurationTypeDef",
    "SlateSourceTypeDef",
    "SourceLocationTypeDef",
    "SpliceInsertMessageTypeDef",
    "StartChannelRequestRequestTypeDef",
    "StopChannelRequestRequestTypeDef",
    "TagResourceRequestRequestTypeDef",
    "TransitionTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdateChannelRequestRequestTypeDef",
    "UpdateChannelResponseTypeDef",
    "UpdateSourceLocationRequestRequestTypeDef",
    "UpdateSourceLocationResponseTypeDef",
    "UpdateVodSourceRequestRequestTypeDef",
    "UpdateVodSourceResponseTypeDef",
    "VodSourceTypeDef",
)

AccessConfigurationTypeDef = TypedDict(
    "AccessConfigurationTypeDef",
    {
        "AccessType": AccessTypeType,
        "SecretsManagerAccessTokenConfiguration": "SecretsManagerAccessTokenConfigurationTypeDef",
    },
    total=False,
)

AdBreakTypeDef = TypedDict(
    "AdBreakTypeDef",
    {
        "MessageType": Literal["SPLICE_INSERT"],
        "OffsetMillis": int,
        "Slate": "SlateSourceTypeDef",
        "SpliceInsertMessage": "SpliceInsertMessageTypeDef",
    },
    total=False,
)

AdMarkerPassthroughTypeDef = TypedDict(
    "AdMarkerPassthroughTypeDef",
    {
        "Enabled": bool,
    },
    total=False,
)

AlertTypeDef = TypedDict(
    "AlertTypeDef",
    {
        "AlertCode": str,
        "AlertMessage": str,
        "LastModifiedTime": datetime,
        "RelatedResourceArns": List[str],
        "ResourceArn": str,
    },
)

AvailMatchingCriteriaTypeDef = TypedDict(
    "AvailMatchingCriteriaTypeDef",
    {
        "DynamicVariable": str,
        "Operator": Literal["EQUALS"],
    },
)

AvailSuppressionTypeDef = TypedDict(
    "AvailSuppressionTypeDef",
    {
        "Mode": ModeType,
        "Value": str,
    },
    total=False,
)

BumperTypeDef = TypedDict(
    "BumperTypeDef",
    {
        "EndUrl": str,
        "StartUrl": str,
    },
    total=False,
)

CdnConfigurationTypeDef = TypedDict(
    "CdnConfigurationTypeDef",
    {
        "AdSegmentUrlPrefix": str,
        "ContentSegmentUrlPrefix": str,
    },
    total=False,
)

_RequiredChannelTypeDef = TypedDict(
    "_RequiredChannelTypeDef",
    {
        "Arn": str,
        "ChannelName": str,
        "ChannelState": str,
        "Outputs": List["ResponseOutputItemTypeDef"],
        "PlaybackMode": str,
    },
)
_OptionalChannelTypeDef = TypedDict(
    "_OptionalChannelTypeDef",
    {
        "CreationTime": datetime,
        "FillerSlate": "SlateSourceTypeDef",
        "LastModifiedTime": datetime,
        "Tags": Dict[str, str],
    },
    total=False,
)


class ChannelTypeDef(_RequiredChannelTypeDef, _OptionalChannelTypeDef):
    pass


ConfigureLogsForPlaybackConfigurationRequestRequestTypeDef = TypedDict(
    "ConfigureLogsForPlaybackConfigurationRequestRequestTypeDef",
    {
        "PercentEnabled": int,
        "PlaybackConfigurationName": str,
    },
)

ConfigureLogsForPlaybackConfigurationResponseTypeDef = TypedDict(
    "ConfigureLogsForPlaybackConfigurationResponseTypeDef",
    {
        "PercentEnabled": int,
        "PlaybackConfigurationName": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredCreateChannelRequestRequestTypeDef = TypedDict(
    "_RequiredCreateChannelRequestRequestTypeDef",
    {
        "ChannelName": str,
        "Outputs": Sequence["RequestOutputItemTypeDef"],
        "PlaybackMode": PlaybackModeType,
    },
)
_OptionalCreateChannelRequestRequestTypeDef = TypedDict(
    "_OptionalCreateChannelRequestRequestTypeDef",
    {
        "FillerSlate": "SlateSourceTypeDef",
        "Tags": Mapping[str, str],
    },
    total=False,
)


class CreateChannelRequestRequestTypeDef(
    _RequiredCreateChannelRequestRequestTypeDef, _OptionalCreateChannelRequestRequestTypeDef
):
    pass


CreateChannelResponseTypeDef = TypedDict(
    "CreateChannelResponseTypeDef",
    {
        "Arn": str,
        "ChannelName": str,
        "ChannelState": ChannelStateType,
        "CreationTime": datetime,
        "FillerSlate": "SlateSourceTypeDef",
        "LastModifiedTime": datetime,
        "Outputs": List["ResponseOutputItemTypeDef"],
        "PlaybackMode": str,
        "Tags": Dict[str, str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredCreatePrefetchScheduleRequestRequestTypeDef = TypedDict(
    "_RequiredCreatePrefetchScheduleRequestRequestTypeDef",
    {
        "Consumption": "PrefetchConsumptionTypeDef",
        "Name": str,
        "PlaybackConfigurationName": str,
        "Retrieval": "PrefetchRetrievalTypeDef",
    },
)
_OptionalCreatePrefetchScheduleRequestRequestTypeDef = TypedDict(
    "_OptionalCreatePrefetchScheduleRequestRequestTypeDef",
    {
        "StreamId": str,
    },
    total=False,
)


class CreatePrefetchScheduleRequestRequestTypeDef(
    _RequiredCreatePrefetchScheduleRequestRequestTypeDef,
    _OptionalCreatePrefetchScheduleRequestRequestTypeDef,
):
    pass


CreatePrefetchScheduleResponseTypeDef = TypedDict(
    "CreatePrefetchScheduleResponseTypeDef",
    {
        "Arn": str,
        "Consumption": "PrefetchConsumptionTypeDef",
        "Name": str,
        "PlaybackConfigurationName": str,
        "Retrieval": "PrefetchRetrievalTypeDef",
        "StreamId": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredCreateProgramRequestRequestTypeDef = TypedDict(
    "_RequiredCreateProgramRequestRequestTypeDef",
    {
        "ChannelName": str,
        "ProgramName": str,
        "ScheduleConfiguration": "ScheduleConfigurationTypeDef",
        "SourceLocationName": str,
        "VodSourceName": str,
    },
)
_OptionalCreateProgramRequestRequestTypeDef = TypedDict(
    "_OptionalCreateProgramRequestRequestTypeDef",
    {
        "AdBreaks": Sequence["AdBreakTypeDef"],
    },
    total=False,
)


class CreateProgramRequestRequestTypeDef(
    _RequiredCreateProgramRequestRequestTypeDef, _OptionalCreateProgramRequestRequestTypeDef
):
    pass


CreateProgramResponseTypeDef = TypedDict(
    "CreateProgramResponseTypeDef",
    {
        "AdBreaks": List["AdBreakTypeDef"],
        "Arn": str,
        "ChannelName": str,
        "CreationTime": datetime,
        "ProgramName": str,
        "ScheduledStartTime": datetime,
        "SourceLocationName": str,
        "VodSourceName": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredCreateSourceLocationRequestRequestTypeDef = TypedDict(
    "_RequiredCreateSourceLocationRequestRequestTypeDef",
    {
        "HttpConfiguration": "HttpConfigurationTypeDef",
        "SourceLocationName": str,
    },
)
_OptionalCreateSourceLocationRequestRequestTypeDef = TypedDict(
    "_OptionalCreateSourceLocationRequestRequestTypeDef",
    {
        "AccessConfiguration": "AccessConfigurationTypeDef",
        "DefaultSegmentDeliveryConfiguration": "DefaultSegmentDeliveryConfigurationTypeDef",
        "SegmentDeliveryConfigurations": Sequence["SegmentDeliveryConfigurationTypeDef"],
        "Tags": Mapping[str, str],
    },
    total=False,
)


class CreateSourceLocationRequestRequestTypeDef(
    _RequiredCreateSourceLocationRequestRequestTypeDef,
    _OptionalCreateSourceLocationRequestRequestTypeDef,
):
    pass


CreateSourceLocationResponseTypeDef = TypedDict(
    "CreateSourceLocationResponseTypeDef",
    {
        "AccessConfiguration": "AccessConfigurationTypeDef",
        "Arn": str,
        "CreationTime": datetime,
        "DefaultSegmentDeliveryConfiguration": "DefaultSegmentDeliveryConfigurationTypeDef",
        "HttpConfiguration": "HttpConfigurationTypeDef",
        "LastModifiedTime": datetime,
        "SegmentDeliveryConfigurations": List["SegmentDeliveryConfigurationTypeDef"],
        "SourceLocationName": str,
        "Tags": Dict[str, str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredCreateVodSourceRequestRequestTypeDef = TypedDict(
    "_RequiredCreateVodSourceRequestRequestTypeDef",
    {
        "HttpPackageConfigurations": Sequence["HttpPackageConfigurationTypeDef"],
        "SourceLocationName": str,
        "VodSourceName": str,
    },
)
_OptionalCreateVodSourceRequestRequestTypeDef = TypedDict(
    "_OptionalCreateVodSourceRequestRequestTypeDef",
    {
        "Tags": Mapping[str, str],
    },
    total=False,
)


class CreateVodSourceRequestRequestTypeDef(
    _RequiredCreateVodSourceRequestRequestTypeDef, _OptionalCreateVodSourceRequestRequestTypeDef
):
    pass


CreateVodSourceResponseTypeDef = TypedDict(
    "CreateVodSourceResponseTypeDef",
    {
        "Arn": str,
        "CreationTime": datetime,
        "HttpPackageConfigurations": List["HttpPackageConfigurationTypeDef"],
        "LastModifiedTime": datetime,
        "SourceLocationName": str,
        "Tags": Dict[str, str],
        "VodSourceName": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DashConfigurationForPutTypeDef = TypedDict(
    "DashConfigurationForPutTypeDef",
    {
        "MpdLocation": str,
        "OriginManifestType": OriginManifestTypeType,
    },
    total=False,
)

DashConfigurationTypeDef = TypedDict(
    "DashConfigurationTypeDef",
    {
        "ManifestEndpointPrefix": str,
        "MpdLocation": str,
        "OriginManifestType": OriginManifestTypeType,
    },
    total=False,
)

DashPlaylistSettingsTypeDef = TypedDict(
    "DashPlaylistSettingsTypeDef",
    {
        "ManifestWindowSeconds": int,
        "MinBufferTimeSeconds": int,
        "MinUpdatePeriodSeconds": int,
        "SuggestedPresentationDelaySeconds": int,
    },
    total=False,
)

DefaultSegmentDeliveryConfigurationTypeDef = TypedDict(
    "DefaultSegmentDeliveryConfigurationTypeDef",
    {
        "BaseUrl": str,
    },
    total=False,
)

DeleteChannelPolicyRequestRequestTypeDef = TypedDict(
    "DeleteChannelPolicyRequestRequestTypeDef",
    {
        "ChannelName": str,
    },
)

DeleteChannelRequestRequestTypeDef = TypedDict(
    "DeleteChannelRequestRequestTypeDef",
    {
        "ChannelName": str,
    },
)

DeletePlaybackConfigurationRequestRequestTypeDef = TypedDict(
    "DeletePlaybackConfigurationRequestRequestTypeDef",
    {
        "Name": str,
    },
)

DeletePrefetchScheduleRequestRequestTypeDef = TypedDict(
    "DeletePrefetchScheduleRequestRequestTypeDef",
    {
        "Name": str,
        "PlaybackConfigurationName": str,
    },
)

DeleteProgramRequestRequestTypeDef = TypedDict(
    "DeleteProgramRequestRequestTypeDef",
    {
        "ChannelName": str,
        "ProgramName": str,
    },
)

DeleteSourceLocationRequestRequestTypeDef = TypedDict(
    "DeleteSourceLocationRequestRequestTypeDef",
    {
        "SourceLocationName": str,
    },
)

DeleteVodSourceRequestRequestTypeDef = TypedDict(
    "DeleteVodSourceRequestRequestTypeDef",
    {
        "SourceLocationName": str,
        "VodSourceName": str,
    },
)

DescribeChannelRequestRequestTypeDef = TypedDict(
    "DescribeChannelRequestRequestTypeDef",
    {
        "ChannelName": str,
    },
)

DescribeChannelResponseTypeDef = TypedDict(
    "DescribeChannelResponseTypeDef",
    {
        "Arn": str,
        "ChannelName": str,
        "ChannelState": ChannelStateType,
        "CreationTime": datetime,
        "FillerSlate": "SlateSourceTypeDef",
        "LastModifiedTime": datetime,
        "Outputs": List["ResponseOutputItemTypeDef"],
        "PlaybackMode": str,
        "Tags": Dict[str, str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeProgramRequestRequestTypeDef = TypedDict(
    "DescribeProgramRequestRequestTypeDef",
    {
        "ChannelName": str,
        "ProgramName": str,
    },
)

DescribeProgramResponseTypeDef = TypedDict(
    "DescribeProgramResponseTypeDef",
    {
        "AdBreaks": List["AdBreakTypeDef"],
        "Arn": str,
        "ChannelName": str,
        "CreationTime": datetime,
        "ProgramName": str,
        "ScheduledStartTime": datetime,
        "SourceLocationName": str,
        "VodSourceName": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeSourceLocationRequestRequestTypeDef = TypedDict(
    "DescribeSourceLocationRequestRequestTypeDef",
    {
        "SourceLocationName": str,
    },
)

DescribeSourceLocationResponseTypeDef = TypedDict(
    "DescribeSourceLocationResponseTypeDef",
    {
        "AccessConfiguration": "AccessConfigurationTypeDef",
        "Arn": str,
        "CreationTime": datetime,
        "DefaultSegmentDeliveryConfiguration": "DefaultSegmentDeliveryConfigurationTypeDef",
        "HttpConfiguration": "HttpConfigurationTypeDef",
        "LastModifiedTime": datetime,
        "SegmentDeliveryConfigurations": List["SegmentDeliveryConfigurationTypeDef"],
        "SourceLocationName": str,
        "Tags": Dict[str, str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

DescribeVodSourceRequestRequestTypeDef = TypedDict(
    "DescribeVodSourceRequestRequestTypeDef",
    {
        "SourceLocationName": str,
        "VodSourceName": str,
    },
)

DescribeVodSourceResponseTypeDef = TypedDict(
    "DescribeVodSourceResponseTypeDef",
    {
        "Arn": str,
        "CreationTime": datetime,
        "HttpPackageConfigurations": List["HttpPackageConfigurationTypeDef"],
        "LastModifiedTime": datetime,
        "SourceLocationName": str,
        "Tags": Dict[str, str],
        "VodSourceName": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetChannelPolicyRequestRequestTypeDef = TypedDict(
    "GetChannelPolicyRequestRequestTypeDef",
    {
        "ChannelName": str,
    },
)

GetChannelPolicyResponseTypeDef = TypedDict(
    "GetChannelPolicyResponseTypeDef",
    {
        "Policy": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredGetChannelScheduleRequestRequestTypeDef = TypedDict(
    "_RequiredGetChannelScheduleRequestRequestTypeDef",
    {
        "ChannelName": str,
    },
)
_OptionalGetChannelScheduleRequestRequestTypeDef = TypedDict(
    "_OptionalGetChannelScheduleRequestRequestTypeDef",
    {
        "DurationMinutes": str,
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class GetChannelScheduleRequestRequestTypeDef(
    _RequiredGetChannelScheduleRequestRequestTypeDef,
    _OptionalGetChannelScheduleRequestRequestTypeDef,
):
    pass


GetChannelScheduleResponseTypeDef = TypedDict(
    "GetChannelScheduleResponseTypeDef",
    {
        "Items": List["ScheduleEntryTypeDef"],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetPlaybackConfigurationRequestRequestTypeDef = TypedDict(
    "GetPlaybackConfigurationRequestRequestTypeDef",
    {
        "Name": str,
    },
)

GetPlaybackConfigurationResponseTypeDef = TypedDict(
    "GetPlaybackConfigurationResponseTypeDef",
    {
        "AdDecisionServerUrl": str,
        "AvailSuppression": "AvailSuppressionTypeDef",
        "Bumper": "BumperTypeDef",
        "CdnConfiguration": "CdnConfigurationTypeDef",
        "ConfigurationAliases": Dict[str, Dict[str, str]],
        "DashConfiguration": "DashConfigurationTypeDef",
        "HlsConfiguration": "HlsConfigurationTypeDef",
        "LivePreRollConfiguration": "LivePreRollConfigurationTypeDef",
        "LogConfiguration": "LogConfigurationTypeDef",
        "ManifestProcessingRules": "ManifestProcessingRulesTypeDef",
        "Name": str,
        "PersonalizationThresholdSeconds": int,
        "PlaybackConfigurationArn": str,
        "PlaybackEndpointPrefix": str,
        "SessionInitializationEndpointPrefix": str,
        "SlateAdUrl": str,
        "Tags": Dict[str, str],
        "TranscodeProfileName": str,
        "VideoContentSourceUrl": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

GetPrefetchScheduleRequestRequestTypeDef = TypedDict(
    "GetPrefetchScheduleRequestRequestTypeDef",
    {
        "Name": str,
        "PlaybackConfigurationName": str,
    },
)

GetPrefetchScheduleResponseTypeDef = TypedDict(
    "GetPrefetchScheduleResponseTypeDef",
    {
        "Arn": str,
        "Consumption": "PrefetchConsumptionTypeDef",
        "Name": str,
        "PlaybackConfigurationName": str,
        "Retrieval": "PrefetchRetrievalTypeDef",
        "StreamId": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

HlsConfigurationTypeDef = TypedDict(
    "HlsConfigurationTypeDef",
    {
        "ManifestEndpointPrefix": str,
    },
    total=False,
)

HlsPlaylistSettingsTypeDef = TypedDict(
    "HlsPlaylistSettingsTypeDef",
    {
        "ManifestWindowSeconds": int,
    },
    total=False,
)

HttpConfigurationTypeDef = TypedDict(
    "HttpConfigurationTypeDef",
    {
        "BaseUrl": str,
    },
)

HttpPackageConfigurationTypeDef = TypedDict(
    "HttpPackageConfigurationTypeDef",
    {
        "Path": str,
        "SourceGroup": str,
        "Type": TypeType,
    },
)

_RequiredListAlertsRequestRequestTypeDef = TypedDict(
    "_RequiredListAlertsRequestRequestTypeDef",
    {
        "ResourceArn": str,
    },
)
_OptionalListAlertsRequestRequestTypeDef = TypedDict(
    "_OptionalListAlertsRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class ListAlertsRequestRequestTypeDef(
    _RequiredListAlertsRequestRequestTypeDef, _OptionalListAlertsRequestRequestTypeDef
):
    pass


ListAlertsResponseTypeDef = TypedDict(
    "ListAlertsResponseTypeDef",
    {
        "Items": List["AlertTypeDef"],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListChannelsRequestRequestTypeDef = TypedDict(
    "ListChannelsRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

ListChannelsResponseTypeDef = TypedDict(
    "ListChannelsResponseTypeDef",
    {
        "Items": List["ChannelTypeDef"],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListPlaybackConfigurationsRequestRequestTypeDef = TypedDict(
    "ListPlaybackConfigurationsRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

ListPlaybackConfigurationsResponseTypeDef = TypedDict(
    "ListPlaybackConfigurationsResponseTypeDef",
    {
        "Items": List["PlaybackConfigurationTypeDef"],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredListPrefetchSchedulesRequestRequestTypeDef = TypedDict(
    "_RequiredListPrefetchSchedulesRequestRequestTypeDef",
    {
        "PlaybackConfigurationName": str,
    },
)
_OptionalListPrefetchSchedulesRequestRequestTypeDef = TypedDict(
    "_OptionalListPrefetchSchedulesRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
        "StreamId": str,
    },
    total=False,
)


class ListPrefetchSchedulesRequestRequestTypeDef(
    _RequiredListPrefetchSchedulesRequestRequestTypeDef,
    _OptionalListPrefetchSchedulesRequestRequestTypeDef,
):
    pass


ListPrefetchSchedulesResponseTypeDef = TypedDict(
    "ListPrefetchSchedulesResponseTypeDef",
    {
        "Items": List["PrefetchScheduleTypeDef"],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListSourceLocationsRequestRequestTypeDef = TypedDict(
    "ListSourceLocationsRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)

ListSourceLocationsResponseTypeDef = TypedDict(
    "ListSourceLocationsResponseTypeDef",
    {
        "Items": List["SourceLocationTypeDef"],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "ResourceArn": str,
    },
)

ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "Tags": Dict[str, str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredListVodSourcesRequestRequestTypeDef = TypedDict(
    "_RequiredListVodSourcesRequestRequestTypeDef",
    {
        "SourceLocationName": str,
    },
)
_OptionalListVodSourcesRequestRequestTypeDef = TypedDict(
    "_OptionalListVodSourcesRequestRequestTypeDef",
    {
        "MaxResults": int,
        "NextToken": str,
    },
    total=False,
)


class ListVodSourcesRequestRequestTypeDef(
    _RequiredListVodSourcesRequestRequestTypeDef, _OptionalListVodSourcesRequestRequestTypeDef
):
    pass


ListVodSourcesResponseTypeDef = TypedDict(
    "ListVodSourcesResponseTypeDef",
    {
        "Items": List["VodSourceTypeDef"],
        "NextToken": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

LivePreRollConfigurationTypeDef = TypedDict(
    "LivePreRollConfigurationTypeDef",
    {
        "AdDecisionServerUrl": str,
        "MaxDurationSeconds": int,
    },
    total=False,
)

LogConfigurationTypeDef = TypedDict(
    "LogConfigurationTypeDef",
    {
        "PercentEnabled": int,
    },
)

ManifestProcessingRulesTypeDef = TypedDict(
    "ManifestProcessingRulesTypeDef",
    {
        "AdMarkerPassthrough": "AdMarkerPassthroughTypeDef",
    },
    total=False,
)

PaginatorConfigTypeDef = TypedDict(
    "PaginatorConfigTypeDef",
    {
        "MaxItems": int,
        "PageSize": int,
        "StartingToken": str,
    },
    total=False,
)

PlaybackConfigurationTypeDef = TypedDict(
    "PlaybackConfigurationTypeDef",
    {
        "AdDecisionServerUrl": str,
        "AvailSuppression": "AvailSuppressionTypeDef",
        "Bumper": "BumperTypeDef",
        "CdnConfiguration": "CdnConfigurationTypeDef",
        "ConfigurationAliases": Dict[str, Dict[str, str]],
        "DashConfiguration": "DashConfigurationTypeDef",
        "HlsConfiguration": "HlsConfigurationTypeDef",
        "LivePreRollConfiguration": "LivePreRollConfigurationTypeDef",
        "LogConfiguration": "LogConfigurationTypeDef",
        "ManifestProcessingRules": "ManifestProcessingRulesTypeDef",
        "Name": str,
        "PersonalizationThresholdSeconds": int,
        "PlaybackConfigurationArn": str,
        "PlaybackEndpointPrefix": str,
        "SessionInitializationEndpointPrefix": str,
        "SlateAdUrl": str,
        "Tags": Dict[str, str],
        "TranscodeProfileName": str,
        "VideoContentSourceUrl": str,
    },
    total=False,
)

_RequiredPrefetchConsumptionTypeDef = TypedDict(
    "_RequiredPrefetchConsumptionTypeDef",
    {
        "EndTime": Union[datetime, str],
    },
)
_OptionalPrefetchConsumptionTypeDef = TypedDict(
    "_OptionalPrefetchConsumptionTypeDef",
    {
        "AvailMatchingCriteria": Sequence["AvailMatchingCriteriaTypeDef"],
        "StartTime": Union[datetime, str],
    },
    total=False,
)


class PrefetchConsumptionTypeDef(
    _RequiredPrefetchConsumptionTypeDef, _OptionalPrefetchConsumptionTypeDef
):
    pass


_RequiredPrefetchRetrievalTypeDef = TypedDict(
    "_RequiredPrefetchRetrievalTypeDef",
    {
        "EndTime": Union[datetime, str],
    },
)
_OptionalPrefetchRetrievalTypeDef = TypedDict(
    "_OptionalPrefetchRetrievalTypeDef",
    {
        "DynamicVariables": Mapping[str, str],
        "StartTime": Union[datetime, str],
    },
    total=False,
)


class PrefetchRetrievalTypeDef(
    _RequiredPrefetchRetrievalTypeDef, _OptionalPrefetchRetrievalTypeDef
):
    pass


_RequiredPrefetchScheduleTypeDef = TypedDict(
    "_RequiredPrefetchScheduleTypeDef",
    {
        "Arn": str,
        "Consumption": "PrefetchConsumptionTypeDef",
        "Name": str,
        "PlaybackConfigurationName": str,
        "Retrieval": "PrefetchRetrievalTypeDef",
    },
)
_OptionalPrefetchScheduleTypeDef = TypedDict(
    "_OptionalPrefetchScheduleTypeDef",
    {
        "StreamId": str,
    },
    total=False,
)


class PrefetchScheduleTypeDef(_RequiredPrefetchScheduleTypeDef, _OptionalPrefetchScheduleTypeDef):
    pass


PutChannelPolicyRequestRequestTypeDef = TypedDict(
    "PutChannelPolicyRequestRequestTypeDef",
    {
        "ChannelName": str,
        "Policy": str,
    },
)

PutPlaybackConfigurationRequestRequestTypeDef = TypedDict(
    "PutPlaybackConfigurationRequestRequestTypeDef",
    {
        "AdDecisionServerUrl": str,
        "AvailSuppression": "AvailSuppressionTypeDef",
        "Bumper": "BumperTypeDef",
        "CdnConfiguration": "CdnConfigurationTypeDef",
        "ConfigurationAliases": Mapping[str, Mapping[str, str]],
        "DashConfiguration": "DashConfigurationForPutTypeDef",
        "LivePreRollConfiguration": "LivePreRollConfigurationTypeDef",
        "ManifestProcessingRules": "ManifestProcessingRulesTypeDef",
        "Name": str,
        "PersonalizationThresholdSeconds": int,
        "SlateAdUrl": str,
        "Tags": Mapping[str, str],
        "TranscodeProfileName": str,
        "VideoContentSourceUrl": str,
    },
    total=False,
)

PutPlaybackConfigurationResponseTypeDef = TypedDict(
    "PutPlaybackConfigurationResponseTypeDef",
    {
        "AdDecisionServerUrl": str,
        "AvailSuppression": "AvailSuppressionTypeDef",
        "Bumper": "BumperTypeDef",
        "CdnConfiguration": "CdnConfigurationTypeDef",
        "ConfigurationAliases": Dict[str, Dict[str, str]],
        "DashConfiguration": "DashConfigurationTypeDef",
        "HlsConfiguration": "HlsConfigurationTypeDef",
        "LivePreRollConfiguration": "LivePreRollConfigurationTypeDef",
        "LogConfiguration": "LogConfigurationTypeDef",
        "ManifestProcessingRules": "ManifestProcessingRulesTypeDef",
        "Name": str,
        "PersonalizationThresholdSeconds": int,
        "PlaybackConfigurationArn": str,
        "PlaybackEndpointPrefix": str,
        "SessionInitializationEndpointPrefix": str,
        "SlateAdUrl": str,
        "Tags": Dict[str, str],
        "TranscodeProfileName": str,
        "VideoContentSourceUrl": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredRequestOutputItemTypeDef = TypedDict(
    "_RequiredRequestOutputItemTypeDef",
    {
        "ManifestName": str,
        "SourceGroup": str,
    },
)
_OptionalRequestOutputItemTypeDef = TypedDict(
    "_OptionalRequestOutputItemTypeDef",
    {
        "DashPlaylistSettings": "DashPlaylistSettingsTypeDef",
        "HlsPlaylistSettings": "HlsPlaylistSettingsTypeDef",
    },
    total=False,
)


class RequestOutputItemTypeDef(
    _RequiredRequestOutputItemTypeDef, _OptionalRequestOutputItemTypeDef
):
    pass


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

_RequiredResponseOutputItemTypeDef = TypedDict(
    "_RequiredResponseOutputItemTypeDef",
    {
        "ManifestName": str,
        "PlaybackUrl": str,
        "SourceGroup": str,
    },
)
_OptionalResponseOutputItemTypeDef = TypedDict(
    "_OptionalResponseOutputItemTypeDef",
    {
        "DashPlaylistSettings": "DashPlaylistSettingsTypeDef",
        "HlsPlaylistSettings": "HlsPlaylistSettingsTypeDef",
    },
    total=False,
)


class ResponseOutputItemTypeDef(
    _RequiredResponseOutputItemTypeDef, _OptionalResponseOutputItemTypeDef
):
    pass


ScheduleAdBreakTypeDef = TypedDict(
    "ScheduleAdBreakTypeDef",
    {
        "ApproximateDurationSeconds": int,
        "ApproximateStartTime": datetime,
        "SourceLocationName": str,
        "VodSourceName": str,
    },
    total=False,
)

ScheduleConfigurationTypeDef = TypedDict(
    "ScheduleConfigurationTypeDef",
    {
        "Transition": "TransitionTypeDef",
    },
)

_RequiredScheduleEntryTypeDef = TypedDict(
    "_RequiredScheduleEntryTypeDef",
    {
        "Arn": str,
        "ChannelName": str,
        "ProgramName": str,
        "SourceLocationName": str,
        "VodSourceName": str,
    },
)
_OptionalScheduleEntryTypeDef = TypedDict(
    "_OptionalScheduleEntryTypeDef",
    {
        "ApproximateDurationSeconds": int,
        "ApproximateStartTime": datetime,
        "ScheduleAdBreaks": List["ScheduleAdBreakTypeDef"],
        "ScheduleEntryType": ScheduleEntryTypeType,
    },
    total=False,
)


class ScheduleEntryTypeDef(_RequiredScheduleEntryTypeDef, _OptionalScheduleEntryTypeDef):
    pass


SecretsManagerAccessTokenConfigurationTypeDef = TypedDict(
    "SecretsManagerAccessTokenConfigurationTypeDef",
    {
        "HeaderName": str,
        "SecretArn": str,
        "SecretStringKey": str,
    },
    total=False,
)

SegmentDeliveryConfigurationTypeDef = TypedDict(
    "SegmentDeliveryConfigurationTypeDef",
    {
        "BaseUrl": str,
        "Name": str,
    },
    total=False,
)

SlateSourceTypeDef = TypedDict(
    "SlateSourceTypeDef",
    {
        "SourceLocationName": str,
        "VodSourceName": str,
    },
    total=False,
)

_RequiredSourceLocationTypeDef = TypedDict(
    "_RequiredSourceLocationTypeDef",
    {
        "Arn": str,
        "HttpConfiguration": "HttpConfigurationTypeDef",
        "SourceLocationName": str,
    },
)
_OptionalSourceLocationTypeDef = TypedDict(
    "_OptionalSourceLocationTypeDef",
    {
        "AccessConfiguration": "AccessConfigurationTypeDef",
        "CreationTime": datetime,
        "DefaultSegmentDeliveryConfiguration": "DefaultSegmentDeliveryConfigurationTypeDef",
        "LastModifiedTime": datetime,
        "SegmentDeliveryConfigurations": List["SegmentDeliveryConfigurationTypeDef"],
        "Tags": Dict[str, str],
    },
    total=False,
)


class SourceLocationTypeDef(_RequiredSourceLocationTypeDef, _OptionalSourceLocationTypeDef):
    pass


SpliceInsertMessageTypeDef = TypedDict(
    "SpliceInsertMessageTypeDef",
    {
        "AvailNum": int,
        "AvailsExpected": int,
        "SpliceEventId": int,
        "UniqueProgramId": int,
    },
    total=False,
)

StartChannelRequestRequestTypeDef = TypedDict(
    "StartChannelRequestRequestTypeDef",
    {
        "ChannelName": str,
    },
)

StopChannelRequestRequestTypeDef = TypedDict(
    "StopChannelRequestRequestTypeDef",
    {
        "ChannelName": str,
    },
)

TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "ResourceArn": str,
        "Tags": Mapping[str, str],
    },
)

_RequiredTransitionTypeDef = TypedDict(
    "_RequiredTransitionTypeDef",
    {
        "RelativePosition": RelativePositionType,
        "Type": str,
    },
)
_OptionalTransitionTypeDef = TypedDict(
    "_OptionalTransitionTypeDef",
    {
        "RelativeProgram": str,
        "ScheduledStartTimeMillis": int,
    },
    total=False,
)


class TransitionTypeDef(_RequiredTransitionTypeDef, _OptionalTransitionTypeDef):
    pass


UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "ResourceArn": str,
        "TagKeys": Sequence[str],
    },
)

_RequiredUpdateChannelRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateChannelRequestRequestTypeDef",
    {
        "ChannelName": str,
        "Outputs": Sequence["RequestOutputItemTypeDef"],
    },
)
_OptionalUpdateChannelRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateChannelRequestRequestTypeDef",
    {
        "FillerSlate": "SlateSourceTypeDef",
    },
    total=False,
)


class UpdateChannelRequestRequestTypeDef(
    _RequiredUpdateChannelRequestRequestTypeDef, _OptionalUpdateChannelRequestRequestTypeDef
):
    pass


UpdateChannelResponseTypeDef = TypedDict(
    "UpdateChannelResponseTypeDef",
    {
        "Arn": str,
        "ChannelName": str,
        "ChannelState": ChannelStateType,
        "CreationTime": datetime,
        "FillerSlate": "SlateSourceTypeDef",
        "LastModifiedTime": datetime,
        "Outputs": List["ResponseOutputItemTypeDef"],
        "PlaybackMode": str,
        "Tags": Dict[str, str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredUpdateSourceLocationRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateSourceLocationRequestRequestTypeDef",
    {
        "HttpConfiguration": "HttpConfigurationTypeDef",
        "SourceLocationName": str,
    },
)
_OptionalUpdateSourceLocationRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateSourceLocationRequestRequestTypeDef",
    {
        "AccessConfiguration": "AccessConfigurationTypeDef",
        "DefaultSegmentDeliveryConfiguration": "DefaultSegmentDeliveryConfigurationTypeDef",
        "SegmentDeliveryConfigurations": Sequence["SegmentDeliveryConfigurationTypeDef"],
    },
    total=False,
)


class UpdateSourceLocationRequestRequestTypeDef(
    _RequiredUpdateSourceLocationRequestRequestTypeDef,
    _OptionalUpdateSourceLocationRequestRequestTypeDef,
):
    pass


UpdateSourceLocationResponseTypeDef = TypedDict(
    "UpdateSourceLocationResponseTypeDef",
    {
        "AccessConfiguration": "AccessConfigurationTypeDef",
        "Arn": str,
        "CreationTime": datetime,
        "DefaultSegmentDeliveryConfiguration": "DefaultSegmentDeliveryConfigurationTypeDef",
        "HttpConfiguration": "HttpConfigurationTypeDef",
        "LastModifiedTime": datetime,
        "SegmentDeliveryConfigurations": List["SegmentDeliveryConfigurationTypeDef"],
        "SourceLocationName": str,
        "Tags": Dict[str, str],
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

UpdateVodSourceRequestRequestTypeDef = TypedDict(
    "UpdateVodSourceRequestRequestTypeDef",
    {
        "HttpPackageConfigurations": Sequence["HttpPackageConfigurationTypeDef"],
        "SourceLocationName": str,
        "VodSourceName": str,
    },
)

UpdateVodSourceResponseTypeDef = TypedDict(
    "UpdateVodSourceResponseTypeDef",
    {
        "Arn": str,
        "CreationTime": datetime,
        "HttpPackageConfigurations": List["HttpPackageConfigurationTypeDef"],
        "LastModifiedTime": datetime,
        "SourceLocationName": str,
        "Tags": Dict[str, str],
        "VodSourceName": str,
        "ResponseMetadata": "ResponseMetadataTypeDef",
    },
)

_RequiredVodSourceTypeDef = TypedDict(
    "_RequiredVodSourceTypeDef",
    {
        "Arn": str,
        "HttpPackageConfigurations": List["HttpPackageConfigurationTypeDef"],
        "SourceLocationName": str,
        "VodSourceName": str,
    },
)
_OptionalVodSourceTypeDef = TypedDict(
    "_OptionalVodSourceTypeDef",
    {
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "Tags": Dict[str, str],
    },
    total=False,
)


class VodSourceTypeDef(_RequiredVodSourceTypeDef, _OptionalVodSourceTypeDef):
    pass
