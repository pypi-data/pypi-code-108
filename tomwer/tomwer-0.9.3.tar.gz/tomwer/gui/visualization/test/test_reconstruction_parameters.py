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
__date__ = "15/12/2021"


import tempfile
from silx.gui.utils.testutils import TestCaseQt
from silx.gui import qt
from silx.io.url import DataUrl
import shutil
import os
from tomwer.core.utils import scanutils
from tomwer.gui.visualization.reconstructionparameters import ReconstructionParameters


class TestReconstructionParameters(TestCaseQt):
    def setUp(self):
        super().setUp()
        self._window = ReconstructionParameters()
        self._output_dir = tempfile.mkdtemp()
        scan_path = os.path.join(self._output_dir, "my_acquisition")
        self.scan = scanutils.MockHDF5(
            scan_path=scan_path, n_proj=10, n_ini_proj=0
        ).scan

    def tearDown(self):
        shutil.rmtree(self._output_dir)
        self._window.setAttribute(qt.Qt.WA_DeleteOnClose)
        self._window.close()
        self._window = None
        super().tearDown()

    def test(self):
        url = DataUrl(
            file_path=self.scan.master_file,
            data_path=self.scan.entry,
        )
        # in real expect a nabu slice reconstruction file...
        self._window.setUrl(url)
        self._window.show()
        self.qWaitForWindowExposed(self._window)
