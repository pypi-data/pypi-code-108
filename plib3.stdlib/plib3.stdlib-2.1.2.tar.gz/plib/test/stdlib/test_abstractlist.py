#!/usr/bin/env python3
"""
TEST.STDLIB.TEST_ABSTRACTLIST.PY -- test script for plib.stdlib.baselist
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the abstractlist class.
"""

import unittest

from plib.stdlib.coll import abstractlist

from plib.test.stdlib import abstract_testlib


class testlist(abstractlist):
    def __init__(self, seq=None):
        self._storage = []
        abstractlist.__init__(self, seq)
    
    def __getitem__(self, index):
        result = self._storage[index]
        if isinstance(index, slice):
            result = self.__class__(result)
        return result
    
    def __setitem__(self, index, value):
        # Make sure we match Python 2.6 list semantics for extended slices with step == 1
        if isinstance(index, slice) and (index.step is not None) and (index.step == 1):
            index = slice(index.start, index.stop)  # make it a non-extended slice to make sure
        self._storage[index] = value
    
    def __delitem__(self, index):
        del self._storage[index]
    
    def insert(self, index, value):
        self._storage.insert(index, value)


class Test_abstractlist(abstract_testlib.MutableSequenceTest):
    type2test = testlist


if __name__ == '__main__':
    unittest.main()
