from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.user_validation_validation_status import UserValidationValidationStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="UserValidation")


@attr.s(auto_attribs=True, repr=False)
class UserValidation:
    """  """

    _validation_comment: Union[Unset, str] = UNSET
    _validation_status: Union[Unset, UserValidationValidationStatus] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("validation_comment={}".format(repr(self._validation_comment)))
        fields.append("validation_status={}".format(repr(self._validation_status)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "UserValidation({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        validation_comment = self._validation_comment
        validation_status: Union[Unset, int] = UNSET
        if not isinstance(self._validation_status, Unset):
            validation_status = self._validation_status.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if validation_comment is not UNSET:
            field_dict["validationComment"] = validation_comment
        if validation_status is not UNSET:
            field_dict["validationStatus"] = validation_status

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_validation_comment() -> Union[Unset, str]:
            validation_comment = d.pop("validationComment")
            return validation_comment

        validation_comment = (
            get_validation_comment() if "validationComment" in d else cast(Union[Unset, str], UNSET)
        )

        def get_validation_status() -> Union[Unset, UserValidationValidationStatus]:
            validation_status = None
            _validation_status = d.pop("validationStatus")
            if _validation_status is not None and _validation_status is not UNSET:
                try:
                    validation_status = UserValidationValidationStatus(_validation_status)
                except ValueError:
                    validation_status = UserValidationValidationStatus.of_unknown(_validation_status)

            return validation_status

        validation_status = (
            get_validation_status()
            if "validationStatus" in d
            else cast(Union[Unset, UserValidationValidationStatus], UNSET)
        )

        user_validation = cls(
            validation_comment=validation_comment,
            validation_status=validation_status,
        )

        user_validation.additional_properties = d
        return user_validation

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
    def validation_comment(self) -> str:
        """ A string explaining the reason for the provided validation status. """
        if isinstance(self._validation_comment, Unset):
            raise NotPresentError(self, "validation_comment")
        return self._validation_comment

    @validation_comment.setter
    def validation_comment(self, value: str) -> None:
        self._validation_comment = value

    @validation_comment.deleter
    def validation_comment(self) -> None:
        self._validation_comment = UNSET

    @property
    def validation_status(self) -> UserValidationValidationStatus:
        """Valid values for this enum depend on whether it is used to set a value (e.g., in a POST request), or is a return value for an existing result.
        Acceptable values for setting a status are 'VALID' or 'INVALID'. Possible return values are 'VALID', 'INVALID', or 'PARTIALLY_VALID' (a result will be partially valid if it has some valid fields and some invalid fields).
        """
        if isinstance(self._validation_status, Unset):
            raise NotPresentError(self, "validation_status")
        return self._validation_status

    @validation_status.setter
    def validation_status(self, value: UserValidationValidationStatus) -> None:
        self._validation_status = value

    @validation_status.deleter
    def validation_status(self) -> None:
        self._validation_status = UNSET
