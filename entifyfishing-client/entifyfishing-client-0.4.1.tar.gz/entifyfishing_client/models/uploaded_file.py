from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="UploadedFile")


@attr.s(auto_attribs=True)
class UploadedFile:
    """ """

    filename: str
    id: str
    content_type: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        filename = self.filename
        id = self.id
        content_type = self.content_type

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "filename": filename,
                "id": id,
            }
        )
        if content_type is not UNSET:
            field_dict["contentType"] = content_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        filename = d.pop("filename")

        id = d.pop("id")

        content_type = d.pop("contentType", UNSET)

        uploaded_file = cls(
            filename=filename,
            id=id,
            content_type=content_type,
        )

        return uploaded_file
