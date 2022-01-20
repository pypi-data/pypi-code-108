"""
This module enables object serialization to and reconstruction from dotted notation strings.
"""

import inspect
import re
from collections import namedtuple
from functools import partial, wraps
from importlib import import_module


__ALL__ = ['get_dotted_path', 'unsafe_build_object', 'build_object', 'register_safe_dotted_path',
           'register_safe_object', 'safe_constructor', 'get_attr_by_path', 'set_attr_by_path', 'del_attr_by_path',
           'has_attr_by_path', 'get_ancestor_paths', 'filter_ancestors', 'filter_descendants']


# Regex helpers to parse a dotted qualified path
RE_PATH = r'[a-zA-Z_][a-zA-Z0-9_\.]*?'
RE_BRACKETS = r'(?P<indices>\[.*\])?'
RE_DOTTED_PATH = re.compile(f'^((?P<module>{RE_PATH}):)?((?P<path>{RE_PATH}){RE_BRACKETS})$')

RE_KEY = r'(\[(\'|\")(?P<key>.*?)(\'|\")\])'
RE_INDEX = r'(\[(?P<index>\d+)\])'
RE_SLICE = r'(?P<slice>\[(?P<start>\d*?):((?P<stop>\d*?)(:(?P<step>\d*?))?)?\])'
RE_INDICES = re.compile(f'({RE_SLICE}|{RE_INDEX}|{RE_KEY})*?')


CONSTRUCTOR_REGISTRY = set()


class _RaiseNotFound:
    pass


DottedPath = namedtuple('DottedPath', ('module', 'path', 'indices'))


def get_cls_dotted_path(obj):
    return f"{obj.__module__}:{obj.__qualname__}"


def get_attr_dotted_path(obj):
    cls = obj.__self__.__class__
    return f"{cls.__module__}:{cls.__qualname__}.{obj.__func__.__name__}"


def get_descriptor_dotted_path(obj):
    cls = obj.__objclass__
    return f"{cls.__module__}:{cls.__qualname__}.{obj.__name__}"


OBJECT_PARSER = (
    (inspect.ismodule, lambda obj: obj.__name__),
    (inspect.isclass, get_cls_dotted_path),
    (inspect.isfunction, get_cls_dotted_path),
    (inspect.ismethod, get_attr_dotted_path),
    (inspect.ismethoddescriptor, get_descriptor_dotted_path),
    (lambda _: True, lambda obj: get_cls_dotted_path(obj.__class__)),
)


def get_dotted_path(obj):
    """Returns a string containing a fully qualified path that refers to the constructor class or module where the
    object resides, enabling to import the specific object by that its string with get_object_by_full_path. If you need
    to access a nested attribute, please refer to nested_attribute family of helpers in this module.
    """
    try:
        return next(parser(obj) for condition, parser in OBJECT_PARSER if condition(obj))
    except StopIteration:
        raise NotImplementedError(f"Unexpected object type {type(obj)} while parsing dotted path for: {obj!r}")


def register_safe_dotted_path(dotted_path, registry=None):
    registry = registry or CONSTRUCTOR_REGISTRY
    registry.add(dotted_path)


def register_safe_object(obj, registry=None):
    dotted_path = get_dotted_path(obj)
    register_safe_dotted_path(dotted_path, registry=registry)


def build_object(dotted_path, registry=None):
    if dotted_path not in (registry or CONSTRUCTOR_REGISTRY):
        raise TypeError(f"Unregistered constructor: {dotted_path}; please refer to register_safe_object")

    return unsafe_build_object(dotted_path)


def safe_constructor(constructor=None, *, registry=None):
    if constructor is None:
        return partial(safe_constructor, registry=registry)

    register_safe_object(constructor, registry=registry)
    return constructor


def unsafe_build_object(dotted_path):
    dotted_path = _parse_dotted_path(dotted_path)

    # Get module, defaults to main if no module is obtained from path
    module = import_module(dotted_path.module) if dotted_path.module else import_module('__main__')

    return _get_attr_and_indices_by_path(module, dotted_path.path, dotted_path.indices)


def get_attr_by_path(obj, path):
    path = _parse_simple_path(path)

    return _get_attr_by_path(obj, path)


def set_attr_by_path(obj, path, value):
    path, name = _split_parent_path(_parse_simple_path(path))
    setattr(obj, name, value)


def del_attr_by_path(obj, path):
    path, name = _split_parent_path(_parse_simple_path(path))
    delattr(obj, name)


def has_attr_by_path(obj, path):
    path, name = _split_parent_path(_parse_simple_path(path))
    return hasattr(obj, name)


def get_ancestor_paths(path, reverse=False):
    path = path.split('.')
    rng = range(len(path), 0, -1) if reverse else range(1, len(path) + 1)
    return ['.'.join(p) for p in [path[:i] for i in rng]]


def filter_ancestors(path, family):
    return {p for p in family if p in set(get_ancestor_paths(path))}


def filter_descendents(path, family):
    return {p for p in family if p.startswith(path)}


# Helpers: getters
def _get_attr_and_indices_by_path(obj, path, indices):
    attr = _get_attr_by_path(obj, path)
    if indices:
        return _get_indices_by_atrr(attr, indices)
    return attr


def _get_attr_by_path(obj, path):
    if not path:
        return obj

    path = path.split('.')

    for path_index, name in enumerate(path):
        obj = getattr(obj, name, _RaiseNotFound)
        if obj is _RaiseNotFound:
            searched_path = ('.'.join(path[:path_index])) or get_dotted_path(obj)
            raise AttributeError(f"Unable to find attribute in path: {path[path_index]} in {searched_path}")

    return obj


def _get_indices_by_atrr(attr, indices):
    for index in indices:
        attr = attr[index]
    return attr


# Helpers: Parsers

def _parse_dotted_path(dotted_path):
    if match := RE_DOTTED_PATH.match(dotted_path):
        module, obj, raw_indices = _parse_multiple_regex_groups(match, ['module', 'path', 'indices']).values()
        indices = _parse_indices(raw_indices) if raw_indices else None
        return DottedPath(module, obj, indices)


def _parse_simple_path(path):
    dotted_path = _parse_dotted_path(path)

    if dotted_path.module:
        raise AttributeError(f'Modules are not supported: {path}')

    if dotted_path.indices:
        raise AttributeError(f'Indices are not supported: {path}')

    return dotted_path.path


def _parse_indices(raw_indices):
    def _cast_results(r):
        parsers = [('key', lambda a, b: a), ('index', lambda a, b: int(a)), ('slice', lambda a, b: _parse_slice(b))]
        return next((f(r[i], r) for i, f in parsers if r[i] is not None), None)

    indices = list()

    for match in RE_INDICES.finditer(raw_indices):
        results = _parse_multiple_regex_groups(match, ['key', 'index', 'slice', 'start', 'stop', 'step'])
        if (results := _cast_results(results)) is not None:
            indices.append(results)

    return indices


def _parse_slice(match):
    def _cast_int(i):
        return int(i) if i is not None else None

    start, stop, step = map(_cast_int, (value for group, value in match.items() if group in ['start', 'stop', 'step']))
    return slice(start, stop, step)


def _parse_multiple_regex_groups(match, groups):
    return {group: match.groupdict().get(group, None) for group in groups}


def _split_parent_path(path):
    parent_path, name = path.rsplit('.', 1)
    return parent_path, name
