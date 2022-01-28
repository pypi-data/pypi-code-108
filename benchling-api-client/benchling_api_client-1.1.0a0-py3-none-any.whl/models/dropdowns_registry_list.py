from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.dropdown_summary import DropdownSummary
from ..types import UNSET, Unset

T = TypeVar("T", bound="DropdownsRegistryList")


@attr.s(auto_attribs=True, repr=False)
class DropdownsRegistryList:
    """  """

    _dropdowns: Union[Unset, List[DropdownSummary]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("dropdowns={}".format(repr(self._dropdowns)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "DropdownsRegistryList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        dropdowns: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._dropdowns, Unset):
            dropdowns = []
            for dropdowns_item_data in self._dropdowns:
                dropdowns_item = dropdowns_item_data.to_dict()

                dropdowns.append(dropdowns_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if dropdowns is not UNSET:
            field_dict["dropdowns"] = dropdowns

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_dropdowns() -> Union[Unset, List[DropdownSummary]]:
            dropdowns = []
            _dropdowns = d.pop("dropdowns")
            for dropdowns_item_data in _dropdowns or []:
                dropdowns_item = DropdownSummary.from_dict(dropdowns_item_data)

                dropdowns.append(dropdowns_item)

            return dropdowns

        dropdowns = get_dropdowns() if "dropdowns" in d else cast(Union[Unset, List[DropdownSummary]], UNSET)

        dropdowns_registry_list = cls(
            dropdowns=dropdowns,
        )

        dropdowns_registry_list.additional_properties = d
        return dropdowns_registry_list

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
    def dropdowns(self) -> List[DropdownSummary]:
        if isinstance(self._dropdowns, Unset):
            raise NotPresentError(self, "dropdowns")
        return self._dropdowns

    @dropdowns.setter
    def dropdowns(self, value: List[DropdownSummary]) -> None:
        self._dropdowns = value

    @dropdowns.deleter
    def dropdowns(self) -> None:
        self._dropdowns = UNSET
