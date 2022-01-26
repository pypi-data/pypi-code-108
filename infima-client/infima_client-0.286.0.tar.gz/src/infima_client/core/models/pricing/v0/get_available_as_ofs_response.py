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

from infima_client.core.models.core.date import CoreDate
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="PricingV0GetAvailableAsOfsResponse")


@define(auto_attribs=True)
class PricingV0GetAvailableAsOfsResponse:
    """
    Attributes:
        as_ofs (Union[Unset, List[CoreDate]]):
    """

    as_ofs: Union[Unset, List[CoreDate]] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        as_ofs: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.as_ofs, Unset):
            as_ofs = []
            for as_ofs_item_data in self.as_ofs:
                as_ofs_item = as_ofs_item_data.to_dict()

                as_ofs.append(as_ofs_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if as_ofs is not UNSET:
            field_dict["asOfs"] = as_ofs

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        as_ofs = []
        _as_ofs = d.pop("asOfs", UNSET)
        for as_ofs_item_data in _as_ofs or []:
            as_ofs_item = CoreDate.from_dict(as_ofs_item_data)

            as_ofs.append(as_ofs_item)

        pricing_v0_get_available_as_ofs_response = cls(
            as_ofs=as_ofs,
        )

        pricing_v0_get_available_as_ofs_response.additional_properties = d
        return pricing_v0_get_available_as_ofs_response

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
