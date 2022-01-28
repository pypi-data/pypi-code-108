from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="EntryAttachments")


@attr.s(auto_attribs=True, repr=False)
class EntryAttachments:
    """  """

    _attachments: Union[Unset, List[str]] = UNSET

    def __repr__(self):
        fields = []
        fields.append("attachments={}".format(repr(self._attachments)))
        return "EntryAttachments({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        attachments: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._attachments, Unset):
            attachments = self._attachments

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if attachments is not UNSET:
            field_dict["attachments"] = attachments

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_attachments() -> Union[Unset, List[str]]:
            attachments = cast(List[str], d.pop("attachments"))

            return attachments

        attachments = get_attachments() if "attachments" in d else cast(Union[Unset, List[str]], UNSET)

        entry_attachments = cls(
            attachments=attachments,
        )

        return entry_attachments

    @property
    def attachments(self) -> List[str]:
        """An array of IDs representing Blob objects in Benchling to be attached to the entry."""
        if isinstance(self._attachments, Unset):
            raise NotPresentError(self, "attachments")
        return self._attachments

    @attachments.setter
    def attachments(self, value: List[str]) -> None:
        self._attachments = value

    @attachments.deleter
    def attachments(self) -> None:
        self._attachments = UNSET
