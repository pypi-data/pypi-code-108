from functools import partial
from typing import Any, List, Tuple

from ..common import Predicate, Transform


class Simplification:
    """Reduce multiple config formats to more standard formats."""

    simplifications: List[Tuple[Predicate, Transform]]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._init_simplifications()
        super().__init__(*args, **kwargs)

    @classmethod
    def aggregate(cls, simplifications: List[Tuple[Predicate, Transform]]) -> Transform:
        """
        Create a Transform function from a list of simplifications.

        This Transform function will be the application of these
        simplifications.
        """
        return partial(cls.simplify_with, simplifications)

    @classmethod
    def simplify_with(cls, simplifications: List[Tuple[Predicate, Transform]], value: Any) -> Any:
        """
        Using a list of simplifications to simplify a value.
        """
        for predicate, transform in simplifications:
            if predicate(value):
                return cls.simplify_with(simplifications, transform(value))

        return value

    def _init_simplifications(self) -> None:
        self.simplifications = []

    def simplify(self, value: Any) -> Any:
        """
        Simplify a value with registered simplifications.
        """
        return self.simplify_with(self.simplifications, value)
