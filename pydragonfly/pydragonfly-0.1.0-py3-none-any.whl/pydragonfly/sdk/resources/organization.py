from typing import Optional
import dataclasses
from django_rest_client import (
    APIResource,
    APIResponse,
    CreateableAPIResourceMixin,
    SingletonAPIResourceMixin,
)
from django_rest_client.types import TParams


@dataclasses.dataclass
class CreateOrgRequestBody:
    name: str


@dataclasses.dataclass
class InviteRequestBody:
    username: str


@dataclasses.dataclass
class RemoveMemberRequestBody:
    username: str


class Organization(
    APIResource,
    SingletonAPIResourceMixin,
    CreateableAPIResourceMixin,
):
    """
    :class:`pydragonfly.Dragonfly.Organization`

    Note: ``delete`` and ``leave`` methods are
    intentionally not provided to avoid accidents.
    Please use the GUI for those operations.
    """

    OBJECT_NAME = "api.me.organization"
    EXPANDABLE_FIELDS = {
        "retrieve": ["members", "pending_invitations"],
        "list": ["members", "pending_invitations"],
    }
    ORDERING_FIELDS = []

    # models
    CreateOrgRequestBody = CreateOrgRequestBody
    InviteRequestBody = InviteRequestBody
    RemoveMemberRequestBody = RemoveMemberRequestBody

    @classmethod
    def create(
        cls,
        data: CreateOrgRequestBody,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        post_data = dataclasses.asdict(data)
        return super().create(data=post_data, params=params)

    @classmethod
    def invite(
        cls,
        data: InviteRequestBody,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        url = cls.class_url() + "/invite"
        return cls._request(
            "POST", url=url, json=dataclasses.asdict(data), params=params
        )

    @classmethod
    def remove_member(
        cls,
        data: RemoveMemberRequestBody,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        url = cls.class_url() + "/remove_member"
        return cls._request(
            "POST", url=url, json=dataclasses.asdict(data), params=params
        )
