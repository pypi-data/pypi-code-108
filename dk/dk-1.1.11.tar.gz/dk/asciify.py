# -*- coding: utf-8 -*-

"""Convert unicode strings to visually similar ascii representations.
"""
import re


REPLACEMENTS = {
    u'æ': 'ae',
    u'øôöòóõ': 'o',
    u'àáâãäå': 'a',
    u'èéêë': 'e',
    u'ìíîï': 'i',
    u'üúùû': 'u',
    u'ÿý': 'y',
}
REPL_CHARS = u''.join(REPLACEMENTS.keys())
REPL_CHARS += REPL_CHARS.upper()


def _replacement(ch):
    """Return replacement for `ch`.
    """
    c = ch.lower()
    for key in REPLACEMENTS:
        if c in key:
            val = REPLACEMENTS[key]
            return val.upper() if ch.isupper() else val
    return ch


def asciify(s, spaces=None, legal=None, replacement=''):
    """Convert unicode string `s` to a similarly looking ascii string.

       If `spaces` is specified, runs of space characters are replaced
       with exactly one `spaces`.

       If `legal` is specified (as a string), only characters from
       `legal` will be in the result, otherwise all characters from
       ascii 32 to ascii 127 are allowed.

       If `replacement` is passed, then any characters that are elided
       will be replaced by `replacement`.
    """
    res = ""
    for ch in s:
        if ch in REPL_CHARS:
            res += _replacement(ch)
        elif legal is None:
            if 32 <= ord(ch) < 127:
                res += ch
            else:
                res += replacement
        else:
            if ch in legal + ' ':
                res += ch
            else:
                res += replacement

    if spaces:
        res = re.sub(r'\s+', spaces, res)

    return str(res)


def ascii_name(name):
    """Convert name from unicode to a ascii representation that
       (while surely a grave bastardization) can be used as a
       filename without (ever!) causing problems.
    """
    return asciify(name.lower(), spaces='-',
                   legal=u'abcdefghijklmnopqrstuvwxyz-')


def slug(txt):
    """Same as above, but intended for URIs.
    """
    return asciify(txt.lower(), spaces='-',
                   legal=u'abcdefghijklmnopqrstuvwxyz-0123456789')
