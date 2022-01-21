from typing import Optional

from django_rest_client import (
    APIResponse,
    APIResource,
    RetrievableAPIResourceMixin,
    ListableAPIResourceMixin,
    PaginationAPIResourceMixin,
)
from django_rest_client.types import Toid, TParams


class Report(
    APIResource,
    RetrievableAPIResourceMixin,
    ListableAPIResourceMixin,
    PaginationAPIResourceMixin,
):
    """
    :class:`pydragonfly.Dragonfly.Report`
    """

    OBJECT_NAME = "api.report"
    EXPANDABLE_FIELDS = {
        "retrieve": ["profile", "analysis", "structs_count"],
        "list": ["profile", "analysis", "structs_count"],
    }
    ORDERING_FIELDS = [
        "time__start_analysis",
        "analysis__sample__filename",
        "weight",
    ]

    @classmethod
    def timeline(
        cls,
        object_id: Toid,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        url = cls.instance_url(object_id) + "/timeline"
        return cls._request("GET", url=url, params=params)

    @classmethod
    def matched_rules(
        cls,
        object_id: Toid,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        url = cls.instance_url(object_id) + "/matched-rules"
        return cls._request("GET", url=url, params=params)

    @classmethod
    def revoke(
        cls,
        object_id: Toid,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        url = cls.instance_url(object_id) + "/revoke"
        return cls._request("POST", url=url, params=params)
