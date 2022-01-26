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

T = TypeVar("T", bound="PoolV1GetSummaryRequest")


@define(auto_attribs=True)
class PoolV1GetSummaryRequest:
    """
    Attributes:
        cusips (List[str]): Pool CUSIPs to fetch summaries. Example: 31417EUD1.
    """

    cusips: List[str]
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        cusips = self.cusips

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cusips": cusips,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        cusips = cast(List[str], d.pop("cusips"))

        pool_v1_get_summary_request = cls(
            cusips=cusips,
        )

        pool_v1_get_summary_request.additional_properties = d
        return pool_v1_get_summary_request

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
