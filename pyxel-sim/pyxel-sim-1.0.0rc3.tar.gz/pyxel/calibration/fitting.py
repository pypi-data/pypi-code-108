#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

""":term:`CDM` model calibration with PYGMO.

https://esa.github.io/pagmo2/index.html
"""
import copy
import logging
import math
import typing as t
from copy import deepcopy
from numbers import Number
from pathlib import Path

import dask.delayed as delayed
import numpy as np
import pandas as pd
from typing_extensions import Literal

from pyxel.calibration import (
    CalibrationMode,
    ProblemSingleObjective,
    check_ranges,
    list_to_3d_slice,
    list_to_slice,
    read_data,
    read_datacubes,
)
from pyxel.exposure import run_exposure_pipeline
from pyxel.observation.parameter_values import ParameterValues
from pyxel.pipelines import Processor
from pyxel.pipelines.processor import ResultType

if t.TYPE_CHECKING:
    import xarray as xr
    from numpy.typing import ArrayLike

    from pyxel.exposure import Readout


class ModelFitting(ProblemSingleObjective):
    """Pygmo problem class to fit data with any model in Pyxel."""

    def __init__(
        self,
        processor: Processor,
        variables: t.Sequence[ParameterValues],
        readout: "Readout",
    ):
        self.processor = processor  # type: Processor
        self.variables = variables  # type: t.Sequence[ParameterValues]

        self.calibration_mode = None  # type: t.Optional[CalibrationMode]
        self.original_processor = None  # type: t.Optional[Processor]
        self.generations = None  # type: t.Optional[int]
        self.pop = None  # type: t.Optional[int]
        self.readout = readout  # type: Readout

        self.all_target_data = []  # type: t.List[np.ndarray]
        self.weighting = None  # type: t.Optional[np.ndarray]
        self.weighting_from_file = None  # type: t.Optional[t.Sequence[np.ndarray]]
        self.fitness_func = None  # type: t.Optional[t.Callable]
        self.sim_output = None  # type: t.Optional[ResultType]
        # self.fitted_model = None            # type: t.Optional['ModelFunction']
        self.param_processor_list = []  # type: t.List[Processor]

        self.file_path = None  # type: t.Optional[Path]
        self.pipeline_seed = None  # type: t.Optional[int]

        self.fitness_array = None  # type: t.Optional[np.ndarray]
        self.population = None  # type: t.Optional[np.ndarray]
        self.champion_f_list = None  # type: t.Optional[np.ndarray]
        self.champion_x_list = None  # type: t.Optional[np.ndarray]

        self.lbd = []  # type: t.Sequence[float]  # lower boundary
        self.ubd = []  # type: t.Sequence[float]  # upper boundary

        self.sim_fit_range = (
            slice(None),
            slice(None),
            slice(None),
        )  # type: t.Tuple[slice, slice, slice]
        self.targ_fit_range = (
            slice(None),
            slice(None),
        )  # type: t.Union[t.Tuple[slice, slice], t.Tuple[slice, slice, slice]]

        self.match = {}  # type: t.Dict[int, t.List[str]]

    def get_bounds(self) -> t.Tuple[t.Sequence[float], t.Sequence[float]]:
        """Get the box bounds of the problem (lower_boundary, upper_boundary).

        It also implicitly defines the dimension of the problem.

        Returns
        -------
        tuple of lower boundaries and upper boundaries
        """
        return self.lbd, self.ubd

    def configure(
        self,
        calibration_mode: CalibrationMode,
        simulation_output: ResultType,
        fitness_func: t.Callable,
        population_size: int,
        generations: int,
        file_path: t.Optional[Path],
        target_fit_range: t.Sequence[int],
        out_fit_range: t.Sequence[int],
        target_output: t.Sequence[Path],
        input_arguments: t.Optional[t.Sequence[ParameterValues]] = None,
        weights: t.Optional[t.Sequence[float]] = None,
        weights_from_file: t.Optional[t.Sequence[Path]] = None,
        pipeline_seed: t.Optional[int] = None,
    ) -> None:
        """TBW.

        Parameters
        ----------
        pipeline_seed
        calibration_mode
        simulation_output
        fitness_func
        population_size
        generations
        file_path
        target_fit_range
        out_fit_range
        target_output
        input_arguments
        weights
        weights_from_file
        """
        self.calibration_mode = CalibrationMode(calibration_mode)
        self.sim_output = ResultType(simulation_output)
        self.fitness_func = fitness_func
        self.pop = population_size
        self.generations = generations
        self.pipeline_seed = pipeline_seed

        # TODO: Remove 'assert'
        # assert isinstance(self.pop, int)

        # if self.calibration_mode == 'single_model':           # TODO update
        #     self.single_model_calibration()

        self.set_bound()

        self.original_processor = deepcopy(self.processor)
        if input_arguments:

            max_val, min_val = 0, 1000
            for arg in input_arguments:
                min_val = min(min_val, len(arg.values))
                max_val = max(max_val, len(arg.values))
            if min_val != max_val:
                logging.warning(
                    'The "result_input_arguments" value lists have different lengths! '
                    "Some values will be ignored."
                )
            for i in range(min_val):
                new_processor = deepcopy(self.processor)  # type: Processor
                for step in input_arguments:  # type: ParameterValues
                    assert step.values != "_"

                    value = step.values[i]  # type: t.Union[Literal['_'], str, Number]

                    step.current = value
                    new_processor.set(key=step.key, value=step.current)
                self.param_processor_list += [new_processor]
        else:
            self.param_processor_list = [deepcopy(self.processor)]

        params = 0  # type: int
        for var in self.variables:  # type: ParameterValues
            if isinstance(var.values, list):
                b = len(var.values)
            else:
                b = 1

            params += b
        self.champion_f_list = np.zeros((1, 1))
        self.champion_x_list = np.zeros((1, params))
        self.file_path = file_path

        if self.readout.time_domain_simulation:
            target_list_3d = read_datacubes(
                filenames=target_output
            )  # type: t.Sequence[np.ndarray]
            times, rows, cols = target_list_3d[0].shape
            check_ranges(
                target_fit_range=target_fit_range,
                out_fit_range=out_fit_range,
                rows=rows,
                cols=cols,
                readout_times=times,
            )
            self.targ_fit_range = list_to_slice(target_fit_range)
            self.sim_fit_range = list_to_3d_slice(out_fit_range)
            for target_3d in target_list_3d:  # type: np.ndarray
                self.all_target_data += [target_3d[self.targ_fit_range]]

        else:
            target_list_2d = read_data(
                filenames=target_output
            )  # type: t.Sequence[np.ndarray]
            rows, cols = target_list_2d[0].shape
            check_ranges(
                target_fit_range=target_fit_range,
                out_fit_range=out_fit_range,
                rows=rows,
                cols=cols,
            )
            self.targ_fit_range = list_to_slice(target_fit_range)
            out_fit_range = [None, None] + out_fit_range  # type: ignore
            self.sim_fit_range = list_to_3d_slice(out_fit_range)
            for target_2d in target_list_2d:  # type: np.ndarray
                self.all_target_data += [target_2d[self.targ_fit_range]]

            self._configure_weights(
                weights=weights, weights_from_file=weights_from_file
            )

    def _configure_weights(
        self,
        weights: t.Optional[t.Sequence[float]] = None,
        weights_from_file: t.Optional[t.Sequence[Path]] = None,
    ) -> None:
        """TBW.

        Parameters
        ----------
        weights
        weights_from_file

        Returns
        -------
        None
        """
        if weights_from_file is not None:
            if self.readout.time_domain_simulation:
                wf = read_datacubes(weights_from_file)
                self.weighting_from_file = [
                    weight_array[self.targ_fit_range] for weight_array in wf
                ]
            else:
                wf = read_data(weights_from_file)
                self.weighting_from_file = [
                    weight_array[self.targ_fit_range] for weight_array in wf
                ]
        elif weights is not None:
            self.weighting = np.array(weights)

    def set_bound(self) -> None:
        """TBW."""
        self.lbd = []
        self.ubd = []
        for var in self.variables:  # type: ParameterValues
            assert var.boundaries
            low_val, high_val = var.boundaries  # type: t.Tuple[float, float]

            if var.logarithmic:
                low_val = math.log10(low_val)
                high_val = math.log10(high_val)

            if var.values == "_":
                self.lbd += [low_val]
                self.ubd += [high_val]
            elif isinstance(var.values, list) and all(x == "_" for x in var.values[:]):
                self.lbd += [low_val] * len(var.values)
                self.ubd += [high_val] * len(var.values)
            else:
                raise ValueError(
                    'Character "_" (or a list of it) should be used to '
                    "indicate variables need to be calibrated"
                )

    def get_simulated_data(self, processor: Processor) -> np.ndarray:
        """Extract 2D data from a processor."""
        if self.sim_output == ResultType.Image:
            simulated_data = processor.result["image"][
                self.sim_fit_range
            ]  # type: np.ndarray

        elif self.sim_output == ResultType.Signal:
            simulated_data = processor.result["signal"][self.sim_fit_range]
        elif self.sim_output == ResultType.Pixel:
            simulated_data = processor.result["pixel"][self.sim_fit_range]

        return simulated_data

    def calculate_fitness(
        self,
        simulated_data: np.ndarray,
        target_data: np.ndarray,
        weighting: t.Optional[np.ndarray] = None,
    ) -> float:
        """TBW.

        Parameters
        ----------
        simulated_data
        target_data
        weighting
        """
        # TODO: Remove 'assert'
        assert self.fitness_func is not None

        if weighting is not None:
            factor = weighting
        else:
            factor = np.ones(np.shape(target_data))

        fitness = self.fitness_func(
            simulated=simulated_data.astype(np.float64),
            target=target_data.astype(np.float64),
            weighting=factor.astype(np.float64),
        )  # type: float

        return fitness

    # TODO: If possible, use 'numba' for this method
    def fitness(self, decision_vector_1d: np.ndarray) -> t.Sequence[float]:
        """Call the fitness function, elements of parameter array could be logarithmic values.

        Parameters
        ----------
        decision_vector_1d : array_like
            A 1d decision vector.

        Returns
        -------
        sequence
            The fitness of the input decision vector (concatenating the objectives,
            the equality and the inequality constraints)
        """
        # TODO: Fix this
        if self.pop is None:
            raise NotImplementedError("'pop' is not initialized.")

        try:

            # TODO: Use directory 'logging.'
            logger = logging.getLogger("pyxel")
            prev_log_level = logger.getEffectiveLevel()

            parameter_1d = self.convert_to_parameters(decision_vector_1d)
            # TODO: deepcopy is not needed. Check this
            processor_list = self.param_processor_list  # type: t.Sequence[Processor]

            overall_fitness = 0.0  # type: float
            for i, (processor, target_data) in enumerate(
                zip(processor_list, self.all_target_data)
            ):

                processor = self.update_processor(
                    parameter=parameter_1d, processor=processor
                )

                logger.setLevel(logging.WARNING)
                # result_proc = None
                if self.calibration_mode == CalibrationMode.Pipeline:
                    _ = run_exposure_pipeline(
                        processor=processor,
                        readout=self.readout,
                        pipeline_seed=self.pipeline_seed,
                    )
                # elif self.calibration_mode == 'single_model':
                #     self.fitted_model.function(processor.detector)               # todo: update
                else:
                    raise NotImplementedError

                logger.setLevel(prev_log_level)

                simulated_data = self.get_simulated_data(processor=processor)

                weighting = None  # type: t.Optional[np.ndarray]

                if self.weighting is not None:
                    weighting = self.weighting[i] * np.ones(
                        (
                            processor.detector.geometry.row,
                            processor.detector.geometry.col,
                        )
                    )
                elif self.weighting_from_file is not None:
                    weighting = self.weighting_from_file[i]

                overall_fitness += self.calculate_fitness(
                    simulated_data=simulated_data,
                    target_data=target_data,
                    weighting=weighting,
                )

        except Exception:
            logging.exception(
                "Catch an exception in 'fitness' for ModelFitting: %r. exc: %r",
                self,
            )
            raise

        return [overall_fitness]

    def convert_to_parameters(self, decisions_vector: "ArrayLike") -> np.ndarray:
        """Convert a decision version from Pygmo2 to parameters.

        Parameters
        ----------
        decisions_vector : array_like
            It could a 1D or 2D array.

        Returns
        -------
        array_like
            Parameters
        """
        parameters = np.asarray(decisions_vector)

        a = 0
        for var in self.variables:
            b = 1
            if isinstance(var.values, list):
                b = len(var.values)
            if var.logarithmic:
                start = a
                stop = a + b
                parameters[..., start:stop] = np.power(10, parameters[..., start:stop])
            a += b

        return parameters

    def apply_parameters(
        self, processor: Processor, parameter: np.ndarray
    ) -> Processor:
        """Create a new ``Processor`` with new parameters."""
        new_processor = self.update_processor(parameter=parameter, processor=processor)

        _ = run_exposure_pipeline(
            processor=new_processor,
            readout=self.readout,
            pipeline_seed=self.pipeline_seed,
        )

        return new_processor

    def apply_parameters_to_processors(
        self, parameters: "xr.DataArray"
    ) -> pd.DataFrame:
        """TBW."""
        assert "island" in parameters.dims
        assert "param_id" in parameters.dims

        lst = []
        for id_processor, processor in enumerate(self.param_processor_list):
            delayed_processor = delayed(processor)

            for idx_island, params_array in parameters.groupby("island"):
                params = params_array.data  # type: np.ndarray

                result_processor = delayed(self.apply_parameters)(
                    processor=delayed_processor, parameter=params
                )

                lst.append(
                    {
                        "island": idx_island,
                        "id_processor": id_processor,
                        "processor": result_processor,
                    }
                )

        df = pd.DataFrame(lst).sort_values(["island", "id_processor"])

        return df

    def update_processor(
        self, parameter: np.ndarray, processor: Processor
    ) -> Processor:
        """TBW."""
        new_processor = copy.deepcopy(processor)
        a, b = 0, 0
        for var in self.variables:
            if var.values == "_":
                b = 1
                new_processor.set(key=var.key, value=parameter[a])
            elif isinstance(var.values, list):
                b = len(var.values)

                start = a
                stop = a + b
                new_processor.set(key=var.key, value=parameter[start:stop])
            a += b
        return new_processor
