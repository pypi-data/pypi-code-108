from typing import (
    Any,
    BinaryIO,
    Dict,
    List,
    Optional,
    TextIO,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

from attr import define, field

from infima_client.core.models.cohort.v1.get_pool_memberships_response_memberships import (
    CohortV1GetPoolMembershipsResponseMemberships,
)
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="CohortV1GetPoolMembershipsResponse")


@define(auto_attribs=True)
class CohortV1GetPoolMembershipsResponse:
    """
    Attributes:
        memberships (Union[Unset, CohortV1GetPoolMembershipsResponseMemberships]):
    """

    memberships: Union[Unset, CohortV1GetPoolMembershipsResponseMemberships] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        memberships: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.memberships, Unset):
            memberships = self.memberships.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if memberships is not UNSET:
            field_dict["memberships"] = memberships

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _memberships = d.pop("memberships", UNSET)
        memberships: Union[Unset, CohortV1GetPoolMembershipsResponseMemberships]
        if isinstance(_memberships, Unset):
            memberships = UNSET
        else:
            memberships = CohortV1GetPoolMembershipsResponseMemberships.from_dict(
                _memberships
            )

        cohort_v1_get_pool_memberships_response = cls(
            memberships=memberships,
        )

        cohort_v1_get_pool_memberships_response.additional_properties = d
        return cohort_v1_get_pool_memberships_response

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
