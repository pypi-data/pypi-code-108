from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="GenericDataPoint")


@attr.s(auto_attribs=True)
class GenericDataPoint:
    """ A single data point in a serialised column  """

    x_value: str
    y_value: float
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        x_value = self.x_value
        y_value = self.y_value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "xValue": x_value,
                "yValue": y_value,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        x_value = d.pop("xValue")

        y_value = d.pop("yValue")

        generic_data_point = cls(
            x_value=x_value,
            y_value=y_value,
        )

        generic_data_point.additional_properties = d
        return generic_data_point

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
