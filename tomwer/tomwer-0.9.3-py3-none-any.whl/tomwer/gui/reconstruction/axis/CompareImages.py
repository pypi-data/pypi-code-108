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

__authors__ = ["v. Valls", "H. Payno"]
__license__ = "MIT"
__date__ = "26/02/2019"

from silx.gui import qt
from silx.gui.plot import CompareImages as _CompareImages
from silx.gui import icons as silx_icons
from tomwer.gui import icons as tomwer_icons
from silx.gui.plot import tools
import numpy
import weakref
import logging

_logger = logging.getLogger(__name__)


class CompareImagesToolBar(qt.QToolBar):
    """ToolBar containing specific tools to custom the configuration of a
    :class:`CompareImages` widget

    Use :meth:`setCompareWidget` to connect this toolbar to a specific
    :class:`CompareImages` widget.

    :param Union[qt.QWidget,None] parent: Parent of this widget.
    """

    def __init__(self, parent=None):
        qt.QToolBar.__init__(self, parent)

        self.__compareWidget = None

        menu = qt.QMenu(self)
        self.__visualizationAction = qt.QAction(self)
        self.__visualizationAction.setMenu(menu)
        self.__visualizationAction.setCheckable(False)
        self.addAction(self.__visualizationAction)
        self.__visualizationGroup = qt.QActionGroup(self)
        self.__visualizationGroup.setExclusive(True)
        self.__visualizationGroup.triggered.connect(self.__visualizationModeChanged)

        icon = silx_icons.getQIcon("compare-mode-a")
        action = qt.QAction(icon, "Display frame 1", self)
        action.setIconVisibleInMenu(True)
        action.setCheckable(True)
        action.setShortcut(qt.QKeySequence(qt.Qt.Key_A))
        action.setProperty("mode", CompareImages.VisualizationMode.ONLY_A)
        menu.addAction(action)
        self.__aModeAction = action
        self.__visualizationGroup.addAction(action)

        icon = silx_icons.getQIcon("compare-mode-b")
        action = qt.QAction(icon, "Display frame 2", self)
        action.setIconVisibleInMenu(True)
        action.setCheckable(True)
        action.setShortcut(qt.QKeySequence(qt.Qt.Key_B))
        action.setProperty("mode", CompareImages.VisualizationMode.ONLY_B)
        menu.addAction(action)
        self.__bModeAction = action
        self.__visualizationGroup.addAction(action)

        icon = silx_icons.getQIcon("compare-mode-rbneg-channel")
        action = qt.QAction(icon, "Subtract in color mode", self)
        action.setIconVisibleInMenu(True)
        action.setCheckable(True)
        action.setShortcut(qt.QKeySequence(qt.Qt.Key_C))
        action.setProperty(
            "mode", _CompareImages.VisualizationMode.COMPOSITE_RED_BLUE_GRAY_NEG
        )
        menu.addAction(action)
        self.__ycChannelModeAction = action
        self.__visualizationGroup.addAction(action)

        icon = tomwer_icons.getQIcon("compare_mode_a_minus_b")
        action = qt.QAction(icon, "Subtract in BW mode", self)
        action.setIconVisibleInMenu(True)
        action.setCheckable(True)
        action.setShortcut(qt.QKeySequence(qt.Qt.Key_S))
        action.setProperty("mode", _CompareImages.VisualizationMode.COMPOSITE_A_MINUS_B)
        menu.addAction(action)
        self.__ycChannelModeAction = action
        self.__visualizationGroup.addAction(action)

    def setCompareWidget(self, widget):
        """
        Connect this tool bar to a specific :class:`CompareImages` widget.

        :param Union[None,CompareImages] widget: The widget to connect with.
        """
        compareWidget = self.getCompareWidget()
        if compareWidget is not None:
            compareWidget.sigConfigurationChanged.disconnect(
                self.__updateSelectedActions
            )
        compareWidget = widget
        if compareWidget is None:
            self.__compareWidget = None
        else:
            self.__compareWidget = weakref.ref(compareWidget)
        if compareWidget is not None:
            widget.sigConfigurationChanged.connect(self.__updateSelectedActions)
        self.__updateSelectedActions()

    def getCompareWidget(self):
        """Returns the connected widget.

        :rtype: CompareImages
        """
        if self.__compareWidget is None:
            return None
        else:
            return self.__compareWidget()

    def __updateSelectedActions(self):
        """
        Update the state of this tool bar according to the state of the
        connected :class:`CompareImages` widget.
        """
        widget = self.getCompareWidget()
        if widget is None:
            return

        mode = widget.getVisualizationMode()
        action = None
        for a in self.__visualizationGroup.actions():
            actionMode = a.property("mode")
            if mode == actionMode:
                action = a
                break
        old = self.__visualizationGroup.blockSignals(True)
        if action is not None:
            # Check this action
            action.setChecked(True)
        else:
            action = self.__visualizationGroup.checkedAction()
            if action is not None:
                # Uncheck this action
                action.setChecked(False)
        self.__updateVisualizationMenu()
        self.__visualizationGroup.blockSignals(old)

    def __visualizationModeChanged(self, selectedAction):
        """Called when user requesting changes of the visualization mode."""
        self.__updateVisualizationMenu()
        widget = self.getCompareWidget()
        if widget is not None:
            mode = selectedAction.property("mode")
            widget.setVisualizationMode(mode)

    def __updateVisualizationMenu(self):
        """Update the state of the action containing visualization menu."""
        selectedAction = self.__visualizationGroup.checkedAction()
        if selectedAction is not None:
            self.__visualizationAction.setText(selectedAction.text())
            self.__visualizationAction.setIcon(selectedAction.icon())
            self.__visualizationAction.setToolTip(selectedAction.toolTip())
        else:
            self.__visualizationAction.setText("")
            self.__visualizationAction.setIcon(qt.QIcon())
            self.__visualizationAction.setToolTip("")

    def __alignmentModeChanged(self, selectedAction):
        """Called when user requesting changes of the alignment mode."""
        self.__updateAlignmentMenu()
        widget = self.getCompareWidget()
        if widget is not None:
            mode = selectedAction.property("mode")
            widget.setAlignmentMode(mode)

    def __updateAlignmentMenu(self):
        """Update the state of the action containing alignment menu."""
        selectedAction = self.__alignmentGroup.checkedAction()
        if selectedAction is not None:
            self.__alignmentAction.setText(selectedAction.text())
            self.__alignmentAction.setIcon(selectedAction.icon())
            self.__alignmentAction.setToolTip(selectedAction.toolTip())
        else:
            self.__alignmentAction.setText("")
            self.__alignmentAction.setIcon(qt.QIcon())
            self.__alignmentAction.setToolTip("")

    def __keypointVisibilityChanged(self):
        """Called when action managing keypoints visibility changes"""
        widget = self.getCompareWidget()
        if widget is not None:
            keypointsVisible = self.__displayKeypoints.isChecked()
            widget.setKeypointsVisible(keypointsVisible)


class CompareImages(_CompareImages.CompareImages):
    def _createToolBars(self, plot):
        """Create tool bars displayed by the widget"""
        self._interactiveModeToolBar = tools.InteractiveModeToolBar(
            parent=self, plot=plot
        )
        self._imageToolBar = tools.ImageToolBar(parent=self, plot=plot)

        toolBar = CompareImagesToolBar(self)
        toolBar.setCompareWidget(self)
        self._compareToolBar = toolBar

    def _createStatusBar(self, plot):
        self._statusBar = CompareImagesStatusBar(self)
        self._statusBar.setCompareWidget(self)

    def getCompareToolBar(self):
        return self._compareToolBar


class CompareImagesStatusBar(qt.QStatusBar):
    """StatusBar containing specific information contained in a
    :class:`CompareImages` widget

    Use :meth:`setCompareWidget` to connect this toolbar to a specific
    :class:`CompareImages` widget.

    :param Union[qt.QWidget,None] parent: Parent of this widget.
    """

    def __init__(self, parent=None):
        qt.QStatusBar.__init__(self, parent)
        self.setSizeGripEnabled(False)
        self.layout().setSpacing(0)
        self.__compareWidget = None
        self._label1 = qt.QLabel(self)
        self._label1.setFrameShape(qt.QFrame.WinPanel)
        self._label1.setFrameShadow(qt.QFrame.Sunken)
        self._label2 = qt.QLabel(self)
        self._label2.setFrameShape(qt.QFrame.WinPanel)
        self._label2.setFrameShadow(qt.QFrame.Sunken)
        self._transform = qt.QLabel(self)
        self._transform.setFrameShape(qt.QFrame.WinPanel)
        self._transform.setFrameShadow(qt.QFrame.Sunken)
        self.addWidget(self._label1)
        self.addWidget(self._label2)
        self.addWidget(self._transform)
        self._pos = None
        self._updateStatusBar()

    def setCompareWidget(self, widget):
        """
        Connect this tool bar to a specific :class:`CompareImages` widget.

        :param Union[None,CompareImages] widget: The widget to connect with.
        """
        compareWidget = self.getCompareWidget()
        if compareWidget is not None:
            compareWidget.getPlot().sigPlotSignal.disconnect(self.__plotSignalReceived)
            compareWidget.sigConfigurationChanged.disconnect(self.__dataChanged)
        compareWidget = widget
        if compareWidget is None:
            self.__compareWidget = None
        else:
            self.__compareWidget = weakref.ref(compareWidget)
        if compareWidget is not None:
            compareWidget.getPlot().sigPlotSignal.connect(self.__plotSignalReceived)
            compareWidget.sigConfigurationChanged.connect(self.__dataChanged)

    def getCompareWidget(self):
        """Returns the connected widget.

        :rtype: CompareImages
        """
        if self.__compareWidget is None:
            return None
        else:
            return self.__compareWidget()

    def __plotSignalReceived(self, event):
        """Called when old style signals at emmited from the plot."""
        if event["event"] == "mouseMoved":
            x, y = event["x"], event["y"]
            self.__mouseMoved(x, y)

    def __mouseMoved(self, x, y):
        """Called when mouse move over the plot."""
        self._pos = x, y
        self._updateStatusBar()

    def __dataChanged(self):
        """Called when internal data from the connected widget changes."""
        self._updateStatusBar()

    def _formatData(self, data):
        """Format pixel of an image.

        It supports intensity, RGB, and RGBA.

        :param Union[int,float,numpy.ndarray,str]: Value of a pixel
        :rtype: str
        """
        if data is None:
            return "-"
        if isinstance(data, (int, numpy.integer)):
            return "%d" % data
        if isinstance(data, (float, numpy.floating)):
            return "%f" % data
        if isinstance(data, numpy.ndarray):
            # RGBA value
            if data.shape == (3,):
                return "R:%d G:%d B:%d" % (data[0], data[1], data[2])
            elif data.shape == (4,):
                return "R:%d G:%d B:%d A:%d" % (data[0], data[1], data[2], data[3])
        _logger.debug("Unsupported data format %s. Cast it to string.", type(data))
        return str(data)

    def _updateStatusBar(self):
        """Update the content of the status bar"""
        widget = self.getCompareWidget()
        if widget is None:
            self._label1.setText("Frame 1: -")
            self._label2.setText("Frame 2: -")
            self._transform.setVisible(False)
        else:
            transform = widget.getTransformation()
            self._transform.setVisible(transform is not None)
            if transform is not None:
                has_notable_translation = not numpy.isclose(
                    transform.tx, 0.0, atol=0.01
                ) or not numpy.isclose(transform.ty, 0.0, atol=0.01)
                has_notable_scale = not numpy.isclose(
                    transform.sx, 1.0, atol=0.01
                ) or not numpy.isclose(transform.sy, 1.0, atol=0.01)
                has_notable_rotation = not numpy.isclose(transform.rot, 0.0, atol=0.01)

                strings = []
                if has_notable_translation:
                    strings.append("Translation")
                if has_notable_scale:
                    strings.append("Scale")
                if has_notable_rotation:
                    strings.append("Rotation")
                if strings == []:
                    has_translation = not numpy.isclose(
                        transform.tx, 0.0
                    ) or not numpy.isclose(transform.ty, 0.0)
                    has_scale = not numpy.isclose(
                        transform.sx, 1.0
                    ) or not numpy.isclose(transform.sy, 1.0)
                    has_rotation = not numpy.isclose(transform.rot, 0.0)
                    if has_translation or has_scale or has_rotation:
                        text = "No big changes"
                    else:
                        text = "No changes"
                else:
                    text = "+".join(strings)
                self._transform.setText("Align: " + text)

                strings = []
                if not numpy.isclose(transform.ty, 0.0):
                    strings.append("Translation x: %0.3fpx" % transform.tx)
                if not numpy.isclose(transform.ty, 0.0):
                    strings.append("Translation y: %0.3fpx" % transform.ty)
                if not numpy.isclose(transform.sx, 1.0):
                    strings.append("Scale x: %0.3f" % transform.sx)
                if not numpy.isclose(transform.sy, 1.0):
                    strings.append("Scale y: %0.3f" % transform.sy)
                if not numpy.isclose(transform.rot, 0.0):
                    strings.append(
                        "Rotation: %0.3fdeg" % (transform.rot * 180 / numpy.pi)
                    )
                if strings == []:
                    text = "No transformation"
                else:
                    text = "\n".join(strings)
                self._transform.setToolTip(text)

            if self._pos is None:
                self._label1.setText("Frame 1: -")
                self._label2.setText("Frame 2: -")
            else:
                data1, data2 = widget.getRawPixelData(self._pos[0], self._pos[1])
                if isinstance(data1, str):
                    self._label1.setToolTip(data1)
                    text1 = "-"
                else:
                    self._label1.setToolTip("")
                    text1 = self._formatData(data1)
                if isinstance(data2, str):
                    self._label2.setToolTip(data2)
                    text2 = "-"
                else:
                    self._label2.setToolTip("")
                    text2 = self._formatData(data2)
                self._label1.setText("Frame 1: %s" % text1)
                self._label2.setText("Frame 2: %s" % text2)
