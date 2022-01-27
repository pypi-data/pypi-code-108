# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""
A simple Priority Dictionary. A hybrid of heap and a dictionary.
"""

from __future__ import unicode_literals
import collections
from operator import le, ge

from appdynamics.lang import range


class Node(object):
    __slots__ = ('key', 'val')

    def __init__(self, key, value):
        self.key = key
        self.val = value


class PriorityDict(collections.MutableMapping):
    """
    A simple Priority Dict
    """
    def __init__(self, data=None, min_heap=True):
        """
        A simple priority dict that arranges elements
        by the priority assigned (values). Also provides 0(1)
        look ups for the elements.

        Parameters
        ----------
        data: An iterable
        min_heap: True if elements are arranged as minheap parents < {children};
        false for max heap

        """
        self.cmp = le if min_heap else ge
        self._heap = []
        self._indices = {}  # keys mapped to indices in the actual heap
        if data:
            self.update(data)
        self.heapify()

    def __len__(self):
        return len(self._heap)

    def __getitem__(self, key):
        return self._heap[self._indices[key]].val

    def __setitem__(self, key, value):
        try:
            index = self._indices[key]
        except KeyError:
            # new key
            new_index = len(self._heap)
            self._heap.append(Node(key, value))
            self.bubble_up(new_index)
        else:
            # update existing key
            self._heap[index].val = value
            self.reheapify(index)

    def __delitem__(self, key):
        pos = self._indices.pop(key)  # raises KeyError
        node_to_delete = self._heap[pos]
        # swap the last node and re-heapify from that position -> O(log(n))
        last = self._heap.pop(-1)
        if last is not node_to_delete:
            self._heap[pos] = last
            self._indices[last.key] = pos
            self.reheapify(pos)
        del node_to_delete

    def __iter__(self):
        for node in self._heap:
            yield node.key

    def __repr__(self):
        return '({' + ', '.join([
            '%s: %s' % (repr(node.key), repr(node.val))
            for node in self._heap]) + '})'

    def reheapify(self, pos):
        """
        Re compute and arrange elements in the heap from a given position.

        Parameters
        ----------
        pos: index from which heap needs to be recomputed.
        """
        heap = self._heap
        parent_pos = (pos - 1) // 2
        child_pos = (2 * pos) + 1
        if parent_pos > -1 and self.cmp(heap[pos].val, heap[parent_pos].val):
            self.bubble_up(pos)
        elif child_pos < len(heap):
            other_pos = child_pos + 1
            if other_pos < len(heap) and not self.cmp(
                    heap[child_pos].val, heap[other_pos].val):
                child_pos = other_pos
            if self.cmp(heap[child_pos].val, heap[pos].val):
                self.bubble_down(pos)

    def heapify(self):
        """
        Compute heap from initial data
        """
        n = len(self._heap)
        for pos in reversed(range(n // 2)):
            self.bubble_down(pos)

    def bubble_up(self, pos, top=0):
        """
        re-adjust an element in pos by looking at its parents
        till it reaches top

        Parameters
        ----------
        pos: positon of the current element that needs to be adjusted.
        top: position till the search should continue.

        Returns
        -------

        """

        heap = self._heap
        indices = self._indices
        cmp_fn = self.cmp
        node = heap[pos]
        while pos > top:
            parent_pos = (pos - 1) // 2
            parent_node = heap[parent_pos]
            if cmp_fn(node.val, parent_node.val):
                heap[pos] = parent_node
                indices[parent_node.key] = pos
                pos = parent_pos
                continue
            break
        heap[pos] = node
        indices[node.key] = pos

    def bubble_down(self, top=0):
        """
        re-adjust an element in pos by looking at its children
        from top

        Parameters
        ----------
        pos: positon of the current element that needs to be adjusted.
        top: position till the search should continue.

        Returns
        -------
        """
        heap = self._heap
        indices = self._indices
        cmp_fn = self.cmp
        last = len(heap)
        pos = top
        node = heap[pos]
        child_pos = (2 * pos) + 1
        while child_pos < last:
            next_pos = child_pos + 1
            if next_pos < last and not cmp_fn(
                    heap[child_pos].val, heap[next_pos].val):
                child_pos = next_pos
            child_node = heap[child_pos]
            heap[pos] = child_node
            indices[child_node.key] = pos
            pos = child_pos
            child_pos = (2 * pos) + 1
        heap[pos] = node
        indices[node.key] = pos
        self.bubble_up(pos, top)

    def popitem(self):
        """
        retrieve the element with most priority.
        """

        heap = self._heap
        indices = self._indices

        try:
            last = heap.pop(-1)
        except IndexError:
            raise KeyError('Empty')

        if heap:
            node = heap[0]
            heap[0] = last
            indices[last.key] = 0
            self.bubble_down()
        else:
            node = last
        del indices[node.key]
        return node.key, node.val

    def popitems(self):
        """
        Priority Dict iterator.
        """
        try:
            while True:
                yield self.popitem()
        except KeyError:
            return

    def additem(self, key, value):
        """
        Add item to the Priority Dict
        Parameters
        ----------
        key: key
        value: value (used in determining  priority)

        """
        if key in self._indices:
            raise KeyError('Duplicate Insertions for key: %s' % repr(key))
        self[key] = value
