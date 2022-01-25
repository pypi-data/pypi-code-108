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
"""some utils relative to PyHST
"""

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "17/02/2021"


from silx.gui import qt
import numpy


class LogSlider(qt.QWidget):
    """Slider to select a value with a QSlider displayed with log scale"""

    valueChanged = qt.Signal(float)
    """signal emitted when the value changed"""

    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QGridLayout())
        # QSlider
        self._slider = qt.QSlider(self)
        self._slider.setOrientation(qt.Qt.Horizontal)
        self.layout().addWidget(self._slider, 0, 0, 1, 1)
        # Double spin box
        self._valueQBSB = qt.QDoubleSpinBox(self)
        self.layout().addWidget(self._valueQBSB, 0, 1, 1, 1)

        # connect signal / slot
        self._slider.valueChanged.connect(self._sliderValueChanged)
        self._valueQBSB.valueChanged.connect(self._qdsbValueChanged)
        # set up
        self.setRange(1, 100)
        self.setValue(5)

    def setSuffix(self, txt):
        self._valueQBSB.setSuffix(txt)

    def setPrefix(self, txt):
        self._valueQBSB.setPrefix(txt)

    def setRange(self, min_: float, max_: float) -> None:
        """
        Define slider range

        :param float min_:
        :param float max_:
        """
        if min_ <= 0.0 or max_ <= 0.0:
            raise ValueError("LogSlider can only handled positive values")
        self._valueQBSB.setRange(min_, max_)
        self._slider.setRange(numpy.log(min_), numpy.log(max_))

    def _sliderValueChanged(self, *args, **kwargs):
        old = self._valueQBSB.blockSignals(True)
        self._valueQBSB.setValue(numpy.exp(self._slider.value()))
        self._valueQBSB.blockSignals(old)
        self.valueChanged.emit(self.value())

    def _qdsbValueChanged(self, *args, **kwargs):
        old = self._slider.blockSignals(True)
        self._slider.setValue(numpy.log(self._valueQBSB.value()))
        self._slider.blockSignals(old)
        self.valueChanged.emit(self.value())

    def value(self):
        return self._valueQBSB.value()

    def setValue(self, value):
        self._valueQBSB.setValue(value)


class _TickBar(qt.QWidget):
    _FONT_SIZE = 6

    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)
        self._min = 1
        self._max = 100
        self._ticks = {}

    def setRange(self, min_, max_):
        self._min = min_
        self._max = max_
        tick_names = self._ticks.values()
        for tick_name in tick_names:
            tick_value = self._ticks[tick_name]
            self._ticks[tick_name] = min(max(self._min, tick_value), self._max)

    def addTick(self, name, value):
        value = min(max(self._valueQBSB.minimum(), value), self._valueQBSB.maximum())
        self._ticks[name] = value

    def paintEvent(self, event):
        painter = qt.QPainter(self)
        font = painter.font()
        font.setPixelSize(_TickBar._FONT_SIZE)
        painter.setFont(font)

        # paint ticks
        for tick_name, tick_value in self._ticks.items():
            self._paintTick(tick_value, painter, majorTick=True)

    def _getRelativePosition(self, val):
        """Return the relative position of val according to min and max value"""
        if self._normalizer is None:
            return 0.0
        normMin, normMax, normVal = self._normalizer.apply(
            [self._vmin, self._vmax, val], self._vmin, self._vmax
        )

        if normMin == normMax:
            return 0.0
        else:
            return 1.0 - (normVal - normMin) / (normMax - normMin)

    def _paintTick(self, val, painter, majorTick=True):
        """

        :param bool majorTick: if False will never draw text and will set a line
            with a smaller width
        """
        fm = qt.QFontMetrics(painter.font())
        viewportHeight = self.rect().height() - self.margin * 2 - 1
        relativePos = self._getRelativePosition(val)
        height = int(viewportHeight * relativePos + self.margin)
        lineWidth = _TickBar._LINE_WIDTH
        if majorTick is False:
            lineWidth /= 2

        painter.drawLine(
            qt.QLine(int(self.width() - lineWidth), height, self.width(), height)
        )

        if self.displayValues and majorTick is True:
            painter.drawText(
                qt.QPoint(0, int(height + fm.height() / 2)), self.form.format(val)
            )


class LogSliderWithTick(LogSlider):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # register ticks to be displayed with name as key and value as value
        # Double spin box
        self._ticksBar = _TickBar(self)
        self.layout().addWidget(self._ticksBar, 1, 0, 1, 1)

    def addTick(self, name, value):
        self._ticksBar.addTick(name, value)

    def setRange(self, min_: float, max_: float) -> None:
        super().setRange(min_=min_, max_=max_)
        if hasattr(self, "_ticksBar"):
            self._ticksBar.setRange(min_=min_, max_=max_)

    def clearTicks(self):
        self._ticks.clear()


if __name__ == "__main__":
    app = qt.QApplication([])
    slider = LogSliderWithTick()
    slider.setFixedWidth(250)
    # slider.addTick("toto", 1)
    # slider.addTick("tata", 10)
    # slider.addTick("titi", 100)
    slider.setRange(0.01, 1000)
    slider.setValue(10)
    slider.show()
    app.exec_()
