from collections.abc import Sequence

import pandas  # type: ignore


def get_list_shape(sequence, inner_types=(), shape=()):
    """
    returns the shape of nested lists similarly to numpy's shape.
    """
    if not isinstance(sequence, Sequence):
        return shape, inner_types

    if isinstance(sequence[0], Sequence):
        length = len(sequence[0])
        if not all(len(item) == length for item in sequence):
            raise ValueError("Lists with inconsistent shapes")
        types = ()
    else:

        types = ((next(type(v) for v in sequence if not pandas.isna(v))),)
    shape += (len(sequence),)
    shape, types = get_list_shape(sequence[0], inner_types=types, shape=shape)
    return shape, types


def is_valid_list_of_lists(lst):
    is_list_of_lists = all([isinstance(i, list) for i in lst])
    if not is_list_of_lists:
        return False
    lengths = [len(i) for i in lst]
    return lengths.count(lengths[0]) == len(lengths)
