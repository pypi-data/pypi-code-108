from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="FoldersUnarchive")


@attr.s(auto_attribs=True, repr=False)
class FoldersUnarchive:
    """  """

    _folder_ids: List[str]

    def __repr__(self):
        fields = []
        fields.append("folder_ids={}".format(repr(self._folder_ids)))
        return "FoldersUnarchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        folder_ids = self._folder_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "folderIds": folder_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_folder_ids() -> List[str]:
            folder_ids = cast(List[str], d.pop("folderIds"))

            return folder_ids

        folder_ids = get_folder_ids() if "folderIds" in d else cast(List[str], UNSET)

        folders_unarchive = cls(
            folder_ids=folder_ids,
        )

        return folders_unarchive

    @property
    def folder_ids(self) -> List[str]:
        """ A list of folder IDs to unarchive. """
        if isinstance(self._folder_ids, Unset):
            raise NotPresentError(self, "folder_ids")
        return self._folder_ids

    @folder_ids.setter
    def folder_ids(self, value: List[str]) -> None:
        self._folder_ids = value
