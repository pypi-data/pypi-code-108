from typing import Any, Dict, Type, TypeVar

import attr

T = TypeVar("T", bound="Sentence")


@attr.s(auto_attribs=True)
class Sentence:
    """ """

    offset_start: int
    offset_end: int

    def to_dict(self) -> Dict[str, Any]:
        offset_start = self.offset_start
        offset_end = self.offset_end

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "offsetStart": offset_start,
                "offsetEnd": offset_end,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        offset_start = d.pop("offsetStart")

        offset_end = d.pop("offsetEnd")

        sentence = cls(
            offset_start=offset_start,
            offset_end=offset_end,
        )

        return sentence
