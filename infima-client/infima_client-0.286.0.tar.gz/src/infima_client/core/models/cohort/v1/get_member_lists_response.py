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

from infima_client.core.models.cohort.v1.get_member_lists_response_member_lists import (
    CohortV1GetMemberListsResponseMemberLists,
)
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="CohortV1GetMemberListsResponse")


@define(auto_attribs=True)
class CohortV1GetMemberListsResponse:
    """
    Attributes:
        member_lists (Union[Unset, CohortV1GetMemberListsResponseMemberLists]): Mapping of cohort name to member list.
    """

    member_lists: Union[Unset, CohortV1GetMemberListsResponseMemberLists] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        member_lists: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.member_lists, Unset):
            member_lists = self.member_lists.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if member_lists is not UNSET:
            field_dict["memberLists"] = member_lists

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _member_lists = d.pop("memberLists", UNSET)
        member_lists: Union[Unset, CohortV1GetMemberListsResponseMemberLists]
        if isinstance(_member_lists, Unset):
            member_lists = UNSET
        else:
            member_lists = CohortV1GetMemberListsResponseMemberLists.from_dict(
                _member_lists
            )

        cohort_v1_get_member_lists_response = cls(
            member_lists=member_lists,
        )

        cohort_v1_get_member_lists_response.additional_properties = d
        return cohort_v1_get_member_lists_response

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
