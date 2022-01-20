"""
Type annotations for mediatailor service client.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html)

Usage::

    ```python
    import boto3
    from mypy_boto3_mediatailor import MediaTailorClient

    client: MediaTailorClient = boto3.client("mediatailor")
    ```
"""
import sys
from typing import Any, Dict, Mapping, Sequence, Type, overload

from botocore.client import BaseClient, ClientMeta

from .literals import PlaybackModeType
from .paginator import (
    GetChannelSchedulePaginator,
    ListAlertsPaginator,
    ListChannelsPaginator,
    ListPlaybackConfigurationsPaginator,
    ListPrefetchSchedulesPaginator,
    ListSourceLocationsPaginator,
    ListVodSourcesPaginator,
)
from .type_defs import (
    AccessConfigurationTypeDef,
    AdBreakTypeDef,
    AvailSuppressionTypeDef,
    BumperTypeDef,
    CdnConfigurationTypeDef,
    ConfigureLogsForPlaybackConfigurationResponseTypeDef,
    CreateChannelResponseTypeDef,
    CreatePrefetchScheduleResponseTypeDef,
    CreateProgramResponseTypeDef,
    CreateSourceLocationResponseTypeDef,
    CreateVodSourceResponseTypeDef,
    DashConfigurationForPutTypeDef,
    DefaultSegmentDeliveryConfigurationTypeDef,
    DescribeChannelResponseTypeDef,
    DescribeProgramResponseTypeDef,
    DescribeSourceLocationResponseTypeDef,
    DescribeVodSourceResponseTypeDef,
    GetChannelPolicyResponseTypeDef,
    GetChannelScheduleResponseTypeDef,
    GetPlaybackConfigurationResponseTypeDef,
    GetPrefetchScheduleResponseTypeDef,
    HttpConfigurationTypeDef,
    HttpPackageConfigurationTypeDef,
    ListAlertsResponseTypeDef,
    ListChannelsResponseTypeDef,
    ListPlaybackConfigurationsResponseTypeDef,
    ListPrefetchSchedulesResponseTypeDef,
    ListSourceLocationsResponseTypeDef,
    ListTagsForResourceResponseTypeDef,
    ListVodSourcesResponseTypeDef,
    LivePreRollConfigurationTypeDef,
    ManifestProcessingRulesTypeDef,
    PrefetchConsumptionTypeDef,
    PrefetchRetrievalTypeDef,
    PutPlaybackConfigurationResponseTypeDef,
    RequestOutputItemTypeDef,
    ScheduleConfigurationTypeDef,
    SegmentDeliveryConfigurationTypeDef,
    SlateSourceTypeDef,
    UpdateChannelResponseTypeDef,
    UpdateSourceLocationResponseTypeDef,
    UpdateVodSourceResponseTypeDef,
)

if sys.version_info >= (3, 9):
    from typing import Literal
else:
    from typing_extensions import Literal


__all__ = ("MediaTailorClient",)


class BotocoreClientError(BaseException):
    MSG_TEMPLATE: str

    def __init__(self, error_response: Mapping[str, Any], operation_name: str) -> None:
        self.response: Dict[str, Any]
        self.operation_name: str


class Exceptions:
    BadRequestException: Type[BotocoreClientError]
    ClientError: Type[BotocoreClientError]


class MediaTailorClient(BaseClient):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html)
    """

    meta: ClientMeta

    @property
    def exceptions(self) -> Exceptions:
        """
        MediaTailorClient exceptions.
        """

    def can_paginate(self, operation_name: str) -> bool:
        """
        Check if an operation can be paginated.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.can_paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#can_paginate)
        """

    def configure_logs_for_playback_configuration(
        self, *, PercentEnabled: int, PlaybackConfigurationName: str
    ) -> ConfigureLogsForPlaybackConfigurationResponseTypeDef:
        """
        Configures Amazon CloudWatch log settings for a playback configuration.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.configure_logs_for_playback_configuration)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#configure_logs_for_playback_configuration)
        """

    def create_channel(
        self,
        *,
        ChannelName: str,
        Outputs: Sequence["RequestOutputItemTypeDef"],
        PlaybackMode: PlaybackModeType,
        FillerSlate: "SlateSourceTypeDef" = ...,
        Tags: Mapping[str, str] = ...
    ) -> CreateChannelResponseTypeDef:
        """
        Creates a channel.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.create_channel)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#create_channel)
        """

    def create_prefetch_schedule(
        self,
        *,
        Consumption: "PrefetchConsumptionTypeDef",
        Name: str,
        PlaybackConfigurationName: str,
        Retrieval: "PrefetchRetrievalTypeDef",
        StreamId: str = ...
    ) -> CreatePrefetchScheduleResponseTypeDef:
        """
        Creates a new prefetch schedule for the specified playback configuration.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.create_prefetch_schedule)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#create_prefetch_schedule)
        """

    def create_program(
        self,
        *,
        ChannelName: str,
        ProgramName: str,
        ScheduleConfiguration: "ScheduleConfigurationTypeDef",
        SourceLocationName: str,
        VodSourceName: str,
        AdBreaks: Sequence["AdBreakTypeDef"] = ...
    ) -> CreateProgramResponseTypeDef:
        """
        Creates a program.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.create_program)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#create_program)
        """

    def create_source_location(
        self,
        *,
        HttpConfiguration: "HttpConfigurationTypeDef",
        SourceLocationName: str,
        AccessConfiguration: "AccessConfigurationTypeDef" = ...,
        DefaultSegmentDeliveryConfiguration: "DefaultSegmentDeliveryConfigurationTypeDef" = ...,
        SegmentDeliveryConfigurations: Sequence["SegmentDeliveryConfigurationTypeDef"] = ...,
        Tags: Mapping[str, str] = ...
    ) -> CreateSourceLocationResponseTypeDef:
        """
        Creates a source location on a specific channel.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.create_source_location)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#create_source_location)
        """

    def create_vod_source(
        self,
        *,
        HttpPackageConfigurations: Sequence["HttpPackageConfigurationTypeDef"],
        SourceLocationName: str,
        VodSourceName: str,
        Tags: Mapping[str, str] = ...
    ) -> CreateVodSourceResponseTypeDef:
        """
        Creates name for a specific VOD source in a source location.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.create_vod_source)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#create_vod_source)
        """

    def delete_channel(self, *, ChannelName: str) -> Dict[str, Any]:
        """
        Deletes a channel.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.delete_channel)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#delete_channel)
        """

    def delete_channel_policy(self, *, ChannelName: str) -> Dict[str, Any]:
        """
        Deletes a channel's IAM policy.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.delete_channel_policy)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#delete_channel_policy)
        """

    def delete_playback_configuration(self, *, Name: str) -> Dict[str, Any]:
        """
        Deletes the playback configuration for the specified name.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.delete_playback_configuration)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#delete_playback_configuration)
        """

    def delete_prefetch_schedule(
        self, *, Name: str, PlaybackConfigurationName: str
    ) -> Dict[str, Any]:
        """
        Deletes a prefetch schedule for a specific playback configuration.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.delete_prefetch_schedule)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#delete_prefetch_schedule)
        """

    def delete_program(self, *, ChannelName: str, ProgramName: str) -> Dict[str, Any]:
        """
        Deletes a specific program on a specific channel.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.delete_program)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#delete_program)
        """

    def delete_source_location(self, *, SourceLocationName: str) -> Dict[str, Any]:
        """
        Deletes a source location on a specific channel.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.delete_source_location)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#delete_source_location)
        """

    def delete_vod_source(self, *, SourceLocationName: str, VodSourceName: str) -> Dict[str, Any]:
        """
        Deletes a specific VOD source in a specific source location.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.delete_vod_source)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#delete_vod_source)
        """

    def describe_channel(self, *, ChannelName: str) -> DescribeChannelResponseTypeDef:
        """
        Describes the properties of a specific channel.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.describe_channel)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#describe_channel)
        """

    def describe_program(
        self, *, ChannelName: str, ProgramName: str
    ) -> DescribeProgramResponseTypeDef:
        """
        Retrieves the properties of the requested program.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.describe_program)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#describe_program)
        """

    def describe_source_location(
        self, *, SourceLocationName: str
    ) -> DescribeSourceLocationResponseTypeDef:
        """
        Retrieves the properties of the requested source location.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.describe_source_location)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#describe_source_location)
        """

    def describe_vod_source(
        self, *, SourceLocationName: str, VodSourceName: str
    ) -> DescribeVodSourceResponseTypeDef:
        """
        Provides details about a specific VOD source in a specific source location.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.describe_vod_source)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#describe_vod_source)
        """

    def generate_presigned_url(
        self,
        ClientMethod: str,
        Params: Mapping[str, Any] = ...,
        ExpiresIn: int = 3600,
        HttpMethod: str = ...,
    ) -> str:
        """
        Generate a presigned url given a client, its method, and arguments.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.generate_presigned_url)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#generate_presigned_url)
        """

    def get_channel_policy(self, *, ChannelName: str) -> GetChannelPolicyResponseTypeDef:
        """
        Retrieves information about a channel's IAM policy.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.get_channel_policy)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#get_channel_policy)
        """

    def get_channel_schedule(
        self,
        *,
        ChannelName: str,
        DurationMinutes: str = ...,
        MaxResults: int = ...,
        NextToken: str = ...
    ) -> GetChannelScheduleResponseTypeDef:
        """
        Retrieves information about your channel's schedule.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.get_channel_schedule)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#get_channel_schedule)
        """

    def get_playback_configuration(self, *, Name: str) -> GetPlaybackConfigurationResponseTypeDef:
        """
        Returns the playback configuration for the specified name.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.get_playback_configuration)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#get_playback_configuration)
        """

    def get_prefetch_schedule(
        self, *, Name: str, PlaybackConfigurationName: str
    ) -> GetPrefetchScheduleResponseTypeDef:
        """
        Returns information about the prefetch schedule for a specific playback
        configuration.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.get_prefetch_schedule)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#get_prefetch_schedule)
        """

    def list_alerts(
        self, *, ResourceArn: str, MaxResults: int = ..., NextToken: str = ...
    ) -> ListAlertsResponseTypeDef:
        """
        Returns a list of alerts for the given resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.list_alerts)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#list_alerts)
        """

    def list_channels(
        self, *, MaxResults: int = ..., NextToken: str = ...
    ) -> ListChannelsResponseTypeDef:
        """
        Retrieves a list of channels that are associated with this account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.list_channels)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#list_channels)
        """

    def list_playback_configurations(
        self, *, MaxResults: int = ..., NextToken: str = ...
    ) -> ListPlaybackConfigurationsResponseTypeDef:
        """
        Returns a list of the playback configurations defined in AWS Elemental
        MediaTailor.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.list_playback_configurations)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#list_playback_configurations)
        """

    def list_prefetch_schedules(
        self,
        *,
        PlaybackConfigurationName: str,
        MaxResults: int = ...,
        NextToken: str = ...,
        StreamId: str = ...
    ) -> ListPrefetchSchedulesResponseTypeDef:
        """
        Creates a new prefetch schedule.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.list_prefetch_schedules)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#list_prefetch_schedules)
        """

    def list_source_locations(
        self, *, MaxResults: int = ..., NextToken: str = ...
    ) -> ListSourceLocationsResponseTypeDef:
        """
        Retrieves a list of source locations.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.list_source_locations)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#list_source_locations)
        """

    def list_tags_for_resource(self, *, ResourceArn: str) -> ListTagsForResourceResponseTypeDef:
        """
        Returns a list of the tags assigned to the specified playback configuration
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.list_tags_for_resource)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#list_tags_for_resource)
        """

    def list_vod_sources(
        self, *, SourceLocationName: str, MaxResults: int = ..., NextToken: str = ...
    ) -> ListVodSourcesResponseTypeDef:
        """
        Lists all the VOD sources in a source location.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.list_vod_sources)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#list_vod_sources)
        """

    def put_channel_policy(self, *, ChannelName: str, Policy: str) -> Dict[str, Any]:
        """
        Creates an IAM policy for the channel.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.put_channel_policy)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#put_channel_policy)
        """

    def put_playback_configuration(
        self,
        *,
        AdDecisionServerUrl: str = ...,
        AvailSuppression: "AvailSuppressionTypeDef" = ...,
        Bumper: "BumperTypeDef" = ...,
        CdnConfiguration: "CdnConfigurationTypeDef" = ...,
        ConfigurationAliases: Mapping[str, Mapping[str, str]] = ...,
        DashConfiguration: "DashConfigurationForPutTypeDef" = ...,
        LivePreRollConfiguration: "LivePreRollConfigurationTypeDef" = ...,
        ManifestProcessingRules: "ManifestProcessingRulesTypeDef" = ...,
        Name: str = ...,
        PersonalizationThresholdSeconds: int = ...,
        SlateAdUrl: str = ...,
        Tags: Mapping[str, str] = ...,
        TranscodeProfileName: str = ...,
        VideoContentSourceUrl: str = ...
    ) -> PutPlaybackConfigurationResponseTypeDef:
        """
        Adds a new playback configuration to AWS Elemental MediaTailor.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.put_playback_configuration)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#put_playback_configuration)
        """

    def start_channel(self, *, ChannelName: str) -> Dict[str, Any]:
        """
        Starts a specific channel.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.start_channel)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#start_channel)
        """

    def stop_channel(self, *, ChannelName: str) -> Dict[str, Any]:
        """
        Stops a specific channel.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.stop_channel)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#stop_channel)
        """

    def tag_resource(self, *, ResourceArn: str, Tags: Mapping[str, str]) -> None:
        """
        Adds tags to the specified playback configuration resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.tag_resource)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#tag_resource)
        """

    def untag_resource(self, *, ResourceArn: str, TagKeys: Sequence[str]) -> None:
        """
        Removes tags from the specified playback configuration resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.untag_resource)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#untag_resource)
        """

    def update_channel(
        self,
        *,
        ChannelName: str,
        Outputs: Sequence["RequestOutputItemTypeDef"],
        FillerSlate: "SlateSourceTypeDef" = ...
    ) -> UpdateChannelResponseTypeDef:
        """
        Updates an existing channel.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.update_channel)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#update_channel)
        """

    def update_source_location(
        self,
        *,
        HttpConfiguration: "HttpConfigurationTypeDef",
        SourceLocationName: str,
        AccessConfiguration: "AccessConfigurationTypeDef" = ...,
        DefaultSegmentDeliveryConfiguration: "DefaultSegmentDeliveryConfigurationTypeDef" = ...,
        SegmentDeliveryConfigurations: Sequence["SegmentDeliveryConfigurationTypeDef"] = ...
    ) -> UpdateSourceLocationResponseTypeDef:
        """
        Updates a source location on a specific channel.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.update_source_location)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#update_source_location)
        """

    def update_vod_source(
        self,
        *,
        HttpPackageConfigurations: Sequence["HttpPackageConfigurationTypeDef"],
        SourceLocationName: str,
        VodSourceName: str
    ) -> UpdateVodSourceResponseTypeDef:
        """
        Updates a specific VOD source in a specific source location.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Client.update_vod_source)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/client.html#update_vod_source)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["get_channel_schedule"]
    ) -> GetChannelSchedulePaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Paginator.GetChannelSchedule)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/paginators.html#getchannelschedulepaginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_alerts"]) -> ListAlertsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Paginator.ListAlerts)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/paginators.html#listalertspaginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_channels"]) -> ListChannelsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Paginator.ListChannels)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/paginators.html#listchannelspaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_playback_configurations"]
    ) -> ListPlaybackConfigurationsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Paginator.ListPlaybackConfigurations)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/paginators.html#listplaybackconfigurationspaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_prefetch_schedules"]
    ) -> ListPrefetchSchedulesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Paginator.ListPrefetchSchedules)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/paginators.html#listprefetchschedulespaginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_source_locations"]
    ) -> ListSourceLocationsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Paginator.ListSourceLocations)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/paginators.html#listsourcelocationspaginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_vod_sources"]) -> ListVodSourcesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Paginator.ListVodSources)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/paginators.html#listvodsourcespaginator)
        """
