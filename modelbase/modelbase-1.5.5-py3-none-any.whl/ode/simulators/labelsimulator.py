from __future__ import annotations

__all__ = [
    "_LabelSimulate",
]

import re
from typing import Any, Dict, Iterable, List, Optional, Tuple, Type, Union, cast

import matplotlib as plt
import numpy as np
import numpy.typing as npt
import pandas as pd
from matplotlib.figure import Figure

from ...utils.plotting import plot, plot_grid
from ..integrators import AbstractIntegrator
from ..models import LabelModel
from .abstract_simulator import _BaseRateSimulator


class _LabelSimulate(_BaseRateSimulator[LabelModel]):
    """Simulator for LabelModels."""

    def __init__(
        self,
        model: LabelModel,
        integrator: Type[AbstractIntegrator],
        y0: Optional[List[float]] = None,
        time: Optional[List[npt.NDArray[np.float64]]] = None,
        results: Optional[List[npt.NDArray[np.float64]]] = None,
        parameters: List[Dict[str, float]] = None,
    ) -> None:
        super().__init__(
            model=model,
            integrator=integrator,
            y0=y0,
            time=time,
            results=results,
            parameters=parameters,
        )

    def generate_y0(
        self,
        base_y0: Union[List[float], Dict[str, float]],
        label_positions: Dict[str, Union[int, List[int]]],
    ) -> Dict[str, float]:
        """Generate y0 for all isotopomers given a base y0.

        Examples
        --------
        >>> base_y0 = {"GAP": 1, "DHAP": 0, "FBP": 0}
        >>> generate_y0(base_y0=base_y0, label_positions={"GAP": 0})
        {"GAP__100": 1, "DHAP__000": 1, "FBP__000000": 1}  # excluding the zeros
        """
        return self.model.generate_y0(base_y0=base_y0, label_positions=label_positions)

    def get_total_concentration(self, compound: str) -> Optional[npt.NDArray[np.float64]]:
        """Get the total concentration of all isotopomers of a compound."""
        res = self.get_full_results_dict(concatenated=True)
        if res is None:
            return None
        return cast(Dict[str, npt.NDArray[np.float64]], res)[compound + "__total"]

    def get_unlabeled_concentration(self, compound: str) -> Optional[npt.NDArray[np.float64]]:
        """Get the concentration of an isotopomer that is unlabeled."""
        carbons = "0" * self.model.label_compounds[compound]["num_labels"]
        res = self.get_full_results_dict()
        if res is None:
            return None
        return cast(Dict[str, npt.NDArray[np.float64]], res)[compound + f"__{carbons}"]

    def get_total_label_concentration(self, compound: str) -> Optional[npt.NDArray[np.float64]]:
        """Get the total concentration of all labeled isotopomers of a compound."""
        total = self.get_total_concentration(compound=compound)
        unlabeled = self.get_unlabeled_concentration(compound=compound)
        if total is None or unlabeled is None:
            return None
        return cast(npt.NDArray[np.float64], total - unlabeled)

    def get_all_isotopomer_concentrations_array(self, compound: str) -> Optional[npt.NDArray[np.float64]]:
        """Get concentrations of all isotopomers of a compound."""
        res = self.get_all_isotopomer_concentrations_df(compound=compound)
        if res is None:
            return None
        return cast(npt.NDArray[np.float64], res.values)

    def get_all_isotopomer_concentrations_dict(
        self, compound: str
    ) -> Optional[Dict[str, npt.NDArray[np.float64]]]:
        """Get concentrations of all isotopomers of a compound."""
        res = self.get_all_isotopomer_concentrations_df(compound=compound)
        if res is None:
            return None
        return dict(
            zip(
                res.columns,
                res.values.T,  # type: ignore
            )
        )

    def get_all_isotopomer_concentrations_df(self, compound: str) -> Optional[pd.Series]:
        """Get concentrations of all isotopomers of a compound."""
        isotopomers = self.model.get_compound_isotopomers(compound=compound)
        df = self.get_results_df()
        if isotopomers is None or df is None:
            return None
        df = cast(pd.DataFrame, df)[isotopomers]
        return cast(pd.Series, df[isotopomers])

    def get_concentrations_by_reg_exp_array(self, reg_exp: str) -> Optional[npt.NDArray[np.float64]]:
        """Get concentrations of all isotopomers matching the regular expression."""
        isotopomers = [i for i in self.model.get_compounds() if re.match(reg_exp, i)]
        df = self.get_results_df()
        if isotopomers is None or df is None:
            return None
        df = cast(pd.DataFrame, df)[isotopomers]
        return cast(npt.NDArray[np.float64], df[isotopomers].values)

    def get_concentrations_by_reg_exp_dict(
        self, reg_exp: str
    ) -> Optional[Dict[str, npt.NDArray[np.float64]]]:
        """Get concentrations of all isotopomers of a compound."""
        isotopomers = [i for i in self.model.get_compounds() if re.match(reg_exp, i)]
        df = self.get_results_df(concatenated=True)
        if isotopomers is None or df is None:
            return None
        df = cast(pd.DataFrame, df)[isotopomers]
        return dict(zip(df.columns, df.values.T))

    def get_concentrations_by_reg_exp_df(self, reg_exp: str) -> Optional[pd.DataFrame]:
        """Get concentrations of all isotopomers of a compound."""
        isotopomers = [i for i in self.model.get_compounds() if re.match(reg_exp, i)]
        df = self.get_results_df(concatenated=True)
        if isotopomers is None:
            return None
        df = cast(pd.DataFrame, df)[isotopomers]
        return df[isotopomers]

    def get_concentration_at_positions(
        self, compound: str, positions: Union[int, List[int]]
    ) -> Optional[npt.NDArray[np.float64]]:
        """Get concentration of an isotopomer labelled at certain position(s)."""
        if isinstance(positions, int):
            positions = [positions]
        num_labels = self.model.label_compounds[compound]["num_labels"]
        label_positions = ["[01]"] * num_labels
        for position in positions:
            label_positions[position] = "1"
        reg_exp = f"{compound}__{''.join(label_positions)}"
        res = self.get_concentrations_by_reg_exp_array(reg_exp=reg_exp)
        if res is None:
            return None
        return cast(npt.NDArray[np.float64], np.sum(res, axis=1))

    def get_concentrations_of_n_labeled_array(
        self, compound: str, n_labels: int
    ) -> Optional[npt.NDArray[np.float64]]:
        """Get concentrations of all isotopomers that carry n labels."""
        res = self.get_concentrations_of_n_labeled_df(compound=compound, n_labels=n_labels)
        if res is None:
            return None
        return cast(npt.NDArray[np.float64], res.values)

    def get_concentrations_of_n_labeled_dict(
        self, compound: str, n_labels: int
    ) -> Optional[Dict[str, npt.NDArray[np.float64]]]:
        """Get concentrations of all isotopomers that carry n labels."""
        df = self.get_concentrations_of_n_labeled_df(compound=compound, n_labels=n_labels)
        if df is None:
            return None
        return dict(zip(df.columns, df.values.T))

    def get_concentrations_of_n_labeled_df(self, compound: str, n_labels: int) -> Optional[pd.DataFrame]:
        """Get concentrations of all isotopomers that carry n labels."""
        isotopomers = self.model.get_compound_isotopomers_with_n_labels(
            compound=compound,
            n_labels=n_labels,
        )
        res = self.get_results_df(concatenated=True)
        if res is None:
            return None
        return cast(pd.DataFrame, res)[isotopomers]

    def plot(
        self,
        xlabel: str = None,
        ylabel: str = None,
        title: str = None,
        grid: bool = True,
        tight_layout: bool = True,
        ax: plt.Axes = None,
        figure_kwargs: Dict[str, Any] = None,
        subplot_kwargs: Dict[str, Any] = None,
        plot_kwargs: Dict[str, Any] = None,
        grid_kwargs: Dict[str, Any] = None,
        legend_kwargs: Dict[str, Any] = None,
        tick_kwargs: Dict[str, Any] = None,
        label_kwargs: Dict[str, Any] = None,
        title_kwargs: Dict[str, Any] = None,
    ) -> Tuple[Optional[Figure], Optional[plt.Axes]]:
        """Plot all total concentrations."""
        compounds = sorted(
            [f"{i}__total" for i in self.model.label_compounds] + self.model.nonlabel_compounds
        )
        y = self.get_full_results_df(concatenated=True)
        if y is None:
            return None, None
        y = cast(pd.DataFrame, y).loc[:, compounds]
        return plot(
            plot_args=(y,),
            legend=None,
            xlabel=xlabel,
            ylabel=ylabel,
            title=title,
            grid=grid,
            tight_layout=tight_layout,
            ax=ax,
            figure_kwargs=figure_kwargs,
            subplot_kwargs=subplot_kwargs,
            plot_kwargs=plot_kwargs,
            grid_kwargs=grid_kwargs,
            legend_kwargs=legend_kwargs,
            tick_kwargs=tick_kwargs,
            label_kwargs=label_kwargs,
            title_kwargs=title_kwargs,
        )

    def _calculate_label_distribution(
        self, *, compound: str, relative: bool
    ) -> Optional[npt.NDArray[np.float64]]:
        """Calculate the label distribution of a compound."""
        total_concentration = self.get_total_concentration(compound=compound)
        if total_concentration is None:
            return None
        concentrations = []
        for position in range(self.model.get_compound_number_of_label_positions(compound=compound)):
            concentration = self.get_concentration_at_positions(compound=compound, positions=position)
            if concentration is None:
                return None
            if relative:
                concentration = concentration / total_concentration
            concentrations.append(concentration)
        return np.array(concentrations).T

    def plot_label_distribution(
        self,
        compound: str,
        relative: bool = True,
        xlabel: str = None,
        ylabel: str = None,
        title: str = None,
        grid: bool = True,
        tight_layout: bool = True,
        ax: plt.Axes = None,
        figure_kwargs: Dict[str, Any] = None,
        subplot_kwargs: Dict[str, Any] = None,
        plot_kwargs: Dict[str, Any] = None,
        grid_kwargs: Dict[str, Any] = None,
        legend_kwargs: Dict[str, Any] = None,
        tick_kwargs: Dict[str, Any] = None,
        label_kwargs: Dict[str, Any] = None,
        title_kwargs: Dict[str, Any] = None,
    ) -> Tuple[Optional[Figure], Optional[plt.Axes]]:
        """Plot label distribution of a compound."""
        if ylabel is None and relative:
            ylabel = "Relative concentration"
        x = self.get_time()
        y = self._calculate_label_distribution(compound=compound, relative=relative)
        if x is None or y is None:
            return None, None
        return plot(
            plot_args=(x, y),
            legend=None,
            xlabel=xlabel,
            ylabel=ylabel,
            title=title,
            grid=grid,
            tight_layout=tight_layout,
            ax=ax,
            figure_kwargs=figure_kwargs,
            subplot_kwargs=subplot_kwargs,
            plot_kwargs=plot_kwargs,
            grid_kwargs=grid_kwargs,
            legend_kwargs=legend_kwargs,
            tick_kwargs=tick_kwargs,
            label_kwargs=label_kwargs,
            title_kwargs=title_kwargs,
        )

    def plot_label_distribution_grid(
        self,
        compounds: List[str],
        relative: bool = True,
        ncols: Optional[int] = None,
        sharex: bool = True,
        sharey: bool = True,
        xlabels: Optional[Union[str, List[str]]] = None,
        ylabels: Optional[Union[str, List[str]]] = None,
        plot_titles: Optional[Iterable[str]] = None,
        figure_title: Optional[str] = None,
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
    ) -> Tuple[Optional[Figure], Optional[npt.NDArray[np.float64]]]:
        """Plot label distributions of multiple compounds on a grid."""
        time = self.get_time()
        if time is None:
            return None, None
        plot_groups = [
            (
                time,
                self._calculate_label_distribution(compound=compound, relative=relative),
            )
            for compound in compounds
        ]
        legend_groups = [
            [f"Pos {i}" for i in range(self.model.get_compound_number_of_label_positions(compound=compound))]
            for compound in compounds
        ]
        if ylabels is None and relative:
            ylabels = "Relative concentration"
        if plot_titles is None:
            plot_titles = compounds
        return plot_grid(
            plot_groups=plot_groups,  # type: ignore
            legend_groups=legend_groups,
            ncols=ncols,
            sharex=sharex,
            sharey=sharey,
            xlabels=xlabels,
            ylabels=ylabels,
            figure_title=figure_title,
            plot_titles=plot_titles,
            grid=grid,
            tight_layout=tight_layout,
            figure_kwargs=figure_kwargs,
            subplot_kwargs=subplot_kwargs,
            plot_kwargs=plot_kwargs,
            grid_kwargs=grid_kwargs,
            legend_kwargs=legend_kwargs,
            tick_kwargs=tick_kwargs,
            label_kwargs=label_kwargs,
            title_kwargs=title_kwargs,
        )

    def plot_all_label_distributions(
        self,
        relative: bool = True,
        ncols: Optional[int] = None,
        sharex: bool = True,
        sharey: bool = True,
        xlabels: Optional[Union[str, List[str]]] = None,
        ylabels: Optional[Union[str, List[str]]] = None,
        plot_titles: Optional[Iterable[str]] = None,
        figure_title: Optional[str] = None,
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
    ) -> Tuple[Optional[Figure], Optional[npt.NDArray[np.float64]]]:
        """Plot label distributions of all compounds on a grid."""
        time = self.get_time()
        if time is None:
            return None, None
        base_compounds = self.model.label_compounds
        plot_groups = [
            (
                time,
                self._calculate_label_distribution(compound=compound, relative=relative),
            )
            for compound in base_compounds
        ]
        legend_groups = [
            [f"Pos {i}" for i in range(self.model.get_compound_number_of_label_positions(compound=compound))]
            for compound in base_compounds
        ]
        if ylabels is None and relative:
            ylabels = "Relative concentration"

        return plot_grid(
            plot_groups=plot_groups,  # type: ignore
            legend_groups=legend_groups,
            ncols=ncols,
            sharex=sharex,
            sharey=sharey,
            xlabels=xlabels,
            ylabels=ylabels,
            figure_title=figure_title,
            plot_titles=plot_titles,
            grid=grid,
            tight_layout=tight_layout,
            figure_kwargs=figure_kwargs,
            subplot_kwargs=subplot_kwargs,
            plot_kwargs=plot_kwargs,
            grid_kwargs=grid_kwargs,
            legend_kwargs=legend_kwargs,
            tick_kwargs=tick_kwargs,
            label_kwargs=label_kwargs,
            title_kwargs=title_kwargs,
        )
