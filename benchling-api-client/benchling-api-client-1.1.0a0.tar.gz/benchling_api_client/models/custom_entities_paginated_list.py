from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.custom_entity import CustomEntity
from ..types import UNSET, Unset

T = TypeVar("T", bound="CustomEntitiesPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class CustomEntitiesPaginatedList:
    """  """

    _custom_entities: Union[Unset, List[CustomEntity]] = UNSET
    _next_token: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("custom_entities={}".format(repr(self._custom_entities)))
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "CustomEntitiesPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        custom_entities: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._custom_entities, Unset):
            custom_entities = []
            for custom_entities_item_data in self._custom_entities:
                custom_entities_item = custom_entities_item_data.to_dict()

                custom_entities.append(custom_entities_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if custom_entities is not UNSET:
            field_dict["customEntities"] = custom_entities
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_custom_entities() -> Union[Unset, List[CustomEntity]]:
            custom_entities = []
            _custom_entities = d.pop("customEntities")
            for custom_entities_item_data in _custom_entities or []:
                custom_entities_item = CustomEntity.from_dict(custom_entities_item_data)

                custom_entities.append(custom_entities_item)

            return custom_entities

        custom_entities = (
            get_custom_entities() if "customEntities" in d else cast(Union[Unset, List[CustomEntity]], UNSET)
        )

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        custom_entities_paginated_list = cls(
            custom_entities=custom_entities,
            next_token=next_token,
        )

        custom_entities_paginated_list.additional_properties = d
        return custom_entities_paginated_list

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

    def get(self, key, default=None) -> Optional[Any]:
        return self.additional_properties.get(key, default)

    @property
    def custom_entities(self) -> List[CustomEntity]:
        if isinstance(self._custom_entities, Unset):
            raise NotPresentError(self, "custom_entities")
        return self._custom_entities

    @custom_entities.setter
    def custom_entities(self, value: List[CustomEntity]) -> None:
        self._custom_entities = value

    @custom_entities.deleter
    def custom_entities(self) -> None:
        self._custom_entities = UNSET

    @property
    def next_token(self) -> str:
        if isinstance(self._next_token, Unset):
            raise NotPresentError(self, "next_token")
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value

    @next_token.deleter
    def next_token(self) -> None:
        self._next_token = UNSET
