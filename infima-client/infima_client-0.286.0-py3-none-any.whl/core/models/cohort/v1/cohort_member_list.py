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

from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="CohortV1CohortMemberList")


@define(auto_attribs=True)
class CohortV1CohortMemberList:
    """
    Attributes:
        cohort (Union[Unset, str]):
        cusips (Union[Unset, List[str]]):
    """

    cohort: Union[Unset, str] = UNSET
    cusips: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        cohort = self.cohort
        cusips: Union[Unset, List[str]] = UNSET
        if not isinstance(self.cusips, Unset):
            cusips = self.cusips

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cohort is not UNSET:
            field_dict["cohort"] = cohort
        if cusips is not UNSET:
            field_dict["cusips"] = cusips

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        cohort = d.pop("cohort", UNSET)

        cusips = cast(List[str], d.pop("cusips", UNSET))

        cohort_v1_cohort_member_list = cls(
            cohort=cohort,
            cusips=cusips,
        )

        cohort_v1_cohort_member_list.additional_properties = d
        return cohort_v1_cohort_member_list

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
