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
)

from attr import define, field

from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="CohortV1SaveCohortSummariesResponse")


@define(auto_attribs=True)
class CohortV1SaveCohortSummariesResponse:
    """
    Attributes:
        num_summaries_saved (Union[Unset, int]):
    """

    num_summaries_saved: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        num_summaries_saved = self.num_summaries_saved

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if num_summaries_saved is not UNSET:
            field_dict["numSummariesSaved"] = num_summaries_saved

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        num_summaries_saved = d.pop("numSummariesSaved", UNSET)

        cohort_v1_save_cohort_summaries_response = cls(
            num_summaries_saved=num_summaries_saved,
        )

        cohort_v1_save_cohort_summaries_response.additional_properties = d
        return cohort_v1_save_cohort_summaries_response

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
