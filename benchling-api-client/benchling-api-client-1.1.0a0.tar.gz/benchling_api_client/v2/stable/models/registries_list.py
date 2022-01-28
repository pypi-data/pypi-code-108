from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.registry import Registry
from ..types import UNSET, Unset

T = TypeVar("T", bound="RegistriesList")


@attr.s(auto_attribs=True, repr=False)
class RegistriesList:
    """  """

    _registries: Union[Unset, List[Registry]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("registries={}".format(repr(self._registries)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "RegistriesList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        registries: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._registries, Unset):
            registries = []
            for registries_item_data in self._registries:
                registries_item = registries_item_data.to_dict()

                registries.append(registries_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if registries is not UNSET:
            field_dict["registries"] = registries

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_registries() -> Union[Unset, List[Registry]]:
            registries = []
            _registries = d.pop("registries")
            for registries_item_data in _registries or []:
                registries_item = Registry.from_dict(registries_item_data)

                registries.append(registries_item)

            return registries

        registries = get_registries() if "registries" in d else cast(Union[Unset, List[Registry]], UNSET)

        registries_list = cls(
            registries=registries,
        )

        registries_list.additional_properties = d
        return registries_list

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
    def registries(self) -> List[Registry]:
        if isinstance(self._registries, Unset):
            raise NotPresentError(self, "registries")
        return self._registries

    @registries.setter
    def registries(self, value: List[Registry]) -> None:
        self._registries = value

    @registries.deleter
    def registries(self) -> None:
        self._registries = UNSET
