from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.assay_result_create import AssayResultCreate
from ..types import UNSET, Unset

T = TypeVar("T", bound="AssayResultsBulkCreateRequest")


@attr.s(auto_attribs=True, repr=False)
class AssayResultsBulkCreateRequest:
    """  """

    _assay_results: List[AssayResultCreate]

    def __repr__(self):
        fields = []
        fields.append("assay_results={}".format(repr(self._assay_results)))
        return "AssayResultsBulkCreateRequest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        assay_results = []
        for assay_results_item_data in self._assay_results:
            assay_results_item = assay_results_item_data.to_dict()

            assay_results.append(assay_results_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "assayResults": assay_results,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_assay_results() -> List[AssayResultCreate]:
            assay_results = []
            _assay_results = d.pop("assayResults")
            for assay_results_item_data in _assay_results:
                assay_results_item = AssayResultCreate.from_dict(assay_results_item_data)

                assay_results.append(assay_results_item)

            return assay_results

        assay_results = get_assay_results() if "assayResults" in d else cast(List[AssayResultCreate], UNSET)

        assay_results_bulk_create_request = cls(
            assay_results=assay_results,
        )

        return assay_results_bulk_create_request

    @property
    def assay_results(self) -> List[AssayResultCreate]:
        if isinstance(self._assay_results, Unset):
            raise NotPresentError(self, "assay_results")
        return self._assay_results

    @assay_results.setter
    def assay_results(self, value: List[AssayResultCreate]) -> None:
        self._assay_results = value
