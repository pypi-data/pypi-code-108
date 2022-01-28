import math

import matplotlib.pyplot as plt

from ..figman import FigManager

# -------------------------------------------------------------------------


def style_lines(self, *axes):
    """Apply the relevant style to the lines on the given axis/axes."""
    for ax in axes:
        prefix = ""
        label = ax.get_yaxis().get_label().get_text()
        if label is not None:
            prefix = label
        for line in ax.get_lines():
            self.linestyler.style(prefix + line.get_label(), line)

# -------------------------------------------------------------------------


def graph_poi(
    self,
    figman,
    df,
    ax,
    title,
    *,
    x_bounds=None,
    mem_bounds=None,
    single_core=None,
    overview: bool = False,  # pylint: disable=unused-argument
):
    """Draw the graph of Processes of Interest (POI) using the given DataFrame."""
    max_cpu = 100
    max_mem = None

    # Convenience aliasing
    plot_cpu_lines = self.config.plot_poi_cpu_lines
    plot_cpu_sum = self.config.plot_poi_cpu_sum
    plot_mem_lines = self.config.plot_poi_mem_lines
    plot_mem_sum = self.config.plot_poi_mem_sum

    if (plot_mem_lines or plot_mem_sum) and self.config.include_process_mem:
        ax_cpu = ax.twinx()
        ax_mem = ax
    else:
        ax_cpu = ax
        ax_mem = ax.twinx()

    figman.ax_name_map[ax_cpu] = "ax_cpu"
    figman.ax_name_map[ax_mem] = "ax_mem"

    if (
        (plot_cpu_lines or plot_cpu_sum)
        and self.config.include_process_cpu
        and (plot_mem_lines or plot_cpu_sum)
        and self.config.include_process_mem
    ):
        figman.ax_pairs.append(ax_cpu, ax_mem)

    # ---------------------------------------------------------------------

    def style_line(
        ax, index, colour, alpha, linestyle, marker=None, mark_every=None
    ):
        line = ax.get_lines()[index]
        line.set_color(colour)
        line.set_alpha(alpha)
        line.set_linestyle(linestyle)
        if marker is None:
            marker = ""
        line.set_marker(marker)
        if mark_every is None:
            mark_every = 10
        line.set_markevery(mark_every)

    # ---------------------------------------------------------------------

    def max_cpu_fu(column_name):
        max_cpu = df[column_name].max()
        if max_cpu > 100:
            max_cpu = 100 * math.ceil((max_cpu + 0.1) / 100.0)
        else:
            max_cpu = 110
        return max_cpu

    # ---------------------------------------------------------------------

    def max_mem_fu(column_name):
        max_mem = df[column_name].max()
        return 10 * math.ceil((max_mem + 0.1) / 10.0)

    # ---------------------------------------------------------------------

    def handle_data(
        df,
        ax,
        separate_cores,
        plot_data_lines,
        plot_summary,
        plot_at_all,
        mode,
        summary_line_style,
        max_fu,
        max_fu_default,
        x_bounds,
    ):
        plotted = False
        if (plot_data_lines or plot_summary) and plot_at_all:
            summary_title = f"poi {mode} sum - {mode}"
            if plot_summary and not separate_cores:
                # Create summary column if not already present
                if summary_title not in df.columns.to_list():
                    summary = self.data.poi_df.filter(regex=f" - {mode}$").sum(
                        axis=1
                    )
                    df.insert(0, summary_title, summary)

            # Select columns by regex
            if not plot_data_lines:
                regex = f"^{summary_title}$"
            else:
                regex = f"- {mode}$"

            # Strip trailing category from names then plot
            def stripper(x):
                return x[:-6] if x[-6:] == f" - {mode}" else x

            df = df.filter(regex=regex)
            if not df.empty:
                df.rename(columns=stripper).plot(ax=ax, xlim=x_bounds)
                plotted = True
            ax.set_ylabel(f"{mode} (%)")
            style_lines(self, ax)

            # Override summary line
            if plot_summary and not separate_cores:
                colour, alpha, linestyle, marker, mark_every = summary_line_style
                style_line(ax, 0, colour, alpha, linestyle, marker, mark_every)
                return (plotted, max_fu(summary_title))

        return (plotted, max_fu_default)

    # ---------------------------------------------------------------------

    total_markers = 7.5
    mark_every = int(len(df) / total_markers)
    alpha = 0.33
    cpu_summary_line_style = (
        "mediumvioletred",
        alpha,
        (1, (1, 2, 1, 3)),
        "$c$",
        mark_every,
    )
    mem_summary_line_style = (
        "dodgerblue",
        alpha,
        (0, (2, 6, 2, 2)),
        "$m$",
        mark_every,
    )

    cpu_plotted, max_cpu = handle_data(
        df,
        ax_cpu,
        x_bounds is not None,
        plot_cpu_lines,
        plot_cpu_sum,
        self.config.include_process_cpu,
        "cpu",
        cpu_summary_line_style,
        max_cpu_fu,
        100 if single_core else 110,
        x_bounds,
    )

    mem_plotted, max_mem = handle_data(  # pylint: disable=unused-variable
        df,
        ax_mem,
        x_bounds is not None,
        plot_mem_lines,
        plot_mem_sum,
        self.config.include_process_mem,
        "mem",
        mem_summary_line_style,
        max_mem_fu,
        None,
        x_bounds,
    )

    # Handle legends
    l_mem_cuckoo = None

    # Handle mem
    if (plot_mem_lines or plot_mem_sum) and self.config.include_process_mem:
        # ax_mem's legend shouldn't be overwritten by lines on ax_cpu
        # Sadly they are being overwritten, so ensure they're not by adding
        # them to ax_cpu
        if (
            (plot_cpu_lines or plot_cpu_sum)
            and self.config.include_process_cpu
            and cpu_plotted
        ):
            handles, labels = ax_mem.get_legend_handles_labels()
            # Remove old legend's artists from drawing tree to avoid
            # bitching about artist reuse
            # Note: doesn't delete legend object
            old_l_mem = ax_mem.legend()
            old_l_mem.remove()
            l_mem_cuckoo = plt.legend(
                handles, labels, loc="upper left", title="mem"
            )

        else:
            ax_mem.legend(loc="upper left", title="mem")
            ax_cpu.set_visible(False)

            l_mem = ax_mem.get_legend()
            # WARNING: accessing internal mpl details here
            label = (
                l_mem._legend_title_box._text  # pylint: disable=protected-access
            )
            figman.map_legend_lines(ax_mem, label, l_mem)
            l_mem.set_draggable(True)
            ax_mem.xaxis.set_visible(True)
            ax_mem.patch.set_visible(True)

    # Handle cpu
    if (plot_cpu_lines or plot_cpu_sum) and self.config.include_process_cpu:
        l_cpu = ax_cpu.legend(loc="upper right", title="cpu")
        # WARNING: accessing internal mpl details here
        label = l_cpu._legend_title_box._text  # pylint: disable=protected-access
        figman.map_legend_lines(ax_cpu, label, l_cpu)
        l_cpu.set_draggable(True)

        if (
            not plot_mem_lines and not plot_mem_sum
        ) or not self.config.include_process_mem:
            ax_mem.set_visible(False)

    if l_mem_cuckoo is not None:
        ax_cpu.add_artist(l_mem_cuckoo)
        figman.register_legend(ax_cpu, "cuckoo", l_mem_cuckoo)
        # WARNING: accessing internal mpl details here
        label = (
            l_mem_cuckoo._legend_title_box._text  # pylint: disable=protected-access
        )
        figman.map_legend_lines(ax_mem, label, l_mem_cuckoo)
        l_mem_cuckoo.set_draggable(True)

    # Handle furniture
    ax_cpu.set_title(title)
    ax_mem.set_title(title)

    self.common_ax1(figman, ax_mem)
    self.common_ax2(figman, ax_cpu)

    if x_bounds is None:
        x_bounds = (df.head(1).index[0], df.tail(1).index[0])
    ax_cpu.set_xlim(x_bounds)

    ax_cpu.set_ybound(lower=0, upper=max_cpu)

    if mem_bounds is not None:
        min_mem, max_mem = mem_bounds
        ax_mem.set_ybound(lower=min_mem, upper=max_mem)
    elif max_mem is not None:
        ax_mem.set_ybound(lower=0, upper=max_mem)

# -------------------------------------------------------------------------


def graph_poi_per_cpu(self, use_progress_window: bool = False):
    """Draw the Processes of Interest in separate plots for each CPU core."""
    figman_name = "poi_by_cpu"
    title = "poi by cpu core"

    # Find the nearest integer square that will fit the plots
    sqrt = math.ceil(math.sqrt(int(self.config.cores)))

    # Account for this possibly being a row larger than needed
    excess_rows = 0
    if (sqrt * sqrt) > (self.config.cores + sqrt - 1):
        excess_rows = 1

    def setup(figman):
        min_timestamp = self.data.poi_df.head(1).index[0]
        max_timestamp = self.data.poi_df.tail(1).index[0]

        max_mem = 0
        for core in range(self.config.cores):
            max_mem = max(
                max_mem,
                self.data.core_dfs[core].filter(regex=" - mem$").max().max(),
            )

        for core in range(self.config.cores):
            if self.config.cores < 3:
                ax = figman.plots[core]
            else:
                x = int(core / sqrt)
                y = core % sqrt
                ax = figman.plots[x][y]
            self.graph_poi(
                figman,
                self.data.core_dfs[core],
                ax,
                f"core {core}",
                x_bounds=(min_timestamp, max_timestamp),
                mem_bounds=(0, max_mem),
                single_core=core,
            )

    def generate_figman():
        return FigManager(
            figman_name,
            self,
            self.title(f"{title}\n{self.config.poi_categories}"),
            self.window_size,
            sqrt - excess_rows,
            sqrt,
            subtitle=True,
            share_legends_regex="^(.*)$"
        )

    self.dispense_graph(
        title.partition("\n")[0],
        figman_name,
        setup,
        generate_figman,
        use_progress_window,
    )

# -------------------------------------------------------------------------
