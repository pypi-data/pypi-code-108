from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="FileImportDescriptionConfig")


@attr.s(auto_attribs=True)
class FileImportDescriptionConfig:
    """ """

    discriminator: str
    file_id: str
    column_seperator: Union[Unset, None, str] = UNSET
    decimal_seperator: Union[Unset, None, str] = UNSET
    date_time_format: Union[Unset, None, str] = UNSET
    first_row_contains_data: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        discriminator = self.discriminator
        file_id = self.file_id
        column_seperator = self.column_seperator
        decimal_seperator = self.decimal_seperator
        date_time_format = self.date_time_format
        first_row_contains_data = self.first_row_contains_data

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "discriminator": discriminator,
                "fileId": file_id,
            }
        )
        if column_seperator is not UNSET:
            field_dict["columnSeperator"] = column_seperator
        if decimal_seperator is not UNSET:
            field_dict["decimalSeperator"] = decimal_seperator
        if date_time_format is not UNSET:
            field_dict["dateTimeFormat"] = date_time_format
        if first_row_contains_data is not UNSET:
            field_dict["firstRowContainsData"] = first_row_contains_data

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        discriminator = d.pop("discriminator")

        file_id = d.pop("fileId")

        column_seperator = d.pop("columnSeperator", UNSET)

        decimal_seperator = d.pop("decimalSeperator", UNSET)

        date_time_format = d.pop("dateTimeFormat", UNSET)

        first_row_contains_data = d.pop("firstRowContainsData", UNSET)

        file_import_description_config = cls(
            discriminator=discriminator,
            file_id=file_id,
            column_seperator=column_seperator,
            decimal_seperator=decimal_seperator,
            date_time_format=date_time_format,
            first_row_contains_data=first_row_contains_data,
        )

        file_import_description_config.additional_properties = d
        return file_import_description_config

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
