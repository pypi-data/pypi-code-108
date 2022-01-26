import numpy as np
import plotext as plt

from typing import List
from rich.jupyter import JupyterMixin
from rich.ansi import AnsiDecoder
from rich.console import Group as RenderGroup
from rich.layout import Layout
from rich.panel import Panel


def plot_race(gender: str, length: int, names: List[str], lap_times: np.array, *size):
    """Function that takes all parameters and times and produces the two plots in the tracking view. Depends mainly on
     plotext

    :param str gender: string indicating if the race is for Men or Women. Accepted values are ["M", "F"]
    :param int length: integer indicating the length of the race. Accepted values are
     [500, 1000, 1500, 3000, 5000, 10000]

    :param List[str] names: List of strings with the names of the athletes.
    :param np.array lap_times:  Numpy array with the times so far.
    :param size: Additional arguments for the width and the height of the plots
    :return:
    """
    colors = ("red", "blue")

    gender_name = "Men" if gender == "M" else "Women"
    title_names = " vs ".join(names)
    nr_athletes = len(names)
    nr_laps = lap_times.shape[1]
    plt.subplots(2,1)

    total_times = np.cumsum(lap_times, axis=1)
    total_times[lap_times == 0] = 0
    # Plot of the total
    plt.subplot(1, 1)
    for i in range(nr_athletes):
        if total_times[i, :].sum() == 0:
            athlete_times = total_times[i, :]
        else:
            athlete_times = total_times[i, total_times[i, :] > 0]
        plt.plot(athlete_times, color=colors[i], label=names[i])
    plt.plotsize(*size)
    plt.ylim(0, nr_laps * 35)
    plt.title(f"{gender_name}'s {length}m race total times: {title_names}")
    plt.xticks(list(range(nr_laps)))
    plt.xlim(1, nr_laps)

    # Plot of the lap times
    plt.subplot(2, 1)
    for i in range(nr_athletes):
        if total_times[i, :].sum() == 0:
            athlete_times = lap_times[i, :]
        else:
            athlete_times = lap_times[i, lap_times[i, :] > 0]
        plt.plot(athlete_times, color=colors[i])
    plt.plotsize(*size)
    plt.ylim(5, 35)
    plt.title(f"{gender_name}'s {length}m race lap times: {title_names}")
    plt.xticks(list(range(nr_laps)))
    plt.xlim(1, nr_laps)
    return plt.build()


class plotextMixin(JupyterMixin):
    """plotextMixin that allows plotext figures to be placed inside a rich.Layout. Got the code from
     https://github.com/piccolomo/plotext/issues/26
    """
    def __init__(self, gender: str, length: int, names: List[str], lap_times: np.array):
        """Initialize

        :param str gender: string indicating if the race is for Men or Women. Accepted values are ["M", "F"]
        :param int length: integer indicating the length of the race. Accepted values are
         [500, 1000, 1500, 3000, 5000, 10000]

        :param List[str] names: List of strings with the names of the athletes.
        :param np.array lap_times:  Numpy array with the times so far.
        """
        self.decoder = AnsiDecoder()
        self.gender = gender
        self.length = length
        self.names = names
        self.lap_times = lap_times

    def __rich_console__(self, console, options):
        self.width = options.max_width or console.width
        self.height = options.height or console.height
        canvas = plot_race(
            self.gender,
            self.length,
            self.names,
            self.lap_times,
            self.width,
            self.height / 2)
        self.rich_canvas = RenderGroup(*self.decoder.decode(canvas))
        yield self.rich_canvas


def create_plotext_panel(
        gender: str,
        length: int,
        names: List[str],
        lap_times: np.array,
        layout: Layout) -> Panel:
    """Creates the actual ponel with the plotext in it. The layouy that is supplied will be used to put the panel into.

    :param str gender: string indicating if the race is for Men or Women. Accepted values are ["M", "F"]
    :param int length: integer indicating the length of the race. Accepted values are
     [500, 1000, 1500, 3000, 5000, 10000]

    :param List[str] names: List of strings with the names of the athletes.
    :param np.array lap_times:  Numpy array with the times so far.
    :param rich.Layout layout:  The layout in which the plotext figure will be placed.
    :return rich.Panel:  The panel with the plotext in it is returned
    """
    mix = plotextMixin(
        gender,
        length,
        names,
        lap_times
    )
    mix = Panel(mix)
    layout.update(mix)
    return mix