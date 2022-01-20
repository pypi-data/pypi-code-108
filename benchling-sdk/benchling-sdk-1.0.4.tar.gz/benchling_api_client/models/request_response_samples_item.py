from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError, UnknownType
from ..models.aa_sequence import AaSequence
from ..models.custom_entity import CustomEntity
from ..models.dna_sequence import DnaSequence
from ..models.request_response_samples_item_batch import RequestResponseSamplesItemBatch
from ..models.request_response_samples_item_status import RequestResponseSamplesItemStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="RequestResponseSamplesItem")


@attr.s(auto_attribs=True, repr=False)
class RequestResponseSamplesItem:
    """  """

    _batch: Union[Unset, RequestResponseSamplesItemBatch] = UNSET
    _entity: Union[Unset, None, DnaSequence, AaSequence, CustomEntity, UnknownType] = UNSET
    _status: Union[Unset, RequestResponseSamplesItemStatus] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("batch={}".format(repr(self._batch)))
        fields.append("entity={}".format(repr(self._entity)))
        fields.append("status={}".format(repr(self._status)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "RequestResponseSamplesItem({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        batch: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._batch, Unset):
            batch = self._batch.to_dict()

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

        status: Union[Unset, int] = UNSET
        if not isinstance(self._status, Unset):
            status = self._status.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if batch is not UNSET:
            field_dict["batch"] = batch
        if entity is not UNSET:
            field_dict["entity"] = entity
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_batch() -> Union[Unset, RequestResponseSamplesItemBatch]:
            batch: Union[Unset, RequestResponseSamplesItemBatch] = UNSET
            _batch = d.pop("batch")
            if not isinstance(_batch, Unset):
                batch = RequestResponseSamplesItemBatch.from_dict(_batch)

            return batch

        batch = get_batch() if "batch" in d else cast(Union[Unset, RequestResponseSamplesItemBatch], UNSET)

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

        def get_status() -> Union[Unset, RequestResponseSamplesItemStatus]:
            status = None
            _status = d.pop("status")
            if _status is not None and _status is not UNSET:
                try:
                    status = RequestResponseSamplesItemStatus(_status)
                except ValueError:
                    status = RequestResponseSamplesItemStatus.of_unknown(_status)

            return status

        status = (
            get_status() if "status" in d else cast(Union[Unset, RequestResponseSamplesItemStatus], UNSET)
        )

        request_response_samples_item = cls(
            batch=batch,
            entity=entity,
            status=status,
        )

        request_response_samples_item.additional_properties = d
        return request_response_samples_item

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
    def batch(self) -> RequestResponseSamplesItemBatch:
        if isinstance(self._batch, Unset):
            raise NotPresentError(self, "batch")
        return self._batch

    @batch.setter
    def batch(self, value: RequestResponseSamplesItemBatch) -> None:
        self._batch = value

    @batch.deleter
    def batch(self) -> None:
        self._batch = UNSET

    @property
    def entity(self) -> Optional[Union[DnaSequence, AaSequence, CustomEntity, UnknownType]]:
        """ The sample, if it is an entity resource. Null otherwise. """
        if isinstance(self._entity, Unset):
            raise NotPresentError(self, "entity")
        return self._entity

    @entity.setter
    def entity(self, value: Optional[Union[DnaSequence, AaSequence, CustomEntity, UnknownType]]) -> None:
        self._entity = value

    @entity.deleter
    def entity(self) -> None:
        self._entity = UNSET

    @property
    def status(self) -> RequestResponseSamplesItemStatus:
        """ The status of the sample, based on the status of the stage run that generated it. """
        if isinstance(self._status, Unset):
            raise NotPresentError(self, "status")
        return self._status

    @status.setter
    def status(self, value: RequestResponseSamplesItemStatus) -> None:
        self._status = value

    @status.deleter
    def status(self) -> None:
        self._status = UNSET
