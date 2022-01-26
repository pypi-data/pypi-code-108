#!/usr/bin/env python3
"""
TEST.EXTENSIONS.TEST_EXTENSIONS.PY -- test script for Python/C extensions
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the Python/C extensions in
the PLIB3.EXTENSIONS sub-package.
"""

import unittest

from plib.stdlib.iters import split_n
from plib.extensions import capsule_compare

from plib.test.extensions import extensions_testmod


class Test_capsule_compare(unittest.TestCase):
    
    def test_compare(self):
        o_orig = extensions_testmod.capsule_orig()
        o_same = extensions_testmod.capsule_same()
        o_diff = extensions_testmod.capsule_different()
        
        n_orig = extensions_testmod.capsule_null_orig()
        n_same = extensions_testmod.capsule_null_same()
        n_diff = extensions_testmod.capsule_null_different()
        
        capsules = [o_orig, o_same, o_diff, n_orig, n_same, n_diff]
        for i, capsule in enumerate(capsules):
            for other in capsules[:i] + capsules[i+1:]:
                self.assertTrue(capsule is not other)
        
        self.assertTrue(all(capsule_compare(c1, c2) == capsule_compare(c2, c1)
                        for c1 in capsules for c2 in capsules))
        
        o_capsules, n_capsules = split_n(3, capsules)
        
        self.assertTrue(all(capsule_compare(o, o) for o in o_capsules))
        self.assertTrue(capsule_compare(o_orig, o_same))
        self.assertFalse(capsule_compare(o_orig, o_diff))
        
        self.assertTrue(all(capsule_compare(n, n) for n in n_capsules))
        self.assertTrue(capsule_compare(n_orig, n_same))
        self.assertFalse(capsule_compare(n_orig, n_diff))
        
        self.assertTrue(all(capsule_compare(o, n) for o, n in zip(o_capsules, n_capsules)))
        self.assertTrue(capsule_compare(o_orig, n_same))
        self.assertFalse(capsule_compare(o_orig, n_diff))
        self.assertTrue(capsule_compare(n_orig, o_same))
        self.assertFalse(capsule_compare(n_orig, o_diff))
        
        self.assertRaises(TypeError, capsule_compare)
        self.assertRaises(TypeError, capsule_compare, None)
        self.assertRaises(TypeError, capsule_compare, None, None)
        self.assertRaises(TypeError, capsule_compare, None, o_orig)
        self.assertRaises(TypeError, capsule_compare, o_orig, None)
        self.assertRaises(TypeError, capsule_compare, None, None, None)


if __name__ == '__main__':
    unittest.main()
