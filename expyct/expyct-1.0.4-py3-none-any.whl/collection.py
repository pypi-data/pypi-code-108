import typing
from collections import Counter

from dataclasses import dataclass

from expyct.base import Equals, MapBefore, Satisfies, Optional, BaseMatcher
from expyct.base import Instance


@dataclass(repr=False, eq=False)
class AllOrAny(BaseMatcher):
    """Mixin for matching a collection object by checking that all or at least
    one of its members are equal to given.

    Like all other `expyct` objects, these can be nested. For example,
    `assert l == exp.AllOrAny(all=exp.Int(min=3))`.
    """

    all: typing.Optional[typing.Any] = None
    any: typing.Optional[typing.Any] = None

    def __init__(
        self,
        all: typing.Optional[typing.Any] = None,
        any: typing.Optional[typing.Any] = None,
    ):
        """Mixin for matching a collection object by checking that all or at least
        one of its members are equal to given.

        Args:
            all : all members of collection must equal
            any : any member of collection must equal
        """
        self.all = all
        self.any = any

    def _eq(self, other):
        if self.all is not None:
            if not all(x == self.all for x in other):
                return False
        if self.any is not None:
            if not any(x == self.any for x in other):
                return False
        return True


@dataclass(repr=False, eq=False)
class Length(BaseMatcher):
    """Mixin for matching a collection object by its length as the result of len()."""

    length: typing.Optional[int] = None
    min_length: typing.Optional[int] = None
    max_length: typing.Optional[int] = None
    non_empty: bool = False

    def __init__(
        self,
        length: typing.Optional[int] = None,
        min_length: typing.Optional[int] = None,
        max_length: typing.Optional[int] = None,
        non_empty: bool = False,
    ):
        """Mixin for matching a collection object by its length as the result of len().

        Args:
        Args:
            length : object length must be exactly
            min_length : object length must be at least
            max_length : object length must be at most
            non_empty : object must have at least one member [default: `False`]
        """
        self.length = length
        self.min_length = min_length
        self.max_length = max_length
        self.non_empty = non_empty

    def _eq(self, other):
        if self.length is not None:
            if not len(other) == self.length:
                return False
        if self.min_length is not None:
            if not len(other) >= self.min_length:
                return False
        if self.max_length is not None:
            if not len(other) <= self.max_length:
                return False
        if self.non_empty:
            if not len(other) > 0:
                return False
        return True


@dataclass(repr=False, eq=False)
class Contains(BaseMatcher):
    """Mixin matching a collection object by the containment of specified members."""

    superset_of: typing.Optional[typing.Collection] = None
    subset_of: typing.Optional[typing.Collection] = None

    def __init__(
        self,
        superset_of: typing.Optional[typing.Collection] = None,
        subset_of: typing.Optional[typing.Collection] = None,
    ):
        """Mixin matching a collection object by the containment of specified members.

        Args:
            superset_of : collection of which the object must be a superset
            subset_of : collection of which the object must be a subset
        """
        self.superset_of = superset_of
        self.subset_of = subset_of

    def _eq(self, other):
        if self.subset_of is not None:
            if isinstance(other, dict) and isinstance(self.subset_of, dict):
                if not all(x in self.subset_of.items() for x in other.items()):
                    return False
            else:
                if not all(x in self.subset_of for x in other):
                    return False

        if self.superset_of is not None:
            if isinstance(other, dict) and isinstance(self.superset_of, dict):
                if not all(x in other.items() for x in self.superset_of.items()):
                    return False
            else:
                if not all(x in other for x in self.superset_of):
                    return False
        return True


@dataclass(repr=False, eq=False)
class Collection(
    Satisfies,
    Contains,
    Length,
    Instance,
    Equals[typing.Collection],
    Optional,
    MapBefore,
    AllOrAny,
    BaseMatcher,
):
    """Match any object that is an instance of `typing.Collection`."""

    def __init__(
        self,
        all: typing.Optional[typing.Any] = None,
        any: typing.Optional[typing.Any] = None,
        map_before: typing.Optional[typing.Callable] = None,
        optional: typing.Optional[bool] = None,
        equals: typing.Optional[typing.Any] = None,
        type: typing.Optional[typing.Type] = None,
        instance_of: typing.Optional[typing.Type] = None,
        length: typing.Optional[int] = None,
        min_length: typing.Optional[int] = None,
        max_length: typing.Optional[int] = None,
        non_empty: bool = False,
        superset_of: typing.Optional[typing.Collection] = None,
        subset_of: typing.Optional[typing.Collection] = None,
        satisfies: typing.Optional[typing.Callable[[typing.Any], bool]] = None,
    ):
        """Match any object that is an instance of `typing.Collection`.

        Args:
            all : all members of collection must equal
            any : any member of collection must equal
            map_before : apply function before checking equality
            optional : whether `None` is allowed
            equals : object must equal exactly. This is useful together with
                `map_before` to check a value after applying a function
            type : type of object must equal to given type
            instance_of : object must be an instance of given type
            length : object length must be exactly
            min_length : object length must be at least
            max_length : object length must be at most
            non_empty : object must have at least one member [default: `False`]
            superset_of : collection of which the object must be a superset
            subset_of : collection of which the object must be a subset
            satisfies : object must satisfy predicate
        """
        self.all = all
        self.any = any
        self.map_before = map_before
        self.optional = optional
        self.equals = equals
        self.type = type
        self.instance_of = instance_of
        self.length = length
        self.min_length = min_length
        self.max_length = max_length
        self.non_empty = non_empty
        self.superset_of = superset_of
        self.subset_of = subset_of
        self.satisfies = satisfies

    def _eq(self, other):
        try:
            other = MapBefore.map(self, other)
        except Exception:
            return False
        if other is None:
            return Optional._eq(self, other)
        if not isinstance(other, typing.Collection):
            return False
        if not Equals._eq(self, other):
            return False
        if not Instance._eq(self, other):
            return False
        if not Length._eq(self, other):
            return False
        if not Contains._eq(self, other):
            return False
        if not Satisfies._eq(self, other):
            return False
        if not AllOrAny._eq(self, other):
            return False
        return True


@dataclass(repr=False, eq=False)
class List(
    Satisfies, Contains, Length, Equals[list], Optional, MapBefore, AllOrAny, BaseMatcher, list
):
    """Match any object that is an instance of `list`."""

    ignore_order: bool = False

    def __new__(cls, *args, **kwargs):
        return list.__new__(cls)

    def __init__(
        self,
        all: typing.Optional[typing.Any] = None,
        any: typing.Optional[typing.Any] = None,
        map_before: typing.Optional[typing.Callable] = None,
        optional: typing.Optional[bool] = None,
        equals: typing.Optional[typing.Any] = None,
        length: typing.Optional[int] = None,
        min_length: typing.Optional[int] = None,
        max_length: typing.Optional[int] = None,
        non_empty: bool = False,
        superset_of: typing.Optional[typing.Collection] = None,
        subset_of: typing.Optional[typing.Collection] = None,
        satisfies: typing.Optional[typing.Callable[[typing.Any], bool]] = None,
        ignore_order: bool = False,
    ):
        """Match any object that is an instance of `list`.

        Args:
            all : all members of collection must equal
            any : any member of collection must equal
            map_before : apply function before checking equality
            optional : whether `None` is allowed
            equals : object must equal exactly. This is useful together with
                `map_before` to check a value after applying a function
            length : object length must be exactly
            min_length : object length must be at least
            max_length : object length must be at most
            non_empty : object must have at least one member [default: `False`]
            superset_of : collection of which the object must be a superset
            subset_of : collection of which the object must be a subset
            satisfies : object must satisfy predicate
            ignore_order : whether to ignore order for `equals`
        """
        self.all = all
        self.any = any
        self.map_before = map_before
        self.optional = optional
        self.equals = equals
        self.length = length
        self.min_length = min_length
        self.max_length = max_length
        self.non_empty = non_empty
        self.superset_of = superset_of
        self.subset_of = subset_of
        self.satisfies = satisfies
        self.ignore_order = ignore_order

    def _eq(self, other):
        try:
            other = MapBefore.map(self, other)
        except Exception:
            return False
        if other is None:
            return Optional._eq(self, other)
        if not isinstance(other, list):
            return False
        if self.ignore_order:
            if not self._equals_ignore_order(self.equals, other):
                return False
        else:
            if not Equals._eq(self, other):
                return False
        if not Length._eq(self, other):
            return False
        if not Contains._eq(self, other):
            return False
        if not Satisfies._eq(self, other):
            return False
        if not AllOrAny._eq(self, other):
            return False
        return True

    @staticmethod
    def _equals_ignore_order(a: typing.List, b: typing.List):
        # https://stackoverflow.com/a/7829249/4443309
        try:
            return Counter(a) == Counter(b)  # O(n)
        except TypeError:
            return len(a) == len(b) and all(a.count(i) == b.count(i) for i in a)  # O(n * n)


@dataclass(repr=False, eq=False)
class Tuple(
    Satisfies, Contains, Length, Equals[tuple], Optional, MapBefore, AllOrAny, BaseMatcher, tuple
):
    """Match any object that is an instance of `tuple`."""

    def __new__(cls, *args, **kwargs):
        return tuple.__new__(cls)

    def __init__(
        self,
        all: typing.Optional[typing.Any] = None,
        any: typing.Optional[typing.Any] = None,
        map_before: typing.Optional[typing.Callable] = None,
        optional: typing.Optional[bool] = None,
        equals: typing.Optional[typing.Any] = None,
        length: typing.Optional[int] = None,
        min_length: typing.Optional[int] = None,
        max_length: typing.Optional[int] = None,
        non_empty: bool = False,
        superset_of: typing.Optional[typing.Collection] = None,
        subset_of: typing.Optional[typing.Collection] = None,
        satisfies: typing.Optional[typing.Callable[[typing.Any], bool]] = None,
    ):
        """Match any object that is an instance of `tuple`.

        Args:
            all : all members of collection must equal
            any : any member of collection must equal
            map_before : apply function before checking equality
            optional : whether `None` is allowed
            equals : object must equal exactly. This is useful together with
                `map_before` to check a value after applying a function
            type : type of object must equal to given type
            instance_of : object must be an instance of given type
            length : object length must be exactly
            min_length : object length must be at least
            max_length : object length must be at most
            non_empty : object must have at least one member [default: `False`]
            superset_of : collection of which the object must be a superset
            subset_of : collection of which the object must be a subset
            satisfies : object must satisfy predicate
        """
        self.all = all
        self.any = any
        self.map_before = map_before
        self.optional = optional
        self.equals = equals
        self.length = length
        self.min_length = min_length
        self.max_length = max_length
        self.non_empty = non_empty
        self.superset_of = superset_of
        self.subset_of = subset_of
        self.satisfies = satisfies

    def _eq(self, other):
        try:
            other = MapBefore.map(self, other)
        except Exception:
            return False
        if other is None:
            return Optional._eq(self, other)
        if not isinstance(other, tuple):
            return False
        if not Equals._eq(self, other):
            return False
        if not Length._eq(self, other):
            return False
        if not Contains._eq(self, other):
            return False
        if not Satisfies._eq(self, other):
            return False
        if not AllOrAny._eq(self, other):
            return False
        return True


@dataclass(repr=False, eq=False)
class Set(
    Satisfies, Contains, Length, Equals[set], Optional, MapBefore, AllOrAny, BaseMatcher, set
):
    """Match any object that is an instance of `set`."""

    def __new__(cls, *args, **kwargs):
        return set.__new__(cls)

    def __init__(
        self,
        all: typing.Optional[typing.Any] = None,
        any: typing.Optional[typing.Any] = None,
        map_before: typing.Optional[typing.Callable] = None,
        optional: typing.Optional[bool] = None,
        equals: typing.Optional[typing.Any] = None,
        length: typing.Optional[int] = None,
        min_length: typing.Optional[int] = None,
        max_length: typing.Optional[int] = None,
        non_empty: bool = False,
        superset_of: typing.Optional[typing.Collection] = None,
        subset_of: typing.Optional[typing.Collection] = None,
        satisfies: typing.Optional[typing.Callable[[typing.Any], bool]] = None,
    ):
        """Match any object that is an instance of `set`.

        Args:
            all : all members of collection must equal
            any : any member of collection must equal
            map_before : apply function before checking equality
            optional : whether `None` is allowed
            equals : object must equal exactly. This is useful together with
                `map_before` to check a value after applying a function
            type : type of object must equal to given type
            instance_of : object must be an instance of given type
            length : object length must be exactly
            min_length : object length must be at least
            max_length : object length must be at most
            non_empty : object must have at least one member [default: `False`]
            superset_of : collection of which the object must be a superset
            subset_of : collection of which the object must be a subset
            satisfies : object must satisfy predicate
        """
        self.all = all
        self.any = any
        self.map_before = map_before
        self.optional = optional
        self.equals = equals
        self.length = length
        self.min_length = min_length
        self.max_length = max_length
        self.non_empty = non_empty
        self.superset_of = superset_of
        self.subset_of = subset_of
        self.satisfies = satisfies

    def _eq(self, other):
        try:
            other = MapBefore.map(self, other)
        except Exception:
            return False
        if other is None:
            return Optional._eq(self, other)
        if not isinstance(other, set):
            return False
        if not Equals._eq(self, other):
            return False
        if not Length._eq(self, other):
            return False
        if not Contains._eq(self, other):
            return False
        if not Satisfies._eq(self, other):
            return False
        if not AllOrAny._eq(self, other):
            return False
        return True


@dataclass(repr=False, eq=False)
class Dict(Satisfies, Contains, Length, Equals[dict], Optional, MapBefore, BaseMatcher, dict):
    """Match any object that is an instance of `dict`."""

    superset_of: typing.Optional[dict] = None
    subset_of: typing.Optional[dict] = None
    keys: typing.Optional[typing.Set] = None  # type: ignore
    values: typing.Optional[typing.List] = None  # type: ignore
    keys_all: typing.Optional[typing.Any] = None
    keys_any: typing.Optional[typing.Any] = None
    values_all: typing.Optional[typing.Any] = None
    values_any: typing.Optional[typing.Any] = None

    def __new__(cls, *args, **kwargs):
        return dict.__new__(cls)

    def __init__(
        self,
        map_before: typing.Optional[typing.Callable] = None,
        optional: typing.Optional[bool] = None,
        equals: typing.Optional[typing.Any] = None,
        length: typing.Optional[int] = None,
        min_length: typing.Optional[int] = None,
        max_length: typing.Optional[int] = None,
        non_empty: bool = False,
        superset_of: typing.Optional[dict] = None,
        subset_of: typing.Optional[dict] = None,
        satisfies: typing.Optional[typing.Callable[[typing.Any], bool]] = None,
        keys: typing.Optional[typing.Set] = None,
        values: typing.Optional[typing.List] = None,
        keys_all: typing.Optional[typing.Any] = None,
        keys_any: typing.Optional[typing.Any] = None,
        values_all: typing.Optional[typing.Any] = None,
        values_any: typing.Optional[typing.Any] = None,
    ):
        """Match any object that is an instance of `dict`.

        Args:
            map_before : apply function before checking equality
            optional : whether `None` is allowed
            equals : object must equal exactly. This is useful together with
                `map_before` to check a value after applying a function
            length : object length must be exactly
            min_length : object length must be at least
            max_length : object length must be at most
            non_empty : object must have at least one member [default: `False`]
            superset_of : collection of which the object must be a superset
            subset_of : collection of which the object must be a subset
            satisfies : object must satisfy predicate
            keys : dict keys must equal
            values : dict values must equal
            keys_all : all dict keys must equal
            keys_any : any dict key must equal
            values_all : all dict values must equal
            values_any : any dict value must equal
        """
        self.all = all
        self.any = any
        self.map_before = map_before
        self.optional = optional
        self.equals = equals
        self.length = length
        self.min_length = min_length
        self.max_length = max_length
        self.non_empty = non_empty
        self.superset_of = superset_of
        self.subset_of = subset_of
        self.satisfies = satisfies
        self.keys = keys
        self.values = values
        self.keys_all = keys_all
        self.keys_any = keys_any
        self.values_all = values_all
        self.values_any = values_any

    def _eq(self, other):
        try:
            other = MapBefore.map(self, other)
        except Exception:
            return False
        if other is None:
            return Optional._eq(self, other)
        if not isinstance(other, dict):
            return False
        if not Equals._eq(self, other):
            return False
        if not Length._eq(self, other):
            return False
        if self.keys is not None:
            if not other.keys() == self.keys:
                return False
        if self.values is not None:
            if not other.values() == self.values:
                return False
        if not Contains._eq(self, other):
            return False
        if not Satisfies._eq(self, other):
            return False
        if self.keys_all is not None:
            if not all(x == self.keys_all for x in other.keys()):
                return False
        if self.keys_any is not None:
            if not any(x == self.keys_any for x in other.keys()):
                return False
        if self.values_all is not None:
            if not all(x == self.values_all for x in other.values()):
                return False
        if self.values_any is not None:
            if not any(x == self.values_any for x in other.values()):
                return False
        return True
