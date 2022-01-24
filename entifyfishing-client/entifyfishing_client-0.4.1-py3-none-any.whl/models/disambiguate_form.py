import json
from io import BytesIO
from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..models.query_parameters import QueryParameters
from ..types import UNSET, File, FileJsonType, Unset

T = TypeVar("T", bound="DisambiguateForm")


@attr.s(auto_attribs=True)
class DisambiguateForm:
    """ """

    query: QueryParameters
    file: Union[Unset, File] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        query = self.query.to_dict()

        file: Union[Unset, FileJsonType] = UNSET
        if not isinstance(self.file, Unset):
            file = self.file.to_tuple()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "query": query,
            }
        )
        if file is not UNSET:
            field_dict["file"] = file

        return field_dict

    def to_multipart(self) -> Dict[str, Any]:
        query = (None, json.dumps(self.query.to_dict()).encode(), "application/json")

        file: Union[Unset, FileJsonType] = UNSET
        if not isinstance(self.file, Unset):
            file = self.file.to_tuple()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "query": query,
            }
        )
        if file is not UNSET:
            field_dict["file"] = file

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        query = QueryParameters.from_dict(d.pop("query"))

        _file = d.pop("file", UNSET)
        file: Union[Unset, File]
        if isinstance(_file, Unset):
            file = UNSET
        else:
            file = File(payload=BytesIO(_file))

        disambiguate_form = cls(
            query=query,
            file=file,
        )

        return disambiguate_form
