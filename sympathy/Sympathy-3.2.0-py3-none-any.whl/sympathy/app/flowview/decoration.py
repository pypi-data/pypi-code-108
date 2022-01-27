# This file is part of Sympathy for Data.
# Copyright (c) 2013 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import enum
import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets
import Qt.QtSvg as QtSvg

from .. import util
from .. import themes
from .. import actions


def html_escape(text):
    escape_chars = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '\n': '<br>',
    }
    for c, repl in escape_chars.items():
        text = text.replace(c, repl)
    return text


class NodeViewLabel(QtWidgets.QGraphicsTextItem):
    """
    Displays the label of the node just below it.
    """

    # Emitted when edited via the GUI:
    label_edited = QtCore.Signal(str)

    def __init__(self, label='', parent=None):
        super().__init__(parent)

        theme = themes.get_active_theme()
        self.setDefaultTextColor(theme.label_color)
        self._menu = actions.document_text_edit_menu(self)
        self.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        self.setTabChangesFocus(True)
        # self.setCacheMode(QtWidgets.QGraphicsItem.DeviceCoordinateCache)

        font = QtGui.QFont()
        font.setWeight(63)
        self.document().setDefaultFont(font)

        self._update_geometry()
        self.document().contentsChanged.connect(self._update_geometry)
        self.set_label(label)

    def set_label(self, new_label):
        """Set the label. Doesn't emit label_edited."""
        self.setHtml(
            '<div style="background-color:rgba(255, 255, 255, 0);"> '
            '<center>{}</center>'.format(html_escape(new_label)))

    @QtCore.Slot()
    def _update_geometry(self):
        """
        Make sure that the label is correct size and centered under the node.
        """
        self.adjustSize()
        if self.parentItem():
            rect_label = self.boundingRect()
            rect_parent = self.parentItem().boundingRect()
            x = (rect_parent.width() - rect_label.width()) / 2.0
            y = rect_label.top() + rect_parent.bottom()
            self.setPos(x, y)

    def focusInEvent(self, event):
        if event.reason() == QtCore.Qt.PopupFocusReason:
            event.ignore()
        else:
            event.accept()
            self._old_text = self.document().toPlainText().strip()
            super().focusInEvent(event)

    def focusOutEvent(self, event):
        if event.reason() == QtCore.Qt.PopupFocusReason:
            event.ignore()
        else:
            event.accept()
            text = self.document().toPlainText().strip()

            # Workaround to remove text highlighting
            self.set_label(text)

            if text != self._old_text:
                self.label_edited.emit(text)
            super().focusOutEvent(event)

    def keyPressEvent(self, event):
        if ((event.key() == QtCore.Qt.Key_Return or
                event.key() == QtCore.Qt.Key_Enter) and not
                event.modifiers() & QtCore.Qt.ShiftModifier):
            self.clearFocus()
            event.accept()
        else:
            super().keyPressEvent(event)

    def contextMenuEvent(self, event):
        event.accept()
        if self.hasFocus():
            self._menu.setup()
            self._menu.exec_(event.screenPos())


class Status(enum.Enum):
    none = enum.auto()
    unconfigured = enum.auto()
    executable = enum.auto()
    executing = enum.auto()
    executed = enum.auto()
    executed_locked = enum.auto()
    error = enum.auto()
    queued = enum.auto()
    configuring = enum.auto()
    viewing = enum.auto()
    overrides = enum.auto()
    green_migration = enum.auto()
    yellow_migration = enum.auto()
    red_migration = enum.auto()
    missing_node = enum.auto()
    missing_file_flow = enum.auto()
    missing_library_flow = enum.auto()


STATUS_ICONS = None
STATUS_TOOLTIPS = {
    Status.none: '',
    Status.unconfigured: 'Unconfigured or invalid configuration',
    Status.executable: 'Ready to be executed',
    Status.executing: 'Currently executing',
    Status.executed: 'Successfully executed',
    Status.executed_locked: (
        'Successfully executed in locked mode. Output ports '
        'will not show current data'),
    Status.error: 'Error during execution',
    Status.queued: 'Queued for execution',
    Status.configuring: 'Configuration is open',
    Status.viewing: 'Viewer is open',
    Status.overrides: 'Overrides have been set',
    Status.green_migration: (
        'Sympathy is automatically handling migrations for this node'),
    Status.yellow_migration: (
        'This node can be manually upgraded to a newer version'),
    Status.red_migration: (
        'This version of this node is no longer supported'
    ),
    Status.missing_node: (
        'This node is not available in the loaded libraries '
        'and cannot be used until the library is available. '
        ),
    Status.missing_file_flow: (
        'This subflow is not available at the path specified and '
        'cannot be used until the flow is re-opened with the file present.'
    ),
    Status.missing_library_flow: (
        'This subflow is not available in the loaded libraries, it'
        'and cannot be used until the flow is re-opened with the library '
        'available.'
    ),
}


def get_status_tooltip(status):
    return STATUS_TOOLTIPS.get(status)


def get_icon(icon):
    global STATUS_ICONS
    if STATUS_ICONS is None:
        error_icon = QtSvg.QSvgRenderer(util.icon_path('node_error.svg'))
        eye_icon = QtSvg.QSvgRenderer(util.icon_path('node_open.svg'))

        STATUS_ICONS = {
            Status.none: QtSvg.QSvgRenderer(),
            Status.unconfigured: QtSvg.QSvgRenderer(
                util.icon_path('node_debug.svg')),
            Status.green_migration: QtSvg.QSvgRenderer(
                util.icon_path('green_migration.svg')),
            Status.yellow_migration: QtSvg.QSvgRenderer(
                util.icon_path('yellow_migration.svg')),
            Status.red_migration: QtSvg.QSvgRenderer(
                util.icon_path('red_migration.svg')),
            Status.executed: QtSvg.QSvgRenderer(
                util.icon_path('node_executed.svg')),
            Status.error: error_icon,
            Status.missing_node: error_icon,
            Status.missing_file_flow: error_icon,
            Status.missing_library_flow: error_icon,
            Status.queued: QtSvg.QSvgRenderer(
                util.icon_path('node_queued.svg')),
            Status.configuring: eye_icon,
            Status.viewing: eye_icon,
            Status.overrides: QtSvg.QSvgRenderer(
                util.icon_path('node_overrides.svg')),
        }
    none_renderer = STATUS_ICONS[Status.none]
    return STATUS_ICONS.get(icon, none_renderer)


class NodeStatusIconView(QtSvg.QGraphicsSvgItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._icon_type = Status.none
        self._init()

    def _init(self):
        self.setCacheMode(QtWidgets.QGraphicsItem.DeviceCoordinateCache)
        self.setZValue(10)
        self.setScale(0.2)
        self.setSharedRenderer(get_icon(self._icon_type))

    def set_icon_type(self, icon_type):
        if icon_type is None:
            self.setVisible(False)
            return

        self.setVisible(True)
        if icon_type != self._icon_type:
            self._icon_type = icon_type
            self.setSharedRenderer(get_icon(self._icon_type))
            self.setToolTip(f'<p>{STATUS_TOOLTIPS[self._icon_type]}</p>')


class NodeProgressView(QtWidgets.QGraphicsObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._progress = None
        self._outer_offset = 15.0
        self._middle_offset = 5.0
        self._inner_offset = -5.0
        self._has_been_updated = False
        self._number_of_segments = 8
        self._pen_width = 1.0

        theme = themes.get_active_theme()
        self.setZValue(9)

        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._update_heart_beat)
        self._heart_beat_counter = 0
        self._timer.start(1000)

        self._parent_width = self.parentItem().boundingRect().width()
        self._parent_height = self.parentItem().boundingRect().height()
        self._bounding_rect = QtCore.QRectF(
            -self._outer_offset - self._pen_width / 2.0,
            -self._outer_offset - self._pen_width / 2.0,
            self._parent_width + 2.0 *
            (self._outer_offset + self._pen_width / 2.0),
            self._parent_height + 2.0 *
            (self._outer_offset + self._pen_width / 2.0))
        self._outer_rect = QtCore.QRectF(
            -self._outer_offset, -self._outer_offset,
            self._parent_width + 2.0 * self._outer_offset,
            self._parent_height + 2.0 * self._outer_offset)
        self._middle_rect = QtCore.QRectF(
            -self._middle_offset, -self._middle_offset,
            self._parent_width + 2.0 * self._middle_offset,
            self._parent_height + 2.0 * self._middle_offset)
        self._inner_rect = QtCore.QRectF(
            -self._inner_offset, -self._inner_offset,
            self._parent_width + 2.0 * self._inner_offset,
            self._parent_height + 2.0 * self._inner_offset)
        self._border_pen = QtGui.QPen(theme.border_color)
        self._inner_brush = QtGui.QBrush(theme.border_color)

    def boundingRect(self):
        return self._bounding_rect

    def paint(self, painter, option, widget=None):
        start_angle = 90.0
        gap_angle = 5.0
        painter.setPen(self._border_pen)
        start_r, start_g, start_b = 164, 174, 194
        end_r, end_g, end_b = 179, 213, 174
        percentage = float(self._progress or 0)
        percentage_sweep = 100.0 / self._number_of_segments
        sweep = 360.0 / self._number_of_segments - gap_angle
        for segment in range(self._number_of_segments):
            self._path = QtGui.QPainterPath()
            self._path.arcMoveTo(self._outer_rect, start_angle)
            self._path.arcTo(self._outer_rect, start_angle, -sweep)
            self._path.arcTo(self._middle_rect, start_angle - sweep, 0.0)
            self._path.arcTo(self._middle_rect, start_angle - sweep, sweep)
            self._path.closeSubpath()
            start_angle -= sweep + gap_angle
            if self._has_been_updated:
                if percentage <= 0:
                    painter.setBrush(
                        QtGui.QColor.fromRgb(start_r, start_g, start_b, 255))
                elif percentage >= percentage_sweep:
                    painter.setBrush(
                        QtGui.QColor.fromRgb(end_r, end_g, end_b, 255))
                else:
                    fraction = percentage / percentage_sweep
                    painter.setBrush(QtGui.QColor.fromRgb(
                        start_r + (end_r - start_r) * fraction,
                        start_g + (end_g - start_g) * fraction,
                        start_b + (end_b - start_b) * fraction, 255))
            else:
                if self._heart_beat_counter > 0:
                    if ((self._heart_beat_counter - 1) %
                            self._number_of_segments) == segment:
                        painter.setBrush(
                            QtGui.QColor.fromRgb(end_r, end_g, end_b, 255))
                    else:
                        painter.setBrush(
                            QtGui.QColor.fromRgb(
                                start_r, start_g, start_b, 255))
                else:
                    painter.setBrush(
                        QtGui.QColor.fromRgb(start_r, start_g, start_b, 255))

            painter.drawPath(self._path)
            percentage -= percentage_sweep

        if self._has_been_updated:
            text_background_path = QtGui.QPainterPath()
            text_background_path.addEllipse(self._inner_rect)
            painter.fillPath(text_background_path, self._inner_brush)

            progress_text = '%d%%' % (self._progress or 0)
            painter.setPen(QtCore.Qt.white)
            painter.setBrush(self._inner_brush)
            painter.drawText(
                self._inner_rect, progress_text, QtGui.QTextOption(
                    QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter))

    @QtCore.Slot(float)
    def update_progress(self, progress):
        p = int(progress)
        if p != self._progress:
            self._progress = p
            self._has_been_updated = True
            self.update()

    @QtCore.Slot()
    def _update_heart_beat(self):
        if self._has_been_updated:
            self._timer.stop()
            self._timer.timeout.disconnect(self._update_heart_beat)
            del self._timer
        else:
            self._heart_beat_counter += 1
            self.update()
