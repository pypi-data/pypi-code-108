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
__date__ = "26/02/2021"


from silx.gui import qt
from silx.io.url import DataUrl
from silx.gui.plot import PlotWindow
from typing import Union
from typing import Iterable
from silx.io.utils import get_data
from silx.gui.plot.utils.axis import SyncAxes
import numpy
import logging

from tomwer.core.process.reconstruction.scores.scores import ComputedScore

_logger = logging.getLogger(__name__)


class VignettesQDialog(qt.QDialog):
    """ """

    SIZE_HINT = qt.QSize(820, 820)

    def __init__(
        self,
        value_name,
        score_name,
        parent=None,
        value_format=None,
        score_format=None,
        colormap=None,
    ):
        qt.QDialog.__init__(self, parent)
        self._scan = None
        self._selectedValue = None
        self.setLayout(qt.QVBoxLayout())
        self._mainWidget = qt.QScrollArea(self)
        self._vignettesWidget = VignettesWidget(
            self,
            with_spacer=True,
            value_name=value_name,
            score_name=score_name,
            score_format=score_format,
            value_format=value_format,
            colormap=colormap,
        )
        self._mainWidget.setWidget(self._vignettesWidget)
        self.layout().addWidget(self._mainWidget)
        self._mainWidget.setWidgetResizable(True)

        # buttons
        types = qt.QDialogButtonBox.Ok | qt.QDialogButtonBox.Cancel
        self._buttons = qt.QDialogButtonBox(parent=self)
        self._buttons.setStandardButtons(types)
        self.layout().addWidget(self._buttons)

        # connect signal slot
        self._buttons.button(qt.QDialogButtonBox.Ok).clicked.connect(self.accept)

        self._buttons.button(qt.QDialogButtonBox.Cancel).clicked.connect(self.reject)

    def sizeHint(self):
        """Return a reasonable default size for usage in :class:`PlotWindow`"""
        return self.SIZE_HINT

    def setScores(self, scores, score_method):
        self._vignettesWidget.setScores(scores=scores, score_method=score_method)

    def selectedValue(self):
        if self._vignettesWidget is None:
            return self._selectedValue
        else:
            return self._vignettesWidget.selectedValue()

    def acccept(self):
        self._selectedValue = self._vignettesWidget.selectedValue()
        self._vignettesWidget.close()
        super().accept()

    def reject(self):
        self._selectedValue = self._vignettesWidget.selectedValue()
        self._vignettesWidget.close()
        super().reject()


class VignettesWidget(qt.QWidget):
    """
    Widget to display all the frames.

    :param QWidget parent:
    :param str value_name: name of the values for which we are looking for the
                           best one
    :param str score_name: name of the score computed
    :param score_format: None or str that can be formatted to display the
                         score
    :param value_format: None or str that can be formatted to display the
                         value
    """

    DEFAULT_PLOT_PER_ROW = 2

    def __init__(
        self,
        parent=None,
        value_name="value",
        score_name="score",
        with_spacer=True,
        value_format=None,
        score_format=None,
        colormap=None,
    ):
        qt.QWidget.__init__(self, parent)
        self._valueName = value_name
        self._scoreName = score_name
        self._nPlotPerRow = VignettesWidget.DEFAULT_PLOT_PER_ROW
        self._withSpacer = with_spacer
        self._vignettesGroup = qt.QButtonGroup()
        self.__constraintXAxis = None
        self.__constraintYAxis = None
        self._valueFormat = value_format
        self._scoreFormat = score_format
        self._colormap = colormap
        self._vignettes = []

    def close(self):
        for vignette in self._vignettes:
            vignette.close()
        super().close()

    def selectedValue(self):
        sel_vignette = self._vignettesGroup.checkedButton()
        if sel_vignette is not None:
            return sel_vignette.getValue()
        else:
            return None

    def setNElementsPerRow(self, n: int):
        self._nPlotPerRow = n

    def setScores(self, scores: dict, score_method):
        """
        Expect a dictionary with possible values to select as key and
        (2D numpy.array, score) as value.
        Where the 2D numpy.array is the frame to display and the score if the
        "indicator" score to display with the frame.
        :param dict scores: with score as key and url or numpy array as value
        """
        if len(scores) < 1:
            return
        self.setLayout(qt.QGridLayout())
        i_row = 0
        scores_values = []
        for i_score, (value, (data, score_cls)) in enumerate(scores.items()):
            if not isinstance(score_cls, ComputedScore):
                raise TypeError(
                    f"score is expected to be a dict with values as (v1: numpy.ndarray, v2: ComputedScore). v2 type Found: {type(score_cls)}"
                )
            scores_values.append(score_cls.get(score_method))
        highest_score_indices = numpy.nanargmax(scores_values)
        self._vignettesGroup = qt.QButtonGroup(self)
        self._vignettesGroup.setExclusive(True)

        if not isinstance(highest_score_indices, Iterable):
            highest_score_indices = (highest_score_indices,)

        xAxis = []
        yAxis = []

        for i_score, (value, (data, score_cls)) in enumerate(scores.items()):
            score = score_cls.get(score_method)
            i_column = i_score % self.DEFAULT_PLOT_PER_ROW
            # TODO: instead of having a binary color we could use
            # colormap
            # TODO: synchronize zooms
            if i_score == highest_score_indices or i_score in highest_score_indices:
                frame_color = qt.Qt.green
            else:
                frame_color = qt.Qt.lightGray
            widget = Vignette(
                parent=self,
                value_name=self._valueName,
                score_name=self._scoreName,
                value=value,
                data=data,
                score=score,
                frame_color=frame_color,
                value_format=self._valueFormat,
                score_format=self._scoreFormat,
                colormap=self._colormap,
            )
            widget.setAttribute(qt.Qt.WA_DeleteOnClose)
            xAxis.append(widget.getPlotWidget().getXAxis())
            yAxis.append(widget.getPlotWidget().getYAxis())

            self.layout().addWidget(widget, i_row, i_column)
            if i_column == self.DEFAULT_PLOT_PER_ROW - 1:
                i_row += 1
            if i_score == 0:
                # we cannot request all widget to keep the aspect ratio
                widget.setKeepDataAspectRatio(True)
            self._vignettesGroup.addButton(widget)
            self._vignettes.append(widget)

        if self._withSpacer:
            spacer = qt.QWidget(self)
            spacer.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)
            self.layout().addWidget(spacer, i_row + 1, self.DEFAULT_PLOT_PER_ROW - 1)

        # constrain axis synchronization
        self.__constraintXAxis = SyncAxes(
            xAxis,
            syncLimits=False,
            syncScale=True,
            syncDirection=True,
            syncCenter=True,
            syncZoom=True,
        )
        self.__constraintYAxis = SyncAxes(
            yAxis,
            syncLimits=False,
            syncScale=True,
            syncDirection=True,
            syncCenter=True,
            syncZoom=True,
        )


class _PlotForVignette(PlotWindow):
    def __init__(self, parent=None):
        PlotWindow.__init__(
            self,
            parent=parent,
            yInverted=True,
            copy=False,
            save=False,
            print_=False,
            control=False,
            mask=False,
        )
        self.setKeepDataAspectRatio(False)
        self.setAxesDisplayed(False)
        self.toolBar().hide()
        self.getInteractiveModeToolBar().hide()
        self.getOutputToolBar().hide()
        self.setInteractiveMode("zoom", zoomOnWheel=False)

    def close(self) -> bool:
        super().close()


class Vignette(qt.QToolButton):
    """Widget to display a vignette"""

    FRAME_WIDTH = 2

    def __init__(
        self,
        parent,
        value,
        value_name: str,
        score_name: str,
        data: Union[DataUrl, numpy.array],
        score: float,
        frame_color: qt.QColor,
        score_format=None,
        value_format=None,
        colormap=None,
    ):
        self._value = value
        self._scoreName = score_name
        self._valueName = value_name
        qt.QToolButton.__init__(self, parent)
        self.setCheckable(True)
        self.setLayout(qt.QVBoxLayout())
        self._plot = _PlotForVignette(parent=self)
        self._plot.setDefaultColormap(colormap=colormap)

        self.layout().addWidget(self._plot)
        self._valueLabel = ValueLabel(
            self,
            value=value,
            score=score,
            score_name=self._scoreName,
            value_name=self._valueName,
            value_format=value_format,
            score_format=score_format,
        )
        self.layout().addWidget(self._valueLabel)
        self.setFixedSize(400, 400)
        self._frameColor = frame_color
        self._selectedFrameColor = qt.Qt.black

        if isinstance(data, DataUrl):
            data = get_data(data)
        if data.ndim == 3 and data.shape[0] == 1:
            data = data.reshape(data.shape[1:])
        self._plot.addImage(data)

    def setKeepDataAspectRatio(self, keep):
        self._plot.setKeepDataAspectRatio(keep)

    def getPlotWidget(self):
        return self._plot

    def getValue(self):
        return self._value

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = qt.QPainter(self)
        half_h_width = self.FRAME_WIDTH // 2
        rect = qt.QRect(
            half_h_width,
            half_h_width,
            self.width() - self.FRAME_WIDTH,
            self.height() - self.FRAME_WIDTH,
        )
        pen = qt.QPen()
        pen.setWidth(Vignette.FRAME_WIDTH)
        pen.setColor(self._frameColor)
        painter.setPen(pen)
        painter.drawRect(rect)
        if self.isChecked():
            pen.setColor(self._selectedFrameColor)
            pen.setStyle(qt.Qt.DashLine)
            pen.setDashOffset(0.2)
            painter.setPen(pen)
            painter.drawRect(rect)

    def close(self):
        self._plot.clear()
        self._plot.setAttribute(qt.Qt.WA_DeleteOnClose)
        self._plot.close()
        self._plot = None


class ValueLabel(qt.QWidget):
    """Display the value and the associated score"""

    def __init__(
        self, parent, value, score, value_name, score_name, value_format, score_format
    ):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QHBoxLayout())
        if value_format is not None:
            str_value = value_format.format(value)
        else:
            str_value = str(value)
        txt = "{}: {}".format(value_name, str_value)
        self._valueLabel = qt.QLabel(txt, self)
        self.layout().addWidget(self._valueLabel)
        if score_format is not None:
            str_score = score_format.format(score)
        else:
            str_score = str(score)
        txt = "({}: {})".format(score_name, str_score)
        self._scoreLabel = qt.QLabel(txt, self)
        self.layout().addWidget(self._scoreLabel)
