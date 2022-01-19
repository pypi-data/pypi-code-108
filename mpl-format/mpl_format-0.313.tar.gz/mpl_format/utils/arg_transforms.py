from typing import Sized, Dict, Any, Callable


def smart_zip(*args):
    """
    Method to convert arguments into a zipped list.
    Similar to Python's built-in zip method but converts each non-Sized into
    a list so that it can be iterated over by the user without explicitly
    checking its type.

    :param args: Each arg should be a single value or a Sized of values. Sized
                 args which are shorter than the longest Sized will be repeated
                len(Sized) times like any non-Sized arg. Dicts are treated as
                non-Sizeds.
    """
    max_arg_length = 1
    values = []
    # find longest sized arg
    for arg in args:
        if (
                isinstance(arg, Sized) and
                not isinstance(arg, dict) and
                not isinstance(arg, str)
        ):
            arg_length = len(arg)
            if arg_length > max_arg_length:
                max_arg_length = arg_length
    # create values
    for arg in args:
        if (
                isinstance(arg, Sized) and
                not isinstance(arg, dict) and
                not isinstance(arg, str) and
                len(arg) == max_arg_length
        ):
            values.append(arg)
        else:
            values.append([arg] * max_arg_length)
    for value_set in zip(*values):
        yield value_set


def smart_zip_kwargs(**kwargs):
    """
    Takes kwargs, passes the args into smart_zip and yields dicts mapping kws to
    zipped arg values.

    :param kwargs: Keys and values. Values passed into smart_zip.
    :return:
    """
    keys = list(kwargs.keys())
    values = list(kwargs.values())
    for value_set in smart_zip(*values):
        out_dict = {
            key: value for key, value in zip(keys, value_set)
        }
        yield out_dict


def drop_none_values(items: dict) -> dict:
    """
    Return a copy of the dictionary without any keys or values where the value
    is None.
    """
    return {
        key: value for key, value in items.items()
        if value is not None
    }


def apply_mappings(items: Dict[str, Any],
                   mappings: Dict[str, Callable]) -> Dict[str, Any]:
    """
    Return a copy of the dictionary with any items with a key in mappings
    transformed by the callable value associated with that key.

    :param items: dict of items to transform
    :param mappings: dict of mappings.
    """
    return {
        key: mappings[key](value) if key in mappings.keys() else value
        for key, value in items.items()
    }
