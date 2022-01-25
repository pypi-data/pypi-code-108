# coding: utf-8
# /*##########################################################################
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
# ###########################################################################*/

"""
module dealing with log in color

https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
"""

__author__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "22/09/2017"

import logging
from tomwer.core.log.processlog import (
    PROCESS_ENDED_NAME,
    PROCESS_SKIPPED_NAME,
    PROCESS_INFORM_NAME,
    PROCESS_STARTED_NAME,
    PROCESS_FAILED_NAME,
    PROCESS_SUCCEED_NAME,
)
import os

# The background is set with 40 plus the number of the color, and the
# foreground with 30

# These are the sequences need to get colored ouput
_RESET_SEQ = "\033[0m"
_COLOR_SEQ = "\033[1;%dm"
_BOLD_SEQ = "\033[1m"

_BLACK, _RED, _GREEN, _YELLOW, _BLUE, _MAGENTA, _CYAN, _WHITE = range(8)

LOG_COLORS = {
    "WARNING": _MAGENTA,
    "INFO": _BLACK,
    "DEBUG": _BLUE,
    "CRITICAL": _YELLOW,
    "ERROR": _RED,
    PROCESS_SKIPPED_NAME: _MAGENTA,
    PROCESS_ENDED_NAME: _BLACK,
    PROCESS_INFORM_NAME: _BLACK,
    PROCESS_STARTED_NAME: _BLACK,
    PROCESS_FAILED_NAME: _RED,
    PROCESS_SUCCEED_NAME: _GREEN,
}


def _formatter_message(message, use_color=True):
    if use_color is True:
        message = message.replace("$RESET", _RESET_SEQ).replace("$BOLD", _BOLD_SEQ)
    else:
        message = message.replace("$RESET", "").replace("$BOLD", "")
    return message


class _ColoredFormatter(logging.Formatter):
    def __init__(self, msg):
        logging.Formatter.__init__(self, msg)
        self.use_color = os.environ.get("ORANGE_COLOR_STDOUT_LOG", "False") == "True"

    def format(self, record):
        levelname = record.levelname
        if self.use_color is True and levelname in LOG_COLORS:
            levelname_color = (
                _COLOR_SEQ % (30 + LOG_COLORS[levelname]) + levelname + _RESET_SEQ
            )
            record.levelname = levelname_color
        record.asctime = self.formatTime(record, self.datefmt)
        return logging.Formatter.format(self, record)


class TomwerLogger(logging.Logger):
    """
    Custom logger class with multiple destinations
    """

    FORMAT = (
        "%(asctime)s [%(levelname)-16s] %(message)s [$BOLD%(name)-20s$RESET]"
        "($BOLD%(filename)s$RESET:%(lineno)d)"
    )

    def __init__(self, name):
        logging.Logger.__init__(self, name, logging.WARNING)
        self.name = name
        self.color_format = _formatter_message(
            TomwerLogger.FORMAT,
            use_color=os.environ.get("ORANGE_COLOR_STDOUT_LOG", "False") == "True",
        )

        color_formatter = _ColoredFormatter(self.color_format)

        console = logging.StreamHandler()
        console.setFormatter(color_formatter)

        self.addHandler(console)
        return

    def __str__(self):
        return self.name
