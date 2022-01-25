# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
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
"""
contains gui to select a slice in a volume
"""


__authors__ = [
    "H. Payno",
]

__license__ = "MIT"
__date__ = "04/02/2021"


from silx.gui import qt
from silx.gui.plot import PlotWidget
import functools
import numpy


# class SliceSelectorWithMiddle(qt.QWidget):


class SliceSelector(qt.QWidget):
    """
    Allow definition of n slices with a volume slice selector and spin boxes
    :param bool insert: if True add spin boxes at the beginning of the layout
                        otherwise append them
    """

    sigSlicesChanged = qt.Signal()
    """signal emitted when slices value change"""

    def __init__(self, parent=None, insert=True, invert_y_axis=False):
        self._updatePlaneFrmSBLock = False
        self._insert = insert
        self._slicesQSB = []
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QBoxLayout(qt.QBoxLayout.BottomToTop))
        self._volumeView = _SliceSelectorFrmVolume(self, invert_y_axis=invert_y_axis)
        self.layout().addWidget(self._volumeView)

        # expose API
        self.getSlicesValue = self._volumeView.getSlicesValue
        self.getSlicesRange = self._volumeView.getSlicesRange
        self.setSliceValue = self._volumeView.setSliceValue

    def getSlicesRange(self) -> tuple:
        return self._volumeView.getSlicesRange()

    def setSlicesRange(self, min_index, max_index):
        self._volumeView.setSlicesRange(min_index, max_index)
        for widget in self._slicesQSB:
            widget.sliceSB.setRange(min_index, max_index)

    def clearSlices(self):
        self._volumeView.clearSlices()
        for sliceQSB in self._slicesQSB:
            self.layout().removeWidget(sliceQSB)
        self._slicesQSB.clear()

    def addSlice(self, value, name, color):
        self._volumeView.addSlice(value=value, name=name, color=color)
        # create the spin box
        widget = qt.QWidget(self)
        widget.setLayout(qt.QHBoxLayout())
        widget.layout().setContentsMargins(0, 0, 0, 0)
        widget.layout().addWidget(qt.QLabel(name, self))
        sb = qt.QSpinBox(self)
        stylesheet = "background-color: {}".format(color)
        sb.setStyleSheet(stylesheet)

        min_i, max_i = self.getSlicesRange()
        sb.setRange(min_i, max_i)
        sb.setValue(value)
        widget.sliceSB = sb
        widget.layout().addWidget(sb)

        if self._insert:
            self.layout().insertWidget(0, widget)
        else:
            self.layout().addWidget(widget)
        self._slicesQSB.append(widget)

        # connect signal / slot
        sb.valueChanged.connect(functools.partial(self._updatePlaneFrmSB, name, sb))
        sb.valueChanged.connect(self._slicesChanged)
        marker = self._volumeView._getMarker(self._volumeView.getMarkerName(name))
        marker.sigDragFinished.connect(
            functools.partial(self._updateSBFrmMarker, sb, marker)
        )
        marker.sigDragFinished.connect(self._slicesChanged)
        # TODO: we might want to change the plane position when moving the
        # marker. This would require to add a loop when drag start and stop
        # it when drag is finished

    def _slicesChanged(self):
        if not self._updatePlaneFrmSBLock:
            self.sigSlicesChanged.emit()

    def _updatePlaneFrmSB(self, name: str, sb: qt.QSpinBox):
        """callback when a spin box value change from user input"""
        self._updatePlaneFrmSBLock = True
        old = self._volumeView.blockSignals(True)
        marker = self._volumeView._getMarker(self._volumeView.getMarkerName(name))
        marker.setPosition(x=0, y=self._volumeView.valueToPlotSpace(value=sb.value()))
        marker.sigDragFinished.emit()
        self._volumeView.blockSignals(old)
        self._updatePlaneFrmSBLock = False

    def _updateSBFrmMarker(self, sb: qt.QSpinBox, marker):
        if not self._updatePlaneFrmSBLock:
            position = self._volumeView.plotSpaceToValue(marker.getPosition()[1])
            sb.setValue(position)


class _SliceSelectorFrmVolume(PlotWidget):
    """
    Allow definition of n slices on a volume
    """

    sigSlicesChanged = qt.Signal()
    """signal emitted when slices value change"""

    ORIENTATION = -numpy.pi / 2.0
    LOW_RADIUS = 0.4
    HIGH_RADIUS = 1.0
    HEIGHT = 3.0
    PLOT_MARGINS = 1.0

    def __init__(self, parent=None, invert_y_axis=False):
        self._yAxisInverted = invert_y_axis
        PlotWidget.__init__(self, parent)
        self.setAxesDisplayed(False)
        self._plotVolume()
        self.getXAxis().setLimits(-(self.PLOT_MARGINS + 0.5), self.PLOT_MARGINS + 0.5)
        self.getYAxis().setLimits(-self.PLOT_MARGINS, self.HEIGHT + self.PLOT_MARGINS)
        self._slices = []
        self._slicesRange = (0, 1)

        # Retrieve PlotWidget's plot area widget
        plotArea = self.getWidgetHandle()

        # Set plot area custom context menu
        plotArea.setContextMenuPolicy(qt.Qt.CustomContextMenu)
        plotArea.customContextMenuRequested.connect(self._contextMenu)
        self.setInteractiveMode("select", zoomOnWheel=False)
        self.setPanWithArrowKeys(False)

    def _contextMenu(self, pos):
        """Handle plot area customContextMenuRequested signal.

        :param QPoint pos: Mouse position relative to plot area
        """
        # avoir rest zoom action
        pass

    def setSlicesRange(self, min_index, max_index):
        if not isinstance(min_index, int):
            raise TypeError("Invalid type")
        if not isinstance(max_index, int):
            raise TypeError("Invalid type")
        slice_values = self.getSlicesValue()
        self._slicesRange = (
            float(min(min_index, max_index)),
            float(max(min_index, max_index)),
        )

        for slice_name, slice_value in slice_values.items():
            try:
                self.setSliceValue(name=slice_name, value=slice_value)
            except Exception:
                pass

    def getSlicesRange(self) -> tuple:
        return self._slicesRange

    def _plotVolume(self):
        nbpoints = 60
        angles = numpy.arange(nbpoints) * 2.0 * numpy.pi / nbpoints

        # draw ellipsis
        for y_offset, legend in zip(
            (0, self.HEIGHT), ("lower_ellipsis", "higher_ellipsis")
        ):
            X = self.LOW_RADIUS * numpy.cos(angles) * numpy.cos(
                self.ORIENTATION
            ) - self.HIGH_RADIUS * numpy.sin(angles) * numpy.sin(self.ORIENTATION)
            Y = self.LOW_RADIUS * numpy.cos(angles) * numpy.sin(
                self.ORIENTATION
            ) + self.HIGH_RADIUS * numpy.sin(angles) * numpy.cos(self.ORIENTATION)
            X = list(X)
            X.append(X[0])
            X = numpy.array(X)
            Y = list(Y)
            Y.append(Y[0])
            Y = numpy.array(Y)
            self.addCurve(X, Y + y_offset, legend=legend, color="gray")
        # draw sides
        self.addCurve((-1, -1), (0, self.HEIGHT), legend="left side", color="gray")
        self.addCurve((1, 1), (0, self.HEIGHT), legend="right side", color="gray")

    def addSlice(self, value, name, color):
        """

        :param value:
        :param name:
        """
        value = min(max(value, self._slicesRange[0]), self._slicesRange[1])
        self._addSliceAnchor(value, name, color)
        self._slices.append(name)

    def clearSlices(self):
        self._slices.clear()

    def valueToPlotSpace(self, value):
        value = numpy.clip(value, self._slicesRange[0], self._slicesRange[1])
        if self._yAxisInverted:
            value = self._slicesRange[1] - value
        value = (value - self._slicesRange[0]) / (
            self._slicesRange[1] - self._slicesRange[0]
        )
        return value * self.HEIGHT

    def plotSpaceToValue(self, y):
        value = y / self.HEIGHT
        res = int(
            value * (self._slicesRange[1] - self._slicesRange[0]) + self._slicesRange[0]
        )
        if self._yAxisInverted:
            res = self._slicesRange[1] - res
        return res

    def _updatePlane(self, y, curve_name, color):
        anchor_shift = 0.2
        nbpoints = 4
        angles = numpy.arange(nbpoints) * 2.0 * numpy.pi / nbpoints
        X = self.LOW_RADIUS * numpy.cos(angles) * numpy.cos(
            self.ORIENTATION
        ) - self.HIGH_RADIUS * numpy.sin(angles) * numpy.sin(self.ORIENTATION)
        Y = self.LOW_RADIUS * numpy.cos(angles) * numpy.sin(
            self.ORIENTATION
        ) + self.HIGH_RADIUS * numpy.sin(angles) * numpy.cos(self.ORIENTATION)
        y_min = y + min(Y)
        y_max = y + max(Y)

        x_min = min(X)
        x_max = max(X)
        xs = (
            x_min + anchor_shift,
            x_max + anchor_shift,
            x_max - anchor_shift,
            x_min - anchor_shift,
            x_min + anchor_shift,
        )
        self.addCurve(
            x=xs,
            y=(y_max, y_max, y_min, y_min, y_max),
            legend=curve_name,
            color=color,
            resetzoom=False,
        )
        self.sigSlicesChanged.emit()

    def getMarkerName(self, name: str):
        return "marker_{}".format(name)

    def _addSliceAnchor(self, value, curve_name, color):
        y_value = self.valueToPlotSpace(value=value)
        old = self.blockSignals(True)
        self._updatePlane(y=y_value, curve_name=curve_name, color=color)

        marker_name = self.getMarkerName(curve_name)
        self.addYMarker(y=y_value, color=color, legend=marker_name, draggable=True)
        marker = self._getMarker(marker_name)
        if marker:
            marker.setLineStyle("--")
            marker.sigDragFinished.connect(
                functools.partial(
                    self._updateSlicePlane, marker_name, curve_name, color
                )
            )
        self.blockSignals(old)

    def _updateSlicePlane(self, marker_name, curve_name, color):
        marker = self._getMarker(marker_name)
        if marker:
            if marker.getPosition()[1] < 0:
                marker.setPosition(0, 0)
            elif marker.getPosition()[1] > self.HEIGHT:
                marker.setPosition(0, self.HEIGHT)
            self._updatePlane(
                y=marker.getPosition()[1], curve_name=curve_name, color=color
            )

    def getSlicesValue(self) -> dict:
        """

        :return: dict with slice name as key and value as value
        """
        res = {}
        for slice_ in self._slices:
            marker = self._getMarker(self.getMarkerName(slice_))
            if marker:
                res[slice_] = int(self.plotSpaceToValue(marker.getPosition()[1]))
        return res

    def setSliceValue(self, name: str, value: float):
        if name not in self._slices:
            return
        marker = self._getMarker(self.getMarkerName(name))
        marker.setPosition(0, self.valueToPlotSpace(float(value)))
        marker.sigDragFinished.emit()


class _SliceSB(qt.QWidget):
    def __init__(self, parent):
        qt.QWidget.__init__(self, parent)


if __name__ == "__main__":
    app = qt.QApplication([])
    window = SliceSelector(insert=False)
    window.setSlicesRange(0, 100)
    window.addSlice(value=0, name="slice0", color="blue")
    window.addSlice(value=25, name="slice1", color="green")
    window.addSlice(value=70, name="slice2", color="cyan")
    window.addSlice(value=100, name="slice3", color="red")
    window.show()
    app.exec_()
