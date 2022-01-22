#!/usr/bin/env python3
"""
Module MAIN
Sub-Package TEST.CLASSES of Package PLIB3
Copyright (C) 2008-2015 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This is the test-running script for the PLIB3.CLASSES test suite.
"""


if __name__ == '__main__':
    from plib.test.support import run_tests
    
    run_tests(__name__)
