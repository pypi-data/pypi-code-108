import numpy as np
from dataclasses import dataclass, field
from typing import List
from ...math import numerical


@dataclass
class LineXY:
    x: np.array = None
    y: np.array = None
    name: str = None
    tags: List[str] = field(default_factory=list)

    def area_under_curve(self, x_start=None, x_end=None):
        if x_start is None:
            x_start = self.x[0]
        if x_end is None:
            x_end = self.x[-1]
        return numerical.area_under_curve(x=self.x,
                                          y=self.y,
                                          x_start=x_start,
                                          x_end=x_end)

    def xy_with_endpoints(self, x_start, x_end):
        return numerical.xy_with_endpoints(x=self.x,
                                           y=self.y,
                                           x_start=x_start,
                                           x_end=x_end)

    @classmethod
    def from_txt_delimited(cls, fname, delimiter=' ', xcol=0, ycol=1):
        _x, _y = np.loadtxt(fname, delimiter=delimiter, usecols=(xcol, ycol), unpack=True)
        return cls(x=_x, y=_y)

    def load_delimited(self, fname, delimiter=' '):
        self.x, self.y = np.loadtxt(fname, delimiter=delimiter, usecols=(0, 1), unpack=True)

    # not working...νομίζω
    def load_space_delimited_string(self, text, delimiter=' '):
        self.x_ini = np.array([], dtype=np.float)
        self.y_ini = np.array([], dtype=np.float)
        spl = text.splitlines()
        for ln in spl:
            xy = ln.split(delimiter)
            self.x_ini = np.append(self.x_ini, xy[0])
            self.y_ini = np.append(self.y_ini, xy[1])
        self.x_ini = self.x_ini.astype(float)
        self.y_ini = self.y_ini.astype(float)

    @property
    def x_max(self):
        return max(self.x)

    @property
    def x_min(self):
        return min(self.x)

    @property
    def y_max(self):
        return max(self.y)

    @property
    def y_min(self):
        return min(self.y)

    @property
    def y_max_index(self):
        return np.argmax(self.y)
