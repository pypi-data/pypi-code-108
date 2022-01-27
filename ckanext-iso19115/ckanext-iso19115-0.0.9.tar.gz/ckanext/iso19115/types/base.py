from __future__ import annotations
from dataclasses import dataclass

from typing import Any, Generic, Iterable, NamedTuple, Type, TypeVar

T = TypeVar("T")


def _id(v: T) -> T:
    return v


class CodeListValue(NamedTuple):
    name: str
    definition: str
    location: str = ""


@dataclass
class Atomic:
    value: Any

    def as_jml(self):
        ns = self.__module__.split(".")[-1]
        data = JmlRecord(f"{ns}:{self.__class__.__name__}")
        v = getattr(self, "format", _id)(self.value)
        data.append(v)
        return data


@dataclass
class Codelist(Generic[T]):
    value: str

    @classmethod
    def _qualify(cls):
        ns = cls.__module__.split(".")[-1]
        name = cls.__name__
        return ns, name

    @classmethod
    def _into_clv(cls, value: str):
        from ..utils import codelist_options

        ns, name = cls._qualify()
        options = codelist_options(name)
        if not options:
            return CodeListValue(value, "")

        for option in options:
            if option.name == value:
                return option
        raise ValueError(
            f"Codelist {ns}:{name} does not contain value {value}:"
            f" {[o.name for o in options]}"
        )

    def as_jml(self):

        ns, name = self._qualify()
        data = JmlRecord(f"{ns}:{name}")

        option = self._into_clv(self.value)

        data.attrs.update(
            {
                "codeList": option.location,
                "codeListValue": option.name,
            }
        )
        data.append(option.name)

        return data


class JmlRecord(list):
    def __init__(self, name: str, initial_attrs: Iterable[Any] = ()):
        attrs = dict(initial_attrs)
        super().__init__([name, attrs])

    @property
    def name(self):
        return self[0]

    @property
    def attrs(self):
        return self[1]

    @property
    def children(self):
        return self[2:]

    def refine_attributes(self):
        if not self.attrs:
            self.pop(1)
