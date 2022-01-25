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
__date__ = "09/11/2020"


import unittest
import pytest
from silx.gui import qt
from silx.gui.utils.testutils import TestCaseQt
from tomwer.test.utils import skip_gui_test
from tomwer.gui.control.datalistener import ConfigurationWidget
from silx.gui.utils.testutils import SignalListener


@pytest.mark.skipif(skip_gui_test(), reason="skip gui test")
class TestProcessManager(TestCaseQt):
    """
    Simple test on behavior of the ProcessManager
    """

    def setUp(self):
        TestCaseQt.setUp(self)
        self._configWidget = ConfigurationWidget(parent=None)
        self.sig_listener = SignalListener()
        self._configWidget.sigConfigurationChanged.connect(self.sig_listener)
        self._configWidget.setHost("localhost")

    def tearDown(self):
        self._configWidget.setAttribute(qt.Qt.WA_DeleteOnClose)
        self._configWidget.close()
        self._configWidget = None
        TestCaseQt.tearDown(self)

    def testConfiguration(self):
        self.assertEqual(
            self._configWidget.getConfiguration(), {"host": "localhost", "port": 4000}
        )
        self._configWidget.setPort(0)
        self._configWidget.setHost("toto")
        self.assertEqual(
            self._configWidget.getConfiguration(), {"host": "toto", "port": 0}
        )


def suite():
    test_suite = unittest.TestSuite()
    for ui in (TestProcessManager,):
        test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ui))
    return test_suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
