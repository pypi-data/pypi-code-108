#!/usr/bin/env python3
"""
TEST.STDLIB.TEST_BASELIST.PY -- test script for plib.stdlib.baselist
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the baselist class.
"""

import unittest

from plib.stdlib.coll import baselist

from plib.test.stdlib import abstract_testlib


class testlist(baselist):
    def __init__(self, seq=None):
        self._storage = []
        baselist.__init__(self, seq)
    
    def _indexlen(self):
        return len(self._storage)
    
    def _get_data(self, index):
        return self._storage[index]
    
    def _set_data(self, index, value):
        self._storage[index] = value
    
    def _add_data(self, index, value):
        self._storage[index:index] = [value]
    
    def _del_data(self, index):
        del self._storage[index]


class Test_baselist(abstract_testlib.MutableSequenceTest):
    type2test = testlist


if __name__ == '__main__':
    unittest.main()
