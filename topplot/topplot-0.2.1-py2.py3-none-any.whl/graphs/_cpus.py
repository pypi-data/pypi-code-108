import math
from typing import Any, Dict, List, Tuple
from ..figman import FigManager

# -------------------------------------------------------------------------


def generate_markeveries(
    row_count: int, col_count: int, total_markers: int
) -> List[Tuple[int, int]]:
    """Generate a list of (offset, markevery) tuples for a dataset of the given dimensions.

    Makes an attempt to avoid clustering markers on different lines.

    Args:
        row_count (int): How many rows in the dataset.
        col_count (int): How many columns in the dataset.
        total_markers (int): How many markers are required for each line.

    Returns:
        list: The generated (offset, markevery) tuples.
    """
    markeveries = []

    # Calculate offsets for markers so that they don't cluster
    clustering = True

    markevery = int(row_count / total_markers)

    # Loop if offsets are (still) clustered and another attempt makes sense
    while clustering and total_markers >= 1:
        offset_prev = None
        for col in range(col_count):
            offset = int(markevery / col_count) * col
            if offset_prev is not None and offset_prev != offset:
                clustering = False
            offset_prev = offset
            markeveries.append((offset, markevery))
        total_markers -= 1

    return markeveries

# -------------------------------------------------------------------------


def graph_cpus(
    self,
    figman,
    df,
    ax_in,
    title,
    *,
    x_bounds=None,
    force_single_core: bool = None,
    overview: bool = False,
):
    """Draw the load average and CPU graph.

    Forcing a single cpu core isn't the same as there being no multicore data.

    Forcing a single core displays the core's index in labels, and removes the
    load average display since that's not relevant to a single core out of
    multiple cores.
    """
    ax_loadavg = None

    if force_single_core is None:
        ax_loadavg = ax_in
        ax_cpu = ax_loadavg.twinx()
        legend_title = "load and cpu"
    else:
        ax_cpu = ax_in
        legend_title = "cpu"

    if force_single_core is None:
        df.plot(
            y="load average",
            color=self.colours["load average"],
            ax=ax_loadavg,
            lw=3,
        )

    measures = ["user", "system", "nice", "idle", "wait", "hw irq", "sw irq"]

    if self.config.with_cpu_steal:
        measures.append("steal")

    core_test = 0 if force_single_core is None else force_single_core
    colname_test = f"cpu{core_test} exec" if self.config.has_cpu_rows else "cpu exec"
    if colname_test in df.columns:
        measures = ["exec"] + measures

    if self.config.has_cpu_rows or force_single_core is not None:
        # never display line markers for overview, and only if ordered to otherwise
        display_cpu_markers = False if overview else self.config.display_cpu_markers

        if display_cpu_markers:
            # To put text markers on each line has two cost implications
            #  i) df.plot() doesn't handle lists of markers/markeveries, so
            #     you need a two level loop and (cores * len(measures)) calls
            #     to df.plot()
            # ii) the markers trigger mathstext font related calls.
            #     Informative result, but slow.

            markeveries = self.generate_markeveries(len(df), self.config.cores, 10)

            for core in (
                range(0, self.config.cores)
                if force_single_core is None
                else [force_single_core]
            ):
                for measure in measures:
                    extra_args : Dict[str, Any] = {}
                    if force_single_core is None:
                        # The dollar symbols trigger lots of calling of
                        # expensive mathtext font functions
                        extra_args["marker"] = f"${core}$"
                        extra_args["markevery"] = markeveries[core]
                        extra_args["markersize"] = 8

                    df.plot(
                        y=f"cpu{core} {measure}",
                        color=self.colours[measure],
                        ax=ax_cpu,
                        **extra_args,
                    )
        else:  # This is the fast-but-no-markers version
            labels = []
            colours = []

            for measure in measures:
                for core in (
                    range(0, self.config.cores)
                    if force_single_core is None
                    else [force_single_core]
                ):
                    labels.append(f"cpu{core} {measure}")
                    colours.append(self.colours[measure])

            df.plot(
                y=labels,
                color=colours,
                ax=ax_cpu,
            )
    else:  # Single core (forced or natural)
        labels = []
        colours = []

        for measure in measures:
            labels.append(f"cpu {measure}")
            colours.append(self.colours[measure])

        df.plot(
            y=labels,
            color=colours,
            ax=ax_cpu,
        )

    # Legend(s)
    if ax_loadavg and ax_cpu:
        combined_legend = self.combined_legend(
            figman,
            title,
            legend_title,
            "loadavg",
            "cpu (%)",
            ax_loadavg,
            ax_cpu,
            location="upper left",
        )  # , cap2=len(measures))

        self.otm_legend(
            figman,
            "loadavg and\ngrouped cpu" if self.config.has_cpu_rows else "loadavg and cpu",
            # strip any leading "cpu0 ", "cpu1 ", ..
            r"^(?:cpu\d+ )?(.+)",
            ax_cpu,
            combined_legend,
            copy_markers=False,
        )

        if not (force_single_core is None and self.config.cores > 1) or overview:
            combined_legend.remove()
    else:
        self.single_legend(figman, title, legend_title, "cpu (%)", ax_cpu)

    # Axes fettling
    if force_single_core is None and ax_loadavg:
        ax_loadavg.tick_params("x", which="minor", bottom=False)
        self.common_ax1(figman, ax_loadavg)
        ax_loadavg.set_ybound(lower=0, upper=df["load average"].max() * 105.0 / 100)

    if x_bounds is not None:
        min_timestamp, max_timestamp = x_bounds
        ax_cpu.set_xbound(lower=min_timestamp, upper=max_timestamp)

    self.common_ax2(figman, ax_cpu)
    ax_cpu.set_ybound(lower=0, upper=100)

# -------------------------------------------------------------------------


def graph_cpu_per_cpu(self, use_progress_window: bool = False):
    """Draw the cpu data in separate plots for each CPU core."""
    figman_name = "cpu_by_cpu"
    title = "cpu data by cpu core"

    # Find the nearest integer square that will fit the plots
    sqrt = math.ceil(math.sqrt(int(self.config.cores)))

    # Account for this possibly being a row larger than needed
    excess_rows = 0
    if (sqrt * sqrt) > (self.config.cores + sqrt - 1):
        excess_rows = 1

    def setup(figman):
        min_timestamp = self.data.poi_df.head(1).index[0]
        max_timestamp = self.data.poi_df.tail(1).index[0]

        for core in range(self.config.cores):
            if self.config.cores < 3:
                ax = figman.plots[core]
            else:
                x = int(core / sqrt)
                y = core % sqrt

                ax = figman.plots[x][y]
            df = self.data.cpus_df.filter(regex=f"^cpu{core}")

            self.graph_cpus(
                figman,
                df,
                ax,
                f"core {core}",
                x_bounds=(min_timestamp, max_timestamp),
                force_single_core=core,
            )

    def generate_figman():
        return FigManager(
            figman_name,
            self,
            self.title(title),
            self.window_size,
            sqrt - excess_rows,
            sqrt,
            share_legends_regex=r"^cpu\d+ (.*)$"
        )

    self.dispense_graph(
        title.partition("\n")[0],
        figman_name,
        setup,
        generate_figman,
        use_progress_window,
    )

# -------------------------------------------------------------------------
