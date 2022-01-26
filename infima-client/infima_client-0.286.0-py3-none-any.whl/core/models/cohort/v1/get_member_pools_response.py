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

from infima_client.core.models.cohort.v1.get_member_pools_response_member_pools import (
    CohortV1GetMemberPoolsResponseMemberPools,
)
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="CohortV1GetMemberPoolsResponse")


@define(auto_attribs=True)
class CohortV1GetMemberPoolsResponse:
    """
    Attributes:
        member_pools (Union[Unset, CohortV1GetMemberPoolsResponseMemberPools]):
    """

    member_pools: Union[Unset, CohortV1GetMemberPoolsResponseMemberPools] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        member_pools: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.member_pools, Unset):
            member_pools = self.member_pools.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if member_pools is not UNSET:
            field_dict["memberPools"] = member_pools

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _member_pools = d.pop("memberPools", UNSET)
        member_pools: Union[Unset, CohortV1GetMemberPoolsResponseMemberPools]
        if isinstance(_member_pools, Unset):
            member_pools = UNSET
        else:
            member_pools = CohortV1GetMemberPoolsResponseMemberPools.from_dict(
                _member_pools
            )

        cohort_v1_get_member_pools_response = cls(
            member_pools=member_pools,
        )

        cohort_v1_get_member_pools_response.additional_properties = d
        return cohort_v1_get_member_pools_response

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
