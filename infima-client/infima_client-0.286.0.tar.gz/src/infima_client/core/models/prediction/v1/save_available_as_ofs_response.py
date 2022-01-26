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

T = TypeVar("T", bound="PredictionV1SaveAvailableAsOfsResponse")


@define(auto_attribs=True)
class PredictionV1SaveAvailableAsOfsResponse:
    """
    Attributes:
        num_asofs_saved (Union[Unset, int]):
    """

    num_asofs_saved: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        num_asofs_saved = self.num_asofs_saved

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if num_asofs_saved is not UNSET:
            field_dict["numAsofsSaved"] = num_asofs_saved

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        num_asofs_saved = d.pop("numAsofsSaved", UNSET)

        prediction_v1_save_available_as_ofs_response = cls(
            num_asofs_saved=num_asofs_saved,
        )

        prediction_v1_save_available_as_ofs_response.additional_properties = d
        return prediction_v1_save_available_as_ofs_response

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
