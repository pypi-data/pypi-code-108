from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.entity_archive_reason import EntityArchiveReason
from ..types import UNSET, Unset

T = TypeVar("T", bound="RnaOligosArchive")


@attr.s(auto_attribs=True, repr=False)
class RnaOligosArchive:
    """The request body for archiving RNA Oligos."""

    _reason: EntityArchiveReason
    _rna_oligo_ids: List[str]

    def __repr__(self):
        fields = []
        fields.append("reason={}".format(repr(self._reason)))
        fields.append("rna_oligo_ids={}".format(repr(self._rna_oligo_ids)))
        return "RnaOligosArchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        reason = self._reason.value

        rna_oligo_ids = self._rna_oligo_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "reason": reason,
                "rnaOligoIds": rna_oligo_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_reason() -> EntityArchiveReason:
            _reason = d.pop("reason")
            try:
                reason = EntityArchiveReason(_reason)
            except ValueError:
                reason = EntityArchiveReason.of_unknown(_reason)

            return reason

        reason = get_reason() if "reason" in d else cast(EntityArchiveReason, UNSET)

        def get_rna_oligo_ids() -> List[str]:
            rna_oligo_ids = cast(List[str], d.pop("rnaOligoIds"))

            return rna_oligo_ids

        rna_oligo_ids = get_rna_oligo_ids() if "rnaOligoIds" in d else cast(List[str], UNSET)

        rna_oligos_archive = cls(
            reason=reason,
            rna_oligo_ids=rna_oligo_ids,
        )

        return rna_oligos_archive

    @property
    def reason(self) -> EntityArchiveReason:
        """The reason for archiving the provided entities. Accepted reasons may differ based on tenant configuration."""
        if isinstance(self._reason, Unset):
            raise NotPresentError(self, "reason")
        return self._reason

    @reason.setter
    def reason(self, value: EntityArchiveReason) -> None:
        self._reason = value

    @property
    def rna_oligo_ids(self) -> List[str]:
        if isinstance(self._rna_oligo_ids, Unset):
            raise NotPresentError(self, "rna_oligo_ids")
        return self._rna_oligo_ids

    @rna_oligo_ids.setter
    def rna_oligo_ids(self, value: List[str]) -> None:
        self._rna_oligo_ids = value
