from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="AaSequencesUnarchive")


@attr.s(auto_attribs=True, repr=False)
class AaSequencesUnarchive:
    """The request body for unarchiving AA sequences."""

    _aa_sequence_ids: List[str]

    def __repr__(self):
        fields = []
        fields.append("aa_sequence_ids={}".format(repr(self._aa_sequence_ids)))
        return "AaSequencesUnarchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        aa_sequence_ids = self._aa_sequence_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "aaSequenceIds": aa_sequence_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_aa_sequence_ids() -> List[str]:
            aa_sequence_ids = cast(List[str], d.pop("aaSequenceIds"))

            return aa_sequence_ids

        aa_sequence_ids = get_aa_sequence_ids() if "aaSequenceIds" in d else cast(List[str], UNSET)

        aa_sequences_unarchive = cls(
            aa_sequence_ids=aa_sequence_ids,
        )

        return aa_sequences_unarchive

    @property
    def aa_sequence_ids(self) -> List[str]:
        if isinstance(self._aa_sequence_ids, Unset):
            raise NotPresentError(self, "aa_sequence_ids")
        return self._aa_sequence_ids

    @aa_sequence_ids.setter
    def aa_sequence_ids(self, value: List[str]) -> None:
        self._aa_sequence_ids = value
