from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.lab_automation_benchling_app_error import LabAutomationBenchlingAppError
from ..types import UNSET, Unset

T = TypeVar("T", bound="LabAutomationTransformUpdate")


@attr.s(auto_attribs=True, repr=False)
class LabAutomationTransformUpdate:
    """  """

    _blob_id: Union[Unset, str] = UNSET
    _errors: Union[Unset, List[LabAutomationBenchlingAppError]] = UNSET

    def __repr__(self):
        fields = []
        fields.append("blob_id={}".format(repr(self._blob_id)))
        fields.append("errors={}".format(repr(self._errors)))
        return "LabAutomationTransformUpdate({})".format(", ".join(fields))

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

        def get_blob_id() -> Union[Unset, str]:
            blob_id = d.pop("blobId")
            return blob_id

        blob_id = get_blob_id() if "blobId" in d else cast(Union[Unset, str], UNSET)

        def get_errors() -> Union[Unset, List[LabAutomationBenchlingAppError]]:
            errors = []
            _errors = d.pop("errors")
            for errors_item_data in _errors or []:
                errors_item = LabAutomationBenchlingAppError.from_dict(errors_item_data)

                errors.append(errors_item)

            return errors

        errors = (
            get_errors() if "errors" in d else cast(Union[Unset, List[LabAutomationBenchlingAppError]], UNSET)
        )

        lab_automation_transform_update = cls(
            blob_id=blob_id,
            errors=errors,
        )

        return lab_automation_transform_update

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
    def errors(self) -> List[LabAutomationBenchlingAppError]:
        if isinstance(self._errors, Unset):
            raise NotPresentError(self, "errors")
        return self._errors

    @errors.setter
    def errors(self, value: List[LabAutomationBenchlingAppError]) -> None:
        self._errors = value

    @errors.deleter
    def errors(self) -> None:
        self._errors = UNSET
