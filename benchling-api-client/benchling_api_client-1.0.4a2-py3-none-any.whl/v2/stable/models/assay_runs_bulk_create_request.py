from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.assay_run_create import AssayRunCreate
from ..types import UNSET, Unset

T = TypeVar("T", bound="AssayRunsBulkCreateRequest")


@attr.s(auto_attribs=True, repr=False)
class AssayRunsBulkCreateRequest:
    """  """

    _assay_runs: List[AssayRunCreate]

    def __repr__(self):
        fields = []
        fields.append("assay_runs={}".format(repr(self._assay_runs)))
        return "AssayRunsBulkCreateRequest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        assay_runs = []
        for assay_runs_item_data in self._assay_runs:
            assay_runs_item = assay_runs_item_data.to_dict()

            assay_runs.append(assay_runs_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "assayRuns": assay_runs,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_assay_runs() -> List[AssayRunCreate]:
            assay_runs = []
            _assay_runs = d.pop("assayRuns")
            for assay_runs_item_data in _assay_runs:
                assay_runs_item = AssayRunCreate.from_dict(assay_runs_item_data)

                assay_runs.append(assay_runs_item)

            return assay_runs

        assay_runs = get_assay_runs() if "assayRuns" in d else cast(List[AssayRunCreate], UNSET)

        assay_runs_bulk_create_request = cls(
            assay_runs=assay_runs,
        )

        return assay_runs_bulk_create_request

    @property
    def assay_runs(self) -> List[AssayRunCreate]:
        if isinstance(self._assay_runs, Unset):
            raise NotPresentError(self, "assay_runs")
        return self._assay_runs

    @assay_runs.setter
    def assay_runs(self, value: List[AssayRunCreate]) -> None:
        self._assay_runs = value
