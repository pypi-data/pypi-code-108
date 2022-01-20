from collections.abc import Mapping, Sequence, Set, MutableSet, MutableSequence, MutableMapping, Collection
from functools import partial
from itertools import chain
from typing import TypeVar, Type

from nv.utils.typing import BASIC_TYPES, BASIC_SEQUENCES, MISSING, Missing


__ALL__ = ['merge']


K = TypeVar('K')
T = TypeVar('T')
V = TypeVar('V')


def merge_mappings(previous: Mapping[K, T],
                   current: Mapping[K, V],
                   _type: Type = dict) -> Mapping[K, T | V | None]:

    result = dict(previous) if previous else dict()

    for k, current_value in current.items():
        previous_value = result.get(k, MISSING)
        result[k] = merge(previous_value, current_value) if current_value is not MISSING else previous_value
    return _type(result)


def merge_sets(previous: Set[T],
               current: Set[V],
               _type: Type = set) -> Set[T | V | None]:
    """
    In order to apply the merge element to each element of the set, some extra work is required. The extra work is
    valid when you want to enforce that merge runs on each element that compares equal, and you want to keep
    whichever merge results (in the base case, the current prevails over the previous). If you want to move out of
    this technicality and just merge the sets fastly, use merge_simple_sets instead.
    """
    if previous and (not isinstance(previous, Collection) or isinstance(previous, BASIC_SEQUENCES)):
        raise TypeError(f'unable to cast {type(previous)} into a set (or may result in an unexpected behaviour)')

    previous = set(previous) if previous else set()
    current_list = list(current)
    new_items = current - previous
    results = set()

    for previous_item in previous:
        if previous_item in current:
            current_item = current_list[current_list.index(previous_item)]
            merged_item = merge(previous_item, current_item)
            results.add(merged_item)
        else:
            results.add(previous_item)

    results.update(new_items)
    return _type(results)


def merge_simple_sets(previous: Set[T],
                      current: Set[V],
                      _type: Type = set) -> Set[T | V | None]:
    """
    This is a simple function to merge sets. It does not apply the merge element to each element of the set, and
    returns, at least in CPython's implementation, a set in which current elements prevail over previous elements when
    they match equal. If you want to control the element behaviour, use merge_sets instead.
    """
    if previous and (not isinstance(previous, Collection) or isinstance(previous, BASIC_SEQUENCES)):
        raise TypeError(f'unable to cast {type(previous)} into a set (or may result in an unexpected behaviour)')

    previous = set(previous) if previous else set()
    return _type(current | previous)


def merge_sequences(previous: Sequence[T],
                    current: Sequence[V],
                    _type: Type = list) -> Sequence[T | V | None]:
    """
    Contrary to merging sets, merging sequences is a simple operation - the resulting sequence will be exactly what
    you would get from [*previous, *current]. No element matching is performed, as it is not required. If you want
    a different behaviour, feel free to write your own merge_sequences or use sets instead (which will deal with
    duplicates).
    """
    if previous and (not isinstance(previous, Collection) or isinstance(previous, BASIC_SEQUENCES)):
        raise TypeError(f'unable to cast {type(previous)} into a sequence (or may result in an unexpected behaviour)')

    previous = list(previous) if previous else list()
    return _type(chain(previous, current))


class MergeElements:
    class Behaviour:
        @staticmethod
        def keep_current(_, current):
            return current

        @staticmethod
        def keep_previous_if_current_is_false(previous, current):
            return (previous or current) if not current else current

        @staticmethod
        def keep_previous_if_current_is_none(previous, current):
            return previous if current is None else current

        @staticmethod
        def keep_previous_if_current_is_missing(previous, current):
            return previous if current is MISSING else current

        @staticmethod
        def raise_error(previous, current):
            raise TypeError(f"Don't know how to merge {type(current)} into {type(previous)}")


MERGE_ELEMENTS_MAP = (
    (BASIC_TYPES, MergeElements.Behaviour.keep_previous_if_current_is_none),
    (BASIC_SEQUENCES, MergeElements.Behaviour.keep_previous_if_current_is_false),
)


MERGE_COLLECTIONS_MAP = (
    (MutableSet, merge_sets),
    (Set, partial(merge_sets, _type=frozenset)),
    (MutableSequence, merge_sequences),
    (Sequence, partial(merge_sequences, _type=tuple)),
    (MutableMapping, merge_mappings),
)

MERGE_MAP = (
    *MERGE_ELEMENTS_MAP,
    *MERGE_COLLECTIONS_MAP,
)


def merge(previous: T,
          current: V,
          merge_map=MERGE_MAP,
          default=MergeElements.Behaviour.keep_previous_if_current_is_none) -> T | V | None:
    """
    Merge nested mappings, sequences, sets. The appropriate merger strategy is defined by checking if the current
    type is an instance of one of the types in the merge_map. If a match occurs, the appropriate merger function is
    called. If none is found, the default merger is called.

    For elements, the default strategy mapped is to keep the latest version of an element that differs from None. If it
    knows how to deal with the type of the current element, the previous will be discarded. If not, the default
    will be run. Same principle is applied to basic non-empty sequences (strings).  For collections, the default
    behaviour is implemented on the merger. All collection mergers try to coerce the type of previous into the type
    of current. Except for maps, which tries to coerce type to dicts (which are much more reluctant to accept anything),
    the other mergers will raise TypeError if they find something that seems to be a problem (e.g. coerce strings).

    """
    merge_type, merge_fn = next(((t, m) for t, m in merge_map if isinstance(current, t)), (MISSING, MISSING))

    if merge_type is MISSING or merge_fn is MISSING:
        return default(previous, current)

    return merge_fn(previous, current)
