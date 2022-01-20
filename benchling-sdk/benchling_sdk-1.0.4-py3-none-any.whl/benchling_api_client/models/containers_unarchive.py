from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="ContainersUnarchive")


@attr.s(auto_attribs=True, repr=False)
class ContainersUnarchive:
    """  """

    _container_ids: List[str]

    def __repr__(self):
        fields = []
        fields.append("container_ids={}".format(repr(self._container_ids)))
        return "ContainersUnarchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        container_ids = self._container_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "containerIds": container_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_container_ids() -> List[str]:
            container_ids = cast(List[str], d.pop("containerIds"))

            return container_ids

        container_ids = get_container_ids() if "containerIds" in d else cast(List[str], UNSET)

        containers_unarchive = cls(
            container_ids=container_ids,
        )

        return containers_unarchive

    @property
    def container_ids(self) -> List[str]:
        """ Array of container IDs """
        if isinstance(self._container_ids, Unset):
            raise NotPresentError(self, "container_ids")
        return self._container_ids

    @container_ids.setter
    def container_ids(self, value: List[str]) -> None:
        self._container_ids = value
