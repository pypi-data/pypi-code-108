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

from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="CohortV1GetMemberPoolsRequest")


@define(auto_attribs=True)
class CohortV1GetMemberPoolsRequest:
    """
    Attributes:
        cohorts (List[str]):
    """

    cohorts: List[str]
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        cohorts = self.cohorts

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cohorts": cohorts,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        cohorts = cast(List[str], d.pop("cohorts"))

        cohort_v1_get_member_pools_request = cls(
            cohorts=cohorts,
        )

        cohort_v1_get_member_pools_request.additional_properties = d
        return cohort_v1_get_member_pools_request

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
