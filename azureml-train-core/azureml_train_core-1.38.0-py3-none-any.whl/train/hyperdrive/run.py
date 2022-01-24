# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""The HyperDrive Run object."""
import warnings
from typing import List, Optional, Tuple

import azureml.train.restclients.hyperdrive as HyperDriveClient
from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore
from azureml._restclient.constants import RunStatus
from azureml.core import Experiment, Run, Workspace
from azureml.exceptions import TrainingException
from azureml.train.hyperdrive import HyperDriveConfig, PrimaryMetricGoal
from azureml.train.hyperdrive.error_definition import HyperDriveNotImplemented
from azureml.train.hyperdrive.exceptions import (
    HyperDriveConfigException, HyperDriveNotImplementedException)
from azureml.train.restclients.hyperdrive.models import ErrorResponseException

from .error_definition import HyperDriveRunCancellationError, InvalidType

# noinspection PyProtectedMember

TERMINAL_STATES = [RunStatus.CANCELED, RunStatus.COMPLETED, RunStatus.FAILED]

scrubbed_data = "[Scrubbed]"


class HyperDriveRun(Run):
    """HyperDriveRun contains the details of a submitted HyperDrive experiment.

    This class can be used to manage, check status, and retrieve run details for the HyperDrive run and each of
    the generated child runs.

    :param experiment: The experiment for the HyperDrive run.
    :type experiment: azureml.core.experiment.Experiment
    :param run_id: The HyperDrive run ID.
    :type run_id: str
    :param hyperdrive_config: The configuration for this HyperDrive run.
    :type hyperdrive_config: azureml.train.hyperdrive.HyperDriveConfig
    """

    RUN_TYPE = 'hyperdrive'
    HYPER_DRIVE_RUN_USER_AGENT = "sdk_run_hyper_drive"

    def __init__(self, experiment, run_id, hyperdrive_config=None):
        """Initialize a HyperDrive run.

        :param experiment: The experiment for the HyperDrive run.
        :type experiment: azureml.core.experiment.Experiment
        :param run_id: The HyperDrive run id.
        :type run_id: str
        :param hyperdrive_config: The configuration for this HyperDrive run.
            If None, we assume that the run already exists and will try to hydrate from the cloud.
        :type hyperdrive_config: azureml.train.hyperdrive.HyperDriveConfig
        """
        if not isinstance(run_id, str):
            raise HyperDriveConfigException._with_error(
                AzureMLError.create(
                    InvalidType, exp="str", obj="run_id", actual=scrubbed_data,
                    target="run_id"
                )
            )

        super().__init__(experiment=experiment, run_id=run_id,
                         _user_agent=HyperDriveRun.HYPER_DRIVE_RUN_USER_AGENT)
        if hyperdrive_config is None:
            self._hyperdrive_config = HyperDriveConfig._get_runconfig_from_run_dto(self._client.run_dto)
        else:
            self._hyperdrive_config = hyperdrive_config

        self._output_logs_pattern = "azureml-logs/hyperdrive.txt"

    @property
    def hyperdrive_config(self):
        """Return the hyperdrive run config.

        :return: The hyperdrive run config.
        :rtype: azureml.train.hyperdrive.HyperDriveConfig
        """
        return self._hyperdrive_config

    def cancel(self):
        """Return True if the HyperDrive run was cancelled successfully.

        :return: Whether or not the run was cancelled successfully.
        :rtype: bool
        """
        project_auth = self.experiment.workspace._auth_object
        run_history_host = self.experiment.workspace.service_context._get_run_history_url()

        host_url = self.hyperdrive_config._get_host_url(self.experiment.workspace, self.experiment.name)
        try:
            # FIXME: remove this fix once hyperdrive code updates ES URL creation
            # project_context.get_experiment_uri_path() gives /subscriptionid/id_value
            # where as hyperdrive expects subscriptionid/id_value
            # project_context.get_experiment_uri_path()
            experiment_uri_path = self.experiment.workspace.service_context. \
                _get_experiment_scope(self.experiment.name)[1:]
            hyperdrive_client = HyperDriveClient.RestClient(experiment_uri_path, project_auth, host_url)

            cancel_hyperdrive_run_result = hyperdrive_client.cancel_experiment(self._run_id, run_history_host)
            return cancel_hyperdrive_run_result
        except ErrorResponseException as e:
            raise TrainingException._with_error(
                AzureMLError.create(
                    HyperDriveRunCancellationError
                ), inner_exception=e
            ) from None

    def get_best_run_by_primary_metric(
            self,
            include_failed=True,
            include_canceled=True,
            include_resume_from_runs=True) -> Optional[Run]:
        """Find and return the Run instance that corresponds to the best performing run amongst all child runs.

        The best performing run is identified solely based on the primary metric parameter specified in the
        HyperDriveConfig. The PrimaryMetricGoal governs whether the minimum or maximum of the primary metric is
        used. To do a more detailed analysis of all the ExperimentRun metrics launched by this HyperDriveRun, use
        get_metrics. Only one of the runs is returned, even if several of the Runs launched by this HyperDrive
        run reached the same best metric.

        :param include_failed: Whether to include failed runs.
        :type include_failed: bool
        :param include_canceled: Whether to include canceled runs.
        :type include_canceled: bool
        :param include_resume_from_runs: Whether to include inherited resume_from runs.
        :type include_resume_from_runs: bool
        :return: The best Run, or None if no child has the primary metric.
        :rtype: azureml.core.run.Run
        """
        if include_resume_from_runs and self.hyperdrive_config._resume_from:
            return self._get_best_from_current_and_inherited(
                include_failed=include_failed, include_canceled=include_canceled)
        else:
            best_child_run, _ = self._get_best_run_and_metric_value(
                include_failed=include_failed, include_canceled=include_canceled)
            return best_child_run

    def _get_best_from_current_and_inherited(self, include_failed, include_canceled) -> Optional[Run]:
        """Find and return the Run instance and metric value corresponding to the best performing run.

        The runs considered include all child runs including resume_from runs.

        :param include_failed: Whether to include failed runs.
        :type include_failed: bool
        :param include_canceled: Whether to include canceled runs.
        :type include_canceled: bool
        :return: The best Run, or None if no child has the primary metric.
        :rtype: azureml.core.run.Run
        """
        child_runs_and_values = []
        child_run, value = self._get_best_run_and_metric_value(
            include_failed=include_failed, include_canceled=include_canceled)

        if child_run and value:
            child_runs_and_values.append((child_run, value))

        for inherited_parent_run_dict in self.hyperdrive_config._resume_from:
            hd_run = HyperDriveRun._rehydrate_run_from_run_key_dict(inherited_parent_run_dict)
            child_run, value = hd_run._get_best_run_and_metric_value(
                include_failed=include_failed, include_canceled=include_canceled)

            if child_run and value:
                child_runs_and_values.append((child_run, value))

        if not child_runs_and_values:
            return None
        else:
            metric_goal = self.hyperdrive_config._primary_metric_config["goal"]  # type: str
            return HyperDriveRun._get_best_child_from_list_of_runs_values(metric_goal, child_runs_and_values)

    def _get_best_run_and_metric_value(self, include_failed: bool, include_canceled: bool):
        """Find and return the Run instance and metric value corresponding to the best performing child run.

        :param include_failed: Whether to include failed runs.
        :type include_failed: bool
        :param include_canceled: Whether to include canceled runs.
        :type include_canceled: bool
        :return: The best Run and its metric value, or (None, None) if no child has the primary metric.
        :rtype: (azureml.core.run.Run, float)
        """
        # Attempt to obtain the best run by primary metric from values cached in parent run metrics
        try:
            best_child_run, value = self._get_best_run_by_primary_metric_stored_in_parent(
                include_failed=include_failed, include_canceled=include_canceled)
            if best_child_run and value is not None:
                return best_child_run, value
        except Exception:
            warnings.formatwarning = _simple_warning
            warnings.warn("An error occurred getting the best run cached in the parent run metrics. "
                          "Falling back to getting metrics from all child runs.")

        # Fall back to getting best by comparing metrics from all child runs
        best_run_id, value = self._get_best_run_id_by_primary_metric(
            include_failed=include_failed, include_canceled=include_canceled)
        if best_run_id and value is not None:
            return Run(self.experiment, best_run_id), value
        else:
            return None, None

    @staticmethod
    def _rehydrate_run_from_run_key_dict(run_key_dict: dict) -> 'HyperDriveRun':
        """Get a HyperDriveRun object from a Run Key dictionary.

        :param run_key_dict: Run Key dictionary containing entries "run_scope" and "run_id". The "run_scope"
            entry contains a dictionary with entries "host", "subscription_id", "resource_group", "workspace_name"
            and "experiment_name".
        :type include_failed: dict
        :return: The HyperDriveRun object represented by the give Run Key dictionary.
        :rtype: azureml.train.hyperdrive.HyperDriveRun
        """
        run_scope = run_key_dict["run_scope"]  # type: dict
        workspace = Workspace(subscription_id=run_scope["subscription_id"],
                              resource_group=run_scope["resource_group"],
                              workspace_name=run_scope["workspace_name"])
        experiment = Experiment(workspace, run_scope["experiment_name"])

        return HyperDriveRun(experiment, run_key_dict["run_id"])

    @staticmethod
    def _get_best_child_from_list_of_runs_values(metric_goal: str,
                                                 child_runs_and_values: List[Tuple[Run, float]]) -> Optional[Run]:
        """Get the best child run from the ones in the given list.

        :param child_runs_and_values: List of tuples of Runs and metric values to compare.
        :type include_failed: list
        :return: The best Run or None if the list is empty..
        :rtype: azureml.core.run.Run
        """
        if not child_runs_and_values:
            return None

        is_maximize = (metric_goal == PrimaryMetricGoal.MAXIMIZE.value.lower())  # type: bool
        sorted_results = sorted(
            child_runs_and_values,
            key=lambda i: i[1],  # Sort by value
            reverse=is_maximize)  # If we want to maximize, larger numbers go first
        child_run, value = sorted_results[0]
        return child_run

    def _get_best_run_by_primary_metric_stored_in_parent(self, include_failed=True, include_canceled=True):
        """Get the best run by primary metric stored in the parent run's metrics.

        The metrics stored there are continuously appended as the experiment progresses if there is a new best. This
        includes all child runs regardless of status, so if a status type is not desired (according this method's
        arguments) and the global best corresponds to such status, then an exhaustive search in all metrics is needed
        to get the best child requested. Also if the parent run is in a final status, only metrics flagged with the
        final column will be returned.

        :param include_failed: Whether to include failed runs.
        :type include_failed: bool
        :param include_canceled: Whether to include canceled runs.
        :type include_canceled: bool
        :return: The best Run and its metric value, or (None, None) if no best metrics were found.
        :rtype: (azureml.core.run.Run, float) or (None, None)
        """
        all_metrics = super().get_metrics()  # Get metrics stored directly in the parent run
        metric_table_name = "best_child_by_primary_metric"

        if not all_metrics or metric_table_name not in all_metrics or not all_metrics[metric_table_name]:
            return None, None

        metric_table = all_metrics[metric_table_name]

        run_id = self._get_last_value_from_metric_column(metric_table["run_id"])
        value = self._get_last_value_from_metric_column(metric_table["metric_value"])
        is_final = self._get_last_value_from_metric_column(metric_table["final"])

        if not run_id or value is None or is_final is None:
            return None, None

        parent_status_is_terminal = self.get_status() in TERMINAL_STATES
        if not is_final and parent_status_is_terminal:
            return None, None

        best_child_run = Run(self.experiment, run_id)

        if best_child_run.get_status() == RunStatus.CANCELED and not include_canceled:
            return None, None

        if best_child_run.get_status() == RunStatus.FAILED and not include_failed:
            return None, None

        return best_child_run, value

    def _get_last_value_from_metric_column(self, metric_column):
        """Get the last element of the metric column. The column is either a list or a scalar value."""
        if isinstance(metric_column, list):
            return metric_column[-1]
        else:
            return metric_column

    def _is_valid_childrun_tag(self, tag_name, parent_run_id_prefix):
        return tag_name.startswith(parent_run_id_prefix) and \
            tag_name[len(parent_run_id_prefix):].isdigit()

    def get_hyperparameters(self):
        """Return the hyperparameters for all the child runs that were launched by this HyperDriveRun.

        :return: Hyperparameters for all the child runs. It is a dictionary with run_id as key.
        :rtype: dict
        """
        result = {}
        # Hyperparameters of child runs are stored in tags in the format of
        # _aml_system_<parent_run_id>_<index>: <json_string_of_parameter_dictionary>
        # or in case of older SDKs:
        # <parent_run_id>_<index>: <json_string_of_parameter_dictionary>
        aml_prefix = "_aml_system_"
        parent_run_id_prefix = self.id + "_"
        for tag_name, tag_value in self.tags.items():
            if self._is_valid_childrun_tag(tag_name, aml_prefix + parent_run_id_prefix):
                result[tag_name[len(aml_prefix):]] = tag_value
            elif self._is_valid_childrun_tag(tag_name, parent_run_id_prefix) and tag_name not in result.keys():
                result[tag_name] = tag_value

        return result

    def get_children_sorted_by_primary_metric(self, top=0, reverse=False, discard_no_metric=False):
        """Return a list of children sorted by their best primary metric.

        The sorting is done according to the primary metric and its goal: if it is maximize, then the children
        are returned in descending order of their best primary metric. If reverse is True, the order is reversed.

        Each child in the result has run id, hyperparameters, best primary metric value and status.

        Children without primary metric are discarded when discard_no_metric is True. Otherwise, they are appended
        to the list behind other children with primary metric. Note that the reverse option has no impact on them.

        :param top: Number of top children to be returned. If it is 0, all children will be returned.
        :type top: int
        :param reverse: If it is True, the order will be reversed. It only impacts children with primary metric.
        :type reverse: bool
        :param discard_no_metric: If it is False, children without primary metric will be appended to the list.
        :type discard_no_metric: bool
        :return: List of dictionaries with run id, hyperparameters, best primary metric and status
        :rtype: list
        """
        assert isinstance(top, int) and top >= 0, "Value of parameter top should be 0 or a positive integer"
        assert isinstance(reverse, bool), "Type of parameter reverse should be bool"
        assert isinstance(discard_no_metric, bool), "Type of parameter discard_no_metric should be bool"

        hyperparameters = self.get_hyperparameters()

        metric_name = self.hyperdrive_config._primary_metric_config["name"]
        metric_goal = self.hyperdrive_config._primary_metric_config["goal"]
        metric_func = max if metric_goal == PrimaryMetricGoal.MAXIMIZE.value.lower() else min

        children = []
        no_metrics = []
        for run in self.get_children():
            run_id = run.id
            best_metric = None
            best_metric_dict = run.get_metrics(metric_name)
            if metric_name in best_metric_dict:
                metrics = best_metric_dict[metric_name]
                best_metric = metric_func(metrics) if isinstance(metrics, list) else metrics
            child = {"run_id": run_id,
                     "hyperparameters": hyperparameters[run_id] if run_id in hyperparameters else None,
                     "best_primary_metric": best_metric,
                     "status": run.get_status()}
            if best_metric is not None:
                children.append(child)
            elif not discard_no_metric:
                no_metrics.append(child)

        is_maximize = (metric_goal == PrimaryMetricGoal.MAXIMIZE.value.lower())
        sorted_children = sorted(children, key=lambda i: i['best_primary_metric'], reverse=(is_maximize != reverse))

        if no_metrics:
            sorted_children = sorted_children + no_metrics

        return sorted_children if top == 0 else sorted_children[:top]

    def _get_best_run_id_by_primary_metric(self, include_failed=False, include_canceled=False):
        """Return the run id of the instance that corresponds to the best performing child run.

        :param include_failed: Include failed run or not.
        :type include_failed: bool
        :param include_canceled: Include canceled run or not.
        :type include_canceled: bool
        :return: ID of the best run and its metric value, or None if no child has the primary metric.
        :rtype: (str, float) or (None, None)
        """
        children = self.get_children_sorted_by_primary_metric(discard_no_metric=True)
        for child in children:
            if (include_failed and child["status"] == "Failed") \
               or (include_canceled and child["status"] == "Canceled") \
               or (child["status"] not in ["Failed", "Canceled"]):
                return child["run_id"], child["best_primary_metric"]

        return None, None

    def get_metrics(self):
        """Return the metrics from all the runs that were launched by this HyperDriveRun.

        :return: The metrics for all the children of this run.
        :rtype: dict
        """
        child_run_ids = [run.id for run in self.get_children()]
        # noinspection PyProtectedMember
        return self._client.get_metrics(run_ids=child_run_ids, use_batch=True)

    # get_diagnostics looks for a zip in AFS based on run_id.
    # For HyperDrive runs, there is no entry in AFS.
    def get_diagnostics(self):
        """Do not use. The get_diagnostics method is not supported for the HyperDriveRun subclass.

        :raises azureml.train.hyperdrive.exceptions.HyperDriveNotImplementedException:
        """
        raise HyperDriveNotImplementedException._with_error(
            AzureMLError.create(
                HyperDriveNotImplemented, feature="Get diagnostics"
            )
        )

    def fail(self):
        """Do not use. The fail method is not supported for the HyperDriveRun subclass.

        :raises azureml.train.hyperdrive.exceptions.HyperDriveNotImplementedException:
        """
        raise HyperDriveNotImplementedException._with_error(
            AzureMLError.create(
                HyperDriveNotImplemented, feature="Fail"
            )
        )

    @staticmethod
    def _from_run_dto(experiment, run_dto):
        """Return HyperDrive run from a dto.

        :param experiment: The experiment that contains this run.
        :type experiment: azureml.core.experiment.Experiment
        :param run_dto: The HyperDrive run dto as received from the cloud.
        :type run_dto: RunDto
        :return: The HyperDriveRun object.
        :rtype: HyperDriveRun
        """
        hyperdrive_config = HyperDriveConfig._get_runconfig_from_run_dto(run_dto)
        return HyperDriveRun(experiment, run_dto.run_id, hyperdrive_config)


def _simple_warning(message, category, filename, lineno, file=None, line=None):
    """Override detailed stack trace warning with just the message."""
    return str(message) + '\n'
