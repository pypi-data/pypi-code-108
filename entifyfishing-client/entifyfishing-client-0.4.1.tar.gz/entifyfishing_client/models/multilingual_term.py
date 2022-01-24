from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="MultilingualTerm")


@attr.s(auto_attribs=True)
class MultilingualTerm:
    """ """

    term: str
    lang: Union[Unset, str] = UNSET
    page_id: Union[Unset, int] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        term = self.term
        lang = self.lang
        page_id = self.page_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "term": term,
            }
        )
        if lang is not UNSET:
            field_dict["lang"] = lang
        if page_id is not UNSET:
            field_dict["page_id"] = page_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        term = d.pop("term")

        lang = d.pop("lang", UNSET)

        page_id = d.pop("page_id", UNSET)

        multilingual_term = cls(
            term=term,
            lang=lang,
            page_id=page_id,
        )

        return multilingual_term
