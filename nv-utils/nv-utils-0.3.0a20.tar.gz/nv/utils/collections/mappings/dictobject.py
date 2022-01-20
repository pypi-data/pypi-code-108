from collections.abc import Mapping, MutableMapping
from typing import TypeVar

from .facades import ExposesMutableAttrsMixin, ExposesAttrsMixin, MapMixin, MutableMapMixin


V = TypeVar('V')


__ALL__ = ['DictObject', 'DictObjectWrapper', 'MutableDictObjectWrapper']


class DictObject(ExposesMutableAttrsMixin, dict[str, V]):
    """
    Simple implementation of a dictionary that exposes its keys as attributes of an object. This is a simple
    plain vanilla implementation that does not enforce valid attribute names.
    """
    pass


class DictObjectWrapper(ExposesAttrsMixin, MapMixin, Mapping[str, V]):
    """
    Same concept as DictObject, except that it is a wrapper around an existing dictionary that implements the
    double behaviour.
    """
    def __init__(self, container: Mapping[str, V] = None):
        self._container = container or {}


class MutableDictObjectWrapper(ExposesMutableAttrsMixin, MutableMapMixin, MutableMapping[str, V]):
    """
    Mutable version of DictObjectWrapper.
    """
    def __init__(self, container: MutableMapping[str, V] = None):
        self._container = container or {}
