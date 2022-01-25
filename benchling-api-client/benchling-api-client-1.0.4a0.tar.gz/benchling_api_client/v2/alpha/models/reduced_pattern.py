from typing import Any, cast, Dict, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="ReducedPattern")


@attr.s(auto_attribs=True, repr=False)
class ReducedPattern:
    """Patterns must consist of ATGC bases only, and are case-insensitive ("gat" will reduce usage of "GAT"). If avoidReverseComplement is true, then the pattern's reverse complement will also be avoided."""

    _avoid_reverse_complement: Union[Unset, bool] = False
    _pattern: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("avoid_reverse_complement={}".format(repr(self._avoid_reverse_complement)))
        fields.append("pattern={}".format(repr(self._pattern)))
        return "ReducedPattern({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        avoid_reverse_complement = self._avoid_reverse_complement
        pattern = self._pattern

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if avoid_reverse_complement is not UNSET:
            field_dict["avoidReverseComplement"] = avoid_reverse_complement
        if pattern is not UNSET:
            field_dict["pattern"] = pattern

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_avoid_reverse_complement() -> Union[Unset, bool]:
            avoid_reverse_complement = d.pop("avoidReverseComplement")
            return avoid_reverse_complement

        avoid_reverse_complement = (
            get_avoid_reverse_complement()
            if "avoidReverseComplement" in d
            else cast(Union[Unset, bool], UNSET)
        )

        def get_pattern() -> Union[Unset, str]:
            pattern = d.pop("pattern")
            return pattern

        pattern = get_pattern() if "pattern" in d else cast(Union[Unset, str], UNSET)

        reduced_pattern = cls(
            avoid_reverse_complement=avoid_reverse_complement,
            pattern=pattern,
        )

        return reduced_pattern

    @property
    def avoid_reverse_complement(self) -> bool:
        if isinstance(self._avoid_reverse_complement, Unset):
            raise NotPresentError(self, "avoid_reverse_complement")
        return self._avoid_reverse_complement

    @avoid_reverse_complement.setter
    def avoid_reverse_complement(self, value: bool) -> None:
        self._avoid_reverse_complement = value

    @avoid_reverse_complement.deleter
    def avoid_reverse_complement(self) -> None:
        self._avoid_reverse_complement = UNSET

    @property
    def pattern(self) -> str:
        if isinstance(self._pattern, Unset):
            raise NotPresentError(self, "pattern")
        return self._pattern

    @pattern.setter
    def pattern(self, value: str) -> None:
        self._pattern = value

    @pattern.deleter
    def pattern(self) -> None:
        self._pattern = UNSET
