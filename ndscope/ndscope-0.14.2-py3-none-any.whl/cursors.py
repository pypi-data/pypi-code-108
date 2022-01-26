# -*- coding: utf-8 -*-
from __future__ import division

import numpy as np
from qtpy import QtCore
from qtpy.QtCore import Qt
from qtpy.QtCore import Signal
import pyqtgraph as pg

from . import util
from .const import LABEL_FILL, COLOR_MODE


class TCursors(QtCore.QObject):
    __slots__ = [
        'T1', 'T2', 'diff',
    ]

    # the signalling here works differently than for the YCursor
    # class, which is all self contained.  for T cursors we want to
    # synchronize among all plots, so we create a single signal that
    # the scope can subscribe to, and then let the scope update the T
    # cursors in all the plots
    cursor_moved = Signal('PyQt_PyObject')

    def __init__(self):
        super().__init__()
        pen = pg.mkPen(style=Qt.DashLine)
        label_opts = {
            'position': 0,
            'anchors': [(0, 1), (1, 1)],
            'fill': LABEL_FILL,
        }
        self.T1 = pg.InfiniteLine(
            angle=90,
            pen=pen,
            movable=True,
            label='T1',
            labelOpts=label_opts,
        )
        self.T2 = pg.InfiniteLine(
            angle=90,
            pen=pen,
            movable=True,
            label='T2',
            labelOpts=label_opts,
        )
        self.T1._index = 'T1'
        self.T2._index = 'T2'
        self.T1.sigPositionChanged.connect(self.update_line)
        self.T2.sigPositionChanged.connect(self.update_line)
        self.diff = pg.InfiniteLine(
            angle=90,
            pen=(0, 0, 0, 0),
            label='diff',
            labelOpts={
                'position': 1,
                'anchors': [(0.5, 0), (0.5, 0)],
                'fill': LABEL_FILL,
            },
        )

    def set_font(self, font):
        """Set text label font"""
        for label in [self.T1.label, self.T2.label, self.diff.label]:
            label.textItem.setFont(font)

    def set_color_mode(self, mode):
        fg = COLOR_MODE[mode]['fg']
        bg = COLOR_MODE[mode]['bg']
        for line in [self.T1, self.T2, self.diff]:
            line.label.fill = bg
            line.label.setColor(fg)
            line.pen.setColor(fg)

    def update_line(self, line):
        self.cursor_moved.emit((line._index, line.value()))

    def get_values(self):
        return self.T1.value(), self.T2.value()

    def set_values(self, t1=None, t2=None):
        if t1:
            self.T1.setValue(t1)
            self.T1.label.setText(str(util.TDStr(t1)))
        if t2:
            self.T2.setValue(t2)
            self.T2.label.setText(str(util.TDStr(t2)))
        l0 = self.T1.value()
        l1 = self.T2.value()
        self.diff.setValue((l0 + l1)/2)
        vdiff = np.abs(l1 - l0)
        label = u'<table><tr><td rowspan="2" valign="middle">ΔT=</td><td>{}</td></tr><tr><td>{:g} Hz</td></tr></table></nobr>'.format(
            str(util.TDStr(vdiff)),
            1/vdiff,
        )
        self.diff.label.setHtml(label)

    def reset(self, plot):
        x, y = plot.viewRange()
        t1 = (2*x[0] + x[1])/3
        t2 = (x[0] + 2*x[1])/3
        self.set_values(t1=t1, t2=t2)


class YCursors(QtCore.QObject):
    __slots__ = [
        'Y1', 'Y2', 'diff',
    ]

    def __init__(self):
        super().__init__()
        pen = pg.mkPen(style=Qt.DashLine)
        label_opts = {
            'position': 0,
            'anchors': [(0, 0), (0, 1)],
            'fill': LABEL_FILL,
        }
        self.Y1 = pg.InfiniteLine(
            angle=0,
            pen=pen,
            movable=True,
            label='Y1',
            labelOpts=label_opts,
        )
        self.Y2 = pg.InfiniteLine(
            angle=0,
            pen=pen,
            movable=True,
            label='Y2',
            labelOpts=label_opts,
        )
        self.Y1.sigPositionChanged.connect(self.update_line)
        self.Y2.sigPositionChanged.connect(self.update_line)
        self.diff = pg.InfiniteLine(
            angle=0,
            pen=(0, 0, 0, 0),
            label='diff',
            labelOpts={
                'position': 1,
                'anchors': [(1, 0.5), (1, 0.5)],
                'fill': LABEL_FILL,
            },
        )

    def set_font(self, font):
        """Set text label font"""
        for label in [self.Y1.label, self.Y2.label, self.diff.label]:
            label.textItem.setFont(font)

    def set_color_mode(self, mode):
        fg = COLOR_MODE[mode]['fg']
        bg = COLOR_MODE[mode]['bg']
        for line in [self.Y1, self.Y2, self.diff]:
            line.label.fill = bg
            line.label.setColor(fg)
            line.pen.setColor(fg)

    def update_line(self, line):
        value = line.value()
        line.label.setText('{:g}'.format(value))
        l0 = self.Y1.value()
        l1 = self.Y2.value()
        self.diff.setValue((l0 + l1)/2)
        vdiff = np.abs(l1 - l0)
        label = u'ΔY={:g}'.format(vdiff)
        self.diff.label.setText(label)

    def get_values(self):
        return self.Y1.value(), self.Y2.value()

    def set_values(self, y1=None, y2=None):
        if y1:
            self.Y1.setValue(y1)
        if y2:
            self.Y2.setValue(y2)

    def reset(self, plot):
        x, y = plot.viewRange()
        y1 = (2*y[0] + y[1])/3
        y2 = (y[0] + 2*y[1])/3
        self.Y1.setValue(y1)
        self.Y2.setValue(y2)
