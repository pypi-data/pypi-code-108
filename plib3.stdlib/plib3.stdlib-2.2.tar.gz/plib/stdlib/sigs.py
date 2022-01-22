#!/usr/bin/env python3
"""
Module SIGS -- Signal Handler Utilities
Sub-Package STDLIB of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains utilities for signal handling.
"""

from contextlib import contextmanager
from signal import signal


@contextmanager
def signal_handler(sig, handler):
    oldhandler = signal(sig, handler)
    try:
        yield
    finally:
        signal(sig, oldhandler)
