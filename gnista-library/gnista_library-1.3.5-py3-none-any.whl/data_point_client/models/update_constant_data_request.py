from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateConstantDataRequest")


@attr.s(auto_attribs=True)
class UpdateConstantDataRequest:
    """ """

    execution_id: Union[Unset, None, str] = UNSET
    value: Union[Unset, None, float] = UNSET
    unit: Union[Unset, None, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        execution_id = self.execution_id
        value = self.value
        unit = self.unit

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if execution_id is not UNSET:
            field_dict["executionId"] = execution_id
        if value is not UNSET:
            field_dict["value"] = value
        if unit is not UNSET:
            field_dict["unit"] = unit

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        execution_id = d.pop("executionId", UNSET)

        value = d.pop("value", UNSET)

        unit = d.pop("unit", UNSET)

        update_constant_data_request = cls(
            execution_id=execution_id,
            value=value,
            unit=unit,
        )

        return update_constant_data_request
