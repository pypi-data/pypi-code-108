from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="AssayResultIdsRequest")


@attr.s(auto_attribs=True, repr=False)
class AssayResultIdsRequest:
    """  """

    _assay_result_ids: List[str]

    def __repr__(self):
        fields = []
        fields.append("assay_result_ids={}".format(repr(self._assay_result_ids)))
        return "AssayResultIdsRequest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        assay_result_ids = self._assay_result_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "assayResultIds": assay_result_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_assay_result_ids() -> List[str]:
            assay_result_ids = cast(List[str], d.pop("assayResultIds"))

            return assay_result_ids

        assay_result_ids = get_assay_result_ids() if "assayResultIds" in d else cast(List[str], UNSET)

        assay_result_ids_request = cls(
            assay_result_ids=assay_result_ids,
        )

        return assay_result_ids_request

    @property
    def assay_result_ids(self) -> List[str]:
        if isinstance(self._assay_result_ids, Unset):
            raise NotPresentError(self, "assay_result_ids")
        return self._assay_result_ids

    @assay_result_ids.setter
    def assay_result_ids(self, value: List[str]) -> None:
        self._assay_result_ids = value
