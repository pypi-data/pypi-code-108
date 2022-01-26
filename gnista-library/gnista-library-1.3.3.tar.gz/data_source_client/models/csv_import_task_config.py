from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..models.gnista_unit_response import GnistaUnitResponse
from ..types import UNSET, Unset

T = TypeVar("T", bound="CSVImportTaskConfig")


@attr.s(auto_attribs=True)
class CSVImportTaskConfig:
    """ """

    discriminator: str
    file_id: str
    name: Union[Unset, None, str] = UNSET
    tags: Union[Unset, None, List[str]] = UNSET
    date_time_column: Union[Unset, int] = UNSET
    value_column: Union[Unset, int] = UNSET
    first_row_contains_data: Union[Unset, bool] = UNSET
    decimal_seperator: Union[Unset, None, str] = UNSET
    column_seperator: Union[Unset, None, str] = UNSET
    date_time_format: Union[Unset, None, str] = UNSET
    data_point_id: Union[Unset, None, str] = UNSET
    unit: Union[Unset, None, str] = UNSET
    gnista_unit: Union[Unset, None, GnistaUnitResponse] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        discriminator = self.discriminator
        file_id = self.file_id
        name = self.name
        tags: Union[Unset, None, List[str]] = UNSET
        if not isinstance(self.tags, Unset):
            if self.tags is None:
                tags = None
            else:
                tags = self.tags

        date_time_column = self.date_time_column
        value_column = self.value_column
        first_row_contains_data = self.first_row_contains_data
        decimal_seperator = self.decimal_seperator
        column_seperator = self.column_seperator
        date_time_format = self.date_time_format
        data_point_id = self.data_point_id
        unit = self.unit
        gnista_unit: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.gnista_unit, Unset):
            gnista_unit = self.gnista_unit.to_dict() if self.gnista_unit else None

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "discriminator": discriminator,
                "fileId": file_id,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if tags is not UNSET:
            field_dict["tags"] = tags
        if date_time_column is not UNSET:
            field_dict["dateTimeColumn"] = date_time_column
        if value_column is not UNSET:
            field_dict["valueColumn"] = value_column
        if first_row_contains_data is not UNSET:
            field_dict["firstRowContainsData"] = first_row_contains_data
        if decimal_seperator is not UNSET:
            field_dict["decimalSeperator"] = decimal_seperator
        if column_seperator is not UNSET:
            field_dict["columnSeperator"] = column_seperator
        if date_time_format is not UNSET:
            field_dict["dateTimeFormat"] = date_time_format
        if data_point_id is not UNSET:
            field_dict["dataPointId"] = data_point_id
        if unit is not UNSET:
            field_dict["unit"] = unit
        if gnista_unit is not UNSET:
            field_dict["gnistaUnit"] = gnista_unit

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        discriminator = d.pop("discriminator")

        file_id = d.pop("fileId")

        name = d.pop("name", UNSET)

        tags = cast(List[str], d.pop("tags", UNSET))

        date_time_column = d.pop("dateTimeColumn", UNSET)

        value_column = d.pop("valueColumn", UNSET)

        first_row_contains_data = d.pop("firstRowContainsData", UNSET)

        decimal_seperator = d.pop("decimalSeperator", UNSET)

        column_seperator = d.pop("columnSeperator", UNSET)

        date_time_format = d.pop("dateTimeFormat", UNSET)

        data_point_id = d.pop("dataPointId", UNSET)

        unit = d.pop("unit", UNSET)

        _gnista_unit = d.pop("gnistaUnit", UNSET)
        gnista_unit: Union[Unset, None, GnistaUnitResponse]
        if _gnista_unit is None:
            gnista_unit = None
        elif isinstance(_gnista_unit, Unset):
            gnista_unit = UNSET
        else:
            gnista_unit = GnistaUnitResponse.from_dict(_gnista_unit)

        csv_import_task_config = cls(
            discriminator=discriminator,
            file_id=file_id,
            name=name,
            tags=tags,
            date_time_column=date_time_column,
            value_column=value_column,
            first_row_contains_data=first_row_contains_data,
            decimal_seperator=decimal_seperator,
            column_seperator=column_seperator,
            date_time_format=date_time_format,
            data_point_id=data_point_id,
            unit=unit,
            gnista_unit=gnista_unit,
        )

        csv_import_task_config.additional_properties = d
        return csv_import_task_config

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
