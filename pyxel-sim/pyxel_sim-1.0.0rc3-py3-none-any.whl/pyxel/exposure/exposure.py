#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
"""Observation class and functions."""

import logging
import operator
import typing as t

import numpy as np
from tqdm.auto import tqdm
from typing_extensions import Literal

from pyxel.exposure import Readout
from pyxel.pipelines import ResultType, result_keys

if t.TYPE_CHECKING:
    import xarray as xr

    from pyxel.outputs import CalibrationOutputs, ExposureOutputs, ObservationOutputs
    from pyxel.pipelines import Processor


class Exposure:
    """TBW."""

    def __init__(
        self,
        outputs: "ExposureOutputs",
        readout: "Readout",
        result_type: Literal["image", "signal", "pixel", "all"] = "all",
        pipeline_seed: t.Optional[int] = None,
    ):
        self.outputs = outputs
        self.readout = readout
        self._result_type = ResultType(result_type)
        self._pipeline_seed = pipeline_seed

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__  # type: str
        return f"{cls_name}<outputs={self.outputs!r}>"

    @property
    def result_type(self) -> ResultType:
        """TBW."""
        return self._result_type

    @result_type.setter
    def result_type(self, value: ResultType) -> None:
        """TBW."""
        self._result_type = value

    @property
    def pipeline_seed(self) -> t.Optional[int]:
        """TBW."""
        return self._pipeline_seed

    @pipeline_seed.setter
    def pipeline_seed(self, value: t.Optional[int]) -> None:
        """TBW."""
        self._pipeline_seed = value

    def run_exposure(self, processor: "Processor") -> "xr.Dataset":
        """Run a an observation pipeline.

        Parameters
        ----------
        processor : Processor

        Returns
        -------
        Dataset
        """
        progressbar = self.readout._num_steps != 1
        y = range(processor.detector.geometry.row)
        x = range(processor.detector.geometry.col)
        times = self.readout.times

        # Unpure changing of processor
        _ = run_exposure_pipeline(
            processor=processor,
            readout=self.readout,
            outputs=self.outputs,
            progressbar=progressbar,
            result_type=self.result_type,
            pipeline_seed=self.pipeline_seed,
        )

        return processor.result_to_dataset(
            x=x, y=y, times=times, result_type=self.result_type
        )


def run_exposure_pipeline(
    processor: "Processor",
    readout: "Readout",
    outputs: t.Optional[
        t.Union["CalibrationOutputs", "ObservationOutputs", "ExposureOutputs"]
    ] = None,
    progressbar: bool = False,
    result_type: ResultType = ResultType.All,
    pipeline_seed: t.Optional[int] = None,
) -> "Processor":
    """Run standalone exposure pipeline.

    Parameters
    ----------
    pipeline_seed: int
        Random seed for the pipeline.
    result_type: ResultType
    processor: Processor
    readout: Readout
    outputs: DynamicOutputs
        Sampling outputs.
    progressbar: bool
        Sets visibility of progress bar.

    Returns
    -------
    processor: Processor
    """
    # if isinstance(detector, CCD):
    #    dynamic.non_destructive_readout = False

    np.random.seed(seed=pipeline_seed)

    num_steps = readout._num_steps
    ndreadout = readout.non_destructive
    times_linear = readout._times_linear
    start_time = readout._start_time
    end_time = readout._times[-1]
    time_step_it = readout.time_step_it()

    detector = processor.detector

    detector.set_readout(
        num_steps=num_steps,
        ndreadout=ndreadout,
        times_linear=times_linear,
        start_time=start_time,
        end_time=end_time,
    )
    # The detector should be reset before exposure
    detector.empty()

    if progressbar:
        pbar = tqdm(total=num_steps)

    keys = result_keys(result_type)

    unstacked_result = {key: [] for key in keys}  # type: t.Mapping[str, list]

    for i, (time, step) in enumerate(
        time_step_it
    ):  # type: t.Tuple[int, t.Tuple[float, float]]

        detector.time = time
        detector.time_step = step

        logging.info("time = %.3f s", time)

        if detector.non_destructive_readout:
            detector.empty(empty_all=False)
        else:
            detector.empty(empty_all=True)

        processor.run_pipeline()
        detector.pipeline_count = i

        if outputs and detector.read_out:
            outputs.save_to_file(processor)

        for key in keys:
            unstacked_result[key].append(np.array(operator.attrgetter(key)(detector)))

        if progressbar:
            pbar.update(1)

    processor.result = {key: np.stack(unstacked_result[key]) for key in keys}

    if progressbar:
        pbar.close()

    return processor
