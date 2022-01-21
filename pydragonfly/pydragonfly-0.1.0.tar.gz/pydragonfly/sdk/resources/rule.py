import dataclasses
from typing import List, Optional

from django_rest_client import (
    APIResource,
    APIResponse,
    CreateableAPIResourceMixin,
    ListableAPIResourceMixin,
    PaginationAPIResourceMixin,
    RetrievableAPIResourceMixin,
    UpdateableAPIResourceMixin,
)
from django_rest_client.types import Toid, TParams


@dataclasses.dataclass
class CreateRuleRequestBody:
    rule: str
    weight: int
    modules: dict
    variables: List[str] = dataclasses.field(default_factory=list)
    malware_family: str = ""
    mitre_technique: str = None
    meta_description: dict = dataclasses.field(default_factory=dict)
    sensitive: bool = False


@dataclasses.dataclass
class UpdateRuleRequestBody:
    enabled: bool


class Rule(
    APIResource,
    RetrievableAPIResourceMixin,
    ListableAPIResourceMixin,
    CreateableAPIResourceMixin,
    UpdateableAPIResourceMixin,
    PaginationAPIResourceMixin,
):
    """
    :class:`pydragonfly.Dragonfly.Rule`
    """

    OBJECT_NAME = "api.rule"
    EXPANDABLE_FIELDS = {
        "retrieve": ["user", "actions", "clause", "permissions"],
        "list": ["user", "permissions"],
    }
    ORDERING_FIELDS = [
        "created_at",
        "rule",
        "weight",
        "malware_family",
        "mitre_technique",
    ]

    # models
    CreateRuleRequestBody = CreateRuleRequestBody
    UpdateRuleRequestBody = UpdateRuleRequestBody

    @classmethod
    def create(
        cls,
        data: CreateRuleRequestBody,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        post_data = dataclasses.asdict(data)
        return super().create(data=post_data, params=params)

    @classmethod
    def update(
        cls,
        object_id: Toid,
        data: UpdateRuleRequestBody,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        post_data = {
            "enabled": data.enabled,
        }
        return super().update(object_id=object_id, data=post_data, params=params)

    @classmethod
    def mitre(cls, params: Optional[TParams] = None) -> APIResponse:
        """
        .. versionadded:: 0.1.0
        """
        url = cls.class_url() + "/mitre"
        return cls._request("GET", url=url, params=params)

    @classmethod
    def aggregate_malware_behaviour(
        cls,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        """
        Deprecated in favor of ``aggregate_mitre_technique``.
        Will be removed in next release.
        """
        return cls.aggregate_mitre_technique(params=params)

    @classmethod
    def aggregate_mitre_technique(
        cls,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        """
        .. versionadded:: 0.1.0
        """
        url = cls.class_url() + "/aggregate/mitre_technique"
        return cls._request("GET", url=url, params=params)

    @classmethod
    def aggregate_behaviour(
        cls,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        """
        .. versionadded:: 0.1.0
        """
        url = cls.class_url() + "/aggregate/behaviour"
        return cls._request("GET", url=url, params=params)
