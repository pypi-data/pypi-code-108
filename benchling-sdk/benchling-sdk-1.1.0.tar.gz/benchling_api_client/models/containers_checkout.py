from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="ContainersCheckout")


@attr.s(auto_attribs=True, repr=False)
class ContainersCheckout:
    """  """

    _assignee_id: str
    _container_ids: List[str]
    _comment: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("assignee_id={}".format(repr(self._assignee_id)))
        fields.append("container_ids={}".format(repr(self._container_ids)))
        fields.append("comment={}".format(repr(self._comment)))
        return "ContainersCheckout({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        assignee_id = self._assignee_id
        container_ids = self._container_ids

        comment = self._comment

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "assigneeId": assignee_id,
                "containerIds": container_ids,
            }
        )
        if comment is not UNSET:
            field_dict["comment"] = comment

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_assignee_id() -> str:
            assignee_id = d.pop("assigneeId")
            return assignee_id

        assignee_id = get_assignee_id() if "assigneeId" in d else cast(str, UNSET)

        def get_container_ids() -> List[str]:
            container_ids = cast(List[str], d.pop("containerIds"))

            return container_ids

        container_ids = get_container_ids() if "containerIds" in d else cast(List[str], UNSET)

        def get_comment() -> Union[Unset, str]:
            comment = d.pop("comment")
            return comment

        comment = get_comment() if "comment" in d else cast(Union[Unset, str], UNSET)

        containers_checkout = cls(
            assignee_id=assignee_id,
            container_ids=container_ids,
            comment=comment,
        )

        return containers_checkout

    @property
    def assignee_id(self) -> str:
        """ User or Team API ID. """
        if isinstance(self._assignee_id, Unset):
            raise NotPresentError(self, "assignee_id")
        return self._assignee_id

    @assignee_id.setter
    def assignee_id(self, value: str) -> None:
        self._assignee_id = value

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
    def comment(self) -> str:
        if isinstance(self._comment, Unset):
            raise NotPresentError(self, "comment")
        return self._comment

    @comment.setter
    def comment(self, value: str) -> None:
        self._comment = value

    @comment.deleter
    def comment(self) -> None:
        self._comment = UNSET
