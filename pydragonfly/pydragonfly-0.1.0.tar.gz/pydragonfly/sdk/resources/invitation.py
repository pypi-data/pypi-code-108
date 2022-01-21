from typing import Optional

from django_rest_client import (
    APIResource,
    APIResponse,
    ListableAPIResourceMixin,
    DeletableAPIResourceMixin,
)
from django_rest_client.types import Toid, TParams


class Invitation(
    APIResource,
    ListableAPIResourceMixin,
    DeletableAPIResourceMixin,
):
    """
    :class:`pydragonfly.Dragonfly.Invitation`
    """

    OBJECT_NAME = "api.me.invitations"
    EXPANDABLE_FIELDS = {
        "retrieve": [],
        "list": [],
    }
    ORDERING_FIELDS = []

    @classmethod
    def accept(
        cls,
        object_id: Toid,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        url = cls.instance_url(object_id) + "/accept"
        return cls._request("POST", url=url, params=params)

    @classmethod
    def decline(
        cls,
        object_id: Toid,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        url = cls.instance_url(object_id) + "/decline"
        return cls._request("POST", url=url, params=params)
