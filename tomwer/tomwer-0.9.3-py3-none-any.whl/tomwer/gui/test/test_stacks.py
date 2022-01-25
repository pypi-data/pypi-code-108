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
__date__ = "16/06/2021"

from tomwer.gui.stackplot import ImageFromFile
from tomwer.gui.stacks import SliceStack, RadioStack
from tomwer.test.utils import UtilsTest
from silx.gui import qt
from silx.gui.utils.testutils import TestCaseQt
import logging
import time
import pytest
from tomwer.gui.qtapplicationmanager import QApplicationManager
from tomwer.test.utils import skip_gui_test
import weakref

_qapp = QApplicationManager()

logging.disable(logging.INFO)


@pytest.mark.skipif(skip_gui_test(), reason="skip gui test")
class TestSliceStack(TestCaseQt):
    """unit test for the :class:_ImageStack widget"""

    def setUp(self):
        TestCaseQt.setUp(self)
        self._widget = SliceStack()
        self._widget.setAttribute(qt.Qt.WA_DeleteOnClose)

    def tearDown(self):
        self._widget.close()
        self._widget = None
        self.qapp.processEvents()
        TestCaseQt.tearDown(self)

    def test(self):
        """Make sur the addLeaf and clear functions are working"""
        self._widget.setLoadingMode("load when show requested")
        folder = UtilsTest.getEDFDataset("D2_H2_T2_h_")
        self.assertTrue(self._widget._viewer.getActiveImage() is None)

        self.assertEqual(len(self._widget._scans), 0)
        self._widget.addLeafScan(folder)
        self.assertEqual(len(self._widget._scans), 1)
        # some delay to wait for the ImageLoaderThread
        time.sleep(0.3)
        _qapp.processEvents()
        self.assertTrue(self._widget._viewer.getActiveImage() is not None)
        self._widget.clear()
        self.assertEqual(len(self._widget._scans), 0)
        self.assertTrue(self._widget._viewer.getActiveImage() is None)

        self._widget.addLeafScan(folder)
        self.assertEqual(len(self._widget._scans), 1)
        # some delay to wait for the ImageLoaderThread
        time.sleep(0.3)
        _qapp.processEvents()
        self.assertTrue(self._widget._viewer.getActiveImage() is not None)


@pytest.mark.skipif(skip_gui_test(), reason="skip gui test")
class TestRadioStack(TestCaseQt):
    """Test for the RadioStack"""

    def setUp(self):
        TestCaseQt.setUp(self)
        self._widget = RadioStack()
        self._widget.setAttribute(qt.Qt.WA_DeleteOnClose)
        self.spinBox = weakref.ref(self._widget._viewer._qspinbox)
        self.slider = weakref.ref(self._widget._viewer._qslider)

    def tearDown(self):
        self._widget.close()
        self._widget = None
        self.qapp.processEvents()
        TestCaseQt.tearDown(self)

    def _waitImages(self):
        _qapp.processEvents()
        time.sleep(0.2)
        _qapp.processEvents()

    def testASAPMode(self):
        self._widget.setLoadingMode("load ASAP")
        folder = UtilsTest.getEDFDataset("D2_H2_T2_h_")
        self._widget.setForceSync(True)
        self._widget.addLeafScan(folder)
        # wait for all images to be loaded
        self._waitImages()

        self.assertEqual(
            self._getStatsLoadedImage(self._widget._viewer.images), (3600, 0, 0)
        )

        self.spinBox().setValue(20)
        self._waitImages()

        self.assertEqual(
            self._getStatsLoadedImage(self._widget._viewer.images), (3600, 0, 0)
        )
        self.slider().setValue(10)
        _qapp.processEvents()
        self.assertEqual(
            self._getStatsLoadedImage(self._widget._viewer.images), (3600, 0, 0)
        )

    def testLazyLoadingMode(self):
        self._widget.setLoadingMode("lazy loading")
        folder = UtilsTest.getEDFDataset("D2_H2_T2_h_")
        self._widget.addLeafScan(folder)
        self._waitImages()
        self.assertEqual(
            self._getStatsLoadedImage(self._widget._viewer.images), (1, 0, 3599)
        )

        self.spinBox().setValue(20)
        self._waitImages()

        self.assertEqual(
            self._getStatsLoadedImage(self._widget._viewer.images), (1, 0, 3599)
        )
        self.slider().setValue(10)
        self._waitImages()

        self.assertEqual(
            self._getStatsLoadedImage(self._widget._viewer.images), (1, 0, 3599)
        )

        self.spinBox().editingFinished.emit()
        self._waitImages()
        self.assertEqual(
            self._getStatsLoadedImage(self._widget._viewer.images), (2, 0, 3598)
        )

    def testOnShowLoading(self):
        self._widget.setLoadingMode("load when show requested")
        folder = UtilsTest.getEDFDataset("D2_H2_T2_h_")
        self._widget.addLeafScan(folder)
        # wait for all images to be loaded
        self._waitImages()

        self.assertEqual(
            self._getStatsLoadedImage(self._widget._viewer.images), (1, 0, 3599)
        )

        self.spinBox().setValue(20)
        self._waitImages()

        self.assertEqual(
            self._getStatsLoadedImage(self._widget._viewer.images), (2, 0, 3598)
        )
        self.slider().setValue(10)
        self._waitImages()

        self.assertEqual(
            self._getStatsLoadedImage(self._widget._viewer.images), (3, 0, 3597)
        )

    def _getStatsLoadedImage(self, images):
        """

        :param images:
        :return: nLoaded, NLoading, NNotLoaded
        """
        nLoaded = nLoading = nNotLoaded = 0
        for imgIndex, img in images._images.items():
            assert isinstance(img, ImageFromFile)
            nLoaded += int(img._status == "loaded")
            nLoading += int(img._status == "loading")
            nNotLoaded += int(img._status == "not loaded")
        return (nLoaded, nLoading, nNotLoaded)
