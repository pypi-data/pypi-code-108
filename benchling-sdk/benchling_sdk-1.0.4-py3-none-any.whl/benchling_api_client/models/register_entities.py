from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.naming_strategy import NamingStrategy
from ..types import UNSET, Unset

T = TypeVar("T", bound="RegisterEntities")


@attr.s(auto_attribs=True, repr=False)
class RegisterEntities:
    """  """

    _entity_ids: List[str]
    _naming_strategy: NamingStrategy

    def __repr__(self):
        fields = []
        fields.append("entity_ids={}".format(repr(self._entity_ids)))
        fields.append("naming_strategy={}".format(repr(self._naming_strategy)))
        return "RegisterEntities({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        entity_ids = self._entity_ids

        naming_strategy = self._naming_strategy.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "entityIds": entity_ids,
                "namingStrategy": naming_strategy,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_entity_ids() -> List[str]:
            entity_ids = cast(List[str], d.pop("entityIds"))

            return entity_ids

        entity_ids = get_entity_ids() if "entityIds" in d else cast(List[str], UNSET)

        def get_naming_strategy() -> NamingStrategy:
            _naming_strategy = d.pop("namingStrategy")
            try:
                naming_strategy = NamingStrategy(_naming_strategy)
            except ValueError:
                naming_strategy = NamingStrategy.of_unknown(_naming_strategy)

            return naming_strategy

        naming_strategy = get_naming_strategy() if "namingStrategy" in d else cast(NamingStrategy, UNSET)

        register_entities = cls(
            entity_ids=entity_ids,
            naming_strategy=naming_strategy,
        )

        return register_entities

    @property
    def entity_ids(self) -> List[str]:
        """ Array of entity IDs """
        if isinstance(self._entity_ids, Unset):
            raise NotPresentError(self, "entity_ids")
        return self._entity_ids

    @entity_ids.setter
    def entity_ids(self, value: List[str]) -> None:
        self._entity_ids = value

    @property
    def naming_strategy(self) -> NamingStrategy:
        """Specifies the behavior for automatically generated names when registering an entity.
        - NEW_IDS: Generate new registry IDs
        - IDS_FROM_NAMES: Generate registry IDs based on entity names
        - DELETE_NAMES: Generate new registry IDs and replace name with registry ID
        - SET_FROM_NAME_PARTS: Generate new registry IDs, rename according to name template, and keep old name as alias
        - REPLACE_NAMES_FROM_PARTS: Generate new registry IDs, and replace name according to name template
        - KEEP_NAMES: Keep existing entity names as registry IDs
        - REPLACE_ID_AND_NAME_FROM_PARTS: Generate registry IDs and names according to name template
        """
        if isinstance(self._naming_strategy, Unset):
            raise NotPresentError(self, "naming_strategy")
        return self._naming_strategy

    @naming_strategy.setter
    def naming_strategy(self, value: NamingStrategy) -> None:
        self._naming_strategy = value
