from functools import cached_property
from typing import Any, Callable, Iterable, List, Tuple

from ..common import AND, IS_DICT, NOT, OR, TYPE, Predicate, Transform
from .simplification import Simplification


class Variant(Simplification):
    """
    A variant capture an extended config format.

    To reduce the parsing work, Variant will reduce this extended
    format to standard format.
    """

    _variant_simplifications: List[Tuple[Predicate, Transform]]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._init_simplifications_for_variant()
        super().__init__(*args, **kwargs)

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__.lower()

    @classmethod
    def verify(cls, value: Any) -> None:
        """
        Verify is compliant variant config format.

        Should raise exception when not compliant.
        """

    @classmethod
    def reduce(cls, value: Any) -> Any:
        """
        Convert value from variant format to standard format.
        """
        cls.verify(value)

        return value

    @classmethod
    def is_variant(cls, value: Any) -> bool:
        return IS_DICT(value) and TYPE in value and value[TYPE] == cls.get_name()

    @cached_property
    def is_simplified_variant(self) -> Callable[[Any], bool]:
        return AND(self.is_variant, NOT(OR(*self._variant_predicates)))

    @cached_property
    def is_not_simplified_variant(self) -> Callable[[Any], bool]:
        return AND(self.is_variant, OR(*self._variant_predicates))

    @cached_property
    def simplify_variant(self) -> Callable[[Any], Any]:
        return self.aggregate(self._variant_simplifications)

    @cached_property
    def name(self) -> str:
        return self.__class__.get_name()

    @property
    def _variant_predicates(self) -> Iterable[Predicate]:
        for predicate, _ in self._variant_simplifications:
            yield predicate

    def _init_simplifications_for_variant(self) -> None:
        self._variant_simplifications = []

    def _init_simplifications(self) -> None:
        super()._init_simplifications()

        self.simplifications.append((self.is_not_simplified_variant, self.simplify_variant))

        self.simplifications.append((self.is_simplified_variant, self.reduce))


class WithVariants(Simplification):
    variants: List[Variant]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._init_variants()
        super().__init__(*args, **kwargs)

    def _init_variants(self) -> None:
        self.variants = []

    def _init_simplifications(self) -> None:
        super()._init_simplifications()

        for variant in self.variants:
            self.simplifications.extend(variant.simplifications)
