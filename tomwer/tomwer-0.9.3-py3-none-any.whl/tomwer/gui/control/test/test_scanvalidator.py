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
__date__ = "16/06/2021"


import logging
import os
import shutil
import tempfile
import time
import unittest
import pytest
from tomwer.core import settings
from tomwer.core import utils
from tomwer.core.utils.scanutils import MockEDF
from tomwer.core.process.control.scanvalidator import ScanValidatorP
from tomwer.gui.qtapplicationmanager import QApplicationManager
from tomwer.gui.utils.waiterthread import QWaiterThread
from tomwer.core.scan.edfscan import EDFTomoScan
from tomwer.test.utils import skip_gui_test

logging.disable(logging.INFO)

_qapp = QApplicationManager()


@pytest.mark.skipif(skip_gui_test(), reason="skip gui test")
class TestScanValidator(unittest.TestCase):
    """
    Simple test to make sure the timeout of data watcher is working properly
    """

    LOOP_MEM_RELEASER_DURATION = 0.2
    NB_SCANS = 2

    @classmethod
    def setUpClass(cls):
        settings.mock_lsbram(True)

        cls.scanValidator = ScanValidatorP(memoryReleaser=QWaiterThread(0.5))

        cls.scans = []

        for iScan in range(cls.NB_SCANS):
            scanID = tempfile.mkdtemp()
            MockEDF.mockScan(scanID=scanID, nRadio=10, nRecons=2, nPagRecons=0, dim=10)
            cls.scans.append(scanID)

    @classmethod
    def tearDownClass(cls):
        settings.mock_lsbram(False)
        utils.mockLowMemory(False)

        for f in cls.scans:
            if os.path.isdir(f):
                shutil.rmtree(f)

    @pytest.mark.skipif(
        (settings.isOnLbsram() and utils.isLowOnMemory(settings.get_lbsram_path())),
        reason="Lbsram already overloaded",
    )
    def testMemoryReleaseLoop(self):
        """
        Make sure the internal loop of the scan validator is active if we are
        on lbsram.
        """
        for scan in self.scans:
            self.scanValidator.addScan(EDFTomoScan(scan))
        self.assertEqual(len(self.scanValidator._scansToValidate), self.NB_SCANS)
        utils.mockLowMemory(True)

        for i in range(3):
            while _qapp.hasPendingEvents():
                _qapp.processEvents()
            time.sleep(self.LOOP_MEM_RELEASER_DURATION * 2)

        self.assertEqual(len(self.scanValidator._scansToValidate), 0)
        utils.mockLowMemory(False)
