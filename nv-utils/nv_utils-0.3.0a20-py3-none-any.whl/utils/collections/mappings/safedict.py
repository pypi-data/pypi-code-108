from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Iterator, Callable, MutableSet, TypeVar


__ALL__ = ['MissingKey', 'SafeDict', 'SafeDictWrapper', 'SafeDictWrapperWithTracker']


K = TypeVar('K')
V = TypeVar('V')


class MissingKey:
    """
    Drives the behaviour of SafeDict and SafeDictWrapper when the requested key is missing.
    """

    class Behaviour(int, Enum):
        IGNORE = 0
        MARK = 1
        REPLACE = 2
        CALL = 3
        RETURN_PLACEHOLDER = 4
        RAISE = 255

    @dataclass(frozen=True, eq=True)
    class Missing:
        key: str

    REPLACEMENT = ""
    PLACEHOLDER_TEMPLATE = "{{{key!s}}}"
    DEFAULT = object()

    @classmethod
    def match_behaviour(cls,
                        behaviour: 'MissingKey.Behaviour',
                        key: str,
                        replacement: V | Callable[[K], V] | None = DEFAULT
                        ) -> V | Missing | None:
        match behaviour:
            case cls.Behaviour.IGNORE:
                return None
            case cls.Behaviour.MARK:
                return cls.Missing(key)
            case cls.Behaviour.REPLACE:
                return cls.REPLACEMENT if replacement is cls.DEFAULT else replacement
            case cls.Behaviour.CALL:
                clb = cls.REPLACEMENT if replacement is cls.DEFAULT else replacement
                if not callable(clb):
                    raise ValueError(f"replacement={clb!r} must be callable if behaviour={behaviour!r}")
                return clb(key)
            case cls.Behaviour.RETURN_PLACEHOLDER:
                return cls.PLACEHOLDER_TEMPLATE.format(key=key)
            case cls.Behaviour.RAISE:
                raise KeyError(f"missing: {key}")
            case _:
                raise ValueError(f"undefined behaviour for MissingKey: {behaviour}.")

    @classmethod
    def build_missing_key_updater(cls,
                                  missing_keys: MutableSet,
                                  behaviour: Behaviour = Behaviour.IGNORE,
                                  replacement: V | Callable[[K], V] | None = DEFAULT
                                  ) -> Callable[[K], V] | Missing | None:

        def update_missing_keys(k: K) -> V | cls.Missing | None:
            missing_keys.add(k)
            return cls.match_behaviour(behaviour, k, replacement=replacement)

        return update_missing_keys


class SafeDict(dict[K, V]):
    """
    Slim wrapper over Python's dict that implement MissingKey behaviours when a missing key is requested. For
    a wrapper that preserves the original underlying mapping structure refer to SafeDictWrapper.
    """
    MissingKey = MissingKey

    def __init__(self,
                 *args,
                 behaviour: MissingKey.Behaviour = MissingKey.Behaviour.IGNORE,
                 replacement: V | Callable[[K], V] | None = MissingKey.DEFAULT,
                 **kwargs
                 ):
        super().__init__(*args, **kwargs)
        self.behaviour = behaviour
        self.replacement = replacement

    def __missing__(self, key: K) -> V | MissingKey.Missing | None:
        return self.MissingKey.match_behaviour(self.behaviour, key, replacement=self.replacement)


class SafeDictWrapper(Mapping[K, V]):
    """
    Non-mutable wrapper that implements MissingKey behaviour for any Python mapping (e.g. ChainMap). If you only
    need a dict refer to SafeDict.
    """
    MissingKey = MissingKey

    def __init__(self,
                 mapping: Mapping[K, V],
                 behaviour: MissingKey.Behaviour = MissingKey.Behaviour.IGNORE,
                 replacement: V | Callable[[K], V] | None = MissingKey.DEFAULT
                 ):
        self._mapping = mapping
        self.behaviour = behaviour
        self.replacement = replacement

    def __getitem__(self, k: K) -> V | MissingKey.Missing | None:
        if (v := self._mapping.get(k, self.MissingKey.Missing)) is not self.MissingKey.Missing:
            return v
        else:
            return self.MissingKey.match_behaviour(self.behaviour, k, replacement=self.replacement)

    def __len__(self) -> int:
        return len(self._mapping)

    def __iter__(self) -> Iterator[K]:
        return iter(self._mapping)


class SafeDictWrapperWithTracker(SafeDictWrapper[K, V]):
    MissingKey = MissingKey

    def __init__(self,
                 mapping: Mapping[K, V],
                 behaviour: MissingKey.Behaviour = MissingKey.Behaviour.IGNORE,
                 replacement: V | Callable[[K], V] | None = MissingKey.DEFAULT,
                 missing_keys_set: MutableSet[K] = None
                 ):
        self._missing_keys = missing_keys_set or set()
        updater = MissingKey.build_missing_key_updater(self._missing_keys, behaviour=behaviour, replacement=replacement)
        super().__init__(mapping, behaviour=MissingKey.Behaviour.CALL, replacement=updater)
        self.updater = updater

    @property
    def missing_keys(self):
        return set(self._missing_keys)

    def clear_missing_keys(self):
        self._missing_keys.clear()
