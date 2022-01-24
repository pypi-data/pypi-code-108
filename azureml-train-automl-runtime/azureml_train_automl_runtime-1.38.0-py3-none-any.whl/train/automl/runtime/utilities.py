# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Contains utility methods used in automated ML in Azure Machine Learning."""
from typing import Any, Dict, List, Optional, Tuple
from types import ModuleType
from datetime import datetime, timezone
import importlib
import importlib.util
import importlib.abc
import json
import logging
import numbers
import os
from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import NotFound, BadArgument
from azureml.automl.core._run import run_lifecycle_utilities

from azureml.automl.core.shared._diagnostics.automl_error_definitions import InvalidArgumentType, MethodNotFound, \
    DataScriptNotFound
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.core import Run
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared.exceptions import ConfigException
from azureml.automl.runtime._metrics_logging import log_metrics
from azureml.automl.runtime._run_history.offline_automl_run import OfflineAutoMLRun
from azureml.automl.runtime._run_history.run_history_managers.run_manager import RunManager
from azureml.automl.runtime.fit_output import FitOutput
from azureml.train.automl import constants
from azureml.train.automl.runtime._azureautomlruncontext import AzureAutoMLRunContext


logger = logging.getLogger(__name__)


def _load_user_script(script_path: str, calling_in_client_runtime: bool = True) -> ModuleType:
    #  Load user script to get access to GetData function
    logger.info('Loading data using user script.')

    module_name, module_ext = os.path.splitext(os.path.basename(script_path))
    if module_ext != '.py':
        raise ConfigException._with_error(
            AzureMLError.create(
                InvalidArgumentType, target="data_script", argument=script_path,
                actual_type=module_ext, expected_types=".py")
        )
    spec = importlib.util.spec_from_file_location('get_data', script_path)
    if spec is None:
        raise ConfigException(
            azureml_error=AzureMLError.create(DataScriptNotFound, target="data_script", script_path=script_path),
        )

    module_obj = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        raise ConfigException._with_error(
            AzureMLError.create(
                InvalidArgumentType, target="data_script", argument=str(spec),
                actual_type="namespace", expected_types="file"
            )
        )

    # exec_module exists on 3.4+, but it's marked optional so we have to assert
    Contract.assert_type(spec.loader, "data_script", importlib.abc.Loader, log_safe=True)
    Contract.assert_true(hasattr(spec.loader, "exec_module"), "Could not load the data script.",
                         "data_script", log_safe=True)
    Contract.assert_non_empty(spec.loader.exec_module, "data_script", log_safe=True)  # type: ignore
    _execute_user_script_object(spec, calling_in_client_runtime, script_path, module_obj)
    return module_obj


def _execute_user_script_object(spec: Any, calling_in_client_runtime: bool, script_path: str, module_obj: Any) -> Any:
    """Execute the loaded user script to obtain the data."""
    try:
        spec.loader.exec_module(module_obj)
    except FileNotFoundError as fe:
        raise ConfigException(
            azureml_error=AzureMLError.create(DataScriptNotFound, target="data_script", script_path=script_path),
            inner_exception=fe
        ) from fe
    except Exception as e:
        logging_utilities.log_traceback(e, logger)
        raise ConfigException(
            azureml_error=AzureMLError.create(
                BadArgument, target="_module_obj", argument_name=script_path,
                reference_code="_execute_user_script_object.module_obj.exception"
            ),
            inner_exception=e
        ) from e

    if not hasattr(module_obj, 'get_data'):
        raise ConfigException._with_error(
            AzureMLError.create(MethodNotFound, target="get_data", method_name="get_data()")
        )

    return module_obj


def _get_run_createdtime_starttime_and_endtime(run: Optional[Run]) -> Tuple[Optional[datetime],
                                                                            Optional[datetime],
                                                                            Optional[datetime]]:
    if run is None:
        return None, None, None

    if isinstance(run, OfflineAutoMLRun):
        # Add timezone information.
        return (run.created_time.replace(tzinfo=timezone.utc),
                run.start_time.replace(tzinfo=timezone.utc) if run.start_time is not None else None,
                run.end_time.replace(tzinfo=timezone.utc) if run.end_time is not None else None)

    def _get_utc_time(datetime_str: Optional[str]) -> Optional[datetime]:
        if datetime_str is not None and isinstance(datetime_str, str):
            try:
                return datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)
            except Exception:
                pass

        return None

    if run._run_dto is None:
        return None, None, None

    created_time_utc = _get_utc_time(run._run_dto.get('created_utc'))
    start_time_utc = _get_utc_time(run._run_dto.get('start_time_utc'))
    end_time_utc = _get_utc_time(run._run_dto.get('end_time_utc'))

    return created_time_utc, start_time_utc, end_time_utc


def _calculate_start_end_times(start_time: datetime, end_time: datetime, run: Optional[Run]) -> Tuple[datetime,
                                                                                                      datetime]:
    _, run_start_time, run_end_time = _get_run_createdtime_starttime_and_endtime(run)
    start_time = run_start_time or start_time.replace(tzinfo=timezone.utc)
    end_time = run_end_time or end_time.replace(tzinfo=timezone.utc)
    return start_time, end_time


def _create_best_run(
    parent_run: Run,
    best_offline_run: OfflineAutoMLRun
) -> Run:
    """When not tracking all child run details, create a single child run in run history for the best child run."""
    parent_run_manager = RunManager.create_from_run(parent_run)

    best_run_id = '{}_{}'.format(parent_run.id, constants.BEST_RUN_ID_SUFFIX)
    best_run = parent_run_manager.create_child_run(
        run_id=best_run_id,
        tags=best_offline_run.get_tags()).run

    # upload metrics to best run
    best_metrics = best_offline_run.get_metrics()
    log_metrics(best_run, best_metrics, flush_metrics=True)

    best_run_context = AzureAutoMLRunContext(best_run)

    # upload files
    file_names = best_offline_run.get_uploaded_file_names()
    file_paths = []
    for file_name in file_names:
        file_path = best_offline_run.get_file_path(file_name)
        file_paths.append(file_path)
    if file_names:
        best_run_context._batch_save_artifact_files(file_names, file_paths)

    # upload properties
    best_properties = best_offline_run.get_properties()
    best_properties.update(best_run_context._get_artifact_id_run_properties())
    if best_properties:
        best_run.add_properties(best_properties)

    # set terminal status
    run_status = best_offline_run.get_status()
    if run_status == constants.Status.Completed:
        best_run.complete()
    elif run_status == constants.Status.Terminated:
        # Many model runs are executed in an Azure managed environment, hence using default of
        # is_aml_compute = True
        exception = best_offline_run.error_details
        run_lifecycle_utilities.fail_run(best_run, exception, is_aml_compute=True)

    return best_run


def _upload_summary_of_iterations(
    parent_run_context: AzureAutoMLRunContext,
    fit_outputs: List[FitOutput]
) -> None:
    """Upload summary of child iterations to the parent run."""
    summary = []  # type: List[Optional[Dict[str, Any]]]
    for fit_output in fit_outputs:
        if fit_output:
            # Only upload numeric run scores.
            # (Run scores can leverage data structures that are not JSON serializble.)
            scores = {}
            if fit_output.scores:
                for name, score in fit_output.scores.items():
                    if isinstance(score, numbers.Number):
                        scores[name] = score

            summary.append({
                'pipeline_script': fit_output.pipeline_script,
                'run_preprocessor': fit_output.run_preprocessor,
                'run_algorithm': fit_output.run_algorithm,
                'scores': scores
            })
        else:
            summary.append(None)

    summary_str = json.dumps(summary)
    try:
        parent_run_context.save_str_output(
            input_str=summary_str,
            remote_path=constants.CHILD_RUNS_SUMMARY_PATH)
    except Exception as e:
        logging_utilities.log_traceback(e, logger)
        logger.warning("Failed to upload summary of iterations to parent run.")
