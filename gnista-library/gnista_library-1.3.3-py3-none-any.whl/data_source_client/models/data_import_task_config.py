from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="DataImportTaskConfig")


@attr.s(auto_attribs=True)
class DataImportTaskConfig:
    """ """

    discriminator: str
    name: Union[Unset, None, str] = UNSET
    tags: Union[Unset, None, List[str]] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        discriminator = self.discriminator
        name = self.name
        tags: Union[Unset, None, List[str]] = UNSET
        if not isinstance(self.tags, Unset):
            if self.tags is None:
                tags = None
            else:
                tags = self.tags

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "discriminator": discriminator,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if tags is not UNSET:
            field_dict["tags"] = tags

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        discriminator = d.pop("discriminator")

        name = d.pop("name", UNSET)

        tags = cast(List[str], d.pop("tags", UNSET))

        data_import_task_config = cls(
            discriminator=discriminator,
            name=name,
            tags=tags,
        )

        return data_import_task_config
