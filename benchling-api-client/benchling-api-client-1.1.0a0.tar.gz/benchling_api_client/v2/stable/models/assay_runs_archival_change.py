from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="AssayRunsArchivalChange")


@attr.s(auto_attribs=True, repr=False)
class AssayRunsArchivalChange:
    """IDs of all Assay Runs that were archived / unarchived."""

    _assay_run_ids: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("assay_run_ids={}".format(repr(self._assay_run_ids)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "AssayRunsArchivalChange({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        assay_run_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._assay_run_ids, Unset):
            assay_run_ids = self._assay_run_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if assay_run_ids is not UNSET:
            field_dict["assayRunIds"] = assay_run_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_assay_run_ids() -> Union[Unset, List[str]]:
            assay_run_ids = cast(List[str], d.pop("assayRunIds"))

            return assay_run_ids

        assay_run_ids = get_assay_run_ids() if "assayRunIds" in d else cast(Union[Unset, List[str]], UNSET)

        assay_runs_archival_change = cls(
            assay_run_ids=assay_run_ids,
        )

        assay_runs_archival_change.additional_properties = d
        return assay_runs_archival_change

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
    def assay_run_ids(self) -> List[str]:
        if isinstance(self._assay_run_ids, Unset):
            raise NotPresentError(self, "assay_run_ids")
        return self._assay_run_ids

    @assay_run_ids.setter
    def assay_run_ids(self, value: List[str]) -> None:
        self._assay_run_ids = value

    @assay_run_ids.deleter
    def assay_run_ids(self) -> None:
        self._assay_run_ids = UNSET
