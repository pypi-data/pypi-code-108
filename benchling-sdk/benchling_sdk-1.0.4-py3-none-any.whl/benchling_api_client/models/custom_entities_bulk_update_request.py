from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.custom_entity_bulk_update import CustomEntityBulkUpdate
from ..types import UNSET, Unset

T = TypeVar("T", bound="CustomEntitiesBulkUpdateRequest")


@attr.s(auto_attribs=True, repr=False)
class CustomEntitiesBulkUpdateRequest:
    """  """

    _custom_entities: List[CustomEntityBulkUpdate]

    def __repr__(self):
        fields = []
        fields.append("custom_entities={}".format(repr(self._custom_entities)))
        return "CustomEntitiesBulkUpdateRequest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        custom_entities = []
        for custom_entities_item_data in self._custom_entities:
            custom_entities_item = custom_entities_item_data.to_dict()

            custom_entities.append(custom_entities_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "customEntities": custom_entities,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_custom_entities() -> List[CustomEntityBulkUpdate]:
            custom_entities = []
            _custom_entities = d.pop("customEntities")
            for custom_entities_item_data in _custom_entities:
                custom_entities_item = CustomEntityBulkUpdate.from_dict(custom_entities_item_data)

                custom_entities.append(custom_entities_item)

            return custom_entities

        custom_entities = (
            get_custom_entities() if "customEntities" in d else cast(List[CustomEntityBulkUpdate], UNSET)
        )

        custom_entities_bulk_update_request = cls(
            custom_entities=custom_entities,
        )

        return custom_entities_bulk_update_request

    @property
    def custom_entities(self) -> List[CustomEntityBulkUpdate]:
        if isinstance(self._custom_entities, Unset):
            raise NotPresentError(self, "custom_entities")
        return self._custom_entities

    @custom_entities.setter
    def custom_entities(self, value: List[CustomEntityBulkUpdate]) -> None:
        self._custom_entities = value
