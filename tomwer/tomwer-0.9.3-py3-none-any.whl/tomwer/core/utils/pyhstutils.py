# coding: utf-8
# /*##########################################################################
# Copyright (C) 2016 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#############################################################################*/
"""some utils relative to PyHST
"""

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "19/01/2017"

import os
import re
import fnmatch


def _findPyHSTVersions(directory):
    """Try to get the PyHST executables"""

    pyhst_exe = []
    pattern = re.compile("PyHST2_[0-9][0-9][0-9][0-9][a-zA]")
    for f in os.listdir(directory):
        if pattern.match(f):
            pyhst_exe.append(f)

    return pyhst_exe


def _getPyHSTDir():
    """
    :return: the directory where the PyHST executable are"""
    if "PYHST_DIR" in os.environ:
        return os.environ["PYHST_DIR"]
    elif os.path.isdir("/usr/bin/"):
        return "/usr/bin/"
    else:
        return None


def _getPyHSTFromEnvVariable():
    pyhst_exe = []
    pattern = "PyHST2_*"
    for f in os.environ.keys():
        if fnmatch.fnmatch(f, pattern):
            pyhst_exe.append(f)

    return pyhst_exe
