#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
"""Tools for display of calibration IO in notebooks."""

import os
import typing as t

import holoviews as hv
import numpy as np
import pandas as pd
import xarray as xr
from bokeh.models import PrintfTickFormatter

from pyxel import load_image

if t.TYPE_CHECKING:
    from pyxel.calibration import Calibration
    from pyxel.detectors import Detector


def display_calibration_inputs(
    calibration: "Calibration", detector: "Detector"
) -> hv.Layout:
    """Display calibration inputs and target data based on configuration file.

    Parameters
    ----------
    calibration: Calibration
        Instance of Calibration.
    detector: Detector
        Instance of Detector.

    Returns
    -------
    plot: hv.Layout
    """

    fnames_input = calibration.result_input_arguments[0].values
    fnames_target = [str(os.path.relpath(x)) for x in calibration.target_data_path]

    input_range = calibration.result_fit_range
    target_range = calibration.target_fit_range

    input_columns = input_range[3] - input_range[2]
    target_columns = target_range[3] - target_range[2]

    def get_data_input(data_id: int) -> t.Union[hv.Image, hv.Curve]:
        """Get input data based on configuration file.

        Parameters
        ----------
        data_id

        Returns
        -------
        im
        """

        # TODO: Fix typing, what if input arguments in calibration not strings?
        data = load_image(fnames_input[data_id])  # type: ignore
        if data.ndim == 1:
            im = hv.Curve((range(len(data)), data)).opts(
                tools=["hover"], aspect=1.5, xlabel="x", ylabel="z"
            )
        elif input_columns == 1:
            im = hv.Curve(
                (range(len(data[:, input_range[2]])), data[:, input_range[2]])
            ).opts(tools=["hover"], aspect=1.5, xlabel="x", ylabel="z")
        else:
            im = hv.Image((range(data.shape[1]), range(data.shape[0]), data)).opts(
                colorbar=True,
                cmap="gray",
                tools=["hover"],
                aspect=(detector.geometry.col / detector.geometry.row),
            )

        return im

    def get_data_target(data_id: int) -> t.Union[hv.Image, hv.Curve]:
        """Get target data based on the configuration file.

        Parameters
        ----------
        data_id

        Returns
        -------
        im
        """

        data = load_image(fnames_target[data_id])

        if data.ndim == 1:
            im = hv.Curve((range(len(data)), data)).opts(
                tools=["hover"], aspect=1.5, xlabel="x", ylabel="z"
            )
        elif target_columns == 1:
            im = hv.Curve(
                (range(len(data[:, target_range[2]])), data[:, target_range[2]])
            ).opts(tools=["hover"], aspect=1.5, xlabel="x", ylabel="z")
        else:
            im = hv.Image((range(data.shape[1]), range(data.shape[0]), data)).opts(
                colorbar=True,
                cmap="gray",
                tools=["hover"],
                aspect=(detector.geometry.col / detector.geometry.row),
            )

        return im

    ids = range(len(calibration.target_data_path))

    dmap1 = (
        hv.DynamicMap(get_data_input, kdims=["id"])
        .redim.values(id=ids)
        .relabel("Input")
    )
    dmap2 = (
        hv.DynamicMap(get_data_target, kdims=["id"])
        .redim.values(id=ids)
        .relabel("Target")
    )
    table = (
        hv.Table({"Input": fnames_input, "Target": fnames_target}, ["Input", "Target"])
        .opts(width=500)
        .relabel("Filenames")
    )

    plot = (
        dmap1.opts(framewise=True, axiswise=True)
        + dmap2.opts(framewise=True, axiswise=True)
        + table
    ).opts(tabs=True)

    return plot


def display_simulated(ds: xr.Dataset) -> hv.Layout:
    """Display simulated and target data from the output dataset.

    Parameters
    ----------
    ds: Dataset
        Result dataset.

    Returns
    -------
    hv.Layout
    """
    result_type = ds.attrs["result_type"]

    var_name = {
        "ResultType.Image": "simulated_image",
        "ResultType.Signal": "simulated_signal",
        "ResultType.Pixel": "simulated_pixel",
    }[result_type]

    simulated_data = ds[var_name]
    target_data = ds["target"]

    output_data = xr.Dataset()
    output_data["simulated"] = simulated_data
    output_data["target"] = target_data
    output_data["residuals"] = target_data - simulated_data

    if len(output_data["target"].x) == 1:
        ds_target = hv.Dataset(output_data["target"].sel(x=0))
        ds_simulated = hv.Dataset(output_data["simulated"].sel(x=0))
        ds_residuals = hv.Dataset(output_data["residuals"].sel(x=0))

        plot_target_scatter = ds_target.to(hv.Scatter, kdims=["y"], dynamic=True)
        plot_target_line = ds_target.to(hv.Curve, kdims=["y"], dynamic=True)
        plot_simulated = ds_simulated.to(hv.Curve, kdims=["y"], dynamic=True)
        plot_residuals = ds_residuals.to(hv.Curve, kdims=["y"], dynamic=True)

        plot_target_scatter = plot_target_scatter.opts(
            logy=True,
            height=450,
            width=600,
            marker="o",
            size=5,
            fill_color=None,
            title="Target",
        )
        plot_target_line = plot_target_line.opts(
            logy=True,
            height=450,
            width=600,
            ylabel="Signal",
            title="Target",
            framewise=True,
            axiswise=True,
        )
        plot_simulated = plot_simulated.opts(
            logy=True,
            height=450,
            width=600,
            ylabel="Signal",
            title="Simulated",
            color="black",
            framewise=True,
            axiswise=True,
        )
        plot_residuals = plot_residuals.opts(
            height=450, width=600, title="Residuals", framewise=True, axiswise=True
        )

        overlay = (plot_simulated * plot_target_scatter).opts(title="Overlay")

        return (plot_simulated + plot_target_line + overlay + plot_residuals).opts(
            tabs=True
        )

    elif len(output_data["target"].y) == 1:
        ds_target = hv.Dataset(output_data["target"].sel(y=0))
        ds_simulated = hv.Dataset(output_data["simulated"].sel(y=0))
        ds_residuals = hv.Dataset(output_data["residuals"].sel(y=0))

        plot_target_scatter = ds_target.to(hv.Scatter, kdims=["x"], dynamic=True)
        plot_target_line = ds_target.to(hv.Curve, kdims=["x"], dynamic=True)
        plot_simulated = ds_simulated.to(hv.Curve, kdims=["x"], dynamic=True)
        plot_residuals = ds_residuals.to(hv.Curve, kdims=["x"], dynamic=True)

        plot_target_scatter = plot_target_scatter.opts(
            logy=True,
            height=450,
            width=600,
            marker="o",
            size=5,
            fill_color=None,
            title="Target",
        )
        plot_target_line = plot_target_line.opts(
            logy=True,
            height=450,
            width=600,
            ylabel="Signal",
            title="Target",
            framewise=True,
            axiswise=True,
        )
        plot_simulated = plot_simulated.opts(
            logy=True,
            height=450,
            width=600,
            ylabel="Signal",
            title="Simulated",
            color="black",
            framewise=True,
            axiswise=True,
        )
        plot_residuals = plot_residuals.opts(
            height=450, width=600, title="Residuals", framewise=True, axiswise=True
        )

        overlay = (plot_simulated.opts(color="black") * plot_target_scatter).opts(
            title="Overlay"
        )

        return (plot_simulated + plot_target_line + overlay + plot_residuals).opts(
            tabs=True
        )

    else:
        ds_target = hv.Dataset(output_data["target"])
        ds_simulated = hv.Dataset(output_data["simulated"])
        ds_residuals = hv.Dataset(output_data["residuals"])

        plot_target = ds_target.to(hv.Image, dynamic=True).relabel(label="Target")
        plot_simulated = ds_simulated.to(hv.Image, dynamic=True).relabel(
            label="Simulated"
        )
        plot_residuals = ds_residuals.to(hv.Image, dynamic=True).opts(title="Residuals")

        aspect = len(output_data["target"].y) / len(output_data["target"].x)

        plot_target = plot_target.opts(
            colorbar=True,
            cmap="gray",
            tools=["hover"],
            aspect=aspect,
            framewise=True,
            axiswise=True,
        )
        plot_simulated = plot_simulated.opts(
            colorbar=True,
            cmap="gray",
            tools=["hover"],
            aspect=aspect,
            framewise=True,
            axiswise=True,
        )
        plot_residuals = plot_residuals.opts(
            colorbar=True,
            cmap="gray",
            tools=["hover"],
            aspect=aspect,
            framewise=True,
            axiswise=True,
        )

        return (plot_simulated + plot_target + plot_residuals).opts(tabs=True)


def display_evolution(ds: xr.Dataset) -> hv.Layout:
    """Display best champion parameter and overall fitness vs evolution.

    Parameters
    ----------
    ds: Dataset
        Result dataset.

    Returns
    -------
    plot: hv.Layout
        Output plot.
    """
    output_champions = xr.Dataset()
    output_champions["fitness"] = ds["champion_fitness"].drop(labels="evolution")  # type: ignore
    output_champions["parameters"] = ds["champion_parameters"].assign_coords(
        {"param_id": range(len(ds.param_id))}
    )

    ds_parameters = hv.Dataset(output_champions["parameters"])
    plot_parameters = ds_parameters.to(
        hv.Scatter, kdims=["evolution"], dynamic=True
    ).opts(aspect=1.5, axiswise=True, framewise=True, ylabel="Champion parameter")
    ds_fitness = hv.Dataset(output_champions["fitness"])
    plot_fitness = ds_fitness.to(hv.Scatter, kdims=["evolution"], dynamic=True).opts(
        aspect=1.5, axiswise=True, framewise=True, ylabel="Fitness"
    )

    plot = (
        plot_fitness.relabel("Fitness")
        + plot_parameters.relabel("Best champion parameters")
    ).opts(tabs=True)

    return plot


def optimal_parameters(ds: xr.Dataset) -> pd.DataFrame:
    """Return a dataframe of best parameters.

    Parameters
    ----------
    ds: Dataset
        Result dataset.

    Returns
    -------
    best: DataFrame
        Best champion parameters
    """

    best = (
        ds.champion_parameters.isel(evolution=-1)
        .isel(island=ds.champion_fitness.isel(evolution=-1).argmin())
        .to_dataframe()
    )
    return best


def champion_heatmap(
    ds: xr.Dataset,
    num_bins: int = 100,
    logx: bool = False,
    parameter_range: t.Optional[list] = None,
    island_range: t.Optional[list] = None,
    ind_range: t.Optional[list] = None,
) -> hv.Points:
    """Plot a heatmap of champion parameters vs fitness.

    Parameters
    ----------
    ds: Dataset
        Result dataset.
    num_bins: int
        Number of bins, default is 100.
    logx: bool
        Logarithmic x axis.
    parameter_slice: slice
        Parameters slice.
    island_slice: slice
        Islands slice.
    ind_slice: slice
        Individuals slice.

    Returns
    -------
    plot: hv.Points
        Champion heatmap.
    """

    if parameter_range:
        parameter_slice = slice(parameter_range[0], parameter_range[1])
    else:
        parameter_slice = slice(None)
    if island_range:
        island_slice = slice(island_range[0], island_range[1])
    else:
        island_slice = slice(None)
    if ind_range:
        ind_slice = slice(ind_range[0], ind_range[1])
    else:
        ind_slice = slice(None)

    if "best_fitness" in ds:
        individuals = xr.Dataset()
        individuals["fitness"] = ds["best_fitness"].drop(labels="evolution")  # type: ignore
        individuals["parameters"] = ds["best_parameters"].assign_coords(
            {"param_id": range(len(ds.param_id))}
        )

        ind_id = individuals.coords["individual"].values

    output_champions = xr.Dataset()
    output_champions["fitness"] = ds["champion_fitness"].drop(labels="evolution")  # type: ignore
    output_champions["parameters"] = ds["champion_parameters"].assign_coords(
        {"param_id": range(len(ds.param_id))}
    )

    x = np.array([])  # type: np.ndarray
    y = np.array([])  # type: np.ndarray

    for parameter in output_champions.param_id[parameter_slice]:
        for island in output_champions.island[island_slice]:
            x = np.append(
                x,
                np.asarray(
                    output_champions.sel(param_id=parameter).sel(island=island)[
                        "parameters"
                    ]
                ),
            )
            y = np.append(
                y,
                np.asarray(
                    output_champions.sel(param_id=parameter).sel(island=island)[
                        "fitness"
                    ]
                ),
            )

            if "best_fitness" in ds:
                for k in ind_id[ind_slice]:
                    x = np.append(
                        x,
                        np.asarray(
                            individuals.sel(param_id=parameter)
                            .sel(island=island)
                            .sel(individual=k)["parameters"]
                        ),
                    )
                    y = np.append(
                        y,
                        np.asarray(
                            individuals.sel(param_id=parameter)
                            .sel(island=island)
                            .sel(individual=k)["fitness"]
                        ),
                    )

    # x=x[y<18500]
    # y=y[y<18500]

    # y=y[x>1e-7]
    # x=x[x>1e-7]

    if logx is True:
        bins = [
            np.geomspace(0.9 * np.min(x), 1.1 * np.max(x), num_bins + 1),
            num_bins,
        ]  # type: t.Union[list, int]
    else:
        bins = num_bins

    hist, xs, ys = np.histogram2d(x, y, bins=bins)

    df = pd.DataFrame(hist).stack().rename_axis(["x", "y"]).reset_index(name="val")
    df["x"] = [xs[x] for x in df["x"]]
    df["y"] = [ys[y] for y in df["y"]]
    df = df[(df[["val"]] != 0).all(axis=1)]
    df["val"] = np.array(df["val"], dtype=int)

    formatter = PrintfTickFormatter(format="%.0e")

    plot = hv.Points(df, kdims=["x", "y"], vdims=["val"]).opts(logx=logx, logz=True)
    plot = plot.opts(
        marker="s",
        height=650,
        width=900,
        tools=["hover"],
        color="val",
        colorbar=True,
        cmap="kbc_r",
        ylabel="Fitness",
        size=0.5,
        framewise=True,
        axiswise=True,
        colorbar_opts={"formatter": formatter},
        clabel="Occurence",
    )

    return plot
