from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.barcode_validation_result import BarcodeValidationResult
from ..types import UNSET, Unset

T = TypeVar("T", bound="BarcodeValidationResults")


@attr.s(auto_attribs=True, repr=False)
class BarcodeValidationResults:
    """  """

    _validation_results: Union[Unset, List[BarcodeValidationResult]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("validation_results={}".format(repr(self._validation_results)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "BarcodeValidationResults({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        validation_results: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._validation_results, Unset):
            validation_results = []
            for validation_results_item_data in self._validation_results:
                validation_results_item = validation_results_item_data.to_dict()

                validation_results.append(validation_results_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if validation_results is not UNSET:
            field_dict["validationResults"] = validation_results

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_validation_results() -> Union[Unset, List[BarcodeValidationResult]]:
            validation_results = []
            _validation_results = d.pop("validationResults")
            for validation_results_item_data in _validation_results or []:
                validation_results_item = BarcodeValidationResult.from_dict(validation_results_item_data)

                validation_results.append(validation_results_item)

            return validation_results

        validation_results = (
            get_validation_results()
            if "validationResults" in d
            else cast(Union[Unset, List[BarcodeValidationResult]], UNSET)
        )

        barcode_validation_results = cls(
            validation_results=validation_results,
        )

        barcode_validation_results.additional_properties = d
        return barcode_validation_results

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
    def validation_results(self) -> List[BarcodeValidationResult]:
        if isinstance(self._validation_results, Unset):
            raise NotPresentError(self, "validation_results")
        return self._validation_results

    @validation_results.setter
    def validation_results(self, value: List[BarcodeValidationResult]) -> None:
        self._validation_results = value

    @validation_results.deleter
    def validation_results(self) -> None:
        self._validation_results = UNSET
