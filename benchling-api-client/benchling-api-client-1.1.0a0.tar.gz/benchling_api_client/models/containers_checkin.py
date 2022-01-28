from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="ContainersCheckin")


@attr.s(auto_attribs=True, repr=False)
class ContainersCheckin:
    """  """

    _container_ids: List[str]
    _comments: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("container_ids={}".format(repr(self._container_ids)))
        fields.append("comments={}".format(repr(self._comments)))
        return "ContainersCheckin({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        container_ids = self._container_ids

        comments = self._comments

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "containerIds": container_ids,
            }
        )
        if comments is not UNSET:
            field_dict["comments"] = comments

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_container_ids() -> List[str]:
            container_ids = cast(List[str], d.pop("containerIds"))

            return container_ids

        container_ids = get_container_ids() if "containerIds" in d else cast(List[str], UNSET)

        def get_comments() -> Union[Unset, str]:
            comments = d.pop("comments")
            return comments

        comments = get_comments() if "comments" in d else cast(Union[Unset, str], UNSET)

        containers_checkin = cls(
            container_ids=container_ids,
            comments=comments,
        )

        return containers_checkin

    @property
    def container_ids(self) -> List[str]:
        """ Array of container IDs. """
        if isinstance(self._container_ids, Unset):
            raise NotPresentError(self, "container_ids")
        return self._container_ids

    @container_ids.setter
    def container_ids(self, value: List[str]) -> None:
        self._container_ids = value

    @property
    def comments(self) -> str:
        if isinstance(self._comments, Unset):
            raise NotPresentError(self, "comments")
        return self._comments

    @comments.setter
    def comments(self, value: str) -> None:
        self._comments = value

    @comments.deleter
    def comments(self) -> None:
        self._comments = UNSET
