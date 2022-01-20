from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="ContainersArchivalChange")


@attr.s(auto_attribs=True, repr=False)
class ContainersArchivalChange:
    """IDs of all items that were unarchived, grouped by resource type. This includes the IDs of containers that were unarchived."""

    _container_ids: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("container_ids={}".format(repr(self._container_ids)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "ContainersArchivalChange({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        container_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._container_ids, Unset):
            container_ids = self._container_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if container_ids is not UNSET:
            field_dict["containerIds"] = container_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_container_ids() -> Union[Unset, List[str]]:
            container_ids = cast(List[str], d.pop("containerIds"))

            return container_ids

        container_ids = get_container_ids() if "containerIds" in d else cast(Union[Unset, List[str]], UNSET)

        containers_archival_change = cls(
            container_ids=container_ids,
        )

        containers_archival_change.additional_properties = d
        return containers_archival_change

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
    def container_ids(self) -> List[str]:
        if isinstance(self._container_ids, Unset):
            raise NotPresentError(self, "container_ids")
        return self._container_ids

    @container_ids.setter
    def container_ids(self, value: List[str]) -> None:
        self._container_ids = value

    @container_ids.deleter
    def container_ids(self) -> None:
        self._container_ids = UNSET
