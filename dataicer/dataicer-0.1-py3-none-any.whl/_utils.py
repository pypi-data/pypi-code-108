from typing import Union
from pathlib import Path
from re import compile as recompile
from functools import reduce

PathType = Union[str, Path]

_class_name = recompile("(?<=')(.*)(?=')")


def get_full_class_definition(kls):
    """The full class definition from a variable. E.g. a.b.c"""
    kls = str(kls.__class__)
    return _class_name.findall(kls)[0]


def import_object_by_definition(definition):
    """Dynamic importing of an object by it's definition. E.g. 'a.b.c' returns c"""
    return reduce(
        getattr, definition.split(".")[1:], __import__(definition.partition(".")[0])
    )
