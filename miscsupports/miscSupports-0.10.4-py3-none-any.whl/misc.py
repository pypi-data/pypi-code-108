from contextlib import contextmanager
import sys
import os


def parse_as_numeric(value, return_type=int):
    """
    Try isolating converting to return type, if a ValueError Arises then return zero.
    """
    try:
        return return_type(value)
    except ValueError:
        return 0


def index_modifier(index, modifier, index_mod=0):
    """
    Modify and index based on the sub division, whilst also allow to modify the current index by an int
    """
    return (index + index_mod) + ((index + index_mod) * modifier)


def index_range(index, modifier, inclusive=True):
    """
    Create the iterable range of values from the current index base on a modifier

    Example
    --------
    index = 0
    modifier = 3

    0 + 0 * 3 = 0

    The plus 1 is their because range is NOT inclusive yet we need it to be, can be turned off
    (1 + (1 * 3)) + 1 = 5
    """

    if inclusive:
        return range(index_modifier(index, modifier), index_modifier(index, modifier, 1) + 1)
    else:
        return range(index_modifier(index, modifier), index_modifier(index, modifier, 1))


@contextmanager
def suppress_stdout():
    """
    Suppress print statements

    Note
    ----
    Sometimes external packages will prints every step which can end up cluttering .log's or terminal output. This will
    silence it.

    Source: https://stackoverflow.com/questions/2125702/how-to-suppress-console-output-in-python

    Example
    -------
    >>> print("You can't silence me!")
    >>> with suppress_stdout():
    >>>     print("...or maybe not")



    """
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
