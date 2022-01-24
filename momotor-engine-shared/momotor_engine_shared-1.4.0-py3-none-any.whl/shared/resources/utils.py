from itertools import filterfalse
import re
import typing


def unique_everseen(iterable, key=None):
    # https://docs.python.org/3.7/library/itertools.html#itertools-recipes
    """List unique elements, preserving order. Remember all elements ever seen."""
    # unique_everseen('AAAABBBCCDAABBB') --> A B C D
    # unique_everseen('ABBCcAD', str.lower) --> A B C D
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in filterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element


SAFE_STR_RE = re.compile(r'\w+')


def escape_str(s: str, escape_chars: typing.Set[str] = None) -> str:
    """ Return string with characters in `escape_chars` escaped.
    Uses the backslash character for escapes, so that is always escaped and does not have to be supplied
    to `escape_chars`
    """
    escape_chars = {'\\'} | (escape_chars if escape_chars else set())

    result = ''
    for c in s:
        if c in escape_chars:
            result += '\\'

        result += c

    return result


def quote_str(s: str, ) -> str:
    """ Quote string containing unsafe characters for both group-name and items
    :param s: string to make safe
    :return:
    """
    # Only containing safe characters
    m = SAFE_STR_RE.match(s)
    if m and m[0] == s:
        return escape_str(s)

    has_single_quotes = "'" in s
    has_double_quotes = '"' in s

    if has_single_quotes and has_double_quotes:
        return '"' + escape_str(s, {'"'}) + '"'
    elif has_single_quotes:
        return '"' + escape_str(s) + '"'
    else:
        return "'" + escape_str(s) + "'"
