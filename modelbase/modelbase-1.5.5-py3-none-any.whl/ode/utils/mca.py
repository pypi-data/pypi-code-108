from __future__ import annotations

__all__ = [
    "get_compound_elasticity",
    "get_compound_elasticities_array",
    "get_compound_elasticities_df",
    "get_parameter_elasticity",
    "get_parameter_elasticities_array",
    "get_parameter_elasticities_df",
    "get_response_coefficients",
    "get_response_coefficients_array",
    "get_response_coefficients_df",
    "get_concentration_response_coefficient",
    "get_concentration_response_coefficients_array",
    "get_concentration_response_coefficients_df",
    "get_flux_response_coefficient",
    "get_flux_response_coefficients_array",
    "get_flux_response_coefficients_df",
    "plot_coefficient_heatmap",
    "plot_multiple",
    "plot_concentration_response_coefficients",
    "plot_flux_response_coefficients",
]
import math
from typing import Dict, List, Optional, Tuple, Union, cast

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import pandas as pd
from matplotlib import cm
from matplotlib.collections import QuadMesh
from matplotlib.figure import Figure
from tqdm.auto import tqdm

from ...typing import Axes
from ...utils.plotting import get_norm as _get_norm
from ...utils.plotting import heatmap_from_dataframe as _heatmap_from_dataframe
from ..models import Model
from ..simulators import Simulator

_DISPLACEMENT = 1e-4


def _find_steady_state(
    *,
    model: Model,
    y0: Union[List[float], npt.NDArray[np.float64], Dict[str, float]],
) -> Tuple[Optional[npt.NDArray[np.float64]], Optional[npt.NDArray[np.float64]]]:
    """Simulate the system to steadt state."""
    s = Simulator(model=model)
    s.initialise(y0=y0, test_run=False)
    t, y = s.simulate_to_steady_state()
    return t, y


def get_compound_elasticity(
    model: Model,
    compound: str,
    y: Dict[str, float],
    t: float = 0,
    normalized: bool = True,
    displacement: float = _DISPLACEMENT,
) -> npt.NDArray[np.float64]:
    """Get sensitivity of all rates to a change of the concentration of a compound.

    Also called epsilon-elasticities. Not in steady state!
    """
    fcd = model.get_full_concentration_dict(y=y, t=t)
    old_concentration = fcd[compound]
    fluxes = []
    for new_concentration in (
        old_concentration * (1 + displacement),
        old_concentration * (1 - displacement),
    ):
        fcd[compound] = new_concentration
        fluxes.append(model.get_fluxes_array(y=fcd, t=t))
    elasticity_coef = (fluxes[0] - fluxes[1]) / (2 * displacement * old_concentration)
    if normalized:
        fcd[compound] = old_concentration
        flux_array = model.get_fluxes_array(y=fcd, t=t)
        elasticity_coef *= old_concentration / flux_array
    return cast(npt.NDArray[np.float64], np.atleast_1d(np.squeeze(elasticity_coef)))


def get_compound_elasticities_array(
    model: Model,
    compounds: List[str],
    y: Dict[str, float],
    t: float = 0,
    normalized: bool = True,
    displacement: float = _DISPLACEMENT,
) -> npt.NDArray[np.float64]:
    """Get sensitivity of all rates to a change of the concentration of multiple compounds.

    Also called epsilon-elasticities. Not in steady state!
    """
    elasticities = np.full(shape=(len(compounds), len(model.get_rate_names())), fill_value=np.nan)
    for i, compound in enumerate(compounds):
        elasticities[i] = get_compound_elasticity(
            model=model,
            compound=compound,
            y=y,
            t=t,
            normalized=normalized,
            displacement=displacement,
        )
    return elasticities


def get_compound_elasticities_df(
    model: Model,
    compounds: List[str],
    y: Dict[str, float],
    t: float = 0,
    normalized: bool = True,
    displacement: float = _DISPLACEMENT,
) -> pd.DataFrame:
    """Get sensitivity of all rates to a change of the concentration of multiple compounds.

    Also called epsilon-elasticities. Not in steady state!
    """
    array = get_compound_elasticities_array(
        model=model,
        compounds=compounds,
        y=y,
        t=t,
        normalized=normalized,
        displacement=displacement,
    )
    return pd.DataFrame(data=array, index=compounds, columns=model.get_rate_names())


def get_parameter_elasticity(
    model: Model,
    parameter: str,
    y: Dict[str, float],
    t: float = 0,
    normalized: bool = True,
    displacement: float = _DISPLACEMENT,
) -> npt.NDArray[np.float64]:
    """Get sensitivity of all rates to a change of a parameter value.

    Also called pi-elasticities. Not in steady state!
    """
    model = model.copy()
    old_value = model.get_parameter(parameter_name=parameter)
    fluxes = []
    for new_value in [old_value * (1 + displacement), old_value * (1 - displacement)]:
        model.update_parameter(parameter_name=parameter, parameter_value=new_value)
        fluxes.append(model.get_fluxes_array(y=y, t=t))
    elasticity_coef = (fluxes[0] - fluxes[1]) / (2 * displacement * old_value)
    if normalized:
        model.update_parameter(parameter_name=parameter, parameter_value=old_value)
        fluxes_array = model.get_fluxes_array(y=y, t=t)
        elasticity_coef *= old_value / fluxes_array
    return cast(npt.NDArray[np.float64], np.atleast_1d(np.squeeze(elasticity_coef)))


def get_parameter_elasticities_array(
    model: Model,
    parameters: List[str],
    y: Dict[str, float],
    t: float = 0,
    normalized: bool = True,
    displacement: float = _DISPLACEMENT,
) -> npt.NDArray[np.float64]:
    """Get sensitivity of all rates to a change of multiple parameter values.

    Also called pi-elasticities. Not in steady state!
    """
    elasticities = np.full(shape=(len(parameters), len(model.get_rate_names())), fill_value=np.nan)
    for i, parameter in enumerate(parameters):
        elasticities[i] = get_parameter_elasticity(
            model=model,
            parameter=parameter,
            y=y,
            t=t,
            normalized=normalized,
            displacement=displacement,
        )
    return elasticities


def get_parameter_elasticities_df(
    model: Model,
    parameters: List[str],
    y: Dict[str, float],
    t: float = 0,
    normalized: bool = True,
    displacement: float = _DISPLACEMENT,
) -> pd.DataFrame:
    """Get sensitivity of all rates to a change of multiple parameter values.

    Also called pi-elasticities. Not in steady state!"""
    matrix = get_parameter_elasticities_array(
        model=model,
        parameters=parameters,
        y=y,
        t=t,
        normalized=normalized,
        displacement=displacement,
    )
    return pd.DataFrame(matrix, index=parameters, columns=model.get_rate_names())


def get_response_coefficients(
    model: Model,
    parameter: str,
    y: Union[Dict[str, float], npt.NDArray[np.float64], List],
    normalized: bool = True,
    displacement: float = _DISPLACEMENT,
) -> Tuple[Optional[npt.NDArray[np.float64]], Optional[npt.NDArray[np.float64]]]:
    """Get response of the steady state concentrations and fluxes to a change of the given parameter."""
    model = model.copy()
    old_value = model.get_parameter(parameter_name=parameter)
    if normalized:
        t_ss, y_ss = _find_steady_state(model=model, y0=y)
        if t_ss is None or y_ss is None:
            return None, None
        fluxes_array_norm = model.get_fluxes_array(y=y_ss, t=t_ss)
        fcd = model.get_full_concentration_dict(y_ss)
        del fcd["time"]
        y_ss_norm = old_value / np.fromiter(fcd.values(), dtype="float")
        fluxes_array_norm = old_value / fluxes_array_norm

    ss: list[npt.NDArray[np.float64]] = []
    fluxes: list[npt.NDArray[np.float64]] = []
    for new_value in [
        old_value * (1 + displacement),
        old_value * (1 - displacement),
    ]:
        model.update_parameter(parameter_name=parameter, parameter_value=new_value)
        t_ss, y_ss = _find_steady_state(model=model, y0=y)
        if t_ss is None or y_ss is None:
            return None, None
        fcd = model.get_full_concentration_dict(y_ss)
        del fcd["time"]
        ss.append(np.fromiter(fcd.values(), dtype="float"))
        fluxes.append(model.get_fluxes_array(y=y_ss, t=t_ss))

    conc_resp_coef: npt.NDArray[np.float64] = (ss[0] - ss[1]) / (2 * displacement * old_value)
    flux_resp_coef: npt.NDArray[np.float64] = (fluxes[0] - fluxes[1]) / (2 * displacement * old_value)

    if normalized:
        conc_resp_coef *= y_ss_norm  # type: ignore
        flux_resp_coef *= fluxes_array_norm  # type: ignore
    return np.atleast_1d(np.squeeze(conc_resp_coef)), np.atleast_1d(np.squeeze(flux_resp_coef))


def get_response_coefficients_array(
    model: Model,
    parameters: List[str],
    y: Dict[str, float],
    normalized: bool = True,
    displacement: float = _DISPLACEMENT,
) -> Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    """Get response of the steady state concentrations and fluxes to a change of the given parameter."""
    crcs = np.full(shape=(len(parameters), len(model.get_all_compounds())), fill_value=np.nan)
    frcs = np.full(shape=(len(parameters), len(model.get_rate_names())), fill_value=np.nan)
    for i, parameter in tqdm(enumerate(parameters), total=len(parameters)):
        crc, frc = get_response_coefficients(
            model=model,
            parameter=parameter,
            y=y,
            normalized=normalized,
            displacement=displacement,
        )
        if crc is not None:
            crcs[i] = crc
        if frc is not None:
            frcs[i] = frc
    return crcs, frcs


def get_response_coefficients_df(
    model: Model,
    parameters: List[str],
    y: Dict[str, float],
    normalized: bool = True,
    displacement: float = _DISPLACEMENT,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Get response of the steady state concentrations and fluxes to a change of the given parameter."""
    crcs, frcs = get_response_coefficients_array(
        model=model,
        parameters=parameters,
        y=y,
        normalized=normalized,
        displacement=displacement,
    )
    crcs_df = pd.DataFrame(
        data=crcs,
        index=parameters,
        columns=model.get_all_compounds(),
    )
    frcs_df = pd.DataFrame(
        data=frcs,
        index=parameters,
        columns=model.get_rate_names(),
    )
    return crcs_df, frcs_df


def get_concentration_response_coefficient(
    model: Model,
    parameter: str,
    y: Dict[str, float],
    normalized: bool = True,
    displacement: float = _DISPLACEMENT,
) -> Optional[npt.NDArray[np.float64]]:
    """Get response of the steady state concentrations to a change of the given parameter."""
    return get_response_coefficients(
        model=model, parameter=parameter, y=y, normalized=normalized, displacement=displacement
    )[0]


def get_concentration_response_coefficients_array(
    model: Model,
    parameters: List[str],
    y: Dict[str, float],
    normalized: bool = True,
    displacement: float = _DISPLACEMENT,
) -> npt.NDArray[np.float64]:
    """Get response of the steady state concentrations to a change of the given parameters."""
    return get_response_coefficients_array(
        model=model,
        parameters=parameters,
        y=y,
        normalized=normalized,
        displacement=displacement,
    )[0]


def get_concentration_response_coefficients_df(
    model: Model,
    parameters: List[str],
    y: Dict[str, float],
    normalized: bool = True,
    displacement: float = _DISPLACEMENT,
) -> pd.DataFrame:
    """Get response of the steady state concentrations to a change of the given parameters"""
    return get_response_coefficients_df(
        model=model,
        parameters=parameters,
        y=y,
        normalized=normalized,
        displacement=displacement,
    )[0]


def get_flux_response_coefficient(
    model: Model,
    parameter: str,
    y: Dict[str, float],
    normalized: bool = True,
    displacement: float = _DISPLACEMENT,
) -> Optional[npt.NDArray[np.float64]]:
    """Get response of the steady state fluxes to a change of the given parameter."""
    return get_response_coefficients(
        model=model, parameter=parameter, y=y, normalized=normalized, displacement=displacement
    )[1]


def get_flux_response_coefficients_array(
    model: Model,
    parameters: List[str],
    y: Dict[str, float],
    normalized: bool = True,
    displacement: float = _DISPLACEMENT,
) -> npt.NDArray[np.float64]:
    """Get response of the steady state fluxes to a change of the given parameters."""
    return get_response_coefficients_array(
        model=model,
        parameters=parameters,
        y=y,
        normalized=normalized,
        displacement=displacement,
    )[1]


def get_flux_response_coefficients_df(
    model: Model,
    parameters: List[str],
    y: Dict[str, float],
    normalized: bool = True,
    displacement: float = _DISPLACEMENT,
) -> pd.DataFrame:
    """Get response of the steady state fluxes to a change of the given parameters."""
    return get_response_coefficients_df(
        model=model,
        parameters=parameters,
        y=y,
        normalized=normalized,
        displacement=displacement,
    )[1]


def plot_coefficient_heatmap(
    df: pd.DataFrame,
    title: str,
    cmap: str = "RdBu_r",
    rows: int = None,
    columns: int = None,
    vmax: float = None,
    vmin: float = None,
    norm: plt.Normalize = None,
    annotate: bool = True,
    colorbar: bool = True,
    xlabel: str = None,
    ylabel: str = None,
    ax: plt.Axes = None,
    cax: plt.Axes = None,
) -> Tuple[Figure, plt.Axes, QuadMesh]:
    """Plot the DataFrame of a response coefficient as a heatmap.

    Use the rows and columns arguments to only plot a subset of the data.
    """
    df = df.T.round(2)
    if rows is None:
        rows = df.index  # type: ignore
    if columns is None:
        columns = df.columns  # type: ignore
    fig, ax, hm = _heatmap_from_dataframe(
        df=df.loc[rows, columns],  # type: ignore
        title=title,
        xlabel=xlabel,
        ylabel=ylabel,
        annotate=annotate,
        colorbar=colorbar,
        cmap=cmap,
        norm=norm,
        vmax=vmax,
        vmin=vmin,
        ax=ax,
        cax=cax,
    )
    ax.set_xticklabels(ax.get_xticklabels(), **{"rotation": 45, "ha": "right"})
    return fig, ax, hm


def plot_multiple(
    dfs: List[pd.DataFrame],
    titles: List[str],
    cmap: str = "RdBu_r",
    annotate: bool = True,
    colorbar: bool = True,
    figsize: Tuple[int, int] = None,
) -> Tuple[Figure, Axes]:
    """Plot multiple heatmaps of the response coefficient DataFrames.

    See also
    --------
    plot_coefficient_heatmap
    """
    vmin = min(i.values.min() for i in dfs)
    vmax = max(i.values.max() for i in dfs)

    n_cols = 2
    n_rows = math.ceil(len(dfs) / n_cols)

    norm = _get_norm(vmin=vmin, vmax=vmax)

    if figsize is None:
        figsize = (n_cols * 4, n_rows * 4)

    fig, axs = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=figsize, squeeze=False)
    axs = cast(Axes, axs)
    for ax, df, title in zip(axs.ravel(), dfs, titles):
        plot_coefficient_heatmap(
            df=df,
            title=title,
            cmap=cmap,
            annotate=annotate,
            colorbar=False,
            norm=norm,
            ax=ax,
        )

    # Add a colorbar+
    if colorbar:
        cb = fig.colorbar(
            cm.ScalarMappable(norm=norm, cmap=cmap),
            ax=axs.ravel()[-1],
        )
        cb.outline.set_linewidth(0)
    fig.tight_layout()
    return fig, axs


def plot_concentration_response_coefficients(
    model: Model,
    parameters: List[str],
    y: Dict[str, float],
    normalized: bool = True,
    displacement: float = _DISPLACEMENT,
    cmap: str = "RdBu_r",
    rows: int = None,
    columns: int = None,
    vmax: float = None,
    vmin: float = None,
    annotate: bool = True,
    colorbar: bool = True,
    xlabel: str = None,
    ylabel: str = None,
    ax: plt.Axes = None,
    cax: plt.Axes = None,
) -> Tuple[Figure, plt.Axes, QuadMesh]:
    """Calculate and plot response of the steady state concentration to a change of the given parameters.

    See also
    --------
    get_concentration_response_coefficients_df
    plot_coefficient_heatmap
    """
    df = get_concentration_response_coefficients_df(
        model=model,
        parameters=parameters,
        y=y,
        normalized=normalized,
        displacement=displacement,
    )
    return plot_coefficient_heatmap(
        df=df,
        title="Concentration Response Coefficients",
        rows=rows,
        columns=columns,
        xlabel=xlabel,
        ylabel=ylabel,
        annotate=annotate,
        colorbar=colorbar,
        cmap=cmap,
        vmax=vmax,
        vmin=vmin,
        ax=ax,
        cax=cax,
    )


def plot_flux_response_coefficients(
    model: Model,
    parameters: List[str],
    y: Dict[str, float],
    normalized: bool = True,
    displacement: float = _DISPLACEMENT,
    cmap: str = "RdBu_r",
    rows: int = None,
    columns: int = None,
    vmax: float = None,
    vmin: float = None,
    annotate: bool = True,
    colorbar: bool = True,
    xlabel: str = None,
    ylabel: str = None,
    ax: plt.Axes = None,
    cax: plt.Axes = None,
) -> Tuple[Figure, plt.Axes, QuadMesh]:
    """Calculate and plot response of the steady state fluxes to a change of the given parameters.

    See also
    --------
    get_flux_response_coefficients_df
    plot_coefficient_heatmap
    """
    df = get_flux_response_coefficients_df(
        model=model,
        parameters=parameters,
        y=y,
        normalized=normalized,
        displacement=displacement,
    )
    return plot_coefficient_heatmap(
        df=df,
        title="Flux Response Coefficients",
        rows=rows,
        columns=columns,
        xlabel=xlabel,
        ylabel=ylabel,
        annotate=annotate,
        colorbar=colorbar,
        cmap=cmap,
        vmax=vmax,
        vmin=vmin,
        ax=ax,
        cax=cax,
    )
