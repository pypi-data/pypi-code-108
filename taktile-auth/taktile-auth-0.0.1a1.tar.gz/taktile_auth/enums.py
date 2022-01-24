import typing as t
from enum import Enum


class ExtendedEnum(str, Enum):
    @classmethod
    def set(cls) -> t.Set:
        return {c.value for c in cls}

    @classmethod
    def list(cls) -> t.List:
        return [c.value for c in cls]

    @classmethod
    def names(cls: t.Iterable) -> t.List:
        return [c.name for c in cls]


class Action(ExtendedEnum):
    read = "r"
    write = "w"
    delete = "d"


class Wildcard(ExtendedEnum):
    allowed = "wildcard"
    partial = "partial_wildcard"
    not_allowed = "specified"
