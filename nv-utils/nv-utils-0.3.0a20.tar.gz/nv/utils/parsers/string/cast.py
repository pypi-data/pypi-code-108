import datetime
from decimal import Decimal, InvalidOperation
from functools import lru_cache

from ..core import build_parser
from .datetime import parse_datetime, parse_date, parse_time, parse_duration
from .boolean import parse_strict_boolean, parse_boolean


__ALL__ = ['cast', 'guess_type',
           'cast_to_type', 'safe_cast_to_type', 'cast_to_guessed_type',
           'build_caster', 'build_custom_caster',
           'DEFAULT_CASTERS', 'DEFAULT_DECIMAL_CASTERS']


NUMBER_CASTERS = (
    (int, ),
    (float, ),
    (complex, )
)


DECIMAL_NUMBER_CASTERS = (
    (int, ),
    (Decimal, ),
    (float, ),
    (complex, )
)


DATETIME_CASTERS = (
    (datetime.datetime, parse_datetime),
    (datetime.date, parse_date),
    (datetime.time, parse_time),
    (datetime.timedelta, parse_duration),
)


BOOL_CASTERS = (
    (bool, parse_strict_boolean),
)


ENHANCED_BOOL_CASTERS = (
    (bool, parse_boolean),
)


DEFAULT_CASTERS = (
    *NUMBER_CASTERS,
    *BOOL_CASTERS,
    *DATETIME_CASTERS,
    (str, )
)


DEFAULT_DECIMAL_CASTERS = (
    *DECIMAL_NUMBER_CASTERS,
    *BOOL_CASTERS,
    *DATETIME_CASTERS,
    (str, )
)


def _cast_attempt(obj, to_type):
    try:
        resp = to_type(obj) if obj is not None else to_type()
    except (TypeError, ValueError, InvalidOperation):
        return obj, None

    # If we get None from a valid input, it means that our parsing has not went through
    if resp is None and obj is not None:
        return obj, None

    return resp, type(resp)


def _cast_first(obj, to_type, type_casters):
    type_casters = type_casters or (to_type,)
    for type_caster in type_casters:
        cast_obj, tentative_type = _cast_attempt(obj, type_caster)

        if tentative_type is to_type:
            return cast_obj, to_type

    return obj, None


@lru_cache(maxsize=1)
def _get_casters_mapping(casters):
    return {t: (type_casters or (t, )) for t, *type_casters in casters}


def guess_type(obj, casters=DEFAULT_CASTERS):
    """
    Tries to guess the most appropriate type for an object (typically a string) according to a preferred list.
    In essence, what this does is attempt to cast 'obj' into the first type (or callable) that fits. By fitting
    it means returning a valid object (instead of raising a ValueError).
    This is a bit tricky for boolean types, so we stick to 'TRUE/FALSE' (and lower case variations) for the default
    case but we offer the alternative for a more flexible boolean interpretation by setting different parsers.
    We also include a convenience to parse Decimal numbers rather than floats (DEFAULT_PARSERS_DECIMAL).
    """
    if obj is None:
        return None, None

    for type_guess, *guess_parsers in casters:
        cast_obj, cast_type = _cast_first(obj, type_guess, guess_parsers)
        if cast_type is not None:
            return cast_type, cast_obj

    return None, obj


def cast_to_type(obj, to_type, casters=DEFAULT_CASTERS):
    if isinstance(obj, to_type):
        return obj

    casters_mapping = _get_casters_mapping(casters)
    type_casters = casters_mapping.get(to_type, None) or (to_type, )

    cast_obj, cast_type = _cast_first(obj, to_type, type_casters)

    if cast_type is None:
        raise TypeError(f"Unable to cast object into {to_type!s} using {type_casters}: {obj}")

    return cast_obj


def safe_cast_to_type(obj, to_type):
    try:
        return cast_to_type(to_type, obj)
    except TypeError:
        return obj


def cast_to_guessed_type(obj, casters=DEFAULT_CASTERS, strict=False):
    _type, cast_obj = guess_type(obj, casters=casters)
    if strict and _type is None:
        raise TypeError(f"unable to guess type of '{obj}' and strict was set to True.")

    return cast_obj


def cast_element(obj, _, *, strict=False, casters=DEFAULT_CASTERS, **kwargs):
    return cast_to_guessed_type(obj, casters=casters, strict=strict)


def build_caster(casters, strict=False):
    return build_parser(cast_element, strict=strict, casters=casters)


def build_custom_casting_map(decimals=False,
                             enhanced_bool=False,
                             date_time=False
                             ):
    return (
        *(DECIMAL_NUMBER_CASTERS if decimals else NUMBER_CASTERS),
        *(ENHANCED_BOOL_CASTERS if enhanced_bool else BOOL_CASTERS),
        *(DATETIME_CASTERS if date_time else ()),
        (str, )
    )


def build_custom_caster(strict=False, **custom_casting_map_kwargs):
    return build_caster(build_custom_casting_map(**custom_casting_map_kwargs),
                        strict=strict)


cast = build_caster(DEFAULT_CASTERS, strict=False)
