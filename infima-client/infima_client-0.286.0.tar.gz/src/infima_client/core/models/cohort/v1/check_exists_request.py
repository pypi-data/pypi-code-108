from typing import Any, BinaryIO, Dict, List, Optional, TextIO, Tuple, Type, TypeVar

from attr import define, field

from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="CohortV1CheckExistsRequest")


@define(auto_attribs=True)
class CohortV1CheckExistsRequest:
    """
    Attributes:
        cohort (str):
    """

    cohort: str
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        cohort = self.cohort

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cohort": cohort,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        cohort = d.pop("cohort")

        cohort_v1_check_exists_request = cls(
            cohort=cohort,
        )

        cohort_v1_check_exists_request.additional_properties = d
        return cohort_v1_check_exists_request

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
