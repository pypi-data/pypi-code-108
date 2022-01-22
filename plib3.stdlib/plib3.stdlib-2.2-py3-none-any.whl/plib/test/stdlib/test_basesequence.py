#!/usr/bin/env python3
"""
TEST.STDLIB.TEST_BASESEQUENCE.PY -- test script for plib.stdlib.basesequence
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the basesequence class.
"""

import unittest

from plib.stdlib.coll import basesequence

from plib.test.stdlib import abstract_testlib


class testsequence(basesequence):
    def __init__(self, seq=None):
        self._storage = []
        if seq:
            self._storage.extend(seq)
    
    def _indexlen(self):
        return len(self._storage)
    
    def _get_data(self, index):
        return self._storage[index]
    
    def _set_data(self, index, value):
        self._storage[index] = value


class Test_basesequence(abstract_testlib.FixedLengthSequenceTest):
    type2test = testsequence


if __name__ == '__main__':
    unittest.main()
