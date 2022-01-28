from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.dropdown_options_archive_reason import DropdownOptionsArchiveReason
from ..types import UNSET, Unset

T = TypeVar("T", bound="DropdownOptionsArchive")


@attr.s(auto_attribs=True, repr=False)
class DropdownOptionsArchive:
    """  """

    _dropdown_option_ids: Union[Unset, List[str]] = UNSET
    _reason: Union[Unset, DropdownOptionsArchiveReason] = UNSET

    def __repr__(self):
        fields = []
        fields.append("dropdown_option_ids={}".format(repr(self._dropdown_option_ids)))
        fields.append("reason={}".format(repr(self._reason)))
        return "DropdownOptionsArchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        dropdown_option_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._dropdown_option_ids, Unset):
            dropdown_option_ids = self._dropdown_option_ids

        reason: Union[Unset, int] = UNSET
        if not isinstance(self._reason, Unset):
            reason = self._reason.value

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if dropdown_option_ids is not UNSET:
            field_dict["dropdownOptionIds"] = dropdown_option_ids
        if reason is not UNSET:
            field_dict["reason"] = reason

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_dropdown_option_ids() -> Union[Unset, List[str]]:
            dropdown_option_ids = cast(List[str], d.pop("dropdownOptionIds"))

            return dropdown_option_ids

        dropdown_option_ids = (
            get_dropdown_option_ids() if "dropdownOptionIds" in d else cast(Union[Unset, List[str]], UNSET)
        )

        def get_reason() -> Union[Unset, DropdownOptionsArchiveReason]:
            reason = None
            _reason = d.pop("reason")
            if _reason is not None and _reason is not UNSET:
                try:
                    reason = DropdownOptionsArchiveReason(_reason)
                except ValueError:
                    reason = DropdownOptionsArchiveReason.of_unknown(_reason)

            return reason

        reason = get_reason() if "reason" in d else cast(Union[Unset, DropdownOptionsArchiveReason], UNSET)

        dropdown_options_archive = cls(
            dropdown_option_ids=dropdown_option_ids,
            reason=reason,
        )

        return dropdown_options_archive

    @property
    def dropdown_option_ids(self) -> List[str]:
        """ Array of dropdown option IDs """
        if isinstance(self._dropdown_option_ids, Unset):
            raise NotPresentError(self, "dropdown_option_ids")
        return self._dropdown_option_ids

    @dropdown_option_ids.setter
    def dropdown_option_ids(self, value: List[str]) -> None:
        self._dropdown_option_ids = value

    @dropdown_option_ids.deleter
    def dropdown_option_ids(self) -> None:
        self._dropdown_option_ids = UNSET

    @property
    def reason(self) -> DropdownOptionsArchiveReason:
        """Reason that dropdown options are being archived."""
        if isinstance(self._reason, Unset):
            raise NotPresentError(self, "reason")
        return self._reason

    @reason.setter
    def reason(self, value: DropdownOptionsArchiveReason) -> None:
        self._reason = value

    @reason.deleter
    def reason(self) -> None:
        self._reason = UNSET
