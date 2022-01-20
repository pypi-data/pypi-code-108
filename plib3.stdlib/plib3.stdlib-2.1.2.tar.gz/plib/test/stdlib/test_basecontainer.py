#!/usr/bin/env python3
"""
TEST.STDLIB.TEST_BASECONTAINER.PY -- test script for plib.stdlib.basecontainer
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the basecontainer class.
"""

import unittest

from plib.stdlib.coll import basecontainer

from plib.test.stdlib import abstract_testlib


class testcontainer(basecontainer):
    def __init__(self, seq=None):
        self._storage = []
        if seq:
            self._storage.extend(seq)
    
    def _indexlen(self):
        return len(self._storage)
    
    def _get_data(self, index):
        return self._storage[index]


class Test_basecontainer(abstract_testlib.ImmutableSequenceTest):
    type2test = testcontainer


if __name__ == '__main__':
    unittest.main()
