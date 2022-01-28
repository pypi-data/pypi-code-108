from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="FoldersArchivalChange")


@attr.s(auto_attribs=True, repr=False)
class FoldersArchivalChange:
    """IDs of all items that were archived or unarchived, grouped by resource type. This includes the IDs of folders along with any IDs of folder contents that were unarchived."""

    _aa_sequence_ids: Union[Unset, List[str]] = UNSET
    _custom_entity_ids: Union[Unset, List[str]] = UNSET
    _dna_sequence_ids: Union[Unset, List[str]] = UNSET
    _entry_ids: Union[Unset, List[str]] = UNSET
    _folder_ids: Union[Unset, List[str]] = UNSET
    _mixture_ids: Union[Unset, List[str]] = UNSET
    _oligo_ids: Union[Unset, List[str]] = UNSET
    _protocol_ids: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("aa_sequence_ids={}".format(repr(self._aa_sequence_ids)))
        fields.append("custom_entity_ids={}".format(repr(self._custom_entity_ids)))
        fields.append("dna_sequence_ids={}".format(repr(self._dna_sequence_ids)))
        fields.append("entry_ids={}".format(repr(self._entry_ids)))
        fields.append("folder_ids={}".format(repr(self._folder_ids)))
        fields.append("mixture_ids={}".format(repr(self._mixture_ids)))
        fields.append("oligo_ids={}".format(repr(self._oligo_ids)))
        fields.append("protocol_ids={}".format(repr(self._protocol_ids)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "FoldersArchivalChange({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        aa_sequence_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._aa_sequence_ids, Unset):
            aa_sequence_ids = self._aa_sequence_ids

        custom_entity_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._custom_entity_ids, Unset):
            custom_entity_ids = self._custom_entity_ids

        dna_sequence_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._dna_sequence_ids, Unset):
            dna_sequence_ids = self._dna_sequence_ids

        entry_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._entry_ids, Unset):
            entry_ids = self._entry_ids

        folder_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._folder_ids, Unset):
            folder_ids = self._folder_ids

        mixture_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._mixture_ids, Unset):
            mixture_ids = self._mixture_ids

        oligo_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._oligo_ids, Unset):
            oligo_ids = self._oligo_ids

        protocol_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._protocol_ids, Unset):
            protocol_ids = self._protocol_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if aa_sequence_ids is not UNSET:
            field_dict["aaSequenceIds"] = aa_sequence_ids
        if custom_entity_ids is not UNSET:
            field_dict["customEntityIds"] = custom_entity_ids
        if dna_sequence_ids is not UNSET:
            field_dict["dnaSequenceIds"] = dna_sequence_ids
        if entry_ids is not UNSET:
            field_dict["entryIds"] = entry_ids
        if folder_ids is not UNSET:
            field_dict["folderIds"] = folder_ids
        if mixture_ids is not UNSET:
            field_dict["mixtureIds"] = mixture_ids
        if oligo_ids is not UNSET:
            field_dict["oligoIds"] = oligo_ids
        if protocol_ids is not UNSET:
            field_dict["protocolIds"] = protocol_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_aa_sequence_ids() -> Union[Unset, List[str]]:
            aa_sequence_ids = cast(List[str], d.pop("aaSequenceIds"))

            return aa_sequence_ids

        aa_sequence_ids = (
            get_aa_sequence_ids() if "aaSequenceIds" in d else cast(Union[Unset, List[str]], UNSET)
        )

        def get_custom_entity_ids() -> Union[Unset, List[str]]:
            custom_entity_ids = cast(List[str], d.pop("customEntityIds"))

            return custom_entity_ids

        custom_entity_ids = (
            get_custom_entity_ids() if "customEntityIds" in d else cast(Union[Unset, List[str]], UNSET)
        )

        def get_dna_sequence_ids() -> Union[Unset, List[str]]:
            dna_sequence_ids = cast(List[str], d.pop("dnaSequenceIds"))

            return dna_sequence_ids

        dna_sequence_ids = (
            get_dna_sequence_ids() if "dnaSequenceIds" in d else cast(Union[Unset, List[str]], UNSET)
        )

        def get_entry_ids() -> Union[Unset, List[str]]:
            entry_ids = cast(List[str], d.pop("entryIds"))

            return entry_ids

        entry_ids = get_entry_ids() if "entryIds" in d else cast(Union[Unset, List[str]], UNSET)

        def get_folder_ids() -> Union[Unset, List[str]]:
            folder_ids = cast(List[str], d.pop("folderIds"))

            return folder_ids

        folder_ids = get_folder_ids() if "folderIds" in d else cast(Union[Unset, List[str]], UNSET)

        def get_mixture_ids() -> Union[Unset, List[str]]:
            mixture_ids = cast(List[str], d.pop("mixtureIds"))

            return mixture_ids

        mixture_ids = get_mixture_ids() if "mixtureIds" in d else cast(Union[Unset, List[str]], UNSET)

        def get_oligo_ids() -> Union[Unset, List[str]]:
            oligo_ids = cast(List[str], d.pop("oligoIds"))

            return oligo_ids

        oligo_ids = get_oligo_ids() if "oligoIds" in d else cast(Union[Unset, List[str]], UNSET)

        def get_protocol_ids() -> Union[Unset, List[str]]:
            protocol_ids = cast(List[str], d.pop("protocolIds"))

            return protocol_ids

        protocol_ids = get_protocol_ids() if "protocolIds" in d else cast(Union[Unset, List[str]], UNSET)

        folders_archival_change = cls(
            aa_sequence_ids=aa_sequence_ids,
            custom_entity_ids=custom_entity_ids,
            dna_sequence_ids=dna_sequence_ids,
            entry_ids=entry_ids,
            folder_ids=folder_ids,
            mixture_ids=mixture_ids,
            oligo_ids=oligo_ids,
            protocol_ids=protocol_ids,
        )

        folders_archival_change.additional_properties = d
        return folders_archival_change

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
    def aa_sequence_ids(self) -> List[str]:
        if isinstance(self._aa_sequence_ids, Unset):
            raise NotPresentError(self, "aa_sequence_ids")
        return self._aa_sequence_ids

    @aa_sequence_ids.setter
    def aa_sequence_ids(self, value: List[str]) -> None:
        self._aa_sequence_ids = value

    @aa_sequence_ids.deleter
    def aa_sequence_ids(self) -> None:
        self._aa_sequence_ids = UNSET

    @property
    def custom_entity_ids(self) -> List[str]:
        if isinstance(self._custom_entity_ids, Unset):
            raise NotPresentError(self, "custom_entity_ids")
        return self._custom_entity_ids

    @custom_entity_ids.setter
    def custom_entity_ids(self, value: List[str]) -> None:
        self._custom_entity_ids = value

    @custom_entity_ids.deleter
    def custom_entity_ids(self) -> None:
        self._custom_entity_ids = UNSET

    @property
    def dna_sequence_ids(self) -> List[str]:
        if isinstance(self._dna_sequence_ids, Unset):
            raise NotPresentError(self, "dna_sequence_ids")
        return self._dna_sequence_ids

    @dna_sequence_ids.setter
    def dna_sequence_ids(self, value: List[str]) -> None:
        self._dna_sequence_ids = value

    @dna_sequence_ids.deleter
    def dna_sequence_ids(self) -> None:
        self._dna_sequence_ids = UNSET

    @property
    def entry_ids(self) -> List[str]:
        if isinstance(self._entry_ids, Unset):
            raise NotPresentError(self, "entry_ids")
        return self._entry_ids

    @entry_ids.setter
    def entry_ids(self, value: List[str]) -> None:
        self._entry_ids = value

    @entry_ids.deleter
    def entry_ids(self) -> None:
        self._entry_ids = UNSET

    @property
    def folder_ids(self) -> List[str]:
        if isinstance(self._folder_ids, Unset):
            raise NotPresentError(self, "folder_ids")
        return self._folder_ids

    @folder_ids.setter
    def folder_ids(self, value: List[str]) -> None:
        self._folder_ids = value

    @folder_ids.deleter
    def folder_ids(self) -> None:
        self._folder_ids = UNSET

    @property
    def mixture_ids(self) -> List[str]:
        if isinstance(self._mixture_ids, Unset):
            raise NotPresentError(self, "mixture_ids")
        return self._mixture_ids

    @mixture_ids.setter
    def mixture_ids(self, value: List[str]) -> None:
        self._mixture_ids = value

    @mixture_ids.deleter
    def mixture_ids(self) -> None:
        self._mixture_ids = UNSET

    @property
    def oligo_ids(self) -> List[str]:
        if isinstance(self._oligo_ids, Unset):
            raise NotPresentError(self, "oligo_ids")
        return self._oligo_ids

    @oligo_ids.setter
    def oligo_ids(self, value: List[str]) -> None:
        self._oligo_ids = value

    @oligo_ids.deleter
    def oligo_ids(self) -> None:
        self._oligo_ids = UNSET

    @property
    def protocol_ids(self) -> List[str]:
        if isinstance(self._protocol_ids, Unset):
            raise NotPresentError(self, "protocol_ids")
        return self._protocol_ids

    @protocol_ids.setter
    def protocol_ids(self, value: List[str]) -> None:
        self._protocol_ids = value

    @protocol_ids.deleter
    def protocol_ids(self) -> None:
        self._protocol_ids = UNSET
