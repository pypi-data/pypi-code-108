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

from infima_client.core.models.cohort.v1.check_coverage_response_summary import (
    CohortV1CheckCoverageResponseSummary,
)
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="CohortV1CheckCoverageResponse")


@define(auto_attribs=True)
class CohortV1CheckCoverageResponse:
    """
    Attributes:
        summary (Union[Unset, CohortV1CheckCoverageResponseSummary]):
    """

    summary: Union[Unset, CohortV1CheckCoverageResponseSummary] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        summary: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.summary, Unset):
            summary = self.summary.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if summary is not UNSET:
            field_dict["summary"] = summary

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _summary = d.pop("summary", UNSET)
        summary: Union[Unset, CohortV1CheckCoverageResponseSummary]
        if isinstance(_summary, Unset):
            summary = UNSET
        else:
            summary = CohortV1CheckCoverageResponseSummary.from_dict(_summary)

        cohort_v1_check_coverage_response = cls(
            summary=summary,
        )

        cohort_v1_check_coverage_response.additional_properties = d
        return cohort_v1_check_coverage_response

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
