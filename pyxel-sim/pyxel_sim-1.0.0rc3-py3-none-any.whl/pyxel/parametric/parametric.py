#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Parametric mode class and helper functions."""
import itertools
import logging
import operator
import typing as t
from copy import deepcopy
from enum import Enum

import numpy as np
import xarray as xr
from dask import delayed
from tqdm.auto import tqdm
from typing_extensions import Literal

# import dask
from pyxel.observation.parameter_values import ParameterType, ParameterValues
from pyxel.state import get_obj_att, get_value

if t.TYPE_CHECKING:
    from ..inputs_outputs import ParametricOutputs
    from ..pipelines import Processor


class ParametricMode(Enum):
    """Parametric mode class."""

    Product = "product"
    Sequential = "sequential"
    Custom = "custom"


class ParametricResult(t.NamedTuple):
    """Result class for parametric class."""

    dataset: t.Union[xr.Dataset, t.Dict[str, xr.Dataset]]
    parameters: xr.Dataset
    logs: xr.Dataset


# TODO: Use `Enum` for `parametric_mode` ?
class Parametric:
    """Parametric class."""

    def __init__(
        self,
        outputs: "ParametricOutputs",
        parameters: t.Sequence[ParameterValues],
        mode: str = "product",
        from_file: t.Optional[str] = None,
        column_range: t.Optional[t.Tuple[int, int]] = None,
        with_dask: bool = False,
        result_type: Literal["image", "signal", "pixel"] = "image",
    ):
        self.outputs = outputs
        self.parametric_mode = ParametricMode(mode)  # type: ParametricMode
        self._parameters = parameters
        self.file = from_file
        self.data = None  # type: t.Optional[np.ndarray]
        if column_range:
            self.columns = slice(*column_range)
        self.with_dask = with_dask
        self.parameter_types = {}  # type: dict

    def __repr__(self):
        cls_name = self.__class__.__name__  # type: str
        return f"{cls_name}<mode={self.parametric_mode!s}>"

    @property
    def enabled_steps(self) -> t.Sequence[ParameterValues]:
        """Return a list of enabled ParameterValues.

        Returns
        -------
        out: list
        """
        out = [step for step in self._parameters if step.enabled]
        return out

    def _custom_parameters(self) -> t.Generator[t.Tuple[int, dict], None, None]:
        """Generate custom mode parameters based on input file.

        Yields
        ------
        index: int
        parameter_dict: dict
        """
        from pyxel.inputs_outputs import load_table

        # TODO: is self.data really needed
        if self.file is not None:
            result = load_table(self.file).to_numpy()[
                :, self.columns
            ]  # type: np.ndarray
        else:
            raise ValueError("File for custom parametric mode not specified!")
        self.data = result
        for index, data_array in enumerate(self.data):
            i = 0
            parameter_dict = {}
            for step in self.enabled_steps:
                key = step.key

                # TODO: this is confusing code. Fix this.
                #       Furthermore 'step.values' should be a `t.List[int, float]` and not a `str`
                if step.values == "_":
                    value = data_array[i]
                    i += 1
                    parameter_dict.update({key: value})

                elif isinstance(step.values, list):

                    values = np.asarray(deepcopy(step.values))  # type: np.ndarray
                    sh = values.shape  # type: tuple
                    values_flattened = values.flatten()

                    if all(x == "_" for x in values_flattened):
                        value = data_array[i : i + len(values_flattened)]  # noqa: E203
                        i += len(value)
                        value = value.reshape(sh).tolist()
                        parameter_dict.update({key: value})
                    else:
                        raise ValueError(
                            'Only "_" characters (or a list of them) should be used to '
                            "indicate parameters updated from file in custom mode"
                        )
            yield index, parameter_dict

    def _sequential_parameters(self) -> t.Generator[t.Tuple[int, dict], None, None]:
        """Generate sequential mode parameters.

        Yields
        ------
        index: int
        parameter_dict: dict
        """
        for step in self.enabled_steps:  # type: ParameterValues
            key = step.key  # type : str
            for index, value in enumerate(step):
                parameter_dict = {key: value}
                yield index, parameter_dict

    def _product_indices(self) -> "t.Iterator[t.Tuple]":
        """Return an iterator of product parameter indices.

        Returns
        -------
        out: iterator
        """
        step_ranges = []
        for step in self.enabled_steps:
            step_ranges.append(range(len(step)))
        out = itertools.product(*step_ranges)
        return out

    def _product_parameters(
        self,
    ) -> t.Generator[t.Tuple[t.Tuple, t.Dict[str, t.Any]], None, None]:
        """Generate product mode parameters.

        Yields
        ------
        indices: tuple
        parameter_dict: dict
        """
        all_steps = self.enabled_steps
        keys = [step.key for step in self.enabled_steps]
        for indices, params in zip(
            self._product_indices(), itertools.product(*all_steps)
        ):
            parameter_dict = {}
            for key, value in zip(keys, params):
                parameter_dict.update({key: value})
            yield indices, parameter_dict

    def _parameter_it(self) -> t.Callable:
        """Return the method for generating parameters based on parametric mode.

        Returns
        -------
        callable
        """
        if self.parametric_mode == ParametricMode.Product:
            return self._product_parameters

        elif self.parametric_mode == ParametricMode.Sequential:
            return self._sequential_parameters

        elif self.parametric_mode == ParametricMode.Custom:
            return self._custom_parameters
        else:
            raise NotImplementedError

    def _processors_it(
        self, processor: "Processor"
    ) -> t.Generator[
        t.Tuple["Processor", t.Union[int, t.Tuple[int]], t.Dict], None, None
    ]:
        """Generate processors with different parameters.

        Parameters
        ----------
        processor: Processor

        Yields
        ------
        new_processor: Processor
        index: int or tuple
        parameter_dict: dict
        """

        parameter_it = self._parameter_it()

        for index, parameter_dict in parameter_it():
            new_processor = create_new_processor(
                processor=processor, parameter_dict=parameter_dict
            )
            yield new_processor, index, parameter_dict

    def _delayed_processors(self, processor: "Processor") -> t.List:
        """Return a list of Dask delayed processors built from processor generator.

        Parameters
        ----------
        processor: Processor

        Returns
        -------
        processors: list
            List of dask delayed processors.
        """

        processors = []
        delayed_processor = delayed(processor)
        parameter_it = self._parameter_it()

        for _index, parameter_dict in parameter_it():
            delayed_parameter_dict = delayed(parameter_dict)
            processors.append(
                delayed(create_new_processor)(
                    processor=delayed_processor, parameter_dict=delayed_parameter_dict
                )
            )

        return processors

    def _get_parameter_types(self) -> dict:
        """Check for each step if parameters can be used as dataset coordinates (1D, simple) or not (multi).

        Returns
        -------
        self.parameter_types: dict
        """
        for step in self.enabled_steps:
            self.parameter_types.update({step.key: step.type})
        return self.parameter_types

    def run_debug_mode(
        self, processor: "Processor"
    ) -> t.Tuple[t.List["Processor"], xr.Dataset]:
        """Run parametric pipelines in debug mode and return list of processors and parameter logs.

        Parameters
        ----------
        processor: Processor

        Returns
        -------
        processors: list
        final_logs: xr.Dataset
        """
        processors = []
        logs = []  # type: t.List

        for processor_id, (proc, _index, parameter_dict) in enumerate(
            tqdm(self._processors_it(processor))
        ):
            log = log_parameters(
                processor_id=processor_id, parameter_dict=parameter_dict
            )
            logs.append(log)
            result_proc = proc.run_pipeline()
            processors.append(result_proc)

        final_logs = xr.combine_by_coords(logs)

        return processors, final_logs

    def _check_steps(self, processor: "Processor") -> None:
        """Validate enabled parameter steps in processor before running the pipelines.

        Parameters
        ----------
        processor: Processor

        Returns
        -------
        None
        """

        for step in self.enabled_steps:  # type: ParameterValues

            key = step.key  # type: str
            assert processor.has(key)

            # TODO: the string literal expressions are difficult to maintain.
            #     Example: 'pipeline.', '.arguments', '.enabled'
            #     We may want to consider an API for this.
            # Proposed API:
            # value = operator.attrgetter(step.key)(processor)
            if "pipeline." in step.key:
                model_name = step.key[: step.key.find(".arguments")]  # type: str
                model_enabled = model_name + ".enabled"  # type: str
                if not processor.get(model_enabled):
                    raise ValueError(
                        f"The '{model_name}' model referenced in parametric configuration"
                        f"has not been enabled in yaml config!"
                    )

            if (
                any(x == "_" for x in step.values[:])
                and self.parametric_mode != ParametricMode.Custom
            ):
                raise ValueError(
                    "Either define 'custom' as parametric mode or "
                    "do not use '_' character in 'values' field"
                )

    def run_parametric(self, processor: "Processor") -> ParametricResult:
        """Run the parametric pipelines.

        Parameters
        ----------
        processor: Processor

        Returns
        -------
        result: Result
        """
        # validation
        self._check_steps(processor)

        types = self._get_parameter_types()

        if self.with_dask:

            raise NotImplementedError("Parametric with Dask not implemented yet.")

            # delayed_processor_list = self._delayed_processors(processor)
            # result_list = []
            #
            # for proc in delayed_processor_list:
            #     result_proc = delayed(proc.run_pipeline())
            #     result_list.append(result_proc)
            #
            # out = []

        else:

            if self.parametric_mode == ParametricMode.Product:

                # prepare lists for to-be-merged datasets
                dataset_list = []
                parameters = [
                    [] for _ in range(len(self.enabled_steps))
                ]  # type: t.List[t.List[xr.Dataset]]
                logs = []

                for processor_id, (proc, indices, parameter_dict) in enumerate(
                    tqdm(self._processors_it(processor))
                ):
                    # log parameters for this pipeline
                    log = log_parameters(
                        processor_id=processor_id, parameter_dict=parameter_dict
                    )
                    logs.append(log)

                    # run the pipeline
                    result_proc = proc.run_pipeline()

                    _ = self.outputs.save_to_file(processor=result_proc)

                    # save parameters with appropriate product mode indices
                    for i, coordinate in enumerate(parameter_dict):
                        parameter_ds = parameter_to_dataset(
                            parameter_dict=parameter_dict,
                            index=indices[i],
                            coordinate_name=coordinate,
                        )
                        parameters[i].append(parameter_ds)

                    # save data, use simple or multi coordinate+index
                    ds = _product_dataset(
                        processor=result_proc,
                        parameter_dict=parameter_dict,
                        indices=indices,
                        types=types,
                    )
                    dataset_list.append(ds)

                # merging/combining the outputs
                final_parameters_list = [xr.combine_by_coords(p) for p in parameters]
                final_parameters_merged = xr.merge(final_parameters_list)
                final_logs = xr.combine_by_coords(logs)
                final_dataset = xr.combine_by_coords(dataset_list)

                result = ParametricResult(
                    dataset=final_dataset,
                    parameters=final_parameters_merged,
                    logs=final_logs,
                )

                return result

            elif self.parametric_mode == ParametricMode.Sequential:

                # prepare lists/dictionaries for to-be-merged datasets
                dataset_dict = {}  # type: dict
                parameters = [[] for _ in range(len(self.enabled_steps))]
                logs = []

                # overflow to next parameter step counter
                step_counter = -1

                for processor_id, (proc, index, parameter_dict) in enumerate(
                    tqdm(self._processors_it(processor))
                ):
                    # log parameters for this pipeline
                    # TODO: somehow refactor logger so that default parameters
                    #  from other steps are also logged in sequential mode
                    log = log_parameters(
                        processor_id=processor_id, parameter_dict=parameter_dict
                    )
                    logs.append(log)

                    # Figure out current coordinate
                    coordinate = str(list(parameter_dict)[0])
                    # Check for overflow to next parameter
                    if index == 0:
                        dataset_dict.update({short(coordinate): []})
                        step_counter += 1

                    # run the pipeline
                    result_proc = proc.run_pipeline()

                    _ = self.outputs.save_to_file(processor=result_proc)

                    # save sequential parameter with appropriate index
                    parameter_ds = parameter_to_dataset(
                        parameter_dict=parameter_dict,
                        index=index,
                        coordinate_name=coordinate,
                    )
                    parameters[step_counter].append(parameter_ds)

                    # save data, use simple or multi coordinate+index
                    ds = _sequential_dataset(
                        processor=result_proc,
                        parameter_dict=parameter_dict,
                        index=index,
                        coordinate_name=coordinate,
                        types=types,
                    )
                    dataset_dict[short(coordinate)].append(ds)

                # merging/combining the outputs
                final_logs = xr.combine_by_coords(logs)
                final_datasets = {
                    key: xr.combine_by_coords(value)
                    for key, value in dataset_dict.items()
                }
                final_parameters_list = [xr.combine_by_coords(p) for p in parameters]
                final_parameters_merged = xr.merge(final_parameters_list)

                result = ParametricResult(
                    dataset=final_datasets,
                    parameters=final_parameters_merged,
                    logs=final_logs,
                )

                return result

            elif self.parametric_mode == ParametricMode.Custom:

                # prepare lists for to-be-merged datasets
                dataset_list = []
                logs = []

                for proc, index, parameter_dict in tqdm(self._processors_it(processor)):
                    # log parameters for this pipeline
                    log = log_parameters(
                        processor_id=index, parameter_dict=parameter_dict
                    )
                    logs.append(log)

                    # run the pipeline
                    result_proc = proc.run_pipeline()

                    _ = self.outputs.save_to_file(processor=result_proc)

                    # save data for pipeline index
                    ds = _custom_dataset(processor=result_proc, index=index)
                    dataset_list.append(ds)

                # merging/combining the outputs
                final_ds = xr.combine_by_coords(dataset_list)
                final_log = xr.combine_by_coords(logs)
                final_parameters = final_log  # parameter dataset same as logs

                result = ParametricResult(
                    dataset=final_ds, parameters=final_parameters, logs=final_log
                )

                return result

            else:
                raise ValueError("Parametric mode not specified.")

    def debug_parameters(self, processor: "Processor") -> list:
        """List the parameters using processor parameters in processor generator.

        Parameters
        ----------
        processor: Processor

        Returns
        -------
        result: list
        """
        result = []
        processor_generator = self._processors_it(processor=processor)
        for i, (proc, _, _) in enumerate(processor_generator):
            values = []
            for step in self.enabled_steps:
                _, att = get_obj_att(proc, step.key)
                value = get_value(proc, step.key)
                values.append((att, value))
            logging.debug("%d: %r" % (i, values))
            result.append((i, values))
        return result


def create_new_processor(processor: "Processor", parameter_dict: dict) -> "Processor":
    """Create a copy of processor and set new attributes from a dictionary before returning it.

    Parameters
    ----------
    processor: Processor
    parameter_dict: dict

    Returns
    -------
    new_processor: Processor
    """

    new_processor = deepcopy(processor)

    for key in parameter_dict.keys():
        new_processor.set(key=key, value=parameter_dict[key])

    return new_processor


def _id(s: str) -> str:
    """Add _id to the end of a string.

    Parameters
    ----------
    s: str

    Returns
    -------
    out: str
    """
    out = s + "_id"
    return out


def short(s: str) -> str:
    """Split string with . and return the last element.

    Parameters
    ----------
    s: str

    Returns
    -------
    out: str
    """
    out = s.split(".")[-1]
    return out


def log_parameters(processor_id: int, parameter_dict: dict) -> xr.Dataset:
    """Return parameters in the current processor in a xarray dataset.

    Parameters
    ----------
    processor_id: int
    parameter_dict: dict

    Returns
    -------
    out: xr.Dataset
    """
    out = xr.Dataset()
    for key, value in parameter_dict.items():
        da = xr.DataArray(value)
        da = da.assign_coords(coords={"id": processor_id})
        da = da.expand_dims(dim="id")
        out[short(key)] = da
    return out


def parameter_to_dataset(
    parameter_dict: dict, index: int, coordinate_name: str
) -> xr.Dataset:
    """Return a specific parameter dataset from a parameter dictionary.

    Parameters
    ----------
    parameter_dict: dict
    index: int
    coordinate_name: str

    Returns
    -------
    parameter_ds: xr.Dataset
    """

    parameter_ds = xr.Dataset()
    parameter = xr.DataArray(parameter_dict[coordinate_name])
    parameter = parameter.assign_coords({short(_id(coordinate_name)): index})
    parameter = parameter.expand_dims(dim=short(_id(coordinate_name)))
    parameter_ds[short(coordinate_name)] = parameter

    return parameter_ds


def _custom_dataset(processor: "Processor", index: int) -> xr.Dataset:
    """Return detector data for a parameter set in a dataset at coordinate "index".

    Parameters
    ----------
    processor: Processor
    index: ind

    Returns
    -------
    ds: xr.Dataset
    """

    rows, columns = (
        processor.detector.geometry.row,
        processor.detector.geometry.row,
    )
    coordinates = {"x": range(columns), "y": range(rows)}

    arrays = {
        "pixel": "detector.pixel.array",
        "signal": "detector.signal.array",
        "image": "detector.image.array",
    }

    ds = xr.Dataset()

    for key, array in arrays.items():

        da = xr.DataArray(
            operator.attrgetter(array)(processor),
            dims=["y", "x"],
            coords=coordinates,  # type: ignore
        )
        da = da.assign_coords({"id": index})
        da = da.expand_dims(dim="id")
        ds[key] = da

    return ds


def _sequential_dataset(
    processor: "Processor",
    parameter_dict: dict,
    index: int,
    coordinate_name: str,
    types: dict,
) -> xr.Dataset:
    """Return detector data for an sequential parameter in a xarray dataset using true coordinates or index.

    Parameters
    ----------
    processor: Processor
    parameter_dict: dict
    index: int
    coordinate_name: str
    types: dict

    Returns
    -------
    ds: xr.Dataset
    """

    rows, columns = (
        processor.detector.geometry.row,
        processor.detector.geometry.row,
    )
    coordinates = {"x": range(columns), "y": range(rows)}

    ds = xr.Dataset()

    arrays = {
        "pixel": "detector.pixel.array",
        "signal": "detector.signal.array",
        "image": "detector.image.array",
    }

    for key, array in arrays.items():

        da = xr.DataArray(
            operator.attrgetter(array)(processor),
            dims=["y", "x"],
            coords=coordinates,  # type: ignore
        )

        #  assigning the right coordinates based on type
        if types[coordinate_name] == ParameterType.Simple:
            da = da.assign_coords(
                coords={short(coordinate_name): parameter_dict[coordinate_name]}
            )
            da = da.expand_dims(dim=short(coordinate_name))

        elif types[coordinate_name] == ParameterType.Multi:
            da = da.assign_coords({short(_id(coordinate_name)): index})
            da = da.expand_dims(dim=short(_id(coordinate_name)))

        ds[key] = da

    return ds


def _product_dataset(
    processor: "Processor", parameter_dict: dict, indices: t.Tuple[int], types: dict
) -> xr.Dataset:
    """Return detector data for an product parameter set in a xarray dataset using true coordinates or indices.

    Parameters
    ----------
    processor: Processor
    parameter_dict: dict
    indices: tuple
    types: dict

    Returns
    -------
    ds: xr.Dataset
    """

    rows, columns = (
        processor.detector.geometry.row,
        processor.detector.geometry.row,
    )
    coordinates = {"x": range(columns), "y": range(rows)}

    arrays = {
        "pixel": "detector.pixel.array",
        "signal": "detector.signal.array",
        "image": "detector.image.array",
    }

    ds = xr.Dataset()

    for key, array in arrays.items():

        da = xr.DataArray(
            operator.attrgetter(array)(processor),
            dims=["y", "x"],
            coords=coordinates,  # type: ignore
        )

        for i, coordinate in enumerate(parameter_dict):

            #  assigning the right coordinates based on type
            if types[coordinate] == ParameterType.Simple:
                da = da.assign_coords(
                    coords={short(coordinate): parameter_dict[coordinate]}
                )
                da = da.expand_dims(dim=short(coordinate))

            elif types[coordinate] == ParameterType.Multi:
                da = da.assign_coords({short(_id(coordinate)): indices[i]})
                da = da.expand_dims(dim=short(_id(coordinate)))

            else:
                raise NotImplementedError

        ds[key] = da

    return ds

    # processors_it = self.collect(processor)  # type: t.Iterator[Processor]
    #
    # result_list = []  # type: t.List[Result]
    # output_filenames = []  # type: t.List[t.Sequence[Path]]
    #
    # # Run all pipelines
    # for proc in tqdm(processors_it):  # type: Processor
    #
    #     if not self.with_dask:
    #         result_proc = proc.run_pipeline()  # type: Processor
    #         result_val = self.outputs.extract_func(
    #             processor=result_proc
    #         )  # type: Result
    #
    #         # filenames = parametric_outputs.save_to_file(
    #         #    processor=result_proc
    #         # )  # type: t.Sequence[Path]
    #
    #     else:
    #         result_proc = delayed(proc.run_pipeline)()
    #         result_val = delayed(self.outputs.extract_func)(processor=result_proc)
    #
    #         # filenames = delayed(parametric_outputs.save_to_file)(processor=result_proc)
    #
    #     result_list.append(result_val)
    #     # output_filenames.append(filenames)  # TODO: This is not used
    #
    # if not self.with_dask:
    #     plot_array = self.outputs.merge_func(result_list)  # type: np.ndarray
    # else:
    #     array = delayed(self.outputs.merge_func)(result_list)
    #     plot_array = dask.compute(array)
    #
    # # TODO: Plot with dask ?
    # # if parametric_outputs.parametric_plot is not None:
    # #    parametric_outputs.plotting_func(plot_array)
