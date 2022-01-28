from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.custom_entity_bulk_create import CustomEntityBulkCreate
from ..types import UNSET, Unset

T = TypeVar("T", bound="CustomEntitiesBulkCreateRequest")


@attr.s(auto_attribs=True, repr=False)
class CustomEntitiesBulkCreateRequest:
    """  """

    _custom_entities: List[CustomEntityBulkCreate]

    def __repr__(self):
        fields = []
        fields.append("custom_entities={}".format(repr(self._custom_entities)))
        return "CustomEntitiesBulkCreateRequest({})".format(", ".join(fields))

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

        def get_custom_entities() -> List[CustomEntityBulkCreate]:
            custom_entities = []
            _custom_entities = d.pop("customEntities")
            for custom_entities_item_data in _custom_entities:
                custom_entities_item = CustomEntityBulkCreate.from_dict(custom_entities_item_data)

                custom_entities.append(custom_entities_item)

            return custom_entities

        custom_entities = (
            get_custom_entities() if "customEntities" in d else cast(List[CustomEntityBulkCreate], UNSET)
        )

        custom_entities_bulk_create_request = cls(
            custom_entities=custom_entities,
        )

        return custom_entities_bulk_create_request

    @property
    def custom_entities(self) -> List[CustomEntityBulkCreate]:
        if isinstance(self._custom_entities, Unset):
            raise NotPresentError(self, "custom_entities")
        return self._custom_entities

    @custom_entities.setter
    def custom_entities(self, value: List[CustomEntityBulkCreate]) -> None:
        self._custom_entities = value
