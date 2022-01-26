from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="BarcodeValidationResult")


@attr.s(auto_attribs=True, repr=False)
class BarcodeValidationResult:
    """  """

    _barcode: Union[Unset, str] = UNSET
    _is_valid: Union[Unset, bool] = UNSET
    _message: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("barcode={}".format(repr(self._barcode)))
        fields.append("is_valid={}".format(repr(self._is_valid)))
        fields.append("message={}".format(repr(self._message)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "BarcodeValidationResult({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        barcode = self._barcode
        is_valid = self._is_valid
        message = self._message

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if barcode is not UNSET:
            field_dict["barcode"] = barcode
        if is_valid is not UNSET:
            field_dict["isValid"] = is_valid
        if message is not UNSET:
            field_dict["message"] = message

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_barcode() -> Union[Unset, str]:
            barcode = d.pop("barcode")
            return barcode

        barcode = get_barcode() if "barcode" in d else cast(Union[Unset, str], UNSET)

        def get_is_valid() -> Union[Unset, bool]:
            is_valid = d.pop("isValid")
            return is_valid

        is_valid = get_is_valid() if "isValid" in d else cast(Union[Unset, bool], UNSET)

        def get_message() -> Union[Unset, None, str]:
            message = d.pop("message")
            return message

        message = get_message() if "message" in d else cast(Union[Unset, None, str], UNSET)

        barcode_validation_result = cls(
            barcode=barcode,
            is_valid=is_valid,
            message=message,
        )

        barcode_validation_result.additional_properties = d
        return barcode_validation_result

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
    def barcode(self) -> str:
        """ Barcode to validate. """
        if isinstance(self._barcode, Unset):
            raise NotPresentError(self, "barcode")
        return self._barcode

    @barcode.setter
    def barcode(self, value: str) -> None:
        self._barcode = value

    @barcode.deleter
    def barcode(self) -> None:
        self._barcode = UNSET

    @property
    def is_valid(self) -> bool:
        """ Whether the barcode is valid. """
        if isinstance(self._is_valid, Unset):
            raise NotPresentError(self, "is_valid")
        return self._is_valid

    @is_valid.setter
    def is_valid(self, value: bool) -> None:
        self._is_valid = value

    @is_valid.deleter
    def is_valid(self) -> None:
        self._is_valid = UNSET

    @property
    def message(self) -> Optional[str]:
        """ If barcode is not valid, a message string explaining the error. """
        if isinstance(self._message, Unset):
            raise NotPresentError(self, "message")
        return self._message

    @message.setter
    def message(self, value: Optional[str]) -> None:
        self._message = value

    @message.deleter
    def message(self) -> None:
        self._message = UNSET
