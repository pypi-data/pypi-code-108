"""
Functions for phrasing feedback (e.g., pluralization).

phrasing.py
"""


#--------------------------#
# Basic English management #
#--------------------------#

def a_an(string):
    """
    Returns the given string it 'a ' prepended, unless it starts with a
    vowel in which case 'an ' will be prepended.
    """
    if string[0].lower() in 'aeiou':
        return 'an ' + string
    else:
        return 'a ' + string


def plural(n, singular, plural=None):
    """
    Uses a number n to determine whether to use the given singular or
    plural phrasing. If the plural phrasing is omitted, it is assumed to
    be just the singular phrasing plus 's'.
    """
    if plural is None:
        plural = singular + 's'

    if n == 0:
        return plural
    elif n == 1:
        return singular
    else:
        return plural


def obj_num(n, singular, plural=None):
    """
    Translates a number n into a string describing that many objects with
    the given singular and plural phrasing. If the plural phrasing is
    omitted, it is assumed to be just the singular phrasing plus 's'.
    """
    if plural is None:
        plural = singular + 's'

    if n == 0:
        return "zero " + plural
    elif n == 1:
        return "one " + singular
    else:
        return "{} {}".format(n, plural)


def comma_list(strings, junction="and"):
    """
    Turns a list of strings into a comma-separated list using the word
    'and' (or the given junction word) before the final item and an
    Oxford comma, but also does the correct thing for 1- or 2-element
    lists. Returns an empty string if given an empty list.
    """
    strings = list(strings)
    if len(strings) == 0:
        return ""
    if len(strings) == 1:
        return strings[0]
    elif len(strings) == 2:
        return strings[0] + " " + junction + " " + strings[1]
    else:
        return ', '.join(strings[:-1]) + ", " + junction + " " + strings[-1]
