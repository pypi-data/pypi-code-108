from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.algo_execution_data import AlgoExecutionData
from ..types import UNSET, Unset

T = TypeVar("T", bound="AlgoExecutionTestCase")


@attr.s(auto_attribs=True)
class AlgoExecutionTestCase:
    """A basic set of inputs (mock predictions, mock history), which
    can be fed to an Algo to see how it will respond when called by the trading
    simulator."""

    input_id: int
    data: AlgoExecutionData
    name: Union[Unset, str] = ""
    description: Union[Unset, str] = ""
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        input_id = self.input_id
        data = self.data.to_dict()

        name = self.name
        description = self.description

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "inputId": input_id,
                "data": data,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        input_id = d.pop("inputId")

        data = AlgoExecutionData.from_dict(d.pop("data"))

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        algo_execution_test_case = cls(
            input_id=input_id,
            data=data,
            name=name,
            description=description,
        )

        algo_execution_test_case.additional_properties = d
        return algo_execution_test_case

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
