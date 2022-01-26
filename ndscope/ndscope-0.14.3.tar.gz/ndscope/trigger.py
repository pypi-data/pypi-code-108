import numpy as np

import pyqtgraph as pg

from .const import LABEL_FILL, COLOR_MODE


class Trigger:
    __slots__ = [
        '__weakref__',
        'channel', 'line', 'invert', 'single',
    ]

    def __init__(self):
        self.channel = None
        self.line = pg.InfiniteLine(
            angle=0,
            movable=True,
            label='trigger level',
            labelOpts={
                'position': 0.5,
                'anchors': [(1, 0), (1, 1)],
                'fill': LABEL_FILL,
            },
        )
        self.line.sigPositionChanged.connect(self.update_level)
        self.invert = False
        self.single = False

    def set_font(self, font):
        """Set font label text"""
        self.line.label.textItem.setFont(font)

    def set_color_mode(self, mode):
        fg = COLOR_MODE[mode]['fg']
        bg = COLOR_MODE[mode]['bg']
        self.line.label.fill = bg
        self.line.label.setColor(fg)
        self.line.pen.setColor(fg)

    @property
    def active(self):
        return self.channel is not None

    def update_level(self, line):
        value = line.value()
        line.label.setText('trigger level: {:g}'.format(value))

    @property
    def level(self):
        return self.line.value()

    def set_level(self, value):
        self.line.setValue(value)

    @property
    def sigLevelChanged(self):
        return self.line.sigPositionChanged

    def set_single(self, value):
        self.single = value

    def set_invert(self, value):
        self.invert = value

    def check(self, data):
        """Check for trigger in last_append of DataBufferDict

        Returns trigger time or None

        """
        if self.channel is None:
            return

        t, y = data[self.channel].last_append()

        level = self.level
        yp = np.roll(y, 1)
        yp[0] = y[0]
        if self.invert:
            tind = np.where((yp >= level) & (y < level))[0]
        else:
            tind = np.where((yp <= level) & (y > level))[0]

        if not np.any(tind):
            return None

        tti = tind.min()
        ttime = t[tti]
        return ttime
