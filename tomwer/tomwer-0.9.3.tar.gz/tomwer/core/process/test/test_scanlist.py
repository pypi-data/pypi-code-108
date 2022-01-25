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
__date__ = "05/04/2019"


import shutil
import tempfile
import unittest
from tomwer.core.utils.scanutils import MockEDF
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.process.control.scanlist import ScanList


class TestScanListIO(unittest.TestCase):
    """Test inputs and outputs types of the handler functions"""

    def setUp(self):
        self.scan_folder = tempfile.mkdtemp()

        self.scan = MockEDF.mockScan(
            scanID=self.scan_folder, nRadio=10, nRecons=1, nPagRecons=4, dim=10
        )

    def tearDown(self):
        shutil.rmtree(self.scan_folder)

    def testInputOutput(self):
        """Test that io using TomoBase instance work"""
        for return_dict in (True, False):
            with self.subTest(return_dict=return_dict):
                scan_list_process = ScanList(
                    inputs={
                        "scans": (self.scan_folder,),
                        "return_dict": return_dict,
                    }
                )

                scan_list_process.run()

                for out in scan_list_process.outputs["data"]:
                    if return_dict:
                        self.assertTrue(isinstance(out, dict))
                    else:
                        self.assertTrue(isinstance(out, TomwerScanBase))
