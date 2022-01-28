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

import os
import re
import sys
from threading import Timer

import matplotlib as mpl
import matplotlib.pyplot as plt


class DummyEvent:
    def __init__(self, artist, mouseevent):
        self.artist = artist
        self.mouseevent = mouseevent


# -----------------------------------------------------------------------------
# Class to abstract the management of Figs (windows)
#
# The Grapher has one or more FigManagers. It encapsulates the graphing side of topplot.
# A FigManager has one figure with one or more plots/subplots.


class FigManager:
    class PairHierarchy:
        def __init__(self):
            self._primaries = []
            self._map = {}

        def append(self, primary, secondary):
            self._primaries.append(primary)
            self._map[primary] = secondary
            self._map[secondary] = primary

        def __contains__(self, key):
            return key in self._map

        def __len__(self):
            return len(self._map)

        def __getitem__(self, index):
            if isinstance(index, int):
                len_primaries = len(self._primaries)
                if index > 2 * len_primaries:
                    raise KeyError(f"Invalid index: '{index}'")
                return (
                    self._primaries[index]
                    if index < len_primaries
                    else self._map[self._primaries[index]]
                )
            return self._map[index]

        def primary(self, key):
            if key in self._map:
                return key if self.is_primary(key) else self._map[key]
            raise KeyError(f"Not in PairHierarchy: '{key}'")

        def is_primary(self, key):
            return key in self._primaries

        def is_secondary(self, key):
            return key in self._map and not self.is_primary(key)

    def __init__(
        self,
        name,
        parent,
        title,
        window_size,
        x,
        y,
        fig=None,
        subtitle=False,
        *,
        share_legends_regex=None,
    ):
        self.name = name
        self.parent = parent

        self.ax_pairs = (
            FigManager.PairHierarchy()
        )  # Know who your buddy is, if you have one
        self.ax_name_map = {}  # Know who axes are

        self.leglines = {}  # map legend lines  to plotted lines
        self.legtexts = {}  # map legend lines  to legend texts and vice versa
        self.legmarkers = {}  # map legend lines  to legend line markers
        self.legtitles = {}  # map legend titles to plotted lines
        self.legotm = {}  # map otm legend elements to leglines from src legend
        self.legotmtitles = {}  # map otm legend title to otm leglines
        self.legotmtexts = {}  # map otm legend lines to otm legend texts and vice versa

        self.legends = {}  # map of extra legends (i.e. not ones that came with an axis)

        # Used to indicate that clicks should be replicated or shared across all
        # peering legends
        self.share_legends_regex = share_legends_regex

        self.title, _, self.subtitle = title.partition("\n")
        self.fig = plt.figure() if fig is None else fig
        self.plots = self.fig.subplots(x, y)
        self.fig.canvas.set_window_title(self.title)

        win = self.fig.canvas.manager.window
        win.geometry(window_size)  # Tkinter specific
        win.update_idletasks()
        win.after_idle(self.parent.progress_window.center, win)

        self.fig.suptitle(self.title, weight="semibold")
        if subtitle:
            # WARNING: going off mpl API here to get the figure's title's
            # position and fontsize
            x, y = self.fig._suptitle.get_position()
            fontsize = self.fig._suptitle.get_fontsize()
            self.fig.text(
                0.5, 1 - (1 - y) * 2, self.subtitle, fontsize=fontsize, ha="center"
            )

        self.fig.set_facecolor(parent.colours["fig_face"])

        #    cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        _ = self.fig.canvas.mpl_connect("key_press_event", self.onkey)
        _ = self.fig.canvas.mpl_connect("close_event", self.onclose)
        _ = self.fig.canvas.mpl_connect("pick_event", self.onpick)
        _ = self.fig.canvas.mpl_connect("motion_notify_event", self.onmove)

        self.help_text_box = None
        self.showing_help = 0

        self.msg_text_box = None
        self.msg_timer = None

        self.toggle_axes_legend_state = {}

        self.key_presses = {}

        self.key_presses["c"] = [
            lambda self, e: self.display_msg("No multi-core POI data available.", 1)
            if self.parent.config.cores < 2
            else self.display_msg("--dont-graph-cpu-lines on the commandline", 1)
            if not self.parent.config.plot_poi_cpu_lines
            else self.parent.graph_poi_per_cpu(use_progress_window=True),
            "Display POI data in a separate graph for each CPU core.",
        ]

        self.key_presses["C"] = [
            lambda self, e: self.parent.graph_cpu_per_cpu(use_progress_window=True)
            if self.parent.config.has_cpu_rows
            else self.display_msg("No multi-core CPU data available.", 1),
            "Display CPU data in a separate graph for each CPU core.",
        ]

        if self.parent.mplcursors_present:
            self.key_presses["e"] = [
                None,  # Documenting mplcursors default action
                "Toggle whether mplcursors is active or not.",
            ]

        self.key_presses["l"] = [
            lambda self, e: self.toggle_legends(e.inaxes),
            "Toggle legend(s). [#1]",
        ]

        self.key_presses["h"] = [
            lambda self, e: self.display_help(),
            "Cycle through the help pages.",
        ]

        self.key_presses["p"] = [
            lambda self, e: self.save(),
            "Save an image of the current window.",
        ]

        self.key_presses["P"] = [
            lambda self, e: self.parent.save_figs(),
            "Save images all the open windows.",
        ]

        self.key_presses["q"] = [
            None,  # Documenting mpl default action
            "Close the current window.",
        ]

        self.key_presses["Q"] = [
            lambda self, e: self.parent.close_figs(all_figs=True),
            "Exit topplot.",
        ]

        self.key_presses["s"] = [
            None,  # Documenting mpl default action
            "Save an image of the current window to a selectable location.",
        ]

        self.key_presses["t"] = [
            lambda self, e: self.toggle_axes(e.inaxes).fig.canvas.draw(),
            "Cycle through mem/cpu/both axis visibility for POI graph. [#1]",
        ]

        if self.parent.mplcursors_present:
            self.key_presses["v"] = [
                None,  # Documenting mplcursors default action
                "Toggle annotations' visibility. [mplcursors feature]",
            ]

        self.key_presses["0"] = [
            lambda self, e: self.parent.graph_overview(use_progress_window=True),
            "Display the overview graphs.",
        ]

        for n in range(4):

            title, _, subtitle = self.parent.ordinal_to_title(n).partition("\n")

            self.key_presses[f"{str(n+1)}"] = [
                lambda self, e: self.parent.graph_by_overview_ordinal(
                    int(e.key) - 1,
                    use_progress_window=True,
                ),
                f"Display the '{title}' graph in a separate window.",
            ]

        self.key_presses["escape"] = [
            lambda self, e: self.clear_message(),
            "Clear any displayed message.",
        ]

    # -------------------------------------------------------------------------
    # Retrieve ax's name from the map

    def ax_name(self, ax):
        return self.ax_name_map[ax] if ax in self.ax_name_map else "<unknown ax>"

    # -------------------------------------------------------------------------
    # Graphs need to be set up post-init to short circuit initialization cycles

    def setup_graphing(self, setupfn):
        if setupfn is not None:
            setupfn(self)

        plt.setp(
            [a.get_xticklabels() for a in self.fig.axes[:]],
            visible=True,
            rotation=15,
            ha="right",
        )
        self.fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
        self.fig.show()

    # -------------------------------------------------------------------------
    # Given an axis and a specific legend (or set of legend lines), map the
    # legend lines to the axis' lines

    def map_legend_lines(
        self,
        ax,
        legend_title_label,
        legend=None,
        *,
        leglines=None,
        legtexts=None,
        leghandles=None,
    ):
        if legend is not None or leglines is not None:

            handles = None

            if legend is not None:
                leglines = legend.get_lines()
                if legtexts is None:
                    legtexts = legend.get_texts()
                handles = legend.legendHandles

            elif leghandles is not None:
                handles = leghandles

            titlelines = []
            titleleglines = []

            for (i, line) in enumerate(ax.get_lines()):
                if i >= len(leglines):
                    break
                legline = leglines[i]
                legtext = legtexts[i] if legtexts is not None else None

                if legline in self.leglines:
                    print(f"CLASH: legline {legline} already present")

                self.leglines[legline] = line
                legline.set_picker(5)

                if legtext is not None:
                    self.leglines[legtext] = line
                    legtext.set_picker(10)
                    self.legtexts[legline] = legtext
                    self.legtexts[legtext] = legline

                if handles is not None:
                    # pylint: disable=protected-access
                    self.legmarkers[legline] = handles[i]

                titleleglines.append(legline)
                titlelines.append(line)

            if legend_title_label in self.legtitles:
                self.legtitles[legend_title_label]["lines"] += titlelines
                self.legtitles[legend_title_label]["leglines"] += titleleglines
            else:
                self.legtitles[legend_title_label] = {
                    "leglines": titleleglines,
                    "lines": titlelines,
                }
                legend_title_label.set_picker(10)

        else:
            # raise Exception("Must have one of legend or leglines")
            print("Must have one of legend or leglines")

    # -------------------------------------------------------------------------
    # Display a message box. Optionally set a minimum (!) display period.

    def display_msg(self, txt, timeout=None):
        if self.msg_timer is not None:
            self.msg_timer.cancel()
            self.msg_timer = None

        txt += "\n\n[press Esc to clear this message]"

        if self.msg_text_box is None:
            bbox_props = dict(boxstyle="round", pad=2, facecolor="wheat", alpha=0.95)

            props = dict(fontfamily="monospace", fontsize=14, ha="center")

            self.msg_text_box = self.fig.text(0.5, 0.5, txt, bbox=bbox_props, **props)

        else:
            self.msg_text_box._text = txt
            self.msg_text_box.set_visible(True)

        self.fig.canvas.draw()

        if timeout is not None:

            def clearup():
                self.msg_text_box.set_visible(False)

            self.msg_timer = Timer(timeout, clearup)
            self.msg_timer.start()

    # -------------------------------------------------------------------------
    # Tidy away any previously displayed message

    def clear_message(self):
        if self.msg_text_box is not None:
            self.msg_text_box.set_visible(False)

        self.showing_help = 0
        self.fig.canvas.draw()

    # -------------------------------------------------------------------------
    # Display info about using topplot. Mainly runtime keyboard options.

    def display_help(self):
        def get_text(page):
            txt = ""
            if page == 1:
                txt = "Key press menu:\n\n"
                for (key, array) in self.key_presses.items():
                    item_text = array[1]
                    if item_text is not None:
                        txt += f"    '{key}' : {item_text}\n\n"

                txt += "#1: If the mouse pointer is over a graph, this applies to just that graph;"
                txt += (
                    "    otherwise it applies to all the graphs in the active window."
                )

            elif page == 2:
                txt = """Graph legends:

    Click on a legend line to hide it on the graph.
    Click on it again to display the line on the graph once more.

    Click on a legend's title to toggle the display status of each of the lines.
    I.e. if they're hidden, display them, if they're displayed, hide them.

    Right click on a legend's title to reset all the lines to being displayed.

    Legends are draggable, but do not leave them entirely over a different graph.
    If this happens they lose all interactivity, including draggability!
"""

                if self.parent.mplcursors_present:
                    txt += """
Annotations:

    Clicking on plotted lines will display information at that position. Right
    click on the info to dispel it."""
            else:
                return None

            txt += f"""

Page {page}   Version: {self.parent.config.version}    """
            txt += "Copyright (c) 2019-2021 Jonathan Sambrook and Codethink Ltd."
            return txt

        # ----------------------------------------------------------------------

        if self.help_text_box is None:
            self.showing_help = 1
            bbox_props = dict(  # boxstyle='circle',
                pad=15, facecolor="white", alpha=0.975
            )

            props = dict(fontfamily="monospace", fontsize=10, ha="left")

            self.help_text_box = self.fig.text(
                0.015, 0.03, get_text(1), bbox=bbox_props, **props
            )
        else:
            next_page = self.showing_help + 1
            txt = get_text(next_page)
            if txt:
                self.showing_help = next_page
                if self.help_text_box is not None:
                    self.help_text_box.set_text(txt)
                    self.help_text_box.set_visible(True)

            else:
                self.showing_help = 0
                if self.help_text_box is not None:
                    self.help_text_box.set_visible(False)

        self.fig.canvas.draw()

    # -------------------------------------------------------------------------
    # Hook for keypresses

    def onkey(self, e):
        # print(f"you pressed: '{e.key}'   x:'{e.xdata}'   y:'{e.ydata}'     e: {e}")

        if self.showing_help and e.key != "q":
            self.help_text_box.set_visible(False)
            self.fig.canvas.draw()

        if e.key in self.key_presses and self.key_presses[e.key][0] is not None:
            self.key_presses[e.key][0](self, e)

    # -------------------------------------------------------------------------
    # Hook for mouse clicks

    def onclick(self, e):  # pylint: disable=no-self-use
        # print(
        #     "%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f"
        #     % (
        #         "double" if e.dblclick else "single",
        #         e.button,
        #         e.x,
        #         e.y,
        #         e.xdata,
        #         e.ydata,
        #     )
        # )
        if e.inaxes is not None:
            print(f"Click in axis: '{e.inaxes.get_title()}'")

    # -------------------------------------------------------------------------
    # Hook for window closing

    def onclose(self, _):
        if self.name in self.parent.fig_manager:
            del self.parent.fig_manager[self.name]
        self.parent.close_check()

    # -------------------------------------------------------------------------
    # Hook for motion
    # This is intended to resolve occasional flickering issues without too much
    # overhead. Flicker observed on Linux. Seems likely TkInter related.

    onmove_counter = 0

    def onmove(self, _):
        self.onmove_counter += 1
        if self.onmove_counter % 100 == 0:
            self.fig.canvas.draw_idle()

    # -------------------------------------------------------------------------
    # Hook for artist picking

    def onpick(self, e):
        if isinstance(e.artist, mpl.legend.Legend):
            # Not sure how/why these occur, but we're not interested
            return

        if self.share_legends_regex:
            if e.artist in self.legtitles:
                self.shared_legend_title_pick(e)
            else:
                self.shared_legend_line_pick(e)
        else:
            if e.artist in self.legtitles:
                self.on_legend_title_pick(e)
            elif e.artist in self.legotm:
                self.on_otm_legend_line_pick(e)
            elif e.artist in self.legotmtitles:
                self.on_otm_legend_title_pick(e)
            else:
                self.on_legend_line_pick(e)

    # -------------------------------------------------------------------------
    # "Print" this fig to a file

    def save(self):
        directory = self.parent.config.output_dir
        directory = (
            ""
            if directory is None
            else f"{directory}{os.sep}"
            if directory[-1] != os.sep
            else directory
        )

        sep = "\\\\" if os.sep == "\\" else os.sep
        pattern = f"[^0-9a-zA-Z{'' if directory else sep}]+"

        title = self.title.partition("\n")[0]
        title = re.sub(pattern, "_", title)
        title = title.partition("topplot_")[2]

        filename = f"{directory}{title}.png"
        self.fig.savefig(filename)

    # -------------------------------------------------------------------------
    # Set alpha for line, marker, and text label
    # Handles either the line being clicked or the text label since self.legtexts
    # map is bi-directional

    def set_legline_alpha(self, legline, alpha):
        legline.set_alpha(alpha)

        if legline in self.legtexts:
            self.legtexts[legline].set_alpha(alpha)

        if legline in self.legmarkers:
            self.legmarkers[legline].set_alpha(alpha)

        elif self.legtexts[legline] in self.legmarkers:
            self.legmarkers[self.legtexts[legline]].set_alpha(alpha)

    # -------------------------------------------------------------------------
    # Hook for legend title clicks

    def on_legend_title_pick(self, e1, *, redraw=True):
        # on the pick event, find the orig line corresponding to the
        # legend proxy line, and toggle the visibility
        pickee = e1.artist

        rmb = e1.mouseevent.button == mpl.backend_bases.MouseButton.RIGHT
        shift = e1.mouseevent.key == "shift"

        for (i, line) in enumerate(self.legtitles[pickee]["lines"]):
            if rmb or shift:
                legvis = True
            else:
                legvis = not line.get_visible()

            line.set_visible(legvis)

            # Change the alpha on the line in the legend so we can see which lines
            # have been toggled
            legline = self.legtitles[pickee]["leglines"][i]
            self.set_legline_alpha(legline, 1.0 if legvis else 0.2)

        if redraw:
            self.fig.canvas.draw_idle()

    # -------------------------------------------------------------------------
    # Hook for legend title clicks with shared legends
    # Note that this doesn't distinguish between legends. Any line in any legend
    # may match.

    def shared_legend_title_pick(self, e1):
        text = e1.artist._text
        for legend_title in self.legtitles:
            if legend_title._text == text:
                e2 = DummyEvent(legend_title, e1.mouseevent)
                self.on_legend_title_pick(e2, redraw=False)

        self.fig.canvas.draw_idle()

    # -------------------------------------------------------------------------
    # Hook for legend line clicks

    def on_legend_line_pick(self, e1, *, redraw=True):
        # on the pick event, find the orig line corresponding to the
        # legend proxy line, and toggle the visibility
        legline = e1.artist

        rmb = e1.mouseevent.button == mpl.backend_bases.MouseButton.RIGHT
        shift = e1.mouseevent.key == "shift"
        force_visible = rmb or shift

        if legline in self.leglines:
            origline = self.leglines[legline]
            vis = True if force_visible else not origline.get_visible()
            origline.set_visible(vis)

            # Change the alpha on the line in the legend so we can see what lines
            # have been toggled
            self.set_legline_alpha(legline, 1.0 if vis else 0.2)

            if redraw:
                self.fig.canvas.draw_idle()

    # -------------------------------------------------------------------------
    # Hook for legend line clicks with shared legends

    def shared_legend_line_pick(self, e1, *, redraw=True):
        # Sort out legline and label : either could've been clicked to get here
        # and we need the label to "click" all the peers in the shared legends.
        if isinstance(e1.artist, mpl.lines.Line2D):
            legline = e1.artist
            label = self.legtexts[legline]
        else:
            label = e1.artist
            legline = self.legtexts[label]

        label_text = label._text

        # Use regex because the label might need picking apart to extract
        # partial content for comparison.
        re_category = re.compile(self.share_legends_regex)

        m = re_category.match(label_text)
        category = m.group(1)

        for line, text in self.legtexts.items():
            m = re_category.match(text._label)
            if m and m.group(1) == category:
                e2 = DummyEvent(line, e1.mouseevent)
                self.on_legend_line_pick(e2, redraw=False)

        if redraw:
            self.fig.canvas.draw_idle()

    # -------------------------------------------------------------------------
    # Hook for otm legend line clicks
    # Work actually done by the "real" legend's members.

    def on_otm_legend_line_pick(self, e1, *, redraw=True):
        if isinstance(e1.artist, mpl.lines.Line2D):
            legline = e1.artist
            label = self.legotmtexts[legline]
        else:
            label = e1.artist
            legline = self.legotmtexts[label]

        rmb = e1.mouseevent.button == mpl.backend_bases.MouseButton.RIGHT
        shift = e1.mouseevent.key == "shift"
        force_visible = rmb or shift

        # De-reference the legend's element to the "real" legend's lines
        for otmlegline in self.legotm[legline]:
            e2 = DummyEvent(otmlegline, e1.mouseevent)
            self.on_legend_line_pick(e2, redraw=False)

        # Toggle the otm legend line and label
        if force_visible:
            alpha = 999
        else:
            alpha = legline.get_alpha()

        # alpha is None (implying 1.0) if it's not already been explicitly set
        alpha = 0.2 if (alpha is None or alpha == 1.0) else 1.0

        legline.set_alpha(alpha)
        label.set_alpha(alpha)

        if redraw:
            self.fig.canvas.draw_idle()

    # -------------------------------------------------------------------------
    # Hook for otm legend title clicks

    def on_otm_legend_title_pick(self, e1):
        otm_title = e1.artist

        for otm_legline in self.legotmtitles[otm_title]:
            e2 = DummyEvent(otm_legline, e1.mouseevent)
            self.on_otm_legend_line_pick(e2, redraw=False)

        self.fig.canvas.draw_idle()

    # -------------------------------------------------------------------------
    # Get the window to the top of the z-order

    def show(self):
        manager = self.fig.canvas.manager

        # Tkinter specific code follows. If you change GUI toolkit (e.g. to
        # QT), this will break.
        window = manager.window

        # .lift() and .tkraise() should but don't work. The following is ugly but does.
        window.attributes("-topmost", 1)

        if not sys.platform.startswith("win"):
            # Necessary on my Linux WM, but not on Windows
            window.withdraw()
            window.deiconify()

        window.update_idletasks()

        window.attributes("-topmost", 0)

    # -------------------------------------------------------------------------
    # Close the window

    def close(self):
        plt.close(self.fig)

        # Tidy up
        self.onclose(None)

    # -------------------------------------------------------------------------
    # Short cut to return the wrapped Fig's axes

    def get_axes(self):
        return self.fig.get_axes()

    # -------------------------------------------------------------------------
    # Track legend by axis and name

    def register_legend(self, ax, name, legend):
        if ax not in self.legends:
            self.legends[ax] = {}
        if name not in self.legends[ax]:
            self.legends[ax][name] = {}
        self.legends[ax][name]["legend"] = legend

    # -------------------------------------------------------------------------
    # Retrieve the legend of the given name if it has been registered with the given axis.

    def named_legend(self, ax, name):
        if ax in self.legends and name in self.legends[ax]:
            return self.legends[ax][name]["legend"]
        return None

    # -------------------------------------------------------------------------
    # Retrieve the Legends of the given axis, and its pair, if one's been
    # given; otherwise return Legends
    # from all of the Fig's axes

    def get_legends(self, ax=None):
        if ax is None:
            axes = self.get_axes()
        else:
            axes = [ax]
            if ax in self.ax_pairs:
                axes.append(self.ax_pairs[ax])

        legends = []
        for ax in axes:
            for c in ax.get_children():
                if isinstance(c, mpl.legend.Legend):
                    legends.append(c)

        return legends

    # -------------------------------------------------------------------------
    # Toggle the visibility of the Legends associated with an axis and any pair it has

    def toggle_legends(self, ax=None):
        if ax is None:
            legends = self.get_legends()
        else:
            legends = self.get_legends(ax)

        visibility = False

        for legend in legends:
            visibility = legend.get_visible()
            if visibility:
                break

        for legend in legends:
            legend.set_visible(not visibility)

        self.fig.canvas.draw()

    # -------------------------------------------------------------------------
    # Cycle through one, then t'other, then back to both of the axes being visible.

    def toggle_axes(self, ax):
        if ax is None:
            axes = []
            for ax1 in self.ax_pairs:
                if self.ax_pairs[ax1] not in axes:
                    axes.append(ax1)

        else:
            axes = [self.ax_pairs.primary(ax) if ax in self.ax_pairs else ax]

        for ax1 in axes:
            if ax1 in self.ax_pairs:
                ax2 = self.ax_pairs[ax1]

                # print(f"ax1: {hex(id(ax1))}  ax2: {hex(id(ax2))}")

                # If an axis has the other axis' legend attached to it for
                # z-order reasons, this is the way to get hold of it.
                cuckoo = self.named_legend(ax1, "cuckoo")
                if cuckoo is None:
                    cuckoo = self.named_legend(ax2, "cuckoo")

                v1 = ax1.get_visible()
                v2 = ax2.get_visible()
                # print(f"v1: {v1}  v2: {v2}")
                if v1 and v2:
                    # print(f"ax2/{self.ax_name(ax2)} only")
                    ax1.set_visible(False)

                    if cuckoo is not None:
                        # Transfer cuckoo between axes
                        cuckoo.remove()
                        ax2.add_artist(cuckoo)

                    legend2 = ax2.get_legend()
                    if legend2 is not None and not legend2.get_visible():
                        legend2.set_visible(True)
                        self.toggle_axes_legend_state[ax2] = legend2

                elif (not v1) and v2:
                    # print(f"ax1/{self.ax_name(ax1)} only")
                    ax1.set_visible(True)
                    ax2.set_visible(False)

                    # twinx sets the secondary axis's labels, ticks, grid and
                    # background patch to invisible
                    ax1.patch.set_visible(True)
                    ax1.get_xaxis().set_visible(True)  # Covers labels, ticks and grid

                    if cuckoo is not None and cuckoo.get_visible():
                        cuckoo.remove()
                        ax1.add_artist(cuckoo)
                        cuckoo.set_visible(False)
                        self.toggle_axes_legend_state[ax1] = cuckoo

                    if ax2 in self.toggle_axes_legend_state:
                        self.toggle_axes_legend_state[ax2].set_visible(False)
                        del self.toggle_axes_legend_state[ax2]

                else:
                    # print("both axen")
                    ax2.set_visible(True)

                    # twinx sets the secondary axis's labels, ticks, grid and
                    # background patch to invisible
                    ax1.patch.set_visible(False)
                    ax1.get_xaxis().set_visible(False)  # Covers labels, ticks and grid

                    if cuckoo is not None:
                        cuckoo.set_visible(True)

                    if ax1 in self.toggle_axes_legend_state:
                        self.toggle_axes_legend_state[ax1].set_visible(True)
                        del self.toggle_axes_legend_state[ax1]

        return self


# -----------------------------------------------------------------------------
# vi: sw=4:ts=4:et
