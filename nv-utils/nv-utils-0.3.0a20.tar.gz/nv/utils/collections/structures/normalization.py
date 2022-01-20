from typing import Any, Collection, List, Iterator, Mapping, Dict, Iterable

from nv.utils.collections.sets import OrderedSet


__ALL__ = ["extract_headers", "normalize", "check_normalized", "normalize_row", ]


def check_normalized(data: Iterable[Mapping[str, Any]], headers: Collection[str] = None) -> bool:
    """
    Checks if a list of dictionaries is normalized.
    :param data: Iterable with dictionaries or dataclasses
    :param headers: Collection of strings with headers. If None, headers are extracted from the first row.
    :return: True if all rows have the same keys, False otherwise.
    """
    headers = set(headers) if headers else None
    for row in data:
        this_headers = set(row.keys())

        # First header
        if headers is None:
            headers = this_headers
            continue

        if this_headers != headers:
            return False

    return True


def extract_headers(data: Iterable[Mapping[str, Any]], preserve_order: bool = True) -> List[str]:
    """
    Extracts all keys from a list of dictionaries. If preserve_order is True, the algorithm tries to preserve the
    natural order of keys (as dictionaries are ordered since Python 3.6+ and column headers tends to have some
    organization logic behind its order). Set it to false for a quicker execution that does not attempt to preserve
    natural order.
    :param data: data as an iterable of key-value dictionaries.
    :param preserve_order:
    :return:
    """
    headers = None
    natural_order = False

    for row in data:
        this_headers = OrderedSet(row.keys()) if natural_order else set(row.keys())

        # First header
        if headers is None:
            headers = this_headers
            natural_order = True
            continue

        # Straight forward implementation of headers
        if not preserve_order:
            headers = headers | this_headers
            continue

        # Order preservation heuristics
        extra_items = this_headers - headers
        missing_items = headers - this_headers

        if not missing_items and (extra_items or not natural_order):
            # Either a superset of current headers or a natural equal was found
            headers = this_headers
            natural_order = True
            continue

        if extra_items:
            # Stack up extra items and continue to look for a better natural proxy
            headers = headers | extra_items
            natural_order = False

    return list(headers)


def normalize_row(row: Mapping[str, Any], headers: Collection[str], default: Any = None) -> Dict[str, Any]:
    """
    Normalizes a single dictionary, so that all items in the list have same keys by setting non-existent fields to
    default.
    :param row: dictionary.
    :param headers: collection of strings with headers (order will be preserved if possible).
    :param default: default value to be set to non-existent items (typically either None or empty string)
    :return: normalized copy of dictionary.
    """
    return {k: row.get(k, default) for k in headers}


def iter_normalize(data: Iterable[Mapping[str, Any]], headers: Collection[str] | None = None, default: Any = None,
                   ) -> Iterator[Dict[str, Any]]:
    for row in data:
        yield normalize_row(row, headers, default)


def normalize(data: Iterable[Mapping[str, Any]], headers: Collection[str] = None,
              default: Any = None) -> List[Dict[str, Any]]:
    """
    Normalizes a list of dictionaries, so that all items in the list have same keys by setting non-existent fields to
    default.
    :param data: list of dictionaries.
    :param headers: collection of strings with headers (order will be preserved if possible).
    :param default: default value to be set to non existent items (typically either None or empty string)
    :return: normalized copy of list.
    """
    if not headers:
        raise ValueError("Headers are required to normalize data")

    return list(iter_normalize(data, headers, default))
