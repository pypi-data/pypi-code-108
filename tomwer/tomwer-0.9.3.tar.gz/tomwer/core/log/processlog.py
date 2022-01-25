# coding: utf-8
# ##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
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
# ###########################################################################
"""
Simple logs levels definition relative to process status
"""


__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "02/10/2020"

import logging


PROCESS_STARTED_NAME = "PROCESS_STARTED"
PROCESS_STARTED_LEVEL = 32

PROCESS_SUCCEED_NAME = "PROCESS_SUCCEED"
PROCESS_SUCCEED_LEVEL = 33

PROCESS_FAILED_NAME = "PROCESS_FAILED"
PROCESS_FAILED_LEVEL = 38

PROCESS_ENDED_NAME = "PROCESS_ENDED"
"""String name of the process ended"""

PROCESS_ENDED_LEVEL = 35
"""Level of the process ended"""

PROCESS_SKIPPED_NAME = "PROCESS_SKIPPED"
"""String name of the process skipped"""

PROCESS_SKIPPED_LEVEL = 36
"""Level of the process skipped"""

PROCESS_INFORM_NAME = "PROCESS_INFORM"
"""Name of the process information"""

PROCESS_INFORM_LEVEL = 31
"""Level for information send to graylog"""

logging.addLevelName(PROCESS_STARTED_LEVEL, PROCESS_STARTED_NAME)
logging.addLevelName(PROCESS_SUCCEED_LEVEL, PROCESS_SUCCEED_NAME)
logging.addLevelName(PROCESS_FAILED_LEVEL, PROCESS_FAILED_NAME)
logging.addLevelName(PROCESS_ENDED_LEVEL, PROCESS_ENDED_NAME)
logging.addLevelName(PROCESS_SKIPPED_LEVEL, PROCESS_SKIPPED_NAME)
logging.addLevelName(PROCESS_INFORM_LEVEL, PROCESS_INFORM_NAME)


def processEnded(self, message, *args, **kws):
    if self.isEnabledFor(PROCESS_ENDED_LEVEL):
        self._log(PROCESS_ENDED_LEVEL, message, args, **kws)


def processSkipped(self, message, *args, **kws):
    if self.isEnabledFor(PROCESS_SKIPPED_LEVEL):
        self._log(PROCESS_SKIPPED_LEVEL, message, args, **kws)


def inform(self, message, *args, **kws):
    if self.isEnabledFor(PROCESS_INFORM_LEVEL):
        self._log(PROCESS_INFORM_LEVEL, message, args, **kws)


def processSucceed(self, message, *args, **kws):
    if self.isEnabledFor(PROCESS_SUCCEED_LEVEL):
        self._log(PROCESS_SUCCEED_LEVEL, message, args, **kws)


def processFailed(self, message, *args, **kws):
    if self.isEnabledFor(PROCESS_FAILED_LEVEL):
        self._log(PROCESS_FAILED_LEVEL, message, args, **kws)


def processStarted(self, message, *args, **kws):
    if self.isEnabledFor(PROCESS_STARTED_LEVEL):
        self._log(PROCESS_STARTED_LEVEL, message, args, **kws)


logging.Logger.processEnded = processEnded
logging.Logger.processSkipped = processSkipped
logging.Logger.inform = inform
logging.Logger.processSucceed = processSucceed
logging.Logger.processFailed = processFailed
logging.Logger.processStarted = processStarted
