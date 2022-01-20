from collections import Mapping, Iterable
from typing import Any


class DataDict(Mapping):

    def __hash(self, value: Any):
        return hash(e for e in value) if isinstance(value, Iterable) else hash(value)

    def __key(self):
        return tuple((k, self.__hash(self[k])) for k in sorted(self._data))

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return self.__key() == other.__key()

    def __init__(self, data):
        self._data = data if isinstance(data, Mapping) else data.__dict__

    def __getitem__(self, key):
        return self._data[key]

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)
