#!/usr/bin/env python3
"""
TEST.STDLIB.TEST_ABSTRACTDICT.PY -- test script for plib.stdlib.abstractdict
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the abstractdict class.
"""

import unittest

from plib.stdlib.coll import abstractdict

from plib.test.stdlib import mapping_testlib


class testdict(abstractdict):
    def __init__(self, mapping=None, **kwargs):
        self._storage = {}
        abstractdict.__init__(self, mapping, **kwargs)
    
    def __iter__(self):
        return iter(self._storage)
    
    def __getitem__(self, key):
        return self._storage[key]
    
    def __setitem__(self, key, value):
        self._storage[key] = value
    
    def __delitem__(self, key):
        del self._storage[key]


class Test_abstractdict(mapping_testlib.MutableMappingTest):
    type2test = testdict


if __name__ == '__main__':
    unittest.main()
