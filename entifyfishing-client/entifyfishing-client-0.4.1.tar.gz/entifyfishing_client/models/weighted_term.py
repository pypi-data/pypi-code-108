from typing import Any, Dict, Type, TypeVar

import attr

T = TypeVar("T", bound="WeightedTerm")


@attr.s(auto_attribs=True)
class WeightedTerm:
    """ """

    term: str
    score: float

    def to_dict(self) -> Dict[str, Any]:
        term = self.term
        score = self.score

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "term": term,
                "score": score,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        term = d.pop("term")

        score = d.pop("score")

        weighted_term = cls(
            term=term,
            score=score,
        )

        return weighted_term
