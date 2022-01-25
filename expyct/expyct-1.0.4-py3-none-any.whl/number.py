import typing
from numbers import Number as ParentNumber

from dataclasses import dataclass

from expyct.base import MapBefore, Satisfies, Equals, Instance, Optional, BaseMatcher


@dataclass(repr=False, eq=False)
class MinMax(BaseMatcher):
    """Mixin for matching a number that is equal to, larger or smaller than given bounds."""

    min: typing.Optional[ParentNumber] = None
    max: typing.Optional[ParentNumber] = None

    def __init__(
        self,
        min: typing.Optional[ParentNumber] = None,
        max: typing.Optional[ParentNumber] = None,
    ):
        """Mixin for matching a number that is equal to, larger or smaller than given bounds.

        Args:
            min : number must be larger than or equal to given
            max : number must be smaller than or equal to given
        """
        self.min = min
        self.max = max

    def _eq(self, other):
        if self.min is not None and not other >= self.min:
            return False
        if self.max is not None and not other <= self.max:
            return False
        return True


@dataclass(repr=False, eq=False)
class MinMaxStrict(BaseMatcher):
    """Mixin for matching number that is strictly larger or smaller than given bounds."""

    min_strict: typing.Optional[ParentNumber] = None
    max_strict: typing.Optional[ParentNumber] = None

    def __init__(
        self,
        min_strict: typing.Optional[ParentNumber] = None,
        max_strict: typing.Optional[ParentNumber] = None,
    ):
        """Mixin for matching number that is strictly larger or smaller than given bounds.

        Args:
            min_strict : number must be larger than given
            max_strict : number must be smaller than given
        """
        self.min_strict = min_strict
        self.max_strict = max_strict

    def _eq(self, other):
        if self.min_strict is not None and not other > self.min_strict:
            return False
        if self.max_strict is not None and not other < self.max_strict:
            return False
        return True


@dataclass(repr=False, eq=False)
class CloseTo(BaseMatcher):
    """Mixin for matching number that is close to given target within a certain two-side error. In
    other words, the difference between the number and `close_to` must be at most `error`."""

    close_to: typing.Optional[ParentNumber] = None
    error: float = 0.001

    def __init__(
        self,
        close_to: typing.Optional[ParentNumber] = None,
        error: float = 0.001,
    ):
        """Mixin for matching number that is close to given target within a certain two-side error. In
        other words, the difference between the number and `close_to` must be at most `error`.

        Args:
            close_to : number must be close to this
            error : two-sided allowed error
        """
        self.close_to = close_to
        self.error = error

    def _eq(self, other):
        if self.close_to is not None:
            d = self.error * self.close_to
            if not self.close_to - d <= other <= self.close_to + d:
                return False
        return True


@dataclass(repr=False, eq=False)
class Number(
    CloseTo,
    MinMaxStrict,
    MinMax,
    Satisfies,
    Equals[ParentNumber],
    Instance,
    Optional,
    MapBefore,
    BaseMatcher,
):
    """Match any number."""

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(
        self,
        map_before: typing.Optional[typing.Callable] = None,
        type: typing.Optional[typing.Type] = None,
        instance_of: typing.Optional[typing.Type] = None,
        equals: typing.Optional[typing.Any] = None,
        optional: typing.Optional[bool] = None,
        satisfies: typing.Optional[typing.Callable[[typing.Any], bool]] = None,
        min: typing.Optional[ParentNumber] = None,
        max: typing.Optional[ParentNumber] = None,
        min_strict: typing.Optional[ParentNumber] = None,
        max_strict: typing.Optional[ParentNumber] = None,
        close_to: typing.Optional[ParentNumber] = None,
        error: float = 0.01,
    ):
        """Match any number.

        Args:
            map_before : apply function before checking equality
            type : type of object must equal to given type
            instance_of : object must be an instance of given type
            equals : object must equal exactly. This is useful together with
                `map_before` to check a value after applying a function
            optional : whether `None` is allowed [default: `False`]
            satisfies : object must satisfy predicate
            min : number must be larger than or equal to given
            max : number must be smaller than or equal to given
            min_strict : number must be larger than given
            max_strict : number must be smaller than given
            close_to : number must be close to this
            error : two-sided allowed error a
        """
        self.map_before = map_before
        self.type = type
        self.instance_of = instance_of
        self.equals = equals
        self.optional = optional
        self.satisfies = satisfies
        self.min = min
        self.max = max
        self.min_strict = min_strict
        self.max_strict = max_strict
        self.close_to = close_to
        self.error = error

    def _eq(self, other):
        try:
            other = MapBefore.map(self, other)
        except Exception:
            return False
        if other is None:
            return Optional._eq(self, other)
        if not isinstance(other, ParentNumber):
            return False
        if not Instance._eq(self, other):
            return False
        if not Equals._eq(self, other):
            return False
        if not Satisfies._eq(self, other):
            return False
        if not MinMax._eq(self, other):
            return False
        if not MinMaxStrict._eq(self, other):
            return False
        if not CloseTo._eq(self, other):
            return False
        return True


@dataclass(repr=False, eq=False)
class Int(Number, BaseMatcher, int):
    """Match any object that is an instance of `int`."""

    def __new__(cls, *args, **kwargs):
        return int.__new__(cls)

    def __init__(
        self,
        map_before: typing.Optional[typing.Callable] = None,
        type: typing.Optional[typing.Type] = None,
        instance_of: typing.Optional[typing.Type] = None,
        equals: typing.Optional[typing.Any] = None,
        optional: typing.Optional[bool] = None,
        satisfies: typing.Optional[typing.Callable[[typing.Any], bool]] = None,
        min: typing.Optional[ParentNumber] = None,
        max: typing.Optional[ParentNumber] = None,
        min_strict: typing.Optional[ParentNumber] = None,
        max_strict: typing.Optional[ParentNumber] = None,
        close_to: typing.Optional[ParentNumber] = None,
        error: float = 0.01,
    ):
        """Match any object that is an instance of `int`.

        Args:
            map_before : apply function before checking equality
            type : type of object must equal to given type
            instance_of : object must be an instance of given type
            equals : object must equal exactly. This is useful together with
                `map_before` to check a value after applying a function
            optional : whether `None` is allowed
            satisfies : object must satisfy predicate
            min : number must be larger than or equal to given
            max : number must be smaller than or equal to given
            min_strict : number must be larger than given
            max_strict : number must be smaller than given
            close_to : number must be close to this
            error : two-sided allowed error a
        """
        self.map_before = map_before
        self.type = type
        self.instance_of = instance_of
        self.equals = equals
        self.optional = optional
        self.satisfies = satisfies
        self.min = min
        self.max = max
        self.min_strict = min_strict
        self.max_strict = max_strict
        self.close_to = close_to
        self.error = error

    def _eq(self, other):
        if not isinstance(other, int):
            return False
        if not Number._eq(self, other):
            return False
        return True


@dataclass(repr=False, eq=False)
class Float(Number, BaseMatcher, float):
    """Match any object that is an instance of `float`."""

    def __new__(cls, *args, **kwargs):
        return float.__new__(cls)

    def __init__(
        self,
        map_before: typing.Optional[typing.Callable] = None,
        type: typing.Optional[typing.Type] = None,
        instance_of: typing.Optional[typing.Type] = None,
        equals: typing.Optional[typing.Any] = None,
        optional: typing.Optional[bool] = None,
        satisfies: typing.Optional[typing.Callable[[typing.Any], bool]] = None,
        min: typing.Optional[ParentNumber] = None,
        max: typing.Optional[ParentNumber] = None,
        min_strict: typing.Optional[ParentNumber] = None,
        max_strict: typing.Optional[ParentNumber] = None,
        close_to: typing.Optional[ParentNumber] = None,
        error: float = 0.01,
    ):
        """Match any object that is an instance of `float`.

        Args:
            map_before : apply function before checking equality
            type : type of object must equal to given type
            instance_of : object must be an instance of given type
            equals : object must equal exactly. This is useful together with
                `map_before` to check a value after applying a function
            optional : whether `None` is allowed
            satisfies : object must satisfy predicate
            min : number must be larger than or equal to given
            max : number must be smaller than or equal to given
            min_strict : number must be larger than given
            max_strict : number must be smaller than given
            close_to : number must be close to this
            error : two-sided allowed error
        """
        self.map_before = map_before
        self.type = type
        self.instance_of = instance_of
        self.equals = equals
        self.optional = optional
        self.satisfies = satisfies
        self.min = min
        self.max = max
        self.min_strict = min_strict
        self.max_strict = max_strict
        self.close_to = close_to
        self.error = error

    def _eq(self, other):
        if not isinstance(other, float):
            return False
        if not Number._eq(self, other):
            return False
        return True


def parse_number_string(obj: str) -> typing.Union[int, float]:
    """Parse a string as number. First tries to parse as `int`, then as `float`. Throws a ValueError
    if `obj` is not a string.

    Args:
        obj : the string to parse
    """
    if not isinstance(obj, str):
        raise ValueError()
    try:
        return int(obj)
    except ValueError:
        return float(obj)


def parse_int_string(obj: str) -> int:
    """Parse a string as `int`. Throws a ValueError if `obj` is not a string.

    Args:
        obj : the string to parse
    """
    if not isinstance(obj, str):
        raise ValueError()
    return int(obj)


def parse_float_string(obj: str) -> float:
    """Parse a string as `float`. Throws a ValueError if `obj` is not a string.

    Args:
        obj : the string to parse
    """
    if not isinstance(obj, str):
        raise ValueError()
    return float(obj)


#: Any number
ANY_NUMBER = Number()
#: Any instance of `int`
ANY_INT = Int()
#: Any instance of `float`
ANY_FLOAT = Float()

#: Any number, parsed from a string
ANY_NUMBER_STRING = Number(map_before=parse_number_string)
#: Any instance of `int`
ANY_INT_STRING = Int(map_before=parse_int_string)
#: Any instance of `float`
ANY_FLOAT_STRING = Float(map_before=parse_float_string)
