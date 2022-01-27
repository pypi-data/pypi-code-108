#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
"""Timing functions."""

import timeit
import typing as t

import numpy as np
import pandas as pd

if t.TYPE_CHECKING:
    from pyxel.detectors import Detector
    from pyxel.pipelines import DetectionPipeline, ModelFunction, ModelGroup


def _list_of_times_to_dataframe(times: list, model_names: list) -> pd.DataFrame:
    """Convert a list of model times to a dataframe.

    Parameters
    ----------
    times: list
    model_names: list

    Returns
    -------
    df: pd.DataFrame
    """

    times_array = np.array(times) * 1000  # to miliseconds
    times_sum = np.sum(times_array)
    percentages = times_array * 100 / times_sum

    final_times = np.round(np.append(times_array, times_sum), 2)
    percentages = np.round(np.append(percentages, 100.0), 4)

    model_names.append("TOTAL:")

    df = pd.DataFrame({"time [ms]": final_times, "%time": percentages})
    df.index = model_names

    return df


def time_pipeline(detector: "Detector", pipeline: "DetectionPipeline") -> pd.DataFrame:
    """Time a single pipeline.

    Parameters
    ----------
    detector : Detector
    pipeline : DetectionPipeline

    Returns
    -------
    df: DataFrame
    """

    times = []
    model_names = []

    for group_name in pipeline.model_group_names:

        models_grp = getattr(pipeline, group_name)  # type: t.Optional[ModelGroup]

        if models_grp:
            for model in models_grp.models:  # type: ModelFunction
                if model.enabled:
                    model_start = timeit.default_timer()
                    model(detector)
                    model_end = timeit.default_timer()
                    times.append(model_end - model_start)
                    model_names.append(model.name)

    df = _list_of_times_to_dataframe(times, model_names)

    return df
