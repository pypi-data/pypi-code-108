import typing as T
from dataclasses import dataclass
from dbt.contracts.results import TimingInfo

Status = T.Union[None, str, int, bool]


@dataclass
class Freshness:
    unit: str
    age: float
    loader: str
    threshold: float


@dataclass
class Reporting:
    rows: T.Optional[int]
    execution_time: float
    timing: T.Optional[T.List[TimingInfo]]
    freshness: T.Optional[Freshness]


@dataclass
class Message:
    level: int
    title: str
    error: str
    message: str
    context: T.Dict
    reporting: T.Optional[Reporting]
