__all__ = ["Accumulator", "Accuracy"]


class Accumulator:
    def __init__(self) -> None:
        self._cumsum: float = 0.0
        self._length: int = 0

    def update(self, value: float, length: int = 1) -> None:
        self._cumsum += float(value)
        self._length += int(length)

    @property
    def mean(self) -> float:
        if self._length > 0:
            return self._cumsum / self._length
        else:
            return 0.0

    @property
    def total(self) -> float:
        return self._cumsum

    @property
    def length(self) -> int:
        return self._length


class Accuracy:
    def __init__(self) -> None:
        self._cumsum: float = 0.0
        self._length: int = 0

    def update(self, preds, labels) -> None:
        assert len(preds) == len(
            labels), "The list of predictions and the list of labels must have same length"
        self._cumsum += float((preds == labels).sum())
        self._length += len(labels)

    @property
    def value(self) -> float:
        if self._length > 0:
            return float(self._cumsum / self._length)
        else:
            return 0.0
