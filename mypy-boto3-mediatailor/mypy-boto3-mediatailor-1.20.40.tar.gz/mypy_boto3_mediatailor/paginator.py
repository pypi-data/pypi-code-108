"""
Type annotations for mediatailor service client paginators.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/paginators.html)

Usage::

    ```python
    import boto3

    from mypy_boto3_mediatailor import MediaTailorClient
    from mypy_boto3_mediatailor.paginator import (
        GetChannelSchedulePaginator,
        ListAlertsPaginator,
        ListChannelsPaginator,
        ListPlaybackConfigurationsPaginator,
        ListPrefetchSchedulesPaginator,
        ListSourceLocationsPaginator,
        ListVodSourcesPaginator,
    )

    client: MediaTailorClient = boto3.client("mediatailor")

    get_channel_schedule_paginator: GetChannelSchedulePaginator = client.get_paginator("get_channel_schedule")
    list_alerts_paginator: ListAlertsPaginator = client.get_paginator("list_alerts")
    list_channels_paginator: ListChannelsPaginator = client.get_paginator("list_channels")
    list_playback_configurations_paginator: ListPlaybackConfigurationsPaginator = client.get_paginator("list_playback_configurations")
    list_prefetch_schedules_paginator: ListPrefetchSchedulesPaginator = client.get_paginator("list_prefetch_schedules")
    list_source_locations_paginator: ListSourceLocationsPaginator = client.get_paginator("list_source_locations")
    list_vod_sources_paginator: ListVodSourcesPaginator = client.get_paginator("list_vod_sources")
    ```
"""
from typing import Generic, Iterator, TypeVar

from botocore.paginate import PageIterator
from botocore.paginate import Paginator as Boto3Paginator

from .type_defs import (
    GetChannelScheduleResponseTypeDef,
    ListAlertsResponseTypeDef,
    ListChannelsResponseTypeDef,
    ListPlaybackConfigurationsResponseTypeDef,
    ListPrefetchSchedulesResponseTypeDef,
    ListSourceLocationsResponseTypeDef,
    ListVodSourcesResponseTypeDef,
    PaginatorConfigTypeDef,
)

__all__ = (
    "GetChannelSchedulePaginator",
    "ListAlertsPaginator",
    "ListChannelsPaginator",
    "ListPlaybackConfigurationsPaginator",
    "ListPrefetchSchedulesPaginator",
    "ListSourceLocationsPaginator",
    "ListVodSourcesPaginator",
)


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class GetChannelSchedulePaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Paginator.GetChannelSchedule)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/paginators.html#getchannelschedulepaginator)
    """

    def paginate(
        self,
        *,
        ChannelName: str,
        DurationMinutes: str = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[GetChannelScheduleResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Paginator.GetChannelSchedule.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/paginators.html#getchannelschedulepaginator)
        """


class ListAlertsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Paginator.ListAlerts)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/paginators.html#listalertspaginator)
    """

    def paginate(
        self, *, ResourceArn: str, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListAlertsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Paginator.ListAlerts.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/paginators.html#listalertspaginator)
        """


class ListChannelsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Paginator.ListChannels)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/paginators.html#listchannelspaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListChannelsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Paginator.ListChannels.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/paginators.html#listchannelspaginator)
        """


class ListPlaybackConfigurationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Paginator.ListPlaybackConfigurations)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/paginators.html#listplaybackconfigurationspaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListPlaybackConfigurationsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Paginator.ListPlaybackConfigurations.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/paginators.html#listplaybackconfigurationspaginator)
        """


class ListPrefetchSchedulesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Paginator.ListPrefetchSchedules)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/paginators.html#listprefetchschedulespaginator)
    """

    def paginate(
        self,
        *,
        PlaybackConfigurationName: str,
        StreamId: str = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListPrefetchSchedulesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Paginator.ListPrefetchSchedules.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/paginators.html#listprefetchschedulespaginator)
        """


class ListSourceLocationsPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Paginator.ListSourceLocations)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/paginators.html#listsourcelocationspaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListSourceLocationsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Paginator.ListSourceLocations.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/paginators.html#listsourcelocationspaginator)
        """


class ListVodSourcesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Paginator.ListVodSources)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/paginators.html#listvodsourcespaginator)
    """

    def paginate(
        self, *, SourceLocationName: str, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListVodSourcesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.40/reference/services/mediatailor.html#MediaTailor.Paginator.ListVodSources.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_mediatailor/paginators.html#listvodsourcespaginator)
        """
