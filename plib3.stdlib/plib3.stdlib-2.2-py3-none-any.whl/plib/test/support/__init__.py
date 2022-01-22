#! /usr/bin/env python3
"""
Sub-Package TEST.SUPPORT of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the Python Software Foundation License

Boilerplate test running routine. Looks for
the following test files:

- test_*.txt files are run as doctests
- test_*.py files are run as unit tests

Doctests are looked for in the ``doctests`` subdirectory
of the test directory; unit tests are looked for in the
test directory and any subdirectories that are Python
packages.

Also looks at the ``modules_with_doctests`` variable
for the names of Python modules that have doctests
in them.
"""

import sys
import os
import glob
import itertools
import doctest
import unittest

from plib.stdlib.ostools import subdirs


def run_tests(testname, modules_with_doctests=None, standalone_modules=None,
              module_relative=False, verbosity=0):
    """Run all tests found within the module or package ``testname``.
    """
    
    testmod = sys.modules[testname]
    testpkgname = testmod.__package__
    try:
        testpath = testmod.__path__
    except AttributeError:
        if testpkgname:
            testpath = sys.modules[testpkgname].__path__
        else:
            testpath = [os.path.dirname(testmod.__file__)]
    
    doctests = list(itertools.chain(*(
        glob.glob(os.path.join(testdir, "doctests", "test_*.txt"))
        for testdir in testpath
    ))) + list(itertools.chain(*(
        glob.glob(os.path.join(testdir, subdir, "doctests", "test_*.txt"))
        for testdir in testpath
        for subdir in subdirs(testdir)
    )))
    if doctests:
        print("Running doctests...")
        for filename in doctests:
            doctest.testfile(filename, module_relative=module_relative)
    else:
        print("No doctests found.")
    
    if modules_with_doctests:
        print("Running doctests from modules...")
        from importlib import import_module
        for modname in modules_with_doctests:
            mod = import_module(modname)
            doctest.testmod(mod)
    else:
        print("No modules with doctests found.")
    
    if standalone_modules:
        print("Running standalone test modules...")
        from runpy import run_module
        for modname in standalone_modules:
            run_module(modname)
    else:
        print("No standalone test modules found.")
    
    unittests = [
        ('', os.path.splitext(os.path.basename(filename))[0])
        for testdir in testpath
        for filename in glob.glob(os.path.join(testdir, 'test_*.py'))
    ] + [
        (subdir, os.path.splitext(os.path.basename(filename))[0])
        for testdir in testpath
        for subdir in subdirs(testdir)
        if os.path.isfile(os.path.join(testdir, subdir, '__init__.py'))
        for filename in glob.glob(os.path.join(testdir, subdir, 'test_*.py'))
    ]
    if unittests:
        print("Running unittests...")
        loader = unittest.defaultTestLoader
        # Yes, this is a roundabout way of doing it, but we want
        # to exactly duplicate what would be done if we ran each
        # module individually as a unittest (i.e., running
        # unittest.main() from the module itself); otherwise,
        # particularly with the I/O tests, we can get errors
        # from one test stepping on another
        suites = [
            loader.loadTestsFromName('{}{}{}'.format(
                '{}.'.format(testpkgname) if testpkgname else '',
                '{}.'.format(subdir) if subdir else '',
                modname))
            for subdir, modname in unittests
        ]
        fullsuite = unittest.TestSuite(suites)
        runner = unittest.TextTestRunner(verbosity=verbosity)
        runner.run(fullsuite)
    else:
        print("No unittests found.")
