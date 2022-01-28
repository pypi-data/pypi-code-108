from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.benchling_app_error import BenchlingAppError
from ..types import UNSET, Unset

T = TypeVar("T", bound="TransformPatch")


@attr.s(auto_attribs=True, repr=False)
class TransformPatch:
    """  """

    _blob_id: Union[Unset, str] = UNSET
    _errors: Union[Unset, List[BenchlingAppError]] = UNSET

    def __repr__(self):
        fields = []
        fields.append("blob_id={}".format(repr(self._blob_id)))
        fields.append("errors={}".format(repr(self._errors)))
        return "TransformPatch({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        blob_id = self._blob_id
        errors: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._errors, Unset):
            errors = []
            for errors_item_data in self._errors:
                errors_item = errors_item_data.to_dict()

                errors.append(errors_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if blob_id is not UNSET:
            field_dict["blobId"] = blob_id
        if errors is not UNSET:
            field_dict["errors"] = errors

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        blob_id = d.pop("blobId", UNSET)

        errors = []
        _errors = d.pop("errors", UNSET)
        for errors_item_data in _errors or []:
            errors_item = BenchlingAppError.from_dict(errors_item_data)

            errors.append(errors_item)

        transform_patch = cls(
            blob_id=blob_id,
            errors=errors,
        )

        return transform_patch

    @property
    def blob_id(self) -> str:
        if isinstance(self._blob_id, Unset):
            raise NotPresentError(self, "blob_id")
        return self._blob_id

    @blob_id.setter
    def blob_id(self, value: str) -> None:
        self._blob_id = value

    @blob_id.deleter
    def blob_id(self) -> None:
        self._blob_id = UNSET

    @property
    def errors(self) -> List[BenchlingAppError]:
        if isinstance(self._errors, Unset):
            raise NotPresentError(self, "errors")
        return self._errors

    @errors.setter
    def errors(self, value: List[BenchlingAppError]) -> None:
        self._errors = value

    @errors.deleter
    def errors(self) -> None:
        self._errors = UNSET
