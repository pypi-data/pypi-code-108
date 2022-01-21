from collections import namedtuple
from contextvars import ContextVar

TimingValue = namedtuple("TimingValue", ["count", "cost"])


class SqlalchemyConnectionTiming:
    def __init__(self) -> None:
        self._context = ContextVar(
            self.__class__.__name__,
            default=TimingValue(0, 0.0),
        )

    @property
    def value(self) -> TimingValue:
        return self._context.get()

    def increase_count(self, n: int = 1):
        count, cost = self.value
        self._context.set(TimingValue(count + n, cost))

    def increase_cost(self, t: float):
        count, cost = self.value
        self._context.set(TimingValue(count, cost + t))

    def reset(self):
        self._context.set(TimingValue(0, 0.0))
