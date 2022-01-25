from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="Printer")


@attr.s(auto_attribs=True, repr=False)
class Printer:
    """  """

    _address: Union[Unset, str] = UNSET
    _description: Union[Unset, None, str] = UNSET
    _id: Union[Unset, str] = UNSET
    _name: Union[Unset, str] = UNSET
    _port: Union[Unset, None, int] = UNSET
    _registry_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("address={}".format(repr(self._address)))
        fields.append("description={}".format(repr(self._description)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("port={}".format(repr(self._port)))
        fields.append("registry_id={}".format(repr(self._registry_id)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "Printer({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        address = self._address
        description = self._description
        id = self._id
        name = self._name
        port = self._port
        registry_id = self._registry_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if address is not UNSET:
            field_dict["address"] = address
        if description is not UNSET:
            field_dict["description"] = description
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if port is not UNSET:
            field_dict["port"] = port
        if registry_id is not UNSET:
            field_dict["registryId"] = registry_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_address() -> Union[Unset, str]:
            address = d.pop("address")
            return address

        address = get_address() if "address" in d else cast(Union[Unset, str], UNSET)

        def get_description() -> Union[Unset, None, str]:
            description = d.pop("description")
            return description

        description = get_description() if "description" in d else cast(Union[Unset, None, str], UNSET)

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        def get_port() -> Union[Unset, None, int]:
            port = d.pop("port")
            return port

        port = get_port() if "port" in d else cast(Union[Unset, None, int], UNSET)

        def get_registry_id() -> Union[Unset, str]:
            registry_id = d.pop("registryId")
            return registry_id

        registry_id = get_registry_id() if "registryId" in d else cast(Union[Unset, str], UNSET)

        printer = cls(
            address=address,
            description=description,
            id=id,
            name=name,
            port=port,
            registry_id=registry_id,
        )

        printer.additional_properties = d
        return printer

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
    def address(self) -> str:
        """ Web address of the printer (either IP address or URL). """
        if isinstance(self._address, Unset):
            raise NotPresentError(self, "address")
        return self._address

    @address.setter
    def address(self, value: str) -> None:
        self._address = value

    @address.deleter
    def address(self) -> None:
        self._address = UNSET

    @property
    def description(self) -> Optional[str]:
        """ Short description of the printer. """
        if isinstance(self._description, Unset):
            raise NotPresentError(self, "description")
        return self._description

    @description.setter
    def description(self, value: Optional[str]) -> None:
        self._description = value

    @description.deleter
    def description(self) -> None:
        self._description = UNSET

    @property
    def id(self) -> str:
        """ ID of the printer. """
        if isinstance(self._id, Unset):
            raise NotPresentError(self, "id")
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @id.deleter
    def id(self) -> None:
        self._id = UNSET

    @property
    def name(self) -> str:
        """ Name of the printer. """
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @name.deleter
    def name(self) -> None:
        self._name = UNSET

    @property
    def port(self) -> Optional[int]:
        """ Port to reach the printer at. """
        if isinstance(self._port, Unset):
            raise NotPresentError(self, "port")
        return self._port

    @port.setter
    def port(self, value: Optional[int]) -> None:
        self._port = value

    @port.deleter
    def port(self) -> None:
        self._port = UNSET

    @property
    def registry_id(self) -> str:
        """ ID of the registry associated with this printer. """
        if isinstance(self._registry_id, Unset):
            raise NotPresentError(self, "registry_id")
        return self._registry_id

    @registry_id.setter
    def registry_id(self, value: str) -> None:
        self._registry_id = value

    @registry_id.deleter
    def registry_id(self) -> None:
        self._registry_id = UNSET
