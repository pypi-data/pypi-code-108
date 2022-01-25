# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2017 European Synchrotron Radiation Facility
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
__date__ = "30/09/2019"

import unittest
import os
import tempfile
from tomwer.core.utils.scanutils import MockHDF5
from tomwer.core.scan.hdf5scan import HDF5TomoScan


class TestMockHDF5(unittest.TestCase):
    """Test the MockHDF5 file"""

    def test_creation(self):
        folder = tempfile.mkdtemp()
        mock = MockHDF5(scan_path=folder, n_proj=10, n_ini_proj=10)
        self.assertEqual(
            mock.scan_master_file,
            os.path.join(folder, os.path.basename(folder) + ".h5"),
        )
        tomoScan = HDF5TomoScan(mock.scan_path, entry=mock.scan_entry)
        self.assertEqual(len(HDF5TomoScan.get_valid_entries(mock.scan_master_file)), 1)
        tomoScan.update()
        self.assertEqual(tomoScan.scan_range, 360)
        self.assertEqual(len(tomoScan.projections), 10)
