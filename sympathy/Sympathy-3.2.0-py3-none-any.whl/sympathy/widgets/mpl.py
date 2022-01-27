# This file is part of Sympathy for Data.
# Copyright (c) 2020, Combine Control Systems AB
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
"""
Matplotlib widgets for Sympathy.

Assumes that you have already specified the back_end before import using
use_matplotlib_qt() or similar. Therefore, import from a function
which ensures it::

def _widget_mpl():
    qt_compat2.backend.use_matplotlib_qt()
    from sympathy.widgets import mpl as widget_mpl
    return widget_mpl

"""
import enum
import os
import numpy as np
import datetime
import warnings

from Qt import QtWidgets, QtCore, QtGui

import matplotlib
import matplotlib.figure
import matplotlib.backends.backend_qt5agg
import matplotlib.lines as lines
import matplotlib.patches as patches
import matplotlib.dates as dates

from sympathy.widgets import utils as widget_utils
from sympathy.platform import widget_library as sywidgets


def _num_to_type(num, vmin, vmax):
    res = num
    if (isinstance(vmin, (datetime.date, datetime.datetime)) or
        isinstance(vmax, (datetime.date, datetime.datetime))):
        res = dates.num2date(num, tz=None)
    return res


def _num_to_axis(num, axis):
    res = num
    if axis and axis.converter:
        vmin, vmax = axis.converter.axisinfo(axis.units, axis).default_limits
        res = _num_to_type(num, vmin, vmax)
    return res


class SelectionArtist(matplotlib.artist.Artist):
    """
    Base for Selection Artists.

    Selection artists are used for interactive selection and should not be
    considered as part of the data being plotted. For example when using
    snap-to-data or showing stats for different datapoints.
    """

    @classmethod
    def is_selection(cls, artist):
        return isinstance(artist, SelectionArtist)


class SelectionLine2D(SelectionArtist, matplotlib.lines.Line2D):
    pass


class SelectionRectangle(SelectionArtist, matplotlib.patches.Rectangle):
    pass


class Grabber:
    """
    Handles grab state.

    Ensures that the a mouse press will only grab a single object and that
    the the same button is released before returning to released state.
    """

    def __init__(self, grabbed=False):
        self._grabbed = grabbed
        self._event = None

    def _set_enabled(self, enabled):
        res = self._grabbed != enabled
        self._grabbed = enabled
        return res

    def grab(self, event):
        res = False
        if event.button == 1 and event is not self._event:
            res = self._set_enabled(True)
            if res:
                self._event = event
        return res

    def release(self, event):
        res = False
        if self._event and self._event.button == event.button:
            res = self._set_enabled(False)
            self._event = None
        return res


class DraggableParent:

    def child_moved(self, child, dxdata, dydata):
        raise NotImplementedError

    def child_released(self, child):
        raise NotImplementedError


class Draggable:
    """
    Base class for Draggable objects.

    Derived classes need to override the following methods::

        def get_x(self):
        def get_y(self):
        def add(self):

    Optionally override either or both of the following::

        def set_x(self, xdata):
        def set_y(self, ydata):
    """

    def __init__(self,
                 *,
                 ax: matplotlib.axes.Axes,
                 artist: matplotlib.artist.Artist,
                 grabber: Grabber,
                 parent: DraggableParent = None,
                 **kwargs):
        self.ax = ax
        self.artist = artist
        self._grab = grabber
        self._parent = parent
        self._canvas = ax.get_figure().canvas

        self._canvas.draw_idle()

        self._cid_pick = None
        if artist.pickable:
            self._cid_pick = self._canvas.mpl_connect(
                'pick_event', self._on_pick)
        self._cid_motion_notify = None
        self._cid_button_release = None

        self._dxdata_grab = 0
        self._dydata_grab = 0

    def move(self, xdata, ydata):
        xdata_origin = self.get_x()
        ydata_origin = self.get_y()

        self.set_x(xdata)
        self.set_y(ydata)

        if self._parent:
            dxdata = self.get_x() - xdata_origin
            dydata = self.get_y() - ydata_origin
            self._parent.child_moved(self, dxdata, dydata)

    def grab(self):
        pass

    def release(self):
        if self._parent:
            self._parent.child_released(self)

    def add(self):
        raise NotImplementedError

    def remove(self):
        self.artist.remove()
        self._canvas.draw_idle()

    def get_x(self):
        raise NotImplementedError

    def get_y(self):
        raise NotImplementedError

    def set_x(self, xdata):
        pass

    def set_y(self, ydata):
        pass

    def disconnect(self):
        self._disconnect_grab()

        if self._cid_pick is not None:
            try:
                self._canvas.mpl_disconnect(self._cid_pick)
            except Exception:
                pass
            self._cid_pick = None

    def _on_pick(self, event):
        try:
            if (event.artist is self.artist and self._grab.grab(event.mouseevent)):
                self.grab()

                xdata = _num_to_axis(event.mouseevent.xdata, self.ax.get_xaxis())
                ydata = _num_to_axis(event.mouseevent.ydata, self.ax.get_yaxis())

                self._dxdata_grab = xdata - self.get_x()
                self._dydata_grab = ydata - self.get_y()

                self._cid_motion_notify = self._canvas.mpl_connect(
                    "motion_notify_event", self._on_motion_notify)
                self._cid_button_release = self._canvas.mpl_connect(
                    "button_release_event", self._on_button_release)
        except Exception:
            self._disconnect_grab()
            self.release()

    def _on_motion_notify(self, event):

        if not event.inaxes:
            return

        xdata = _num_to_axis(event.xdata, self.ax.get_xaxis())
        ydata = _num_to_axis(event.ydata, self.ax.get_yaxis())

        xdata = xdata - self._dxdata_grab
        ydata = ydata - self._dydata_grab

        self.move(xdata, ydata)
        self._canvas.draw_idle()

    def _on_button_release(self, event):
        if self._grab.release(event):

            self._disconnect_grab()

            self._dxdata_grab = 0
            self._dydata_grab = 0

            self.release()

    def _disconnect_grab(self):
        if self._cid_motion_notify is not None:
            try:
                self._canvas.mpl_disconnect(self._cid_motion_notify)
            except Exception:
                pass
            self._cid_motion_notify = None
        if self._cid_button_release is not None:
            try:
                self._canvas.mpl_disconnect(self._cid_button_release)
            except Exception:
                pass
            self._cid_button_release = None


class Snapper:

    def __init__(self, xdata, ydata):
        self._xdata = xdata
        self._ydata = ydata

    def get_xdata(self):
        return self._xdata

    def get_ydata(self):
        return self._ydata

    def set_xdata(self, xdata):
        """
        Sorted np.array containing all of the datapoints along the x-axis.
        """
        self._xdata = xdata

    def set_ydata(self, ydata):
        """
        Sorted np.array containing all of the datapoints along the x-axis.
        """
        self._ydata = ydata

    def snap_x(self, xdata):
        res = xdata
        if len(self._xdata):
            res = self._nearest_value(xdata, self._xdata)
        return res

    def snap_y(self, ydata):
        res = ydata
        if len(self._ydata):
            res = self._nearest_value(ydata, self._ydata)
        return res

    def _nearest_index(self, point, points):
        # Optimized path for sorted data which uses binary
        # search to find the index and then uses the
        # nearest of the 3 adjacent indices.
        if isinstance(point, datetime.datetime):
            point = point.replace(tzinfo=None)

        idx = min(np.searchsorted(
            points, point), len(points) - 1)

        idx_min = idx - 1
        nearest = points[max(0, idx_min): idx + 1]
        idx_nearest = np.abs(nearest - point).argmin()

        if idx_min < 0:
            return idx + idx_nearest
        else:
            return idx + idx_nearest - 1

    def _nearest_value(self, point, points):
        idx = self._nearest_index(point, points)
        point = points[idx]

        try:
            point = point.tolist()
        except Exception:
            pass

        if isinstance(point, datetime.datetime):
            point = point.replace(tzinfo=datetime.timezone.utc)
        return point


class Snappable(Draggable):
    """
    Base class for Snappable objects.

    Optionally override either or both of the following::

        def get_snap_x(self):
        def get_snap_y(self):
    """

    def __init__(self, *, snapper: Snapper, **kwargs):
        self._snapper = snapper
        self._snap_x = False
        self._snap_y = False
        super().__init__(**kwargs)

    def move(self, xdata, ydata):

        snap_x = self.get_snap_x()
        snap_y = self.get_snap_y()

        if snap_x or snap_y:

            if snap_x:
                xdata = self._snapper.snap_x(xdata)
            if snap_y:
                ydata = self._snapper.snap_y(ydata)

        super().move(xdata, ydata)

    def get_snap_x(self):
        return self._snap_x

    def get_snap_y(self):
        return self._snap_y

    def set_snap_x(self, value):
        self._snap_x = value

    def set_snap_y(self, value):
        self._snap_y = value


class SnappableLine(Snappable):
    picker = 8
    color = 'black'
    alpha = 0.3
    alpha_grab = 0.9

    def grab(self):
        super().grab()
        self.artist.set_alpha(self.alpha_grab)
        self._canvas.draw_idle()

    def release(self):
        super().release()
        self.artist.set_alpha(self.alpha)
        self._canvas.draw_idle()

    def get_x(self):
        return min(self.artist.get_xdata())

    def get_y(self):
        return min(self.artist.get_ydata())

    def add(self):
        self.ax.add_line(self.artist)
        self._canvas.draw_idle()


class DraggableHorizontalLine(SnappableLine):

    def __init__(self, *, ax, y, **kwargs):
        x = [0, 1]
        y = [y, y]
        transform = ax.get_yaxis_transform()
        picker = kwargs.pop('picker', self.picker)
        color = kwargs.pop('color', self.color)
        alpha = kwargs.pop('alpha', self.alpha)

        self._snap_y = False
        self.artist = SelectionLine2D(
            x, y,
            picker=picker, color=color, alpha=alpha,
            transform=transform)
        ax.add_line(self.artist)
        super().__init__(ax, self.artist, **kwargs)

    def set_snap_y(self, value):
        self._snap_y = value

    def get_snap_y(self):
        return self._snap_y

    def set_y(self, ydata):
        self.artist.set_ydata([ydata, ydata])


class DraggableVerticalLine(SnappableLine):

    def __init__(self, *, ax, x, **kwargs):
        x = [x, x]
        y = [0, 1]
        transform = ax.get_xaxis_transform()
        picker = kwargs.pop('picker', self.picker)
        color = kwargs.pop('color', self.color)
        alpha = kwargs.pop('alpha', self.alpha)

        self._snap_x = False
        self.artist = SelectionLine2D(
            x, y,
            picker=picker, color=color, alpha=alpha,
            transform=transform)
        ax.add_line(self.artist)
        super().__init__(ax=ax, artist=self.artist, **kwargs)

    def set_x(self, xdata):
        self.artist.set_xdata([xdata, xdata])


class DraggableRectangle(Draggable):
    picker = 8
    color = 'black'
    alpha = 0.1

    def get_x(self):
        return self.artist.get_x()

    def get_y(self):
        return self.artist.get_y()

    def add(self):
        self.ax.add_patch(self.artist)
        self._canvas.draw_idle()


class DraggableVerticalRectangle(DraggableRectangle):

    def __init__(self, *, ax, x, width, **kwargs):
        y = 0
        height = 1
        transform = ax.get_xaxis_transform()
        picker = kwargs.pop('picker', self.picker)
        color = kwargs.pop('color', self.color)
        alpha = kwargs.pop('alpha', self.alpha)

        self.artist = SelectionRectangle(
            (x, y), width=width, height=height, alpha=alpha,
            picker=picker, color=color, transform=transform)
        ax.add_patch(self.artist)
        super().__init__(ax=ax, artist=self.artist, **kwargs)

    def set_x(self, xdata):
        self.artist.set_x(xdata)

    def set_width(self, width):
        self.artist.set_width(width)

    def set_bounds(self, x, y, width, height):
        self.artist.set_bounds(x, y, width, height)


class VerticalCursorController(DraggableParent, QtCore.QObject):

    cursor_moved = QtCore.Signal()

    def __init__(self, ax, snapper, grabber, cursors, data, band=False):

        self.ax = ax
        self._snapper = snapper
        self._grabber = grabber
        self._canvas = ax.get_figure().canvas
        self._data = data

        self._enable_band = False
        self._enable_snap = False
        self._interval_rect = None

        self._cursors = [DraggableVerticalLine(
            snapper=snapper, grabber=grabber, ax=ax, x=x, label='xo', parent=self)
            for x in cursors]
        self._children = []

        self.set_band(band)
        self.set_snap(False)

        self._interval_rect = DraggableVerticalRectangle(
            ax=ax, grabber=grabber, x=0, width=1, parent=self)
        self._interval_rect.remove()
        self._children = self._cursors[:]

        super().__init__()

    def get_data(self):
        return self._data

    def set_data(self, data):
        self._data = data

    def get_snap(self):
        return self._enable_snap

    def set_snap(self, value):
        self._enable_snap = value
        for line in self._cursors:
            line.set_snap_x(value)

    def get_band(self):
        return self._enable_band

    def set_band(self, value):
        self._enable_band = value

        if len(self._cursors) != 2:
            value = False

        has_interval = self._interval_rect in self._children

        if has_interval != value:
            if value:
                if self._interval_rect not in self._children:
                    xmin, xmax = self.interval()
                    self._interval_rect.set_bounds(xmin, 0, xmax - xmin, 1)
                    self._interval_rect.add()
                    self._children.append(self._interval_rect)
            else:
                if self._interval_rect in self._children:
                    self._interval_rect.remove()
                    self._children.remove(self._interval_rect)

    def get_n_cursors(self):
        return len(self._cursors)

    def set_n_cursors(self, value):
        n_cursors = len(self._cursors)
        diff = value - n_cursors

        if diff < 0:
            for i in range(-diff):
                last_cursor = self._cursors[-1]
                del self._cursors[-1]
                self._children.remove(last_cursor)
                last_cursor.remove()
        elif diff > 0:
            xmin, xmax = self.ax.get_xlim()
            width = xmax - xmin

            for i in range(n_cursors, value):
                j = i + 1
                x = xmin + (j / (value + 1)) * width
                x = _num_to_axis(x, self.ax.get_xaxis())

                cursor = DraggableVerticalLine(
                    snapper=self._snapper, grabber=self._grabber,
                    ax=self.ax, x=x,
                    parent=self)

                self._cursors.append(cursor)
                self._children.append(cursor)

        self.set_band(self._enable_band)
        self.set_snap(self._enable_snap)

    def get_x(self, cursor_n):
        cursor = self._cursors[cursor_n]
        return cursor.get_x()

    def set_x(self, x, cursor_n):
        cursor = self._cursors[cursor_n]
        y = cursor.get_y()
        cursor.move(x, y)
        self._canvas.draw_idle()

    def interval(self):
        res = self.ax.get_xlim()
        if len(self._cursors) >= 2:
            xs = [line.artist.get_xdata()[0] for line in self._cursors]
            res = (min(xs), max(xs))
        return res

    def x_range(self):
        return self.ax.get_xlim()

    def child_moved(self, child, dxdata, dydata):

        if child is self._interval_rect:
            for other_child in self._children:
                if other_child is not child:
                    x = other_child.get_x()
                    y = other_child.get_y()
                    other_child.set_x(x + dxdata)
                    other_child.set_y(y + dydata)

        if child in self._cursors:
            xmin, xmax = self.interval()
            self._interval_rect.set_bounds(xmin, 0, xmax - xmin, 1)

    def child_released(self, child):
        self.cursor_moved.emit()

    def data_line_labels(self):
        return [line.get_label() for line in self._data_lines()]

    def _data_lines(self):
        return [line for line in self.ax.lines
                if not SelectionArtist.is_selection(line)]

    def _get_line(self, label):
        res = None

        for line in self._data_lines():
            if line.get_label() == label:
                res = line
                break
        if res is None:
            raise KeyError(label)
        return res

    def line_data(self, label):
        line = self._get_line(label)
        xdata = line.get_xdata()
        ydata = line.get_ydata()
        return xdata, ydata

    def interval_line_data(self, label):
        xmin, xmax = self.interval()
        xdata, ydata = self.line_data(label)

        if len(self._cursors) == 2:

            if isinstance(xmin, datetime.datetime):
                xmin = xmin.replace(tzinfo=None)

            if isinstance(xmax, datetime.datetime):
                xmax = xmax.replace(tzinfo=None)

            mask = np.logical_and(xmin <= xdata, xdata <= xmax)
            return xdata[mask], ydata[mask]
        else:
            return xdata, ydata

    def interpolated_line_data(self, label, cursor_n, nearest_outside=False):
        def to_res(res, x0, dtype):
            if dtype:
                if not np.isnan(res):
                    res = np.float64([res]).astype(dtype)[0]
                    res = res.tolist().replace(tzinfo=x0.tzinfo)
            return res

        cursor = self._cursors[cursor_n]

        xdata, ydata = self._data[label]

        nan = float('nan')
        res = nan

        if not (len(xdata) and len(ydata)):
            return res

        x = cursor.get_x()

        dtype_orig = None

        if xdata.dtype.kind in ['m', 'M']:
            xdata_dtype = xdata.dtype.kind
            xdata = xdata.astype('f8')

        if ydata.dtype.kind in ['m', 'M']:
            ydata_dtype = ydata.dtype.kind
            dtype_orig = ydata.dtype
            ydata = ydata.astype('f8')

        x0 = x

        if isinstance(x, datetime.datetime):
            x = x.replace(tzinfo=None)
            x = np.datetime64(x, 'us').astype('f8')
        elif isinstance(x, datetime.timedelta):
            x = np.timedelta64(x, 'us').astype('f8')
            td_orig = True

        exact = xdata == x
        exact_count = np.count_nonzero(exact)

        if exact_count == 1:
            idx = np.flatnonzero(exact)[0]
            y = ydata[idx]
            res = to_res(y, x0, dtype_orig)
        elif exact_count > 1:
            if len(np.unique(ydata[exact])) == 1:
                idx = np.flatnonzero(exact)[0]
                y = ydata[idx]
                res = to_res(y, x0, dtype_orig)
        else:
            # TODO(erik): make the function support NaN values on the x-axis.
            # nxdata simply removes NaN values to avoid warnings from numpy.
            nxdata = xdata[~np.isnan(xdata)]

            in_seg = np.logical_or(
                np.logical_and(nxdata[:-1] <= x, nxdata[1:] >= x),
                np.logical_and(nxdata[:-1] >= x, nxdata[1:] <= x))

            in_seg_count = np.count_nonzero(in_seg)

            if in_seg_count < 2:

                sort_idx = np.argsort(xdata)
                xdata = xdata[sort_idx]
                ydata = ydata[sort_idx]

                if nearest_outside:
                    y = np.interp(x, xdata, ydata)
                else:
                    y = np.interp(
                        x, xdata, ydata, left=nan, right=nan)

                res = to_res(y, x0, dtype_orig)
        return res

    def add(self):
        for child in self._children:
            child.add()


# Tuple of range for cell value, (min, max).
RangeRole = QtCore.Qt.UserRole + 1


class CursorTableItemDelegate(QtWidgets.QItemDelegate):

    def createEditor(self, parent, option, index):

        value = index.model().data(index, QtCore.Qt.EditRole)
        value_range = index.model().data(index, RangeRole)

        if isinstance(value, datetime.datetime):
            editor = sywidgets.DateTimeWidget(parent=parent)
        else:
            editor = sywidgets.ValidatedFloatSpinBox(parent=parent)
            if value_range:
                editor.setMinimum(value_range[0])
                editor.setMaximum(value_range[1])
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, QtCore.Qt.EditRole)
        if isinstance(value, datetime.datetime):
            value = value.replace(tzinfo=datetime.timezone.utc)

        editor.setValue(value)
        editor.selectAll()

    def setModelData(self, editor, model, index):
        value = editor.value()
        if isinstance(value, datetime.datetime):
            value = value.replace(tzinfo=datetime.timezone.utc)
        index.model().setData(index, value, QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class CursorTableModel(QtCore.QAbstractTableModel):

    _cursor0_row_headers = ['X 0', 'Y 0']
    _cursor1_row_headers = ['X 1', 'Y 1']
    _stats_row_headers = ['Avg', 'Min', 'Max', 'Std', 'N']
    _delta_row_headers = ['X \u0394', 'Y \u0394']
    _all_row_headers = (
        _cursor0_row_headers + _cursor1_row_headers +
        _delta_row_headers + _stats_row_headers)

    def __init__(self, cursor_controller, column_names, parent=None):

        super().__init__(parent=parent)

        self._show_stats = False
        self._show_delta = False
        self._n_cursors = cursor_controller.get_n_cursors()

        self._cache = {}
        self._all_col_headers = column_names
        self._col_headers = []
        self._row_headers = []

        self._cursor_controller = cursor_controller
        self._cursor_controller.cursor_moved.connect(self.reset_data)

    def rowCount(self, index=QtCore.QModelIndex()):
        return len(self._row_headers)

    def columnCount(self, index=QtCore.QModelIndex()):
        return len(self._col_headers)

    def setData(self, index, value, role):
        if not index.isValid():
            return

        row = index.row()
        col = index.column()

        col_name = self._col_headers[col]
        row_name = self._row_headers[row]

        if role == QtCore.Qt.EditRole:
            if row_name == self._cursor0_row_headers[0]:
                self._cursor_controller.set_x(value, 0)
            elif row_name == self._cursor1_row_headers[0]:
                self._cursor_controller.set_x(value, 1)
            else:
                assert False, 'unknown row'

            self.reset_data()

        super().setData(index, value, role)

    def data(self, index, role):
        def interval_data(col_name):
            key = ('interval', col_name)
            res = self._cache.get(key)
            if res is  None:
                res = self._cursor_controller.interval_line_data(col_name)
                self._cache[key] = res
            return res

        if not index.isValid():
            return None
        row = index.row()
        col = index.column()
        data = float('nan')

        if role in [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole,
                    QtCore.Qt.ToolTipRole]:

            x_c0, y_c0 = self._cursor0_row_headers
            x_c1, y_c1 = self._cursor1_row_headers
            y_mean, y_min, y_max, y_std, n = self._stats_row_headers
            x_delta, y_delta = self._delta_row_headers

            col_name = self._col_headers[col]
            row_name = self._row_headers[row]

            tooltip_fmt = '{}'
            tooltip_fmt_move = '{} - edit to move cursor'
            tooltip_fmt_interp = '{} - interpolated'

            if role == QtCore.Qt.ToolTipRole:
                if row_name == x_c0:
                    tooltip_fmt = tooltip_fmt_move

                elif row_name == y_c0:
                    tooltip_fmt = tooltip_fmt_interp

                elif row_name == x_c1:
                    tooltip_fmt = tooltip_fmt_move

                elif row_name == y_c1:
                    tooltip_fmt = tooltip_fmt_interp

                elif row_name == y_delta:
                    tooltip_fmt = tooltip_fmt_interp

            res = self._cache.get((col_name, row_name))
            if res is not None:
                if role == QtCore.Qt.DisplayRole:
                    res = widget_utils.format_data(res, 2)
                elif role == QtCore.Qt.ToolTipRole:
                    res = tooltip_fmt.format(widget_utils.format_data(res))
                return res

            if row_name == x_c0:
                data = self._cursor_controller.get_x(0)

            elif row_name == y_c0:
                data = self._cursor_controller.interpolated_line_data(
                    col_name, 0)

            elif row_name == x_c1:
                data = self._cursor_controller.get_x(1)

            elif row_name == y_c1:
                data = self._cursor_controller.interpolated_line_data(
                    col_name, 1)

            elif row_name == n:
                ydata = interval_data(col_name)[1]
                data = len(ydata)

            elif row_name == y_mean:
                ydata = interval_data(col_name)[1]
                if len(ydata):
                    data = np.mean(ydata)

            elif row_name == y_min:
                ydata = interval_data(col_name)[1]
                if len(ydata):
                    data = np.min(ydata)

            elif row_name == y_max:
                ydata = interval_data(col_name)[1]
                if len(ydata):
                    data = np.max(ydata)

            elif row_name == y_std:
                ydata = interval_data(col_name)[1]
                if len(ydata):
                    data = np.std(ydata)

            elif row_name == x_delta:
                data0 = self._cursor_controller.get_x(0)
                data1 = self._cursor_controller.get_x(1)
                data = data1 - data0

            elif row_name == y_delta:
                data0 = self._cursor_controller.interpolated_line_data(
                    col_name, 0,
                    nearest_outside=True)

                data1 = self._cursor_controller.interpolated_line_data(
                    col_name, 1,
                    nearest_outside=True)

                data = data1 - data0
            else:
                assert False, row_name

            if isinstance(data, float) and np.isnan(data):
                data = ''

            self._cache[(col_name, row_name)] = data

            res = data
            if role == QtCore.Qt.DisplayRole:
                res = widget_utils.format_data(data, 2)
            elif role == QtCore.Qt.ToolTipRole:
                res = tooltip_fmt.format(widget_utils.format_data(res))
            return res
        elif role == RangeRole:
            col_name = self._col_headers[col]
            row_name = self._row_headers[row]
            return self._cursor_controller.x_range()

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return self._col_headers[section]
            elif role == QtCore.Qt.TextAlignmentRole:
                return QtCore.Qt.AlignLeft
            elif role == QtCore.Qt.ToolTipRole:
                return self._col_headers[section]

        elif orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                return self._row_headers[section]
            elif role == QtCore.Qt.TextAlignmentRole:
                return QtCore.Qt.AlignLeft
            elif role == QtCore.Qt.ToolTipRole:
                row_name = self._row_headers[section]
                # TODO(erik): fix duplication between data and headerData.

                x_c0, y_c0 = self._cursor0_row_headers
                x_c1, y_c1 = self._cursor1_row_headers
                y_mean, y_min, y_max, y_std, n = self._stats_row_headers
                x_delta, y_delta = self._delta_row_headers

                tooltip_fmt = '{}'
                tooltip_fmt_move = '{} - edit cell to move cursor'
                tooltip_fmt_interp = '{} - interpolated'

                if row_name == x_c0:
                    tooltip_fmt = tooltip_fmt_move

                elif row_name == y_c0:
                    tooltip_fmt = tooltip_fmt_interp

                elif row_name == x_c1:
                    tooltip_fmt = tooltip_fmt_move

                elif row_name == y_c1:
                    tooltip_fmt = tooltip_fmt_interp

                elif row_name == y_delta:
                    tooltip_fmt = tooltip_fmt_interp

                return tooltip_fmt.format(row_name)

        return super().headerData(section, orientation, role)

    def reset(self):
        self.beginResetModel()
        self._cache.clear()
        self.endResetModel()

    def add_signal(self, label):
        if label not in self._col_headers:
            self.insert_column(label)

    def remove_signal(self, label):
        if label in self._col_headers:
            self.remove_column(label)

    def update_signal(self, label):
        pass

    def set_show_stats(self, enabled):
        self._show_stats = enabled
        self._update_rows(self._n_cursors, enabled, self._show_delta)

    def get_show_stats(self):
        return self._show_stats

    def set_show_delta(self, enabled):
        self._show_delta = enabled
        self._update_rows(self._n_cursors, self._show_stats, enabled)

    def get_show_delta(self):
        return self._show_delta

    def _update_col_data(self, col, name):
        pass

    def _sort_to_pos(self, name, items, all_items):
        items = list(items)
        items.append(name)
        items = sorted(
            items, key=lambda x: all_items.index(x))
        return items.index(name)

    def insert_row(self, name):
        row = self._sort_to_pos(name, self._row_headers, self._all_row_headers)
        self.beginInsertRows(QtCore.QModelIndex(), row, row)
        self._row_headers.insert(row, name)
        self.endInsertRows()

    def insert_column(self, name):
        col = self._sort_to_pos(name, self._col_headers, self._all_col_headers)
        self.beginInsertColumns(QtCore.QModelIndex(), col, col)
        self._col_headers.insert(col, name)
        self.endInsertColumns()

    def remove_row(self, name):
        row = self._row_headers.index(name)
        self.beginRemoveRows(QtCore.QModelIndex(), row, row)
        self._reset_row_cache(row)
        del self._row_headers[row]
        self.endRemoveRows()

    def remove_column(self, name):
        col = self._col_headers.index(name)
        self.beginRemoveColumns(QtCore.QModelIndex(), col, col)
        self._reset_col_cache(col)
        del self._col_headers[col]
        self.endRemoveColumns()

    def clear_columns(self):
        if self._col_headers:
            self.beginRemoveColumns(QtCore.QModelIndex(), 0,
                                    self.columnCount() - 1)
            self._col_headers.clear()
            self._cache.clear()
            self.endRemoveColumns()

    def _is_x_row(self, row):
        row_name = self._row_headers[row]
        return row_name in [self._cursor0_row_headers[0],
                            self._cursor1_row_headers[0]]

    def flags(self, index):
        if not index.isValid():
            return False

        res = super().flags(index)

        if self._is_x_row(index.row()):
            res |= QtCore.Qt.ItemIsEditable
        return res

    def _update_rows(self, n_cursors, show_stats, show_delta):
        new_headers = []
        old_headers = self._row_headers[:]
        if n_cursors >= 1:
            new_headers.extend(self._cursor0_row_headers)

        if n_cursors >= 2:
            new_headers.extend(self._cursor1_row_headers)

            if show_stats:
                new_headers.extend(self._stats_row_headers)

            if show_delta:
                new_headers.extend(self._delta_row_headers)

        for header in set(old_headers).difference(new_headers):
            self.remove_row(header)

        for header in set(new_headers).difference(old_headers):
            self.insert_row(header)

    def set_n_cursors(self, n):
        assert n <= 2
        self._n_cursors = n
        self._cursor_controller.set_n_cursors(n)
        self._update_rows(n, self._show_stats, self._show_delta)

    def _reset_row_cache(self, row):
        row_name = self._row_headers[row]
        for col_name_ in self._all_col_headers:
            self._cache.pop((col_name_, row_name), None)

    def _reset_col_cache(self, col):
        col_name = self._col_headers[col]
        for row_name_ in self._all_row_headers:
            self._cache.pop((col_name, row_name_), None)

    def reset_data(self):
        self._cache.clear()

        rows = self.rowCount()
        cols = self.columnCount()

        if rows and cols:

            top_left = self.createIndex(0, 0)
            low_right = self.createIndex(rows - 1, cols - 1)

            self.dataChanged.emit(top_left, low_right)

    def set_col_headers(self, col_headers):
        self._all_col_headers = col_headers
        self.reset()
