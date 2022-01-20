from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.entity_archive_reason import EntityArchiveReason
from ..types import UNSET, Unset

T = TypeVar("T", bound="DnaOligosArchive")


@attr.s(auto_attribs=True, repr=False)
class DnaOligosArchive:
    """The request body for archiving DNA Oligos."""

    _dna_oligo_ids: List[str]
    _reason: EntityArchiveReason

    def __repr__(self):
        fields = []
        fields.append("dna_oligo_ids={}".format(repr(self._dna_oligo_ids)))
        fields.append("reason={}".format(repr(self._reason)))
        return "DnaOligosArchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        dna_oligo_ids = self._dna_oligo_ids

        reason = self._reason.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "dnaOligoIds": dna_oligo_ids,
                "reason": reason,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_dna_oligo_ids() -> List[str]:
            dna_oligo_ids = cast(List[str], d.pop("dnaOligoIds"))

            return dna_oligo_ids

        dna_oligo_ids = get_dna_oligo_ids() if "dnaOligoIds" in d else cast(List[str], UNSET)

        def get_reason() -> EntityArchiveReason:
            _reason = d.pop("reason")
            try:
                reason = EntityArchiveReason(_reason)
            except ValueError:
                reason = EntityArchiveReason.of_unknown(_reason)

            return reason

        reason = get_reason() if "reason" in d else cast(EntityArchiveReason, UNSET)

        dna_oligos_archive = cls(
            dna_oligo_ids=dna_oligo_ids,
            reason=reason,
        )

        return dna_oligos_archive

    @property
    def dna_oligo_ids(self) -> List[str]:
        if isinstance(self._dna_oligo_ids, Unset):
            raise NotPresentError(self, "dna_oligo_ids")
        return self._dna_oligo_ids

    @dna_oligo_ids.setter
    def dna_oligo_ids(self, value: List[str]) -> None:
        self._dna_oligo_ids = value

    @property
    def reason(self) -> EntityArchiveReason:
        """The reason for archiving the provided entities. Accepted reasons may differ based on tenant configuration."""
        if isinstance(self._reason, Unset):
            raise NotPresentError(self, "reason")
        return self._reason

    @reason.setter
    def reason(self, value: EntityArchiveReason) -> None:
        self._reason = value
