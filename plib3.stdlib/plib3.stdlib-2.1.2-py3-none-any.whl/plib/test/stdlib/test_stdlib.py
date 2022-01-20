#!/usr/bin/env python3
"""
TEST.STDLIB.TEST_STDLIB.PY -- test script for sub-package STDLIB of package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the PLIB3.STDLIB sub-package.
"""

import unittest

from plib.stdlib.decotools import cached_property


class CachedPropertyTest(object):
    def __init__(self):
        self.accessed = False
    
    def test(self):
        self.accessed = True
        return "Test done."
    
    test = cached_property(test)


class Test_cached_property(unittest.TestCase):
    
    def test_all(self):
        # Initialize
        self.t = CachedPropertyTest()
        self.assertTrue(not self.t.accessed)
        
        # First access sets the accessed flag to True
        # and writes the value to the instance dict
        self.assertEqual(self.t.test, "Test done.")
        self.assertTrue('test' in self.t.__dict__)
        self.assertTrue(self.t.accessed)
        
        # Next access leaves the accessed flag alone
        self.t.accessed = False
        self.assertEqual(self.t.test, "Test done.")
        self.assertTrue(not self.t.accessed)
        
        # The cached property can be deleted
        del self.t.test
        self.assertTrue(not ('test' in self.t.__dict__))
        
        # And overwritten without triggering it
        self.t.test = "Other value."
        self.assertEqual(self.t.test, "Other value.")
        self.assertTrue(not self.t.accessed)
        
        # Deleting re-starts the property
        del self.t.test
        self.assertEqual(self.t.test, "Test done.")
        self.assertTrue('test' in self.t.__dict__)
        self.assertTrue(self.t.accessed)
        
        # One other wrinkle; hasattr also triggers
        # the property!
        del self.t.test
        self.t.accessed = False
        self.assertTrue(hasattr(self.t, 'test'))
        self.assertTrue('test' in self.t.__dict__)
        self.assertTrue(self.t.accessed)


if __name__ == '__main__':
    unittest.main()
