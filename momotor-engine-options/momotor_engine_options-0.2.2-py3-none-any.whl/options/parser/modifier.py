"""
    A modifier converts a list of values into a single value
"""
import json
import typing

from momotor.options.parser.consts import MOD_RE


def parse_mod(modded_ref: str) -> typing.Tuple[typing.Optional[str], str]:
    """

    >>> parse_mod('')
    (None, '')

    >>> parse_mod(' 123')
    (None, ' 123')

    >>> parse_mod('%mod')
    ('mod', '')

    >>> parse_mod('%mod 123')
    ('mod', ' 123')

    >>> parse_mod(' %mod 123')
    ('mod', ' 123')

    :param modded_ref:
    :return:
    """
    m_mod = MOD_RE.match(modded_ref)

    if m_mod:
        mod = m_mod.group('mod')
        if mod:
            return mod, modded_ref[m_mod.end(m_mod.lastindex):]

    return None, modded_ref


def exclude_none(values):
    for v in values:
        if v is not None:
            yield v


def cast_number(values):
    for v in values:
        if v is None:
            continue

        if isinstance(v, (int, float)):
            yield v
        else:
            try:
                yield int(v)
            except ValueError:
                try:
                    yield float(v)
                except ValueError:
                    pass


def quote_str(value):
    if isinstance(value, str) and (' ' in value or '"' in value or "'" in value):
        if "'" in value:
            return '"' + value.replace('"', '\\"') + '"'
        else:
            return "'" + value + "'"

    return str(value)


def none_if_empty(fn, values):
    values = list(values)
    return fn(values) if values else None


# All modifiers
COMBINER_MODIFIERS = {
    'all': lambda values: none_if_empty(all, values),
    'any': lambda values: none_if_empty(any, values),
    'notall': lambda values: none_if_empty(lambda v: not all(v), values),
    'not': lambda values: none_if_empty(lambda v: not any(v), values),
    'notany': lambda values: none_if_empty(lambda v: not any(v), values),
    'sum': lambda values: none_if_empty(sum, cast_number(values)),
    'max': lambda values: none_if_empty(max, cast_number(values)),
    'min': lambda values: none_if_empty(min, cast_number(values)),
    'cat': lambda values: ''.join(str(v) for v in exclude_none(values)),
    'join': lambda values: ','.join(quote_str(v) for v in exclude_none(values)),
    'joinc': lambda values: ','.join(quote_str(v) for v in exclude_none(values)),
    'joins': lambda values: ' '.join(quote_str(v) for v in exclude_none(values)),
    'joincs': lambda values: ', '.join(quote_str(v) for v in exclude_none(values)),
    'json': lambda values: json.dumps(list(values), separators=(',', ':')),
    'first': lambda values: list(exclude_none(values))[0],
    'last': lambda values: list(exclude_none(values))[-1],
}


def apply_combiner_modifier(mod: str, values: typing.Sequence[typing.Union[str, int, float, bool]]) \
        -> typing.Union[str, int, float, bool, None]:

    try:
        mod_fn = COMBINER_MODIFIERS[mod]
    except KeyError:
        raise ValueError(f"invalid modifier {mod!r}")

    try:
        result = mod_fn(values)
    except (ValueError, IndexError):
        result = None

    return result
