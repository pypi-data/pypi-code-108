from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="PandasSeries")


@attr.s(auto_attribs=True)
class PandasSeries:
    """  """

    data: List[Union[float, str]]
    index: List[float]
    index_dtype: str
    name: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = []
        for data_item_data in self.data:
            data_item = data_item_data

            data.append(data_item)

        index = []
        for index_item_data in self.index:
            index_item = index_item_data

            index.append(index_item)

        index_dtype = self.index_dtype
        name = self.name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
                "index": index,
                "indexDtype": index_dtype,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        data = []
        _data = d.pop("data")
        for data_item_data in _data:

            def _parse_data_item(data: object) -> Union[float, str]:
                return cast(Union[float, str], data)

            data_item = _parse_data_item(data_item_data)

            data.append(data_item)

        index = []
        _index = d.pop("index")
        for index_item_data in _index:

            def _parse_index_item(data: object) -> float:
                return cast(float, data)

            index_item = _parse_index_item(index_item_data)

            index.append(index_item)

        index_dtype = d.pop("indexDtype")

        name = d.pop("name", UNSET)

        pandas_series = cls(
            data=data,
            index=index,
            index_dtype=index_dtype,
            name=name,
        )

        pandas_series.additional_properties = d
        return pandas_series

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
