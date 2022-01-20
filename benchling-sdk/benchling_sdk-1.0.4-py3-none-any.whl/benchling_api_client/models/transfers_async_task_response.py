from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.container import Container
from ..types import UNSET, Unset

T = TypeVar("T", bound="TransfersAsyncTaskResponse")


@attr.s(auto_attribs=True, repr=False)
class TransfersAsyncTaskResponse:
    """  """

    _destination_containers: Union[Unset, List[Container]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("destination_containers={}".format(repr(self._destination_containers)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "TransfersAsyncTaskResponse({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        destination_containers: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._destination_containers, Unset):
            destination_containers = []
            for destination_containers_item_data in self._destination_containers:
                destination_containers_item = destination_containers_item_data.to_dict()

                destination_containers.append(destination_containers_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if destination_containers is not UNSET:
            field_dict["destinationContainers"] = destination_containers

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_destination_containers() -> Union[Unset, List[Container]]:
            destination_containers = []
            _destination_containers = d.pop("destinationContainers")
            for destination_containers_item_data in _destination_containers or []:
                destination_containers_item = Container.from_dict(destination_containers_item_data)

                destination_containers.append(destination_containers_item)

            return destination_containers

        destination_containers = (
            get_destination_containers()
            if "destinationContainers" in d
            else cast(Union[Unset, List[Container]], UNSET)
        )

        transfers_async_task_response = cls(
            destination_containers=destination_containers,
        )

        transfers_async_task_response.additional_properties = d
        return transfers_async_task_response

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
    def destination_containers(self) -> List[Container]:
        if isinstance(self._destination_containers, Unset):
            raise NotPresentError(self, "destination_containers")
        return self._destination_containers

    @destination_containers.setter
    def destination_containers(self, value: List[Container]) -> None:
        self._destination_containers = value

    @destination_containers.deleter
    def destination_containers(self) -> None:
        self._destination_containers = UNSET
