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
__date__ = "24/11/2021"


from tomwer.core.utils.scanutils import MockEDF
from tomwer.core.utils.scanutils import MockHDF5
from tomwer.core.process.reconstruction.darkref.darkrefs import (
    requires_normed_dark_and_flat,
)


def test_quick_run_necessary_edf(tmpdir):
    """test the `quick_run_necessary` function for EDFTomoScan"""
    scan = MockEDF.mockScan(scanID=str(tmpdir), start_dark=True, start_flat=True)
    assert scan.normed_darks in (None, {})
    assert scan.normed_flats in (None, {})
    requires_normed_dark_and_flat(scan=scan)
    assert len(scan.normed_darks) == 1
    assert len(scan.normed_flats) == 1


def test_quick_run_necessary_hdf5(tmpdir):
    """test the `quick_run_necessary` function for HDF5TomoScan"""
    scan = MockHDF5(
        scan_path=tmpdir,
        n_proj=20,
        n_ini_proj=20,
        dim=10,
    ).scan
    assert scan.normed_darks in (None, {})
    assert scan.normed_flats in (None, {})
    requires_normed_dark_and_flat(scan=scan)
    assert len(scan.normed_darks) == 1
    assert len(scan.normed_flats) == 1
