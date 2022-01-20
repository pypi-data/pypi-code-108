#!/usr/bin/env python3
"""
TEST.STDLIB.TEST_BASEMAPPING.PY -- test script for plib.stdlib.basemapping
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the basemapping class.
"""

import unittest

from plib.stdlib.coll import basemapping

from plib.test.stdlib import mapping_testlib


class testmapping(basemapping):
    def __init__(self, mapping=None):
        self._storage = {}
        if mapping:
            self._storage.update(mapping)
    
    def _keylist(self):
        return list(self._storage.keys())
    
    def _get_value(self, key):
        return self._storage[key]
    
    def _set_value(self, key, value):
        self._storage[key] = value


class Test_basemapping(mapping_testlib.FixedKeysMappingTest):
    type2test = testmapping


if __name__ == '__main__':
    unittest.main()
