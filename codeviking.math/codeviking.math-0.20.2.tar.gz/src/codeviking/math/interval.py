from typing import NamedTuple, Tuple, Union

RICompat = Union['RI', Tuple[float, float]]


class RI(NamedTuple):
    """
    float Interval

    .. py:method:: __new__

    .. py:attribute:: min

        lower bound.

    .. py:attribute:: max

        upper bound.

    .. describe:: x in interval

        Determine if x lies inside interval: min <= x <= max
    """
    min: float
    max: float

    @property
    def length(self) -> float:
        """        length of this interval"""
        return self.max - self.min

    def __contains__(self, v: float) -> bool:
        return self.min <= v <= self.max

    def expand(self, item: Union['RI', Tuple[float, float], float]) -> 'RI':
        """
        return a RI that contains both this interval and item.

        :param item: can be either a RI, a tuple of length 2, or a float
        """
        if isinstance(item, RI):
            return RI(min(self.min, item.min), max(self.max, item.max))
        if isinstance(item, tuple):
            return RI(min(self.min, item[0]), max(self.max, item[1]))

        if item in self:
            return self
        if self.is_empty:
            return RI(item, item)
        return RI(min(self.min, item), max(self.max, item))

    @property
    def is_empty(self) -> bool:
        """
        return True if this interval is empty.
        """
        return self.min > self.max

    @property
    def is_all(self) -> bool:
        """True if this interval is the entire real line."""
        return self.min == float('-inf') and self.max == float('inf')

    @property
    def is_point(self) -> bool:
        """True if this interval is a single point."""
        return self.max == self.min

    def intersects(self, other: RICompat) -> bool:
        """
        Return True if self and other intersects.
        """
        if not isinstance(other, RI):
            other = RI(*other)
        # empty intervals never intersect with anything.
        if self.is_empty or other.is_empty:
            return False
        # handle the special case when the intervals are the same
        if self == other:
            return True
        r = [(self.min, 0), (self.max, 0), (other.min, 1), (other.max, 1)]
        r.sort()

        # check if the first two values are from different intervals,
        return r[0][1] != r[1][1]

    def intersection(self, other: RICompat) -> 'RI':
        """
        Compute the intersection of self and other.
        """
        if not isinstance(other, RI):
            other = RI(*other)
        if not self.intersects(other):
            return self.__class__.empty
        return RI(max(self.min, other.min), min(self.max, other.max))

    def alpha(self, value: float) -> float:
        return (value - self.min) / self.length

    def interpolate(self, alpha: float) -> float:
        return self.min + alpha * self.length

    def constrain(self, value: float) -> float:
        return max(self.min, min(self.max, value))

    def __eq__(self, other: RICompat) -> bool:
        if not self.is_empty:
            return self.min == other[0] and self.max == other[1]
        return other[0] >= other[1]


RI.empty = RI(float("inf"), float("-inf"))
