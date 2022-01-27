from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.date_value_pair import DateValuePair

T = TypeVar("T", bound="DateValueSeries")


@attr.s(auto_attribs=True)
class DateValueSeries:
    """ Serialised column, split into contiguous segments  """

    title: str
    data: List[List[DateValuePair]]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        title = self.title
        data = []
        for data_item_data in self.data:
            data_item = []
            for data_item_item_data in data_item_data:
                data_item_item = data_item_item_data.to_dict()

                data_item.append(data_item_item)

            data.append(data_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "title": title,
                "data": data,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        title = d.pop("title")

        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = []
            _data_item = data_item_data
            for data_item_item_data in _data_item:
                data_item_item = DateValuePair.from_dict(data_item_item_data)

                data_item.append(data_item_item)

            data.append(data_item)

        date_value_series = cls(
            title=title,
            data=data,
        )

        date_value_series.additional_properties = d
        return date_value_series

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
