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


import unittest
import pytest
from silx.gui import qt
from silx.gui.utils.testutils import TestCaseQt

from tomwer.core.process.reconstruction.ftseries.params.fastsetupdefineglobals import (
    FastSetupAll,
)
from tomwer.core.utils.pyhstutils import _findPyHSTVersions, _getPyHSTDir
from tomwer.gui.reconstruction.ftserie import FtserieWidget
from tomwer.gui.qtapplicationmanager import QApplicationManager
from tomwer.gui.reconstruction.recpyhstwidget import RecPyHSTWidget
from tomwer.synctools.ftseries import QReconsParams
from tomwer.test.utils import skip_gui_test

pyhstVersion = _findPyHSTVersions(_getPyHSTDir())
_qapp = QApplicationManager()


@pytest.mark.skipif(skip_gui_test(), reason="skip gui test")
class TestRecPyHSTWidget(TestCaseQt):
    """Make sure the gui is correctly editing the ReconsParam and the
    RecPyHST class
    """

    def setUp(self):
        self._recons_params = QReconsParams()
        self.ftserieWidget = FtserieWidget(recons_params=self._recons_params)
        self.ftserieWidget.setAttribute(qt.Qt.WA_DeleteOnClose)

        self.widget = RecPyHSTWidget(
            parent=None, recons_params=self._recons_params.pyhst
        )
        self.widget.setAttribute(qt.Qt.WA_DeleteOnClose)
        assert id(self.ftserieWidget.recons_params.pyhst) == id(
            self._recons_params.pyhst
        )
        assert id(self.widget.recons_params) == id(self._recons_params.pyhst)

    def tearDown(self):
        self.widget.close()
        self.ftserieWidget.close()

    @pytest.mark.skipif(len(pyhstVersion) == 0, reason="PyHST2 missing")
    def testUpdating(self):
        """Check behavior of the gui when editing the self.recons_params
        Make sure also that sync with the ftserie is made
        """
        pyhstWidget = self.ftserieWidget.getReconsParamSetEditor()._PyHSTWidget

        # Test make oar
        isMakeOAR = self.widget.recons_params["MAKE_OAR_FILE"]
        self.assertTrue(self.widget._makeOARFileCB.isChecked() == isMakeOAR)
        self.assertTrue(pyhstWidget._makeOARFileCB.isChecked() == isMakeOAR)
        self.widget.recons_params["MAKE_OAR_FILE"] = not isMakeOAR
        self.assertTrue(self.widget._makeOARFileCB.isChecked() != isMakeOAR)
        self.assertTrue(pyhstWidget._makeOARFileCB.isChecked() != isMakeOAR)

        # test pyhst version
        self.assertTrue(self.widget._qcbPyHSTVersion.currentText() == FastSetupAll.OFFV)
        self.assertTrue(pyhstWidget._qcbPyHSTVersion.currentText() == FastSetupAll.OFFV)
        self._recons_params["PYHSTEXE"]["EXE"] = "toto"
        self.assertTrue(pyhstWidget._qcbPyHSTVersion.currentText() == "toto")
        self.assertTrue(self.widget._qcbPyHSTVersion.currentText() == "toto")

    @pytest.mark.skipif(len(pyhstVersion) == 0, reason="PyHST2 missing")
    def testEdition(self):
        """Check behavior of ReconsParam when editing i through the gui"""
        pyhstWidget = self.ftserieWidget.getReconsParamSetEditor()._PyHSTWidget

        # Test make oar
        oVal = self.widget._makeOARFileCB.isChecked()
        self.assertTrue(oVal == pyhstWidget._makeOARFileCB.isChecked())
        self.widget._makeOARFileCB.setChecked(not oVal)
        self.qapp.processEvents()

        self.assertTrue(self.widget.recons_params["MAKE_OAR_FILE"] != oVal)
        self.assertFalse(oVal == pyhstWidget._makeOARFileCB.isChecked())
        pyhstWidget._makeOARFileCB.setChecked(oVal)
        self.assertTrue(self.widget._makeOARFileCB.isChecked() == oVal)
        self.assertTrue(self.widget.recons_params["MAKE_OAR_FILE"] == oVal)

        # test pyhst version
        oExe = self.widget.recons_params["EXE"] = "toto"
        self.assertTrue(self.widget._qcbPyHSTVersion.currentText() == oExe)
        self.assertTrue(pyhstWidget._qcbPyHSTVersion.currentText() == oExe)
        self.widget._qcbPyHSTVersion.addItem("toto")
        iToto = self.widget._qcbPyHSTVersion.findText("toto")
        self.assertTrue(iToto > 0)
        self.widget._qcbPyHSTVersion.setCurrentIndex(iToto)
        self.assertTrue(self.widget._qcbPyHSTVersion.currentText() == "toto")
        self.assertTrue(pyhstWidget._qcbPyHSTVersion.currentText() == "toto")
        self.assertTrue(self.widget.recons_params["EXE"] == "toto")
        iOExe = self.widget._qcbPyHSTVersion.findText(oExe)
        self.assertTrue(iOExe > 0)
        pyhstWidget._qcbPyHSTVersion.setCurrentIndex(iOExe)
        self.assertTrue(self.widget._qcbPyHSTVersion.currentText() == oExe)
        self.assertTrue(pyhstWidget._qcbPyHSTVersion.currentText() == oExe)
        self.assertTrue(self.widget.recons_params["EXE"] == oExe)


def suite():
    test_suite = unittest.TestSuite()
    for ui in (TestRecPyHSTWidget,):
        test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ui))
    return test_suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
