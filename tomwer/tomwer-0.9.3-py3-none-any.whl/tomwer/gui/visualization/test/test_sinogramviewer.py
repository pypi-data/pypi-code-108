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


__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "22/01/2017"


from silx.gui.utils.testutils import SignalListener
from tomwer.gui.visualization import sinogramviewer
from silx.gui import qt
from tomwer.core.utils.scanutils import MockHDF5
from silx.gui.utils.testutils import TestCaseQt
import unittest
import logging
import time
import tempfile
import shutil
import os

logging.disable(logging.INFO)


class TestSinogramViewer(TestCaseQt):
    """unit test for the :class:_ImageStack widget"""

    def setUp(self):
        TestCaseQt.setUp(self)
        self._widget = sinogramviewer.SinogramViewer()
        self._widget.setAttribute(qt.Qt.WA_DeleteOnClose)

        self.tmp_dir = tempfile.mkdtemp()
        self.scan = MockHDF5(
            scan_path=os.path.join(self.tmp_dir, "myscan"),
            n_proj=20,
            n_ini_proj=20,
            dim=10,
        ).scan

        # listen to the 'sigSinoLoadEnded' signal from the sinogram viewer
        self.signalListener = SignalListener()
        self._widget.sigSinoLoadEnded.connect(self.signalListener)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)
        self._widget.close()
        self._widget = None
        unittest.TestCase.tearDown(self)

    def test(self):
        """Make sur the addLeaf and clear functions are working"""
        self._widget.setScan(self.scan)
        timeout = 10
        while timeout >= 0 and self.signalListener.callCount() < 1:
            timeout -= 0.1
            time.sleep(0.1)
        if timeout >= 0:
            raise TimeoutError("widget never emitted the sigSinogramLoaded " "signal")
        self._widget.show()
        self.qWaitForWindowExposed(self._widget)
        self.qapp.processEvents()
        self.assertTrue(self._widget.getActiveImage() is not None)
