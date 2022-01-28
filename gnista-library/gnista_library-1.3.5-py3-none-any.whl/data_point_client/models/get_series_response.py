from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.time_series_response import TimeSeriesResponse
from ..types import UNSET, Unset

T = TypeVar("T", bound="GetSeriesResponse")


@attr.s(auto_attribs=True)
class GetSeriesResponse:
    """ """

    discriminator: str
    curves: Union[Unset, None, List[TimeSeriesResponse]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        discriminator = self.discriminator
        curves: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.curves, Unset):
            if self.curves is None:
                curves = None
            else:
                curves = []
                for curves_item_data in self.curves:
                    curves_item = curves_item_data.to_dict()

                    curves.append(curves_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "discriminator": discriminator,
            }
        )
        if curves is not UNSET:
            field_dict["curves"] = curves

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        discriminator = d.pop("discriminator")

        curves = []
        _curves = d.pop("curves", UNSET)
        for curves_item_data in _curves or []:
            curves_item = TimeSeriesResponse.from_dict(curves_item_data)

            curves.append(curves_item)

        get_series_response = cls(
            discriminator=discriminator,
            curves=curves,
        )

        get_series_response.additional_properties = d
        return get_series_response

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
