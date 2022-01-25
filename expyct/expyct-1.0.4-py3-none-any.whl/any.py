import inspect
import typing

from dataclasses import dataclass

from expyct.base import MapBefore, Satisfies, Instance, Type, Equals, Vars, Optional, BaseMatcher


@dataclass(repr=False, eq=False)
class Any(Instance, Satisfies, Vars, Equals[typing.Any], Optional, MapBefore, BaseMatcher):
    """Match any object."""

    def __init__(
        self,
        map_before: typing.Optional[typing.Callable] = None,
        optional: typing.Optional[bool] = None,
        equals: typing.Optional[typing.Any] = None,
        vars: typing.Optional[typing.Any] = None,
        satisfies: typing.Optional[typing.Callable[[typing.Any], bool]] = None,
        type: typing.Optional[typing.Type] = None,
        instance_of: typing.Optional[typing.Type] = None,
    ):
        """Match any object.

        Args:
            map_before : apply function before checking equality
            optional : whether `None` is allowed [default: `False`]
            equals : object must equal exactly. This is useful together with
                `map_before` to check a value after applying a function
            vars : object attributes (result of `vars()`) must equal
            satisfies : object must satisfy predicate
            type : type of object must equal to given type
            instance_of : object must be an instance of given type
        """
        self.map_before = map_before
        self.optional = optional
        self.equals = equals
        self.vars = vars
        self.satisfies = satisfies
        self.type = type
        self.instance_of = instance_of

    def _eq(self, other):
        try:
            other = MapBefore.map(self, other)
        except Exception:
            return False
        if other is None:
            return Optional._eq(self, other)
        if not Equals._eq(self, other):
            return False
        if not Vars._eq(self, other):
            return False
        if not Satisfies._eq(self, other):
            return False
        if not Instance._eq(self, other):
            return False
        return True


@dataclass(repr=False, eq=False)
class AnyValue(
    Instance,
    Satisfies,
    Vars,
    Equals[typing.Any],
    Optional,
    MapBefore,
    BaseMatcher,
):
    """Match any value."""

    def __init__(
        self,
        map_before: typing.Optional[typing.Callable] = None,
        optional: typing.Optional[bool] = None,
        equals: typing.Optional[typing.Any] = None,
        vars: typing.Optional[typing.Any] = None,
        satisfies: typing.Optional[typing.Callable[[typing.Any], bool]] = None,
        type: typing.Optional[typing.Type] = None,
        instance_of: typing.Optional[typing.Type] = None,
    ):
        """Match any value.

        Args:
            map_before : apply function before checking equality
            optional : whether `None` is allowed [default: `False`]
            equals : object must equal exactly. This is useful together with
                `map_before` to check a value after applying a function
            vars : object attributes (result of `vars()`) must equal
            satisfies : object must satisfy predicate
            type : type of object must equal to given type
            instance_of : object must be an instance of given type
        """
        self.map_before = map_before
        self.optional = optional
        self.equals = equals
        self.vars = vars
        self.satisfies = satisfies
        self.type = type
        self.instance_of = instance_of

    def _eq(self, other):
        try:
            other = MapBefore.map(self, other)
        except Exception:
            return False
        # TODO check
        if (
            inspect.ismodule(other)
            or inspect.isclass(other)
            or inspect.isfunction(other)
            or inspect.ismethod(other)
        ):
            return False
        if other is None:
            return Optional._eq(self, other)
        if not Equals._eq(self, other):
            return False
        if not Vars._eq(self, other):
            return False
        if not Satisfies._eq(self, other):
            return False
        if not Instance._eq(self, other):
            return False
        return True


@dataclass(repr=False, eq=False)
class AnyType(Type, Satisfies, Vars, Equals[typing.Any], Optional, MapBefore, BaseMatcher):
    """Match any class."""

    def __init__(
        self,
        map_before: typing.Optional[typing.Callable] = None,
        optional: typing.Optional[bool] = None,
        equals: typing.Optional[typing.Any] = None,
        vars: typing.Optional[typing.Any] = None,
        satisfies: typing.Optional[typing.Callable[[typing.Any], bool]] = None,
        superclass_of: typing.Optional[typing.Type] = None,
        subclass_of: typing.Optional[typing.Type] = None,
    ):
        """Match any class.

        Args:
            map_before : apply function before checking equality
            optional : whether `None` is allowed [default: `False`]
            equals : object must equal exactly. This is useful together with
                `map_before` to check a value after applying a function
            vars : object attributes (result of `vars()`) must equal
            satisfies : object must satisfy predicate
            superclass_of : class must be superclass of given type
            subclass_of : class must be subclass of given type
        """
        self.map_before = map_before
        self.optional = optional
        self.equals = equals
        self.vars = vars
        self.satisfies = satisfies
        self.superclass_of = superclass_of
        self.subclass_of = subclass_of

    def _eq(self, other):
        try:
            other = MapBefore.map(self, other)
        except Exception:
            return False
        if other is None:
            return Optional._eq(self, other)
        if not Equals._eq(self, other):
            return False
        if not Vars._eq(self, other):
            return False
        if not Satisfies._eq(self, other):
            return False
        if not Type._eq(self, other):
            return False
        return True


#: Literally anything
ANY = Any()
#: Any value
ANY_VALUE = AnyValue()
#: Any type (i.e. class)
ANY_TYPE = AnyType()
