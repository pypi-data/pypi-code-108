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

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "12/12/2018"


from tomwer.core.process.task import Task
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.scan.scanfactory import ScanFactory
import time
import logging

_logger = logging.getLogger(__name__)


class Timer(Task, input_names=("data",), output_names=("data",)):
    """
    Simple timer / time out - function
    """

    def __init__(self, varinfo=None, inputs=None, name=None):
        Task.__init__(self, varinfo=varinfo, inputs=inputs, label=name)
        if inputs is None:
            inputs = {}
        self.waiting_time = inputs.get("wait", 1)

    @property
    def waiting_time(self):
        return self._waiting_time

    @waiting_time.setter
    def waiting_time(self, wait):
        self._waiting_time = wait

    def run(self):
        scan = self.inputs.data
        if type(scan) is dict:
            scan = ScanFactory.create_scan_object_frm_dict(scan)
        else:
            scan = scan
        if not isinstance(scan, TomwerScanBase):
            raise TypeError(
                "scan is expected to be a dict or an instance "
                "of TomwerScanBase. Not {}".format(type(scan))
            )
        time.sleep(self.waiting_time)
        if self._return_dict:
            self.outputs.data = scan.to_dict()
        else:
            self.outputs.data = scan
