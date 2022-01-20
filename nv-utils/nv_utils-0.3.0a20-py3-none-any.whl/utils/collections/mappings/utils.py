from typing import TypeVar, Callable, Mapping, MutableMapping

__ALL__ = ['split_dict', 'extract_from_dict']


K = TypeVar('K')
V = TypeVar('V')


def split_dict(d: Mapping[K, V], criteria: Callable[[K, V], bool]) -> tuple[dict[K, V], dict[K, V]]:
    """
    Splits a mapping in two dictionaries according to a callable criteria function.
    :param d: original mapping
    :param criteria: Callable that shall return True if (k,v) pair matches a desired criteria
    :return: tuple of dictionaries (d_true, d_false)
    """
    d_true, d_false = dict(), dict()
    for k, v in d.items():
        d_to_append = d_true if criteria(k, v) else d_false
        d_to_append[k] = v
    return d_true, d_false


def extract_from_dict(d: MutableMapping[K, V], criteria: Callable[[K, V], bool]) -> dict[K, V]:
    """
    Filters out items that match a criteria function from a MutableMapping. Use split_dict if you want
    to avoid mutating the original mapping.
    :param d: original mapping (will be mutated)
    :param criteria: Callable that returns True if (k,v) pair matches a desired criteria
    :return: dictionary containing filtered out items
    """
    filtered_dict = dict()

    filtered_keys = [k for k, v in d.items() if criteria(k, v)]

    for k in filtered_keys:
        filtered_dict[k] = d.pop(k)

    return filtered_dict
