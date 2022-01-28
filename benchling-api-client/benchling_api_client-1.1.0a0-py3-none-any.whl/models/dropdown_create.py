from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.dropdown_option_create import DropdownOptionCreate
from ..types import UNSET, Unset

T = TypeVar("T", bound="DropdownCreate")


@attr.s(auto_attribs=True, repr=False)
class DropdownCreate:
    """  """

    _name: str
    _options: List[DropdownOptionCreate]
    _registry_id: Union[Unset, None, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("name={}".format(repr(self._name)))
        fields.append("options={}".format(repr(self._options)))
        fields.append("registry_id={}".format(repr(self._registry_id)))
        return "DropdownCreate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        name = self._name
        options = []
        for options_item_data in self._options:
            options_item = options_item_data.to_dict()

            options.append(options_item)

        registry_id = self._registry_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "name": name,
                "options": options,
            }
        )
        if registry_id is not UNSET:
            field_dict["registryId"] = registry_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_name() -> str:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(str, UNSET)

        def get_options() -> List[DropdownOptionCreate]:
            options = []
            _options = d.pop("options")
            for options_item_data in _options:
                options_item = DropdownOptionCreate.from_dict(options_item_data)

                options.append(options_item)

            return options

        options = get_options() if "options" in d else cast(List[DropdownOptionCreate], UNSET)

        def get_registry_id() -> Union[Unset, None, str]:
            registry_id = d.pop("registryId")
            return registry_id

        registry_id = get_registry_id() if "registryId" in d else cast(Union[Unset, None, str], UNSET)

        dropdown_create = cls(
            name=name,
            options=options,
            registry_id=registry_id,
        )

        return dropdown_create

    @property
    def name(self) -> str:
        """ Name of the dropdown """
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def options(self) -> List[DropdownOptionCreate]:
        """ Options to set for the dropdown """
        if isinstance(self._options, Unset):
            raise NotPresentError(self, "options")
        return self._options

    @options.setter
    def options(self, value: List[DropdownOptionCreate]) -> None:
        self._options = value

    @property
    def registry_id(self) -> Optional[str]:
        """ ID of registry in which to create the dropdown. Required if multiple registries exist. """
        if isinstance(self._registry_id, Unset):
            raise NotPresentError(self, "registry_id")
        return self._registry_id

    @registry_id.setter
    def registry_id(self, value: Optional[str]) -> None:
        self._registry_id = value

    @registry_id.deleter
    def registry_id(self) -> None:
        self._registry_id = UNSET
