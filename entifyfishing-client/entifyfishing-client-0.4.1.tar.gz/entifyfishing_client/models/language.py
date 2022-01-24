from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="Language")


@attr.s(auto_attribs=True)
class Language:
    """ """

    lang: str
    conf: Union[Unset, float] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        lang = self.lang
        conf = self.conf

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "lang": lang,
            }
        )
        if conf is not UNSET:
            field_dict["conf"] = conf

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        lang = d.pop("lang")

        conf = d.pop("conf", UNSET)

        language = cls(
            lang=lang,
            conf=conf,
        )

        return language
