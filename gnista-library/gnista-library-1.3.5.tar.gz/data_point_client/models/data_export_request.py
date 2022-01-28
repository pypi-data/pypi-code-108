from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="DataExportRequest")


@attr.s(auto_attribs=True)
class DataExportRequest:
    """ """

    data_point_id: str
    separator: str
    version: int
    unit: Union[Unset, None, str] = UNSET
    window_hours: Union[Unset, None, int] = UNSET
    file_name: Union[Unset, None, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        data_point_id = self.data_point_id
        separator = self.separator
        version = self.version
        unit = self.unit
        window_hours = self.window_hours
        file_name = self.file_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "dataPointId": data_point_id,
                "separator": separator,
                "version": version,
            }
        )
        if unit is not UNSET:
            field_dict["unit"] = unit
        if window_hours is not UNSET:
            field_dict["windowHours"] = window_hours
        if file_name is not UNSET:
            field_dict["fileName"] = file_name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        data_point_id = d.pop("dataPointId")

        separator = d.pop("separator")

        version = d.pop("version")

        unit = d.pop("unit", UNSET)

        window_hours = d.pop("windowHours", UNSET)

        file_name = d.pop("fileName", UNSET)

        data_export_request = cls(
            data_point_id=data_point_id,
            separator=separator,
            version=version,
            unit=unit,
            window_hours=window_hours,
            file_name=file_name,
        )

        return data_export_request
