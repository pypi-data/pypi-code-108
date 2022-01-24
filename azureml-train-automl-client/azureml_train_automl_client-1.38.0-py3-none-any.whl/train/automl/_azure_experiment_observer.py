# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Console interface for AutoML experiments logs."""
from typing import Optional, TextIO
import logging
from . import constants
from azureml.automl.core._experiment_observer import ExperimentObserver, ExperimentStatus
from azureml.automl.core.shared import logging_utilities
from azureml.core import Run


_logger = logging.getLogger(__name__)


class AzureExperimentObserver(ExperimentObserver):
    """Observer pattern implementation for the states of an AutoML Experiment."""

    def __init__(self, run_instance: Run, console_logger: Optional[TextIO] = None,
                 upload_metrics: bool = True) -> None:
        """Initialize an instance of this class.

        :param run_instance: A Run object representing the current experiment.
        :param console_logger: The destination for sending the status output to.
        :param upload_metrics: Whether to upload metrics to the parent run to track progress and status.
        """
        super(AzureExperimentObserver, self).__init__(console_logger)
        self.run_instance = run_instance
        self._upload_metrics = upload_metrics

    def report_status(self, status: ExperimentStatus, description: str, carriage_return: bool = False) -> None:
        """Report the current status for an experiment.

        :param status: An ExperimentStatus enum value representing current status.
        :param description: A description for the associated experiment status.
        :param carriage_return: Whether or not escape character should be a
        carriage return, bool.
        """
        try:
            super(AzureExperimentObserver, self).report_status(status, description)
            if self._upload_metrics:
                self.run_instance.log(constants.ExperimentObserver.EXPERIMENT_STATUS_METRIC_NAME, str(status))
                self.run_instance.log(
                    constants.ExperimentObserver.EXPERIMENT_STATUS_DESCRIPTION_METRIC_NAME, description)
        except Exception as ex:
            self.report_error(ex)

    def report_progress(self, status: ExperimentStatus, progress: float,
                        carriage_return: bool = False) -> None:
        """Report the current progress for an experiment. Logs progress as a metric not
        as a tag and allows for a carriage return escape character.

        :param status: An ExperimentStatus enum value representing current status.
        :param progress: Progress of the experiment step as a percentage.
        :param carriage_return: Whether or not escape character should be a
        carriage return, bool.
        """
        try:
            description = "{:.1f} %".format(progress)
            super(AzureExperimentObserver, self).report_status(status, description, carriage_return)
            if self._upload_metrics:
                self.run_instance.log(status, progress)
        except Exception as ex:
            self.report_error(ex)

    def report_error(self, ex: Exception) -> None:
        """Log the occurrence of an exception while reporting status."""
        _logger.warning("Error while updating experiment progress.")
        logging_utilities.log_traceback(ex, _logger, is_critical=False)
