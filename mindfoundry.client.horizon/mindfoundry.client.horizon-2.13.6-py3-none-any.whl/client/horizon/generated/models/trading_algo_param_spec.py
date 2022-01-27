from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.trading_algo_param_type import TradingAlgoParamType
from ..types import UNSET, Unset

T = TypeVar("T", bound="TradingAlgoParamSpec")


@attr.s(auto_attribs=True)
class TradingAlgoParamSpec:
    """ User-defined custom parameter for Algos  """

    name: str
    dtype: TradingAlgoParamType
    description: Union[Unset, str] = ""
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        dtype = self.dtype.value

        description = self.description

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "dtype": dtype,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        dtype = TradingAlgoParamType(d.pop("dtype"))

        description = d.pop("description", UNSET)

        trading_algo_param_spec = cls(
            name=name,
            dtype=dtype,
            description=description,
        )

        trading_algo_param_spec.additional_properties = d
        return trading_algo_param_spec

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
