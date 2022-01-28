from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="TimeSeriesMaskImportTaskConfig")


@attr.s(auto_attribs=True)
class TimeSeriesMaskImportTaskConfig:
    """ """

    discriminator: str
    file_id: str
    name: Union[Unset, None, str] = UNSET
    tags: Union[Unset, None, List[str]] = UNSET
    date_time_start_column: Union[Unset, int] = UNSET
    date_time_end_column: Union[Unset, int] = UNSET
    name_column: Union[Unset, int] = UNSET
    date_time_format: Union[Unset, None, str] = UNSET
    first_row_contains_data: Union[Unset, bool] = UNSET
    decimal_seperator: Union[Unset, None, str] = UNSET
    column_seperator: Union[Unset, None, str] = UNSET
    time_series_mask_id: Union[Unset, None, str] = UNSET
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

        date_time_start_column = self.date_time_start_column
        date_time_end_column = self.date_time_end_column
        name_column = self.name_column
        date_time_format = self.date_time_format
        first_row_contains_data = self.first_row_contains_data
        decimal_seperator = self.decimal_seperator
        column_seperator = self.column_seperator
        time_series_mask_id = self.time_series_mask_id

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
        if date_time_start_column is not UNSET:
            field_dict["dateTimeStartColumn"] = date_time_start_column
        if date_time_end_column is not UNSET:
            field_dict["dateTimeEndColumn"] = date_time_end_column
        if name_column is not UNSET:
            field_dict["nameColumn"] = name_column
        if date_time_format is not UNSET:
            field_dict["dateTimeFormat"] = date_time_format
        if first_row_contains_data is not UNSET:
            field_dict["firstRowContainsData"] = first_row_contains_data
        if decimal_seperator is not UNSET:
            field_dict["decimalSeperator"] = decimal_seperator
        if column_seperator is not UNSET:
            field_dict["columnSeperator"] = column_seperator
        if time_series_mask_id is not UNSET:
            field_dict["timeSeriesMaskId"] = time_series_mask_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        discriminator = d.pop("discriminator")

        file_id = d.pop("fileId")

        name = d.pop("name", UNSET)

        tags = cast(List[str], d.pop("tags", UNSET))

        date_time_start_column = d.pop("dateTimeStartColumn", UNSET)

        date_time_end_column = d.pop("dateTimeEndColumn", UNSET)

        name_column = d.pop("nameColumn", UNSET)

        date_time_format = d.pop("dateTimeFormat", UNSET)

        first_row_contains_data = d.pop("firstRowContainsData", UNSET)

        decimal_seperator = d.pop("decimalSeperator", UNSET)

        column_seperator = d.pop("columnSeperator", UNSET)

        time_series_mask_id = d.pop("timeSeriesMaskId", UNSET)

        time_series_mask_import_task_config = cls(
            discriminator=discriminator,
            file_id=file_id,
            name=name,
            tags=tags,
            date_time_start_column=date_time_start_column,
            date_time_end_column=date_time_end_column,
            name_column=name_column,
            date_time_format=date_time_format,
            first_row_contains_data=first_row_contains_data,
            decimal_seperator=decimal_seperator,
            column_seperator=column_seperator,
            time_series_mask_id=time_series_mask_id,
        )

        time_series_mask_import_task_config.additional_properties = d
        return time_series_mask_import_task_config

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
