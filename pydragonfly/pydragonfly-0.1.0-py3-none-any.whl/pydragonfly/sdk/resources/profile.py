import base64
import dataclasses
from typing import Optional
from typing_extensions import Literal
from django_rest_client import (
    APIResource,
    APIResponse,
    RetrievableAPIResourceMixin,
    ListableAPIResourceMixin,
    CreateableAPIResourceMixin,
    UpdateableAPIResourceMixin,
    PaginationAPIResourceMixin,
)
from django_rest_client.types import Toid, TParams


@dataclasses.dataclass
class CreateProfileRequestBody:
    filename: str
    emulator: Literal["qiling", "speakeasy"]
    content: bytes


@dataclasses.dataclass
class UpdateProfileRequestBody:
    enabled: bool


class Profile(
    APIResource,
    RetrievableAPIResourceMixin,
    ListableAPIResourceMixin,
    CreateableAPIResourceMixin,
    UpdateableAPIResourceMixin,
    PaginationAPIResourceMixin,
):
    """
    :class:`pydragonfly.Dragonfly.Profile`
    """

    OBJECT_NAME = "api.profile"
    EXPANDABLE_FIELDS = {
        "retrieve": ["user", "permissions"],
        "list": ["user", "permissions"],
    }
    ORDERING_FIELDS = [
        "id",
        "filename",
        "created_at",
    ]

    # models
    CreateProfileRequestBody = CreateProfileRequestBody
    UpdateProfileRequestBody = UpdateProfileRequestBody

    @classmethod
    def create(
        cls,
        data: CreateProfileRequestBody,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        post_data = {
            "filename": data.filename,
            "emulator": data.emulator,
            "file_buffer_b64": base64.b64encode(data.content),
        }
        return super().create(data=post_data, params=params)

    @classmethod
    def update(
        cls,
        object_id: Toid,
        data: UpdateProfileRequestBody,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        post_data = {
            "enabled": data.enabled,
        }
        return super().update(object_id=object_id, data=post_data, params=params)
