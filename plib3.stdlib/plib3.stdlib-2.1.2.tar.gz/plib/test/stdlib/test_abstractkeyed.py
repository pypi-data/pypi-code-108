#!/usr/bin/env python3
"""
TEST.STDLIB.TEST_ABSTRACTKEYED.PY -- test script for plib.stdlib.abstractkeyed
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the abstractkeyed class.
"""

import unittest

from plib.stdlib.coll import abstractkeyed

from plib.test.stdlib import mapping_testlib


class testkeyed(abstractkeyed):
    def __init__(self, mapping=None):
        self._storage = {}
        if mapping:
            self._storage.update(mapping)
    
    def __iter__(self):
        return iter(self._storage)
    
    def __getitem__(self, key):
        return self._storage[key]


class Test_abstractkeyed(mapping_testlib.ImmutableMappingTest):
    type2test = testkeyed


if __name__ == '__main__':
    unittest.main()
