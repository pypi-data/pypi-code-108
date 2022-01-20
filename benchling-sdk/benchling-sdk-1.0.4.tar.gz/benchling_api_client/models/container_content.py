from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError, UnknownType
from ..models.aa_sequence import AaSequence
from ..models.batch import Batch
from ..models.custom_entity import CustomEntity
from ..models.dna_sequence import DnaSequence
from ..models.measurement import Measurement
from ..types import UNSET, Unset

T = TypeVar("T", bound="ContainerContent")


@attr.s(auto_attribs=True, repr=False)
class ContainerContent:
    """  """

    _batch: Union[Unset, None, Batch] = UNSET
    _concentration: Union[Unset, Measurement] = UNSET
    _entity: Union[Unset, None, DnaSequence, AaSequence, CustomEntity, UnknownType] = UNSET
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

        entity: Union[Unset, None, Dict[str, Any]]
        if isinstance(self._entity, Unset):
            entity = UNSET
        elif self._entity is None:
            entity = None
        elif isinstance(self._entity, UnknownType):
            entity = self._entity.value
        elif isinstance(self._entity, DnaSequence):
            entity = UNSET
            if not isinstance(self._entity, Unset):
                entity = self._entity.to_dict()

        elif isinstance(self._entity, AaSequence):
            entity = UNSET
            if not isinstance(self._entity, Unset):
                entity = self._entity.to_dict()

        else:
            entity = UNSET
            if not isinstance(self._entity, Unset):
                entity = self._entity.to_dict()

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

        def get_batch() -> Union[Unset, None, Batch]:
            batch = None
            _batch = d.pop("batch")
            if _batch is not None and not isinstance(_batch, Unset):
                batch = Batch.from_dict(_batch)

            return batch

        batch = get_batch() if "batch" in d else cast(Union[Unset, None, Batch], UNSET)

        def get_concentration() -> Union[Unset, Measurement]:
            concentration: Union[Unset, Measurement] = UNSET
            _concentration = d.pop("concentration")
            if not isinstance(_concentration, Unset):
                concentration = Measurement.from_dict(_concentration)

            return concentration

        concentration = (
            get_concentration() if "concentration" in d else cast(Union[Unset, Measurement], UNSET)
        )

        def get_entity() -> Union[Unset, None, DnaSequence, AaSequence, CustomEntity, UnknownType]:
            def _parse_entity(
                data: Union[Unset, None, Dict[str, Any]]
            ) -> Union[Unset, None, DnaSequence, AaSequence, CustomEntity, UnknownType]:
                entity: Union[Unset, None, DnaSequence, AaSequence, CustomEntity, UnknownType]
                if data is None:
                    return data
                if isinstance(data, Unset):
                    return data
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    entity = UNSET
                    _entity = data
                    if not isinstance(_entity, Unset):
                        entity = DnaSequence.from_dict(_entity)

                    return entity
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    entity = UNSET
                    _entity = data
                    if not isinstance(_entity, Unset):
                        entity = AaSequence.from_dict(_entity)

                    return entity
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    entity = UNSET
                    _entity = data
                    if not isinstance(_entity, Unset):
                        entity = CustomEntity.from_dict(_entity)

                    return entity
                except:  # noqa: E722
                    pass
                return UnknownType(data)

            entity = _parse_entity(d.pop("entity"))

            return entity

        entity = (
            get_entity()
            if "entity" in d
            else cast(Union[Unset, None, DnaSequence, AaSequence, CustomEntity, UnknownType], UNSET)
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
    def batch(self) -> Optional[Batch]:
        if isinstance(self._batch, Unset):
            raise NotPresentError(self, "batch")
        return self._batch

    @batch.setter
    def batch(self, value: Optional[Batch]) -> None:
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
    def entity(self) -> Optional[Union[DnaSequence, AaSequence, CustomEntity, UnknownType]]:
        if isinstance(self._entity, Unset):
            raise NotPresentError(self, "entity")
        return self._entity

    @entity.setter
    def entity(self, value: Optional[Union[DnaSequence, AaSequence, CustomEntity, UnknownType]]) -> None:
        self._entity = value

    @entity.deleter
    def entity(self) -> None:
        self._entity = UNSET
