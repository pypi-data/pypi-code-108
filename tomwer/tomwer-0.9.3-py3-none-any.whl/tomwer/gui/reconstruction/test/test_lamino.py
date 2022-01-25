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
__date__ = "16/06/2021"


import os
import shutil
import tempfile
import unittest
import pytest
from silx.gui import qt
from tomwer.core import settings
from tomwer.gui.reconstruction.lamino.tofu import TofuWindow
from tomwer.test.utils import UtilsTest
from tomwer.test.utils import skip_gui_test


@pytest.mark.skipif(skip_gui_test(), reason="skip gui test")
class TestLamino(unittest.TestCase):
    """Test the TofuWidget"""

    def setUp(self):
        super().setUp()
        self._window = TofuWindow(parent=None)
        self._widget = self._window._mainWidget
        # add a dark.edf file and a darkHSTFile
        self._folder = tempfile.mkdtemp()

    def tearDown(self):
        super().tearDown()
        self._window.setAttribute(qt.Qt.WA_DeleteOnClose)
        self._window.close()
        shutil.rmtree(self._folder)

    def testSetup(self):
        """Make sure the widget is correctly setting parameters from a scan"""
        dataset = UtilsTest.getEDFDataset("test01")
        self._window.loadFromScan(dataset)
        reconsParams = self._widget.getParameters()
        # check general information
        # note : the .info file is incorrect
        self.assertTrue(self._widget._tabs._inputWidget.getNumber() == 1)
        self.assertTrue(reconsParams["number"] == 1)
        # check flat field correction is set
        ffcWidget = self._widget._tabs._inputWidget.widget._ffcWidget
        thFlats = os.path.join(dataset, "refHST0000.edf")
        self.assertTrue(ffcWidget.getFlats() == thFlats)
        self.assertTrue(reconsParams["flats"] == thFlats)
        thSecondFlats = os.path.join(dataset, "refHST0010.edf")
        self.assertTrue(ffcWidget.getSecondFlats() == thSecondFlats)
        self.assertTrue(reconsParams["flats2"] == thSecondFlats)
        thDarks = os.path.join(dataset, "darkend0000.edf")
        self.assertTrue(ffcWidget.getDarks() == thDarks)
        self.assertTrue(reconsParams["darks"] == thDarks)

        inputWidget = self._widget._tabs._inputWidget.widget
        self.assertTrue(inputWidget.rotationAngle._overallAngle.getAngle() == 180.0)
        self.assertTrue(inputWidget.rotationAngle._axisAngleY.getAngle() == 0.0)
        self.assertTrue(inputWidget.rotationAngle._axisAngleZ.getAngle() == 0.0)

    def testSetupWithLockedParams(self):
        """Make sure lockers are corrcetly taking into account"""
        # check flat field correction is set

        inputWidget = self._widget._tabs._inputWidget.widget
        inputWidget.rotationAngle._overallAngle.setAngle(12.0)
        inputWidget.rotationAngle._overallAngle.lock()

        inputWidget.rotationAngle._axisAngleY.setAngle(-26.0)
        inputWidget.rotationAngle._axisAngleY.lock()

        inputWidget.rotationAngle._axisAngleZ.setAngle(63.5)
        inputWidget.rotationAngle._axisAngleZ.lock()

        outputWidget = self._widget._tabs._outputWidget
        outputWidget.setOutput("toto")
        outputWidget.lockOutput()

        dataset = UtilsTest.getEDFDataset("test01")
        self._window.loadFromScan(dataset)

        self.assertTrue(inputWidget.rotationAngle._overallAngle.getAngle() == 12.0)
        self.assertTrue(inputWidget.rotationAngle._axisAngleY.getAngle() == -26.0)
        self.assertTrue(inputWidget.rotationAngle._axisAngleZ.getAngle() == 63.5)

        self.assertTrue(outputWidget.getOutput() == "toto")

    def testEditionDisplay(self):
        """
        Test that edition of parameters by the user are taking into account
        """
        displayWidget = self._widget._tabs._inputWidget.widget.rotationAngle
        # angles
        displayWidget._laminoAngle.setAngle(12.0)
        self.assertTrue(self._widget.getParameters()["axis-angle-x"] == 12.0)
        displayWidget._axisAngleY.setAngle(10.0)
        self.assertTrue(self._widget.getParameters()["axis-angle-y"] == 10.0)

        # regions
        regionWidget = self._widget._tabs._outputWidget._region
        regionWidget._xRegion._regionLE.setText("0")
        self.assertTrue(self._widget.getParameters()["x-region"] == (0, -1, 1))
        regionWidget.setYRegion(10, 12, 25)
        self.assertTrue(self._widget.getParameters()["y-region"] == (10, 12, 25))

        # make sure saving and loading is correct
        savingFile = os.path.join(self._folder, "savingFile.ini")
        self._widget.saveTo(savingFile)
        self.assertTrue(os.path.exists(savingFile))
        regionWidget.setYRegion(10, 12, 22)
        self.assertTrue(self._widget.getParameters()["y-region"] == (10, 12, 22))
        self._widget.loadFile(savingFile)
        self.assertTrue(self._widget.getParameters()["y-region"] == (10, 12, 25))

    def testOutputWidget(self):
        """test behavior of the output widget and link with get and set
        parameters"""
        outputWidget = self._widget._tabs._outputWidget
        # volume angles
        outputWidget._volumeAngleGrp.setAngles(0, 20, -36.0)
        reconsParams = self._widget.getParameters()
        self.assertTrue(reconsParams["volume-angle-x"] == 0)
        self.assertTrue(reconsParams["volume-angle-y"] == 20.0)
        self.assertTrue(reconsParams["volume-angle-z"] == -36.0)

    def testCenteringWidget(self):
        """test behavior of the centering widget and link with get and set
        parameters"""
        centeringWidget = self._widget._tabs._inputWidget.widget.centeringWidget
        centeringWidget._xCenterLE.setText("12")
        centeringWidget._yCenterLE.setText("2")
        self.assertTrue(self._widget.getParameters()["center-position-x"] == 12.0)
        self.assertTrue(self._widget.getParameters()["center-position-z"] == 2.0)

    def testForceLbsRam(self):
        """Test the behavior of the forcelbsram option"""
        scan1 = tempfile.mkdtemp(suffix="1")
        self._window.loadFromScan(scan1)
        _end = os.path.join("1", "xySlice")
        self.assertTrue(self._window.getParameters()["output"].endswith(_end))

        self._window._mainWidget._tabs._outputWidget.lockOutput()
        scan2 = tempfile.mkdtemp(suffix="2")
        self._window.loadFromScan(scan2)
        _end = os.path.join("1", "xySlice")
        self.assertTrue(self._window.getParameters()["output"].endswith(_end))

        self._window._mainWidget._tabs._outputWidget.lockOutput(False)
        self._window.loadFromScan(scan2)
        _end = os.path.join("2", "xySlice")
        self.assertTrue(self._window.getParameters()["output"].endswith(_end))

        self._window._mainWidget._tabs._outputWidget.setForceLbsram(True)
        self.assertTrue(
            self._window.getParameters()["output"].startswith(
                settings.get_lbsram_path()
            )
        )
        self._window.loadFromScan(scan1)
        self.assertTrue(
            self._window.getParameters()["output"].startswith(
                settings.get_lbsram_path()
            )
        )
