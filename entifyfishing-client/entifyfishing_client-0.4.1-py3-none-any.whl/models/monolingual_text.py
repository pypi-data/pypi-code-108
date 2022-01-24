from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="MonolingualText")


@attr.s(auto_attribs=True)
class MonolingualText:
    """ """

    text: str
    language: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        text = self.text
        language = self.language

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "text": text,
            }
        )
        if language is not UNSET:
            field_dict["language"] = language

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        text = d.pop("text")

        language = d.pop("language", UNSET)

        monolingual_text = cls(
            text=text,
            language=language,
        )

        return monolingual_text
