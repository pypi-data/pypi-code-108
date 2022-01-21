# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4; encoding:utf8 -*-
#
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()

import os
import sys
import pytest

@pytest.fixture(scope=u"function")
def redirect_stdin():
    u"""GPG requires stdin to be open and have real file descriptor, which interferes with pytest's capture facility.
    Work around this by redirecting /dev/null to stdin temporarily.

    Activate this fixture on unittest test methods and classes by means of @pytest.mark.usefixtures("redirect_stdin")."""
    try:
        targetfd_save = os.dup(0)
        stdin_save = sys.stdin

        nullfile = open(os.devnull, u"r")
        sys.stdin = nullfile
        os.dup2(nullfile.fileno(), 0)
        yield
    finally:
        os.dup2(targetfd_save, 0)
        sys.stdin = stdin_save
        os.close(targetfd_save)
        nullfile.close()
