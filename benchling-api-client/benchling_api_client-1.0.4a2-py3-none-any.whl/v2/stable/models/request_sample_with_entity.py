from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="RequestSampleWithEntity")


@attr.s(auto_attribs=True, repr=False)
class RequestSampleWithEntity:
    """  """

    _entity_id: str
    _container_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("entity_id={}".format(repr(self._entity_id)))
        fields.append("container_id={}".format(repr(self._container_id)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "RequestSampleWithEntity({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        entity_id = self._entity_id
        container_id = self._container_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "entityId": entity_id,
            }
        )
        if container_id is not UNSET:
            field_dict["containerId"] = container_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_entity_id() -> str:
            entity_id = d.pop("entityId")
            return entity_id

        entity_id = get_entity_id() if "entityId" in d else cast(str, UNSET)

        def get_container_id() -> Union[Unset, str]:
            container_id = d.pop("containerId")
            return container_id

        container_id = get_container_id() if "containerId" in d else cast(Union[Unset, str], UNSET)

        request_sample_with_entity = cls(
            entity_id=entity_id,
            container_id=container_id,
        )

        request_sample_with_entity.additional_properties = d
        return request_sample_with_entity

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
    def entity_id(self) -> str:
        if isinstance(self._entity_id, Unset):
            raise NotPresentError(self, "entity_id")
        return self._entity_id

    @entity_id.setter
    def entity_id(self, value: str) -> None:
        self._entity_id = value

    @property
    def container_id(self) -> str:
        if isinstance(self._container_id, Unset):
            raise NotPresentError(self, "container_id")
        return self._container_id

    @container_id.setter
    def container_id(self, value: str) -> None:
        self._container_id = value

    @container_id.deleter
    def container_id(self) -> None:
        self._container_id = UNSET
