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


from tomwer.gui.utils import inputwidget
from tomwer.test.utils import skip_gui_test
from silx.gui.utils.testutils import TestCaseQt
from silx.gui import qt
import numpy
import pytest


@pytest.mark.skipif(skip_gui_test(), reason="skip gui test")
class SelectionLineEditTest(TestCaseQt):
    """Test the SelectionLineEdit"""

    def setUp(self):
        super().setUp()
        self.widget = inputwidget.SelectionLineEdit(parent=None)

    def tearDown(self):
        self.widget.setAttribute(qt.Qt.WA_DeleteOnClose)
        self.widget.close()
        self.widget = None
        super().tearDown()

    def testListSelection(self):
        self.widget.mode = inputwidget.SelectionLineEdit.LIST_MODE
        self.widget.setText("1.0, 2.0; 6.3")
        self.assertTrue(self.widget.selection == (1.0, 2.0, 6.3))
        self.widget.setText("1.0:3.6:0.2")
        self.assertTrue(
            self.widget.selection == tuple(numpy.linspace(1.0, 3.6, num=int(2.6 / 0.2)))
        )
        self.assertTrue(
            self.widget.getMode() == inputwidget.SelectionLineEdit.RANGE_MODE
        )
        self.widget.setText("1.0")
        self.assertTrue(self.widget.selection == 1.0)

    def testRangeSelection(self):
        self.widget.mode = inputwidget.SelectionLineEdit.RANGE_MODE
        self.widget.setText("1.0:3.6:0.2")
        self.assertTrue(
            self.widget.selection == tuple(numpy.linspace(1.0, 3.6, num=int(2.6 / 0.2)))
        )
        self.widget.setText("1.0")
        self.assertTrue(self.widget.selection == 1.0)
        self.widget.setText("1.0, 2.0, 6.3")
        self.assertTrue(
            self.widget.getMode() == inputwidget.SelectionLineEdit.LIST_MODE
        )
        self.assertTrue(self.widget.selection == (1.0, 2.0, 6.3))
