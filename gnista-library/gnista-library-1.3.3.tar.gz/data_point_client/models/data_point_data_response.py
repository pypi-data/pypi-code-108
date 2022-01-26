from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..models.en_data_point_status import EnDataPointStatus
from ..models.gnista_unit_response import GnistaUnitResponse
from ..types import UNSET, Unset

T = TypeVar("T", bound="DataPointDataResponse")


@attr.s(auto_attribs=True)
class DataPointDataResponse:
    """ """

    unit: Union[Unset, None, GnistaUnitResponse] = UNSET
    status: Union[Unset, EnDataPointStatus] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        unit: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.unit, Unset):
            unit = self.unit.to_dict() if self.unit else None

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if unit is not UNSET:
            field_dict["unit"] = unit
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _unit = d.pop("unit", UNSET)
        unit: Union[Unset, None, GnistaUnitResponse]
        if _unit is None:
            unit = None
        elif isinstance(_unit, Unset):
            unit = UNSET
        else:
            unit = GnistaUnitResponse.from_dict(_unit)

        _status = d.pop("status", UNSET)
        status: Union[Unset, EnDataPointStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = EnDataPointStatus(_status)

        data_point_data_response = cls(
            unit=unit,
            status=status,
        )

        return data_point_data_response
