from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.concept import Concept
from ..types import UNSET, Unset

T = TypeVar("T", bound="WeightedTermEntities")


@attr.s(auto_attribs=True)
class WeightedTermEntities:
    """ """

    term: str
    score: float
    entities: Union[Unset, List[Concept]] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        term = self.term
        score = self.score
        entities: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.entities, Unset):
            entities = []
            for entities_item_data in self.entities:
                entities_item = entities_item_data.to_dict()

                entities.append(entities_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "term": term,
                "score": score,
            }
        )
        if entities is not UNSET:
            field_dict["entities"] = entities

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        term = d.pop("term")

        score = d.pop("score")

        entities = []
        _entities = d.pop("entities", UNSET)
        for entities_item_data in _entities or []:
            entities_item = Concept.from_dict(entities_item_data)

            entities.append(entities_item)

        weighted_term_entities = cls(
            term=term,
            score=score,
            entities=entities,
        )

        return weighted_term_entities
