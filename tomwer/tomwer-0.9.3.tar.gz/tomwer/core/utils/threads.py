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

"""
This module is used to manage observations. Initially on files.
Observations are runned on a thread and run each n seconds.
They are manage by thread and signals
"""

__authors__ = ["H.Payno"]
__license__ = "MIT"
__date__ = "09/01/2019"


import threading
import time


class LoopThread(threading.Thread):
    """
    Thread looping on a defined process, as long not receiving the stopEvent.
    Wait for `_time_between_loops` between two loops
    """

    startEvent = threading.Event()
    """Event to restart the loop on process"""
    stopEvent = threading.Event()
    """Event to stop the loop on process"""
    quitEvent = threading.Event()
    """Event to quit the Thread"""

    def __init__(self, time_between_loops):
        threading.Thread.__init__(self)
        self._time_between_loops = time_between_loops
        self._status = None
        self._last_processing = None

    def run(self):
        threading.Thread.run(self)
        while not self.quitEvent.isSet():
            if self._status is None or (
                self._status == "not running" and self.startEvent.isSet()
            ):
                self._status = "running"
                self.startEvent.clear()

            if self._status == "running" and self.stopEvent.isSet() is True:
                self.stopEvent.clear()
                self._status = "not running"
            if self._status == "running" and self.should_process():
                self._last_processing = time.time()
                self.process()
            time.sleep(0.05)

    def process(self):
        raise NotImplementedError("Pure virtual class")

    def should_process(self):
        if self._last_processing is None:
            return True
        _pass_time_since_last_pro = time.time() - self._last_processing
        return _pass_time_since_last_pro > self._time_between_loops

    def _stop(self):
        pass
