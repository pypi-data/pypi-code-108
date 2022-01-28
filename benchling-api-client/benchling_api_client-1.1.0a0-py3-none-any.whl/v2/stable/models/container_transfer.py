from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.container_quantity import ContainerQuantity
from ..models.container_transfer_destination_contents_item import ContainerTransferDestinationContentsItem
from ..models.deprecated_container_volume_for_input import DeprecatedContainerVolumeForInput
from ..types import UNSET, Unset

T = TypeVar("T", bound="ContainerTransfer")


@attr.s(auto_attribs=True, repr=False)
class ContainerTransfer:
    """  """

    _destination_contents: Union[Unset, List[ContainerTransferDestinationContentsItem]] = UNSET
    _destination_quantity: Union[Unset, ContainerQuantity] = UNSET
    _destination_volume: Union[Unset, DeprecatedContainerVolumeForInput] = UNSET
    _source_batch_id: Union[Unset, str] = UNSET
    _source_container_id: Union[Unset, str] = UNSET
    _source_entity_id: Union[Unset, str] = UNSET
    _transfer_quantity: Union[Unset, ContainerQuantity] = UNSET
    _transfer_volume: Union[Unset, DeprecatedContainerVolumeForInput] = UNSET

    def __repr__(self):
        fields = []
        fields.append("destination_contents={}".format(repr(self._destination_contents)))
        fields.append("destination_quantity={}".format(repr(self._destination_quantity)))
        fields.append("destination_volume={}".format(repr(self._destination_volume)))
        fields.append("source_batch_id={}".format(repr(self._source_batch_id)))
        fields.append("source_container_id={}".format(repr(self._source_container_id)))
        fields.append("source_entity_id={}".format(repr(self._source_entity_id)))
        fields.append("transfer_quantity={}".format(repr(self._transfer_quantity)))
        fields.append("transfer_volume={}".format(repr(self._transfer_volume)))
        return "ContainerTransfer({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        destination_contents: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._destination_contents, Unset):
            destination_contents = []
            for destination_contents_item_data in self._destination_contents:
                destination_contents_item = destination_contents_item_data.to_dict()

                destination_contents.append(destination_contents_item)

        destination_quantity: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._destination_quantity, Unset):
            destination_quantity = self._destination_quantity.to_dict()

        destination_volume: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._destination_volume, Unset):
            destination_volume = self._destination_volume.to_dict()

        source_batch_id = self._source_batch_id
        source_container_id = self._source_container_id
        source_entity_id = self._source_entity_id
        transfer_quantity: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._transfer_quantity, Unset):
            transfer_quantity = self._transfer_quantity.to_dict()

        transfer_volume: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._transfer_volume, Unset):
            transfer_volume = self._transfer_volume.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if destination_contents is not UNSET:
            field_dict["destinationContents"] = destination_contents
        if destination_quantity is not UNSET:
            field_dict["destinationQuantity"] = destination_quantity
        if destination_volume is not UNSET:
            field_dict["destinationVolume"] = destination_volume
        if source_batch_id is not UNSET:
            field_dict["sourceBatchId"] = source_batch_id
        if source_container_id is not UNSET:
            field_dict["sourceContainerId"] = source_container_id
        if source_entity_id is not UNSET:
            field_dict["sourceEntityId"] = source_entity_id
        if transfer_quantity is not UNSET:
            field_dict["transferQuantity"] = transfer_quantity
        if transfer_volume is not UNSET:
            field_dict["transferVolume"] = transfer_volume

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_destination_contents() -> Union[Unset, List[ContainerTransferDestinationContentsItem]]:
            destination_contents = []
            _destination_contents = d.pop("destinationContents")
            for destination_contents_item_data in _destination_contents or []:
                destination_contents_item = ContainerTransferDestinationContentsItem.from_dict(
                    destination_contents_item_data
                )

                destination_contents.append(destination_contents_item)

            return destination_contents

        destination_contents = (
            get_destination_contents()
            if "destinationContents" in d
            else cast(Union[Unset, List[ContainerTransferDestinationContentsItem]], UNSET)
        )

        def get_destination_quantity() -> Union[Unset, ContainerQuantity]:
            destination_quantity: Union[Unset, ContainerQuantity] = UNSET
            _destination_quantity = d.pop("destinationQuantity")
            if not isinstance(_destination_quantity, Unset):
                destination_quantity = ContainerQuantity.from_dict(_destination_quantity)

            return destination_quantity

        destination_quantity = (
            get_destination_quantity()
            if "destinationQuantity" in d
            else cast(Union[Unset, ContainerQuantity], UNSET)
        )

        def get_destination_volume() -> Union[Unset, DeprecatedContainerVolumeForInput]:
            destination_volume: Union[Unset, DeprecatedContainerVolumeForInput] = UNSET
            _destination_volume = d.pop("destinationVolume")
            if not isinstance(_destination_volume, Unset):
                destination_volume = DeprecatedContainerVolumeForInput.from_dict(_destination_volume)

            return destination_volume

        destination_volume = (
            get_destination_volume()
            if "destinationVolume" in d
            else cast(Union[Unset, DeprecatedContainerVolumeForInput], UNSET)
        )

        def get_source_batch_id() -> Union[Unset, str]:
            source_batch_id = d.pop("sourceBatchId")
            return source_batch_id

        source_batch_id = get_source_batch_id() if "sourceBatchId" in d else cast(Union[Unset, str], UNSET)

        def get_source_container_id() -> Union[Unset, str]:
            source_container_id = d.pop("sourceContainerId")
            return source_container_id

        source_container_id = (
            get_source_container_id() if "sourceContainerId" in d else cast(Union[Unset, str], UNSET)
        )

        def get_source_entity_id() -> Union[Unset, str]:
            source_entity_id = d.pop("sourceEntityId")
            return source_entity_id

        source_entity_id = get_source_entity_id() if "sourceEntityId" in d else cast(Union[Unset, str], UNSET)

        def get_transfer_quantity() -> Union[Unset, ContainerQuantity]:
            transfer_quantity: Union[Unset, ContainerQuantity] = UNSET
            _transfer_quantity = d.pop("transferQuantity")
            if not isinstance(_transfer_quantity, Unset):
                transfer_quantity = ContainerQuantity.from_dict(_transfer_quantity)

            return transfer_quantity

        transfer_quantity = (
            get_transfer_quantity()
            if "transferQuantity" in d
            else cast(Union[Unset, ContainerQuantity], UNSET)
        )

        def get_transfer_volume() -> Union[Unset, DeprecatedContainerVolumeForInput]:
            transfer_volume: Union[Unset, DeprecatedContainerVolumeForInput] = UNSET
            _transfer_volume = d.pop("transferVolume")
            if not isinstance(_transfer_volume, Unset):
                transfer_volume = DeprecatedContainerVolumeForInput.from_dict(_transfer_volume)

            return transfer_volume

        transfer_volume = (
            get_transfer_volume()
            if "transferVolume" in d
            else cast(Union[Unset, DeprecatedContainerVolumeForInput], UNSET)
        )

        container_transfer = cls(
            destination_contents=destination_contents,
            destination_quantity=destination_quantity,
            destination_volume=destination_volume,
            source_batch_id=source_batch_id,
            source_container_id=source_container_id,
            source_entity_id=source_entity_id,
            transfer_quantity=transfer_quantity,
            transfer_volume=transfer_volume,
        )

        return container_transfer

    @property
    def destination_contents(self) -> List[ContainerTransferDestinationContentsItem]:
        if isinstance(self._destination_contents, Unset):
            raise NotPresentError(self, "destination_contents")
        return self._destination_contents

    @destination_contents.setter
    def destination_contents(self, value: List[ContainerTransferDestinationContentsItem]) -> None:
        self._destination_contents = value

    @destination_contents.deleter
    def destination_contents(self) -> None:
        self._destination_contents = UNSET

    @property
    def destination_quantity(self) -> ContainerQuantity:
        """ Quantity of a container, well, or transfer. Supports mass, volume, and other quantities. """
        if isinstance(self._destination_quantity, Unset):
            raise NotPresentError(self, "destination_quantity")
        return self._destination_quantity

    @destination_quantity.setter
    def destination_quantity(self, value: ContainerQuantity) -> None:
        self._destination_quantity = value

    @destination_quantity.deleter
    def destination_quantity(self) -> None:
        self._destination_quantity = UNSET

    @property
    def destination_volume(self) -> DeprecatedContainerVolumeForInput:
        """Desired volume for a container, well, or transfer. "volume" type keys are deprecated in API requests; use the more permissive "quantity" type key instead."""
        if isinstance(self._destination_volume, Unset):
            raise NotPresentError(self, "destination_volume")
        return self._destination_volume

    @destination_volume.setter
    def destination_volume(self, value: DeprecatedContainerVolumeForInput) -> None:
        self._destination_volume = value

    @destination_volume.deleter
    def destination_volume(self) -> None:
        self._destination_volume = UNSET

    @property
    def source_batch_id(self) -> str:
        """ID of the batch that will be transferred in. Must specify one of sourceEntityId, sourceBatchId, or sourceContainerId."""
        if isinstance(self._source_batch_id, Unset):
            raise NotPresentError(self, "source_batch_id")
        return self._source_batch_id

    @source_batch_id.setter
    def source_batch_id(self, value: str) -> None:
        self._source_batch_id = value

    @source_batch_id.deleter
    def source_batch_id(self) -> None:
        self._source_batch_id = UNSET

    @property
    def source_container_id(self) -> str:
        """ID of the container that will be transferred in. Must specify one of sourceEntityId, sourceBatchId, or sourceContainerId."""
        if isinstance(self._source_container_id, Unset):
            raise NotPresentError(self, "source_container_id")
        return self._source_container_id

    @source_container_id.setter
    def source_container_id(self, value: str) -> None:
        self._source_container_id = value

    @source_container_id.deleter
    def source_container_id(self) -> None:
        self._source_container_id = UNSET

    @property
    def source_entity_id(self) -> str:
        """ID of the entity that will be transferred in. Must specify one of sourceEntityId, sourceBatchId, or sourceContainerId."""
        if isinstance(self._source_entity_id, Unset):
            raise NotPresentError(self, "source_entity_id")
        return self._source_entity_id

    @source_entity_id.setter
    def source_entity_id(self, value: str) -> None:
        self._source_entity_id = value

    @source_entity_id.deleter
    def source_entity_id(self) -> None:
        self._source_entity_id = UNSET

    @property
    def transfer_quantity(self) -> ContainerQuantity:
        """ Quantity of a container, well, or transfer. Supports mass, volume, and other quantities. """
        if isinstance(self._transfer_quantity, Unset):
            raise NotPresentError(self, "transfer_quantity")
        return self._transfer_quantity

    @transfer_quantity.setter
    def transfer_quantity(self, value: ContainerQuantity) -> None:
        self._transfer_quantity = value

    @transfer_quantity.deleter
    def transfer_quantity(self) -> None:
        self._transfer_quantity = UNSET

    @property
    def transfer_volume(self) -> DeprecatedContainerVolumeForInput:
        """Desired volume for a container, well, or transfer. "volume" type keys are deprecated in API requests; use the more permissive "quantity" type key instead."""
        if isinstance(self._transfer_volume, Unset):
            raise NotPresentError(self, "transfer_volume")
        return self._transfer_volume

    @transfer_volume.setter
    def transfer_volume(self, value: DeprecatedContainerVolumeForInput) -> None:
        self._transfer_volume = value

    @transfer_volume.deleter
    def transfer_volume(self) -> None:
        self._transfer_volume = UNSET
