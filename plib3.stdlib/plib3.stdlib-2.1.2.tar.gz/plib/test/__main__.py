#!/usr/bin/env python3
"""
Module MAIN
Sub-Package TEST of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This is the overall test-running script for the PLIB3 test suite.
"""

subpackage_names = (
    "stdlib",
    "dbtools",
    "ui",
    "classes",
    "extensions",
)


if __name__ == '__main__':
    from importlib import import_module
    from plib.test.support import run_tests
    
    for name in subpackage_names:
        modname = "plib.test.{}.__main__".format(name)
        try:
            mod = import_module(modname)
        except ImportError:
            print("No tests found for plib.{}".format(name))
        else:
            print("Running tests for plib.{}".format(name))
            modules_with_doctests = getattr(mod, 'modules_with_doctests', None)
            standalone_modules = getattr(mod, 'standalone_modules', None)
            run_tests(modname, modules_with_doctests, standalone_modules)
