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
This module is used to define the process of the reference creator.
This is related to the issue #184
"""

__authors__ = ["H.Payno"]
__license__ = "MIT"
__date__ = "19/07/2018"

import fnmatch
import logging
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.scan.scanfactory import ScanFactory
import tomwer.version
import os
import re

from tomwer.core.process.task import Task

_logger = logging.getLogger(__name__)


class BaseFilter(object):
    """
    Apply a filter to an object
    """

    def description(self):
        pass

    def isFiltered(self, value):
        """
        Return True if the value not filtered

        """
        raise NotImplementedError("Base class")


class _PatternBaseFilter(BaseFilter):
    """Filter based on a pattern"""

    def __init__(self, pattern):
        BaseFilter.__init__(self)
        self.setPattern(pattern)

    def setPattern(self, pattern):
        """
        compile th filter for the given pattern
        :param str pattern:
        """
        self._pattern = pattern

    def getPattern(self):
        return self._pattern


class RegularExpressionFilter(_PatternBaseFilter):
    """Filter a string based on a defined pattern"""

    def __init__(self, pattern):
        _PatternBaseFilter.__init__(self, pattern=pattern)

    def setPattern(self, pattern):
        """
        compile th filter for the given pattern
        :param str pattern:
        """
        super().setPattern(pattern)
        if self._pattern is not None:
            try:
                self._filter = re.compile(self._pattern)
            except re.error as e:
                self.unvalidPatternDefinition(self, self._pattern, e)
                _logger.error(e)

    def description(self):
        return "Filter a string base on a regular expression"

    def isFiltered(self, value):
        try:
            match = self._filter.match(value) is None
        except Exception:
            return False
        else:
            return match

    def unvalidPatternDefinition(self, cls, pattern, error):
        _logger.error(f"{cls} {pattern} is not a valid pattern. Error is {error}")


class UnixFileNamePatternFilter(_PatternBaseFilter):
    """Filter a string based on 'fnmatch' module (unix filename pattern
    matching)"""

    def __init__(self, pattern):
        _PatternBaseFilter.__init__(self, pattern)

    def description(self):
        return "Filter a string base on a glob (unix style pathname)"

    def isFiltered(self, value):
        try:
            match = fnmatch.fnmatch(value, self._pattern)
        except Exception:
            match = False
        return not match


class FileNameFilter(
    _PatternBaseFilter, Task, input_names=("data",), output_names=("data",)
):
    """Filter than can call several filter type"""

    UNIX_PATTERN_FILTER = "unix file name pattern"

    REGULAR_EXP_FILTER = "regular expression"

    FILTER_TYPES = UNIX_PATTERN_FILTER, REGULAR_EXP_FILTER

    _DEFAULT_FILTER_TYPE = FILTER_TYPES[0]

    _FILTER_CONSTR = {
        UNIX_PATTERN_FILTER: UnixFileNamePatternFilter,
        REGULAR_EXP_FILTER: RegularExpressionFilter,
    }

    def __init__(self, varinfo=None, inputs=None, label=None):
        Task.__init__(self, varinfo=varinfo, inputs=inputs, label=label)
        pattern = inputs.get("pattern", None)
        if pattern is None:
            raise ValueError("'pattern' should be provided")
        filter_type = inputs.get("filter_type", self._DEFAULT_FILTER_TYPE)
        self._invert = inputs.get("invert_result", False)

        self._filter = self._FILTER_CONSTR[filter_type](pattern)

        _PatternBaseFilter.__init__(self, pattern)

    @property
    def invert_result(self):
        return self._invert

    @property
    def filter(self):
        return self._filter

    def isFiltered(self, value):
        result = self._filter.isFiltered(value)
        if self.invert_result:
            return not result
        else:
            return result

    def run(self):
        scan = self.inputs.data
        if scan is None:
            raise ValueError("'data' should be provided")
        if isinstance(scan, dict):
            scan = ScanFactory.create_scan_object_frm_dict(scan)
        if scan is None:
            return False
        assert isinstance(scan, TomwerScanBase)

        if not self.isFiltered(os.path.basename(scan.path)):
            if self._return_dict:
                self.outputs.data = scan.to_dict()
            else:
                self.outputs.data = scan
        else:
            self.outputs.data = None

    @staticmethod
    def program_name():
        return "scan filter"

    @staticmethod
    def program_version():
        """version of the program used for this processing"""
        return tomwer.version.version

    @staticmethod
    def definition():
        """definition of the process"""
        return "filter a scan according to his name"
