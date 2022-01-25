from typing import Dict, Callable, Union, TypeVar

from sm.misc.funcs import identity_func


K = TypeVar('K')
V = TypeVar('V')


class InMemStore(Dict[K, V]):
    def __init__(self, rdict: Dict[K, V], deserialize: Callable[[str], V] = None):
        self.rdict = rdict
        self.deserialize = deserialize or identity_func

    def __contains__(self, item):
        return item in self.rdict

    def __getitem__(self, item):
        return self.deserialize(self.rdict[item])

    def __setitem__(self, key: str, value: Union[str, bytes]):
        self.rdict[key] = value

    def values(self):
        return (self.deserialize(x) for x in self.rdict.values())

    def items(self):
        return ((k, self.deserialize(v)) for k, v in self.rdict.items())

    def keys(self):
        return self.rdict.keys()

    def __len__(self):
        return len(self.rdict)

    def cache_dict(self) -> 'CacheDictStore[K, V]':
        return CacheDictStore(self)

    def as_dict(self):
        return {k: self.deserialize(v) for k, v in self.rdict.items()}


class CacheDictStore(Dict[K, V]):
    def __init__(self, store: Dict[K, V]):
        self.store = store
        self.cache = {}

    def __contains__(self, item: str):
        return item in self.cache or item in self.store

    def __getitem__(self, item: str):
        if item not in self.cache:
            self.cache[item] = self.store[item]
        return self.cache[item]

    def __setitem__(self, key: str, value: Union[str, bytes]):
        raise Exception("NotSupportedFunction")

    def values(self):
        return self.store.values()

    def items(self):
        return self.store.items()

    def keys(self):
        return self.store.keys()

    def __len__(self):
        return len(self.store)