from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="DropdownOptionsUnarchive")


@attr.s(auto_attribs=True, repr=False)
class DropdownOptionsUnarchive:
    """  """

    _dropdown_option_ids: Union[Unset, List[str]] = UNSET

    def __repr__(self):
        fields = []
        fields.append("dropdown_option_ids={}".format(repr(self._dropdown_option_ids)))
        return "DropdownOptionsUnarchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        dropdown_option_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._dropdown_option_ids, Unset):
            dropdown_option_ids = self._dropdown_option_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if dropdown_option_ids is not UNSET:
            field_dict["dropdownOptionIds"] = dropdown_option_ids

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

        dropdown_options_unarchive = cls(
            dropdown_option_ids=dropdown_option_ids,
        )

        return dropdown_options_unarchive

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
