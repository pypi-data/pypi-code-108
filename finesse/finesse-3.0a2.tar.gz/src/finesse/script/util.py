"""Kat script utility functions."""

from itertools import groupby
from collections import defaultdict


def index_ranges(intlist):
    """Create a sequence of range strings from a sequence of integers.

    Based on https://stackoverflow.com/a/9471386/2251982.

    Parameters
    ----------
    intlist : sequence
        Integers to convert to range strings.

    Yields
    ------
    str
        The next range string.

    Examples
    --------
    >>> list(index_ranges([1, 2, 4, 5, 6, 7, 9]))
    ["1-2", "4-7", "9"]
    """

    def sub(x):
        return x[1] - x[0]

    for k, iterable in groupby(enumerate(sorted(intlist)), sub):
        indices = list(iterable)
        if len(indices) == 1:
            yield str(indices[0][1])
        else:
            yield f"{indices[0][1]}-{indices[-1][1]}"


def scriptsorted(items, reverse=False):
    """Sort container items by their script position.

    Parameters
    ----------
    items : sequence of :class:`.TokenContainer`
        The container items to sort.

    reverse : bool, optional
        Request the result in descending instead of ascending order.

    Returns
    -------
    list of :class:`.TokenContainer`
        Container items sorted by line number then column.
    """
    return sorted(items, key=lambda item: item.start, reverse=reverse)


def duplicates(items, key=None):
    """Get duplicate keys and values in the 1D sequence `items`.

    Parameters
    ----------
    items : sequence
        The sequence to find duplicates in.

    key : callable, optional
        The key function to use for comparisons. If not specified, defaults to the
        identity function.

    Returns
    -------
    list
        The duplicates in `items`. This is a sequence of tuples containing the result
        of the key function for each entry of `items`, where at least two such keys
        exist, and the original items that matched that `key`.

    Examples
    --------
    >>> [k for k, _ in duplicates("AAAABBCDAAB")]
    ["A", "B", "C", "D"]

    >>> [list(g) for _, g in duplicates("AAAABBCDAAB")]
    [["A", "A", "A", "A", "A", "A"], ["B", "B", "B"], ["C"], ["D"]]
    """
    if key is None:
        key = lambda item: item
    groups = defaultdict(list)
    for item in items:
        groups[key(item)].append(item)
    return [(k, v) for k, v in groups.items() if len(v) > 1]


def merge_attributes(attr1, attr2):
    """Perform a deep attribute dictionary merge.

    This merges list and tuples in `attr1` and `attr2` into one dict. Values that are
    not lists or tuples result in an error. Items in `attr1` appear before those in
    `attr2` where they share the same key.

    Parameters
    ----------
    attr1, attr2 : dict
        The attribute dictionaries to merge.

    Returns
    -------
    dict
        The merged attribute dictionary.

    Raises
    ------
    ValueError
        If a dict value in `attr1` or `attr2` is not a list or tuple.
    """
    out = {}

    if attr2 is None:
        secondkeys = set()
    else:
        secondkeys = set(attr2)

    # Add keys in attr1 and optionally attr2.
    for key, value in attr1.items():
        if isinstance(value, list):
            value = [*value, *attr2.get(key, [])]
        elif isinstance(value, tuple):
            value = (*value, *attr2.get(key, ()))
        elif key in attr2:
            raise ValueError(
                f"don't know how to merge {type(value)} and {type(attr2[key])}"
            )

        out[key] = value
        secondkeys.discard(key)

    # Add keys only in attr2.
    for key in secondkeys:
        out[key] = attr2[key]

    return out
