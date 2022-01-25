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
from tomwer.core.utils import getParametersFromParOrInfo
from ..reconstruction.ftseries import Ftseries
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.scan.edfscan import EDFTomoScan
from tomwer.core.process.reconstruction.ftseries.params import ReconsParams
from tomwer.test.utils import UtilsTest
import os


class TestFtseriesIO(unittest.TestCase):
    """Test inputs and outputs types of the handler functions"""

    def setUp(self) -> None:
        self.scan_folder = tempfile.mkdtemp()

        self.scan = MockEDF.mockScan(
            scanID=self.scan_folder, nRadio=10, nRecons=1, nPagRecons=4, dim=10
        )
        self.recons_params = ReconsParams()

    def tearDown(self) -> None:
        shutil.rmtree(self.scan_folder)

    def testInputOutput(self) -> None:
        """Test that io using TomoBase instance work"""
        for input_type in (dict, TomwerScanBase):
            for return_dict in (True, False):
                with self.subTest(
                    return_dict=return_dict,
                    input_type=input_type,
                ):
                    input_obj = self.scan
                    if input_obj is dict:
                        input_obj = input_obj.to_dict()
                    ftseries_process = Ftseries(
                        inputs={
                            "pyhst2_params": self.recons_params,
                            "mock_mode": True,
                            "return_dict": return_dict,
                            "data": input_obj,
                        }
                    )
                    ftseries_process.run()
                    out = ftseries_process.outputs.data
                    if return_dict:
                        self.assertTrue(isinstance(out, dict))
                    else:
                        self.assertTrue(isinstance(out, TomwerScanBase))


class TestFtseriesAxis(unittest.TestCase):
    """Test the behavior of ftseries depending on the axis parameter"""

    def setUp(self) -> None:
        self.outputDir = tempfile.mkdtemp()
        self.dataSetID = "scan_3_"
        self.dataDir = UtilsTest.getEDFDataset(self.dataSetID)
        self.datasetDir = os.path.join(self.outputDir, self.dataSetID)
        shutil.copytree(src=os.path.join(self.dataDir), dst=self.datasetDir)
        self.recons_params = ReconsParams()
        self.parFile = os.path.join(self.datasetDir, self.dataSetID + ".par")
        if os.path.exists(self.parFile):
            os.remove(self.parFile)
        self.scan = EDFTomoScan(self.datasetDir)
        self.axis_frm_tomwer_file = os.path.join(self.datasetDir, "correct.txt")

    def tearDown(self) -> None:
        shutil.rmtree(self.outputDir)

    def testAxisCorrectionOption(self) -> None:
        """Test that the pyhst parameter 'DO_AXIS_CORRECTION' is correctly set"""
        self.recons_params.axis.do_axis_correction = False
        ftseries_process = Ftseries(
            inputs={
                "pyhst2_params": self.recons_params,
                "data": self.scan,
            }
        )

        ftseries_process.run()
        self.assertTrue(os.path.exists(self.parFile))
        par_info = getParametersFromParOrInfo(self.parFile)
        self.assertTrue("DO_AXIS_CORRECTION".lower() in par_info)

        self.recons_params.axis.do_axis_correction = True
        ftseries_process.run()
        self.assertTrue(os.path.exists(self.parFile))
        par_info = getParametersFromParOrInfo(self.parFile)
        self.assertFalse(os.path.exists(self.axis_frm_tomwer_file))
