# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2020 European Synchrotron Radiation Facility
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
# ###########################################################################*/

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "06/08/2020"


import logging

_logger = logging.getLogger(__name__)


NABU_FILE_PER_GROUP = 100

NABU_CONFIG_FILE_EXTENSION = ".cfg"

NABU_CFG_FILE_FOLDER = "nabu_cfg_files"

try:
    import nabu.app.reconstruct  # noqa: F401
except ImportError:
    try:
        import nabu.resources.cli.reconstruct  # noqa: F401
    except ImportError:
        _logger.warning(
            "Fail to get path to nabu reconstruct main path. Take the most recent path"
        )
        NABU_FULL_FIELD_APP_PATH = "nabu.app.reconstruct"
    else:
        NABU_FULL_FIELD_APP_PATH = "nabu.resources.cli.reconstruct"
else:
    NABU_FULL_FIELD_APP_PATH = "nabu.app.reconstruct"
