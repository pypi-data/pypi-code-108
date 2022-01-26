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

from infima_client.core.models.pool.v1.pool import PoolV1Pool
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="CohortV1CohortMemberPools")


@define(auto_attribs=True)
class CohortV1CohortMemberPools:
    """
    Attributes:
        cohort (Union[Unset, str]):
        members (Union[Unset, List[PoolV1Pool]]):
    """

    cohort: Union[Unset, str] = UNSET
    members: Union[Unset, List[PoolV1Pool]] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        cohort = self.cohort
        members: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.members, Unset):
            members = []
            for members_item_data in self.members:
                members_item = members_item_data.to_dict()

                members.append(members_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cohort is not UNSET:
            field_dict["cohort"] = cohort
        if members is not UNSET:
            field_dict["members"] = members

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        cohort = d.pop("cohort", UNSET)

        members = []
        _members = d.pop("members", UNSET)
        for members_item_data in _members or []:
            members_item = PoolV1Pool.from_dict(members_item_data)

            members.append(members_item)

        cohort_v1_cohort_member_pools = cls(
            cohort=cohort,
            members=members,
        )

        cohort_v1_cohort_member_pools.additional_properties = d
        return cohort_v1_cohort_member_pools

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
