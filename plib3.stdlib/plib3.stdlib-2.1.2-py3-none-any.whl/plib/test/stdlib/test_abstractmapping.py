#!/usr/bin/env python3
"""
TEST.STDLIB.TEST_ABSTRACTMAPPING.PY -- test script for plib.stdlib.abstractmapping
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the abstractmapping class.
"""

import unittest

from plib.stdlib.coll import abstractmapping

from plib.test.stdlib import mapping_testlib


class testmapping(abstractmapping):
    def __init__(self, mapping=None):
        self._storage = {}
        if mapping:
            self._storage.update(mapping)
    
    def __iter__(self):
        return iter(self._storage)
    
    def __getitem__(self, key):
        return self._storage[key]
    
    def set_key(self, key, value):
        self._storage[key] = value


class Test_abstractmapping(mapping_testlib.FixedKeysMappingTest):
    type2test = testmapping


if __name__ == '__main__':
    unittest.main()
