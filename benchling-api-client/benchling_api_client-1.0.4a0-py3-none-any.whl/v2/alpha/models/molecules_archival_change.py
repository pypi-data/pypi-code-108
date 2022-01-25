from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="MoleculesArchivalChange")


@attr.s(auto_attribs=True, repr=False)
class MoleculesArchivalChange:
    """IDs of all items that were archived or unarchived, grouped by resource type. This includes the IDs of Molecules along with any IDs of batches that were archived / unarchived."""

    _batch_ids: Union[Unset, List[str]] = UNSET
    _molecule_ids: Union[Unset, List[str]] = UNSET

    def __repr__(self):
        fields = []
        fields.append("batch_ids={}".format(repr(self._batch_ids)))
        fields.append("molecule_ids={}".format(repr(self._molecule_ids)))
        return "MoleculesArchivalChange({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        batch_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._batch_ids, Unset):
            batch_ids = self._batch_ids

        molecule_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._molecule_ids, Unset):
            molecule_ids = self._molecule_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if batch_ids is not UNSET:
            field_dict["batchIds"] = batch_ids
        if molecule_ids is not UNSET:
            field_dict["moleculeIds"] = molecule_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_batch_ids() -> Union[Unset, List[str]]:
            batch_ids = cast(List[str], d.pop("batchIds"))

            return batch_ids

        batch_ids = get_batch_ids() if "batchIds" in d else cast(Union[Unset, List[str]], UNSET)

        def get_molecule_ids() -> Union[Unset, List[str]]:
            molecule_ids = cast(List[str], d.pop("moleculeIds"))

            return molecule_ids

        molecule_ids = get_molecule_ids() if "moleculeIds" in d else cast(Union[Unset, List[str]], UNSET)

        molecules_archival_change = cls(
            batch_ids=batch_ids,
            molecule_ids=molecule_ids,
        )

        return molecules_archival_change

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
    def molecule_ids(self) -> List[str]:
        if isinstance(self._molecule_ids, Unset):
            raise NotPresentError(self, "molecule_ids")
        return self._molecule_ids

    @molecule_ids.setter
    def molecule_ids(self, value: List[str]) -> None:
        self._molecule_ids = value

    @molecule_ids.deleter
    def molecule_ids(self) -> None:
        self._molecule_ids = UNSET
