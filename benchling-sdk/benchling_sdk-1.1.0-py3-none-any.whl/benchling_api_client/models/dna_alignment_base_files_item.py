from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="DnaAlignmentBaseFilesItem")


@attr.s(auto_attribs=True, repr=False)
class DnaAlignmentBaseFilesItem:
    """  """

    _sequence_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("sequence_id={}".format(repr(self._sequence_id)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "DnaAlignmentBaseFilesItem({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        sequence_id = self._sequence_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if sequence_id is not UNSET:
            field_dict["sequenceId"] = sequence_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_sequence_id() -> Union[Unset, str]:
            sequence_id = d.pop("sequenceId")
            return sequence_id

        sequence_id = get_sequence_id() if "sequenceId" in d else cast(Union[Unset, str], UNSET)

        dna_alignment_base_files_item = cls(
            sequence_id=sequence_id,
        )

        dna_alignment_base_files_item.additional_properties = d
        return dna_alignment_base_files_item

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
    def sequence_id(self) -> str:
        if isinstance(self._sequence_id, Unset):
            raise NotPresentError(self, "sequence_id")
        return self._sequence_id

    @sequence_id.setter
    def sequence_id(self, value: str) -> None:
        self._sequence_id = value

    @sequence_id.deleter
    def sequence_id(self) -> None:
        self._sequence_id = UNSET
