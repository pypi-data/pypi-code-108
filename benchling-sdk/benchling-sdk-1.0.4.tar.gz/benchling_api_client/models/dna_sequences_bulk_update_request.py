from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.dna_sequence_bulk_update import DnaSequenceBulkUpdate
from ..types import UNSET, Unset

T = TypeVar("T", bound="DnaSequencesBulkUpdateRequest")


@attr.s(auto_attribs=True, repr=False)
class DnaSequencesBulkUpdateRequest:
    """  """

    _dna_sequences: Union[Unset, List[DnaSequenceBulkUpdate]] = UNSET

    def __repr__(self):
        fields = []
        fields.append("dna_sequences={}".format(repr(self._dna_sequences)))
        return "DnaSequencesBulkUpdateRequest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        dna_sequences: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._dna_sequences, Unset):
            dna_sequences = []
            for dna_sequences_item_data in self._dna_sequences:
                dna_sequences_item = dna_sequences_item_data.to_dict()

                dna_sequences.append(dna_sequences_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if dna_sequences is not UNSET:
            field_dict["dnaSequences"] = dna_sequences

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_dna_sequences() -> Union[Unset, List[DnaSequenceBulkUpdate]]:
            dna_sequences = []
            _dna_sequences = d.pop("dnaSequences")
            for dna_sequences_item_data in _dna_sequences or []:
                dna_sequences_item = DnaSequenceBulkUpdate.from_dict(dna_sequences_item_data)

                dna_sequences.append(dna_sequences_item)

            return dna_sequences

        dna_sequences = (
            get_dna_sequences()
            if "dnaSequences" in d
            else cast(Union[Unset, List[DnaSequenceBulkUpdate]], UNSET)
        )

        dna_sequences_bulk_update_request = cls(
            dna_sequences=dna_sequences,
        )

        return dna_sequences_bulk_update_request

    @property
    def dna_sequences(self) -> List[DnaSequenceBulkUpdate]:
        if isinstance(self._dna_sequences, Unset):
            raise NotPresentError(self, "dna_sequences")
        return self._dna_sequences

    @dna_sequences.setter
    def dna_sequences(self, value: List[DnaSequenceBulkUpdate]) -> None:
        self._dna_sequences = value

    @dna_sequences.deleter
    def dna_sequences(self) -> None:
        self._dna_sequences = UNSET
