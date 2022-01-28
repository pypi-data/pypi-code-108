import re
from typing import Optional, Union

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from pandas.core.series import Series

from openqlab.conversion import db
from openqlab.io import DataContainer


def zero_span(
    traces: DataContainer,
    normalize: bool = True,
    title: Optional[str] = "Zero Span",
    annotate: bool = True,
    digits_number: int = 2,
    x_pos: int = 20,
    alignment: str = "left",
    ax: matplotlib.axes.Axes = None,
) -> Figure:
    """
    Create a sensible plot for zero-span squeezing `scope` measurements.

    Args:
        traces : A Pandas :obj:`DataFrame` containing the zero-span traces,
            where the time-base is given in the frame's index.
        normalize (bool, optional):
            Normalize the data to the vacuum trace, which requires a column
            name starting with "*vac*".
        title (str, optional):
            The figure title.
        annotate (bool, optional):
            Add noise values to the plot.
        digits_number (int, optional):
            Number of digits for the calculated dB values.
        x_pos (int, optional):
            Distance between graph and labels.
        alignment (str, optional):
            Horizontal alignment of labels.
            Can be "left", "center" or "right".
        ax (Axes, optional):
            Provide an Axes for advanced figures.

    Returns:
        matplotlib.figure.Figure: A handle to the created matplotlib Figure.
    """
    if ax is None:
        _, ax = plt.subplots()

    ylabel = "Noise Power (dBm)"
    unit = "dBm"
    vac_trace = None
    for trace in traces:
        if re.match("vac", trace, re.IGNORECASE):
            vac_trace = trace
            break

    if vac_trace and normalize:
        vac_level = db.mean(traces[vac_trace])
        traces = traces - vac_level
        ylabel = "Relative Noise (dB)"
        unit = "dB"

    traces.plot(ax=ax, title=title)
    ax.legend(loc="best", frameon=True)
    plt.ylabel(ylabel)
    plt.grid(True)

    # add average values for those traces that don't fluctuate too much, i.e.
    # not for McDonald's _type traces
    ii = 0
    for trace in traces:
        std = traces[trace].std()
        if annotate and std < 1:
            mean_val = db.mean(traces[trace])
            ax.annotate(
                f"{mean_val:.{digits_number}f} {unit}",
                (traces.index[-1], mean_val),
                (x_pos, 0),
                textcoords="offset points",
                horizontalalignment=alignment,
                verticalalignment="center",
                color=ax.lines[ii].get_color(),
            )
        ii += 1
    return ax.figure


# SCOPE
#
# A very simple plot of time-domain traces, e.g. from an oscilloscope
def scope(
    traces: Union[Series, DataContainer], title: str = "Oscilloscope View"
) -> Figure:
    """
    Create plot for oscilloscope data.

    This function plots up to four channels from oscilloscope time-voltage
    data into one plot. Each trace will have its own auto-scaled y axis.

    Args:
        traces : A Pandas :obj:`DataFrame` containing the time-domain traces,
            where the time-base is given by the frame's index.
        title : The figure title.

    Returns:
        matplotlib.figure.Figure: A handle to the created matplotlib figure.
    """
    from mpl_toolkits.axes_grid1 import host_subplot
    import mpl_toolkits.axisartist as AA

    # then you can also conviniently put in a single column, which would otherwise be a series
    traces = DataContainer(traces)
    offset = 50
    Ntraces = len(traces.columns)
    if Ntraces > 4:
        raise Exception("This plot only works with up to four traces.")

    fig = plt.figure()
    host = host_subplot(111, axes_class=AA.Axes)
    plt.subplots_adjust(right=1.0 - 0.11 * (Ntraces - 1))

    (line,) = host.plot(
        np.array(traces.index), np.array(traces.iloc[:, 0]), label=traces.columns[0]
    )
    host.set_ylabel(traces.columns[0])
    host.set_xlabel(traces.index.name)
    host.axis["left"].label.set_color(line.get_color())

    for ii in range(1, Ntraces):
        ax = host.twinx()
        if ii >= 2:
            new_fixed_axis = ax.get_grid_helper().new_fixed_axis
            pax = new_fixed_axis(loc="right", axes=ax, offset=((ii - 1) * offset, 0))

            pax.line.set_linewidth(0.5)
            pax.line.set_color("k")
            pax.major_ticks.set_linewidth(0.5)
            pax.major_ticks.set_color("k")
            pax.major_ticks.set_ticksize(4.0)
            ax.axis["right"] = pax

        (line,) = ax.plot(
            np.array(traces.index),
            np.array(traces.iloc[:, ii]),
            label=traces.columns[ii],
        )
        ax.axis["right"].toggle(all=True)
        ax.set_ylabel(traces.columns[ii])
        ax.axis["right"].label.set_color(line.get_color())

    host.grid(True, zorder=1)
    host.set_title(title)
    return fig
