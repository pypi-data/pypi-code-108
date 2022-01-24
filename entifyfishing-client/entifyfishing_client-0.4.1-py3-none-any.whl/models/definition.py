from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="Definition")


@attr.s(auto_attribs=True)
class Definition:
    """ """

    definition: str
    source: Union[Unset, str] = UNSET
    lang: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        definition = self.definition
        source = self.source
        lang = self.lang

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "definition": definition,
            }
        )
        if source is not UNSET:
            field_dict["source"] = source
        if lang is not UNSET:
            field_dict["lang"] = lang

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        definition = d.pop("definition")

        source = d.pop("source", UNSET)

        lang = d.pop("lang", UNSET)

        definition = cls(
            definition=definition,
            source=source,
            lang=lang,
        )

        return definition
