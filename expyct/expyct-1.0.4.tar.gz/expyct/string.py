import re
import typing

from dataclasses import dataclass

from expyct.base import Equals, MapBefore, Instance, Satisfies, Optional, BaseMatcher
from expyct.collection import Length, Contains


@dataclass(repr=False, eq=False)
class String(
    Contains,
    Length,
    Satisfies,
    Equals[str],
    Instance,
    Optional,
    MapBefore,
    BaseMatcher,
    str,
):
    """Match any object that is a string."""

    starts_with: typing.Optional[str] = None
    ends_with: typing.Optional[str] = None
    regex: typing.Optional[typing.Union[str, bytes, typing.Pattern]] = None
    ignore_case: bool = False

    def __new__(cls, *args, **kwargs):
        return str.__new__(cls)

    def __init__(
        self,
        map_before: typing.Optional[typing.Callable] = None,
        optional: typing.Optional[bool] = None,
        type: typing.Optional[typing.Type] = None,
        instance_of: typing.Optional[typing.Type] = None,
        equals: typing.Optional[typing.Any] = None,
        satisfies: typing.Optional[typing.Callable[[typing.Any], bool]] = None,
        length: typing.Optional[int] = None,
        min_length: typing.Optional[int] = None,
        max_length: typing.Optional[int] = None,
        non_empty: bool = False,
        superset_of: typing.Optional[typing.Collection] = None,
        subset_of: typing.Optional[typing.Collection] = None,
        starts_with: typing.Optional[str] = None,
        ends_with: typing.Optional[str] = None,
        regex: typing.Optional[typing.Union[str, bytes, typing.Pattern]] = None,
        ignore_case: bool = False,
    ):
        """Match any object that is a string.

        Args:
            map_before : apply function before checking equality
            optional : whether `None` is allowed [default: `False`]
            type : type of object must equal to given type
            instance_of : object must be an instance of given type
            equals : object must equal exactly. This is useful together with
              `map_before` to check a value after applying a function
            satisfies : object must satisfy predicate
            length : object length must be exactly
            min_length : object length must be at least
            max_length : object length must be at most
            non_empty : object must have at least one member [default: `False`]
            superset_of : collection of which the object must be a superset
            subset_of : collection of which the object must be a subset
            starts_with : string must start with given
            ends_with : string must end with given
            regex : string must fully match predicate
            ignore_case : whether to ignore case for starts_with, ends_with,
            equality and regex matching [default: `False`]
        """
        self.map_before = map_before
        self.optional = optional
        self.type = type
        self.instance_of = instance_of
        self.equals = equals
        self.satisfies = satisfies
        self.length = length
        self.min_length = min_length
        self.max_length = max_length
        self.non_empty = non_empty
        self.superset_of = superset_of
        self.subset_of = subset_of
        self.starts_with = starts_with
        self.ends_with = ends_with
        self.regex = regex
        self.ignore_case = ignore_case

    def _eq(self, other):
        try:
            other = MapBefore.map(self, other)
        except Exception:
            return False
        if other is None:
            return Optional._eq(self, other)
        if self.ignore_case:
            other = other.lower()
            if self.equals is not None:
                self.equals = self.equals.lower()
            if self.starts_with is not None:
                self.starts_with = self.starts_with.lower()
            if self.ends_with is not None:
                self.ends_with = self.ends_with.lower()
        if not isinstance(other, (str, bytes)):
            return False
        if not Instance._eq(self, other):
            return False
        if not Equals._eq(self, other):
            return False
        if not Length._eq(self, other):
            return False
        if not Contains._eq(self, other):
            return False
        if not Satisfies._eq(self, other):
            return False
        if self.starts_with is not None:
            if not other.startswith(self.starts_with):
                return False
        if self.ends_with is not None:
            if not other.endswith(self.ends_with):
                return False
        if self.regex:
            if isinstance(self.regex, (str, bytes)) and not re.fullmatch(
                self.regex, str(other), self.flags()
            ):
                return False
            if isinstance(self.regex, typing.Pattern) and not self.regex.fullmatch(other):
                return False
        return True

    def flags(self):
        flags = 0
        if self.ignore_case:
            flags |= re.IGNORECASE
        return flags


#: Any string in the form of a UUID
ANY_UUID = String(
    regex=re.compile("[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89aAbB][a-f0-9]{3}-[a-f0-9]{12}")
)
