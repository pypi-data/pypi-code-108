# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import datetime
import logging
from typing import Any, Dict, Union

import azureml.dataprep as dprep
import pandas as pd
from azureml._tracing._tracer_factory import get_tracer
from azureml.automl.core.shared import constants, logging_utilities as log_utils
from azureml.automl.core.shared.constants import (Sample_Weights_Unsupported)
from azureml.automl.runtime._data_definition import TabularData, LazyTabularData, MaterializedTabularData
from azureml.automl.runtime.shared.nimbus_wrappers import NimbusMlPipelineWrapper
from sklearn.pipeline import Pipeline

logger = logging.getLogger(__name__)
tracer = get_tracer(__name__)


def train(pipeline: Union[Pipeline, NimbusMlPipelineWrapper], training_data: TabularData) -> float:
    """
    train the model that can do predictions

    :param pipeline: The pipeline to run the fit on.
    :param training_data: data on which to train.
    :return: The time elapsed for fit.
    """

    if isinstance(pipeline, NimbusMlPipelineWrapper):
        assert (isinstance(training_data, LazyTabularData))
        return fit_nimbus_pipeline(pipeline, training_data)
    else:
        assert (isinstance(training_data, MaterializedTabularData))
        return fit_scikit_pipeline(pipeline, training_data)


def fit_scikit_pipeline(pipeline: Pipeline, training_data: MaterializedTabularData) -> float:
    """
    Run the fit and calculate the time elapsed.

    :param pipeline: The pipeline to fit.
    :param training_data: Input data.
    :return: The time elapsed for fit.
    """
    with tracer.start_as_current_span(
            constants.TelemetryConstants.SPAN_FORMATTING.format(
                constants.TelemetryConstants.COMPONENT_NAME, constants.TelemetryConstants.TRAINING
            ),
            user_facing_name=constants.TelemetryConstants.TRAINING_USER_FACING
    ):
        with log_utils.log_activity(logger, activity_name=constants.TelemetryConstants.TIME_FIT_NAME):
            t = datetime.datetime.utcnow()  # time.process_time()

            kwargs = {}  # type: Dict[str, Any]
            if isinstance(pipeline, Pipeline) and training_data.weights is not None:
                # get model's name in steps array
                clf = pipeline.steps[-1][0]
                if clf not in Sample_Weights_Unsupported:
                    # pipeline expects kwargs to be formatted as stepname__arg.
                    # The arg is then passed to fit of stepname
                    kwargs = {clf + "__sample_weight": training_data.weights}

            pipeline.fit(training_data.X, training_data.y, **kwargs)
            elapsed_time = datetime.datetime.utcnow() - t

            return elapsed_time.total_seconds()


def fit_nimbus_pipeline(pipeline: NimbusMlPipelineWrapper,
                        training_data: LazyTabularData) -> float:
    """
    Run the fit and calculate the time elapsed.

    :param pipeline: The pipeline to fit.
    :param training_data: data to fit.
    :return: The time elapsed for fit.
    """
    with tracer.start_as_current_span(
            constants.TelemetryConstants.SPAN_FORMATTING.format(
                constants.TelemetryConstants.COMPONENT_NAME, constants.TelemetryConstants.TRAINING
            ),
            user_facing_name=constants.TelemetryConstants.TRAINING_USER_FACING
    ):
        with log_utils.log_activity(logger, activity_name=constants.TelemetryConstants.TIME_FIT_INPUT):
            t = datetime.datetime.utcnow()  # time.process_time()

            kwargs = {}  # type: Dict[str, Any]
            pipeline.fit(training_data.data, output_predictor_model=True, **kwargs)

            elapsed_time = datetime.datetime.utcnow() - t
            return elapsed_time.total_seconds()
