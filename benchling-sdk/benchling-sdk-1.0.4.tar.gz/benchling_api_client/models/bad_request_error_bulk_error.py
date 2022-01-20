from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.bad_request_error_bulk_error_errors_item import BadRequestErrorBulkErrorErrorsItem
from ..types import UNSET, Unset

T = TypeVar("T", bound="BadRequestErrorBulkError")


@attr.s(auto_attribs=True, repr=False)
class BadRequestErrorBulkError:
    """  """

    _errors: Union[Unset, List[BadRequestErrorBulkErrorErrorsItem]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("errors={}".format(repr(self._errors)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "BadRequestErrorBulkError({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        errors: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._errors, Unset):
            errors = []
            for errors_item_data in self._errors:
                errors_item = errors_item_data.to_dict()

                errors.append(errors_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if errors is not UNSET:
            field_dict["errors"] = errors

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_errors() -> Union[Unset, List[BadRequestErrorBulkErrorErrorsItem]]:
            errors = []
            _errors = d.pop("errors")
            for errors_item_data in _errors or []:
                errors_item = BadRequestErrorBulkErrorErrorsItem.from_dict(errors_item_data)

                errors.append(errors_item)

            return errors

        errors = (
            get_errors()
            if "errors" in d
            else cast(Union[Unset, List[BadRequestErrorBulkErrorErrorsItem]], UNSET)
        )

        bad_request_error_bulk_error = cls(
            errors=errors,
        )

        bad_request_error_bulk_error.additional_properties = d
        return bad_request_error_bulk_error

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
    def errors(self) -> List[BadRequestErrorBulkErrorErrorsItem]:
        if isinstance(self._errors, Unset):
            raise NotPresentError(self, "errors")
        return self._errors

    @errors.setter
    def errors(self, value: List[BadRequestErrorBulkErrorErrorsItem]) -> None:
        self._errors = value

    @errors.deleter
    def errors(self) -> None:
        self._errors = UNSET
