from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.folders_archive_reason import FoldersArchiveReason
from ..types import UNSET, Unset

T = TypeVar("T", bound="FoldersArchive")


@attr.s(auto_attribs=True, repr=False)
class FoldersArchive:
    """  """

    _folder_ids: List[str]
    _reason: FoldersArchiveReason

    def __repr__(self):
        fields = []
        fields.append("folder_ids={}".format(repr(self._folder_ids)))
        fields.append("reason={}".format(repr(self._reason)))
        return "FoldersArchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        folder_ids = self._folder_ids

        reason = self._reason.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "folderIds": folder_ids,
                "reason": reason,
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

        def get_reason() -> FoldersArchiveReason:
            _reason = d.pop("reason")
            try:
                reason = FoldersArchiveReason(_reason)
            except ValueError:
                reason = FoldersArchiveReason.of_unknown(_reason)

            return reason

        reason = get_reason() if "reason" in d else cast(FoldersArchiveReason, UNSET)

        folders_archive = cls(
            folder_ids=folder_ids,
            reason=reason,
        )

        return folders_archive

    @property
    def folder_ids(self) -> List[str]:
        """ A list of folder IDs to archive. """
        if isinstance(self._folder_ids, Unset):
            raise NotPresentError(self, "folder_ids")
        return self._folder_ids

    @folder_ids.setter
    def folder_ids(self, value: List[str]) -> None:
        self._folder_ids = value

    @property
    def reason(self) -> FoldersArchiveReason:
        """The reason for archiving the provided folders. Accepted reasons may differ based on tenant configuration."""
        if isinstance(self._reason, Unset):
            raise NotPresentError(self, "reason")
        return self._reason

    @reason.setter
    def reason(self, value: FoldersArchiveReason) -> None:
        self._reason = value
