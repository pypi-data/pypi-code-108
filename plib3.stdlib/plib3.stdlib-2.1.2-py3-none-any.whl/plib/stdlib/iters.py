#!/usr/bin/env python3
"""
Module ITERS -- Tools for Iterators and Generators
Sub-Package STDLIB of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module supplements the ``itertools`` standard library
module. It currently provides the following:

function first_n -- generates first n items from iterable

    >>> list(first_n(1, range(2)))
    [0]
    >>> list(first_n(2, range(2)))
    [0, 1]
    >>> list(first_n(2, range(3)))
    [0, 1]
    >>> list(first_n(2, range(1)))
    [0]
    >>> list(first_n(1, range(0)))
    []

function split_n -- returns tuple (first n items, rest of items)
from iterable
    
    >>> split_n(1, list(range(3)))
    ([0], [1, 2])
    >>> split_n(1, list(range(2)))
    ([0], [1])
    >>> split_n(1, list(range(1)))
    ([0], [])
    >>> split_n(2, list(range(5)))
    ([0, 1], [2, 3, 4])
    >>> split_n(2, list(range(4)))
    ([0, 1], [2, 3])
    >>> split_n(2, list(range(3)))
    ([0, 1], [2])
    >>> split_n(2, list(range(2)))
    ([0, 1], [])
    >>> split_n(2, list(range(1)))
    ([0], [])
    >>> split_n(0, list(range(1)))
    ([], [0])
    >>> split_n(-1, list(range(2)))
    ([0], [1])
    >>> split_n(-1, list(range(1)))
    ([], [0])
    >>> split_n(2, [])
    ([], [])
    >>> split_n(1, [])
    ([], [])
    >>> split_n(0, [])
    ([], [])
    >>> split_n(-1, [])
    ([], [])

Iterables that don't support slicing can't be split at
negative indexes

    >>> from itertools import count
    >>> it = islice(count(), 2)
    >>> split_n(2, it)
    ([0, 1], [])
    >>> it = islice(count(), 2)
    >>> split_n(1, it)
    ([0], [1])
    >>> it = islice(count(), 2)
    >>> split_n(0, it)
    ([], [0, 1])
    >>> it = islice(count(), 2)
    >>> split_n(-1, it)
    Traceback (most recent call last):
     ...
    ValueError: can't split iterable at negative index

function pairwise -- generates items from iterable in pairs

    >>> list(pairwise(range(3)))
    [(0, 1), (1, 2)]
    >>> list(pairwise(range(2)))
    [(0, 1)]
    >>> list(pairwise(range(1)))
    []
    >>> list(pairwise(range(0)))
    []

function n_wise -- generates items from iterable in n-tuples; n = 2
is equivalent to pairwise; note that n = 1 converts a list of elements
into a list of 1-tuples; also note that n = 0 raises ValueError

    >>> list(n_wise(3, range(6)))
    [(0, 1, 2), (1, 2, 3), (2, 3, 4), (3, 4, 5)]
    >>> list(n_wise(3, range(5)))
    [(0, 1, 2), (1, 2, 3), (2, 3, 4)]
    >>> list(n_wise(3, range(4)))
    [(0, 1, 2), (1, 2, 3)]
    >>> list(n_wise(3, range(3)))
    [(0, 1, 2)]
    >>> list(n_wise(4, range(6)))
    [(0, 1, 2, 3), (1, 2, 3, 4), (2, 3, 4, 5)]
    >>> list(n_wise(4, range(5)))
    [(0, 1, 2, 3), (1, 2, 3, 4)]
    >>> list(n_wise(4, range(4)))
    [(0, 1, 2, 3)]
    >>> list(n_wise(2, range(2)))
    [(0, 1)]
    >>> list(n_wise(2, range(1)))
    []
    >>> list(n_wise(2, range(0)))
    []
    >>> list(n_wise(1, range(1)))
    [(0,)]
    >>> list(n_wise(1, range(0)))
    []
    >>> list(n_wise(0, range(0)))
    Traceback (most recent call last):
    ...
    ValueError: n_wise requires n > 0
    >>> list(n_wise(0, range(1)))
    Traceback (most recent call last):
    ...
    ValueError: n_wise requires n > 0

function end_pairs -- generates pairs of items from ends of sequence, working inwards

    >>> list(end_pairs(list(range(5))))
    [(0, 4), (1, 3), (2,)]
    >>> list(end_pairs(list(range(4))))
    [(0, 3), (1, 2)]
    >>> list(end_pairs(list(range(3))))
    [(0, 2), (1,)]
    >>> list(end_pairs(list(range(2))))
    [(0, 1)]
    >>> list(end_pairs(list(range(1))))
    [(0,)]
    >>> list(end_pairs(list(range(0))))
    []
    
    >>> list(end_pairs(list(range(5)), include_odd=False))
    [(0, 4), (1, 3)]
    >>> list(end_pairs(list(range(4)), include_odd=False))
    [(0, 3), (1, 2)]
    >>> list(end_pairs(list(range(3)), include_odd=False))
    [(0, 2)]
    >>> list(end_pairs(list(range(2)), include_odd=False))
    [(0, 1)]
    >>> list(end_pairs(list(range(1)), include_odd=False))
    []
    >>> list(end_pairs(list(range(0)), include_odd=False))
    []
    
    >>> list(end_pairs(list(range(5)), pad_odd_with=None))
    [(0, 4), (1, 3), (2, None)]
    >>> list(end_pairs(list(range(4)), pad_odd_with=None))
    [(0, 3), (1, 2)]
    >>> list(end_pairs(list(range(3)), pad_odd_with=None))
    [(0, 2), (1, None)]
    >>> list(end_pairs(list(range(2)), pad_odd_with=None))
    [(0, 1)]
    >>> list(end_pairs(list(range(1)), pad_odd_with=None))
    [(0, None)]
    >>> list(end_pairs(list(range(0)), pad_odd_with=None))
    []

function partitions -- generates all partitions of a sequence or set

    >>> list(partitions(list(range(3))))
    [([0], [1, 2]), ([1], [0, 2]), ([2], [0, 1])]

function subsequences -- generates all subsequences of a sequence,
from shortest to longest

    >>> list(subsequences(list(range(2))))
    [[0], [1], [0, 1]]
    >>> list(subsequences(list(range(3))))
    [[0], [1], [2], [0, 1], [1, 2], [0, 1, 2]]
    >>> list(subsequences(list(range(1))))
    [[0]]
    >>> list(subsequences(list(range(0))))
    []

function inverse_subsequences -- generates all subsequences of a sequence,
from longest to shortest

    >>> list(inverse_subsequences(list(range(3))))
    [[0, 1, 2], [0, 1], [1, 2], [0], [1], [2]]
    >>> list(inverse_subsequences(list(range(2))))
    [[0, 1], [0], [1]]
    >>> list(inverse_subsequences(list(range(1))))
    [[0]]
    >>> list(inverse_subsequences(list(range(0))))
    []

function cyclic_permutations -- generates cyclic permutations of iterable

    >>> list(cyclic_permutations(range(3)))
    [(0, 1, 2), (1, 2, 0), (2, 0, 1)]
    >>> list(cyclic_permutations(range(2)))
    [(0, 1), (1, 0)]
    >>> list(cyclic_permutations(range(1)))
    [(0,)]
    >>> list(cyclic_permutations(range(0)))
    []

function unique_permutations -- generates cyclically unique permutations
of iterable with given length r; if r is greater than the length of
iterable, the generator is empty; if r = 0, one empty permutation is
generated (since there is only one 0-length permutation)

    >>> list(unique_permutations(range(2), 2))
    [(0, 1)]
    >>> list(unique_permutations(range(2), 3))
    []
    >>> list(unique_permutations(range(3), 2))
    [(0, 1), (0, 2), (1, 2)]
    >>> list(unique_permutations(range(3), 3))
    [(0, 1, 2), (0, 2, 1)]
    >>> list(unique_permutations(range(3), 4))
    []
    >>> list(unique_permutations(range(3), 1))
    [(0,), (1,), (2,)]
    >>> list(unique_permutations(range(2), 1))
    [(0,), (1,)]
    >>> list(unique_permutations(range(1), 1))
    [(0,)]
    >>> list(unique_permutations(range(1), 2))
    []
    >>> list(unique_permutations(range(0), 1))
    []
    >>> list(unique_permutations(range(0), 0))
    [()]
    >>> list(unique_permutations(range(1), 0))
    [()]
    >>> list(unique_permutations(range(2), 0))
    [()]
    >>> list(unique_permutations(range(3), 0))
    [()]

function unique_permutations_with_replacement -- generates cyclically
unique permutations of iterable where repeated elements are allowed

    >>> list(unique_permutations_with_replacement(range(2), 2))
    [(0, 0), (0, 1), (1, 1)]
    >>> list(unique_permutations_with_replacement(range(2), 3))
    [(0, 0, 0), (0, 0, 1), (0, 1, 1), (1, 1, 1)]
    >>> list(unique_permutations_with_replacement(range(2), 1))
    [(0,), (1,)]
    >>> list(unique_permutations_with_replacement(range(1), 1))
    [(0,)]
    >>> list(unique_permutations_with_replacement(range(1), 2))
    [(0, 0)]
    >>> list(unique_permutations_with_replacement(range(1), 0))
    [()]

function unzip -- inverse of the zip builtin, splits sequence of tuples
into multiple sequences

    >>> unzip(list(zip(list(range(3)), list(range(3)))))
    ([0, 1, 2], [0, 1, 2])
    >>> unzip(list(zip(list(range(3)), list(range(3)), list(range(3)))))
    ([0, 1, 2], [0, 1, 2], [0, 1, 2])
    >>> unzip(list(zip(list(range(1)), list(range(1)))))
    ([0], [0])
    >>> unzip(list(zip(list(range(0)), list(range(0)))))
    ()

function group_into -- Generate tuples of every n elements of iterable

    >>> list(group_into(2, range(10)))
    [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9)]
    >>> list(group_into(3, range(10)))
    [(0, 1, 2), (3, 4, 5), (6, 7, 8)]
    >>> list(group_into(3, range(10), include_tail=True))
    [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9,)]
    >>> list(group_into(3, range(10), include_tail=True, fill_tail=True))
    [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9, None, None)]
    >>> list(group_into(1, range(2)))
    [(0,), (1,)]
    >>> list(group_into(1, range(1)))
    [(0,)]
    >>> list(group_into(2, range(1)))
    []
    >>> list(group_into(2, range(1), include_tail=True))
    [(0,)]
    >>> list(group_into(2, range(1), include_tail=True, fill_tail=True, fillvalue=-1))
    [(0, -1)]
    >>> list(group_into(2, range(1), raise_if_tail=True))
    Traceback (most recent call last):
     ...
    ValueError: extra terms in grouped iterable
    >>> list(group_into(0, range(1)))
    Traceback (most recent call last):
     ...
    ValueError: can't group iterable into 0-element tuples
    >>> list(group_into(1, range(0)))
    []
    >>> list(group_into(1, range(0), include_tail=True))
    []
    >>> list(group_into(1, range(0), include_tail=True, fill_tail=True))
    []
    >>> list(group_into(2, range(0)))
    []
    >>> list(group_into(2, range(0), include_tail=True))
    []
    >>> list(group_into(2, range(0), include_tail=True, fill_tail=True))
    []
    
    >>> list(group_into(2, list(range(4))))
    [(0, 1), (2, 3)]
    >>> list(group_into(2, list(range(4)), include_tail=True))
    [(0, 1), (2, 3)]
    >>> list(group_into(2, list(range(4)), include_tail=True, fill_tail=True))
    [(0, 1), (2, 3)]
    >>> list(group_into(3, list(range(4))))
    [(0, 1, 2)]
    >>> list(group_into(3, list(range(4)), include_tail=True))
    [(0, 1, 2), (3,)]
    >>> list(group_into(3, list(range(4)), include_tail=True, fill_tail=True))
    [(0, 1, 2), (3, None, None)]
    >>> list(group_into(4, list(range(4))))
    [(0, 1, 2, 3)]
    >>> list(group_into(4, list(range(4)), include_tail=True))
    [(0, 1, 2, 3)]
    >>> list(group_into(4, list(range(4)), include_tail=True, fill_tail=True))
    [(0, 1, 2, 3)]
    >>> list(group_into(5, list(range(4))))
    []
    >>> list(group_into(5, list(range(4)), include_tail=True))
    [(0, 1, 2, 3)]
    >>> list(group_into(5, list(range(4)), include_tail=True, fill_tail=True))
    [(0, 1, 2, 3, None)]
    >>> list(group_into(2, list(range(6)), include_tail=True))
    [(0, 1), (2, 3), (4, 5)]
    >>> list(group_into(3, list(range(6)), include_tail=True))
    [(0, 1, 2), (3, 4, 5)]
    >>> list(group_into(4, list(range(6)), include_tail=True))
    [(0, 1, 2, 3), (4, 5)]
    >>> list(group_into(5, list(range(6)), include_tail=True))
    [(0, 1, 2, 3, 4), (5,)]
    >>> list(group_into(6, list(range(6)), include_tail=True))
    [(0, 1, 2, 3, 4, 5)]
    >>> list(group_into(7, list(range(6)), include_tail=True))
    [(0, 1, 2, 3, 4, 5)]
    >>> list(group_into(1, list(range(4)), include_tail=True))
    [(0,), (1,), (2,), (3,)]
    >>> list(group_into(1, list(range(1)), include_tail=True))
    [(0,)]
    >>> list(group_into(2, list(range(1)), include_tail=True))
    [(0,)]
    >>> list(group_into(2, list(range(1)), include_tail=True, fill_tail=True))
    [(0, None)]

function interleave -- interleaves iterables

    >>> list(interleave("abc", "d", "ef"))
    ['a', 'd', 'e', 'b', 'f', 'c']
    >>> list(interleave("abc", "defg"))
    ['a', 'd', 'b', 'e', 'c', 'f', 'g']
    >>> list(interleave("abc", "defg", "hi"))
    ['a', 'd', 'h', 'b', 'e', 'i', 'c', 'f', 'g']
    >>> list(interleave("abc"))
    ['a', 'b', 'c']
    >>> list(interleave())
    []

function inverse_index -- index of item counting from end of sequence

    >>> inverse_index(list(range(3)), 0)
    2
    >>> inverse_index(list(range(3)), 1)
    1
    >>> inverse_index(list(range(3)), 2)
    0
    >>> inverse_index(list(range(3)), 3)
    Traceback (most recent call last):
     ...
    ValueError: 3 is not in list

function is_subsequence -- tests if one sequence is subsequence of another

    >>> is_subsequence(list(range(2)), list(range(3)))
    True
    >>> is_subsequence(list(range(3)), list(range(1, 3)))
    False
    >>> is_subsequence(list(range(1, 2)), list(range(1, 3)))
    True
    >>> is_subsequence(list(range(1)), list(range(2)))
    True
    >>> is_subsequence(list(range(1)), list(range(1, 2)))
    False
    >>> is_subsequence(list(range(0)), list(range(1)))
    True
    >>> is_subsequence(list(range(0)), list(range(0)))
    True
    >>> is_subsequence(list(range(3)), list(range(2)))
    False
    >>> is_subsequence(list(range(1)), list(range(0)))
    False

function count_matches -- returns mapping of unique elements in sequence
to number of times they appear

    >>> sorted(count_matches(list(range(1))).items())
    [(0, 1)]
    >>> sorted(count_matches(list(range(2))).items())
    [(0, 1), (1, 1)]
    >>> sorted(count_matches(list(range(2)) * 2).items())
    [(0, 2), (1, 2)]
    >>> sorted(count_matches(list(range(2)) * 2 + [1]).items())
    [(0, 2), (1, 3)]
    >>> sorted(count_matches(list(range(2)) * 2 + [2]).items())
    [(0, 2), (1, 2), (2, 1)]
    >>> sorted(count_matches(list(range(0))).items())
    []
    >>> sorted(count_matches('abracadabra').items())
    [('a', 5), ('b', 2), ('c', 1), ('d', 1), ('r', 2)]

function sorted_unzip -- returns two sequences from mapping, of keys and
values, in corresponding order, sorted by key or value

    >>> sorted_unzip(dict((i, chr(ord('a') + i)) for i in range(5)))
    ([0, 1, 2, 3, 4], ['a', 'b', 'c', 'd', 'e'])
    >>> sorted_unzip(dict((i, chr(ord('a') + i)) for i in range(5)), by_value=True)
    ([0, 1, 2, 3, 4], ['a', 'b', 'c', 'd', 'e'])
    >>> sorted_unzip(dict((i, chr(ord('a') + i)) for i in range(5)), reverse=True)
    ([4, 3, 2, 1, 0], ['e', 'd', 'c', 'b', 'a'])
    >>> sorted_unzip(dict((i, chr(ord('a') + i)) for i in range(5)), by_value=True, reverse=True)
    ([4, 3, 2, 1, 0], ['e', 'd', 'c', 'b', 'a'])
    >>> sorted_unzip(dict((4 - i, chr(ord('a') + i)) for i in range(5)))
    ([0, 1, 2, 3, 4], ['e', 'd', 'c', 'b', 'a'])
    >>> sorted_unzip(dict((4 - i, chr(ord('a') + i)) for i in range(5)), by_value=True)
    ([4, 3, 2, 1, 0], ['a', 'b', 'c', 'd', 'e'])
    >>> sorted_unzip(dict((4 - i, chr(ord('a') + i)) for i in range(5)), reverse=True)
    ([4, 3, 2, 1, 0], ['a', 'b', 'c', 'd', 'e'])
    >>> sorted_unzip(dict((4 - i, chr(ord('a') + i)) for i in range(5)), by_value=True, reverse=True)
    ([0, 1, 2, 3, 4], ['e', 'd', 'c', 'b', 'a'])

functions prefixed_items and suffixed_items -- return items from iterable of
strings that have a given prefix or suffix

    >>> list(prefixed_items(['a_1', 'a_2', 'b_3', 'c_4', 'a_5', 'd_6'], 'a_'))
    ['1', '2', '5']
    >>> list(prefixed_items(['a_1', 'a_2', 'b_3', 'c_4', 'a_5', 'd_6'], 'a_', full=True))
    ['a_1', 'a_2', 'a_5']
    >>> list(suffixed_items(['a_1', 'a_2', 'b_1', 'c_2', 'a_3', 'd_4'], '_2'))
    ['a', 'c']
    >>> list(suffixed_items(['a_1', 'a_2', 'b_1', 'c_2', 'a_3', 'd_4'], '_2', full=True))
    ['a_2', 'c_2']
    >>> list(prefixed_items(['a', 'b', 'c'], ''))
    ['a', 'b', 'c']
    >>> list(prefixed_items(['a', 'b', 'c'], '', full=True))
    ['a', 'b', 'c']
    >>> list(suffixed_items(['a', 'b', 'c'], ''))
    ['a', 'b', 'c']
    >>> list(suffixed_items(['a', 'b', 'c'], '', full=True))
    ['a', 'b', 'c']
    >>> list(prefixed_items(['b', 'c'], 'a'))
    []
    >>> list(prefixed_items(['b', 'c'], 'a', full=True))
    []
    >>> list(suffixed_items(['b', 'c'], 'a'))
    []
    >>> list(suffixed_items(['b', 'c'], 'a', full=True))
    []
    >>> list(prefixed_items([], 'a'))
    []
    >>> list(prefixed_items([], 'a', full=True))
    []
    >>> list(suffixed_items([], 'a'))
    []
    >>> list(suffixed_items([], 'a', full=True))
    []
    >>> list(prefixed_items([], ''))
    []
    >>> list(prefixed_items([], '', full=True))
    []
    >>> list(suffixed_items([], ''))
    []
    >>> list(suffixed_items([], '', full=True))
    []

function range_lookup -- returns first match from sequence of comparison range
boundaries

    >>> lookup_items = [(1, 'a'), (3, 'b'), (7, 'c'), (None, 'd')]
    >>> [range_lookup(lookup_items, i) for i in range(10)]
    ['a', 'a', 'b', 'b', 'c', 'c', 'c', 'c', 'd', 'd']
    >>> lookup_items = [(1, 'a'), (3, 'b'), (7, 'c')]
    >>> [range_lookup(lookup_items, i) for i in range(10)]
    ['a', 'a', 'b', 'b', 'c', 'c', 'c', 'c', None, None]
    >>> lookup_items = [1, 3, 7, None]
    >>> [range_lookup(lookup_items, i, key_value=True) for i in range(10)]
    [1, 1, 3, 3, 7, 7, 7, 7, None, None]
    >>> [range_lookup(lookup_items, i, index_value=True) for i in range(10)]
    [0, 0, 1, 1, 2, 2, 2, 2, 3, 3]
    >>> lookup_items = [1, 3, 7]
    >>> [range_lookup(lookup_items, i, key_value=True) for i in range(10)]
    [1, 1, 3, 3, 7, 7, 7, 7, None, None]
    >>> [range_lookup(lookup_items, i, index_value=True) for i in range(10)]
    [0, 0, 1, 1, 2, 2, 2, 2, None, None]

The default comparison is ``operator.le``, but this can be changed (note
that we can reference the ``lt`` function because it's imported into this
module)

    >>> lookup_items = [(1, 'a'), (3, 'b'), (7, 'c'), (None, 'd')]
    >>> [range_lookup(lookup_items, i, cmpfunc=lt) for i in range(10)]
    ['a', 'b', 'b', 'c', 'c', 'c', 'c', 'd', 'd', 'd']

The function assumes that the comparison range sequence is sorted in the
order that makes sense for the chosen comparison operator; if the sort order
and comparison are mismatched, you can get weird results

    >>> [range_lookup(lookup_items, i, cmpfunc=gt) for i in range(10)]
    ['d', 'd', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a']
    >>> lookup_items = [(1, 'a'), (3, 'b'), (7, 'c')]
    >>> [range_lookup(lookup_items, i, cmpfunc=gt) for i in range(10)]
    [None, None, 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a']

Reversing the comparison range sequence might also give weird results if you
don't also reverse the order in which you compare values

    >>> [range_lookup(reversed(lookup_items), i, cmpfunc=gt) for i in range(10)]
    [None, None, 'a', 'a', 'b', 'b', 'b', 'b', 'c', 'c']
    >>> [range_lookup(reversed(lookup_items), i, cmpfunc=gt) for i in range(10, 0, -1)]
    ['c', 'c', 'c', 'b', 'b', 'b', 'b', 'a', 'a', None]

If you don't give a default, the default result is ``None``; note that this
includes lookups into empty sequence

    >>> range_lookup([], 0) is None
    True
    >>> range_lookup([], 0, key_value=True) is None
    True
    >>> range_lookup([], 0, index_value=True) is None
    True
    >>> range_lookup([], 0, cmpfunc=lt) is None
    True

"""

from itertools import (
    chain, groupby,
    combinations, combinations_with_replacement, cycle, islice,
    permutations, takewhile, tee, zip_longest
)
from operator import le, lt, gt

from plib.stdlib.builtins import first


# Iterable functions

def sorted_groupby(iterable, key=None):
    # Encapsulates a useful idiom
    return groupby(sorted(iterable, key=key), key)


def first_n(n, iterable):
    # More intuitive spelling for this usage of islice
    return islice(iterable, n)


def split_n(n, iterable):
    # Return a tuple (first n items, rest of items) from iterable
    try:
        # If iterable supports slicing, we're home
        return iterable[:n], iterable[n:]
    except TypeError:
        pass
    if n < 0:
        raise ValueError("can't split iterable at negative index")
    it = iter(iterable)
    return list(islice(it, n)), list(it)


def pairwise(iterable):
    # s -> (s0,s1), (s1,s2), (s2, s3), ...
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def n_wise(n, iterable):
    # Return items from iterable in groups of n
    if n <= 0:
        raise ValueError("n_wise requires n > 0")
    iters = []
    a = iterable
    for _ in range(n - 1):
        a, b = tee(a)
        iters.append(a)
        next(b, None)
        a = b  # this makes sure append(a) below gets the right iterable
    iters.append(a)  # this takes care of the n = 1 case as well
    return zip(*iters)


_end_pairs_sentinel = object()

def end_pairs(seq, include_odd=True, pad_odd_with=_end_pairs_sentinel):
    """Yield pairs from ends of seq, working inward.
    
    Last "pair" may be a 1-element tuple instead of 2 if
    seq has an odd number of members. The include_odd
    keyword argument controls this behavior: if it's
    False, the odd "pair" is not yielded. The pad_odd_with
    keyword argument, if present, causes the odd "pair" to
    be padded with that object so it has 2 elements.
    """
    q, r = divmod(len(seq), 2)
    for i in range(q):
        yield (seq[i], seq[-(i + 1)])
    if r:
        if include_odd:
            yield (
                (seq[q],) if pad_odd_with is _end_pairs_sentinel
                else (seq[q], pad_odd_with)
            )


def partitions(s):
    # Generate all pairs of non-empty subsets that partition s
    itemcount = len(s)
    for n in range(1, (itemcount // 2) + 1):
        for indexes in combinations(range(itemcount), n):
            p = [s[i] for i in indexes]
            o = [s[j] for j in range(itemcount) if j not in indexes]
            yield p, o


def _subseq(sequence, step=0):
    length = len(sequence)
    indexes = (0, length)
    start = indexes[step] + 1 + step
    stop = indexes[1 + step] + 1 + step
    step = step or 1
    for current in range(start, stop, step):
        for i in range(length - current + 1):
            yield sequence[i:i + current]


def subsequences(sequence):
    # Generate all subsequences of sequence, starting with
    # the shortest and ending with the sequence itself
    return _subseq(sequence)


def inverse_subsequences(sequence):
    # Generate all subsequences of sequence, starting with
    # the longest (which is just the sequence itself)
    return _subseq(sequence, -1)


def cyclic_permutations(iterable):
    # Generate just the cyclic permutations of iterable
    # (all permutations are the same length as iterable)
    # cyclic_permutations('123') -> '123', '231', '312'
    pool = tuple(iterable)
    seen = {}  # FIXME: get rid of this?
    r = len(pool)
    s = pool + pool
    for i in range(r):
        p = s[i:i + r]
        if p not in seen:
            seen[p] = p
            yield p


def unique_permutations(iterable, r):
    # Generate all cyclically unique r-length permutations of iterable
    pool = tuple(iterable)
    seen = {}  # FIXME: get rid of this?
    for c in combinations(pool, r):
        car, cdr = c[:1], c[1:]
        for p in permutations(cdr):
            u = car + p
            if u not in seen:
                for t in cyclic_permutations(u):
                    seen[t] = u
                yield u


def unique_permutations_with_replacement(iterable, r):
    # Generate all cyclically unique r-length permutations of iterable,
    # where elements can be repeated
    pool = tuple(iterable)
    seen = {}  # FIXME: get rid of this?
    s = len(pool)
    for i in range(min(r, s) + 1):
        for c in combinations(pool, i):
            for p in combinations_with_replacement(pool, r - i):
                for u in unique_permutations(c + p, r):
                    if u not in seen:
                        for t in cyclic_permutations(u):
                            seen[t] = u
                        yield u


def unzip(iterable):
    # Unzip iterable into multiple sequences; assumes iterable
    # contains tuples that are all of the same length.
    return tuple(map(list, zip(*iterable)))


def group_into(n, iterable,
               include_tail=False, fill_tail=False,
               fillvalue=None, raise_if_tail=False):
    # Return tuples of every n elements of iterable
    # If include_tail is True, yield a last tuple of less than n
    # elements from iterable if present, filled out with fillvalue
    # if fill_tail is True; otherwise, if raise_if_tail is True,
    # raise ValueError if extra elements are present
    if n < 1:
        raise ValueError("can't group iterable into 0-element tuples")
    args = [iter(iterable)] * n
    sentinel = object()
    for group in zip_longest(*args, fillvalue=sentinel):
        if group[-1] is not sentinel:
            yield group
        elif include_tail:
            tail = tuple(takewhile(lambda g: g is not sentinel, group))
            if fill_tail:
                tail += (fillvalue,) * (n - len(tail))
            yield tail
        elif raise_if_tail:
            raise ValueError("extra terms in grouped iterable")


def interleave(*iterables,
               cycle=cycle, islice=islice):
    
    # Recipe credited to George Sakkis
    num_active = len(iterables)
    nexts = cycle(iter(it).__next__ for it in iterables)
    while num_active:
        try:
            for next in nexts:
                yield next()
        except StopIteration:
            # Remove the iterator we just exhausted from the cycle.
            num_active -= 1
            nexts = cycle(islice(nexts, num_active))


# Test and count functions

def inverse_index(seq, elem):
    # Return inverse index of elem in seq (i.e., first element
    # of seq has highest index, down to 0 for last element)
    return len(seq) - seq.index(elem) - 1


def is_subsequence(s, seq):
    # Test if s is a subsequence of seq
    slen = len(s)
    for i in range(len(seq) - slen + 1):
        if s == seq[i:i + slen]:
            return True
    return False


# Mapping <=> sequence functions

def count_matches(seq):
    # Return dict of unique elements in seq vs. number of times they appear
    # Assumes all sequence elements are hashable
    results = {}
    for item in seq:
        results.setdefault(item, []).append(True)
    return dict((k, len(v)) for k, v in results.items())


def sorted_unzip(mapping, by_value=False, reverse=False):
    # Return list of keys and list of values from mapping, both
    # sorted in corresponding order, by values if by_value is
    # True, by keys otherwise; reverse parameter governs the sort
    if by_value:
        unsorted_result = ((v, k) for k, v in mapping.items())
    else:
        unsorted_result = mapping.items()
    result = sorted(unsorted_result, reverse=reverse)
    r1, r2 = unzip(result)
    if by_value:
        return r2, r1
    return r1, r2


# Functions on iterables of strings

def prefixed_items(iterable, prefix, full=False):
    """Return items from iterable that start with prefix.
    
    The ``full`` argument controls whether the prefix itself is included
    in the returned items; the default is not to do so.
    
    Note that a zero-length prefix will result in every item of ``iterable``
    being yielded unchanged.
    """
    start = (len(prefix), 0)[full]
    return (item[start:] for item in iterable if item.startswith(prefix))


def suffixed_items(iterable, suffix, full=False):
    """Return items from iterable that end with suffix.
    
    The ``full`` argument controls whether the suffix itself is included
    in the returned items; the default is not to do so.
    
    Note that Python's indexing semantics make this case a bit different from
    the prefix case; item[:-0] doesn't have the corresponding effect to item[0:].
    Also we have to put the ``or None`` check in to allow for a zero-length
    suffix (which should result in every item in the iterable being yielded
    unchanged, as with ``prefixed_items`` above).
    """
    i = slice((-len(suffix) or None, None)[full])
    return (item[i] for item in iterable if item.endswith(suffix))


def range_lookup(items, value, key_value=False, index_value=False, cmpfunc=le):
    """Return lookup value for first matching key.
    
    If ``key`` is None, automatic match (this allows the last entry
    in ``items`` to be a default).
    
    The ``key_value`` parameter allows a simple sequence to be passed
    in instead of a sequence of tuples (such as the ``items()`` method
    of a ``dict``); the "value" for each key is then just the key itself.
    
    The ``index_value`` parameter works like ``key_value``, except that
    the "value" for each key is its index in the sequence.
    """
    lookup_items = (
        zip(items, items) if key_value
        else zip(items, range(len(items))) if index_value
        else items
    )
    return first(v for k, v in lookup_items if (k is None) or cmpfunc(value, k))


if __name__ == '__main__':
    import doctest
    doctest.testmod()
