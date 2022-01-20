from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.entries_archive_reason import EntriesArchiveReason
from ..types import UNSET, Unset

T = TypeVar("T", bound="EntriesArchive")


@attr.s(auto_attribs=True, repr=False)
class EntriesArchive:
    """  """

    _entry_ids: List[str]
    _reason: EntriesArchiveReason

    def __repr__(self):
        fields = []
        fields.append("entry_ids={}".format(repr(self._entry_ids)))
        fields.append("reason={}".format(repr(self._reason)))
        return "EntriesArchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        entry_ids = self._entry_ids

        reason = self._reason.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "entryIds": entry_ids,
                "reason": reason,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_entry_ids() -> List[str]:
            entry_ids = cast(List[str], d.pop("entryIds"))

            return entry_ids

        entry_ids = get_entry_ids() if "entryIds" in d else cast(List[str], UNSET)

        def get_reason() -> EntriesArchiveReason:
            _reason = d.pop("reason")
            try:
                reason = EntriesArchiveReason(_reason)
            except ValueError:
                reason = EntriesArchiveReason.of_unknown(_reason)

            return reason

        reason = get_reason() if "reason" in d else cast(EntriesArchiveReason, UNSET)

        entries_archive = cls(
            entry_ids=entry_ids,
            reason=reason,
        )

        return entries_archive

    @property
    def entry_ids(self) -> List[str]:
        """ Array of entry IDs """
        if isinstance(self._entry_ids, Unset):
            raise NotPresentError(self, "entry_ids")
        return self._entry_ids

    @entry_ids.setter
    def entry_ids(self, value: List[str]) -> None:
        self._entry_ids = value

    @property
    def reason(self) -> EntriesArchiveReason:
        """Reason that entries are being archived. One of ["Made in error", "Retired", "Other"]."""
        if isinstance(self._reason, Unset):
            raise NotPresentError(self, "reason")
        return self._reason

    @reason.setter
    def reason(self, value: EntriesArchiveReason) -> None:
        self._reason = value
