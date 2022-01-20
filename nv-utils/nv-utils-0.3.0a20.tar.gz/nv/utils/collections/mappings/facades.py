from collections.abc import Mapping
from typing import TypeVar


K = TypeVar('K')
V = TypeVar('V')


__ALL__ = ["ExposesAttrsMixin, ExposesMutableAttrsMixin", "MapMixin", "MutableMapMixin",
           "ExposesDunderDictMixin", "ExposesMutableDunderDictMixin", "NonMutableDictWrapper"]


class ExposesAttrsMixin:

    def __getattr__(self, name: str) -> V:
        return self[name]


class ExposesMutableAttrsMixin(ExposesAttrsMixin):

    def __setattr__(self, name: str, value: V):
        self[name] = value

    def __delattr__(self, name: str):
        del self[name]


class MapMixin:
    _container = None

    def __getitem__(self, key: str) -> V:
        # Guards against infinite recursion when used with ExposesAttrsMixin
        if self._container is None:
            raise TypeError(f"{key}: container is not initialized")

        return self._container[key]

    def __len__(self):
        return len(self._container)

    def __iter__(self):
        return iter(self._container)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._container!r})"


class MutableMapMixin(MapMixin):

    def __setitem__(self, key: str, value: V):
        # Guards against infinite recursion when used with ExposesAttrsMixin
        if self._container is None:
            raise TypeError(f"{key}: container is not initialized")

        self._container[key] = value

    def __delitem__(self, key: str):
        # Guards against infinite recursion when used with ExposesAttrsMixin
        if self._container is None:
            raise TypeError(f"{key}: container is not initialized")

        del self._container[key]


class ExposesDunderDictMixin:

    def __getitem__(self, key: str) -> V:
        return self.__dict__[key]

    def __len__(self):
        return len(self.__dict__)

    def __iter__(self):
        return iter(self.__dict__)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__!r})"


class ExposesMutableDunderDictMixin(ExposesDunderDictMixin):

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __delitem__(self, key):
        del self.__dict__[key]


class NonMutableDictWrapper(MapMixin, Mapping[K, V]):
    def __init__(self, container):
        self._container = container
