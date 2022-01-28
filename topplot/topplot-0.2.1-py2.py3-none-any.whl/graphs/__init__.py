# Copyright (c) 2019-2020 Jonathan Sambrook and Codethink Ltd.
#
#    This file is part of Topplot.
#
#    Topplot is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Topplot is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Topplot.  If not, see <https://www.gnu.org/licenses/>.
#
# -----------------------------------------------------------------------------
# Grapher has one or more FigManagers.
# FigManager has one figure with one or more plots/subplots and implements
# per-figure functionality.
# Grapher constructs figures, plots the data, and performs supra-FigManager
# functions too.
# -----------------------------------------------------------------------------

# pylint: disable=too-many-lines # C0302: Too many lines in module (>1000)

import sys
from typing import Callable, Dict

import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from ..config import Config
from ..dataframes import Dataframes
from ..figman import FigManager
from ..linestyler import LineStyler
from ..progress_window import ProgressWindow
from ..rcparams import override_rcParams
from ..graphmap import GraphMap
from ..utils import die, warn

try:
    import mplcursors

    mplcursors_present = True
except ImportError:
    print(
        "The mplcursors Python module is not installed, so annotations are not"
        " available. Hint: pip3 install mplcursors"
    )
    mplcursors_present = False

# -----------------------------------------------------------------------------
# Select GUI toolkit

mpl.use("TKAgg")

# -----------------------------------------------------------------------------


def add_annotations(figman, ax):
    """Add mplcursors annotation capability for the given axis' lines, if available."""
    if "mplcursors" in sys.modules:
        c = mplcursors.Cursor(hover=False, multiple=True, artists=tuple(ax.get_lines()))

        # At the time of writing (mpl 3.1.0) mpl doesn't allow consuming of gui
        # events, so they're propogated to all hooks. Which means that
        # mplcursors annotations are triggered even when they are underneath
        # legends.
        # This on_add closure callback fixes that situation.
        def on_add(sel):
            # Convert from data co-ords to display co-ords
            x, y = ax.transData.transform(tuple(sel.target))

            # Cycle through axes' legends checking for hits
            fake_event = mpl.backend_bases.MouseEvent("dummy", figman.fig.canvas, x, y)

            for legend in figman.get_legends():
                result, _ = legend.contains(fake_event)

                # Remove sel on hit
                if result:
                    c.remove_selection(sel)

        c.connect("add", on_add)


# -----------------------------------------------------------------------------


def set_x_axis_time_formatting(ax: mpl.axis.XAxis):
    """Turn on H:M:S date format for the given axis."""
    ax.xaxis.axis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))


# -----------------------------------------------------------------------------


class Grapher:
    """Class to encapsulate the graphing side of topplot."""

    # pylint: disable=import-outside-toplevel
    from ._cpus import graph_cpus, graph_cpu_per_cpu
    from ._legends import single_legend, combined_legend, otm_legend
    from ._mem import graph_mem
    from ._overview import graph_overview, graph_by_overview_ordinal
    from ._poi import graph_poi, graph_poi_per_cpu
    from ._tasks import graph_procps_tasks, graph_busybox_tasks

    # -------------------------------------------------- -----------------------

    def __init__(
        self,
        graph_map: GraphMap,
        config: Config,
        data: Dataframes,
        mem_unit: str,
        mem_cached_or_available: str,
        progress_window: ProgressWindow,
    ):
        self.at_close : Callable[[None], None]
        self.config = config
        self.data = data
        self.mem_unit = mem_unit
        self.graph_map = graph_map
        self.progress_window = progress_window
        width, height = progress_window.get_curr_screen_dimensions(scale=0.9)
        self.window_size = f"{width}x{height}"

        self.display_legends = True

        self.fig_manager: Dict[str, FigManager] = {}

        self.mem_cached_or_available = mem_cached_or_available.replace("_", " ")
        self.mplcursors_present = mplcursors_present

        self.linestyler = LineStyler()

        self.colours = {
            "combined": "red",
            "poi_cpu": "red",
            "poi_mem": "blue",
            "user": "green",
            "system": "red",
            "nice": "blue",
            "idle": (0.3, 0.3, 0.3),
            "wait": "black",
            "hw irq": "orange",
            "sw irq": "cyan",
            "steal": "gray",
            "exec": "chartreuse",
            "task running": "green",
            "task sleeping": "blue",
            "task stopped": "red",
            "task zombie": "black",
            "mem used": "blue",
            "mem free": "green",
            "mem buffers": "pink",
            self.mem_cached_or_available: "green",
            "swap free": "purple",
            "load average": "purple",
            "fig_face": (  # Equivalent to ProgressWindow's __init__().bg = "#F2F2E6".
                0.95,
                0.95,
                0.90,
            ),  # Keep in sync.
        }

        self.markers = {
            "user": "$u$",
            "system": "$s$",
            "nice": "$n$",
            "idle": "$i$",
            "wait": "$w$",
            "hw irq": "$hw$",
            "sw irq": "$sw$",
            "steal": "$st$",
            "exec": "$x$",
        }

        if self.config.cores > 1:
            for core in range(self.config.cores):
                tmp = {}
                for (k, v) in self.markers.items():
                    tmp[f"{core}{k}"] = f"{v}{core}"
                if tmp:
                    self.markers.update(tmp)

        self.cartesian_map = [["", ""], ["", ""]]

    # --------------------------------------------------------------------------

    def ordinal_to_title(self, n: int) -> str:
        """Convert from four-by-one array index to title stored in two-by-two array index."""
        assert (0 <= n <= 3), f"n must be between 0 and 3 but is {n}"
        x = int(n / 2)
        y = n % 2
        return self.cartesian_map[x][y]

    # --------------------------------------------------------------------------

    def title(self, text: str) -> str:
        """Common title formatting."""
        return f"topplot : {self.config.toplog_filename} : {text}"

    # --------------------------------------------------------------------------

    @staticmethod
    def common_axes(figman: FigManager, ax: mpl.axis.Axis):
        """Styles for any/all axes."""
        ax.set_facecolor("white")
        ax.margins(0)
        ax.set_xlabel("")
        set_x_axis_time_formatting(ax)
        add_annotations(figman, ax)

    # --------------------------------------------------------------------------

    def common_ax1(self, figman: FigManager, ax: mpl.axis.Axis):
        """Styles for 'primary' axes."""
        self.common_axes(figman, ax)
        ax.grid(linestyle=":", linewidth="0.5", color="black", alpha=0.5)

    # --------------------------------------------------------------------------

    def common_ax2(self, figman: FigManager, ax: mpl.axis.Axis):
        """Styles for 'secondary' axes."""
        self.common_axes(figman, ax)
        ax.grid(linestyle="--", linewidth="0.5", color="black", alpha=0.75)

    # --------------------------------------------------------------------------

    def dispense_graph(
        self,
        title: str,
        figman_name: str,
        setup: Callable[[FigManager], None],
        generate_figman: Callable[[None], None],
        use_progress_window: bool,
    ):
        """Handle progress window when creating graph."""
        if figman_name in self.fig_manager:
            self.fig_manager[figman_name].show()
        else:

            def create_graph(self):
                figman = generate_figman()

                figman.setup_graphing(setup)

                if use_progress_window:
                    self.progress_window.hide()

                self.fig_manager[figman_name] = figman

            if use_progress_window:
                self.progress_window.update_status(f"preparing '{title}'")
                self.progress_window.show()
                self.progress_window.root.after(100, create_graph, self)
            else:
                create_graph(self)

    # --------------------------------------------------------------------------

    def figs_foo(
        self, func: Callable[[FigManager], None], all_figs: bool, name: str = None
    ):
        """Call specified method on all the figs, the specified one,
        or the most recently created one."""
        if self.fig_manager:
            figs = list(self.fig_manager.values())
            if name is not None:
                figs = next(filter(lambda x: x == name, figs))

            if figs:
                to_do_list = figs if all_figs else [figs[-1]]
                for figman in to_do_list:
                    if figman:
                        func(figman)

    # --------------------------------------------------------------------------

    def save_figs(self, all_figs: bool = True, name: str = None):
        """Save pngs of all the figs, the specified one, or the most recently created one.."""
        self.figs_foo(FigManager.save, all_figs, name)

    # --------------------------------------------------------------------------

    def close_figs(self, all_figs: bool = True, name: str = None):
        """Close all the figs, the specified one, or the most recently created one.."""
        self.figs_foo(FigManager.close, all_figs, name)
        self.close_check()

    # --------------------------------------------------------------------------

    def close_check(self):
        """FigManagers call this when closing to exit the app if they were the last one."""
        if not self.fig_manager and self.at_close is not None:
            self.at_close()

    # --------------------------------------------------------------------------

    def prep_cartesian_title_map(self):
        for (x, y, title) in zip([0, 0, 1, 1], [0, 1, 0, 1], self.graph_map.keys()):
            self.cartesian_map[x][y] = title

    # --------------------------------------------------------------------------

    def doit(
        self, at_showtime: Callable[[None], None], at_close: Callable[[None], None]
    ):
        """Main function for setting things up and running."""
        self.at_close = at_close

        override_rcParams()

        self.prep_cartesian_title_map()

        count = 1

        if len(self.config.which_graphs) > 0:
            count = 0
            for c in self.config.which_graphs:
                if c.isnumeric():
                    i = int(c)
                    if i == 0:
                        self.graph_overview()
                        count += 1

                    elif 1 <= i <= 4:
                        self.graph_by_overview_ordinal(i - 1)
                        count += 1

                    else:
                        warn("'-g' takes numbers from 0 to 4.")

                elif c == "c":
                    if self.config.has_cpu_column and self.config.cores > 1:
                        self.graph_poi_per_cpu()
                        count += 1
                    else:
                        warn("No multi-core data available to plot POI by CPU core.")

                elif c == "C":
                    if self.config.has_cpu_rows and self.config.cores > 1:
                        self.graph_cpu_per_cpu()
                        count += 1
                    else:
                        warn("No multi-core data available to plot CPU data by core.")

                elif c == "p":
                    if count > 0:
                        self.save_figs(all_figs=False)

                elif c == "P":
                    if count > 0:
                        self.save_figs()

                elif c == "q":
                    if count > 0:
                        self.close_figs(all_figs=False)
                        if count > 1:
                            count -= 1
                        else:
                            break
                    else:
                        break

                elif c == "Q":
                    if count > 0:
                        self.close_figs()
                        count = 0
                    break

                else:
                    die(f"The character '{c}' doesn't represent a graph.")

        else:
            self.graph_overview()

        at_showtime()
        if count > 0:
            plt.show()


# -----------------------------------------------------------------------------
# vi: sw=4:ts=4:et
