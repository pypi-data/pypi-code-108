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
Button of general usage.
"""

__authors__ = ["H.Payno"]
__license__ = "MIT"
__date__ = "03/10/2018"


from silx.gui import qt
from tomwer.gui import icons


class PadlockButton(qt.QPushButton):
    """Simple button to define a button with PadLock icons"""

    sigLockChanged = qt.Signal(bool)
    """signal emitted when the lock status change"""

    def __init__(self, parent):
        qt.QPushButton.__init__(self, parent)
        self._lockIcon = icons.getQIcon("locked")
        self._unlockIcon = icons.getQIcon("unlocked")
        self.setIcon(self._unlockIcon)
        self.setCheckable(True)

        # add some speakfull API
        self.isLocked = self.isChecked

        # connect signals
        self.toggled.connect(self._updateDisplay)

    def setLock(self, lock):
        self.setChecked(lock)
        self._updateDisplay(lock)

    def _updateDisplay(self, checked):
        _icon = self._lockIcon if checked else self._unlockIcon
        self.setIcon(_icon)
        self.sigLockChanged.emit(checked)


class TabBrowsersButtons(qt.QWidget):
    """Simple widget containing buttons to go to 'next' or 'previous'"""

    sigPreviousReleased = qt.Signal()
    """emitted when the previous button is released"""
    sigNextReleased = qt.Signal()
    """emitted when the next button is released"""

    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QHBoxLayout())
        # define gui
        style = qt.QApplication.style()
        self._previousButton = qt.QPushButton("previous", self)
        previous_icon = style.standardIcon(qt.QStyle.SP_ArrowLeft)
        self._previousButton.setIcon(previous_icon)
        self.layout().addWidget(self._previousButton)

        self._nextButton = qt.QPushButton("next", self)
        next_icon = style.standardIcon(qt.QStyle.SP_ArrowRight)
        self._nextButton.setIcon(next_icon)
        self.layout().addWidget(self._nextButton)
        spacer = qt.QWidget(self)
        spacer.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum)
        self.layout().addWidget(spacer)

        # connect signal / slot
        self._previousButton.released.connect(self._previousReleased)
        self._nextButton.released.connect(self._nextReleased)

    def _previousReleased(self, *args, **kwargs):
        self.sigPreviousReleased.emit()

    def _nextReleased(self, *args, **kwargs):
        self.sigNextReleased.emit()
