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
__date__ = "19/07/2018"

import unittest
import tempfile
import shutil
from tomwer.core.process.reconstruction.lamino import tofu
from tomwer.core.scan.edfscan import EDFTomoScan


class TestTofuReconstruction(unittest.TestCase):
    """Simple test of the Lamino reconstruction API"""

    def tearDown(self):
        shutil.rmtree(self._scan_path)

    def setUp(self):
        self._scan_path = tempfile.mkdtemp()
        self.scan = EDFTomoScan(self._scan_path)
        self.reconstruction = tofu.LaminoReconstruction(
            inputs={
                "dry_run": True,
                "data": self.scan,
                "lamino_params": {
                    "center-position-x": 5.0,
                    "projections": "tata-yoyo",
                    "output": "output_dir",
                },
            }
        )

    def testProcessAPI(self):
        self.reconstruction.run()

    def testPreProcessAPI(self):
        self.assertFalse(
            self.reconstruction.is_ffc_has_been_preprocessed(
                scan=self.scan, x_center=5.0, method=None, darks=None, ff=[None, None]
            )
        )
        self.reconstruction.preprocess_ff(self.scan)
        self.assertTrue(
            self.reconstruction.is_ffc_has_been_preprocessed(
                scan=self.scan, x_center=5.0, method=None, darks=None, ff=[None, None]
            )
        )
        self.reconstruction.run()
        self.assertTrue(
            self.reconstruction.is_ffc_has_been_preprocessed(
                scan=self.scan, x_center=5.0, method=None, darks=None, ff=[None, None]
            )
        )
        self.reconstruction.reconstruction_parameters["center-position-x"] = 2.0
        self.assertFalse(
            self.reconstruction.is_ffc_has_been_preprocessed(
                scan=self.scan, x_center=2.0, method=None, darks=None, ff=[None, None]
            )
        )
        self.reconstruction.preprocess_ff(self.scan)
        self.assertTrue(
            self.reconstruction.is_ffc_has_been_preprocessed(
                scan=self.scan, x_center=2.0, method=None, darks=None, ff=[None, None]
            )
        )
