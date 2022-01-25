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
__date__ = "28/10/2020"


import unittest
import pytest
from silx.gui import qt
from silx.gui.utils.testutils import TestCaseQt
from tomwer.test.utils import skip_gui_test
from tomwer.core.utils.scanutils import MockHDF5
from tomwer.gui.edit.dkrfpatch import DarkRefPatchWidget
from tomwer.gui.edit.dkrfpatch import _DarkOrFlatUrl
from silx.io.url import DataUrl
from silx.io.utils import get_data
from tomoscan.esrf.hdf5scan import ImageKey
from nxtomomill.utils import add_dark_flat_nx_file
from tomwer.core.scan.hdf5scan import HDF5TomoScan
import tempfile
import shutil
import numpy


@pytest.mark.skipif(skip_gui_test(), reason="skip gui test")
class TestDarkOrFlatUrl(TestCaseQt):
    """
    Test some critical utils of the _DarkOrFlatUrl widget
    """

    def setUp(self):
        TestCaseQt.setUp(self)
        self._widgetForDark = _DarkOrFlatUrl(
            parent=None, type_=ImageKey.DARK_FIELD, when="start"
        )
        self._widgetForFlat = _DarkOrFlatUrl(
            parent=None, type_=ImageKey.FLAT_FIELD, when="start"
        )
        self.output_folder = tempfile.mkdtemp()
        #
        hdf5_mock = MockHDF5(
            scan_path=self.output_folder,
            n_ini_proj=20,
            n_proj=20,
            create_ini_dark=True,
            create_ini_ref=True,
            create_final_ref=True,
        )
        self._scan = hdf5_mock.scan
        self.scan_url = DataUrl(
            file_path=self._scan.master_file, data_path=self._scan.entry
        )

    def tearDown(self):
        shutil.rmtree(self.output_folder)
        self._widgetForDark.setAttribute(qt.Qt.WA_DeleteOnClose)
        self._widgetForDark.close()
        self._widgetForDark = None
        self._widgetForFlat.setAttribute(qt.Qt.WA_DeleteOnClose)
        self._widgetForFlat.close()
        self._widgetForFlat = None
        TestCaseQt.tearDown(self)

    def testSetUrlForFlat(self):
        self._widgetForFlat.setUrl(self.scan_url)
        self.assertEqual(self._widgetForFlat._optionsCB.count(), 3)
        data_url = self._widgetForFlat._redirectDataPath(self.scan_url)
        image_keys = self._widgetForFlat._getImageKey(data_url)
        self.assertTrue(image_keys is not None)
        slices_index_0 = self._widgetForFlat._getSlices(image_keys, 0)
        self.assertTrue(slices_index_0 is not None)
        self.assertEqual(
            list(range(slices_index_0.start, slices_index_0.stop)),
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        )
        slices_index_1 = self._widgetForFlat._getSlices(image_keys, 1)
        self.assertTrue(slices_index_1 is not None)
        self.assertEqual(slices_index_1, slice(31, 41))

    def testSetUrlForDark(self):
        self._widgetForDark.setUrl(self.scan_url)
        self._widgetForDark.show()
        self.assertEqual(self._widgetForDark._optionsCB.count(), 2)
        data_url = self._widgetForDark._redirectDataPath(self.scan_url)
        image_keys = self._widgetForDark._getImageKey(data_url)
        slices_index_0 = self._widgetForDark._getSlices(image_keys, 0)
        self.assertEqual(
            list(range(slices_index_0.start, slices_index_0.stop)),
            [
                0,
            ],
        )

        slices_index_1 = self._widgetForDark._getSlices(image_keys, 1)
        self.assertTrue(slices_index_1 is None)


@pytest.mark.skipif(skip_gui_test(), reason="skip gui test")
class TestDarkRefPatchWidget(TestCaseQt):
    """
    Simple test to insure DarkRefWidget is working
    """

    def setUp(self):
        TestCaseQt.setUp(self)
        self._widget = DarkRefPatchWidget(parent=None)
        self.output_folder1 = tempfile.mkdtemp()
        self.output_folder2 = tempfile.mkdtemp()

        hdf5_mock = MockHDF5(
            scan_path=self.output_folder1,
            n_ini_proj=20,
            n_proj=20,
            create_ini_dark=True,
            create_ini_ref=True,
            create_final_ref=True,
        )
        self._scanWithDarkAndRef = hdf5_mock.scan

        hdf5_mock = MockHDF5(
            scan_path=self.output_folder2,
            n_ini_proj=20,
            n_proj=20,
            create_ini_dark=False,
            create_ini_ref=False,
            create_final_ref=False,
        )
        self._scan = hdf5_mock.scan
        assert len(self._scan.darks) == 0
        assert len(self._scan.flats) == 0

    def tearDown(self):
        shutil.rmtree(self.output_folder1)
        shutil.rmtree(self.output_folder2)
        self._widget.setAttribute(qt.Qt.WA_DeleteOnClose)
        self._widget.close()
        self._widget = None
        self.qapp.processEvents()
        TestCaseQt.tearDown(self)

    def testEdition(self):
        # insure the widget work and post processing made by the application
        # and the widget succeed to
        url = DataUrl(
            file_path=self._scanWithDarkAndRef.master_file,
            data_path=self._scanWithDarkAndRef.entry,
        )
        self._widget.setStartDarkUrl(url, serie_index=0)
        self._widget.setStartFlatUrl(url, serie_index=1)
        self.assertTrue(self._widget.getStartDarkUrl() is not None)
        self.assertTrue(self._widget.getStartDarkUrl().is_valid())
        self.assertTrue(self._widget.getStartFlatUrl() is not None)
        self.assertTrue(self._widget.getStartFlatUrl().is_valid())
        self.assertTrue(self._widget.getEndDarkUrl() is None)
        self.assertTrue(self._widget.getEndFlatUrl() is None)
        self.process()
        new_scan = HDF5TomoScan(scan=self._scan.master_file, entry=self._scan.entry)
        self.assertEqual(len(new_scan.darks), 1)
        self.assertTrue(0 in new_scan.darks)
        numpy.testing.assert_array_equal(
            get_data(new_scan.darks[0]),
            get_data(self._scanWithDarkAndRef.darks[0]),
        )

        self.assertEqual(len(self._scanWithDarkAndRef.flats), 20)
        self.assertEqual(len(new_scan.flats), 10)

        self.assertEqual(tuple(new_scan.flats.keys()), tuple(range(1, 11)))
        numpy.testing.assert_array_equal(
            get_data(new_scan.flats[1]),
            get_data(self._scanWithDarkAndRef.flats[31]),
        )
        numpy.testing.assert_array_equal(
            get_data(new_scan.flats[10]),
            get_data(self._scanWithDarkAndRef.flats[40]),
        )

    def process(self):
        url_sd = self._widget.getStartDarkUrl()
        url_sf = self._widget.getStartFlatUrl()
        url_ed = self._widget.getEndDarkUrl()
        url_ef = self._widget.getEndFlatUrl()
        add_dark_flat_nx_file(
            file_path=self._scan.master_file,
            entry=self._scan.entry,
            darks_start=url_sd,
            flats_start=url_sf,
            darks_end=url_ed,
            flats_end=url_ef,
        )


def suite():
    test_suite = unittest.TestSuite()
    for ui in (TestDarkRefPatchWidget, TestDarkOrFlatUrl):
        test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ui))
    return test_suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
