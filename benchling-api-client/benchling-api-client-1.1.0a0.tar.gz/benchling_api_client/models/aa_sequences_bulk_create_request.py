from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.aa_sequence_bulk_create import AaSequenceBulkCreate
from ..types import UNSET, Unset

T = TypeVar("T", bound="AaSequencesBulkCreateRequest")


@attr.s(auto_attribs=True, repr=False)
class AaSequencesBulkCreateRequest:
    """  """

    _aa_sequences: Union[Unset, List[AaSequenceBulkCreate]] = UNSET

    def __repr__(self):
        fields = []
        fields.append("aa_sequences={}".format(repr(self._aa_sequences)))
        return "AaSequencesBulkCreateRequest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        aa_sequences: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._aa_sequences, Unset):
            aa_sequences = []
            for aa_sequences_item_data in self._aa_sequences:
                aa_sequences_item = aa_sequences_item_data.to_dict()

                aa_sequences.append(aa_sequences_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if aa_sequences is not UNSET:
            field_dict["aaSequences"] = aa_sequences

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_aa_sequences() -> Union[Unset, List[AaSequenceBulkCreate]]:
            aa_sequences = []
            _aa_sequences = d.pop("aaSequences")
            for aa_sequences_item_data in _aa_sequences or []:
                aa_sequences_item = AaSequenceBulkCreate.from_dict(aa_sequences_item_data)

                aa_sequences.append(aa_sequences_item)

            return aa_sequences

        aa_sequences = (
            get_aa_sequences()
            if "aaSequences" in d
            else cast(Union[Unset, List[AaSequenceBulkCreate]], UNSET)
        )

        aa_sequences_bulk_create_request = cls(
            aa_sequences=aa_sequences,
        )

        return aa_sequences_bulk_create_request

    @property
    def aa_sequences(self) -> List[AaSequenceBulkCreate]:
        if isinstance(self._aa_sequences, Unset):
            raise NotPresentError(self, "aa_sequences")
        return self._aa_sequences

    @aa_sequences.setter
    def aa_sequences(self, value: List[AaSequenceBulkCreate]) -> None:
        self._aa_sequences = value

    @aa_sequences.deleter
    def aa_sequences(self) -> None:
        self._aa_sequences = UNSET
