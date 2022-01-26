from typing import Any, BinaryIO, Dict, List, Optional, TextIO, Tuple, Type, TypeVar

from attr import define, field

from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="PredictionV1SaveFactorDateLatestAsOfsResponse")


@define(auto_attribs=True)
class PredictionV1SaveFactorDateLatestAsOfsResponse:
    """ """

    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        prediction_v1_save_factor_date_latest_as_ofs_response = cls()

        prediction_v1_save_factor_date_latest_as_ofs_response.additional_properties = d
        return prediction_v1_save_factor_date_latest_as_ofs_response

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
