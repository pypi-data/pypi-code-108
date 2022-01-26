#!/usr/bin/python
"""\
@file   toposort.py
@author Nat Goodspeed
@date   2016-04-04
@brief  Topological sort of a dict graph representation
"""

class Cycle(Exception):
    pass

def topological_sort(items):
    """
    'items' is a dict of (item, dependencies) pairs, where 'dependencies' is
    an iterable of the same type as 'item'.

    topological_sort() returns a list of items in dependency order. It
    guarantees that no item depends on items with lower indices. Keys on which
    no other keys depend are last in the list. That is, given entries:

    'a': ['b', 'c']
    'b': ['d']
    'c': ['d']

    It produces ['a', 'c', 'b'].

    topological_sort() is implemented in terms of topological_rsort(): it
    builds and reverses a list in memory.

    topological_sort() has the peculiarity that it only mentions items that
    appear as a key in the dict. That is, given entries:

    'a': ['b']
    'b': ['c']

    the result will include 'a' and 'b' but not 'c'. If that's important, you
    could add an entry:

    'c': []

    (See fill_leaves().)

    Or you could simply be aware that, since 'c' obviously does not depend on
    anything else, it logically follows the last entry in the returned list.
    (See find_leaves().)

    topological_sort() raises Cycle if it detects a cyclic dependency in the
    provided input.
    """
    result = list(topological_rsort(items))
    result.reverse()
    return result

# This implementation is derived from
# https://en.wikipedia.org/wiki/Topological_sorting#Depth-first_search
def topological_rsort(items):
    """
    'items' is a dict of (item, dependencies) pairs, where 'dependencies' is
    an iterable of the same type as 'item'.

    topological_rsort() yields items in reverse dependency order. It
    guarantees that no item depends on items not yet yielded. Keys on which no
    other keys depend are emitted first. That is, given entries:

    'a': ['b', 'c']
    'b': ['d']
    'c': ['d']

    It produces 'b', 'c', 'a'.

    This can be useful if the set is large and you don't mind the reverse order.

    topological_rsort() has the peculiarity that it only yields items that
    appear as a key in the dict. That is, given entries:

    'a': ['b']
    'b': ['c']

    the result will include 'a' and 'b' but not 'c'. If that's important, you
    could add an entry:

    'c': []

    (See fill_leaves().)

    Or you could simply be aware that, since 'c' obviously does not depend on
    anything else, it logically precedes the first output from
    topological_rsort(). (See find_leaves().)

    topological_rsort() raises Cycle if it detects a cyclic dependency in the
    provided input.
    """
    # being in 'visiting' corresponds to 'temporary mark' from Wikipedia
    visiting = set()
    # removal from 'remaining' corresponds to 'permanent mark'
    remaining = list(items)
    while remaining:
        node = remaining[0]
        for n in _visit(items, visiting, remaining, node):
            yield n

def _visit(items, visiting, remaining, node):
    if node in visiting:
        # "temporary mark"
        raise Cycle("Cycle detected back to node %s" % node)
    if node not in remaining:
        # "permanent mark"
        return
    # "unmarked" node
    # mark node temporarily
    visiting.add(node)
    try:
        # traverse each edge from node to successor
        for child in items[node]:
            for n in _visit(items, visiting, remaining, child):
                yield n
    finally:
        # unmark node temporarily
        visiting.remove(node)
    # mark node permanently
    remaining.remove(node)
    # report node
    yield node

def find_leaves(items):
    """
    'items' is a dict of (item, dependencies) pairs, where 'dependencies' is
    an iterable of the same type as 'item'.

    Since neither topological_sort() nor topological_rsort() emit items that
    only appear as dependencies -- not having keys of their own -- it can be
    useful to make a separate pass over the items dict to tease out such leaf
    items. This function returns a set of items mentioned in dependencies that
    do not have corresponding keys.
    """
    # Nested list comprehension syntax is a little funky to me in that you
    # write the nested loops in the same order as if they were imperative
    # statements, even though you consume the inner value before the loops.
    return set(dep
               for deps in items.values()
               for dep in deps
               if dep not in items)

def fill_leaves(items):
    """
    'items' is a dict of (item, dependencies) pairs, where 'dependencies' is
    an iterable of the same type as 'item'.

    Since neither topological_sort() nor topological_rsort() emit items that
    only appear as dependencies -- not having keys of their own -- you might
    choose to prefill the items dict with keys for each of those leaf items.

    fill_leaves() modifies the items dict in place. It also returns it. If you
    want to leave the original dict unmodified, pass a copy() of items.
    """
    for item in find_leaves(items):
        items[item] = ()
    return items
