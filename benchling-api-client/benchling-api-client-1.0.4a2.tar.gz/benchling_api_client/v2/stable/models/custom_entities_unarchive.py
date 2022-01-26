from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="CustomEntitiesUnarchive")


@attr.s(auto_attribs=True, repr=False)
class CustomEntitiesUnarchive:
    """The request body for unarchiving custom entities."""

    _custom_entity_ids: List[str]

    def __repr__(self):
        fields = []
        fields.append("custom_entity_ids={}".format(repr(self._custom_entity_ids)))
        return "CustomEntitiesUnarchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        custom_entity_ids = self._custom_entity_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "customEntityIds": custom_entity_ids,
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

        custom_entities_unarchive = cls(
            custom_entity_ids=custom_entity_ids,
        )

        return custom_entities_unarchive

    @property
    def custom_entity_ids(self) -> List[str]:
        if isinstance(self._custom_entity_ids, Unset):
            raise NotPresentError(self, "custom_entity_ids")
        return self._custom_entity_ids

    @custom_entity_ids.setter
    def custom_entity_ids(self, value: List[str]) -> None:
        self._custom_entity_ids = value
