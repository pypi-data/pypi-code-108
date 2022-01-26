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

from infima_client.core.models.cohort.v1.cohort_member_pools import (
    CohortV1CohortMemberPools,
)
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="CohortV1GetMemberPoolsResponseMemberPools")


@define(auto_attribs=True)
class CohortV1GetMemberPoolsResponseMemberPools:
    """ """

    additional_properties: Dict[str, CohortV1CohortMemberPools] = field(
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
        cohort_v1_get_member_pools_response_member_pools = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = CohortV1CohortMemberPools.from_dict(prop_dict)

            additional_properties[prop_name] = additional_property

        cohort_v1_get_member_pools_response_member_pools.additional_properties = (
            additional_properties
        )
        return cohort_v1_get_member_pools_response_member_pools

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> CohortV1CohortMemberPools:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: CohortV1CohortMemberPools) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
