from datetime import timedelta

from typing import List

import numpy as np

from rich.align import Align
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn


def make_start_layout() -> Layout:
    """Define the layout for the starting screen."""
    layout = Layout(name="root")

    layout.split(
        Layout(name="header", ratio=4),
        Layout(name="main", ratio=3),
    )
    layout["main"].split_row(
        Layout(name="side"),
        Layout(name="body", ratio=2, minimum_size=60),
    )
    return layout


def make_race_layout() -> Layout:
    """Defines the layout of the race tracking screen."""
    layout = Layout(name="root")
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="progress", size=3)
    )
    layout["main"].split_row(
        Layout(name="plotext", ratio=7),
        Layout(name="current_race", ratio=4),
        Layout(name="best_results", ratio=3)
    )
    layout["header"].update(Panel("", border_style="navy_blue"))

    return layout


def create_lap_time_table(names: List[str], times: np.array, top_3_times: np.array) -> Panel:
    """Creates a table which shows the progress of the current races. It has 4 columns. 2 groups of two, with the lap
    times of an athlete and the difference with the current best time.

    :param List[str] names: List of strings with the names of the athletes.
    :param np.array times: Numpy array with the times so far.
    :param np.array top_3_times: Numpy array with the best times so far
    :return rich.Panel: Returns a rich.Panel with the table in it
    """
    table_lap_times = Table(
        title="Lap time progression",
        show_footer=True,
    )

    total_times = times.sum(axis=1)
    table_lap_times.add_column(
        names[0],
        justify="center",
        no_wrap=True,
        min_width=10,
        header_style="red",
        style="red",
        footer=f"{str(timedelta(seconds=total_times[0]))[2:10]}"
    )
    table_lap_times.add_column("Best diff", justify="center", no_wrap=True, min_width=10)
    table_lap_times.add_column(
        names[1],
        justify="center",
        no_wrap=True,
        min_width=10,
        header_style="blue",
        style="blue",
        footer=f"{str(timedelta(seconds=total_times[1]))[2:10]}"
    )
    table_lap_times.add_column("Best diff", justify="center", no_wrap=True, min_width=10)

    best_lap_times = top_3_times[0, :]
    diff = times - best_lap_times
    times = np.vstack((times, diff))

    colors = ("bright_red", "bright_cyan")

    for col in times.T:
        if col[0] == 0 and col[1] == 0:
            table_lap_times.add_row("NA", "NA", "NA", "NA")
        else:
            colors_race = (colors[1 - int(col[0] > col[1])], colors[int(col[0] > col[1])])
            color_diff_1 = colors[1 - int(col[2] > 0)]
            color_diff_2 = colors[1 - int(col[3] > 0)]
            item_1 = f"[{colors_race[0]}]{col[0]:.2f}"
            item_2 = f"[{color_diff_1}]{col[2]:.2f}" if col[2] < 0 else f"[{color_diff_1}]+{col[2]:.2f}"
            item_3 = f"[{colors_race[1]}]{col[1]:.2f}"
            item_4 = f"[{color_diff_2}]{col[3]:.2f}" if col[3] < 0 else f"[{color_diff_2}]+{col[3]:.2f}"
            table_lap_times.add_row(item_1, item_2, item_3, item_4)

    panel_lap_times = Panel(
        Align.center(table_lap_times, vertical="top"),
        border_style="bright_red"
    )

    return panel_lap_times


def create_best_table(names: List[str], times: np.array) -> Panel:
    """Creates the table with the top 3 best times so far.

    :param List[str] names: List of strings with the names of the best athletes so far.
    :param np.array times: Numpy array with the best times so far
    :return rich.Panel: Panel with the table showing the top 3 best results so far.
    """
    table_best = Table(
        title="Best times so far",
        show_footer=True)

    total_times = times.sum(axis=1)
    table_best.add_column(
        names[0],
        justify="center",
        no_wrap=True,
        min_width=10,
        style="gold3",
        header_style="gold3",
        footer=f"{str(timedelta(seconds=total_times[0]))[2:10]}"
    )
    table_best.add_column(
        names[1],
        justify="center",
        no_wrap=True,
        min_width=10,
        style="grey74",
        header_style="grey74",
        footer=f"{str(timedelta(seconds=total_times[1]))[2:10]}"
    )
    table_best.add_column(
        names[2],
        justify="center",
        no_wrap=True,
        min_width=10,
        style="orange4",
        header_style="orange4",
        footer=f"{str(timedelta(seconds=total_times[2]))[2:10]}"
    )
    for col in times.T:
        table_best.add_row(*col.astype(str))

    panel_best = Panel(
        Align.center(table_best, vertical="top"),
        border_style="dark_orange"
    )

    return panel_best


def create_progress_panel(nr_laps: int) -> Panel:
    """Creates a panel with the progress bar

    :param int nr_laps: integer indicating how many laps this race is going to take.
    :return rich.Panel: Panel with the progress bar
    """
    race_progress = Progress(
        "{task.description}",
        SpinnerColumn(),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%")
    )
    race_progress.add_task("[cyan]Progress", total=nr_laps)
    progress_panel = Panel(
        Align.center(race_progress, vertical="middle"),
        border_style="cyan"
    )
    return progress_panel

