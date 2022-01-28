from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.entity_archive_reason import EntityArchiveReason
from ..types import UNSET, Unset

T = TypeVar("T", bound="CustomEntitiesArchive")


@attr.s(auto_attribs=True, repr=False)
class CustomEntitiesArchive:
    """The request body for archiving custom entities."""

    _custom_entity_ids: List[str]
    _reason: EntityArchiveReason

    def __repr__(self):
        fields = []
        fields.append("custom_entity_ids={}".format(repr(self._custom_entity_ids)))
        fields.append("reason={}".format(repr(self._reason)))
        return "CustomEntitiesArchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        custom_entity_ids = self._custom_entity_ids

        reason = self._reason.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "customEntityIds": custom_entity_ids,
                "reason": reason,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_custom_entity_ids() -> List[str]:
            custom_entity_ids = cast(List[str], d.pop("customEntityIds"))

            return custom_entity_ids

        custom_entity_ids = get_custom_entity_ids() if "customEntityIds" in d else cast(List[str], UNSET)

        def get_reason() -> EntityArchiveReason:
            _reason = d.pop("reason")
            try:
                reason = EntityArchiveReason(_reason)
            except ValueError:
                reason = EntityArchiveReason.of_unknown(_reason)

            return reason

        reason = get_reason() if "reason" in d else cast(EntityArchiveReason, UNSET)

        custom_entities_archive = cls(
            custom_entity_ids=custom_entity_ids,
            reason=reason,
        )

        return custom_entities_archive

    @property
    def custom_entity_ids(self) -> List[str]:
        if isinstance(self._custom_entity_ids, Unset):
            raise NotPresentError(self, "custom_entity_ids")
        return self._custom_entity_ids

    @custom_entity_ids.setter
    def custom_entity_ids(self, value: List[str]) -> None:
        self._custom_entity_ids = value

    @property
    def reason(self) -> EntityArchiveReason:
        """The reason for archiving the provided entities. Accepted reasons may differ based on tenant configuration."""
        if isinstance(self._reason, Unset):
            raise NotPresentError(self, "reason")
        return self._reason

    @reason.setter
    def reason(self, value: EntityArchiveReason) -> None:
        self._reason = value
