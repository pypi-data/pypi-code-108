# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Console interface for AutoML experiments logs"""
import json
import logging
import time
from datetime import timedelta, timezone
import math
from typing import Any, cast, Dict, List, Optional, TYPE_CHECKING, Union

from azureml._restclient.constants import RunStatus
from azureml._restclient.models.run_dto import RunDto
from azureml.core import Run
from azureml.automl.core.shared import constants, logging_utilities
from azureml.automl.core.shared.utilities import minimize_or_maximize
from azureml.automl.core._experiment_observer import ExperimentStatus
from azureml.automl.core.console_interface import ConsoleInterface
from azureml.automl.core.console_writer import ConsoleWriter
from . import _constants_azureml
from . import constants as automl_constants
from ._azureautomlsettings import AzureAutoMLSettings
from .exceptions import SystemException

if TYPE_CHECKING:
    from .run import AutoMLRun


class RemoteConsoleInterface:
    """
    Class responsible for printing iteration information to console for a remote run
    """

    def __init__(self,
                 logger: ConsoleWriter,
                 file_logger: Optional[Union[logging.Logger, logging.LoggerAdapter]] = None,
                 check_status_interval: float = 10) -> None:
        """
        RemoteConsoleInterface constructor

        :param logger: Console logger for printing this info
        :param file_logger: Optional file logger for more detailed logs
        :param check_status_interval: Number of seconds to sleep before checking again for status
        """
        self._ci = None             # type: Optional[ConsoleInterface]
        self._console_logger = logger
        self.logger = file_logger
        self.metric_map = {}        # type: Dict[str, Dict[str, float]]
        self.run_map = {}           # type: Dict[str, Any]
        self.best_metric = None
        self._check_status_interval = check_status_interval

    def _init_console_interface(self, parent_run: 'AutoMLRun') -> bool:
        """
        Initialize the console interface once the setup iteration is complete.

        :param parent_run: AutoMLRun object for the parent run
        :return: True if the initialization succeeded, False otherwise
        """
        # If there are any setup errors, print them and exit
        parent_run_status = parent_run.get_status()
        setup_errors = RemoteConsoleInterface._setup_errors(parent_run_status, parent_run.properties)
        if setup_errors:
            if self._ci is None:
                self._ci = ConsoleInterface("score", self._console_logger)
            self._ci.print_line("")
            self._ci.print_error(setup_errors)
            return False

        # Check the local properties first and double check from RH only if it was not found in the cached object
        if _constants_azureml.Properties.PROBLEM_INFO not in parent_run.properties and \
                _constants_azureml.Properties.PROBLEM_INFO not in parent_run.get_properties():
            raise SystemException.create_without_pii('Key "{}" missing from setup run properties'.format(
                _constants_azureml.Properties.PROBLEM_INFO))

        problem_info_str = parent_run.properties[_constants_azureml.Properties.PROBLEM_INFO]
        problem_info_dict = json.loads(problem_info_str)
        subsampling = problem_info_dict.get('subsampling', False)

        self._ci = ConsoleInterface("score", self._console_logger, mask_sampling=not subsampling)
        parent_run._print_guardrails(self._ci)
        self._ci.print_descriptions()
        self._ci.print_columns()

        return True

    def print_scores(self, parent_run: 'AutoMLRun', primary_metric: str) -> None:
        """
        Print all history for a given parent run

        :param parent_run: AutoMLRun to print status for
        :param primary_metric: Metric being optimized for this run
        :return:
        """
        # initialize ConsoleInterface when setup iteration is complete
        if not self._init_console_interface(parent_run):
            return

        best_metric = None  # type: Optional[Union[str, float]]
        automl_settings = AzureAutoMLSettings(
            experiment=None, **json.loads(parent_run.properties['AMLSettingsJsonString']))
        max_concurrency = automl_settings.max_concurrent_iterations

        objective = minimize_or_maximize(metric=primary_metric)

        child_runs_not_finished = RemoteConsoleInterface._get_child_run_ids(
            parent_run.id, automl_settings, parent_run.tags)
        while True:
            runs_to_query = child_runs_not_finished[:max_concurrency]
            if not runs_to_query and RemoteConsoleInterface._is_run_terminal(parent_run.get_status()):
                break   # Finished processing all the runs
            if automl_settings.track_child_runs is False and (
                    parent_run.status == RunStatus.FAILED or parent_run.status == RunStatus.CANCELED):
                break

            if runs_to_query is None or runs_to_query == []:
                new_children_dtos = []
            else:
                new_children_dtos = parent_run._client.run.get_runs_by_run_ids(run_ids=runs_to_query)
            # An indicator to check if we processed any children, if not, it means there were no runs to query for
            processed_children = False
            runs_finished = []

            for run in new_children_dtos:
                if not processed_children:
                    processed_children = True
                run_id = run.run_id
                status = run.status
                if run_id not in self.run_map and RemoteConsoleInterface._is_run_terminal(status):
                    runs_finished.append(run_id)
                    self.run_map[run_id] = run

            # Don't re-use `parent_run_status` from above, as the status can constantly be mutating
            if not processed_children and RemoteConsoleInterface._is_run_terminal(parent_run.get_status()):
                # We got no child runs and the parent is completed - we are done with all the children.
                break

            if runs_finished:
                runs_finished.sort()
                run_metrics_map = parent_run._client.get_metrics(run_ids=runs_finished)

                for run_id in run_metrics_map:
                    self.metric_map[run_id] = run_metrics_map[run_id]

                for run_id in runs_finished:
                    if "setup" in run_id:
                        continue
                    run = self.run_map[run_id]
                    properties = run.properties
                    current_iter = properties.get('iteration', None)
                    # Bug-393631
                    if current_iter is None:
                        continue
                    run_metric = self.metric_map.get(run_id, {})
                    run_preprocessor = properties.get('run_preprocessor', "")
                    run_algorithm = properties.get('run_algorithm', "")
                    training_frac = properties.get('training_percent', 100)
                    # in case training_percent was set to None, default it back to 100%
                    if training_frac is None:
                        training_frac = 1.0
                    else:
                        training_frac = float(training_frac) / 100

                    start_iter_time = run.start_time_utc.replace(tzinfo=timezone.utc)

                    end_iter_time = run.end_time_utc.replace(tzinfo=timezone.utc)

                    iter_duration = str(RemoteConsoleInterface._round_timedelta_to_nearest_second(
                        end_iter_time - start_iter_time))

                    if primary_metric in run_metric:
                        score = run_metric[primary_metric]
                    else:
                        score = constants.Defaults.DEFAULT_PIPELINE_SCORE

                    is_unknown = False
                    if best_metric is None or RemoteConsoleInterface._is_bad_metric(best_metric):
                        best_metric = score
                    else:
                        best_metric_converted = float(best_metric)  # type: float
                        if objective == constants.OptimizerObjectives.MINIMIZE:
                            if score < best_metric_converted:
                                best_metric_converted = score
                        elif objective == constants.OptimizerObjectives.MAXIMIZE:
                            if score > best_metric_converted:
                                best_metric_converted = score
                        else:
                            is_unknown = True

                        if is_unknown:
                            best_metric = "Unknown"
                        else:
                            best_metric = best_metric_converted

                    if self._ci is not None:
                        self._ci.print_start(current_iter)
                        self._ci.print_pipeline(run_preprocessor, run_algorithm, training_frac)
                        self._ci.print_end(iter_duration, score, best_metric)

                    error = None
                    if isinstance(run, Run):
                        error = run.get_details().get('error')
                    elif isinstance(run, RunDto):
                        error = run.error

                    if error:
                        if self._ci is not None:
                            self._ci.print_error(error)
                    if run_id in child_runs_not_finished:
                        child_runs_not_finished.remove(run_id)

            time.sleep(self._check_status_interval)

    def print_pre_training_progress(self, parent_run: 'AutoMLRun',
                                    file_logger: Optional[Union[logging.Logger, logging.LoggerAdapter]] = None
                                    ) -> None:
        """
        Print pre-training progress during an experiment.

        :param parent_run: the parent run to print status for.
        :return: None
        """
        max_retry_count = 3
        retry_count = 1

        self._console_logger.println()
        last_experiment_status = None  # type: Optional[str]
        last_progress_update = -1  # type: float

        while True:
            try:
                tags = parent_run.get_tags()

                status = tags.get('_aml_system_automl_status', None)
                if status is None:
                    status = parent_run.get_status()
                if RemoteConsoleInterface._is_run_terminal(status):
                    break

                experiment_status = self.get_updated_metric(
                    parent_run, automl_constants.ExperimentObserver.EXPERIMENT_STATUS_METRIC_NAME)

                status_description = self.get_updated_metric(
                    parent_run, automl_constants.ExperimentObserver.EXPERIMENT_STATUS_DESCRIPTION_METRIC_NAME)

                if experiment_status is not None and status_description is not None:
                    if experiment_status != last_experiment_status:
                        self._console_logger.println(
                            "\rCurrent status: {}. {}".format(experiment_status, status_description))
                        last_experiment_status = cast(str, experiment_status)

                    elif experiment_status == str(ExperimentStatus.TextDNNTraining):
                        curr_progress = cast(Optional[float], self.get_updated_metric(
                            parent_run, str(ExperimentStatus.TextDNNTrainingProgress)))

                        if curr_progress is not None and curr_progress > last_progress_update:
                            experiment_status = str(ExperimentStatus.TextDNNTrainingProgress)
                            self._console_logger.print(
                                "\rCurrent status: {}. {}%".format(experiment_status, round(curr_progress)),
                                carriage_return=True)
                            last_progress_update = curr_progress

                # Break out if the setup phase finished successfully,
                # identified by checking for the presence of ProblemInfo in the run's properties
                if _constants_azureml.Properties.PROBLEM_INFO in parent_run.get_properties():
                    break
                time.sleep(self._check_status_interval)

                # reset the retry counter for exceptions every time we sleep
                retry_count = 1
            except Exception as e:
                logging_utilities.log_traceback(e, file_logger)
                if (retry_count >= max_retry_count):
                    break
                retry_count += 1

    def get_updated_metric(self, run: 'AutoMLRun', metric_name: str) -> Optional[Union[str, float, int]]:
        """
        Retrieve the most recent value of a metric from the run with
        the supplied metric name.

        :param run: the run to retrieve the metric from
        :param metric_name: the name of the metric to retrieve
        :return: None if no metrics available, or the most recent metric
        """
        metrics_dict = run.get_metrics(metric_name)
        # check if metric is actually logged, if not return none
        ret = None  # type: Optional[Union[str, float, int]]
        if metrics_dict == {}:
            return ret

        # retrieve metric from dict. This will be safe because we've only asked for a single metric name
        metric = metrics_dict[metric_name]

        # if metric is list retrieve last update, otherwise return value
        if isinstance(metric, list):
            ret = metric[-1]
        else:
            ret = metric
        return ret

    def print_auto_parameters(self, parent_run: 'AutoMLRun') -> None:
        """
        Print the heiristic parameters if they were set.

        :param parent_run: the parent run to print status for.
        :return: None
        """
        try:
            message = parent_run.tags.get('auto', None)
            if message is not None:
                self._console_logger.println(message)
        except Exception:
            pass

    @staticmethod
    def _is_run_terminal(status: str) -> bool:
        return status in [RunStatus.COMPLETED, RunStatus.FAILED, RunStatus.CANCELED]

    @staticmethod
    def _get_child_run_ids(
        parent_run_id: str,
        automl_settings: AzureAutoMLSettings,
        tags: Dict[str, str]
    ) -> List[str]:
        if automl_settings.track_child_runs is False:
            return ['{}_{}'.format(parent_run_id, automl_constants.BEST_RUN_ID_SUFFIX)]

        total_children_count = int(tags.get('iterations', "0"))
        if total_children_count == 0:
            total_children_count = automl_settings.iterations

        child_run_ids = []
        i = 0
        while i < total_children_count:
            child_run_ids.append('{}_{}'.format(parent_run_id, i))
            i += 1
        return child_run_ids

    @staticmethod
    def _get_setup_run(parent_run: 'AutoMLRun') -> 'AutoMLRun':
        setup_run_list = list(parent_run._client.run.get_runs_by_run_ids(
            run_ids=['{}_{}'.format(parent_run.run_id, 'setup')]))
        # if this is a local run there will be no setup iteration
        if len(setup_run_list) == 0:
            setup_run = parent_run
        else:
            setup_run = setup_run_list[0]
        return setup_run

    @staticmethod
    def _setup_errors(parent_run_status: str, parent_run_properties: Dict[str, Any]) -> Optional[Any]:
        """Return any setup errors that may have occurred in the parent run."""
        parent_run_status = parent_run_status
        if RemoteConsoleInterface._is_run_terminal(parent_run_status):
            parent_errors = parent_run_properties.get('errors')
            if parent_errors is not None and parent_errors.startswith("Setup iteration failed"):
                return parent_errors
        return None

    @staticmethod
    def _show_output(current_run: 'AutoMLRun',
                     logger: ConsoleWriter,
                     file_logger: Optional[Union[logging.Logger, logging.LoggerAdapter]],
                     primary_metric: str) -> None:
        try:
            remote_printer = RemoteConsoleInterface(logger, file_logger)
            remote_printer.print_pre_training_progress(current_run, file_logger)
            remote_printer.print_auto_parameters(current_run)
            remote_printer.print_scores(current_run, primary_metric)
        except KeyboardInterrupt:
            logger.write("Received interrupt. Returning now.")
        except Exception as e:
            logging_utilities.log_traceback(e, file_logger)
            logger.write("Something went wrong while printing the experiment progress "
                         "but the run is still executing on the compute target. \n"
                         "Please check portal for updated status: {0}\n".format(
                             current_run.get_portal_url())
                         )

    @staticmethod
    def _round_timedelta_to_nearest_second(td: timedelta) -> timedelta:
        if td.microseconds >= timedelta(seconds=0.5).microseconds:
            td += timedelta(seconds=1)
        td -= timedelta(microseconds=td.microseconds)
        return td

    @staticmethod
    def _is_bad_metric(metric):
        return metric in [None, 'nan', 'NaN'] or (isinstance(metric, float) and math.isnan(metric))
