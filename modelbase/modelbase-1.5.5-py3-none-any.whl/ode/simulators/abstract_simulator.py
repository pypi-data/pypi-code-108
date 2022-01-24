from __future__ import annotations

__all__ = [
    "_BaseSimulator",
    "_BaseRateSimulator",
]

import copy
import json
import pickle
import sys
import warnings
from abc import ABC, abstractmethod
from concurrent import futures
from functools import partial
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    Union,
    cast,
)

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import pandas as pd
from matplotlib.figure import Figure
from tqdm.auto import tqdm

from ...typing import Axes
from ...utils.plotting import _get_plot_kwargs, _style_subplot, plot, plot_grid
from ..integrators import AbstractIntegrator
from . import BASE_MODEL_TYPE, RATE_MODEL_TYPE


class _BaseSimulator(Generic[BASE_MODEL_TYPE], ABC):
    def __init__(
        self,
        model: BASE_MODEL_TYPE,
        integrator: Type[AbstractIntegrator],
        y0: Optional[List[float]] = None,
        time: Optional[List[npt.NDArray[np.float64]]] = None,
        results: Optional[List[npt.NDArray[np.float64]]] = None,
    ) -> None:
        self.model = model
        self._integrator = integrator
        self.integrator: Optional[AbstractIntegrator] = None

        # For restoring purposes
        self.y0 = y0
        self.time = time
        self.results = results

    def __reduce__(self) -> Any:
        """Pickle this class."""
        return (
            self.__class__,
            (
                self.model,
                self._integrator,
            ),
            (
                ("y0", self.y0),
                ("time", self.time),
                ("results", self.results),
            ),
        )

    def clear_results(self) -> None:
        """Clear simulation results."""
        self.time = None
        self.results = None
        if self.integrator is not None:
            self.integrator.reset()

    def _initialise_integrator(self, *, y0: Union[npt.NDArray[np.float64], List[float]]) -> None:
        """Initialise the integrator.

        Required for assimulo, as it needs y0 to initialise
        """
        self.integrator = self._integrator(rhs=self.model._get_rhs, y0=y0)

    def get_integrator_params(self) -> Optional[Dict[str, Any]]:
        if self.integrator is None:
            return None
        return self.integrator.get_integrator_kwargs()

    @abstractmethod
    def copy(self) -> Any:
        """Create a copy."""

    def _normalise_split_array(
        self,
        *,
        split_array: List[npt.NDArray[np.float64]],
        normalise: Union[float, List[float]],
    ) -> List[npt.NDArray[np.float64]]:
        if isinstance(normalise, (int, float)):
            return [i / normalise for i in split_array]
        if len(normalise) == len(split_array):
            return [i / np.reshape(j, (len(i), 1)) for i, j in zip(split_array, normalise)]

        results = []
        start = 0
        end = 0
        for i in split_array:
            end += len(i)
            results.append(i / np.reshape(normalise[start:end], (len(i), 1)))
            start += end
        return results

    @abstractmethod
    def _test_run(self) -> None:
        """Perform a test step of the simulation in Python to get proper error handling."""

    def _save_simulation_results(
        self, *, time: npt.NDArray[np.float64], results: npt.NDArray[np.float64], skipfirst: bool
    ) -> None:
        if self.time is None or self.results is None:
            self.time = [time]
            self.results = [results]
        else:  # Continuous simulation
            if skipfirst:
                self.time.append(time[1:])
                self.results.append(results[1:, :])
            else:
                self.time.append(time)
                self.results.append(results)

    def get_time(
        self, concatenated: bool = True
    ) -> Union[None, npt.NDArray[np.float64], List[npt.NDArray[np.float64]]]:
        """Get simulation time.

        Returns
        -------
        time : numpy.array
        """
        if self.time is None:
            return None
        if concatenated:
            return np.concatenate(self.time, axis=0)  # type: ignore
        return self.time.copy()

    def simulate(
        self,
        t_end: float = None,
        steps: int = None,
        time_points: List[float] = None,
        **integrator_kwargs: Dict[str, Any],
    ) -> Tuple[Optional[npt.NDArray[np.float64]], Optional[npt.NDArray[np.float64]]]:
        """Simulate the model."""
        if self.integrator is None:
            raise AttributeError("Initialise the simulator first.")

        if steps is not None and time_points is not None:
            warnings.warn(
                """
            You can either specify the steps or the time return points.
            I will use the time return points"""
            )
            if t_end is None:
                t_end = time_points[-1]
            time, results = self.integrator._simulate(
                t_end=t_end,
                time_points=time_points,
                **integrator_kwargs,  # type: ignore
            )
        elif time_points is not None:
            time, results = self.integrator._simulate(
                t_end=time_points[-1],
                time_points=time_points,
                **integrator_kwargs,  # type: ignore
            )
        elif steps is not None:
            if t_end is None:
                raise ValueError("t_end must no be None")
            time, results = self.integrator._simulate(
                t_end=t_end,
                steps=steps,
                **integrator_kwargs,  # type: ignore
            )
        else:
            time, results = self.integrator._simulate(
                t_end=t_end,
                **integrator_kwargs,  # type: ignore
            )

        if time is None or results is None:
            return None, None
        time_array = np.array(time)
        results_array = np.array(results)
        self._save_simulation_results(time=time_array, results=results_array, skipfirst=True)
        return time_array, results_array

    def simulate_to_steady_state(
        self,
        tolerance: float = 1e-6,
        simulation_kwargs: Dict[str, Any] = None,
        **integrator_kwargs: Dict[str, Any],
    ) -> Tuple[Optional[npt.NDArray[np.float64]], Optional[npt.NDArray[np.float64]]]:
        """Simulate the model."""
        if self.integrator is None:
            raise AttributeError("Initialise the simulator first.")
        if simulation_kwargs is None:
            simulation_kwargs = {}
        time, results = self.integrator._simulate_to_steady_state(
            tolerance=tolerance,
            simulation_kwargs=simulation_kwargs,
            integrator_kwargs=integrator_kwargs,
        )
        if time is None or results is None:
            return None, None
        time_array = np.array([time])
        results_array = np.array([results])
        self._save_simulation_results(time=time_array, results=results_array, skipfirst=False)
        return time_array, results_array

    def get_results_array(
        self,
        normalise: Union[float, List[float]] = None,
        concatenated: bool = True,
    ) -> Union[None, npt.NDArray[np.float64], List[npt.NDArray[np.float64]]]:
        """Get simulation results."""
        if self.results is None:
            return None

        results = self.results.copy()
        if normalise is not None:
            results = self._normalise_split_array(split_array=results, normalise=normalise)
        if concatenated:
            return np.concatenate(results, axis=0)  # type: ignore
        return results

    def get_results_dict(
        self,
        normalise: Union[float, List[float]] = None,
        concatenated: bool = True,
    ) -> Union[None, Dict[str, npt.NDArray[np.float64]], List[Dict[str, npt.NDArray[np.float64]]]]:
        """Get simulation results."""
        results = self.get_results_array(normalise=normalise, concatenated=concatenated)
        if results is None:
            return None
        if concatenated:
            results = cast(npt.NDArray[np.float64], results)  # this is just a typing annotation
            return dict(zip(self.model.get_compounds(), results.T))
        results = cast(List[npt.NDArray[np.float64]], results)  # this is just a typing annotation
        return [dict(zip(self.model.get_compounds(), i.T)) for i in results]

    def get_results_df(
        self,
        normalise: Union[float, List[float]] = None,
        concatenated: bool = True,
    ) -> Union[None, pd.DataFrame, List[pd.DataFrame]]:
        """Get simulation results."""
        results = self.get_results_array(normalise=normalise, concatenated=concatenated)
        time = self.get_time(concatenated=concatenated)
        if results is None or time is None:
            return None
        if concatenated:
            return pd.DataFrame(
                data=results,
                index=self.get_time(),
                columns=self.model.get_compounds(),
            )
        return [
            pd.DataFrame(
                data=result,
                index=t,
                columns=self.model.get_compounds(),
            )
            for t, result in zip(time, results)
        ]

    def store_results_to_file(self, filename: str, filetype: str = "json") -> None:
        """Store the simulation results into a json or pickle file.

        Parameters
        ----------
        filename
            The name of the pickle file
        filetype
            Output file type. Json or pickle.
        """
        if self.time is None or self.results is None:
            raise ValueError("Cannot save results, since none are stored in the simulator")

        res = cast(
            Dict[str, npt.NDArray[np.float64]], self.get_results_dict(concatenated=True)
        )  # cast is just typing annotation
        time = cast(
            npt.NDArray[np.float64], self.get_time(concatenated=True)
        )  # cast is just typing annotation
        res["time"] = time

        res = {k: v.tolist() for k, v in res.items()}
        if filetype == "json":
            if not filename.endswith(".json"):
                filename += ".json"
            with open(filename, "w") as f:
                json.dump(obj=res, fp=f)
        elif filetype == "pickle":
            if not filename.endswith(".p"):
                filename += ".p"
            with open(filename, "wb") as f:  # type: ignore
                pickle.dump(obj=res, file=f)  # type: ignore
        else:
            raise ValueError("Can only save to json or pickle")

    def load_results_from_file(self, filename: str, filetype: str = "json") -> None:
        """Load simulation results from a json or pickle file.

        Parameters
        ----------
        filename
            The name of the pickle file
        filetype
            Input file type. Json or pickle.
        """
        if filetype == "json":
            with open(filename, "r") as f:
                res: Dict[str, npt.NDArray[np.float64]] = json.load(fp=f)
        elif filetype == "pickle":
            with open(filename, "rb") as f:  # type: ignore
                res = pickle.load(file=f)  # type: ignore
        else:
            raise ValueError("Can only save to json or pickle")
        res = {k: np.array(v) for k, v in res.items()}
        self.time = [res.pop("time")]
        cpds = np.array([v for k, v in res.items()]).reshape(
            (len(self.time[0]), len(self.model.get_compounds()))
        )
        self.results = [cpds]


class _BaseRateSimulator(Generic[RATE_MODEL_TYPE], _BaseSimulator[RATE_MODEL_TYPE]):  # type: ignore
    def __init__(
        self,
        model: RATE_MODEL_TYPE,
        integrator: Type[AbstractIntegrator],
        y0: Optional[List[float]] = None,
        time: Optional[List[npt.NDArray[np.float64]]] = None,
        results: Optional[List[npt.NDArray[np.float64]]] = None,
        parameters: List[Dict[str, float]] = None,
    ) -> None:
        _BaseSimulator.__init__(self, model=model, integrator=integrator, y0=y0, time=time, results=results)
        self.full_results: Optional[List[npt.NDArray[np.float64]]] = None
        self.fluxes: Optional[List[npt.NDArray[np.float64]]] = None
        self.simulation_parameters = parameters

    def __reduce__(self) -> Any:
        """Pickle this class."""
        return (
            self.__class__,
            (
                self.model,
                self._integrator,
            ),
            (
                ("y0", self.y0),
                ("time", self.time),
                ("results", self.results),
                ("parameters", self.simulation_parameters),
            ),
        )

    def copy(self) -> Any:
        """Return a deepcopy of this class."""
        new = copy.deepcopy(self)
        if self.simulation_parameters is not None:
            new.simulation_parameters = self.simulation_parameters.copy()
        if new.results is not None:
            new._initialise_integrator(y0=new.results[-1])
        elif new.y0 is not None:
            new.initialise(y0=new.y0, test_run=False)
        return new

    def clear_results(self) -> None:
        """Clear simulation results."""
        super().clear_results()
        self.full_results = None
        self.fluxes = None
        self.simulation_parameters = None

    def _test_run(self) -> None:
        """Test run of a single integration step to get proper error handling."""
        if not self.model.rates:
            raise AttributeError("Please set at least one rate for the integration")

        if self.y0 is not None:
            y = self.model.get_full_concentration_dict(y=self.y0, t=0)
            self.model.get_fluxes_dict(y=y, t=0)
            self.model.get_right_hand_side(y=y, t=0)

    def initialise(
        self,
        y0: Union[List[float], npt.NDArray[np.float64], Dict[str, float]],
        test_run: bool = True,
    ) -> None:
        """Initialise the integrator."""
        if self.results is not None:
            self.clear_results()
        if isinstance(y0, dict):
            self.y0 = [y0[compound] for compound in self.model.get_compounds()]
        else:
            self.y0 = list(y0)
        self._initialise_integrator(y0=self.y0)

        if test_run:
            self._test_run()

    def update_parameter(self, parameter_name: str, parameter_value: float) -> None:
        """Update a model parameter."""
        self.model.update_parameter(parameter_name=parameter_name, parameter_value=parameter_value)

    def update_parameters(self, parameters: Dict[str, float]) -> None:
        """Update model parameters."""
        self.model.update_parameters(parameters=parameters)

    def _save_simulation_results(
        self, *, time: npt.NDArray[np.float64], results: npt.NDArray[np.float64], skipfirst: bool
    ) -> None:
        super()._save_simulation_results(time=time, results=results, skipfirst=skipfirst)
        if self.simulation_parameters is None:
            self.simulation_parameters = []
        self.simulation_parameters.append(self.model.parameters.copy())

    def simulate(
        self,
        t_end: Optional[float] = None,
        steps: Optional[int] = None,
        time_points: Optional[List[float]] = None,
        **integrator_kwargs: Dict[str, Any],
    ) -> Tuple[Optional[npt.NDArray[np.float64]], Optional[npt.NDArray[np.float64]]]:
        """Simulate the model.

        You can either supply only a terminal time point, or additionally also the
        number of steps or exact time points for which values should be returned.

        Parameters
        ----------
        t_end
            Last point of the integration
        steps
            Number of integration time steps to be returned
        time_points
            Explicit time points which shall be returned
        integrator_kwargs : dict
            Integrator options
        """
        self.model._update_derived_parameters()
        time, results = super().simulate(
            t_end=t_end,
            steps=steps,
            time_points=time_points,
            **integrator_kwargs,
        )
        self.full_results = None
        self.fluxes = None
        return time, results

    def simulate_to_steady_state(
        self,
        tolerance: float = 1e-8,
        simulation_kwargs: Dict[str, Any] = None,
        **integrator_kwargs: Dict[str, Any],
    ) -> Tuple[Optional[npt.NDArray[np.float64]], Optional[npt.NDArray[np.float64]]]:
        """Simulate the model to steady state."""
        self.model._update_derived_parameters()
        time, results = super().simulate_to_steady_state(
            tolerance=tolerance,
            simulation_kwargs=simulation_kwargs,
            **integrator_kwargs,
        )
        self.full_results = None
        self.fluxes = None
        return time, results

    def _calculate_fluxes(self) -> None:
        if any((i is None for i in [self.time, self.results, self.simulation_parameters])):
            pass
        else:
            fluxes = []
            for t, y, pars in zip(
                cast(List[npt.NDArray[np.float64]], self.time),
                cast(List[npt.NDArray[np.float64]], self.results),
                cast(List[Dict[str, float]], self.simulation_parameters),
            ):
                self.update_parameters(parameters=pars)
                fluxes_array = self.model.get_fluxes_array(y=y, t=t)
                fluxes.append(fluxes_array)
            self.fluxes = fluxes

    def get_fluxes_array(
        self,
        normalise: Union[float, List[float]] = None,
        concatenated: bool = True,
    ) -> Optional[Union[npt.NDArray[np.float64], List[npt.NDArray[np.float64]]]]:
        """Get the model fluxes for the simulation."""
        if self.time is None or self.results is None:
            return None
        if self.fluxes is None:
            self._calculate_fluxes()
        fluxes = cast(List[npt.NDArray[np.float64]], self.fluxes)
        if normalise is not None:
            fluxes = self._normalise_split_array(split_array=fluxes, normalise=normalise)
        if concatenated:
            return np.concatenate(fluxes, axis=0)  # type: ignore
        return fluxes

    def get_fluxes_dict(
        self,
        normalise: Union[float, List[float]] = None,
        concatenated: bool = True,
    ) -> Optional[Union[Dict[str, npt.NDArray[np.float64]], List[Dict[str, npt.NDArray[np.float64]]]]]:
        """Get the model fluxes for the simulation."""
        fluxes = self.get_fluxes_array(normalise=normalise, concatenated=concatenated)
        if fluxes is None:
            return None
        if concatenated:
            return dict(zip(self.model.rates, cast(npt.NDArray[np.float64], fluxes).T))
        return [dict(zip(self.model.rates, i.T)) for i in fluxes]

    def get_fluxes_df(
        self,
        normalise: Union[float, List[float]] = None,
        concatenated: bool = True,
    ) -> Optional[Union[pd.DataFrame, List[pd.DataFrame]]]:
        """Get the model fluxes for the simulation."""
        fluxes = self.get_fluxes_array(normalise=normalise, concatenated=concatenated)
        time = self.get_time(concatenated=concatenated)
        if fluxes is None or time is None:
            return None
        if concatenated:
            return pd.DataFrame(
                data=fluxes,
                index=self.get_time(),
                columns=self.model.get_rate_names(),
            )
        return [
            pd.DataFrame(
                data=flux,
                index=t,
                columns=self.model.get_rate_names(),
            )
            for t, flux in zip(time, fluxes)
        ]

    def _calculate_full_results(self) -> None:
        full_results = []
        for t, y, p in zip(self.time, self.results, self.simulation_parameters):  # type: ignore
            self.update_parameters(parameters=p)
            results = self.model.get_full_concentration_dict(y=y, t=t)
            del results["time"]
            full_results.append(np.reshape(list(results.values()), (len(results), len(t))).T)  # type: ignore
        self.full_results = full_results

    def get_full_results_array(
        self,
        normalise: Union[float, List[float]] = None,
        concatenated: bool = True,
    ) -> Optional[Union[npt.NDArray[np.float64], List[npt.NDArray[np.float64]]]]:
        """Get simulation results and derived compounds.

        Returns
        -------
        results : numpy.array
        """
        if self.results is None or self.time is None:
            return None
        if self.full_results is None:
            self._calculate_full_results()
        full_results = cast(List[npt.NDArray[np.float64]], self.full_results).copy()
        if normalise is not None:
            full_results = self._normalise_split_array(
                split_array=full_results,
                normalise=normalise,
            )
        if concatenated:
            return np.concatenate(full_results, axis=0)  # type: ignore
        return full_results

    def get_full_results_dict(
        self,
        normalise: Union[float, List[float]] = None,
        concatenated: bool = True,
    ) -> Optional[Union[Dict[str, npt.NDArray[np.float64]], List[Dict[str, npt.NDArray[np.float64]]]]]:
        """Get simulation results and derived compounds."""
        full_results = self.get_full_results_array(normalise=normalise, concatenated=concatenated)
        if full_results is None:
            return None
        all_compounds = self.model.get_all_compounds()
        if concatenated:
            return dict(zip(all_compounds, cast(npt.NDArray[np.float64], full_results).T))
        return [dict(zip(all_compounds, i.T)) for i in full_results]

    def get_full_results_df(
        self,
        normalise: Union[float, List[float]] = None,
        concatenated: bool = True,
    ) -> Optional[Union[pd.DataFrame, List[pd.DataFrame]]]:
        """Get simulation results and derived compounds."""
        full_results = self.get_full_results_array(normalise=normalise, concatenated=concatenated)
        time = self.get_time(concatenated=concatenated)
        if full_results is None or time is None:
            return None
        all_compounds = self.model.get_all_compounds()

        if concatenated:
            return pd.DataFrame(data=full_results, index=time, columns=all_compounds)
        return [pd.DataFrame(data=res, index=t, columns=all_compounds) for t, res in zip(time, full_results)]

    def get_variable(
        self,
        variable: str,
        normalise: Union[float, List[float]] = None,
        concatenated: bool = True,
    ) -> Optional[Union[npt.NDArray[np.float64], List[npt.NDArray[np.float64]]]]:
        """Get simulation results for a specific variable.

        Returns
        -------
        results : numpy.array
        """
        full_results_dict = self.get_full_results_dict(normalise=normalise, concatenated=concatenated)
        if full_results_dict is None:
            return None
        if concatenated:
            return cast(Dict[str, npt.NDArray[np.float64]], full_results_dict)[variable]
        return [i[variable] for i in cast(List[Dict[str, npt.NDArray[np.float64]]], full_results_dict)]

    def get_variables(
        self,
        variables: List[str],
        normalise: Union[float, List[float]] = None,
        concatenated: bool = True,
    ) -> Union[npt.NDArray[np.float64], List[npt.NDArray[np.float64]]]:
        """Get simulation results for a specific variable."""
        full_results_df = self.get_full_results_df(normalise=normalise, concatenated=concatenated)
        if concatenated:
            full_results_df = cast(pd.DataFrame, full_results_df)
            return full_results_df.loc[:, variables].values  # type: ignore
        full_results_df = cast(List[pd.DataFrame], full_results_df)
        return [i.loc[:, variables].values for i in full_results_df]

    @staticmethod
    def _parameter_scan_worker(
        parameter_value: float,
        *,
        parameter_name: str,
        model: RATE_MODEL_TYPE,
        Sim: Type[_BaseRateSimulator],
        integrator: Type[AbstractIntegrator],
        tolerance: float,
        y0: Dict[str, float],
        integrator_kwargs: Dict[str, Any],
        include_fluxes: bool,
    ) -> Tuple[float, Dict[str, float], Dict[str, float]]:
        m = model.copy()
        s = Sim(model=m, integrator=integrator)
        s.initialise(y0=y0, test_run=False)
        s.update_parameter(parameter_name=parameter_name, parameter_value=parameter_value)
        t, y = s.simulate_to_steady_state(tolerance=tolerance, **integrator_kwargs)
        if t is None or y is None:
            concentrations = dict(zip(m.get_all_compounds(), np.full(len(m.get_all_compounds()), np.NaN)))
            fluxes = dict(zip(m.get_rate_names(), np.full(len(m.get_rate_names()), np.NaN)))
            return parameter_value, concentrations, fluxes
        if include_fluxes:
            fluxes = dict(s.get_fluxes_df(concatenated=True).iloc[-1])  # type: ignore
        else:
            fluxes = {}
        concentrations = dict(s.get_full_results_df(concatenated=True).iloc[-1])  # type: ignore
        return parameter_value, concentrations, fluxes  # type: ignore

    def _scan_threading(self, parameter_name: str, parameter_values: list[float], worker: Callable) -> list:
        with tqdm(total=len(parameter_values), desc=parameter_name) as pbar:
            results = []
            for value in parameter_values:
                results.append(worker(value))
                pbar.update(1)
        return results

    def _scan_multiprocessing(
        self, parameter_name: str, parameter_values: list[float], worker: Callable
    ) -> list:
        with tqdm(total=len(parameter_values), desc=parameter_name) as pbar:
            with futures.ProcessPoolExecutor() as executor:
                results = []
                for task in futures.as_completed((executor.submit(worker, i) for i in parameter_values)):
                    results.append(task.result())
                    pbar.update(1)
        return results

    def parameter_scan(
        self,
        parameter_name: str,
        parameter_values: List[float],
        tolerance: float = 1e-8,
        multiprocessing: bool = True,
        **integrator_kwargs: Dict[str, Any],
    ) -> pd.DataFrame:
        """Scan the model steady state changes caused by a change to a parameter."""
        if sys.platform in ["win32", "cygwin"]:
            warnings.warn(
                """
                Windows does not behave well with multiple processes.
                Falling back to threading routine."""
            )
        worker = partial(
            self._parameter_scan_worker,
            **{
                "parameter_name": parameter_name,
                "model": self.model,
                "Sim": self.__class__,
                "integrator": self._integrator,
                "tolerance": tolerance,
                "y0": self.y0,
                "integrator_kwargs": integrator_kwargs,
                "include_fluxes": False,
            },
        )
        if sys.platform in ["win32", "cygwin"] or not multiprocessing:
            results = self._scan_threading(parameter_name, parameter_values, worker)
        else:
            results = self._scan_multiprocessing(parameter_name, parameter_values, worker)
        concentrations = {}
        for (i, conc, _) in results:
            concentrations[i] = conc
        return pd.DataFrame(concentrations).T.sort_index()

    def parameter_scan_with_fluxes(
        self,
        parameter_name: str,
        parameter_values: List[float],
        tolerance: float = 1e-8,
        multiprocessing: bool = True,
        **integrator_kwargs: Dict[str, Any],
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Scan the model steady state changes caused by a change to a parameter."""
        if sys.platform in ["win32", "cygwin"]:
            warnings.warn(
                """
                Windows does not behave well with multiple processes.
                Falling back to threading routine."""
            )
        worker = partial(
            self._parameter_scan_worker,
            **{
                "parameter_name": parameter_name,
                "model": self.model,
                "Sim": self.__class__,
                "integrator": self._integrator,
                "tolerance": tolerance,
                "y0": self.y0,
                "integrator_kwargs": integrator_kwargs,
                "include_fluxes": True,
            },
        )
        if sys.platform in ["win32", "cygwin"] or not multiprocessing:
            results = self._scan_threading(parameter_name, parameter_values, worker)
        else:
            results = self._scan_multiprocessing(parameter_name, parameter_values, worker)
        concentrations = {}
        fluxes = {}
        for (i, conc, flux) in results:
            concentrations[i] = conc
            fluxes[i] = flux
        return pd.DataFrame(concentrations).T.sort_index(), pd.DataFrame(fluxes).T.sort_index()

    def parameter_scan_2d(
        self,
        p1: Tuple[str, List[float]],
        p2: Tuple[str, List[float]],
        tolerance: float = 1e-8,
        multiprocessing: bool = True,
        **integrator_kwargs: Dict[str, Any],
    ) -> Dict[float, pd.DataFrame]:
        cs = {}
        parameter_name1, parameter_values1 = p1
        parameter_name2, parameter_values2 = p2
        original_pars = self.model.parameters.copy()
        for value in tqdm(parameter_values2, total=len(parameter_values2), desc=parameter_name2):
            self.update_parameter(parameter_name2, value)
            cs[value] = self.parameter_scan(
                parameter_name1,
                parameter_values1,
                tolerance=tolerance,
                multiprocessing=multiprocessing,
                **integrator_kwargs,
            )
        self.update_parameters(original_pars)
        return cs

    def parameter_scan_2d_with_fluxes(
        self,
        p1: Tuple[str, List[float]],
        p2: Tuple[str, List[float]],
        tolerance: float = 1e-8,
        multiprocessing: bool = True,
        **integrator_kwargs: Dict[str, Any],
    ) -> Tuple[Dict[float, pd.DataFrame], Dict[float, pd.DataFrame]]:
        cs = {}
        vs = {}
        parameter_name1, parameter_values1 = p1
        parameter_name2, parameter_values2 = p2
        original_pars = self.model.parameters.copy()
        for value in tqdm(parameter_values2, total=len(parameter_values2), desc=parameter_name2):
            self.update_parameter(parameter_name2, value)
            c, v = self.parameter_scan_with_fluxes(
                parameter_name1,
                parameter_values1,
                tolerance=tolerance,
                multiprocessing=multiprocessing,
                **integrator_kwargs,
            )
            cs[value] = c
            vs[value] = v
        self.update_parameters(original_pars)
        return cs, vs

    def plot_log(
        self,
        xlabel: str = None,
        ylabel: str = None,
        title: str = None,
        normalise: Union[float, List[float]] = None,
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
        compounds = self.model.get_compounds()
        y = cast(pd.DataFrame, self.get_full_results_df(normalise=normalise, concatenated=True))
        if y is None:
            return None, None
        fig, ax = plot(
            plot_args=(y.loc[:, compounds],),
            legend=compounds,
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
        ax.set_xscale("log")
        ax.set_yscale("log")
        return fig, ax

    def plot_semilog(
        self,
        log_axis: str = "y",
        xlabel: str = None,
        ylabel: str = None,
        title: str = None,
        normalise: Union[float, List[float]] = None,
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
        compounds = self.model.get_compounds()
        y = cast(pd.DataFrame, self.get_full_results_df(normalise=normalise, concatenated=True))
        if y is None:
            return None, None
        fig, ax = plot(
            plot_args=(y.loc[:, compounds],),
            legend=compounds,
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
        if log_axis == "y":
            ax.set_yscale("log")
        elif log_axis == "x":
            ax.set_xscale("log")
        else:
            raise ValueError("log_axis must be either x or y")
        return fig, ax

    def plot_derived(
        self,
        xlabel: str = None,
        ylabel: str = None,
        title: str = None,
        normalise: Union[float, List[float]] = None,
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
        compounds = self.model.get_derived_compounds()
        y = cast(pd.DataFrame, self.get_full_results_df(normalise=normalise, concatenated=True))
        if y is None:
            return None, None
        return plot(
            plot_args=(y.loc[:, compounds],),
            legend=compounds,
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

    def plot_all(
        self,
        xlabel: str = None,
        ylabel: str = None,
        title: str = None,
        normalise: Union[float, List[float]] = None,
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
        compounds = self.model.get_all_compounds()
        y = cast(pd.DataFrame, self.get_full_results_df(normalise=normalise, concatenated=True))
        if y is None:
            return None, None
        return plot(
            plot_args=(y.loc[:, compounds],),
            legend=compounds,
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

    def plot_selection(
        self,
        compounds: List[str],
        xlabel: str = None,
        ylabel: str = None,
        title: str = None,
        normalise: Union[float, List[float]] = None,
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
        y = cast(pd.DataFrame, self.get_full_results_df(normalise=normalise, concatenated=True))
        if y is None:
            return None, None
        return plot(
            plot_args=(y.loc[:, compounds],),
            legend=compounds,
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

    def plot_grid(
        self,
        compound_groups: List[List[str]],
        ncols: int = None,
        sharex: bool = True,
        sharey: bool = True,
        xlabels: List[str] = None,
        ylabels: List[str] = None,
        normalise: Union[float, List[float]] = None,
        plot_titles: Optional[Iterable[str]] = None,
        figure_title: str = None,
        grid: bool = True,
        tight_layout: bool = True,
        figure_kwargs: Dict[str, Any] = None,
        subplot_kwargs: Dict[str, Any] = None,
        plot_kwargs: Dict[str, Any] = None,
        grid_kwargs: Dict[str, Any] = None,
        legend_kwargs: Dict[str, Any] = None,
        tick_kwargs: Dict[str, Any] = None,
        label_kwargs: Dict[str, Any] = None,
        title_kwargs: Dict[str, Any] = None,
    ) -> Tuple[Optional[Figure], Optional[Axes]]:
        """Plot simulation results of the compound groups as a grid.

        Examples
        --------
        >>> plot_grid([["x1", "x2"], ["x3", "x4]])
        """
        y = cast(pd.DataFrame, self.get_full_results_df(normalise=normalise, concatenated=True))
        if y is None:
            return None, None
        plot_groups = [(y.loc[:, compounds].values,) for compounds in compound_groups]
        return plot_grid(
            plot_groups=plot_groups,  # type: ignore
            legend_groups=compound_groups,
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

    def plot_against_variable(
        self,
        variable: str,
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
        if xlabel is None:
            xlabel = variable
        results = cast(pd.DataFrame, self.get_full_results_df(concatenated=True))
        if results is None:
            return None, None
        compounds = cast(List[str], self.model.get_compounds())
        x = results.loc[:, variable].values  # type: ignore
        y = results.loc[:, compounds].values
        return plot(
            plot_args=(x, y),
            legend=compounds,
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

    def plot_derived_against_variable(
        self,
        variable: str,
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
        if xlabel is None:
            xlabel = variable
        results = cast(pd.DataFrame, self.get_full_results_df(concatenated=True))
        if results is None:
            return None, None
        compounds = cast(List[str], self.model.get_derived_compounds())
        x = results.loc[:, variable].values  # type: ignore
        y = results.loc[:, compounds].values
        return plot(
            plot_args=(x, y),
            legend=compounds,
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

    def plot_all_against_variable(
        self,
        variable: str,
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
        if xlabel is None:
            xlabel = variable
        results = cast(pd.DataFrame, self.get_full_results_df(concatenated=True))
        if results is None:
            return None, None
        compounds = cast(List[str], self.model.get_all_compounds())
        x = results.loc[:, variable].values  # type: ignore
        y = results.loc[:, compounds].values
        return plot(
            plot_args=(x, y),
            legend=compounds,
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

    def plot_selection_against_variable(
        self,
        compounds: Iterable[str],
        variable: str,
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
        if xlabel is None:
            xlabel = variable
        results = cast(pd.DataFrame, self.get_full_results_df(concatenated=True))
        if results is None:
            return None, None
        x = results.loc[:, variable].values  # type: ignore
        y = results.loc[:, compounds].values  # type: ignore
        return plot(
            plot_args=(x, y),
            legend=compounds,
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

    def plot_fluxes(
        self,
        xlabel: str = None,
        ylabel: str = None,
        title: str = None,
        normalise: Union[float, List[float]] = None,
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
        rate_names = cast(List[str], self.model.get_rate_names())
        y = self.get_fluxes_df(normalise=normalise, concatenated=True)
        if y is None:
            return None, None
        y = cast(pd.DataFrame, y)
        return plot(
            plot_args=(y.loc[:, rate_names],),
            legend=rate_names,
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

    def plot_flux_selection(
        self,
        rate_names: List[str],
        xlabel: str = None,
        ylabel: str = None,
        title: str = None,
        normalise: Union[float, List[float]] = None,
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
        y = self.get_fluxes_df(normalise=normalise, concatenated=True)
        if y is None:
            return None, None
        y = cast(pd.DataFrame, y)
        return plot(
            plot_args=(y.loc[:, rate_names],),
            legend=rate_names,
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

    def plot_fluxes_grid(
        self,
        rate_groups: List[List[str]],
        ncols: int = None,
        sharex: bool = True,
        sharey: bool = True,
        xlabels: List[str] = None,
        ylabels: List[str] = None,
        normalise: Union[float, List[float]] = None,
        plot_titles: Optional[Iterable[str]] = None,
        figure_title: str = None,
        grid: bool = True,
        tight_layout: bool = True,
        figure_kwargs: Dict[str, Any] = None,
        subplot_kwargs: Dict[str, Any] = None,
        plot_kwargs: Dict[str, Any] = None,
        grid_kwargs: Dict[str, Any] = None,
        legend_kwargs: Dict[str, Any] = None,
        tick_kwargs: Dict[str, Any] = None,
        label_kwargs: Dict[str, Any] = None,
        title_kwargs: Dict[str, Any] = None,
    ) -> Tuple[Optional[Figure], Optional[npt.NDArray[np.float64]]]:
        """Plot simulation results of the compound groups as a grid.

        Examples
        --------
        >>> plot_fluxes_grid([["v1", "v2"], ["v3", "v4]])
        """
        fluxes = self.get_fluxes_df(normalise=normalise, concatenated=True)
        if fluxes is None:
            return None, None
        fluxes = cast(pd.DataFrame, fluxes)
        plot_groups = [(cast(npt.NDArray[np.float64], fluxes.loc[:, group].values),) for group in rate_groups]
        return plot_grid(
            plot_groups=plot_groups,  # type: ignore
            legend_groups=rate_groups,
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

    def plot_fluxes_against_variable(
        self,
        variable: str,
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
        if xlabel is None:
            xlabel = variable
        rate_names = cast(List[str], self.model.get_rate_names())
        x = self.get_variable(variable=variable)
        y = self.get_fluxes_df(concatenated=True)
        if x is None or y is None:
            return None, None
        y = cast(pd.DataFrame, y).loc[:, rate_names].values
        return plot(
            plot_args=(x, y),
            legend=rate_names,
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

    def plot_flux_selection_against_variable(
        self,
        rate_names: List[str],
        variable: str,
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
        if xlabel is None:
            xlabel = variable
        x = self.get_variable(variable=variable)
        y = self.get_fluxes_df(concatenated=True)
        if x is None or y is None:
            return None, None
        y = cast(pd.DataFrame, y).loc[:, rate_names].values
        return plot(
            plot_args=(x, y),
            legend=rate_names,
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

    def plot_phase_plane(
        self,
        cpd1: str,
        cpd2: str,
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
        if xlabel is None:
            xlabel = cpd1
        if ylabel is None:
            ylabel = cpd2
        x = self.get_variable(variable=cpd1)
        y = self.get_variable(variable=cpd2)
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

    def plot_phase_space(
        self,
        cpd1: str,
        cpd2: str,
        cpd3: str,
        xlabel: str = None,
        ylabel: str = None,
        zlabel: str = None,
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
        kwargs["subplot"].update({"projection": "3d"})

        x = self.get_variable(variable=cpd1)
        y = self.get_variable(variable=cpd2)
        z = self.get_variable(variable=cpd3)

        if x is None or y is None or z is None:
            return None, None

        xlabel = cpd1 if xlabel is None else xlabel
        ylabel = cpd2 if ylabel is None else ylabel
        zlabel = cpd3 if zlabel is None else zlabel

        if ax is None:
            fig, ax = plt.subplots(1, 1, subplot_kw=kwargs["subplot"], **kwargs["figure"])
        else:
            fig = ax.get_figure()

        ax.plot(x, y, z, **kwargs["plot"])
        _style_subplot(
            ax=ax,
            xlabel=xlabel,
            ylabel=ylabel,
            zlabel=zlabel,
            title=title,
            grid=grid,
            kwargs=kwargs,
        )
        if tight_layout:
            fig.tight_layout()
        return fig, ax

    def plot_trajectories(
        self,
        cpd1: str,
        cpd2: str,
        cpd1_bounds: Tuple[float, float],
        cpd2_bounds: Tuple[float, float],
        n: int,
        y0: Dict[str, float],
        t0: float = 0,
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
        xlabel = cpd1 if xlabel is None else xlabel
        ylabel = cpd2 if ylabel is None else ylabel

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

        x = np.linspace(*cpd1_bounds, n)
        y = np.linspace(*cpd2_bounds, n)
        u = np.zeros((n, n))
        v = np.zeros((n, n))

        fcd = self.model.get_full_concentration_dict(y=y0, t=t0)
        for i, s1 in enumerate(x):
            for j, s2 in enumerate(y):
                # Update y0 to new values
                fcd.update({cpd1: s1, cpd2: s2})
                rhs = self.model.get_right_hand_side(y=fcd, t=t0)
                u[i, j] = rhs[f"d{cpd1}dt"]
                v[i, j] = rhs[f"d{cpd2}dt"]

        if ax is None:
            fig, ax = plt.subplots(1, 1, subplot_kw=kwargs["subplot"], **kwargs["figure"])
        else:
            fig = ax.get_figure()
        ax.quiver(x, y, u.T, v.T)
        _style_subplot(
            ax=ax,
            xlabel=xlabel,
            ylabel=ylabel,
            title=title,
            grid=grid,
            kwargs=kwargs,
        )
        if tight_layout:
            fig.tight_layout()
        return fig, ax

    def plot_3d_trajectories(
        self,
        cpd1: str,
        cpd2: str,
        cpd3: str,
        cpd1_bounds: Tuple[float, float],
        cpd2_bounds: Tuple[float, float],
        cpd3_bounds: Tuple[float, float],
        n: int,
        y0: Dict[str, float],
        t0: float = 0,
        xlabel: str = None,
        ylabel: str = None,
        zlabel: str = None,
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
        kwargs["subplot"].update({"projection": "3d"})

        x = np.linspace(*cpd1_bounds, n)
        y = np.linspace(*cpd2_bounds, n)
        z = np.linspace(*cpd3_bounds, n)
        u = np.zeros((n, n, n))
        v = np.zeros((n, n, n))
        w = np.zeros((n, n, n))

        fcd = self.model.get_full_concentration_dict(y=y0, t=t0)
        for i, s1 in enumerate(x):
            for j, s2 in enumerate(y):
                for k, s3 in enumerate(y):
                    fcd.update({cpd1: s1, cpd2: s2, cpd3: s3})
                    rhs = self.model.get_right_hand_side(y=fcd, t=t0)
                    u[i, j, k] = rhs[f"d{cpd1}dt"]
                    v[i, j, k] = rhs[f"d{cpd2}dt"]
                    w[i, j, k] = rhs[f"d{cpd3}dt"]

        if ax is None:
            fig, ax = plt.subplots(1, 1, subplot_kw=kwargs["subplot"], **kwargs["figure"])
        else:
            fig = ax.get_figure()
        X, Y, Z = np.meshgrid(x, y, z)
        ax.quiver(
            X,
            Y,
            Z,
            np.transpose(u, [1, 0, 2]),
            np.transpose(v, [1, 0, 2]),
            np.transpose(w, [1, 0, 2]),
            length=0.05,
            normalize=True,
            alpha=0.5,
        )
        xlabel = cpd1 if xlabel is None else xlabel
        ylabel = cpd2 if ylabel is None else ylabel
        zlabel = cpd3 if zlabel is None else zlabel
        _style_subplot(
            ax=ax,
            xlabel=xlabel,
            ylabel=ylabel,
            zlabel=zlabel,
            title=title,
            grid=grid,
            kwargs=kwargs,
        )
        if tight_layout:
            fig.tight_layout()
        return fig, ax
