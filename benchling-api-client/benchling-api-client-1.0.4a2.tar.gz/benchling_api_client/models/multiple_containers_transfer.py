from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.container_quantity import ContainerQuantity
from ..models.deprecated_container_volume_for_input import DeprecatedContainerVolumeForInput
from ..models.multiple_containers_transfer_source_concentration import (
    MultipleContainersTransferSourceConcentration,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="MultipleContainersTransfer")


@attr.s(auto_attribs=True, repr=False)
class MultipleContainersTransfer:
    """  """

    _destination_container_id: str
    _final_quantity: Union[Unset, ContainerQuantity] = UNSET
    _final_volume: Union[Unset, DeprecatedContainerVolumeForInput] = UNSET
    _source_concentration: Union[Unset, MultipleContainersTransferSourceConcentration] = UNSET
    _source_batch_id: Union[Unset, str] = UNSET
    _source_container_id: Union[Unset, str] = UNSET
    _source_entity_id: Union[Unset, str] = UNSET
    _transfer_quantity: Union[Unset, ContainerQuantity] = UNSET
    _transfer_volume: Union[Unset, DeprecatedContainerVolumeForInput] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("destination_container_id={}".format(repr(self._destination_container_id)))
        fields.append("final_quantity={}".format(repr(self._final_quantity)))
        fields.append("final_volume={}".format(repr(self._final_volume)))
        fields.append("source_concentration={}".format(repr(self._source_concentration)))
        fields.append("source_batch_id={}".format(repr(self._source_batch_id)))
        fields.append("source_container_id={}".format(repr(self._source_container_id)))
        fields.append("source_entity_id={}".format(repr(self._source_entity_id)))
        fields.append("transfer_quantity={}".format(repr(self._transfer_quantity)))
        fields.append("transfer_volume={}".format(repr(self._transfer_volume)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "MultipleContainersTransfer({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        destination_container_id = self._destination_container_id
        final_quantity: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._final_quantity, Unset):
            final_quantity = self._final_quantity.to_dict()

        final_volume: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._final_volume, Unset):
            final_volume = self._final_volume.to_dict()

        source_concentration: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._source_concentration, Unset):
            source_concentration = self._source_concentration.to_dict()

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
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "destinationContainerId": destination_container_id,
            }
        )
        if final_quantity is not UNSET:
            field_dict["finalQuantity"] = final_quantity
        if final_volume is not UNSET:
            field_dict["finalVolume"] = final_volume
        if source_concentration is not UNSET:
            field_dict["sourceConcentration"] = source_concentration
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

        def get_destination_container_id() -> str:
            destination_container_id = d.pop("destinationContainerId")
            return destination_container_id

        destination_container_id = (
            get_destination_container_id() if "destinationContainerId" in d else cast(str, UNSET)
        )

        def get_final_quantity() -> Union[Unset, ContainerQuantity]:
            final_quantity: Union[Unset, ContainerQuantity] = UNSET
            _final_quantity = d.pop("finalQuantity")
            if not isinstance(_final_quantity, Unset):
                final_quantity = ContainerQuantity.from_dict(_final_quantity)

            return final_quantity

        final_quantity = (
            get_final_quantity() if "finalQuantity" in d else cast(Union[Unset, ContainerQuantity], UNSET)
        )

        def get_final_volume() -> Union[Unset, DeprecatedContainerVolumeForInput]:
            final_volume: Union[Unset, DeprecatedContainerVolumeForInput] = UNSET
            _final_volume = d.pop("finalVolume")
            if not isinstance(_final_volume, Unset):
                final_volume = DeprecatedContainerVolumeForInput.from_dict(_final_volume)

            return final_volume

        final_volume = (
            get_final_volume()
            if "finalVolume" in d
            else cast(Union[Unset, DeprecatedContainerVolumeForInput], UNSET)
        )

        def get_source_concentration() -> Union[Unset, MultipleContainersTransferSourceConcentration]:
            source_concentration: Union[Unset, MultipleContainersTransferSourceConcentration] = UNSET
            _source_concentration = d.pop("sourceConcentration")
            if not isinstance(_source_concentration, Unset):
                source_concentration = MultipleContainersTransferSourceConcentration.from_dict(
                    _source_concentration
                )

            return source_concentration

        source_concentration = (
            get_source_concentration()
            if "sourceConcentration" in d
            else cast(Union[Unset, MultipleContainersTransferSourceConcentration], UNSET)
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

        multiple_containers_transfer = cls(
            destination_container_id=destination_container_id,
            final_quantity=final_quantity,
            final_volume=final_volume,
            source_concentration=source_concentration,
            source_batch_id=source_batch_id,
            source_container_id=source_container_id,
            source_entity_id=source_entity_id,
            transfer_quantity=transfer_quantity,
            transfer_volume=transfer_volume,
        )

        multiple_containers_transfer.additional_properties = d
        return multiple_containers_transfer

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
    def destination_container_id(self) -> str:
        """ ID of container that will be transferred into. """
        if isinstance(self._destination_container_id, Unset):
            raise NotPresentError(self, "destination_container_id")
        return self._destination_container_id

    @destination_container_id.setter
    def destination_container_id(self, value: str) -> None:
        self._destination_container_id = value

    @property
    def final_quantity(self) -> ContainerQuantity:
        """ Quantity of a container, well, or transfer. Supports mass, volume, and other quantities. """
        if isinstance(self._final_quantity, Unset):
            raise NotPresentError(self, "final_quantity")
        return self._final_quantity

    @final_quantity.setter
    def final_quantity(self, value: ContainerQuantity) -> None:
        self._final_quantity = value

    @final_quantity.deleter
    def final_quantity(self) -> None:
        self._final_quantity = UNSET

    @property
    def final_volume(self) -> DeprecatedContainerVolumeForInput:
        """Desired volume for a container, well, or transfer. "volume" type keys are deprecated in API requests; use the more permissive "quantity" type key instead."""
        if isinstance(self._final_volume, Unset):
            raise NotPresentError(self, "final_volume")
        return self._final_volume

    @final_volume.setter
    def final_volume(self, value: DeprecatedContainerVolumeForInput) -> None:
        self._final_volume = value

    @final_volume.deleter
    def final_volume(self) -> None:
        self._final_volume = UNSET

    @property
    def source_concentration(self) -> MultipleContainersTransferSourceConcentration:
        """Concentration at which to transfer entities or batches. Not applicable for container-to-container transfers (the concentration of the source container’s contents will be used)."""
        if isinstance(self._source_concentration, Unset):
            raise NotPresentError(self, "source_concentration")
        return self._source_concentration

    @source_concentration.setter
    def source_concentration(self, value: MultipleContainersTransferSourceConcentration) -> None:
        self._source_concentration = value

    @source_concentration.deleter
    def source_concentration(self) -> None:
        self._source_concentration = UNSET

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
