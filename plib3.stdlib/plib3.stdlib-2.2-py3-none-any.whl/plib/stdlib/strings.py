#!/usr/bin/env python3
"""
Module STRINGS -- String Utilities
Sub-Package STDLIB of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

This module contains utilities for working with strings. The
current contents are:

constant universal_newline -- string representing the "universal
    newline" character

function fix_newlines -- returns a string with line breaks changed
    from old_newline to newline.

function split_string -- splits a string into three pieces, at the
    line breaks after the given start string and before the given
    end string appear. Note edge case behavior: if the start string
    is not found, the first of the three strings returned will be
    empty; if the end string is not found, the last of the three
    will be empty, and if both are not found, the middle of the
    three strings will be the entire string passed in. This may
    seem a little strange, but if you think about how you would use
    this function, it makes sense. (Note also that finding the
    start string really means that plus finding a newline after it,
    and finding the end string really means that plus finding a
    newline before it. This can be tweaked by setting the
    ``find_newlines`` argument to ``False``.)

functions strtobool, strtodate -- self-explanatory.
"""

import datetime

# Newline handling functions

universal_newline = '\n'


def split_string(s, start, end,
                 find_newlines=True, newline=None,
                 remove_delimiters=False):
    
    newline = newline or universal_newline
    i = h = s.find(start)
    if i < 0:
        j = k = s.find(end)
    else:
        j = k = s.find(end, i)
        if find_newlines:
            i = s.find(newline, i) + len(newline)
        else:
            i += len(start)
        if not remove_delimiters:
            h = i
    if (j > -1) and find_newlines:
        if i > -1:
            j = s.rfind(newline, i, j)
        else:
            j = s.rfind(newline, 0, j)
    if remove_delimiters:
        if k > -1:
            k += len(end)
    else:
        k = j
    if i < 0:
        if j < 0:
            return "", s, ""
        return "", s[:j], s[k:]
    if j < 0:
        if h < 1:
            return "", s[i:], ""
        return s[:h], s[i:], ""
    if h < 1:
        return "", s[i:j], s[k:]
    return s[:h], s[i:j], s[k:]


def fix_newlines(s, newline, old_newline=None):
    old_newline = old_newline or universal_newline
    result = newline.join(s.splitlines())
    if s.endswith(old_newline):
        return result + newline
    return result


# Type conversion functions

def strtoint(s, default=""):
    """Return int from string s interpreting ``default`` as 0.
    """
    return 0 if s == default else int(s)


def strtobool(s, falsestr='False', truestr='True'):
    """Return bool from string s interpreting s as a 'Python value string'.
    
    Return None if s is not 'True' or 'False'.
    """
    return {falsestr: False, truestr: True}.get(s, None)


def strtodate(s):
    """Return date object from string formatted as date.__str__ would return.
    """
    return datetime.date(*list(map(int, s.split('-'))))
