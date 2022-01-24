from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.sense import Sense
from ..types import UNSET, Unset

T = TypeVar("T", bound="TermSenses")


@attr.s(auto_attribs=True)
class TermSenses:
    """ """

    term: str
    lang: Union[Unset, str] = UNSET
    senses: Union[Unset, List[Sense]] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        term = self.term
        lang = self.lang
        senses: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.senses, Unset):
            senses = []
            for senses_item_data in self.senses:
                senses_item = senses_item_data.to_dict()

                senses.append(senses_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "term": term,
            }
        )
        if lang is not UNSET:
            field_dict["lang"] = lang
        if senses is not UNSET:
            field_dict["senses"] = senses

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        term = d.pop("term")

        lang = d.pop("lang", UNSET)

        senses = []
        _senses = d.pop("senses", UNSET)
        for senses_item_data in _senses or []:
            senses_item = Sense.from_dict(senses_item_data)

            senses.append(senses_item)

        term_senses = cls(
            term=term,
            lang=lang,
            senses=senses,
        )

        return term_senses
