from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="ImportOrigin")


@attr.s(auto_attribs=True)
class ImportOrigin:
    """ """

    discriminator: str
    data_source_id: Union[Unset, None, str] = UNSET
    data_import_id: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        discriminator = self.discriminator
        data_source_id = self.data_source_id
        data_import_id = self.data_import_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "discriminator": discriminator,
            }
        )
        if data_source_id is not UNSET:
            field_dict["dataSourceId"] = data_source_id
        if data_import_id is not UNSET:
            field_dict["dataImportId"] = data_import_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        discriminator = d.pop("discriminator")

        data_source_id = d.pop("dataSourceId", UNSET)

        data_import_id = d.pop("dataImportId", UNSET)

        import_origin = cls(
            discriminator=discriminator,
            data_source_id=data_source_id,
            data_import_id=data_import_id,
        )

        import_origin.additional_properties = d
        return import_origin

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
