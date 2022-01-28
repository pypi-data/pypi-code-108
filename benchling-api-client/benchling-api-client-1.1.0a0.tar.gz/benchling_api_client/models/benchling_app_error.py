from typing import Any, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.benchling_app_error_errors import BenchlingAppErrorErrors
from ..types import UNSET, Unset

T = TypeVar("T", bound="BenchlingAppError")


@attr.s(auto_attribs=True, repr=False)
class BenchlingAppError:
    """  """

    _errors: Union[Unset, BenchlingAppErrorErrors] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("errors={}".format(repr(self._errors)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "BenchlingAppError({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        errors: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._errors, Unset):
            errors = self._errors.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if errors is not UNSET:
            field_dict["errors"] = errors

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        errors: Union[Unset, BenchlingAppErrorErrors] = UNSET
        _errors = d.pop("errors", UNSET)
        if not isinstance(_errors, Unset):
            errors = BenchlingAppErrorErrors.from_dict(_errors)

        benchling_app_error = cls(
            errors=errors,
        )

        benchling_app_error.additional_properties = d
        return benchling_app_error

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
    def errors(self) -> BenchlingAppErrorErrors:
        if isinstance(self._errors, Unset):
            raise NotPresentError(self, "errors")
        return self._errors

    @errors.setter
    def errors(self, value: BenchlingAppErrorErrors) -> None:
        self._errors = value

    @errors.deleter
    def errors(self) -> None:
        self._errors = UNSET
