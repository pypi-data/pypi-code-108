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

from infima_client.core.models.pool.v1.get_summary_response_summary import (
    PoolV1GetSummaryResponseSummary,
)
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="PoolV1GetSummaryResponse")


@define(auto_attribs=True)
class PoolV1GetSummaryResponse:
    """
    Attributes:
        summary (Union[Unset, PoolV1GetSummaryResponseSummary]): Mapping of Pool summaries.
    """

    summary: Union[Unset, PoolV1GetSummaryResponseSummary] = UNSET
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
        summary: Union[Unset, PoolV1GetSummaryResponseSummary]
        if isinstance(_summary, Unset):
            summary = UNSET
        else:
            summary = PoolV1GetSummaryResponseSummary.from_dict(_summary)

        pool_v1_get_summary_response = cls(
            summary=summary,
        )

        pool_v1_get_summary_response.additional_properties = d
        return pool_v1_get_summary_response

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
