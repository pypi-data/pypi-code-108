from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="AssayRunsUnarchive")


@attr.s(auto_attribs=True, repr=False)
class AssayRunsUnarchive:
    """The request body for unarchiving Assay Runs."""

    _assay_run_ids: List[str]

    def __repr__(self):
        fields = []
        fields.append("assay_run_ids={}".format(repr(self._assay_run_ids)))
        return "AssayRunsUnarchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        assay_run_ids = self._assay_run_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "assayRunIds": assay_run_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_assay_run_ids() -> List[str]:
            assay_run_ids = cast(List[str], d.pop("assayRunIds"))

            return assay_run_ids

        assay_run_ids = get_assay_run_ids() if "assayRunIds" in d else cast(List[str], UNSET)

        assay_runs_unarchive = cls(
            assay_run_ids=assay_run_ids,
        )

        return assay_runs_unarchive

    @property
    def assay_run_ids(self) -> List[str]:
        if isinstance(self._assay_run_ids, Unset):
            raise NotPresentError(self, "assay_run_ids")
        return self._assay_run_ids

    @assay_run_ids.setter
    def assay_run_ids(self, value: List[str]) -> None:
        self._assay_run_ids = value
