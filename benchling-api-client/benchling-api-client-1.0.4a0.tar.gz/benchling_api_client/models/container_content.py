from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.batch_or_inaccessible_resource import BatchOrInaccessibleResource
from ..models.entity_or_inaccessible_resource import EntityOrInaccessibleResource
from ..models.measurement import Measurement
from ..types import UNSET, Unset

T = TypeVar("T", bound="ContainerContent")


@attr.s(auto_attribs=True, repr=False)
class ContainerContent:
    """  """

    _batch: Union[Unset, None, BatchOrInaccessibleResource] = UNSET
    _concentration: Union[Unset, Measurement] = UNSET
    _entity: Union[Unset, None, EntityOrInaccessibleResource] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("batch={}".format(repr(self._batch)))
        fields.append("concentration={}".format(repr(self._concentration)))
        fields.append("entity={}".format(repr(self._entity)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "ContainerContent({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        batch: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._batch, Unset):
            batch = self._batch.to_dict() if self._batch else None

        concentration: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._concentration, Unset):
            concentration = self._concentration.to_dict()

        entity: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._entity, Unset):
            entity = self._entity.to_dict() if self._entity else None

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if batch is not UNSET:
            field_dict["batch"] = batch
        if concentration is not UNSET:
            field_dict["concentration"] = concentration
        if entity is not UNSET:
            field_dict["entity"] = entity

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_batch() -> Union[Unset, None, BatchOrInaccessibleResource]:
            batch = None
            _batch = d.pop("batch")
            if _batch is not None and not isinstance(_batch, Unset):
                batch = BatchOrInaccessibleResource.from_dict(_batch)

            return batch

        batch = get_batch() if "batch" in d else cast(Union[Unset, None, BatchOrInaccessibleResource], UNSET)

        def get_concentration() -> Union[Unset, Measurement]:
            concentration: Union[Unset, Measurement] = UNSET
            _concentration = d.pop("concentration")
            if not isinstance(_concentration, Unset):
                concentration = Measurement.from_dict(_concentration)

            return concentration

        concentration = (
            get_concentration() if "concentration" in d else cast(Union[Unset, Measurement], UNSET)
        )

        def get_entity() -> Union[Unset, None, EntityOrInaccessibleResource]:
            entity = None
            _entity = d.pop("entity")
            if _entity is not None and not isinstance(_entity, Unset):
                entity = EntityOrInaccessibleResource.from_dict(_entity)

            return entity

        entity = (
            get_entity() if "entity" in d else cast(Union[Unset, None, EntityOrInaccessibleResource], UNSET)
        )

        container_content = cls(
            batch=batch,
            concentration=concentration,
            entity=entity,
        )

        container_content.additional_properties = d
        return container_content

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
    def batch(self) -> Optional[BatchOrInaccessibleResource]:
        if isinstance(self._batch, Unset):
            raise NotPresentError(self, "batch")
        return self._batch

    @batch.setter
    def batch(self, value: Optional[BatchOrInaccessibleResource]) -> None:
        self._batch = value

    @batch.deleter
    def batch(self) -> None:
        self._batch = UNSET

    @property
    def concentration(self) -> Measurement:
        if isinstance(self._concentration, Unset):
            raise NotPresentError(self, "concentration")
        return self._concentration

    @concentration.setter
    def concentration(self, value: Measurement) -> None:
        self._concentration = value

    @concentration.deleter
    def concentration(self) -> None:
        self._concentration = UNSET

    @property
    def entity(self) -> Optional[EntityOrInaccessibleResource]:
        if isinstance(self._entity, Unset):
            raise NotPresentError(self, "entity")
        return self._entity

    @entity.setter
    def entity(self, value: Optional[EntityOrInaccessibleResource]) -> None:
        self._entity = value

    @entity.deleter
    def entity(self) -> None:
        self._entity = UNSET
