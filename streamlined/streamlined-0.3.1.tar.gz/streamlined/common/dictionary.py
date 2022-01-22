from __future__ import annotations

from collections import UserDict
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Tuple, TypeVar

from .predicates import IS_DICT, IS_SEQUENCE

K = TypeVar("K")
V = TypeVar("V")


def DEFAULT_KEYERROR(value: Dict[K, V], property: K) -> ValueError:
    return ValueError(f"{value} should have {property} property")


def get_or_raise(value: Dict[K, V], property: K, error: Optional[Exception] = None) -> V:
    try:
        return value[property]
    except KeyError as keyerror:
        if error is None:
            error = DEFAULT_KEYERROR(value, property)
        raise error from keyerror


def get_or_default(mapping: Mapping[K, V], key: K, default: V) -> V:
    try:
        return mapping[key]
    except KeyError:
        return default


def set_if_not_none(dictionary: Dict[Any, Any], key: Any, value: Any) -> bool:
    if value is not None:
        dictionary[key] = value
        return True
    return False


def update_with_callable(dictionary: Dict[K, V], key: K, value_updater: Callable[[V], V]) -> bool:
    """
    Update existing value under specified key by transforming it through a callable.
    Return whether value of specified key is updated.
    """
    try:
        new_value = value_updater(dictionary[key])
        dictionary[key] = new_value
        return True
    except KeyError:
        return False


class ProxyDictionary(UserDict):
    """
    A proxy dictionary is intended to provide some more key value
    pairs beyond a mapping object.

    >>> original = {'a': 1, 'b': 2}
    >>> proxied = ProxyDictionary(original, c=3)
    >>> proxied['a'] + proxied['b'] + proxied['c']
    6
    """

    proxy: Mapping[Any, Any]

    def __init__(self, proxy: Mapping[Any, Any], **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.proxy = proxy

    def __getitem__(self, key: Any) -> Any:
        try:
            return super().__getitem__(key)
        except KeyError:
            return self.proxy[key]


def findkey(source: Any, predicate: Callable[[Any], bool]) -> Iterable[Any]:
    """
    Search for value(s) under given key in a dictionary.

    The search will be recursive.

    >>> list(findkey({'a': 1, 'b': [{'a': 3}, {'b': 4}, {'a': 7}]}, lambda key: key == 'a'))
    [1, 3, 7]
    """
    if IS_DICT(source):
        for k, v in source.items():
            if predicate(k):
                yield v
            yield from findkey(v, predicate)
    elif IS_SEQUENCE(source):
        for item in source:
            yield from findkey(item, predicate)


def findvalue(source: Any, predicate: Callable[[Any], bool]) -> Iterable[Any]:
    """
    Search for value(s) matching a condition in a dictionary.

    The search will be recursive.

    >>> list(findvalue({'a': 1, 'b': [{'a': 3}, {'b': 4}, {'a': 7}]}, lambda value: isinstance(value, int) and value > 3))
    [4, 7]
    """
    if predicate(source):
        yield source

    if IS_DICT(source):
        for v in source.values():
            yield from findvalue(v, predicate)
    elif IS_SEQUENCE(source):
        for item in source:
            yield from findvalue(item, predicate)


def chained_get(
    dictionary: Dict[K, V], *keys: K, criterion: Callable[[V], bool] = bool, default: Any = None
) -> Optional[Tuple[K, V]]:
    """
    Try getting with each key until one value is found
    matching provided criterion, return that key value pair
    in this case. If no such key is found, return the default
    value if provided.

    >>> d = {'a': 10, 'c': -1}
    >>> chained_get(d, 'b', 'c', 'a', criterion=lambda v: v > 0)
    ('a', 10)
    """
    for key in keys:
        try:
            value = dictionary[key]
            if criterion(value):
                return (key, value)
        except KeyError:
            continue
    return default


if __name__ == "__main__":
    import doctest

    doctest.testmod()
