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
"""module for giving information on process progress"""

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "07/08/2019"


import sys
from enum import Enum
import logging

_logger = logging.getLogger(__name__)


class _Advancement(Enum):
    step_1 = "\\"
    step_2 = "-"
    step_3 = "/"
    step_4 = "|"

    @staticmethod
    def getNextStep(step):
        if step is _Advancement.step_1:
            return _Advancement.step_2
        elif step is _Advancement.step_2:
            return _Advancement.step_3
        elif step is _Advancement.step_3:
            return _Advancement.step_4
        else:
            return _Advancement.step_1

    @staticmethod
    def getStep(value):
        if value % 4 == 0:
            return _Advancement.step_4
        elif value % 3 == 0:
            return _Advancement.step_3
        elif value % 2 == 0:
            return _Advancement.step_2
        else:
            return _Advancement.step_1


class Progress(object):
    """Simple interface for defining advancement on a 100 percentage base"""

    def __init__(self, name):
        self._name = name
        self.reset()

    def reset(self, max_=None):
        self._nProcessed = 0
        self._maxProcessed = max_

    def startProcess(self):
        self.setAdvancement(0)

    def setAdvancement(self, value):
        length = 20  # modify this to change the length
        block = int(round(length * value / 100))
        msg = "\r{0}: [{1}] {2}%".format(
            self._name, "#" * block + "-" * (length - block), round(value, 2)
        )
        if value >= 100:
            msg += " DONE\r\n"
        sys.stdout.write(msg)
        sys.stdout.flush()

    def endProcess(self):
        self.setAdvancement(100)

    def setMaxAdvancement(self, n):
        self._maxProcessed = n

    def increaseAdvancement(self, i=1):
        self._nProcessed += i
        self.setAdvancement((self._nProcessed / self._maxProcessed) * 100)
