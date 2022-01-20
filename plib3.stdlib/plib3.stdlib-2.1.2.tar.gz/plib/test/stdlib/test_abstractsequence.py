#!/usr/bin/env python3
"""
TEST.STDLIB.TEST_ABSTRACTSEQUENCE.PY -- test script for plib.stdlib.abstractsequence
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the abstractsequence class.
"""

import unittest

from plib.stdlib.coll import abstractsequence, normalize_slice

from plib.test.stdlib import abstract_testlib


class testsequence(abstractsequence):
    def __init__(self, seq=None):
        self._storage = []
        if seq:
            self._storage.extend(seq)
    
    def __getitem__(self, index):
        result = self._storage[index]
        if isinstance(index, slice):
            result = self.__class__(result)
        return result
    
    def set_index(self, index, value):
        # TODO Should this code be moved into abstractsequence?
        if isinstance(index, slice):
            try:
                vlen = len(value)
            except TypeError:
                try:
                    value = tuple(value)
                    vlen = len(value)
                except TypeError:
                    raise TypeError("can only assign an iterable")
            indexes = normalize_slice(len(self), index)
            if isinstance(indexes, list):
                slen = len(indexes)
            elif ((index.step is None) or (index.step == 1)) and (vlen > 0):
                raise TypeError("object does not support item insert/append")
            else:
                slen = 0
            if slen != vlen:
                raise ValueError("slice must be the same length as object assigned")
        self._storage[index] = value


class Test_abstractsequence(abstract_testlib.FixedLengthSequenceTest):
    type2test = testsequence


if __name__ == '__main__':
    unittest.main()
