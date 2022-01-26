import json
from io import BytesIO
from typing import Any, Dict, List, Tuple, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, File, FileJsonType, Unset

T = TypeVar("T", bound="FileUploadFileMultipartData")


@attr.s(auto_attribs=True)
class FileUploadFileMultipartData:
    """ """

    file: Union[Unset, None, File] = UNSET
    tags: Union[Unset, None, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        file: Union[Unset, None, FileJsonType] = UNSET
        if not isinstance(self.file, Unset):
            file = self.file.to_tuple() if self.file else None

        tags: Union[Unset, None, List[str]] = UNSET
        if not isinstance(self.tags, Unset):
            if self.tags is None:
                tags = None
            else:
                tags = self.tags

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if file is not UNSET:
            field_dict["File"] = file
        if tags is not UNSET:
            field_dict["Tags"] = tags

        return field_dict

    def to_multipart(self) -> Dict[str, Any]:
        file: Union[Unset, None, FileJsonType] = UNSET
        if not isinstance(self.file, Unset):
            file = self.file.to_tuple() if self.file else None

        tags: Union[Unset, Tuple[None, str, str]] = UNSET
        if not isinstance(self.tags, Unset):
            if self.tags is None:
                tags = None
            else:
                _temp_tags = self.tags
                tags = (None, json.dumps(_temp_tags), "application/json")

        field_dict: Dict[str, Any] = {}
        field_dict.update({key: (None, str(value), "text/plain") for key, value in self.additional_properties.items()})
        field_dict.update({})
        if file is not UNSET:
            field_dict["File"] = file
        if tags is not UNSET:
            field_dict["Tags"] = tags

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _file = d.pop("File", UNSET)
        file: Union[Unset, None, File]
        if _file is None:
            file = None
        elif isinstance(_file, Unset):
            file = UNSET
        else:
            file = File(payload=BytesIO(_file))

        tags = cast(List[str], d.pop("Tags", UNSET))

        file_upload_file_multipart_data = cls(
            file=file,
            tags=tags,
        )

        file_upload_file_multipart_data.additional_properties = d
        return file_upload_file_multipart_data

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
