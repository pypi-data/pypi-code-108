# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for handling SDK dependencies required during Ensemble iterations."""
from asyncio import CancelledError
import logging
from typing import Any

from azureml import _async  # type: ignore
from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import ArgumentBlankOrEmpty
from azureml.core import Run
from azureml.exceptions import AzureMLException

from azureml.automl.core.shared import logging_utilities
from azureml.automl.runtime import ensemble_base
from azureml.automl.runtime._run_history.run_history_managers import RunHistoryManagerFactory
from azureml.train.automl import _logging  # type: ignore
from azureml.train.automl._azureautomlsettings import AzureAutoMLSettings
from azureml.train.automl.exceptions import ConfigException


logger = logging.getLogger(__name__)


class EnsembleHelper(object):
    """
    Helper class for ensembling previous AutoML iterations.

    This helper class is used for handling SDK dependencies used during Ensemble iterations (like model downloading)


    :param automl_settings: The settings for this current experiment
    :param ensemble_run_id: The id of the current ensembling run
    :param experiment_name: The name of the current Azure ML experiment
    :param workspace_name: The name of the current Azure ML workspace where the experiment is run
    :param subscription_id: The id of the current Azure ML subscription where the experiment is run
    :param resource_group_name: The name of the current Azure resource group
    """

    DEFAULT_DOWNLOAD_MODELS_TIMEOUT_IN_SEC = 5 * 60  # 5 minutes
    DEFAULT_MODEL_DOWNLOAD_WORKERS_COUNT = None

    def __init__(self,
                 automl_settings: AzureAutoMLSettings,
                 ensemble_run_id: str,
                 experiment_name: str,
                 workspace_name: str,
                 subscription_id: str,
                 resource_group_name: str):
        """Create an Ensemble pipeline out of a collection of already fitted pipelines.

        :param automl_settings: The settings for this current experiment
        :param ensemble_run_id: The id of the current ensembling run
        :param experiment_name: The name of the current Azure ML experiment
        :param workspace_name: The name of the current Azure ML workspace where the experiment is run
        :param subscription_id: The id of the current Azure ML subscription where the experiment is run
        :param resource_group_name: The name of the current Azure resource group
        """
        # input validation
        EnsembleHelper._check_preconditions(automl_settings, "automl_settings")
        EnsembleHelper._check_preconditions(ensemble_run_id, "ensemble_run_id")
        EnsembleHelper._check_preconditions(subscription_id, "subscription_id")
        EnsembleHelper._check_preconditions(resource_group_name, "resource_group_name")
        EnsembleHelper._check_preconditions(workspace_name, "workspace_name")

        self._automl_settings = automl_settings
        self._ensemble_run_id = ensemble_run_id
        self._subscription_id = subscription_id
        self._resource_group_name = resource_group_name
        self._workspace_name = workspace_name

        parent_run_id_length = self._ensemble_run_id.rindex("_")
        self._parent_run_id = self._ensemble_run_id[0:parent_run_id_length]

        # for potentially large models, we should allow users to override this timeout
        if hasattr(self._automl_settings, "ensemble_download_models_timeout_sec"):
            # TODO: Can this be converted into a real attribute?
            self._download_models_timeout_sec = \
                self._automl_settings.ensemble_download_models_timeout_sec
        else:
            self._download_models_timeout_sec = self.DEFAULT_DOWNLOAD_MODELS_TIMEOUT_IN_SEC

    def download_fitted_models_for_child_runs(self, child_runs, model_remote_path):
        """Override the base implementation for downloading the fitted pipelines in an async manner.

        :param child_runs: collection of child runs for which we need to download the pipelines
        :param model_remote_path: the remote path where we're downloading the pipelines from
        """
        with _async.WorkerPool(max_workers=self.DEFAULT_MODEL_DOWNLOAD_WORKERS_COUNT) as worker_pool:
            task_queue = _async.TaskQueue(worker_pool=worker_pool,
                                          _ident="download_fitted_models",
                                          _parent_logger=logger)
            index = 0
            tasks = []
            for run in child_runs:
                task = task_queue.add(
                    ensemble_base.EnsembleBase._download_model,
                    run,
                    index,
                    model_remote_path
                )
                tasks.append(task)
                index += 1
            try:
                task_queue.flush(source=task_queue.identity, timeout_seconds=self._download_models_timeout_sec)
            except AzureMLException as e:
                logging_utilities.log_traceback(e, logger, is_critical=False)

                # cancel all pending async tasks
                in_flight_downloads = 0
                for task in tasks:
                    if not task.done():
                        cancellation_result = task.cancel()
                        if not cancellation_result:
                            in_flight_downloads += 1
                msg = "Failed to download {} models within {} seconds."
                msg += "Downloaded {} models so far, {} are in progress"
                logger.warning(msg.format(len(tasks),
                                          self._download_models_timeout_sec,
                                          len(list(task_queue.results)),
                                          in_flight_downloads))

            results = []
            for task in tasks:
                # this will result in waiting for any in-flight download to finish
                # the ones we successfully cancelled will raise right away a CancelledError
                try:
                    result = task.wait()
                    results.append(result)
                except CancelledError:
                    # if the task gets cancelled then this exception will be CancelledError
                    pass
                except Exception as ex:
                    # if the task fails with an exception, then that will be re-raised here upon task.wait()
                    logging_utilities.log_traceback(ex, logger, is_critical=False)
            return results

    def get_ensemble_and_parent_run(self):
        """Return a tuple (ensemble_run_instance, parent_run_instance)."""

        # we'll instantiate the current run from the environment variables
        ensemble_run = RunHistoryManagerFactory.get_run_history_manager().get_context()

        parent_run = None
        if isinstance(ensemble_run, Run):
            parent_run = Run(ensemble_run.experiment, self._parent_run_id)

        return ensemble_run, parent_run

    def get_logger(self):
        """Return a logger instance."""
        return logger

    @staticmethod
    def _check_preconditions(val: Any, name: str) -> None:
        if val is None:
            raise ConfigException._with_error(
                AzureMLError.create(ArgumentBlankOrEmpty, target=name, argument_name=name)
            )
