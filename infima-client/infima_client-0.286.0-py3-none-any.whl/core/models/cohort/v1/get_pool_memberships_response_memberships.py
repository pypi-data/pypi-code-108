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
    cast,
)

from attr import define, field

from infima_client.core.models.cohort.v1.pool_memberships import CohortV1PoolMemberships
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="CohortV1GetPoolMembershipsResponseMemberships")


@define(auto_attribs=True)
class CohortV1GetPoolMembershipsResponseMemberships:
    """ """

    additional_properties: Dict[str, CohortV1PoolMemberships] = field(
        init=False, factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()

        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        cohort_v1_get_pool_memberships_response_memberships = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = CohortV1PoolMemberships.from_dict(prop_dict)

            additional_properties[prop_name] = additional_property

        cohort_v1_get_pool_memberships_response_memberships.additional_properties = (
            additional_properties
        )
        return cohort_v1_get_pool_memberships_response_memberships

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> CohortV1PoolMemberships:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: CohortV1PoolMemberships) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
