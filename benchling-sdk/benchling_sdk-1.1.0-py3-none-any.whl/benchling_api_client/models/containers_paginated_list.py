from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.container import Container
from ..types import UNSET, Unset

T = TypeVar("T", bound="ContainersPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class ContainersPaginatedList:
    """  """

    _next_token: Union[Unset, str] = UNSET
    _containers: Union[Unset, List[Container]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("containers={}".format(repr(self._containers)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "ContainersPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        next_token = self._next_token
        containers: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._containers, Unset):
            containers = []
            for containers_item_data in self._containers:
                containers_item = containers_item_data.to_dict()

                containers.append(containers_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token
        if containers is not UNSET:
            field_dict["containers"] = containers

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        def get_containers() -> Union[Unset, List[Container]]:
            containers = []
            _containers = d.pop("containers")
            for containers_item_data in _containers or []:
                containers_item = Container.from_dict(containers_item_data)

                containers.append(containers_item)

            return containers

        containers = get_containers() if "containers" in d else cast(Union[Unset, List[Container]], UNSET)

        containers_paginated_list = cls(
            next_token=next_token,
            containers=containers,
        )

        containers_paginated_list.additional_properties = d
        return containers_paginated_list

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
    def next_token(self) -> str:
        if isinstance(self._next_token, Unset):
            raise NotPresentError(self, "next_token")
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value

    @next_token.deleter
    def next_token(self) -> None:
        self._next_token = UNSET

    @property
    def containers(self) -> List[Container]:
        if isinstance(self._containers, Unset):
            raise NotPresentError(self, "containers")
        return self._containers

    @containers.setter
    def containers(self, value: List[Container]) -> None:
        self._containers = value

    @containers.deleter
    def containers(self) -> None:
        self._containers = UNSET
