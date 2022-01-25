from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.container_quantity import ContainerQuantity
from ..models.deprecated_container_volume_for_input import DeprecatedContainerVolumeForInput
from ..models.fields import Fields
from ..types import UNSET, Unset

T = TypeVar("T", bound="ContainerBulkUpdateItem")


@attr.s(auto_attribs=True, repr=False)
class ContainerBulkUpdateItem:
    """  """

    _container_id: str
    _quantity: Union[Unset, ContainerQuantity] = UNSET
    _volume: Union[Unset, DeprecatedContainerVolumeForInput] = UNSET
    _fields: Union[Unset, Fields] = UNSET
    _name: Union[Unset, str] = UNSET
    _parent_storage_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("container_id={}".format(repr(self._container_id)))
        fields.append("quantity={}".format(repr(self._quantity)))
        fields.append("volume={}".format(repr(self._volume)))
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("parent_storage_id={}".format(repr(self._parent_storage_id)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "ContainerBulkUpdateItem({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        container_id = self._container_id
        quantity: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._quantity, Unset):
            quantity = self._quantity.to_dict()

        volume: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._volume, Unset):
            volume = self._volume.to_dict()

        fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._fields, Unset):
            fields = self._fields.to_dict()

        name = self._name
        parent_storage_id = self._parent_storage_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "containerId": container_id,
            }
        )
        if quantity is not UNSET:
            field_dict["quantity"] = quantity
        if volume is not UNSET:
            field_dict["volume"] = volume
        if fields is not UNSET:
            field_dict["fields"] = fields
        if name is not UNSET:
            field_dict["name"] = name
        if parent_storage_id is not UNSET:
            field_dict["parentStorageId"] = parent_storage_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_container_id() -> str:
            container_id = d.pop("containerId")
            return container_id

        container_id = get_container_id() if "containerId" in d else cast(str, UNSET)

        def get_quantity() -> Union[Unset, ContainerQuantity]:
            quantity: Union[Unset, ContainerQuantity] = UNSET
            _quantity = d.pop("quantity")
            if not isinstance(_quantity, Unset):
                quantity = ContainerQuantity.from_dict(_quantity)

            return quantity

        quantity = get_quantity() if "quantity" in d else cast(Union[Unset, ContainerQuantity], UNSET)

        def get_volume() -> Union[Unset, DeprecatedContainerVolumeForInput]:
            volume: Union[Unset, DeprecatedContainerVolumeForInput] = UNSET
            _volume = d.pop("volume")
            if not isinstance(_volume, Unset):
                volume = DeprecatedContainerVolumeForInput.from_dict(_volume)

            return volume

        volume = (
            get_volume() if "volume" in d else cast(Union[Unset, DeprecatedContainerVolumeForInput], UNSET)
        )

        def get_fields() -> Union[Unset, Fields]:
            fields: Union[Unset, Fields] = UNSET
            _fields = d.pop("fields")
            if not isinstance(_fields, Unset):
                fields = Fields.from_dict(_fields)

            return fields

        fields = get_fields() if "fields" in d else cast(Union[Unset, Fields], UNSET)

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        def get_parent_storage_id() -> Union[Unset, str]:
            parent_storage_id = d.pop("parentStorageId")
            return parent_storage_id

        parent_storage_id = (
            get_parent_storage_id() if "parentStorageId" in d else cast(Union[Unset, str], UNSET)
        )

        container_bulk_update_item = cls(
            container_id=container_id,
            quantity=quantity,
            volume=volume,
            fields=fields,
            name=name,
            parent_storage_id=parent_storage_id,
        )

        container_bulk_update_item.additional_properties = d
        return container_bulk_update_item

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
    def container_id(self) -> str:
        if isinstance(self._container_id, Unset):
            raise NotPresentError(self, "container_id")
        return self._container_id

    @container_id.setter
    def container_id(self, value: str) -> None:
        self._container_id = value

    @property
    def quantity(self) -> ContainerQuantity:
        """ Quantity of a container, well, or transfer. Supports mass, volume, and other quantities. """
        if isinstance(self._quantity, Unset):
            raise NotPresentError(self, "quantity")
        return self._quantity

    @quantity.setter
    def quantity(self, value: ContainerQuantity) -> None:
        self._quantity = value

    @quantity.deleter
    def quantity(self) -> None:
        self._quantity = UNSET

    @property
    def volume(self) -> DeprecatedContainerVolumeForInput:
        """Desired volume for a container, well, or transfer. "volume" type keys are deprecated in API requests; use the more permissive "quantity" type key instead."""
        if isinstance(self._volume, Unset):
            raise NotPresentError(self, "volume")
        return self._volume

    @volume.setter
    def volume(self, value: DeprecatedContainerVolumeForInput) -> None:
        self._volume = value

    @volume.deleter
    def volume(self) -> None:
        self._volume = UNSET

    @property
    def fields(self) -> Fields:
        if isinstance(self._fields, Unset):
            raise NotPresentError(self, "fields")
        return self._fields

    @fields.setter
    def fields(self, value: Fields) -> None:
        self._fields = value

    @fields.deleter
    def fields(self) -> None:
        self._fields = UNSET

    @property
    def name(self) -> str:
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
    def parent_storage_id(self) -> str:
        if isinstance(self._parent_storage_id, Unset):
            raise NotPresentError(self, "parent_storage_id")
        return self._parent_storage_id

    @parent_storage_id.setter
    def parent_storage_id(self, value: str) -> None:
        self._parent_storage_id = value

    @parent_storage_id.deleter
    def parent_storage_id(self) -> None:
        self._parent_storage_id = UNSET
