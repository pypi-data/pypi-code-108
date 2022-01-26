from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="OligosUnarchive")


@attr.s(auto_attribs=True, repr=False)
class OligosUnarchive:
    """The request body for unarchiving Oligos."""

    _oligo_ids: List[str]

    def __repr__(self):
        fields = []
        fields.append("oligo_ids={}".format(repr(self._oligo_ids)))
        return "OligosUnarchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        oligo_ids = self._oligo_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "oligoIds": oligo_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_oligo_ids() -> List[str]:
            oligo_ids = cast(List[str], d.pop("oligoIds"))

            return oligo_ids

        oligo_ids = get_oligo_ids() if "oligoIds" in d else cast(List[str], UNSET)

        oligos_unarchive = cls(
            oligo_ids=oligo_ids,
        )

        return oligos_unarchive

    @property
    def oligo_ids(self) -> List[str]:
        if isinstance(self._oligo_ids, Unset):
            raise NotPresentError(self, "oligo_ids")
        return self._oligo_ids

    @oligo_ids.setter
    def oligo_ids(self, value: List[str]) -> None:
        self._oligo_ids = value
