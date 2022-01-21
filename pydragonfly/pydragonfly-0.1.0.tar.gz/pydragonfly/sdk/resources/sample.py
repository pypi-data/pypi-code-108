from typing import Optional

from django_rest_client import (
    APIResponse,
    APIResource,
    RetrievableAPIResourceMixin,
)
from django_rest_client.types import Toid, TParams


class Sample(
    APIResource,
    RetrievableAPIResourceMixin,
):
    """
    :class:`pydragonfly.Dragonfly.Sample`
    """

    OBJECT_NAME = "api.sample"
    EXPANDABLE_FIELDS = {
        "retrieve": ["user", "analysis"],
        "list": [],
    }
    ORDERING_FIELDS = []

    @classmethod
    def download(
        cls,
        object_id: Toid,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        url = cls.instance_url(object_id) + "/download"
        return cls._request("GET", url=url, params=params)
