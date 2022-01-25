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


import unittest
from tomwer.core.process.control.volumesymlink import VolumeSymbolicLinkProcess
from tomwer.core.utils.scanutils import MockEDF
from tomwer.core.scan.edfscan import EDFTomoScan
import tempfile
import shutil
import os


class TestVolumeSymbolicLink(unittest.TestCase):
    """Simple test of the VolumeSymbolicLink"""

    def setUp(self) -> None:
        self._scan_folder = tempfile.mkdtemp()
        self._output_folder = tempfile.mkdtemp()
        MockEDF.fastMockAcquisition(self._scan_folder)
        MockEDF.mockReconstruction(self._scan_folder, nRecons=2, nPagRecons=2)
        self._scan = EDFTomoScan(self._scan_folder)
        # here we simply estimate that the slice reconstruction will be
        # volume reconstruction but the mechanism is the same.
        self._scan.set_latest_vol_reconstructions(self._scan.get_reconstructions_urls())

    def tearDown(self) -> None:
        for folder in (self._scan_folder, self._output_folder):
            shutil.rmtree(folder)

    def test(self):
        """simple test that the creation of a symbolic link works"""
        vlink_process = VolumeSymbolicLinkProcess(inputs={"data": self._scan})
        vlink_process.set_configuration(
            {
                "output_type": "static",
                "output_folder": self._output_folder,
            }
        )
        self.assertEqual(len(os.listdir(self._output_folder)), 0)
        vlink_process.run()
        self.assertEqual(len(os.listdir(self._output_folder)), 4)

        self.assertTrue(isinstance(vlink_process.program_name(), str))
        self.assertTrue(isinstance(vlink_process.program_version(), str))
        self.assertTrue(isinstance(vlink_process.definition(), str))
