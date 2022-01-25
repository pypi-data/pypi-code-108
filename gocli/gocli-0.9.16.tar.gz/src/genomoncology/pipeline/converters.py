try:
    import ujson as json

    default_json_kwargs = dict(escape_forward_slashes=False)
except ImportError:
    import json

    default_json_kwargs = {}

from typing import Optional
from pygments import highlight, lexers, formatters

from cytoolz.curried import curry
from functools import singledispatch


@singledispatch
def to_json_str(unit, **kwargs):
    kwargs = {**default_json_kwargs, **kwargs}
    return json.dumps(unit, **kwargs)


@to_json_str.register(str)  # noqa F811
def _(unit, **_):
    return unit


@to_json_str.register(float)  # noqa F811
@to_json_str.register(int)
def _(unit, **_):
    return str(unit)


@curry
def to_pretty_json_str(unit):
    formatted_json = to_json_str(unit, indent=4)
    colorful_json = highlight(
        formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter()
    )
    return colorful_json


@singledispatch
def from_json_str(unit):
    return unit


@from_json_str.register(str)  # noqa F811
def _(unit):
    return json.loads(unit)


@singledispatch
def clean_str(unit):
    raise NotImplementedError(f"{unit}: Invalid Type [{type(unit)}]")


@clean_str.register(str)  # noqa F811
def _(unit):
    return unit.strip()


def non_null(unit):
    return unit is not None and unit != ""


@singledispatch
def to_str(value):
    return str(value)


@to_str.register(float)  # noqa F811
def _(value):
    return f"{value:.5f}"


def obj_to_dict(fields, obj, **extras) -> Optional[dict]:
    if obj is None:
        return None

    # return all from Bravado object if fields is None
    elif fields is None:
        return obj.__dict__.get("_Model__dict", vars())

    # return only selected fields
    else:
        a_dict = {key: getattr(obj, key, None) for key in fields}
        a_dict.update(extras)
        return a_dict


def fint(str_val):
    """ try to convert to int, then float if fails, then return None. """
    for f in [int, float]:
        try:
            return f(str_val)
        except (ValueError, TypeError):
            pass


@curry
def cint(str_val, default=0):
    """ try to convert to int, then float if fails, then return None. """
    try:
        return int(str_val)
    except (ValueError, TypeError):
        return default
