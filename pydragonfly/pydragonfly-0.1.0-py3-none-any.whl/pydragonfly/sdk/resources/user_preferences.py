import dataclasses
from typing import List, Optional
from django_rest_client import (
    APIResource,
    APIResponse,
    SingletonAPIResourceMixin,
)
from django_rest_client.mixins import UpdateableAPIResourceMixin
from django_rest_client.types import Toid, TParams


@dataclasses.dataclass
class UpdateUserPreferencesRequestBody:
    apistructure_ignore_list: List[str]


class UserPreferences(
    APIResource,
    UpdateableAPIResourceMixin,
    SingletonAPIResourceMixin,
):
    """
    :class:`pydragonfly.Dragonfly.UserPreferences`

    .. versionadded:: 0.0.2
    """

    OBJECT_NAME = "api.me.preferences"
    EXPANDABLE_FIELDS = {
        "retrieve": [],
        "list": [],
    }
    ORDERING_FIELDS = []

    # models
    UpdateUserPreferencesRequestBody = UpdateUserPreferencesRequestBody

    @classmethod
    def update(
        cls,
        object_id: Toid,
        data: UpdateUserPreferencesRequestBody,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        post_data = dataclasses.asdict(data)
        return super().update(object_id=object_id, data=post_data, params=params)
