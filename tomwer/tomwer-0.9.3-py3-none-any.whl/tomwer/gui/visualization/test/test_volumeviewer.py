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
__date__ = "21/06/2021"


from silx.gui import qt
from tomwer.core.utils.scanutils import MockHDF5
from silx.gui.utils.testutils import TestCaseQt
from tomwer.gui.visualization.volumeviewer import VolumeViewer
from silx.io.url import DataUrl
import numpy
import unittest
import logging
import tempfile
import shutil
import os

logging.disable(logging.INFO)


class TestDiffViewer(TestCaseQt):
    """unit test for the :class:_ImageStack widget"""

    def setUp(self):
        TestCaseQt.setUp(self)
        self._widget = VolumeViewer(parent=None)
        self._widget.setAttribute(qt.Qt.WA_DeleteOnClose)

        self.tmp_dir = tempfile.mkdtemp()

        self.scan = MockHDF5(
            scan_path=os.path.join(self.tmp_dir, "myscan"),
            n_proj=20,
            n_ini_proj=20,
            dim=10,
        ).scan
        volume = numpy.random.random(60 * 10 * 10).reshape(60, 10, 10)
        vol_path = os.path.join(self.scan.path, "volume.npy")
        numpy.save(vol_path, volume)
        self.scan.set_latest_vol_reconstructions(
            [
                DataUrl(file_path=vol_path, scheme="numpy"),
            ]
        )

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)
        self._widget.close()
        self._widget = None
        unittest.TestCase.tearDown(self)

    def test(self):
        self._widget.setScan(self.scan)
