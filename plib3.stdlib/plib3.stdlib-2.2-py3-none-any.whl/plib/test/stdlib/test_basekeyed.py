#!/usr/bin/env python3
"""
TEST.STDLIB.TEST_BASEKEYED.PY -- test script for plib.stdlib.basekeyed
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the basekeyed class.
"""

import unittest

from plib.stdlib.coll import basekeyed

from plib.test.stdlib import mapping_testlib


class testkeyed(basekeyed):
    def __init__(self, mapping=None):
        self._storage = {}
        if mapping:
            self._storage.update(mapping)
    
    def _keylist(self):
        return list(self._storage.keys())
    
    def _get_value(self, key):
        return self._storage[key]


class Test_basekeyed(mapping_testlib.ImmutableMappingTest):
    type2test = testkeyed


if __name__ == '__main__':
    unittest.main()
