from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..models.en_data_point_existence_dto import EnDataPointExistenceDTO
from ..types import UNSET, Unset

T = TypeVar("T", bound="DataPointRequest")


@attr.s(auto_attribs=True)
class DataPointRequest:
    """ """

    name: Union[Unset, None, str] = UNSET
    description: Union[Unset, None, str] = UNSET
    existence: Union[Unset, None, EnDataPointExistenceDTO] = UNSET
    tags: Union[Unset, None, List[str]] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        description = self.description
        existence: Union[Unset, None, str] = UNSET
        if not isinstance(self.existence, Unset):
            existence = self.existence.value if self.existence else None

        tags: Union[Unset, None, List[str]] = UNSET
        if not isinstance(self.tags, Unset):
            if self.tags is None:
                tags = None
            else:
                tags = self.tags

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if existence is not UNSET:
            field_dict["existence"] = existence
        if tags is not UNSET:
            field_dict["tags"] = tags

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        _existence = d.pop("existence", UNSET)
        existence: Union[Unset, None, EnDataPointExistenceDTO]
        if _existence is None:
            existence = None
        elif isinstance(_existence, Unset):
            existence = UNSET
        else:
            existence = EnDataPointExistenceDTO(_existence)

        tags = cast(List[str], d.pop("tags", UNSET))

        data_point_request = cls(
            name=name,
            description=description,
            existence=existence,
            tags=tags,
        )

        return data_point_request
