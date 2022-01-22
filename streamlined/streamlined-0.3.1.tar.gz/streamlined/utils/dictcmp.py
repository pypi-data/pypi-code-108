from __future__ import annotations

from dataclasses import dataclass
from operator import eq
from typing import Callable, Dict, Generic, Iterable, Optional, Set, TypeVar

from ..common import IDENTITY

K = TypeVar("K")
V = TypeVar("V")


MissingInSourceFormatter = Callable[[K, V], str]
MissingInTargetFormatter = Callable[[K, V], str]
EqualValueFormatter = Callable[[K, V, K, V], str]
UnequalValueFormatter = Callable[[K, V, K, V], str]


@dataclass
class ItemPair(Generic[K, V]):
    @staticmethod
    def DEFAULT_MISSING_IN_SOURCE_FORMATTER(target_key: K, target_value: V) -> str:
        return f"{target_key} is only present in target with value {target_value}"

    @staticmethod
    def DEFAULT_MISSING_IN_TARGET_FORMATTER(source_key: K, source_value: V) -> str:
        return f"{source_key} is only present in source with value {source_value}"

    @staticmethod
    def DEFAULT_EQUAL_VALUE_FORMATTER(
        source_key: K, source_value: V, target_key: K, target_value: V
    ) -> str:
        return f"source[{source_key}] and target[{target_key}] have equal value {source_value} and {target_value}"

    @staticmethod
    def DEFAULT_UNEQUAL_VALUE_FORMATTER(
        source_key: K, source_value: V, target_key: K, target_value: V
    ) -> str:
        return f"source[{source_key}] has value {source_value} while target[{target_key}] has value {target_value}"

    source_key: Optional[K] = None
    source_value: Optional[V] = None
    target_key: Optional[K] = None
    target_value: Optional[V] = None

    are_equal: bool = False

    @property
    def is_missing_in_source(self) -> bool:
        return self.source_key is None

    @property
    def is_missing_in_target(self) -> bool:
        return self.target_key is None

    @property
    def is_present_in_both(self) -> bool:
        return not self.is_missing_in_source and not self.is_missing_in_target

    @property
    def is_present_and_equal(self) -> bool:
        return self.is_present_in_both and self.are_equal

    def format(
        self,
        missing_in_source_formatter: Optional[MissingInSourceFormatter[K, V]] = None,
        missing_in_target_formatter: Optional[MissingInTargetFormatter[K, V]] = None,
        unequal_value_formatter: Optional[UnequalValueFormatter[K, V]] = None,
        equal_value_formatter: Optional[EqualValueFormatter[K, V]] = None,
    ) -> str:
        if missing_in_source_formatter is None:
            missing_in_source_formatter = self.DEFAULT_MISSING_IN_SOURCE_FORMATTER
        if missing_in_target_formatter is None:
            missing_in_target_formatter = self.DEFAULT_MISSING_IN_TARGET_FORMATTER
        if unequal_value_formatter is None:
            unequal_value_formatter = self.DEFAULT_UNEQUAL_VALUE_FORMATTER
        if equal_value_formatter is None:
            equal_value_formatter = self.DEFAULT_EQUAL_VALUE_FORMATTER

        if self.is_missing_in_source:
            return missing_in_source_formatter(self.target_key, self.target_value)
        elif self.is_missing_in_target:
            return missing_in_target_formatter(self.source_key, self.source_value)
        else:  # self.is_present_in_both:
            formatter = (
                equal_value_formatter if self.is_present_and_equal else unequal_value_formatter
            )
            return formatter(
                self.source_key, self.source_value, self.target_key, self.target_value
            )


def dict_cmp(
    source: Dict[K, V],
    target: Dict[K, V],
    key_func: Callable[[K], K] = IDENTITY,
    are_equal: Callable[[V, V], bool] = eq,
) -> Iterable[ItemPair[K, V]]:
    target_keys: Set[K] = set(target.keys())

    for source_key, source_value in source.items():
        transformed_source_key = key_func(source_key)
        try:
            target_keys.remove(transformed_source_key)
            target_key = transformed_source_key
            target_value = target[target_key]
            yield ItemPair(
                source_key=source_key,
                source_value=source_value,
                target_key=target_key,
                target_value=target_value,
                are_equal=are_equal(source_value, target_value),
            )
        except KeyError:
            yield ItemPair(source_key=source_key, source_value=source_value)

    for target_key in target_keys:
        target_value = target[target_key]
        yield ItemPair(target_key=target_key, target_value=target_value)
