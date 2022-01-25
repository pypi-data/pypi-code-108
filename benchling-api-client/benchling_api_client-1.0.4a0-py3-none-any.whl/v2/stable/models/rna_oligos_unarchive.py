from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="RnaOligosUnarchive")


@attr.s(auto_attribs=True, repr=False)
class RnaOligosUnarchive:
    """The request body for unarchiving RNA Oligos."""

    _rna_oligo_ids: List[str]

    def __repr__(self):
        fields = []
        fields.append("rna_oligo_ids={}".format(repr(self._rna_oligo_ids)))
        return "RnaOligosUnarchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        rna_oligo_ids = self._rna_oligo_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "rnaOligoIds": rna_oligo_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_rna_oligo_ids() -> List[str]:
            rna_oligo_ids = cast(List[str], d.pop("rnaOligoIds"))

            return rna_oligo_ids

        rna_oligo_ids = get_rna_oligo_ids() if "rnaOligoIds" in d else cast(List[str], UNSET)

        rna_oligos_unarchive = cls(
            rna_oligo_ids=rna_oligo_ids,
        )

        return rna_oligos_unarchive

    @property
    def rna_oligo_ids(self) -> List[str]:
        if isinstance(self._rna_oligo_ids, Unset):
            raise NotPresentError(self, "rna_oligo_ids")
        return self._rna_oligo_ids

    @rna_oligo_ids.setter
    def rna_oligo_ids(self, value: List[str]) -> None:
        self._rna_oligo_ids = value
