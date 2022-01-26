#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
"""Classes for creating outputs."""
import typing as t
from enum import Enum
from glob import glob
from pathlib import Path

import attr
from matplotlib import pyplot as plt
from matplotlib.ticker import ScalarFormatter


@attr.s(auto_attribs=True, slots=True, frozen=True)
class PlotArguments:
    """TBW."""

    title: t.Optional[str] = None
    xscale: str = "linear"
    yscale: str = "linear"
    xlabel: t.Optional[str] = None
    ylabel: t.Optional[str] = None
    xlim: t.Tuple[t.Optional[float], t.Optional[float]] = (None, None)
    ylim: t.Tuple[t.Optional[float], t.Optional[float]] = (None, None)
    xticks: t.Any = None
    yticks: t.Any = None
    sci_x: bool = False
    sci_y: bool = False
    grid: bool = False
    axis: t.Any = None
    bins: t.Optional[int] = None  # TODO: This should not be here !

    @classmethod
    def from_dict(cls, dct: t.Mapping[str, t.Any]) -> "PlotArguments":
        """TBW."""
        return cls(**dct)

    def to_dict(self) -> t.Dict[str, t.Any]:
        """TBW."""
        return attr.asdict(self)


class PlotType(Enum):
    """TBW."""

    Histogram = "histogram"
    Graph = "graph"
    Scatter = "scatter"


def show_plots() -> None:
    """Close last empty canvas and show all the previously created figures."""
    plt.close()
    plt.show()


def update_plot(ax_args: dict, ax: plt.Axes) -> None:
    """TBW.

    Parameters
    ----------
    ax_args
    ax
    """
    ax.set_xlabel(ax_args["xlabel"])
    ax.set_ylabel(ax_args["ylabel"])

    ax.set_xscale(ax_args["xscale"])
    ax.set_yscale(ax_args["yscale"])

    ax.set_xlim(ax_args["xlim"][0], ax_args["xlim"][1])
    ax.set_ylim(ax_args["ylim"][0], ax_args["ylim"][1])

    ax.set_title(ax_args["title"])

    if ax_args["axis"]:
        # TODO: Fix this
        raise NotImplementedError
        # plt.axis(ax_args["axis"])

    if ax_args["xticks"]:
        ax.set_xticks(ax_args["xticks"])
    if ax_args["yticks"]:
        ax.set_yticks(ax_args["yticks"])

    # TODO: Enable this
    ax.grid(ax_args["grid"])

    if ax_args["sci_x"]:
        ax.xaxis.set_major_formatter(ScalarFormatter())
        ax.ticklabel_format(style="scientific", axis="x", scilimits=(0, 0))
    if ax_args["sci_y"]:
        ax.yaxis.set_major_formatter(ScalarFormatter())
        ax.ticklabel_format(style="scientific", axis="y", scilimits=(0, 0))


# TODO: Refactor this function
def update_fits_header(
    header: dict, key: t.Union[str, list, tuple], value: t.Any
) -> None:
    """TBW.

    Parameters
    ----------
    header
    key
    value
    """
    if isinstance(value, (str, int, float)):
        result = value  # type: t.Union[str, int, float]
    else:
        result = repr(value)

    if isinstance(result, str):
        result = result[0:24]

    if isinstance(key, (list, tuple)):
        key = "/".join(key)

    key = key.replace(".", "/")[0:36]
    header[key] = value


# TODO: Create unit tests
# TODO: Refactor this in 'def apply_run_number(folder, template_filename) -> Path
def apply_run_number(template_filename: Path) -> Path:
    """Convert the file name numeric placeholder to a unique number.

    :param template_filename:
    :return:
    """
    path_str = str(template_filename)
    if "?" in path_str:
        # TODO: Use method 'Path.glob'
        dir_list = sorted(glob(path_str))

        p_0 = path_str.find("?")
        p_1 = path_str.rfind("?")
        template = path_str[slice(p_0, p_1 + 1)]
        path_str = path_str.replace(template, "{:0%dd}" % len(template))

        last_num = 0
        if len(dir_list):
            path_last = dir_list[-1]
            last_num = int(path_last[slice(p_0, p_1 + 1)])
        last_num += 1
        path_str = path_str.format(last_num)

    return Path(path_str)


# TODO: the log file should directly write in 'output_dir'
def save_log_file(output_dir: Path) -> None:
    """Move log file to the outputs directory of the simulation."""
    log_file = Path("pyxel.log").resolve(strict=True)  # type: Path

    new_log_filename = output_dir.joinpath(log_file.name)
    log_file.rename(new_log_filename)
