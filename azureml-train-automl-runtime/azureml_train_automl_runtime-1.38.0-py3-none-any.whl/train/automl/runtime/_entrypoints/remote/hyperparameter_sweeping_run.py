# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods for AutoML Hyperparameter Sweeping Runs."""
import logging
from typing import Any, Dict

from azureml._tracing import get_tracer
from azureml.automl.core.shared.telemetry_activity_logger import TelemetryActivityLogger
from azureml.core import Run
from azureml.train.automl.runtime._entrypoints import remote_training_run_entrypoint
from azureml.train.automl.runtime._hyperparameter_sweeping import generate_pipeline, util

logger = logging.getLogger(__name__)
activity_logger = TelemetryActivityLogger()
tracer = get_tracer(__name__)


def execute(
        script_directory: str,
        automl_settings: str,
        run_id: str,
        training_percent: float,
        iteration: int,
        pipeline_id: str,
        dataprep_json: str,
        entry_point: str,
        **kwargs: Any
) -> Dict[str, Any]:
    """
    Driver script that runs one sweeping iteration
    """
    current_run = Run.get_context()
    result = {}  # type: Dict[str, Any]
    pipeline_spec = generate_pipeline.generate_pipeline_spec(
        automl_settings=automl_settings,
        pipeline_id=pipeline_id)
    util.prepare_properties(
        run=current_run,
        pipeline_spec=pipeline_spec)
    result = remote_training_run_entrypoint.execute(
        script_directory=script_directory,
        automl_settings=automl_settings,
        run_id=run_id,
        training_percent=training_percent,
        iteration=iteration,
        pipeline_spec=pipeline_spec,
        pipeline_id=pipeline_id,
        dataprep_json=dataprep_json,
        entry_point=entry_point
    )
    return result
