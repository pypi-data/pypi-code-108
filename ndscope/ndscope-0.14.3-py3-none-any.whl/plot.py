import copy
import collections

import numpy as np
from qtpy import QtCore
from qtpy.QtGui import QPen
from qtpy.QtCore import Signal
import pyqtgraph as pg
from pyqtgraph import PlotItem, PlotDataItem, FillBetweenItem

from gpstime import gpstime, gpsnow

from . import util
from . import const
from .plotMenu import NDScopePlotMenu
from . import template
from . import legend
from . import cursors


##################################################

CHANNEL_COLORS = {}


def hold_over_nan(y):
    """hold data over subsequent nans

    This function finds all nans in the input array, and produces an
    creates an output array that is nan everywhere except where the
    input array was nan.  Where the input array was nan, the output
    array will be the value of the input array right before the nan.
    If the first element of the input array is nan then zero will be
    used.  Example:

    y   = [nan, nan,   2,   3,   4,   5, nan, nan, nan,   9,  10]
    out = [  0,   0,   0, nan, nan,   5,   5,   5,   5,   5, nan]

    We use this for indicating "bad" data regions in plots.

    """
    nani = np.where(np.isnan(y))[0]
    if nani.size == y.size:
        return np.zeros_like(y, dtype=np.float)
    out = np.empty_like(y, dtype=np.float)
    out[:] = np.nan
    if nani.size == 0:
        return out
    ti = np.where(np.diff(nani) > 1)[0]
    nstart = np.append(nani[0], nani[ti+1])
    nend = np.append(nani[ti], nani[-1]) + 1
    for s, e in zip(nstart, nend):
        if s == 0:
            v = 0
        else:
            v = y[s-1]
        out[s-1:e+1] = v
    return out


##################################################

class TimeStringAxis(pg.AxisItem):
    def __init__(self, orientation='bottom', **kwargs):
        super().__init__(orientation, **kwargs)
        self.t0 = 0
        self.setTickStringsMode('relative')

    def t_to_relative(self, t):
        return str(util.TDStr(t))

    def t_to_gps(self, t):
        return str(t + self.t0)

    def t_to_utc(self, t):
        gps = gpstime.fromgps(t + self.t0)
        return gps.strftime(const.TICK_DATE_FMT)

    def t_to_local(self, t):
        gps = gpstime.fromgps(t + self.t0)
        local = gps.astimezone()
        return local.strftime(const.TICK_DATE_FMT)

    def setTickStringsMode(self, mode):
        func_map = {
            'relative': self.t_to_relative,
            'absolute GPS': self.t_to_gps,
            'absolute UTC': self.t_to_utc,
            'absolute local': self.t_to_local,
        }
        self.tick_func = func_map[mode]
        # this is needed to clear/update the ticks on change:
        self.picture = None
        self.update()
        self.mode = mode

    ######

    def tickSpacing(self, minVal, maxVal, size):
        span = abs(maxVal - minVal)
        for major, minordiv in const.TICK_SPACINGS:
            if span >= 3*major:
                break
        return [
            (major, 0),
            (major/minordiv, 0),
        ]

    def tickStrings(self, values, scale, spacing):
        return [self.tick_func(t) for t in values]


##################################################


class NDScopePlot(PlotItem):
    channel_select_request = Signal('PyQt_PyObject')
    channel_add_complete = Signal()
    new_plot_request = Signal('PyQt_PyObject')
    remove_plot_request = Signal('PyQt_PyObject')
    t0_reset = Signal(float)
    t_cursors_enabled = Signal(bool)
    t_cursor_moved = Signal('PyQt_PyObject')

    def __init__(self, data_store, *args, loc=None):
        """Initialize NDSCope Plot object

        """
        super().__init__(
            *args,
            axisItems={'bottom': TimeStringAxis()},
        )

        self.data = data_store
        self.loc = loc

        # dict of channel:curve
        self.channels = collections.OrderedDict()

        # plot options
        # use automatic downsampling and clipping to reduce the
        # drawing load
        self.setDownsampling(mode='peak')
        # clip data to only what's visible
        # FIXME: is this what we want?
        self.setClipToView(True)
        # don't auto-range x axis, since we have special handling
        self.disableAutoRange(axis='x')
        # hide auto-scale buttons
        self.hideButtons()
        # add legend
        self.legend = legend.Legend()
        self.legend.setParentItem(self.vb)
        self.legend.setVisible(False)
        # show grid lines
        self.showGrid(x=True, y=True, alpha=0.2)
        self.setLabel('left', 'counts')
        # limit the zooming range
        self.setLimits(
            minXRange=0.0001,
        )
        # accept drops
        self.setAcceptDrops(True)

        self.ctrlMenu = None
        vb = self.getViewBox()
        vb.menu = NDScopePlotMenu(self)

        # If this option is not removed then a default font size will
        # be set in the generated html that will not overridable by
        # setting the font.
        self.titleLabel.opts.pop('size')

        self.t_cursors = None
        self.y_cursors = None

    def dropEvent(self, event):
        data = event.mimeData()
        if data.hasFormat('text/plain'):
            text_list = data.text().splitlines()
            for text in text_list:
                self.add_channel(text)

    def add_channel(self, channel, **kwargs):
        """Add channel to plot

        keyword arguments are passed directly to NDScopePlotChannel.

        """
        if channel in self.channels:
            return
        cc = NDScopePlotChannel(channel, **kwargs)
        self._add_channel_obj(cc)

    def _add_channel_obj(self, cc):
        channel = cc.channel
        try:
            self.data.add_channel(channel)
        except ValueError:
            return
        self.channels[channel] = cc
        self.addItem(cc.curves['y'])
        self.addItem(cc.curves['bad'])
        self.enableAutoRange(axis='y')
        self._update_title_legend()
        cc.label_changed.connect(self._update_legend_item)
        cc.label_changed.connect(self._update_title_legend)
        self._update_legend_item(channel)

    def _select_channel_menu(self):
        self.channel_select_request.emit(self)

    def _add_channel_menu(self, channel):
        self.add_channel(channel)
        self.channel_add_complete.emit()

    def remove_channel(self, channel):
        """remove channel from plot

        """
        if channel not in self.channels:
            return
        cc = self.channels[channel]
        self._remove_channel_obj(cc)

    def _remove_channel_obj(self, cc):
        channel = cc.channel
        self.data.remove_channel(channel)
        self.legend.removeItem(cc.label)
        for curve in cc.curves.values():
            self.removeItem(curve)
        del self.channels[channel]
        self._update_title_legend()

    def set_channel_objs(self, chan_obj_list):
        """set plot channels from list NDScopePlotChannel objects

        Any channels currently being plotted that are not in list will
        be removed.

        """
        set_chans = set(chan_obj_list)
        cur_chans = set(self.channels.values())
        added = False
        for chan in cur_chans - set_chans:
            self._remove_channel_obj(chan)
        for chan in set_chans - cur_chans:
            self._add_channel_obj(chan)
            added = True
        if added:
            self.channel_add_complete.emit()

    def set_font(self, font):
        """Set label and axis font"""
        self.titleLabel.item.setFont(font)
        self.legend.setFont(font)
        self.axes['left']['item'].label.setFont(font)
        self.axes['bottom']['item'].setTickFont(font)
        self.axes['left']['item'].setTickFont(font)
        if self.t_cursors:
            self.t_cursors.set_font(font)
        if self.y_cursors:
            self.y_cursors.set_font(font)

    def set_color_mode(self, mode):
        fg = const.COLOR_MODE[mode]['fg']
        bg = const.COLOR_MODE[mode]['bg']
        self.titleLabel.setAttr('color', fg)
        self.titleLabel.setText(self.titleLabel.text)
        self.legend.setTextColor(fg)
        self.axes['left']['item'].set_color_mode(mode)
        self.axes['bottom']['item'].set_color_mode(mode)
        if self.t_cursors:
            self.t_cursors.set_color_mode(mode)
        if self.y_cursors:
            self.y_cursors.set_color_mode(mode)
        self._color_mode = mode

    def _reset_t0(self, val):
        self.t0_reset.emit(val)

    def enable_t_cursors(self):
        """enable T axis cursors"""
        if self.t_cursors:
            return
        self.t_cursors = cursors.TCursors()
        self.t_cursors.cursor_moved.connect(self._update_t_cursor)
        self.addItem(self.t_cursors.T1)
        self.addItem(self.t_cursors.T2)
        self.addItem(self.t_cursors.diff)
        self.t_cursors.set_color_mode(self._color_mode)

    def disable_t_cursors(self):
        """disable T axis cursors"""
        if not self.t_cursors:
            return
        self.removeItem(self.t_cursors.T1)
        self.removeItem(self.t_cursors.T2)
        self.removeItem(self.t_cursors.diff)
        self.t_cursors = None

    def _update_t_cursors(self, enable):
        self.t_cursors_enabled.emit(enable)

    def _update_t_cursor(self, indval):
        self.t_cursor_moved.emit(indval)

    def enable_y_cursors(self):
        """enable Y axis cursors"""
        if self.y_cursors:
            return
        self.y_cursors = cursors.YCursors()
        self.addItem(self.y_cursors.Y1)
        self.addItem(self.y_cursors.Y2)
        self.addItem(self.y_cursors.diff)
        self.y_cursors.reset(self)
        self.y_cursors.set_color_mode(self._color_mode)

    def disable_y_cursors(self):
        """disable Y axis cursors"""
        if not self.y_cursors:
            return
        self.removeItem(self.y_cursors.Y1)
        self.removeItem(self.y_cursors.Y2)
        self.removeItem(self.y_cursors.diff)
        self.y_cursors = None

    # SLOT
    def _update_legend_item(self, channel):
        cc = self.channels[channel]
        self.legend.removeItem(cc.curves['y'])
        self.legend.addItem(cc.curves['y'], cc.label)

    def _update_title_legend(self):
        """update plot title and legend"""
        if len(self.channels) < 1:
            self.legend.setVisible(False)
            self.setTitle(None)
        elif len(self.channels) == 1:
            self.legend.setVisible(False)
            self.setTitle(list(self.channels.values())[0].label)
        else:
            self.legend.setVisible(True)
            self.setTitle(None)

    def clear_data(self):
        """clear data for all channels

        """
        for curve in self.channels.values():
            curve.clear_data()

    def _set_t_limits(self, t0):
        """Set the t axis limits for a given t0"""
        self.setLimits(
            xMin=const.GPS_MIN-t0,
            #xMax=gpsnow()-t0+1,
        )

    def update(self, data, t0):
        """update all channel

        `data` should be a DataBufferDict object, and `t0` is the GPS
        time for t=0.

        """
        self.axes['bottom']['item'].t0 = t0
        self._set_t_limits(t0)

        ctype_changed = False

        units = set()

        for channel, cc in self.channels.items():
            if channel not in data or not data[channel]:
                continue

            cd = data[channel]

            if cd.is_trend and not cc.is_trend:
                self.addItem(cc.curves['min'])
                self.addItem(cc.curves['max'])
                if cc.curves['fill']:
                    self.addItem(cc.curves['fill'])
            elif not cd.is_trend and cc.is_trend:
                self.removeItem(cc.curves['min'])
                self.removeItem(cc.curves['max'])
                if cc.curves['fill']:
                    self.removeItem(cc.curves['fill'])

            ctype_changed |= cc.set_ctype(cd.ctype)

            cc.set_data(cd, t0)

            units.add(cc.get_unit(cd.unit))

        self.setLabel('left', '/'.join(list(units)))

        if ctype_changed:
            self._update_title_legend()


##################################################


class NDScopePlotChannel(QtCore.QObject):
    label_changed = Signal(str)

    def __init__(self, channel, **kwargs):
        """Initialize channel curve object

        Holds curves for y value, and for trend min/max/fill.

        Keyword arguments are trace style parameters, e.g. `color`,
        `width`, `unit`, `scale` and `offset`.  `color` can be a
        single letter color spec ('b', 'r', etc.), an integer, or an
        [r,g,b] list.  See the following for more info:

          http://www.pyqtgraph.org/documentation/functions.html#pyqtgraph.mkColor

        """
        super().__init__()

        global CHANNEL_COLORS

        self.channel = channel
        self.ctype = None
        self.is_trend = None
        self.params = dict(template.CURVE)
        self.label = channel

        self.curves = {}
        self.curves['y'] = PlotDataItem([0, 0], name=self.label)
        self.curves['min'] = PlotDataItem([0, 0])
        self.curves['max'] = PlotDataItem([0, 0])
        # FIXME: fill is expensive, so we disable it until figure it out
        if False:
            self.curves['fill'] = FillBetweenItem(
                self.curves['min'],
                self.curves['max'],
            )
        else:
            self.curves['fill'] = None
        # special curve for bad data (nans, infs)
        self.curves['bad'] = PlotDataItem(
            [0, 0],
            pen=pg.mkPen('r', width=1, style=QtCore.Qt.DotLine)
        )

        if channel in CHANNEL_COLORS:
            color = CHANNEL_COLORS[channel]
        else:
            while True:
                color = template.get_pen_color()
                if color not in CHANNEL_COLORS.values():
                    break
        CHANNEL_COLORS[channel] = color
        self.params['color'] = color

        self.set_params(**kwargs)

    def as_tuple(self):
        return (('channel', self.channel),) + tuple(sorted(self.params.items()))

    def __repr__(self):
        return "<{} {} {}>".format(
            self.__class__.__name__,
            self.channel,
            self.params,
        )

    # NOTE: we override the hash and eq definitions for these objects
    # so that we can compare them in sets.  hopefully this doesn't
    # cause any other problems
    def __hash__(self):
        return hash(self.as_tuple())

    def __eq__(self, other):
        return self.as_tuple() == other.as_tuple()

    def _update_transform(self):
        """update the transform function"""
        if self.params['scale'] != 1 or self.params['offset'] != 0:
            def transform(data):
                return (data + self.params['offset']) * self.params['scale']
        else:
            def transform(data):
                return data
        self.transform = transform

    def _update_label(self):
        label = self.channel
        if self.params['offset'] != 0:
            label += ' {:+g}'.format(self.params['offset'])
        if self.params['scale'] != 1:
            label += ' *{:g}'.format(self.params['scale'])
        if self.is_trend:
            label += ' [{}]'.format(self.ctype)
        self.label = label
        self.label_changed.emit(self.channel)

    def set_params(self, **params):
        """set parameters for this channel

        """
        PARAMS = ['color', 'width', 'unit', 'scale', 'offset']

        for param, value in params.items():
            if param not in PARAMS:
                raise KeyError(f"invalid parameter '{param}', options are: {PARAMS}")
            self.params[param] = value

        color = self.get_QColor()
        pen = pg.mkPen(color, width=self.params['width'])
        mmc = copy.copy(color)
        mmc.setAlpha(100)
        mmpen = pg.mkPen(mmc, style=QtCore.Qt.DashLine)
        self.curves['y'].setPen(pen)
        self.curves['min'].setPen(mmpen)
        self.curves['max'].setPen(mmpen)
        if self.curves['fill']:
            self.curves['fill'].setBrush(mmc)
        self._update_transform()
        self._update_label()
        self.redraw_data()

    def get_QColor(self):
        """Get channel color as a QColor object"""
        return pg.mkColor(self.params['color'])

    def set_ctype(self, ctype):
        """Update the channel ctype

        Returns True if type changed, False otherwise

        """
        if ctype == self.ctype:
            return False
        self.ctype = ctype
        if ctype in ['s-trend', 'm-trend']:
            self.is_trend = True
        else:
            self.is_trend = False
        self._update_label()
        return True

    def get_unit(self, default):
        """return channel unit"""
        unit = self.params.get('unit')
        if not unit:
            unit = default or 'counts'
        return unit

    def clear_data(self):
        """clear data for curves

        """
        for curve in self.curves.values():
            try:
                curve.setData(np.array([0, 0]))
            except:
                pass

    def _set_curve_data(self, mod, t, y):
        # FIXME: HACK: replace all +-infs with nans.  the infs
        # were causing the following exception in PlotCurveItem
        # when it tried to find the min/max of the array:
        # ValueError: zero-size array to reduction operation minimum which has no identity
        # using nan is not great, since that's also an indicator
        # of a gap, but not sure what else to use.
        try:
            np.place(y, np.isinf(y), np.nan)
        except ValueError:
            # this check throws a value error if y is int.  but in
            # that case there's nothing we need to convert, so
            # just pass
            pass
        self.curves[mod].setData(
            x=t,
            y=self.transform(y),
            connect="finite",
        )

    def set_data(self, data, t0):
        """set data for curves

        Data should be DataBuffer object.

        """
        t = data.tarray - t0

        if 'raw' in data:
            y = data['raw']
        else:
            y = data['mean']
            for mod in ['min', 'max']:
                self._set_curve_data(mod, t, data[mod])

        self._set_curve_data('y', t, y)

        self.curves['bad'].setData(
            x=t,
            y=hold_over_nan(y),
            connect="finite",
        )

    def redraw_data(self):
        """redraw all data, in case transform has changed"""
        for mod, curve in self.curves.items():
            if not curve:
                continue
            (t, y) = curve.getData()
            self._set_curve_data(mod, t, y)

##################################################

# This is a monkey patch to add a set_color_mode method to the
# pg.AxisItem class.

# Copied from pyqtgraph source version 0.12.3.
def _updateLabel(self):
    """Internal method to update the label according to the text"""
    self.label.setHtml(self.labelString())
    self._adjustSize()
    self.picture = None
    self.update()

pg.AxisItem._updateLabel = _updateLabel

def _set_color_mode(self, mode):
    # Modified from pyqtgraph source version 0.12.3 for AxisItem.setTextPen.
    # https://pyqtgraph.readthedocs.io/en/pyqtgraph-0.12.3/_modules/pyqtgraph/graphicsItems/AxisItem.html#AxisItem.setTextPen
    fg = const.COLOR_MODE[mode]['fg']
    pen = QPen(fg)
    self.picture = None
    self._textPen = pen
    self.labelStyle['color'] = self._textPen.color().name()
    self._updateLabel()

pg.AxisItem.set_color_mode = _set_color_mode
