from dataclasses import dataclass
from typing import Any
from typing import Dict


@dataclass
class AggregationFunction:
    name: str
    params: Dict[str, Any]


def last_distinct(n: int) -> AggregationFunction:
    return AggregationFunction("lastn", {"n": n})
