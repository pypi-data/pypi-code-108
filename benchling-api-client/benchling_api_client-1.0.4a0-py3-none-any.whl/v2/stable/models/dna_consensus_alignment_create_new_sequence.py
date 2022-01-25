from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="DnaConsensusAlignmentCreateNewSequence")


@attr.s(auto_attribs=True, repr=False)
class DnaConsensusAlignmentCreateNewSequence:
    """  """

    _folder_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("folder_id={}".format(repr(self._folder_id)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "DnaConsensusAlignmentCreateNewSequence({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        folder_id = self._folder_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if folder_id is not UNSET:
            field_dict["folderId"] = folder_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_folder_id() -> Union[Unset, str]:
            folder_id = d.pop("folderId")
            return folder_id

        folder_id = get_folder_id() if "folderId" in d else cast(Union[Unset, str], UNSET)

        dna_consensus_alignment_create_new_sequence = cls(
            folder_id=folder_id,
        )

        dna_consensus_alignment_create_new_sequence.additional_properties = d
        return dna_consensus_alignment_create_new_sequence

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
    def folder_id(self) -> str:
        if isinstance(self._folder_id, Unset):
            raise NotPresentError(self, "folder_id")
        return self._folder_id

    @folder_id.setter
    def folder_id(self, value: str) -> None:
        self._folder_id = value

    @folder_id.deleter
    def folder_id(self) -> None:
        self._folder_id = UNSET
