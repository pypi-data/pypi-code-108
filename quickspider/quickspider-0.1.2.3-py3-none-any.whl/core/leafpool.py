#!/usr/bin/env python3
class LeafPool:
    def __init__(self, header):
        self._pool = []
        self._scan_leaves(header)

    def __getitem__(self, key):
        return self._pool[key]

    def _add_leaf(self, node):
        self._pool.append(node)

    def _scan_leaves(self, node):
        if not node:
            return
        if node._is_leaf():
            self._add_leaf(node)
            return
        for child in node._child:
            self._scan_leaves(child)

    def loop(self):
        num = len(self._pool)
        pool = self._pool
        index = 0
        while True:
            one_leaf = pool[index]
            success = one_leaf.activate()
            if not success and index == (num-1):
                break
            index += 1
            if index == num:
                index = 0
        return
