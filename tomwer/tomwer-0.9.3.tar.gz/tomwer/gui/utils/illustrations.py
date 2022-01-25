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
Some utils GUI associated to illustrations
"""

__authors__ = ["H.Payno"]
__license__ = "MIT"
__date__ = "28/09/2018"


from silx.gui import qt
from tomwer.gui import illustrations


class _IllustrationWidget(qt.QWidget):
    """Simple widget to display an image keeping the aspect ratio"""

    def __init__(self, parent, img=None):
        qt.QWidget.__init__(self, parent)
        self._ratio = 1.0
        self._oPixmap = None
        """Pixmap containing the image to display"""

        self.setLayout(qt.QGridLayout())
        try:
            self._display = qt.QSvgWidget(parent=self)
            self._use_svg = True
        except Exception:
            self._display = qt.QLabel(parent=self)
            self._use_svg = False
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self._display.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)

        self.layout().addWidget(self._display, 0, 0)
        spacer1 = qt.QWidget(self)
        spacer1.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.MinimumExpanding)
        self.layout().addWidget(spacer1, 0, 1)
        spacer2 = qt.QWidget(self)
        spacer2.setSizePolicy(qt.QSizePolicy.MinimumExpanding, qt.QSizePolicy.Minimum)
        self.layout().addWidget(spacer2, 1, 0)

        if img:
            assert isinstance(img, str)
            self.setImage(img)

    def heightForWidth(self, width):
        return width * self._ratio

    def widthForHeight(self, height):
        return height / self._ratio

    def resizeEvent(self, event):
        width = event.size().width()
        height = self.heightForWidth(width)
        if height > event.size().height():
            height = event.size().height()
            width = self.widthForHeight(height)

        self._display.resize(width, height)
        if self.isUsingSvg() is False:
            self._updatePixamp()

    def setImage(self, image):
        _image = image.replace(" ", "_")
        self._ratio = 1.0
        self._oPixmap = illustrations.getQPixmap(_image)
        self._ratio = self._oPixmap.height() / self._oPixmap.width()

        if type(self._display) is qt.QLabel:
            self._updatePixamp()
        else:
            self._display.load(illustrations.getResourceFileName(_image + ".svg"))

    def _updatePixamp(self):
        pixmap = self._oPixmap.scaled(self.width(), self.height())
        self._display.setPixmap(pixmap)

    def isUsingSvg(self):
        return self._use_svg


class _IllustrationDialog(qt.QDialog):
    def __init__(self, parent, title, img):
        qt.QDialog.__init__(self, parent)
        self.setWindowTitle(title)
        self.setLayout(qt.QVBoxLayout())
        self._illustration = _IllustrationWidget(parent=self, img=img)
        self.layout().addWidget(self._illustration)

        types = qt.QDialogButtonBox.Ok
        self.__buttons = qt.QDialogButtonBox(parent=self)
        self.__buttons.setStandardButtons(types)
        self.layout().addWidget(self.__buttons)

        self.__buttons.accepted.connect(self.accept)

    def sizeHint(self):
        return qt.QSize(300, 300)
