from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.dna_sequence import DnaSequence
from ..types import UNSET, Unset

T = TypeVar("T", bound="BulkUpdateDnaSequencesAsyncTaskResponse")


@attr.s(auto_attribs=True, repr=False)
class BulkUpdateDnaSequencesAsyncTaskResponse:
    """  """

    _dna_sequences: Union[Unset, List[DnaSequence]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("dna_sequences={}".format(repr(self._dna_sequences)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "BulkUpdateDnaSequencesAsyncTaskResponse({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        dna_sequences: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._dna_sequences, Unset):
            dna_sequences = []
            for dna_sequences_item_data in self._dna_sequences:
                dna_sequences_item = dna_sequences_item_data.to_dict()

                dna_sequences.append(dna_sequences_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if dna_sequences is not UNSET:
            field_dict["dnaSequences"] = dna_sequences

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_dna_sequences() -> Union[Unset, List[DnaSequence]]:
            dna_sequences = []
            _dna_sequences = d.pop("dnaSequences")
            for dna_sequences_item_data in _dna_sequences or []:
                dna_sequences_item = DnaSequence.from_dict(dna_sequences_item_data)

                dna_sequences.append(dna_sequences_item)

            return dna_sequences

        dna_sequences = (
            get_dna_sequences() if "dnaSequences" in d else cast(Union[Unset, List[DnaSequence]], UNSET)
        )

        bulk_update_dna_sequences_async_task_response = cls(
            dna_sequences=dna_sequences,
        )

        bulk_update_dna_sequences_async_task_response.additional_properties = d
        return bulk_update_dna_sequences_async_task_response

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

    def get(self, key, default=None) -> Optional[Any]:
        return self.additional_properties.get(key, default)

    @property
    def dna_sequences(self) -> List[DnaSequence]:
        if isinstance(self._dna_sequences, Unset):
            raise NotPresentError(self, "dna_sequences")
        return self._dna_sequences

    @dna_sequences.setter
    def dna_sequences(self, value: List[DnaSequence]) -> None:
        self._dna_sequences = value

    @dna_sequences.deleter
    def dna_sequences(self) -> None:
        self._dna_sequences = UNSET
