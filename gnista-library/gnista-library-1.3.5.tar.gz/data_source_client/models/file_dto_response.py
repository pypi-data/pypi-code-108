import datetime
from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="FileDTOResponse")


@attr.s(auto_attribs=True)
class FileDTOResponse:
    """ """

    file_id: str
    uploaded_at: datetime.datetime
    name: Union[Unset, None, str] = UNSET
    tags: Union[Unset, None, List[str]] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        file_id = self.file_id
        uploaded_at = self.uploaded_at.isoformat()

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
                "fileId": file_id,
                "uploadedAt": uploaded_at,
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
        file_id = d.pop("fileId")

        uploaded_at = isoparse(d.pop("uploadedAt"))

        name = d.pop("name", UNSET)

        tags = cast(List[str], d.pop("tags", UNSET))

        file_dto_response = cls(
            file_id=file_id,
            uploaded_at=uploaded_at,
            name=name,
            tags=tags,
        )

        return file_dto_response
