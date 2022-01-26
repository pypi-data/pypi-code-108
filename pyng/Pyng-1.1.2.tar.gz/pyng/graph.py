#!/usr/bin/python
"""\
@file   graph.py
@author Nat Goodspeed
@date   2016-04-04
@brief  Filtering a dict graph representation
"""
from __future__ import print_function
from __future__ import absolute_import

import sys
import itertools
from .toposort import topological_sort, find_leaves
from .dicts import interdict

class BadLink(Exception):
    pass

def downstream_sorted(deps, start, end=None):
    """
    Given a DAG of nodes that can be stored in a set() (e.g. strings), yield
    an ordered list of nodes 'downstream' from the start nodes. The returned
    nodes are topologically sorted: no node depends on any node earlier in the
    sequence.

    This can be used, for instance, to answer the question: If I update these
    particular third-party packages, what other packages must be updated, in
    what order?

    Pass:

    deps is a dict. Each key is one of the nodes of interest. Its value is an
    iterable of the nodes directly downstream from it.

    start is an ITERABLE of nodes in deps. These are the nodes about which
    we're asking. Passing a single string will likely result in badness as the
    algorithm attempts to find dependencies for each individual character.

    end is optional. If not None, it is one of the nodes in deps. Any path that
    does not lead to 'end' will be pruned. This can be used if you suspect that
    there are 'evolutionary dead ends' that could be reached from 'start' but
    do not participate in 'end'.
    """
    # For each item in start, determine all downstream entries, direct or
    # indirect, using downstream_set(). Get the set union of all.
    affected = set().union(*(downstream_set(deps, node, end) for node in start))
    # Get a copy of deps whose only entries are those affected.
    trimdeps = interdict(deps, affected)
    # The desired result is a topological sort of the resulting dict. But
    # since topological_sort() only returns nodes that appear in
    # trimdeps.keys(), append anything that appears only in its values().
    return itertools.chain(topological_sort(trimdeps), find_leaves(trimdeps))

def downstream_set(deps, start, end=None):
    """
    Given a DAG of nodes that can be stored in a set() (e.g. strings), return
    a set() of nodes 'downstream' from the origin node.

    This can be used, for instance, to answer the question: If I update this
    particular third-party package, what other packages must be updated?

    Pass:

    deps is a dict. Each key is one of the nodes of interest. Its value is an
    iterable of the nodes directly downstream from it.

    start is one of the nodes in deps. This is the node about which we're asking.

    end is optional. If not None, it is one of the nodes in deps. Any path that
    does not lead to 'end' will be pruned. This can be used if you suspect that
    there are 'evolutionary dead ends' that could be reached from 'start' but
    do not participate in 'end'.
    """
    result = set()
    if end is None:
        # No definite 'end' node, just collect all downstream nodes using
        # simpler algorithm.
        _downstream_set(result, ["(param)"], deps, start)
    else:
        # We have a definite 'end' node: collect all paths definitely leading
        # to that node.
        _downstream_set_to(result, ["(param)"], deps, start, end)
    return result

def _downstream_set(result, path, deps, start):
    """
    Given a DAG of nodes that can be stored in a set() (e.g. strings), build a
    set() of nodes 'downstream' from the 'start' node, directly or indirectly.

    This can be used, for instance, to answer the question: If I update this
    particular third-party package, what other packages must be updated?

    Pass:

    result is a set() to which the nodes downstream from 'start' will be added.

    path is a list of nodes traversed so far. The first entry should be a
    dummy, a node or string used only in case of a broken dependency to report
    which node references the bad node.

    deps is a dict. Each key is one of the nodes of interest. Its value is an
    iterable of the nodes directly downstream from it.

    start is one of the nodes in deps. This is the node about which we're asking.
    """
    try:
        children = _validate(path, deps, start)
    except BadLink as err:
        print(err, file=sys.stderr)
        return

    # Now that we know 'start' is valid, add it to result
    result.add(start)
    # Process each of its children as well, adding 'start' as path[-1] for
    # recursive call.
    for child in children:
        _downstream_set(result, path + [start], deps, child)

def _downstream_set_to(result, path, deps, start, end):
    """
    Given a DAG of nodes that can be stored in a set() (e.g. strings), build a
    set() of nodes 'downstream' from the 'start' node that definitely lead to
    the 'end' node.

    This can be used, for instance, to answer the question: If I update this
    particular third-party package, what other packages must be updated to
    rebuild the viewer? This function will ignore packages that depend on
    'start' but are used only for the server, presuming that 'deps' contains
    arcs for both viewer and server.

    Pass:

    result is a set() to which the nodes on all paths leading to 'end' will
    be added. Paths that do not ultimately reach 'end' will be ignored.

    path is a list of nodes traversed so far. The first entry should be a
    dummy, a node or string used only in case of a broken dependency to report
    which node references the bad node.

    deps is a dict. Each key is one of the nodes of interest. Its value is an
    iterable of the nodes directly downstream from it.

    start is one of the nodes in deps. This is the node about which we're asking.

    end is one of the nodes in deps. Any path that does not lead to 'end' will
    be pruned.
    """
    # Once we reach 'end', this path is good: add everything including 'start'
    # (but skipping the requisite dummy first node).
    if start == end:
        result.update(path[1:] + [start])
        return

    # We're not yet at 'end'. Get this node's children.
    try:
        children = _validate(path, deps, start)
    except BadLink as err:
        print(err, file=sys.stderr)
        return

    # Process each of the children, adding 'start' as path[-1] for recursive
    # call. Note that any path not leading to 'end' won't ever contribute nodes
    # to 'result'.
    for child in children:
        _downstream_set_to(result, path + [start], deps, child, end)

def _validate(path, deps, start):
##  # Passing 'start' not in 'deps' isn't good. Could either be caller's error
##  # (passing 'start' that isn't even a node) or literally a broken dependency
##  # (deps[start] contains something that isn't a node).
##  try:
##      children = deps[start]
##  except KeyError:
##      raise BadLink("Broken dependency: %s -> %s" % (path[-1], start))

    # We specify that 'deps' must be a DAG. But in case the data come from an
    # unreliable source, validate rather than going into infinite recursion.
    try:
        # Did we previously visit this 'start' node in the current path? (Skip
        # dummy node.)
        pos = path[1:].index(start)
    except ValueError:
        # No, all's well so far, carry on
        pass
    else:
        # We've already visited this node, at path[1+pos]. Skip the path left
        # of that point; report path subset from the previous visit to 'start'.
        raise BadLink("Circularity: %s" % (" -> ".join(path[1+pos:] + [start])))

##  return children
    # The graph we get from autobuild dependencies doesn't have empty entries
    # for packages without dependencies -- those packages simply aren't
    # mentioned. So instead of complaining about a missing package name,
    # simply say "no dependencies" and carry on.
    return deps.get(start, [])
