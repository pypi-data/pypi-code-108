from typing import Any, BinaryIO, Dict, List, Optional, TextIO, Tuple, Type, TypeVar

from attr import define, field

from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="PredictionV1GetAvailableAsOfsRequest")


@define(auto_attribs=True)
class PredictionV1GetAvailableAsOfsRequest:
    """
    Attributes:
        symbol (str):
    """

    symbol: str
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        symbol = self.symbol

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "symbol": symbol,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        symbol = d.pop("symbol")

        prediction_v1_get_available_as_ofs_request = cls(
            symbol=symbol,
        )

        prediction_v1_get_available_as_ofs_request.additional_properties = d
        return prediction_v1_get_available_as_ofs_request

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
