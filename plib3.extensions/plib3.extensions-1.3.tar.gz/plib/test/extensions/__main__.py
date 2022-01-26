#!/usr/bin/env python3
"""
Module MAIN
Sub-Package TEST.EXTENSIONS of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This is the test-running script for the PLIB3.EXTENSIONS test suite.
"""


if __name__ == '__main__':
    from plib.test.support import run_tests
    
    run_tests(__name__)
