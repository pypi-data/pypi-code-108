from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="AlgoExecutionSymbol")


@attr.s(auto_attribs=True)
class AlgoExecutionSymbol:
    """ Any of the reserved python symbols available for use inside an Algo  """

    name: str
    dtype: str
    examples: List[str]
    group: Union[Unset, str] = ""
    description: Union[Unset, str] = ""
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        dtype = self.dtype
        examples = self.examples

        group = self.group
        description = self.description

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "dtype": dtype,
                "examples": examples,
            }
        )
        if group is not UNSET:
            field_dict["group"] = group
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        dtype = d.pop("dtype")

        examples = cast(List[str], d.pop("examples"))

        group = d.pop("group", UNSET)

        description = d.pop("description", UNSET)

        algo_execution_symbol = cls(
            name=name,
            dtype=dtype,
            examples=examples,
            group=group,
            description=description,
        )

        algo_execution_symbol.additional_properties = d
        return algo_execution_symbol

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
