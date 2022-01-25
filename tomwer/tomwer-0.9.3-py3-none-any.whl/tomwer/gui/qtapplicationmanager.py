# coding: utf-8
# /*##########################################################################
# Copyright (C) 2017 European Synchrotron Radiation Facility
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

"""
This module is used to manage the rsync between files for transfert.
"""

__authors__ = ["H.Payno"]
__license__ = "MIT"
__date__ = "11/04/2017"

from silx.gui import qt
from tomwer.core.utils.Singleton import singleton

# TODO: this should be removed


@singleton
class QApplicationManager(qt.QApplication):
    """Return a singleton on the CanvasApplication"""

    fileOpenRequest = qt.Signal(qt.QUrl)

    def __init__(self):
        qt.QApplication.__init__(self, [])
        self.setAttribute(qt.Qt.AA_DontShowIconsInMenus, True)

    def event(self, event):
        if event.type() == qt.QEvent.FileOpen:
            self.fileOpenRequest.emit(event.url())

        return qt.QApplication.event(self, event)
