from collections import ChainMap
from collections.abc import Mapping, Sequence, Set, MutableMapping
from typing import Optional

from nv.utils.collections.structures import merge_mappings

from .facades import ExposesMutableDunderDictMixin


__ALL__ = ['serialize', 'parse', 'ObjectDict']


# TODO: Revise ObjectDict using parser core module; also needs to check if it's useful vs. pydantic (which typechecks)


BASIC_TYPES = (
    str,
    bytes,
    int,
    float,
    bool,
    type(None),
)


class ObjectDict(ExposesMutableDunderDictMixin, MutableMapping):
    """
    Implements dictionary access to object attributes (e.g. for config files).  It also rebuilds itself
    from dictionaries using the constructor from_dict. Nested dictionaries are implemented as ObjectDicts,
    allowing dotted access to nested dictionaries.

    This is a simple solution when you know and control the data you are parsing from. For things that need
    further checking, probably pydantic or marshmallow are better suited.
    """
    def __init__(self, _recursive=True, _defaults: Optional[Mapping] = None, **kwargs):
        self.apply_mapping(kwargs, recursive=_recursive, defaults=_defaults)

    def __repr__(self):
        return dict.__repr__(self.__dict__)

    def __str__(self):
        return dict.__str__(self.__dict__)

    def apply_mapping(self, d: Mapping, recursive=True, defaults: Optional[Mapping] = None):
        for k, v in ChainMap(d, defaults or dict()).items():
            setattr(self, k, parse(v) if recursive else v)

    @classmethod
    def from_dict(cls, d: Mapping, recursive=True, defaults: Optional[Mapping] = None) -> 'ObjectDict':
        instance = cls.__new__(cls)
        instance.apply_mapping(d, recursive=recursive, defaults=defaults)
        return instance

    def as_dict(self, recursive=True) -> dict:
        return {k: serialize(v) for k, v in self.__dict__.items()} if recursive else self.__dict__

    def merge_into(self, merger: Mapping) -> Mapping:
        return merge_mappings(self, merger)

    def incorporate(self, merged: Mapping):
        self.__dict__ = merge_mappings(merged, self.__dict__)


def apply_base_type(b, fn):
    return b


def apply_mapping(m: Mapping, fn) -> dict:
    return {k: fn(v) for k, v in m.items()}


def apply_sequence(s: Sequence, fn) -> list:
    return [fn(v) for v in s]


def apply_set(s: Set, fn) -> set:
    return {fn(v) for v in s}


def apply_as_dict(o: ObjectDict, fn):
    return o.as_dict()


def apply_from_dict(o, fn):
    return ObjectDict.from_dict(o)



SERIALIZERS_MAP = (
    (ObjectDict, apply_as_dict),
    (BASIC_TYPES, apply_base_type),
    (Set, apply_set),
    (Sequence, apply_sequence),
    (Mapping, apply_mapping),
)


_RaiseError = object()


def apply(obj, fn, type_map, default=_RaiseError):
    try:
        return next((d for t, d in type_map if isinstance(obj, t)))(obj, fn)
    except StopIteration:
        if default is _RaiseError:
            raise TypeError(f'Unable to {fn.__name__} type: {type(obj)}')
        return default


def serialize(obj, type_map=SERIALIZERS_MAP, default=_RaiseError):
    return apply(obj, serialize, type_map, default=default)


PARSERS_MAP = (
    (BASIC_TYPES, apply_base_type),
    (Set, apply_set),
    (Sequence, apply_sequence),
    (Mapping, apply_from_dict),
)


def parse(obj, type_map=PARSERS_MAP, default=_RaiseError):
    return apply(obj, parse, type_map, default=default)
