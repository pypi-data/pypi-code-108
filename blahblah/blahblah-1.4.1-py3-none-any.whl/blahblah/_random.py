import random
from typing import Any, List, Sequence, TypeVar

__all__ = ("Random",)

_T = TypeVar("_T")
SeedType = TypeVar("SeedType", int, float, str, bytes, bytearray)


class Random:
    def set_seed(self, seed: SeedType) -> None:
        random.seed(seed)

    def random_int(self, start: int, end: int) -> int:
        return random.randint(start, end)

    def random_float(self, start: float, end: float) -> float:
        return random.uniform(start, end)

    def random_str(self, length: int, alphabet: str) -> str:
        return "".join(random.choice(alphabet) for _ in range(length))

    def random_choice(self, sequence: Sequence[_T]) -> _T:
        return random.choice(sequence)

    def shuffle_list(self, elements: List[Any]) -> None:
        random.shuffle(elements)
