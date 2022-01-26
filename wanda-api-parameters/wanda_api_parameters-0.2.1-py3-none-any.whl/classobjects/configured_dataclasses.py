from dataclasses import dataclass, field
from typing import List, Tuple
import numpy as np

@dataclass
class FigureData:
    """ "Class to store figure data contains the following parameters:
    :param title (str) tile of the plot
    :param x_label (str) xlabel of the plot
    :param y_label (str) ylabel of the plot
    :param c_label (str) clabel of the plot
    :param x_axis (list[Float]) [xmin, xtick, xmax, xscale]
    :param y_axis (list[Float]) [ymin, ytick, ymax, yscale]
    :param c_axis (list[Float]) [cmin, ctick, cmax, cscale]
    :param times (int) Used in the RPlot functionality to make Route Plots at different time intervals.
    """

    title: str = None
    x_label: str = None
    y_label: str = None
    c_label: str= None
    x_axis: Tuple[float] = field(default_factory=lambda: (0.0, 0.1, 1.0, 1.0))
    y_axis: Tuple[float] = field(default_factory=lambda: (0.0, 0.1, 1.0, 1.0))
    c_axis: Tuple[float] = field(default_factory=lambda: (None, None, None, None))
    times: int = None

    def plot_arguments(self) -> dict:
        opt_dict = {"xmin": self.x_axis[0],
                    "title": self.title,
                    "xlabel": self.x_label,
                    "xmax": self.x_axis[2],
                    "xscale": self.x_axis[3],
                    "ylabel": self.y_label,
                    "ymin": self.y_axis[0],
                    "ymax": self.y_axis[2],
                    "yscale": self.y_axis[3],
                    }
        return opt_dict

if __name__ == "__main__":
    FD = FigureData()
