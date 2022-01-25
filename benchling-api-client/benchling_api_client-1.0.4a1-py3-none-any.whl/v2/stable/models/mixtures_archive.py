from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.entity_archive_reason import EntityArchiveReason
from ..types import UNSET, Unset

T = TypeVar("T", bound="MixturesArchive")


@attr.s(auto_attribs=True, repr=False)
class MixturesArchive:
    """The request body for archiving mixtures."""

    _mixture_ids: List[str]
    _reason: EntityArchiveReason

    def __repr__(self):
        fields = []
        fields.append("mixture_ids={}".format(repr(self._mixture_ids)))
        fields.append("reason={}".format(repr(self._reason)))
        return "MixturesArchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        mixture_ids = self._mixture_ids

        reason = self._reason.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "mixtureIds": mixture_ids,
                "reason": reason,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_mixture_ids() -> List[str]:
            mixture_ids = cast(List[str], d.pop("mixtureIds"))

            return mixture_ids

        mixture_ids = get_mixture_ids() if "mixtureIds" in d else cast(List[str], UNSET)

        def get_reason() -> EntityArchiveReason:
            _reason = d.pop("reason")
            try:
                reason = EntityArchiveReason(_reason)
            except ValueError:
                reason = EntityArchiveReason.of_unknown(_reason)

            return reason

        reason = get_reason() if "reason" in d else cast(EntityArchiveReason, UNSET)

        mixtures_archive = cls(
            mixture_ids=mixture_ids,
            reason=reason,
        )

        return mixtures_archive

    @property
    def mixture_ids(self) -> List[str]:
        if isinstance(self._mixture_ids, Unset):
            raise NotPresentError(self, "mixture_ids")
        return self._mixture_ids

    @mixture_ids.setter
    def mixture_ids(self, value: List[str]) -> None:
        self._mixture_ids = value

    @property
    def reason(self) -> EntityArchiveReason:
        """The reason for archiving the provided entities. Accepted reasons may differ based on tenant configuration."""
        if isinstance(self._reason, Unset):
            raise NotPresentError(self, "reason")
        return self._reason

    @reason.setter
    def reason(self, value: EntityArchiveReason) -> None:
        self._reason = value
