#!/usr/bin/env python3
"""
Module PROC -- Process-Related Utilities
Sub-Package STDLIB of Package PLIB3 -- General Python Utilities
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module is for useful process-related functions that give
a simpler API than the ``subprocess`` module.
"""

from subprocess import check_output, STDOUT, CalledProcessError


def process_call(cmdline, stdin=None, shell=False,
                 universal_newlines=False):
    """Return exit code and output of ``cmdline``.
    
    Useful when you want only the exit code and string output
    and don't care about the details of errors. The output
    includes standard error as well as standard output. The
    ``stdin``, ``shell``, and ``universal_newlines`` arguments
    are as documented for ``subprocess.check_output``.
    """
    
    try:
        return 0, check_output(cmdline, stderr=STDOUT,
                               stdin=stdin, shell=shell,
                               universal_newlines=universal_newlines)
    except CalledProcessError as e:
        return e.returncode, e.output


def process_output(cmdline, stdin=None, shell=False,
                   universal_newlines=False):
    """Return output of ``cmdline`` as a string.
    
    Useful when you don't care about anything except the
    output from the process (i.e., you don't need the return
    code or any specific error information). The output
    includes standard error as well as standard output. The
    ``stdin``, ``shell``, and ``universal_newlines`` arguments
    are as documented for ``subprocess.check_output``.
    """
    
    try:
        return check_output(cmdline, stderr=STDOUT,
                            stdin=stdin, shell=shell,
                            universal_newlines=universal_newlines)
    except CalledProcessError as e:
        return e.output
