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
__date__ = "22/20/2020"


from orangewidget.widget import OWBaseWidget
from processview.core.superviseprocess import SuperviseProcess
import functools
from processview.core.manager import ProcessManager, DatasetState


class SuperviseOW(OWBaseWidget, SuperviseProcess, openclass=True):
    """
    A basic OWWidget but registered on the process manager
    """

    def __init__(self, parent, process_id=None):
        OWBaseWidget.__init__(self, parent, process_id=process_id)
        SuperviseProcess.__init__(self, process_id=process_id)
        self.destroyed.connect(functools.partial(ProcessManager().unregister, self))

    def setCaption(self, caption):
        OWBaseWidget.setCaption(self, caption)
        self.name = caption

    def notify_skip(self, scan, details=None):
        ProcessManager().notify_dataset_state(
            dataset=scan, process=self, state=DatasetState.SKIPPED, details=details
        )

    def notify_pending(self, scan, details=None):
        ProcessManager().notify_dataset_state(
            dataset=scan, process=self, state=DatasetState.PENDING, details=details
        )

    def notify_succeed(self, scan, details=None):
        ProcessManager().notify_dataset_state(
            dataset=scan, process=self, state=DatasetState.SUCCEED, details=details
        )

    def notify_failed(self, scan, details=None):
        ProcessManager().notify_dataset_state(
            dataset=scan, process=self, state=DatasetState.FAILED, details=details
        )
