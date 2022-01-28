from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.assay_results_archive_reason import AssayResultsArchiveReason
from ..types import UNSET, Unset

T = TypeVar("T", bound="AssayResultsArchive")


@attr.s(auto_attribs=True, repr=False)
class AssayResultsArchive:
    """  """

    _assay_result_ids: List[str]
    _reason: Union[Unset, AssayResultsArchiveReason] = UNSET

    def __repr__(self):
        fields = []
        fields.append("assay_result_ids={}".format(repr(self._assay_result_ids)))
        fields.append("reason={}".format(repr(self._reason)))
        return "AssayResultsArchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        assay_result_ids = self._assay_result_ids

        reason: Union[Unset, int] = UNSET
        if not isinstance(self._reason, Unset):
            reason = self._reason.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "assayResultIds": assay_result_ids,
            }
        )
        if reason is not UNSET:
            field_dict["reason"] = reason

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_assay_result_ids() -> List[str]:
            assay_result_ids = cast(List[str], d.pop("assayResultIds"))

            return assay_result_ids

        assay_result_ids = get_assay_result_ids() if "assayResultIds" in d else cast(List[str], UNSET)

        def get_reason() -> Union[Unset, AssayResultsArchiveReason]:
            reason = None
            _reason = d.pop("reason")
            if _reason is not None and _reason is not UNSET:
                try:
                    reason = AssayResultsArchiveReason(_reason)
                except ValueError:
                    reason = AssayResultsArchiveReason.of_unknown(_reason)

            return reason

        reason = get_reason() if "reason" in d else cast(Union[Unset, AssayResultsArchiveReason], UNSET)

        assay_results_archive = cls(
            assay_result_ids=assay_result_ids,
            reason=reason,
        )

        return assay_results_archive

    @property
    def assay_result_ids(self) -> List[str]:
        if isinstance(self._assay_result_ids, Unset):
            raise NotPresentError(self, "assay_result_ids")
        return self._assay_result_ids

    @assay_result_ids.setter
    def assay_result_ids(self, value: List[str]) -> None:
        self._assay_result_ids = value

    @property
    def reason(self) -> AssayResultsArchiveReason:
        """ The reason for archiving the provided results. Accepted reasons may differ based on tenant configuration """
        if isinstance(self._reason, Unset):
            raise NotPresentError(self, "reason")
        return self._reason

    @reason.setter
    def reason(self, value: AssayResultsArchiveReason) -> None:
        self._reason = value

    @reason.deleter
    def reason(self) -> None:
        self._reason = UNSET
