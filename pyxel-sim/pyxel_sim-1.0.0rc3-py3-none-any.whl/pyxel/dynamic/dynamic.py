#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
"""TBW."""

import logging
import operator
import typing as t

import numpy as np
import xarray as xr
from tqdm.notebook import tqdm

from pyxel.evaluator import eval_range
from pyxel.inputs_outputs import load_table

if t.TYPE_CHECKING:
    from ..inputs_outputs import DynamicOutputs
    from ..pipelines import Processor


class Dynamic:
    """TBW."""

    def __init__(
        self,
        outputs: "DynamicOutputs",
        times: t.Optional[t.Union[t.Sequence, str]] = None,
        times_from_file: t.Optional[str] = None,
        start_time: float = 0.0,
        non_destructive_readout: bool = False,
    ):
        """Create an instance of Sampling class.

        Parameters
        ----------
        outputs
        times
        times_from_file
        start_time
        non_destructive_readout
        """
        self.outputs = outputs

        if times is not None and times_from_file is not None:
            raise ValueError("Both times and times_from_file specified. Choose one.")
        elif times_from_file:
            self._times = load_table(times_from_file).to_numpy(dtype=float).flatten()
        elif times:
            self._times = np.array(eval_range(times), dtype=float)
        else:
            raise ValueError("Sampling times not specified.")

        self._non_destructive_readout = non_destructive_readout

        self._times_linear = True  # type: bool
        self._start_time = start_time  # type:float
        self._steps = np.array([])  # type: np.ndarray
        self._num_steps = 0  # type: int

        self._set_steps()

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__  # type: str
        return f"{cls_name}<outputs={self.outputs!r}>"

    def _set_steps(self) -> None:
        """TBW."""
        self._times, self._steps = calculate_steps(self._times, self._start_time)
        self._times_linear = bool(np.all(self._steps == self._steps[0]))
        self._num_steps = len(self._times)

    def time_step_it(self) -> t.Iterator[t.Tuple[float, float]]:
        """TBW."""
        return zip(self._times, self._steps)

    @property
    def times(self) -> t.Any:
        """TBW."""
        return self._times

    @property
    def steps(self) -> np.ndarray:
        """TBW."""
        return self._steps

    @property
    def non_destructive_readout(self) -> bool:
        """TBW."""
        return self._non_destructive_readout

    def run_dynamic(self, processor: "Processor") -> xr.Dataset:
        """TBW."""
        ds = dynamic_pipeline(
            processor=processor,
            time_step_it=self.time_step_it(),
            num_steps=self._num_steps,
            ndreadout=self.non_destructive_readout,
            times_linear=self._times_linear,
            start_time=self._start_time,
            end_time=self._times[-1],
            outputs=self.outputs,
            progressbar=True,
        )
        return ds


def calculate_steps(
    times: np.ndarray, start_time: float
) -> t.Tuple[np.ndarray, np.ndarray]:
    """Calculate time differences for a given array and start time.

    Parameters
    ----------
    times: ndarray
    start_time: float

    Returns
    -------
    times: ndarray
        Modified times according to start time.
    steps: ndarray
        Steps corresponding to times.
    """
    if start_time == times[0]:
        steps = np.diff(times, axis=0)
        times = times[1:]
    else:
        steps = np.diff(
            np.concatenate((np.array([start_time]), times), axis=0),
            axis=0,
        )
    return times, steps


def dynamic_pipeline(
    processor: "Processor",
    time_step_it: t.Iterator[t.Tuple[float, float]],
    num_steps: int,
    times_linear: bool,
    end_time: float,
    start_time: float = 0.0,
    ndreadout: bool = False,
    outputs: t.Optional["DynamicOutputs"] = None,
    progressbar: bool = False,
) -> xr.Dataset:
    """Run standalone dynamic pipeline.

    Parameters
    ----------
    processor: Processor
    time_step_it: Iterator
        Iterates over pairs of times and elapsed time steps.
    num_steps: int
        Number of times.
    ndreadout: bool
        Set non destructive readout mode.
    times_linear: bool
        Set if times are linear.
    start_time: float
        Starting time.
    end_time:
        Last time.
    outputs: DynamicOutputs
        Sampling outputs.
    progressbar: bool
        Sets visibility of progress bar.

    Returns
    -------
    final_dataset: xr.Dataset
        Results of the pipeline in an xarray dataset.
    """
    # if isinstance(detector, CCD):
    #    dynamic.non_destructive_readout = False

    detector = processor.detector

    detector.set_dynamic(
        num_steps=num_steps,
        ndreadout=ndreadout,
        times_linear=times_linear,
        start_time=start_time,
        end_time=end_time,
    )
    # The detector should be reset before exposure
    detector.reset(reset_all=True)

    # prepare lists for to-be-merged datasets
    list_datasets = []

    # Dimensions set by the detectors dimensions
    rows, columns = (
        processor.detector.geometry.row,
        processor.detector.geometry.row,
    )
    # Coordinates
    coordinates = {"x": range(columns), "y": range(rows)}

    if progressbar:
        pbar = tqdm(total=num_steps)

    for i, (time, step) in enumerate(
        time_step_it
    ):  # type: t.Tuple[int, t.Tuple[float, float]]

        detector.time = time
        detector.time_step = step

        logging.info("time = %.3f s", time)

        if detector.non_destructive_readout:
            detector.reset(reset_all=False)
        else:
            detector.reset(reset_all=True)

        processor.run_pipeline()
        detector.pipeline_count = i

        if outputs and detector.read_out:
            outputs.save_to_file(processor)

        out = xr.Dataset()

        # Dataset is storing the arrays at the end of this iter
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
            # Time coordinate of this iteration
            da = da.assign_coords(coords={"t": time})
            da = da.expand_dims(dim="t")

            out[key] = da

        if progressbar:
            pbar.update(1)
        # Append to the list of datasets
        list_datasets.append(out)

    if progressbar:
        pbar.close()

    # Combine the datasets in the list into one xarray
    final_dataset = xr.combine_by_coords(list_datasets)  # type: xr.Dataset

    return final_dataset
