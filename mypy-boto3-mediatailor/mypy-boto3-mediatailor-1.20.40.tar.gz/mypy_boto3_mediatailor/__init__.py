"""
Main interface for mediatailor service.

Usage::

    ```python
    import boto3
    from mypy_boto3_mediatailor import (
        Client,
        GetChannelSchedulePaginator,
        ListAlertsPaginator,
        ListChannelsPaginator,
        ListPlaybackConfigurationsPaginator,
        ListPrefetchSchedulesPaginator,
        ListSourceLocationsPaginator,
        ListVodSourcesPaginator,
        MediaTailorClient,
    )

    session = boto3.Session()

    client: MediaTailorClient = boto3.client("mediatailor")
    session_client: MediaTailorClient = session.client("mediatailor")

    get_channel_schedule_paginator: GetChannelSchedulePaginator = client.get_paginator("get_channel_schedule")
    list_alerts_paginator: ListAlertsPaginator = client.get_paginator("list_alerts")
    list_channels_paginator: ListChannelsPaginator = client.get_paginator("list_channels")
    list_playback_configurations_paginator: ListPlaybackConfigurationsPaginator = client.get_paginator("list_playback_configurations")
    list_prefetch_schedules_paginator: ListPrefetchSchedulesPaginator = client.get_paginator("list_prefetch_schedules")
    list_source_locations_paginator: ListSourceLocationsPaginator = client.get_paginator("list_source_locations")
    list_vod_sources_paginator: ListVodSourcesPaginator = client.get_paginator("list_vod_sources")
    ```
"""
from .client import MediaTailorClient
from .paginator import (
    GetChannelSchedulePaginator,
    ListAlertsPaginator,
    ListChannelsPaginator,
    ListPlaybackConfigurationsPaginator,
    ListPrefetchSchedulesPaginator,
    ListSourceLocationsPaginator,
    ListVodSourcesPaginator,
)

Client = MediaTailorClient


__all__ = (
    "Client",
    "GetChannelSchedulePaginator",
    "ListAlertsPaginator",
    "ListChannelsPaginator",
    "ListPlaybackConfigurationsPaginator",
    "ListPrefetchSchedulesPaginator",
    "ListSourceLocationsPaginator",
    "ListVodSourcesPaginator",
    "MediaTailorClient",
)
