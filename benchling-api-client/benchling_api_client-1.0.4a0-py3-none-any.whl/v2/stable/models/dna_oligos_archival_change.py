from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="DnaOligosArchivalChange")


@attr.s(auto_attribs=True, repr=False)
class DnaOligosArchivalChange:
    """IDs of all items that were archived or unarchived, grouped by resource type. This includes the IDs of DNA Oligos along with any IDs of batches that were archived / unarchived."""

    _batch_ids: Union[Unset, List[str]] = UNSET
    _dna_oligo_ids: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("batch_ids={}".format(repr(self._batch_ids)))
        fields.append("dna_oligo_ids={}".format(repr(self._dna_oligo_ids)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "DnaOligosArchivalChange({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        batch_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._batch_ids, Unset):
            batch_ids = self._batch_ids

        dna_oligo_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._dna_oligo_ids, Unset):
            dna_oligo_ids = self._dna_oligo_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if batch_ids is not UNSET:
            field_dict["batchIds"] = batch_ids
        if dna_oligo_ids is not UNSET:
            field_dict["dnaOligoIds"] = dna_oligo_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_batch_ids() -> Union[Unset, List[str]]:
            batch_ids = cast(List[str], d.pop("batchIds"))

            return batch_ids

        batch_ids = get_batch_ids() if "batchIds" in d else cast(Union[Unset, List[str]], UNSET)

        def get_dna_oligo_ids() -> Union[Unset, List[str]]:
            dna_oligo_ids = cast(List[str], d.pop("dnaOligoIds"))

            return dna_oligo_ids

        dna_oligo_ids = get_dna_oligo_ids() if "dnaOligoIds" in d else cast(Union[Unset, List[str]], UNSET)

        dna_oligos_archival_change = cls(
            batch_ids=batch_ids,
            dna_oligo_ids=dna_oligo_ids,
        )

        dna_oligos_archival_change.additional_properties = d
        return dna_oligos_archival_change

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
    def batch_ids(self) -> List[str]:
        if isinstance(self._batch_ids, Unset):
            raise NotPresentError(self, "batch_ids")
        return self._batch_ids

    @batch_ids.setter
    def batch_ids(self, value: List[str]) -> None:
        self._batch_ids = value

    @batch_ids.deleter
    def batch_ids(self) -> None:
        self._batch_ids = UNSET

    @property
    def dna_oligo_ids(self) -> List[str]:
        if isinstance(self._dna_oligo_ids, Unset):
            raise NotPresentError(self, "dna_oligo_ids")
        return self._dna_oligo_ids

    @dna_oligo_ids.setter
    def dna_oligo_ids(self, value: List[str]) -> None:
        self._dna_oligo_ids = value

    @dna_oligo_ids.deleter
    def dna_oligo_ids(self) -> None:
        self._dna_oligo_ids = UNSET
