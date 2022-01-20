#!/usr/bin/env python3
"""
TEST.STDLIB.TEST_ABSTRACTCONTAINER.PY -- test script for plib.stdlib.abstractcontainer
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the abstractcontainer class.
"""

import unittest

from plib.stdlib.coll import abstractcontainer

from plib.test.stdlib import abstract_testlib


class testcontainer(abstractcontainer):
    def __init__(self, seq=None):
        self._storage = []
        if seq:
            self._storage.extend(seq)
    
    def __getitem__(self, index):
        result = self._storage[index]
        if isinstance(index, slice):
            result = self.__class__(result)
        return result


class Test_abstractcontainer(abstract_testlib.ImmutableSequenceTest):
    type2test = testcontainer


if __name__ == '__main__':
    unittest.main()
