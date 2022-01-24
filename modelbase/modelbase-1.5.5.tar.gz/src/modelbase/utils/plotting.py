from __future__ import annotations

__all__ = [
    "_get_plot_kwargs",
    "_style_subplot",
    "plot",
    "plot_grid",
    "relative_luminance",
    "get_norm",
    "heatmap_from_dataframe",
]

import itertools as it
import math
from typing import Any, Dict, Iterable, List, Optional, Sized, Tuple, Union, cast

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import pandas as pd
from matplotlib.collections import QuadMesh
from matplotlib.colors import colorConverter  # type: ignore
from matplotlib.colors import LogNorm, Normalize, SymLogNorm
from matplotlib.figure import Figure

from ..typing import Axes


def _get_plot_kwargs(
    figure_kwargs: Optional[Dict[str, Any]],
    subplot_kwargs: Optional[Dict[str, Any]],
    plot_kwargs: Optional[Dict[str, Any]],
    grid_kwargs: Optional[Dict[str, Any]],
    tick_kwargs: Optional[Dict[str, Any]],
    label_kwargs: Optional[Dict[str, Any]],
    title_kwargs: Optional[Dict[str, Any]],
    legend_kwargs: Optional[Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """Get default plot kwargs or overwrite them."""
    local_figure_kwargs = {"figsize": (10, 7)}
    local_subplot_kwargs = {"facecolor": "white"}
    local_plot_kwargs = {"linewidth": 4}
    local_grid_kwargs = {
        "color": (0, 0, 0),
        "alpha": 0.33,
        "linestyle": "dashed",
        "linewidth": 1,
    }
    local_tick_kwargs = {
        "direction": "out",
        "length": 6,
        "width": 2,
        "labelsize": 14,
        "color": "0.15",
        "pad": 7,
    }
    local_label_kwargs = {"fontsize": 14}
    local_title_kwargs = {"fontsize": 18}
    local_legend_kwargs = {
        "loc": "upper left",
        "bbox_to_anchor": (1.02, 1),
        "borderaxespad": 0,
        "ncol": 1,
        "fontsize": 12,
        "numpoints": 1,
        "scatterpoints": 1,
        "markerscale": 1,
        "frameon": False,
    }
    if figure_kwargs is not None:
        local_figure_kwargs.update(figure_kwargs)
    if subplot_kwargs is not None:
        local_subplot_kwargs.update(subplot_kwargs)
    if plot_kwargs is not None:
        local_plot_kwargs.update(plot_kwargs)
    if grid_kwargs is not None:
        local_grid_kwargs.update(grid_kwargs)
    if tick_kwargs is not None:
        local_tick_kwargs.update(tick_kwargs)
    if label_kwargs is not None:
        local_label_kwargs.update(label_kwargs)
    if title_kwargs is not None:
        local_title_kwargs.update(title_kwargs)
    if legend_kwargs is not None:
        local_legend_kwargs.update(legend_kwargs)
    return {
        "figure": local_figure_kwargs,
        "subplot": local_subplot_kwargs,
        "plot": local_plot_kwargs,
        "grid": local_grid_kwargs,
        "ticks": local_tick_kwargs,
        "label": local_label_kwargs,
        "title": local_title_kwargs,
        "legend": local_legend_kwargs,
    }


def _style_subplot(
    ax: plt.Axes,
    kwargs: dict,
    xlabel: str = None,
    ylabel: str = None,
    zlabel: str = None,
    title: str = None,
    legend: bool = False,
    grid: bool = None,
) -> None:
    """Set style of the subplot."""
    if grid:
        ax.grid(True, which="major", axis="both", **kwargs["grid"])
    if legend:
        ax.legend(**kwargs["legend"])
    if title is not None:
        ax.set_title(title, **kwargs["title"])
    if xlabel is not None:
        ax.set_xlabel(xlabel, **kwargs["label"])
    if ylabel is not None:
        ax.set_ylabel(ylabel, **kwargs["label"])
    if zlabel is not None:
        ax.set_zlabel(zlabel, **kwargs["label"])
    ax.tick_params(**kwargs["ticks"])
    for axis in ["top", "bottom", "left", "right"]:
        ax.spines[axis].set_linewidth(0)


def plot(
    plot_args: Iterable,
    legend: Optional[Iterable[str]] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    title: Optional[str] = None,
    grid: bool = True,
    tight_layout: bool = True,
    ax: Optional[plt.Axes] = None,
    figure_kwargs: Optional[Dict[str, Any]] = None,
    subplot_kwargs: Optional[Dict[str, Any]] = None,
    plot_kwargs: Optional[Dict[str, Any]] = None,
    grid_kwargs: Optional[Dict[str, Any]] = None,
    legend_kwargs: Optional[Dict[str, Any]] = None,
    tick_kwargs: Optional[Dict[str, Any]] = None,
    label_kwargs: Optional[Dict[str, Any]] = None,
    title_kwargs: Optional[Dict[str, Any]] = None,
) -> Tuple[Figure, plt.Axes]:
    """Plot simulation results as a grid."""
    kwargs = _get_plot_kwargs(
        figure_kwargs=figure_kwargs,
        subplot_kwargs=subplot_kwargs,
        plot_kwargs=plot_kwargs,
        grid_kwargs=grid_kwargs,
        tick_kwargs=tick_kwargs,
        label_kwargs=label_kwargs,
        title_kwargs=title_kwargs,
        legend_kwargs=legend_kwargs,
    )
    ylabel = ylabel if ylabel is not None else "Remember to label your axes"
    xlabel = xlabel if xlabel is not None else "Remember to label your axes"

    if ax is None:
        fig, ax = plt.subplots(
            nrows=1,
            ncols=1,
            squeeze=True,
            subplot_kw=kwargs["subplot"],
            **kwargs["figure"],
        )
    else:
        fig = ax.get_figure()
    ax.plot(*plot_args, **kwargs["plot"])
    if grid:
        ax.grid(True, which="major", axis="both", **kwargs["grid"])
    if legend is not None:
        if isinstance(legend, str):
            legend = [legend]
        ax.legend(legend, **kwargs["legend"])
    ax.set_ylabel(ylabel, **kwargs["label"])
    ax.set_xlabel(xlabel, **kwargs["label"])
    ax.set_title(title, **kwargs["title"])
    ax.tick_params(**kwargs["ticks"])
    if tight_layout:
        fig.tight_layout()
    return fig, ax


def plot_grid(
    plot_groups: List[Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]],
    legend_groups: Optional[Iterable] = None,
    ncols: Optional[int] = None,
    sharex: bool = True,
    sharey: bool = True,
    xlabels: Optional[Union[str, Iterable[str]]] = None,
    ylabels: Optional[Union[str, Iterable[str]]] = None,
    figure_title: str = None,
    plot_titles: Optional[Union[Iterable[str], Iterable[None]]] = None,
    grid: bool = True,
    tight_layout: bool = True,
    figure_kwargs: Optional[Dict[str, Any]] = None,
    subplot_kwargs: Optional[Dict[str, Any]] = None,
    plot_kwargs: Optional[Dict[str, Any]] = None,
    grid_kwargs: Optional[Dict[str, Any]] = None,
    legend_kwargs: Optional[Dict[str, Any]] = None,
    tick_kwargs: Optional[Dict[str, Any]] = None,
    label_kwargs: Optional[Dict[str, Any]] = None,
    title_kwargs: Optional[Dict[str, Any]] = None,
) -> Tuple[Figure, Axes]:
    """Plot simulation results as a grid."""
    if ncols is None:
        _, ncols = min(
            ((math.ceil(len(plot_groups) / i) * i - len(plot_groups), i) for i in range(2, 6)),
            key=lambda x: (x[0], -x[1]),
        )
    nrows = math.ceil(len(plot_groups) / ncols)
    if figure_kwargs is None:
        figure_kwargs = {}
    figure_kwargs.setdefault("figsize", (5 * ncols, 4 * nrows))
    if legend_kwargs is None:
        legend_kwargs = {}
    legend_kwargs.setdefault("loc", "best")
    legend_kwargs.setdefault("bbox_to_anchor", None)
    legend_kwargs.setdefault("borderaxespad", 0.5)
    kwargs = _get_plot_kwargs(
        figure_kwargs=figure_kwargs,
        subplot_kwargs=subplot_kwargs,
        plot_kwargs=plot_kwargs,
        grid_kwargs=grid_kwargs,
        tick_kwargs=tick_kwargs,
        label_kwargs=label_kwargs,
        title_kwargs=title_kwargs,
        legend_kwargs=legend_kwargs,
    )

    if legend_groups is None:
        legend_groups = it.repeat(None)
    if ylabels is None:
        ylabels = it.repeat("Remember to label your axes")
    else:
        if isinstance(ylabels, str):
            ylabels = it.repeat(ylabels)
    if xlabels is None:
        xlabels = it.repeat("Remember to label your axes")
    else:
        if isinstance(xlabels, str):
            xlabels = it.repeat(xlabels)
    if plot_titles is None:
        plot_titles = it.repeat(None)

    fig, axs = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        sharex=sharex,
        sharey=sharey,
        squeeze=False,
        subplot_kw=kwargs["subplot"],
        **kwargs["figure"],
    )
    axs = cast(Axes, axs)
    for ax, plot_args, legend_args, title in zip(axs.ravel(), plot_groups, legend_groups, plot_titles):
        ax.plot(*plot_args, **kwargs["plot"])
        ax.set_title(title, **kwargs["title"])
        if legend_args is not None:
            ax.legend(legend_args, **kwargs["legend"])
        ax.tick_params(**kwargs["ticks"])
        if grid:
            ax.grid(True, which="major", axis="both", **kwargs["grid"])

    if sharey:
        for ax, ylabel in zip(axs[:, 0], ylabels):
            ax.set_ylabel(ylabel, **kwargs["label"])
    else:
        for ax, ylabel in zip(axs.ravel(), ylabels):
            ax.set_ylabel(ylabel, **kwargs["label"])
    if sharex:
        for ax, xlabel in zip(axs[-1], xlabels):
            ax.set_xlabel(xlabel, **kwargs["label"])
    else:
        for ax, xlabel in zip(axs.ravel(), xlabels):
            ax.set_xlabel(xlabel, **kwargs["label"])
    fig.suptitle(figure_title, y=1.025, **kwargs["title"])
    if tight_layout:
        fig.tight_layout()
    return fig, axs


def relative_luminance(color: List[float]) -> float:
    """Calculate the relative luminance of a color."""
    rgb = colorConverter.to_rgba_array(color)[:, :3]

    # If RsRGB <= 0.03928 then R = RsRGB/12.92 else R = ((RsRGB+0.055)/1.055) ^ 2.4
    rsrgb = np.where(rgb <= 0.03928, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)

    # L = 0.2126 * R + 0.7152 * G + 0.0722 * B
    rel_luminance: List[float] = np.matmul(rsrgb, [0.2126, 0.7152, 0.0722])
    return rel_luminance[0]


def get_norm(vmin: float, vmax: float) -> plt.Normalize:
    if vmax < 1000 and vmin > -1000:
        norm = Normalize(vmin=vmin, vmax=vmax)
    elif vmin <= 0:
        norm = SymLogNorm(linthresh=1, vmin=vmin, vmax=vmax, base=10)
    else:
        norm = LogNorm(vmin=vmin, vmax=vmax)
    return norm


def heatmap_from_dataframe(
    df: pd.DataFrame,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    annotate: bool = True,
    colorbar: bool = True,
    cmap: str = "viridis",
    vmax: Optional[float] = None,
    vmin: Optional[float] = None,
    norm: plt.Normalize = None,
    ax: Optional[plt.Axes] = None,
    cax: Optional[plt.Axes] = None,
    sci_annotation_bounds: Tuple[float, float] = (0.01, 100),
    annotation_style: str = "2g",
) -> Tuple[Figure, plt.Axes, QuadMesh]:
    data = df.values
    rows = df.index
    columns = df.columns

    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure()

    # Create norm
    if norm is None:
        if vmax is None:
            vmax = np.nanmax(data)
        if vmin is None:
            vmin = np.nanmin(data)
        vmax = cast(float, vmax)
        vmin = cast(float, vmin)
        norm = get_norm(vmin=vmin, vmax=vmax)

    # Create heatmap
    hm = ax.pcolormesh(data, norm=norm, cmap=cmap)

    # Despine axis
    for side in ["top", "right", "left", "bottom"]:
        ax.spines[side].set_visible(False)

    # Set the axis limits
    ax.set(xlim=(0, data.shape[1]), ylim=(0, data.shape[0]))

    # Set ticks and ticklabels
    ax.set_xticks(np.arange(len(columns)) + 0.5)
    ax.set_xticklabels(columns)

    ax.set_yticks(np.arange(len(rows)) + 0.5)
    ax.set_yticklabels(rows)

    # Set title and axis labels
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    if annotate:
        text_kwargs = {"ha": "center", "va": "center"}
        hm.update_scalarmappable()  # So that get_facecolor is an array
        xpos, ypos = np.meshgrid(np.arange(len(columns)), np.arange(len(rows)))
        for x, y, val, color in zip(xpos.flat, ypos.flat, hm.get_array(), hm.get_facecolor()):
            text_kwargs["color"] = "black" if relative_luminance(color) > 0.45 else "white"
            if sci_annotation_bounds[0] < abs(val) <= sci_annotation_bounds[1]:
                val_text = f"{val:.{annotation_style}}"
            else:
                val_text = f"{val:.0e}"
            ax.text(x + 0.5, y + 0.5, val_text, **text_kwargs)

    if colorbar:
        # Add a colorbar
        cb = ax.figure.colorbar(hm, cax, ax)
        cb.outline.set_linewidth(0)

    # Invert the y axis to show the plot in matrix form
    ax.invert_yaxis()
    return fig, ax, hm
