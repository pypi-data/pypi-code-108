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

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "04/03/2019"


from silx.gui import qt
from silx.utils.enum import Enum as _Enum
from typing import Union
import functools
from tomwer.gui import icons
from tomwer.utils import docstring


class FlowDirection(_Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class _ProcessDescWidget(qt.QWidget):
    """Widget to describe the process"""

    ICON_WIDTH = 16

    def __init__(self, parent, process, icon, direction, locked, show_lock_state=True):
        assert isinstance(direction, FlowDirection)
        super(_ProcessDescWidget, self).__init__(parent=parent)
        self.__active = False

        if direction is FlowDirection.VERTICAL:
            self.setLayout(qt.QHBoxLayout())
        else:
            self.setLayout(qt.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        # lock icon
        self._lockIcon = qt.QLabel("", parent=self)
        self._lockIcon.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Minimum)
        self._lockIcon.setAlignment(qt.Qt.AlignRight | qt.Qt.AlignTop)

        if locked:
            locked_icon = icons.getQIcon("locked")
        else:
            locked_icon = icons.getQIcon("unlocked")

        self._lockIcon.setPixmap(locked_icon.pixmap(20, 20))
        self._lockIcon.setVisible(show_lock_state)

        # process name + process icon
        self.main_widget = qt.QWidget(parent=self)
        self.main_widget.setLayout(qt.QHBoxLayout())

        self._label = qt.QLabel(str(process), self)
        self._label.setAlignment(qt.Qt.AlignCenter)
        self._label.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum)
        self.main_widget.layout().addWidget(self._label)
        if icon is not None:
            self._frame = qt.QLabel(self)
            self._frame.setPixmap(
                icon.pixmap(
                    qt.QSize(
                        _ProcessDescWidget.ICON_WIDTH, _ProcessDescWidget.ICON_WIDTH
                    )
                )
            )
            self.main_widget.layout().addWidget(self._frame)

        # main_widget.layout().addWidget(icon_label)
        if direction is FlowDirection.VERTICAL:
            self.layout().addWidget(self.main_widget)
            self.layout().addWidget(self._lockIcon)
        else:
            self.layout().addWidget(self._lockIcon)
            self.layout().addWidget(self.main_widget)
        # expose API
        self.process = process

    def setActive(self, active: bool) -> None:
        """
        set the widget as active or inactive. This will put or remove the focus
        on.

        :param active:
        """
        self.__active = active
        if active:
            stylesheet = "border: 1px solid red"
        else:
            stylesheet = ""
        self.main_widget.setStyleSheet(stylesheet)
        if hasattr(self, "_frame"):
            self._frame.setStyleSheet("border: 0px")
        self._label.setStyleSheet("border: 0px")

    def isActive(self) -> bool:
        """

        :return: is the widget active / focus / under edition
        """
        return self.__active


class _ProcessDescContainer(qt.QWidget):
    """simple docker for the process description

    :param parent:
    :param process: any object implementing the `__str__` interface
    :param icon:
    :raises: TypeError if process does not implements __str__
    """

    sigWidgetActivated = qt.Signal()
    """Signal emitted when the contained widget become the active process."""
    sigWidgetDeactivated = qt.Signal()
    """Signal emitted when the contained widget is deactivated (not the
    active process anymore)"""

    def __init__(
        self, parent, process, icon, direction, draggable, show_lock_state=True
    ):
        if not hasattr(process, "__str__"):
            raise TypeError("name should implement `__str__`")
        super(_ProcessDescContainer, self).__init__(parent=parent)
        self._widget = _ProcessDescWidget(
            parent=self,
            process=process,
            icon=icon,
            direction=direction,
            locked=not draggable,
            show_lock_state=show_lock_state,
        )
        self.setLayout(qt.QVBoxLayout())
        self.setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self._widget)
        # expose API
        self.process = self._widget.process
        self._draggable = draggable

    def event(self, QEvent):
        if (
            QEvent.type() == qt.QEvent.MouseButtonPress
            and QEvent.button() == qt.Qt.LeftButton
        ):
            self._setIsOnFocus()
        return super(_ProcessDescContainer, self).event(QEvent)

    def _setIsOnFocus(self):
        if self._widget.isActive():
            self.sigWidgetDeactivated.emit()
        else:
            self.sigWidgetActivated.emit()

    @docstring(_ProcessDescWidget)
    def setActive(self, active):
        self._widget.setActive(active=active)
        if active:
            self.sigWidgetActivated.emit()
        else:
            self.sigWidgetDeactivated.emit()

    @docstring(_ProcessDescWidget)
    def isActive(self):
        return self._widget.isActive()


class FlowCanvas(qt.QWidget):
    """
    Widget to describe a flow of process - pipeline

    :param direction: direction can be vertical or horizontal
    :type direction: Union[str,FlowDirection]
    """

    sigWidgetActivated = qt.Signal()
    """Signal emitted when the contained widget become the active process."""
    sigWidgetDeactivated = qt.Signal()
    """Signal emitted when the contained widget is deactivated (not the
    active process anymore)"""

    def __init__(
        self, parent, direction: Union[str, FlowDirection], show_lock_state=True
    ) -> None:
        qt.QWidget.__init__(self, parent=parent)
        self._direction = FlowDirection.from_value(direction)
        if self._direction is FlowDirection.HORIZONTAL:
            layout = qt.QHBoxLayout()
        elif self._direction is FlowDirection.VERTICAL:
            layout = qt.QVBoxLayout()
        else:
            raise ValueError("direction not managed")
        self.setLayout(layout)
        self.setWindowFlags(qt.Qt.Widget)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self._dockers = {}
        self._process_id = 0
        self._show_lock_state = show_lock_state

        if self._direction is FlowDirection.HORIZONTAL:
            self._dockArea = qt.Qt.TopDockWidgetArea
        elif self._direction is FlowDirection.VERTICAL:
            self._dockArea = qt.Qt.LeftDockWidgetArea
        else:
            raise ValueError("direction not managed")

    def getFlow(self) -> list:
        """Return the list of process following the treatment flow"""
        widgetXPos = {}
        # retrieve each docker position
        for process_id, dockWidget in self._dockers.items():
            if self._direction is FlowDirection.HORIZONTAL:
                widgetXPos[process_id] = dockWidget.pos().x()
            else:
                widgetXPos[process_id] = dockWidget.pos().y()
        # order the widget / process according to
        res = []
        for widgetIndex, _ in sorted(widgetXPos.items(), key=lambda item: item[1]):
            res.append(self._dockers[widgetIndex].process)
        return res

    def addProcess(self, process, icon=None, draggable=True) -> int:
        """
        Add a process to the flow with the name 'process' and an optional icon

        :param process_name: any object. Should implement the __str__ interface
                             to define the name if no icon is given
        :return: process id in the process flow
        :rtype: int
        """
        if icon is None:
            assert hasattr(process, "__str__")
        widget = _ProcessDescContainer(
            parent=self,
            process=process,
            icon=icon,
            direction=self._direction,
            draggable=draggable,
            show_lock_state=self._show_lock_state,
        )

        self.layout().addWidget(widget)
        process_id = self._process_id
        self._dockers[self._process_id] = widget
        self._process_id += 1

        # connect signals / slots
        widget.sigWidgetActivated.connect(
            functools.partial(self._activeProcessChanged, process_id)
        )
        widget.sigWidgetDeactivated.connect(
            functools.partial(self._activeProcessChanged, None)
        )

        return process_id

    def _activeProcessChanged(self, active_process):
        for process_id, dock in self._dockers.items():
            old = dock.blockSignals(True)
            dock.setActive(active_process == process_id)
            dock.blockSignals(old)
        if active_process is None:
            self.sigWidgetDeactivated.emit()
        else:
            self.sigWidgetActivated.emit()

    def removeProcess(self, process_id: int) -> None:
        """

        :param int process_id: id of the process to remove from the flow
        """
        if process_id in self._dockers:
            dockWidget = self._dockers[process_id]
            self.layout().removeWidget(dockWidget)
            del self._dockers[process_id]

    def clear(self):
        processes_id = self._dockers.keys()
        for process_id in processes_id:
            self.removeProcess(process_id=process_id)

    def setProcesses(self, processes, icons, draggability) -> None:
        """

        :param Iterable processes: processes of the flow
        :param Iterable icons: icons associated to the flow
        :param Iterable draggability: is the process draggable or not
        :return:
        """
        for process, icon, draggable in zip(processes, icons, draggability):
            self.addProcess(process=process, draggable=draggable, icon=icon)

    def clearActiveProcess(self) -> None:
        """
        Set all process to unactive
        """
        for dock in self._dockers.values():
            old = dock.blockSignals(True)
            dock.setActive(False)
            dock.blockSignals(old)

    def hasProcessFocus(self) -> bool:
        """

        :return: True if the canvas has a process active / focus ...
        :rtype: bool
        """
        return self.getProcessFocused() is not None

    def getProcessFocused(self) -> Union[None, int]:
        """

        :return: id of the process focus or None if no process focus
        """
        for process_id, dock in self._dockers.items():
            if dock.isActive():
                return process_id
        return None

    def _removeActiveProcess(self):
        process_id = self.getProcessFocused()
        if process_id is not None:
            self.removeProcess(process_id=process_id)
