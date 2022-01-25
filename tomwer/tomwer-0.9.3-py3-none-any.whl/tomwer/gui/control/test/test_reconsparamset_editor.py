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


import numpy
from silx.gui import qt
from silx.gui.utils.testutils import TestCaseQt
import pytest
from tomwer.gui.reconstruction.ftserie.reconsparamseditor import ReconsParamSetEditor
from tomwer.test.utils import skip_gui_test
import gc


@pytest.mark.skipif(skip_gui_test(), reason="skip gui test")
class TestReconsParamSet(TestCaseQt):
    """
    Test the ReconsParamSetEditor.
    Make sure we can iterate over the set of ReconsParams
    """

    def setUp(self):
        super().setUp()
        self.widget = ReconsParamSetEditor(parent=None)

    def tearDown(self):
        self.widget.setAttribute(qt.Qt.WA_DeleteOnClose)
        self.widget.close()
        self.widget = None
        self.qapp.processEvents()
        gc.collect()
        super().tearDown()

    def testSeveralPaganin(self):
        iMulti = self.widget._PaganinWidget._qcbpaganin.findText("multi")
        assert iMulti >= 0
        self.widget._PaganinWidget._qcbpaganin.setCurrentIndex(iMulti)
        self.widget._PaganinWidget._qleSigmaBeta.setText("1, 2, 3")
        self.widget._PaganinWidget._qleSigmaBeta.editingFinished.emit()
        self.widget._PaganinWidget._qleSigmaBeta2.setText("0:10:2")
        self.widget._PaganinWidget._qleSigmaBeta2.editingFinished.emit()
        qt.qApp.processEvents()
        reconsParamList = self.widget.getReconsParamSet()
        assert len(reconsParamList) == (5 * 3)
        combinations = []
        for db in (1, 2, 3):
            num = 5
            for db2 in numpy.linspace(0, 10, num=num, endpoint=True):
                combinations.append((db, db2))
        for param in reconsParamList:
            c = (param["PAGANIN"]["DB"], param["PAGANIN"]["DB2"])
            assert c in combinations
            combinations.remove(c)
