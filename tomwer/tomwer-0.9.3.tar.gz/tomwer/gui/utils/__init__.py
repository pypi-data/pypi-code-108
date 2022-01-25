# coding: utf-8
# /*##########################################################################
# Copyright (C) 2017 European Synchrotron Radiation Facility
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

"""
Some utils GUI associated to illustrations
"""

__authors__ = ["H.Payno"]
__license__ = "MIT"
__date__ = "29/01/2020"


import subprocess
import logging

_logger = logging.getLogger(__name__)


__has_image_j = None


def has_imagej():
    """Return if imagej command is accessible from the computer"""
    global __has_image_j
    if __has_image_j is None:
        try:
            # use help because there is no information regarding version
            subprocess.call(["imagej", "-h"], stdout=subprocess.PIPE)
        except OSError:
            __has_image_j = False
        else:
            __has_image_j = True
    return __has_image_j


def open_url_with_image_j(url):
    """open the url in an imagej subprocess

    :param DataUrl url: url we want to open in imagej
    """
    if not has_imagej():
        raise OSError("ImageJ is not installed")
    else:
        # for now we only manage the simple case of an edf file
        try:
            subprocess.call(["imagej", "-o", url.file_path()])
        except Exception:
            _logger.warning("Fail to open {}. Reason is {}".format(str(url), str()))
