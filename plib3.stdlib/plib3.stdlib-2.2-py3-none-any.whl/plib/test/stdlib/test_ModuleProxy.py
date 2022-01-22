#!/usr/bin/env python3
"""
TEST.STDLIB.TEST_MODULEPROXY.PY -- test script for ModuleProxy
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the ModuleProxy class in
the plib.stdlib sub-package.
"""

import unittest

from plib.test.stdlib import ModuleProxy_testmod


class ModuleProxyTest(unittest.TestCase):
    
    def test_proxy(self):
        testdir = dir(ModuleProxy_testmod)
        testdict = set(ModuleProxy_testmod.__dict__.keys())
        testnames = ModuleProxy_testmod._names
        testmod = ModuleProxy_testmod._mod
        
        # The dir function retrieves all attributes, including proxied ones
        # that have not yet been realized
        self.assertTrue('test_var_static' in testdir)
        self.assertTrue('test_var_dynamic' in testdir)
        self.assertTrue('test_fn' in testdir)
        
        # The proxy module dict only contains realized attributes
        self.assertTrue('test_var_static' not in testdict)
        self.assertTrue('test_var_dynamic' not in testdict)
        self.assertTrue('test_fn' not in testdict)
        
        # The names dict only includes proxied attributes that need to be
        # realized on first retrieval
        self.assertTrue('test_var_static' not in testnames)
        self.assertTrue('test_var_dynamic' in testnames)
        self.assertTrue('test_fn' in testnames)
        
        # The wrapped module only contains static attributes directly
        self.assertTrue('test_var_static' in dir(testmod))
        self.assertTrue('test_var_dynamic' not in dir(testmod))
        self.assertTrue('test_fn' not in dir(testmod))
        
        # Static attributes get retrieved directly from the wrapped module;
        # nothing else changes behind the scenes
        self.assertEqual(ModuleProxy_testmod.test_var_static, "Static test variable.")
        self.assertEqual(testdir, dir(ModuleProxy_testmod))
        self.assertTrue('test_var_static' in dir(ModuleProxy_testmod))
        self.assertTrue('test_var_static' not in set(ModuleProxy_testmod.__dict__.keys()))
        self.assertTrue('test_var_static' not in testnames)
        self.assertTrue('test_var_static' in dir(testmod))
        
        # Dynamic attributes get retrieved from the names dict, and are
        # removed from it and put directly on the proxy module to speed
        # up subsequent retrievals
        self.assertEqual(ModuleProxy_testmod.test_var_dynamic, "Dynamic test variable.")
        self.assertEqual(testdir, dir(ModuleProxy_testmod))
        self.assertTrue('test_var_dynamic' in dir(ModuleProxy_testmod))
        self.assertTrue('test_var_dynamic' in set(ModuleProxy_testmod.__dict__.keys()))
        self.assertTrue('test_var_dynamic' not in testnames)
        self.assertTrue('test_var_dynamic' not in dir(testmod))
        
        # Dynamic attributes that are callable work the same as above, except
        # that they get called first and the result is returned as the attribute value
        self.assertEqual(ModuleProxy_testmod.test_fn, "Function returning test value.")
        self.assertEqual(testdir, dir(ModuleProxy_testmod))
        self.assertTrue('test_fn' in dir(ModuleProxy_testmod))
        self.assertTrue('test_fn' in set(ModuleProxy_testmod.__dict__.keys()))
        self.assertTrue('test_fn' not in testnames)
        self.assertTrue('test_fn' not in dir(testmod))
        
        testdir = dir(ModuleProxy_testmod)
        testdict = set(ModuleProxy_testmod.__dict__.keys())
        testnames = dict(ModuleProxy_testmod._names)
        testmoddir = dir(ModuleProxy_testmod._mod)
        
        # A nonexistent attribute leaves everything unchanged after retrieval is attempted
        self.assertRaises(AttributeError, getattr, ModuleProxy_testmod, 'this_one_aint_there')
        self.assertEqual(testdir, dir(ModuleProxy_testmod))
        self.assertEqual(testdict, set(ModuleProxy_testmod.__dict__.keys()))
        self.assertEqual(testnames, ModuleProxy_testmod._names)
        self.assertEqual(testmoddir, dir(ModuleProxy_testmod._mod))


if __name__ == '__main__':
    unittest.main()
