import inspect
import warnings
from dataclasses import dataclass
from functools import partial, partialmethod
import sys
from typing import Any, Dict, Set, Callable, Optional, Iterable, Tuple

# noinspection PyProtectedMember
from pandas._libs.properties import AxisProperty, CachedProperty

from . import call_pandas_function


# WARNING: `sys.gettrace` is considered a CPython implementation detail, so we check that it's available.
# See [documentation](https://docs.python.org/3.8/library/sys.html?highlight=gettrace#sys.gettrace).
# CTRacer is excluded because it is not a debugger but a code coverage tool.
_process_is_being_debugged: bool = (
    hasattr(sys, "gettrace")
    and sys.gettrace() is not None
    and sys.gettrace().__class__.__name__ != "CTracer"
)


class PandasDisplay:
    min_rows: int = 5
    max_rows: int = 20
    min_cols: int = 5
    max_cols: int = 20


class ClassMethod(type):
    """Only to be used for stuff that can't be done directly on yhe class"""

    _class_name: str
    _pandas_class: Any
    _additional_class_methods: Set[str] = {"from_pandas"}

    @classmethod
    def _attr_if_exists(cls, item: str):
        return getattr(cls._pandas_class, item, None)

    def __getattr__(cls, key: str) -> Callable:
        call = partial(call_pandas_function, cls._class_name, None, key)
        if key in cls._additional_class_methods or cls._attr_if_exists(key) is not None:
            return call
        raise AttributeError(f"type object '{cls._pandas_class.__name__}' has no attribute {key!r}")

    def __dir__(cls) -> Iterable[str]:
        return list(cls._additional_class_methods) + list(dir(cls._pandas_class))


class Struct(metaclass=ClassMethod):
    _pandas_class_instance: Any = None
    _additional_methods: Set[str] = {
        "to_pandas",
        "load",
        "save",
    }  # put in the mcs to get in the dir?
    _args_to_replace: Dict[str, Tuple[int, Callable]] = {}
    _accessors: Set[str] = set()  # put in the mcs to get in the dir?
    _indexers = {"iat", "at", "loc", "iloc"}  # put in the mcs to get in the dir?

    @classmethod
    def _is_property(cls, item: str) -> bool:
        property_ = cls._attr_if_exists(item)
        return isinstance(property_, (property, AxisProperty, CachedProperty))  # works for None too

    @classmethod
    def _is_method(cls, item: str) -> bool:
        method = cls._attr_if_exists(item)
        return callable(method)  # works for None too

    @classmethod
    def _call(cls, accessor, func_name, *args, **kwargs):
        return call_pandas_function(cls._class_name, accessor, func_name, *args, **kwargs)

    def _call_method(self, accessor: Optional[str], func_name: str, *args, **kwargs):
        if func_name in self._args_to_replace:
            arg_num, callable_ = self._args_to_replace[func_name]
            args = tuple(
                list(args[:arg_num]) + [callable_(args[arg_num])] + list(args[arg_num + 1 :])
            )
        return self._call(accessor, func_name, self, *args, **kwargs)

    def _on_missing_attribute(self, item: str):
        raise AttributeError(f"'{type(self)}' has no attribute {item!r}")

    ###################################################################################################################
    # Creation/upgrade

    @classmethod
    def _new(cls, id_: str, cached_attributes=None):
        # Workaround to avoid being intercepted
        struct = object.__new__(cls)
        struct._id = id_  # pylint: disable=attribute-defined-outside-init
        struct._cached_attributes = (  # pylint: disable=attribute-defined-outside-init
            {} if cached_attributes is None else cached_attributes
        )
        return struct

    def _mutate(self, other: "Struct") -> None:
        self._id = other._id  # type: ignore  # pylint: disable=attribute-defined-outside-init
        self._cached_attributes = (  # pylint: disable=attribute-defined-outside-init
            other._cached_attributes  # type: ignore
        )

    def getdoc(self):
        """
        Avoid server error "missing attribute getdoc" when tried by IPython.core.oinspect.getdoc
        """

        return inspect.getdoc(self)

    ###################################################################################################################
    # Magic methods

    def __new__(cls, *args, **kwargs):
        return cls._call(None, "__init__", *args, **kwargs)

    def __getattr__(self, item: str):  # pylint: disable=too-many-return-statements
        """Intercepting all not-magic methods"""
        if item.startswith("_") and item not in ("_repr_html_"):
            # _repr_html_ is a supported API call that returns an HTML representation of the struct.
            # All other IPython representation methods (such as _repr_svg or _ipython_display_) are currently
            # not supported and should raise an AttributeError client-side.
            # This will cause IPython to default to a supported representation, without needless requests to
            # the Terality API.
            return object.__getattribute__(self, item)
        if item in self._cached_attributes:  # type: ignore
            return self._cached_attributes[item]  # type: ignore
        if item in self._accessors:
            return NameSpace(self, item)
        if item in self._indexers:
            return Indexer(self, item)
        if item in self._additional_methods:
            return partial(self._call_method, None, item)
        if self._is_property(item):
            return self._call_method(None, item)
        if self._is_method(item):
            return partial(self._call_method, None, item)
        return self._on_missing_attribute(item)

    def __setattr__(self, name, value):  # pylint: disable=inconsistent-return-statements
        if name.startswith("_"):
            object.__setattr__(self, name, value)
        else:
            return self._call_method("__setattr__", name, value=value)

    def __str__(self):
        # NOTE: When debugging, we avoid network calls and fall back to a bare bones representation.
        if _process_is_being_debugged:
            _id = getattr(self, "_id", None)
            return f"terality.{self.__class__.__name__}(_id={_id})"
        return self._call_method(None, "__str__")

    def __repr__(self):
        return self.__str__()

    def __dir__(self) -> Iterable[str]:
        # WARNING: When the process is being debugged, we do not want to list any dynamic properties.
        # Why? Because the debugger's variable view uses `dir` to list a variable's children, then evaluates them.
        # Listing dynamic properties would cause spurious calls to the server.
        if _process_is_being_debugged:
            members = [
                key
                for key in self.__dict__.keys() | type(self).__dict__.keys()
                if key.startswith("_") and not key.startswith("__")
            ]
            return members

        members = list(self._additional_methods)
        if self._pandas_class_instance is not None:
            members += list(dir(self._pandas_class_instance))
        return members

    def __len__(self):
        return self._call_method(None, "__len__")


# Add magic methods (otherwise they won't be itercepted) programmatically rather than by hand
# ------------------------------


def _forward_to_backend(lhs: Struct, func_name: str, *args, **kwargs):
    return lhs._call_method(None, func_name, *args, **kwargs)


def _set_magics(magic_method_names):
    for magic_method_name in magic_method_names:
        full_magic_method_name = f"__{magic_method_name}__"
        operator = partialmethod(_forward_to_backend, full_magic_method_name)
        setattr(Struct, full_magic_method_name, operator)


_access = ["getitem", "setitem", "delitem"]
_comparisons = ["lt", "le", "eq", "ne", "ge", "gt"]
_others = ["neg", "pos", "invert", "abs", "len"]

_arithmetic = [
    "add",
    "sub",
    "mul",
    "matmul",
    "truediv",
    "floordiv",
    "mod",
    "divmod",
    "pow",
]
_boolean = [
    "and",
    "xor",
    "or",
]
_other = [
    "lshift",
    "rshift",
]
_with_reverse = _other + _arithmetic + _boolean
_double = [f"{prefix}{function_name}" for function_name in _with_reverse for prefix in ["", "r"]]


_set_magics(_access + _comparisons + _others + _double)


# Other stuff
# ------------------------------


@dataclass
class NameSpace:
    _obj: Struct
    _name: str

    def __getattr__(self, item: str):
        if item.startswith("_"):
            return object.__getattribute__(self, item)
        pd_class = self._obj.__class__._attr_if_exists(self._name)
        pd_method = getattr(pd_class, item)
        if isinstance(pd_method, property):
            # noinspection PyProtectedMember
            return self._obj._call_method(self._name, item)
        # noinspection PyProtectedMember
        return partial(self._obj._call_method, self._name, item)


@dataclass
class Indexer:
    _obj: Struct
    _name: str

    def __getitem__(self, item):
        # noinspection PyProtectedMember
        return self._obj._call_method(self._name, "__getitem__", item)

    def __setitem__(self, key, value):
        # noinspection PyProtectedMember
        self._obj._call_method(self._name, "__setitem__", key, value)


class TeralityWarning(Warning):
    def __init__(self, message):
        super().__init__()
        self.message = message

    def __str__(self):
        return repr(self.message)


ITERATION_WARNING = "Iterating data structures is inefficient, see https://docs.terality.com/getting-terality/user-guide/best-practices-and-anti-patterns for more information."


class StructIterator:
    struct: Struct
    _pos: int
    _buffer: list
    _buffer_start: int

    def __init__(self, struct: Struct):
        self.struct = struct
        self._pos = 0
        self._buffer = []
        self._buffer_start = 0

        warnings.warn(TeralityWarning(ITERATION_WARNING))

    def __iter__(self):
        # Must return itself, as per the [documentation](https://docs.python.org/3.8/library/stdtypes.html#typeiter).
        return self

    @property
    def _buffer_stop(self):
        return self._buffer_start + len(self._buffer)

    def __next__(self) -> Any:
        if self._pos >= self._buffer_stop:
            self._buffer_start = self._pos
            te_struct_slice = self.struct.get_range_auto(self._buffer_start)
            pd_struct_slice = te_struct_slice.tolist()
            self._buffer = list(pd_struct_slice)
            if len(self._buffer) == 0:
                raise StopIteration()
        value = self._buffer[self._pos - self._buffer_start]
        self._pos += 1
        return value
