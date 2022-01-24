# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""The HyperDriveConfig module defines the allowed configuration options for a HyperDrive experiment."""
import copy
import enum
import json
import logging
import uuid
import warnings

from azureml._base_sdk_common.utils import convert_list_to_dict
from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore
from azureml._execution._commands import _serialize_run_config_to_dict
from azureml._restclient.constants import RunStatus
from azureml.core import Run
from azureml.core.script_run_config import (ScriptRunConfig,
                                            _update_args_and_io,
                                            get_run_config_from_script_run)
from azureml.data._loggerfactory import collect_datasets_usage
from azureml.data.constants import _HYPERDRIVE_SUBMIT_ACTIVITY
from azureml.exceptions import TrainingException
from azureml.train._estimator_helper import _get_arguments
from azureml.train.hyperdrive.error_definition import (
    InvalidConfigSetting, InvalidType,
    ResumeChildRunsContainsDuplicate, ResumeChildRunsFromTooManyParentRuns,
    ResumeChildRunsNotInTerminalState, ResumeChildRunsWithoutParentRun,
    WarmStartRunsDontMatch)
from azureml.train.hyperdrive.exceptions import HyperDriveConfigException
from azureml.train.hyperdrive.policy import (NoTerminationPolicy,
                                             _policy_from_dict)
from azureml.train.hyperdrive.sampling import (BayesianParameterSampling,
                                               _sampling_from_dict)

module_logger = logging.getLogger(__name__)
TERMINAL_STATES = [RunStatus.CANCELED, RunStatus.COMPLETED, RunStatus.FAILED]

HYPERDRIVE_URL_SUFFIX = "/hyperdrive/v1.0"
MAX_DURATION_MINUTES = 10080  # after this max duration the HyperDrive run is cancelled.
RECOMMENDED_MIN_RUNS_PER_PARAMETER_BAYESIAN = 20
RECOMMENDED_MAX_CONCURRENT_RUNS_BAYESIAN = 20
MAX_PARENT_RUNS = 5
RESUME_FROM_TOTAL_RUNS = 1000

scrubbed_data = "[Scrubbed]"


class PrimaryMetricGoal(enum.Enum):
    """Defines supported metric goals for hyperparameter tuning.

    A metric goal is used to determine whether a higher value for a metric is better or worse. Metric goals are
    used when comparing runs based on the primary metric. For example, you may want to maximize accuracy or
    minimize error.

    The primary metric name and goal are specified in the :class:`azureml.train.hyperdrive.HyperDriveConfig`
    class when you configure a HyperDrive run.
    """

    MAXIMIZE = "MAXIMIZE"
    MINIMIZE = "MINIMIZE"

    @staticmethod
    def from_str(goal):
        """Return the primary metric goal that corresponds to the given value.

        :param goal: The string name of the goal.
        :type goal: str
        """
        if goal.lower() == PrimaryMetricGoal.MAXIMIZE.name.lower():
            return PrimaryMetricGoal.MAXIMIZE
        elif goal.lower() == PrimaryMetricGoal.MINIMIZE.name.lower():
            return PrimaryMetricGoal.MINIMIZE
        raise HyperDriveConfigException._with_error(
            AzureMLError.create(
                InvalidConfigSetting, obj="The primary metric goal",
                condition="either 'maximize' or 'minimize'.",
                target="goal"
            )
        )


class HyperDriveConfig(object):
    """Configuration that defines a HyperDrive run.

    HyperDrive configuration includes information about hyperparameter space sampling, termination policy,
    primary metric, resume from configuration, estimator, and the compute target to execute the experiment runs on.

    .. remarks::
        The example below shows creating a HyperDriveConfig object to use for hyperparameter tunning. In the
        example, the primary metric name matches a value logged in the training script.

        .. code-block:: python

            hd_config = HyperDriveConfig(run_config=src,
                                         hyperparameter_sampling=ps,
                                         policy=early_termination_policy,
                                         primary_metric_name='validation_acc',
                                         primary_metric_goal=PrimaryMetricGoal.MAXIMIZE,
                                         max_total_runs=4,
                                         max_concurrent_runs=4)

        Full sample is available from
        https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/machine-learning-pipelines/intro-to-pipelines/aml-pipelines-parameter-tuning-with-hyperdrive.ipynb


        For more information about working with HyperDriveConfig, see the tutorial
        `Tune hyperparameters for your model
        <https://docs.microsoft.com/azure/machine-learning/how-to-tune-hyperparameters>`__.

    :param estimator: An estimator that will be called with sampled hyperparameters.
                        Specify only one of the following parameters: ``estimator``, ``run_config``,
                        or ``pipeline``.
    :type estimator: azureml.train.estimator.MMLBaseEstimator
    :param hyperparameter_sampling: The hyperparameter sampling space.
    :type hyperparameter_sampling: azureml.train.hyperdrive.HyperParameterSampling
    :param policy: The early termination policy to use. If None - the default,
                   no early termination policy will be used.

                   The :class:`azureml.train.hyperdrive.MedianStoppingPolicy` with ``delay_evaluation`` of 5
                   is a good termination policy to start with. These are conservative settings,
                   that can provide 25%-35% savings with no loss on primary metric (based on our evaluation data).
    :type policy: azureml.train.hyperdrive.EarlyTerminationPolicy
    :param primary_metric_name: The name of the primary metric reported by the experiment runs.
    :type primary_metric_name: str
    :param primary_metric_goal: Either PrimaryMetricGoal.MINIMIZE or PrimaryMetricGoal.MAXIMIZE.
                                This parameter determines if the primary metric is to be
                                minimized or maximized when evaluating runs.
    :type primary_metric_goal: azureml.train.hyperdrive.PrimaryMetricGoal
    :param max_total_runs: The maximum total number of runs to create. This is the upper bound; there may
                           be fewer runs when the sample space is smaller than this value.
                           If both ``max_total_runs`` and ``max_duration_minutes`` are specified, the
                           hyperparameter tuning experiment terminates when the first of these two thresholds
                           is reached.
    :type max_total_runs: int
    :param max_concurrent_runs: The maximum number of runs to execute concurrently. If None, all runs are launched
                                in parallel. The number of concurrent runs is gated on the resources available in
                                the specified compute target. Hence, you need to ensure that the compute target
                                has the available resources for the desired concurrency.
    :type max_concurrent_runs: int
    :param max_duration_minutes: The maximum duration of the HyperDrive run. Once this time is exceeded, any runs
                                still executing are cancelled. If both ``max_total_runs`` and
                                ``max_duration_minutes`` are specified, the hyperparameter tuning experiment
                                terminates when the first of these two thresholds is reached.

    :type max_duration_minutes: int
    :param resume_from: A hyperdrive run or a list of hyperdrive runs
                        that will be inherited as data points to warm start the new run.
    :type resume_from: azureml.train.hyperdrive.HyperDriveRun or list[azureml.train.hyperdrive.HyperDriveRun]
    :param resume_child_runs: A hyperdrive child run or a list of hyperdrive child runs
                              that will be resumed as new child runs of the new hyperdrive run.
    :type resume_child_runs: azureml.core.run.Run or list[azureml.core.run.Run]
    :param run_config: An object for setting up configuration for script/notebook runs.
                        Specify only one of the following parameters: ``estimator``, ``run_config``,
                        or ``pipeline``.
    :type run_config: azureml.core.ScriptRunConfig
    :param pipeline: A pipeline object for setting up configuration for pipeline runs.
                        The pipeline object will be called with the sample hyperparameters to submit pipeline runs.
                        Specify only one of the following parameters: ``estimator``, ``run_config``,
                        or ``pipeline``.
    :type pipeline: azureml.pipeline.core.Pipeline
    """

    _PLATFORM = "AML"
    _AML_PIPELINES_PLATFORM = "AML_PIPELINES"

    def __init__(self,
                 hyperparameter_sampling,
                 primary_metric_name, primary_metric_goal,
                 max_total_runs,
                 max_concurrent_runs=None,
                 max_duration_minutes=MAX_DURATION_MINUTES,
                 policy=None,
                 estimator=None,
                 run_config=None,
                 resume_from=None,
                 resume_child_runs=None,
                 pipeline=None,
                 debug_flag=None
                 ):
        """Initialize the HyperDriveConfig.

        :param hyperparameter_sampling: The hyperparameter space sampling definition.
        :type hyperparameter_sampling: azureml.train.hyperdrive.HyperParameterSampling
        :param primary_metric_name: The name of the primary metric reported by the experiment runs.
        :type primary_metric_name: str
        :param primary_metric_goal: Either PrimaryMetricGoal.MINIMIZE or PrimaryMetricGoal.MAXIMIZE.
                                This parameter determines if the primary metric is to be
                                minimized or maximized when evaluating runs.
        :type primary_metric_goal: azureml.train.hyperdrive.PrimaryMetricGoal
        :param max_total_runs: The maximum total number of runs to create. This is the upper bound; there may
                           be fewer runs when the sample space is smaller than this value.
        :type max_total_runs: int
        :param max_concurrent_runs: The maximum number of runs to execute concurrently. If None, all runs are launched
                                    in parallel.
        :type max_concurrent_runs: int
        :param max_duration_minutes: The maximum duration of the HyperDrive run. Once this time is exceeded, any runs
                                still executing are cancelled.
        :type max_duration_minutes: int
        :param policy: The early termination policy to use. If None - the default,
                   no early termination policy will be used.

                   The :class:`azureml.train.hyperdrive.MedianTerminationPolicy` with ``delay_evaluation`` of 5
                   is a good termination policy to start with. These are conservative settings,
                   that can provide 25%-35% savings with no loss on primary metric (based on our evaluation data).
        :type policy: azureml.train.hyperdrive.EarlyTerminationPolicy
        :param estimator: An estimator that will be called with sampled hyper parameters.
                          Specify only one of the following parameters: ``estimator``, ``run_config``,
                          or ``pipeline``.
        :type estimator: azureml.train.estimator.MMLBaseEstimator
        :param run_config: An object for setting up configuration for script/notebook runs.
                           Specify only one of the following parameters: ``estimator``, ``run_config``,
                           or ``pipeline``.
        :type run_config: azureml.core.ScriptRunConfig
        :param resume_from: A hyperdrive run or a list of hyperdrive runs
                            that will be inherited as data points to warm start the new run.
        :type resume_from: azureml.train.hyperdrive.HyperDriveRun | list[azureml.train.hyperdrive.HyperDriveRun]
        :param resume_child_runs: A hyperdrive child run or a list of hyperdrive child runs
                                  that will be resumed as new child runs of the new hyperdrive run.
        :type resume_child_runs: azureml.core.run.Run | list[azureml.core.run.Run]
        :param pipeline: A pipeline object for setting up configuration for pipeline runs.
                         The pipeline object will be called with the sample hyperparameters to submit pipeline runs.
                         Specify only one of the following parameters: ``estimator``, ``run_config``,
                         or ``pipeline``.
        :type pipeline: azureml.pipeline.core.Pipeline
        """
        self._estimator = estimator
        self._run_config = run_config
        self._pipeline = pipeline
        self._debug_flag = debug_flag

        if self._estimator is None and self._run_config is None and self._pipeline is None:
            raise HyperDriveConfigException._with_error(
                AzureMLError.create(
                    InvalidConfigSetting, obj="HyperDriveConfig",
                    condition="at least one of {} to be set"
                              .format(", ".join(['estimator', 'run_config', 'pipeline'])),
                    target="estimator, run_config, pipeline"
                )
            )

        if len([value for value in [self._estimator, self._run_config, self._pipeline] if value is not None]) != 1:
            raise HyperDriveConfigException._with_error(
                AzureMLError.create(
                    InvalidConfigSetting, obj="HyperDriveConfig",
                    condition="only one of {} to be set"
                              .format(", ".join(['estimator', 'run_config', 'pipeline'])),
                    target="estimator, run_config, pipeline"
                )
            )

        if self._run_config is not None and not isinstance(self._run_config, ScriptRunConfig):
            raise HyperDriveConfigException._with_error(
                AzureMLError.create(
                    InvalidType, exp="ScriptRunConfig", obj="run_config", actual=scrubbed_data,
                    target="run_config"
                )
            )

        if hyperparameter_sampling is None:
            raise HyperDriveConfigException._with_error(
                AzureMLError.create(
                    InvalidConfigSetting, obj="HyperDriveConfig",
                    condition="{} to be set".format("hyperparameter_sampling"),
                    target="hyperparameter_sampling"
                )
            )

        if self._pipeline is not None:
            warnings.formatwarning = _simple_warning
            warnings.warn("Use of pipeline parameter in HyperDriveConfig is a preview feature. Please keep in mind "
                          "that the feature can change without notice.")

        if policy is None:
            policy = NoTerminationPolicy()

        self._policy_config = policy.to_json()
        self._generator_config = hyperparameter_sampling.to_json()
        self._primary_metric_config = {
            'name': primary_metric_name,
            'goal': primary_metric_goal.name.lower()}
        self._max_total_runs = max_total_runs
        self._max_concurrent_runs = max_concurrent_runs or max_total_runs
        self._max_duration_minutes = max_duration_minutes
        self._platform = self._PLATFORM if self._pipeline is None else self._AML_PIPELINES_PLATFORM
        self._host_url = None
        # This property is set the first time the platform_config is built.
        self._platform_config = None
        self._is_cloud_hydrate = False

        warnings.formatwarning = _simple_warning
        if self._max_duration_minutes > MAX_DURATION_MINUTES:
            warnings.warn(("The experiment maximum duration provided exceeds the service limit of "
                           "{} minutes. The maximum duration will be overridden with {} minutes.").format(
                               MAX_DURATION_MINUTES, MAX_DURATION_MINUTES))

        is_bayesian = isinstance(hyperparameter_sampling, BayesianParameterSampling)
        if is_bayesian:
            # Needs to be updated once conditional/nested space definitions are added
            num_parameters = len(hyperparameter_sampling._parameter_space)
            recommended_max_total_runs = RECOMMENDED_MIN_RUNS_PER_PARAMETER_BAYESIAN * num_parameters

            if self._max_total_runs < recommended_max_total_runs:
                warnings.warn(("For best results with Bayesian Sampling we recommend using a maximum number of runs "
                               "greater than or equal to {} times the number of hyperparameters being tuned. "
                               "Recommendend value:{}.").format(RECOMMENDED_MIN_RUNS_PER_PARAMETER_BAYESIAN,
                                                                recommended_max_total_runs))
            if self._max_concurrent_runs > RECOMMENDED_MAX_CONCURRENT_RUNS_BAYESIAN:
                warnings.warn(("We recommend using {} max concurrent runs or fewer when using Bayesian sampling "
                               "since a higher number might not provide the best result.").format(
                    RECOMMENDED_MAX_CONCURRENT_RUNS_BAYESIAN))

        if resume_from is not None:
            if (not isinstance(resume_from, list)):
                resume_from = [resume_from]
            if len(resume_from) > MAX_PARENT_RUNS:
                raise HyperDriveConfigException._with_error(
                    AzureMLError.create(
                        InvalidConfigSetting, obj="HyperDriveConfig",
                        condition="the number of parent runs to not exceed than {}"
                                  .format(MAX_PARENT_RUNS),
                        target="resume_from"
                    )
                )

            if len(resume_from) > 0:
                self._validate_warm_start(resume_from, is_bayesian, is_resume_from=True)

            self._resume_from = [self._get_run_key_dict_from_hdrun(hdrun) for hdrun in resume_from]
        else:
            self._resume_from = None

        if resume_child_runs is not None:
            if (not isinstance(resume_child_runs, list)):
                resume_child_runs = [resume_child_runs]
            if len(resume_child_runs) > 0:
                self._validate_resume_child_runs(resume_child_runs, is_bayesian)

            self._register_datastore_for_resume_child_runs(resume_child_runs)

            self._resume_child_runs = [self._get_run_key_dict_from_hd_child_run(run) for run in resume_child_runs]
        else:
            self._resume_child_runs = None

    def _validate_resume_child_runs(self, resume_child_runs, is_bayesian):
        """Validate status and type for resume_child_runs.

        Retrieves a list of parent runs to be passed to _validate_warm_start.

        :param resume_child_runs: The list of runs to be validated.
        :type: resume_child_runs: list[azureml.core.run.Run]
        :param is_bayesian: Determines if the current run uses Bayesian sampling
        :type is_bayesian: bool
        """
        if len(resume_child_runs) > self._max_total_runs:
            raise HyperDriveConfigException._with_error(
                AzureMLError.create(
                    InvalidConfigSetting, obj="HyperDriveConfig",
                    condition="the number of resume_child_runs to not exceed "
                              "max_total_runs of current run",
                    target="resume_child_runs"
                )
            )

        if len(resume_child_runs) >= 5:
            warnings.formatwarning = _simple_warning
            warnings.warn("Validating data to be inherited from previous experiments. "
                          "Please note that this may take a few minutes.")

        parent_dict = {}
        child_set = set()
        for run in resume_child_runs:
            if run.id in child_set:
                raise HyperDriveConfigException._with_error(
                    AzureMLError.create(
                        ResumeChildRunsContainsDuplicate,
                        target="resume_child_runs"
                    )
                )
            child_set.add(run.id)

            if not isinstance(run, Run):
                raise HyperDriveConfigException._with_error(
                    AzureMLError.create(
                        InvalidType, exp="azureml.core.run.Run", obj="resume_child_runs", actual=scrubbed_data,
                        target="run"
                    )
                )
            if run.get_status() not in TERMINAL_STATES:
                raise HyperDriveConfigException._with_error(
                    AzureMLError.create(
                        ResumeChildRunsNotInTerminalState, state=run.get_status(), target="run"
                    )
                )

            if run.parent is None:
                raise HyperDriveConfigException._with_error(
                    AzureMLError.create(
                        ResumeChildRunsWithoutParentRun, target="run"
                    )
                )

            parent_dict[run.parent.id] = run.parent

        if len(parent_dict) > MAX_PARENT_RUNS:
            raise HyperDriveConfigException._with_error(
                AzureMLError.create(
                    ResumeChildRunsFromTooManyParentRuns, max_num=MAX_PARENT_RUNS, found=len(parent_dict),
                    target="parent_dict"
                )
            )
        self._validate_warm_start(list(parent_dict.values()), is_bayesian)

    def _validate_warm_start(self, resume_list, is_bayesian, is_resume_from=False):
        """Validate hyperdrive runs for warm start or resume run.

        Raises an exception with a message if invalid.

        :param resume_list: The list of hyperdrive runs to be validated.
        :type resume_list: list[azureml.train.hyperdrive.HyperDriveRun]
        :param is_bayesian: Determines if the current run uses Bayesian sampling.
        :type is_bayesian: bool
        :param is_resume_from: Determines if the validation is for resume_from or resume_child_runs.
        :type is_resume_from: bool
        """
        # Keep track of total runs for resume_from
        if is_resume_from:
            _total_child_runs = self._max_total_runs

        hdrun_set = set()

        for hdrun in resume_list:

            if hdrun._runtype != "hyperdrive":
                raise HyperDriveConfigException._with_error(
                    AzureMLError.create(
                        InvalidConfigSetting, obj="Parent run",
                        condition="to be HyperDriveRun objects.",
                        target="hdrun"
                    )
                )

            if hdrun.hyperdrive_config._primary_metric_config["name"] != self._primary_metric_config["name"]:
                raise HyperDriveConfigException._with_error(
                    AzureMLError.create(
                        WarmStartRunsDontMatch, obj="primary_metric_name",
                        additional_info="Current run's name is {}, while a run with {} was found"
                                        .format(self._primary_metric_config["name"],
                                                hdrun.hyperdrive_config._primary_metric_config["name"]),
                        target="primary_metric_name"
                    )
                )

            if hdrun.hyperdrive_config._primary_metric_config["goal"] != self._primary_metric_config["goal"]:
                raise HyperDriveConfigException._with_error(
                    AzureMLError.create(
                        WarmStartRunsDontMatch, obj="primary_metric_goal",
                        additional_info="Current run's goal is {}, while a run with {} was found"
                                        .format(self._primary_metric_config["goal"],
                                                hdrun.hyperdrive_config._primary_metric_config["goal"]),
                        target="primary_metric_goal"
                    )
                )

            # Make sure all runs have the same host by comparing with the first Run in the list
            if hdrun.hyperdrive_config._platform_config["ServiceAddress"] \
                    != resume_list[0].hyperdrive_config._platform_config["ServiceAddress"]:
                raise HyperDriveConfigException._with_error(
                    AzureMLError.create(
                        WarmStartRunsDontMatch, obj="The host"
                    )
                )

            if is_bayesian:
                if hdrun.hyperdrive_config._generator_config["parameter_space"] \
                        != self._generator_config["parameter_space"]:
                    raise HyperDriveConfigException._with_error(
                        AzureMLError.create(
                            WarmStartRunsDontMatch, obj="parameter_space for Bayesian sampling"
                        )
                    )

            if is_resume_from:
                if hdrun.id in hdrun_set:
                    raise HyperDriveConfigException(("resume_from cannot contain duplicate runs. More than one "
                                                     "run with id '{}' was found").format(hdrun.id))
                hdrun_set.add(hdrun.id)

                if hdrun.get_status() != RunStatus.COMPLETED \
                        and hdrun.get_status() != RunStatus.CANCELED:
                    raise HyperDriveConfigException(("All resume_from runs should be completed or canceled. A "
                                                     "resume_from run with status '{}' was found.").format(
                                                    hdrun.get_status()))
                _total_child_runs += hdrun.hyperdrive_config._max_total_runs

        if is_resume_from and _total_child_runs > RESUME_FROM_TOTAL_RUNS:
            raise HyperDriveConfigException(("The number of total runs should not "
                                             "be greater than {}. ".format(RESUME_FROM_TOTAL_RUNS)))

    def _register_datastore_for_resume_child_runs(self, resume_child_runs):
        """Register datastore pointing to azureml container for resume_child_runs.

        The name of this datastore is used for mounting outputs folder to load checkpoints.

        :param resume_child_runs: The list of child runs to be resumed.
        :type: resume_child_runs: list[azureml.core.run.Run]
        """
        # Group by workspace.
        workspace_id_to_runs_dict = {}

        for hd_child_run in resume_child_runs:
            workspace_id = hd_child_run.experiment.workspace._workspace_id
            if workspace_id not in workspace_id_to_runs_dict:
                workspace_id_to_runs_dict[workspace_id] = []
            workspace_id_to_runs_dict[workspace_id].append(hd_child_run)

        warnings.formatwarning = _simple_warning
        warnings.warn("Registering {} datastores to be used with resume_child_runs. "
                      "Please note that this may take a few minutes.".format(len(workspace_id_to_runs_dict)))

        # Register datastore per workspace.
        for index, (workspace_id, runs) in enumerate(workspace_id_to_runs_dict.items()):
            warnings.warn("Registering datastore {}.".format(index + 1))
            if len(runs) > 0:
                # _get_blob_azureml_datastore function registers the datastore if there is no datastore registered
                # for the run.
                runs[0]._get_blob_datastore_from_run()

    @property
    def estimator(self):
        """Return the estimator used in the HyperDrive run.

        Value is None if the run uses a script run configuration or a pipeline.

        :return: The estimator.
        :rtype: azureml.train.estimator.Estimator or None
        """
        return self._estimator

    @property
    def run_config(self):
        """Return the script/notebook configuration used in the HyperDrive run.

        Value is None if the run uses an estimator or pipeline.

        :return: The run configuration.
        :rtype: azureml.core.ScriptRunConfig or None
        """
        return self._run_config

    @property
    def pipeline(self):
        """Return the pipeline used in the HyperDrive run.

        Value is None if the run uses a script run configuration or estimator.

        :return: The pipeline.
        :rtype: azureml.pipeline.core.Pipeline or None
        """
        return self._pipeline

    @property
    def source_directory(self):
        """Return the source directory from the config to run.

        :return: The source directory
        :rtype: str
        """
        if self._is_cloud_hydrate:
            return None

        if self.estimator is not None:
            return self.estimator.source_directory
        elif self.run_config is not None:
            return self.run_config.source_directory

        return None

    def _get_host_url(self, workspace, run_name):
        """Return the host url for the HyperDrive service.

        :param workspace: The workspace.
        :type workspace: azureml.core.workspace.Workspace
        :param run_name: The name of the run.
        :type run_name: str
        :return: The host url for HyperDrive service.
        :rtype: str
        """
        if not self._host_url:
            service_url = workspace.service_context._get_hyperdrive_url()
            self._host_url = service_url + HYPERDRIVE_URL_SUFFIX
        return self._host_url

    @staticmethod
    def _get_runconfig_from_run_dto(run_dto):
        hyperparameter_sampling = _sampling_from_dict(
            json.loads(_get_tag_from_dict(run_dto.tags, "generator_config")))
        primary_metric_config = json.loads(_get_tag_from_dict(run_dto.tags, "primary_metric_config"))
        primary_metric_name = primary_metric_config["name"]
        primary_metric_goal = PrimaryMetricGoal.from_str(primary_metric_config["goal"])
        max_total_runs = int(_get_tag_from_dict(run_dto.tags, "max_total_jobs"))
        max_concurrent_runs = int(_get_tag_from_dict(run_dto.tags, "max_concurrent_jobs"))
        max_duration_minutes = int(_get_tag_from_dict(run_dto.tags, "max_duration_minutes"))
        policy = _policy_from_dict(
            json.loads(_get_tag_from_dict(run_dto.tags, "policy_config")))

        hyperdrive_config = HyperDriveConfig(hyperparameter_sampling=hyperparameter_sampling,
                                             primary_metric_name=primary_metric_name,
                                             primary_metric_goal=primary_metric_goal,
                                             max_total_runs=max_total_runs,
                                             max_concurrent_runs=max_concurrent_runs,
                                             max_duration_minutes=max_duration_minutes,
                                             policy=policy,
                                             run_config=ScriptRunConfig('.'))

        hyperdrive_config._platform_config = HyperDriveConfig._get_platform_config_from_run_dto(run_dto)
        hyperdrive_config._resume_from = HyperDriveConfig._get_property_from_run_dto(run_dto, "resume_from")
        hyperdrive_config._resume_child_runs = HyperDriveConfig._get_property_from_run_dto(run_dto,
                                                                                           "resume_child_runs")
        hyperdrive_config._is_cloud_hydrate = True

        if run_dto.properties is not None and "platform" in run_dto.properties:
            hyperdrive_config._platform = run_dto.properties["platform"]

        return hyperdrive_config

    @staticmethod
    def _get_platform_config_from_run_dto(run_dto):
        return json.loads(_get_tag_from_dict(run_dto.tags, "platform_config"))

    @staticmethod
    def _get_property_from_run_dto(run_dto, property_name):
        if run_dto.properties is not None and property_name in run_dto.properties:
            return json.loads(run_dto.properties[property_name])
        else:
            return None

    def _get_platform_config(self, workspace, run_name, **kwargs):
        """Return `dict` containing platform config definition.

        Platform config contains the AML config information about the execution service or
        config information used to submit jobs to aml pipelines.
        """
        if self._platform_config is not None:
            return self._platform_config

        platform_config = \
            {
                "ServiceAddress": workspace.service_context._get_experimentation_url(),
                # FIXME: remove this fix once hyperdrive code updates ES URL creation
                # workspace.service_context._get_experiment_scope(run_name) gives /subscriptionid/id_value
                # where as hyperdrive expects subscriptionid/id_value
                # "ServiceArmScope": workspace.service_context._get_experiment_scope(run_name),
                "ServiceArmScope": workspace.service_context._get_experiment_scope(run_name)[1:],
                "SubscriptionId": workspace.subscription_id,
                "ResourceGroupName": workspace.resource_group,
                "WorkspaceName": workspace.name,
                "ExperimentName": run_name
            }

        if self._pipeline is not None:
            platform_config.update(self._get_platform_config_data_from_pipeline(**kwargs))
        else:
            platform_config.update(self._get_platform_config_data_from_run_config(workspace))

        self._platform_config = platform_config

        return self._platform_config

    def _get_platform_config_data_from_run_config(self, workspace):
        """Return `dict` containing platform config data created from estimator/run_config.

        This contains the AML config information about the execution service.
        """
        if self.estimator is not None:
            run_config = get_run_config_from_script_run(self.estimator._get_script_run_config())
        elif self.run_config is not None:
            run_config = get_run_config_from_script_run(self.run_config)
        else:
            raise TrainingException("Invalid HyperDriveConfig object. "
                                    "The estimator, run_config and platform config are missing.")

        run_config = self._remove_duplicate_arguments(run_config,
                                                      self._generator_config,
                                                      self.estimator is not None)

        if run_config.target == "amlcompute":
            self._set_amlcompute_runconfig_properties(run_config)

        dataset_consumptions, _ = _update_args_and_io(workspace, run_config)
        collect_datasets_usage(module_logger, _HYPERDRIVE_SUBMIT_ACTIVITY, dataset_consumptions,
                               workspace, run_config.target)
        run_config_serialized = _serialize_run_config_to_dict(run_config)
        try:
            # Conda dependencies are being serialized into a string representation of
            # ordereddict by autorest. Convert to dict here so that it is properly
            # serialized.
            conda_dependencies = run_config_serialized['environment']['python']['condaDependencies']
            run_config_serialized['environment']['python']['condaDependencies'] = \
                json.loads(json.dumps(conda_dependencies))
        except KeyError:
            pass

        platform_config_data = {
            "Definition": {
                "Overrides": run_config_serialized,
                "TargetDetails": None
            }
        }

        return platform_config_data

    @staticmethod
    def _remove_duplicate_arguments(run_config, generator_config, is_estimator=True):
        """Remove duplicate arguments from the run_config.

        If HyperDrive parameter space definition has the same script parameter as the run_config,
        remove the script parameter from the run_config. If both have the same parameter, HyperDrive
        parameter space will take precedence over the run_config script parameters.
        """
        warning = False
        run_config_copy = copy.deepcopy(run_config)
        run_config_args = convert_list_to_dict(run_config.arguments)
        input_params = copy.deepcopy(run_config_args).keys() if run_config_args else []
        parameter_space = [item.lstrip("-") for item in generator_config["parameter_space"].keys()]
        duplicate_params = []

        if is_estimator:
            for param in input_params:
                # Add lstrip: The run_config script param input expects the -- to be specified for script_params.
                # In HyperDrive, parameter space, user doesn't specify hyphens in the beginning of the parameter.
                if param.lstrip("-") in parameter_space:
                    run_config_args.pop(param)
                    warning = True
                    duplicate_params.append(param)
        else:
            for param_idx in range(len(input_params)):
                if '-n' in run_config_args:
                    notebook_args = json.loads(run_config_args['-n'])
                    for param in copy.deepcopy(notebook_args).keys() if notebook_args else []:
                        if param.lstrip("-") in parameter_space:
                            notebook_args.pop(param)
                            warning = True
                            duplicate_params.append(param)
                    run_config_args['-n'] = json.dumps(notebook_args)
                    break

        if warning:
            warnings.formatwarning = _simple_warning
            warnings.warn("The same input parameter(s) are specified in estimator/run_config script params "
                          "and HyperDrive parameter space. HyperDrive parameter space definition will override "
                          "these duplicate entries. "
                          "{} is the list of overridden parameter(s).".format(duplicate_params))
            run_config_copy.arguments = _get_arguments(run_config_args)

        return run_config_copy

    def _set_amlcompute_runconfig_properties(self, run_config):
        # A new amlcompute cluster with this name will be created for this HyperDrive run.
        run_config.amlcompute._name = str(uuid.uuid4())
        # All the child runs will use the same cluster.
        # HyperDrive service will delete the cluster once the parent run reaches a terminal state.
        run_config.amlcompute._retain_cluster = True
        run_config.amlcompute._cluster_max_node_count = run_config.node_count * self._max_concurrent_runs
        warnings.formatwarning = _simple_warning
        warnings.warn("A AML compute with {} node count will be created for this HyperDriveRun. "
                      "Please consider modifying max_concurrent_runs if this will exceed the "
                      "quota on the Azure subscription.".format(run_config.amlcompute._cluster_max_node_count))

    def _get_platform_config_data_from_pipeline(self, **kwargs):
        """Return `dict` containing platform config data created from pipeline.

        This contains the config information used to submit jobs to aml pipelines.
        """
        if self._pipeline is None:
            raise TrainingException("Invalid HyperDriveConfig object. "
                                    "The pipeline and platform config are missing.")

        continue_on_step_failure = False
        regenerate_outputs = False
        pipeline_params = None
        for key, value in kwargs.items():
            if key == 'continue_on_step_failure':
                continue_on_step_failure = value
            elif key == 'regenerate_outputs':
                regenerate_outputs = value
            elif key == 'pipeline_params':
                pipeline_params = value

        self._validate_and_remove_duplicate_parameters(self._pipeline, self._generator_config, pipeline_params)

        creation_info_with_graph = self._pipeline.graph._get_pipeline_run_creation_info_with_graph(
            pipeline_parameters=pipeline_params, continue_on_step_failure=continue_on_step_failure,
            regenerate_outputs=regenerate_outputs)

        pipeline_service_address = self._pipeline.service_endpoint()

        return {
            "CreationInfoWithGraph": creation_info_with_graph.serialize(),
            "PipelinesServiceAddress": pipeline_service_address,
            "Definition": {}  # This is updated with telemetry values in search function.
        }

    @staticmethod
    def _get_run_key_dict_from_hdrun(hdrun):
        return {
            "run_scope": {
                "host": hdrun.hyperdrive_config._platform_config["ServiceAddress"],
                "subscription_id": hdrun.hyperdrive_config._platform_config["SubscriptionId"],
                "resource_group": hdrun.hyperdrive_config._platform_config["ResourceGroupName"],
                "workspace_name": hdrun.hyperdrive_config._platform_config["WorkspaceName"],
                "experiment_name": hdrun.hyperdrive_config._platform_config["ExperimentName"]
            },
            "run_id": hdrun.id
        }

    @staticmethod
    def _get_run_key_dict_from_hd_child_run(run):
        parent_run_key_dict = HyperDriveConfig._get_run_key_dict_from_hdrun(run.parent)
        parent_run_key_dict["run_id"] = run.id
        return parent_run_key_dict

    @staticmethod
    def _validate_and_remove_duplicate_parameters(pipeline, generator_config, pipeline_parameters=None):
        """Validate all parameters and remove duplicate parameters from pipeline_parameters.

        Validate that all parameters specified in generator_config are exposed as parameters in the pipeline.
        If HyperDrive parameter space definition has the same parameter as the pipeline_parameters,
        remove the parameter from pipeline_parameters. If both have the same parameter, HyperDrive
        parameter space will take precedence over pipeline_parameters specified.

        :param pipeline: A pipeline object.
        :type pipeline: azureml.pipeline.core.Pipeline
        :param generator_config: Hyperparameter sampling space.
        :type generator_config: dict
        :param pipeline_params: Parameters to pipeline execution.
                                Dictionary of {parameter name, parameter value}
        :type pipeline_params: dict
        """
        parameter_space = [item for item in generator_config["parameter_space"].keys()]
        graph_params = pipeline.graph.params
        if pipeline_parameters is None:
            pipeline_parameters = {}

        warning = False
        duplicate_params = []

        for param in parameter_space:
            if param not in graph_params:
                raise HyperDriveConfigException("Found a parameter in HyperDrive parameter space "
                                                "that is not defined as a pipeline parameter.")

            if param in pipeline_parameters:
                pipeline_parameters.pop(param)
                warning = True
                duplicate_params.append(param)

        if warning:
            warnings.formatwarning = _simple_warning
            warnings.warn("The same input parameter(s) are specified in pipeline parameters "
                          "and HyperDrive parameter space. HyperDrive parameter space definition "
                          "will override these duplicate entries. ")


class HyperDriveRunConfig(HyperDriveConfig):
    """Configuration that defines a HyperDrive run.

    Configuration includes information about parameter space sampling, termination policy,
    primary metric, estimator and the compute target to execute the experiment runs on.

    :param hyperparameter_sampling: The hyperparameter sampling space.
    :type hyperparameter_sampling: azureml.train.hyperdrive.HyperParameterSampling
    :param primary_metric_name: The name of the primary metric reported by the experiment runs.
    :type primary_metric_name: str
    :param primary_metric_goal: One of maximize / minimize.
                                It determines if the primary metric has to be
                                minimized/maximized in the experiment runs' evaluation.
    :type primary_metric_goal: azureml.train.hyperdrive.PrimaryMetricGoal
    :param max_total_runs: Maximum number of runs. This is the upper bound; there may
                           be fewer runs when the sample space is smaller than this value.
    :type max_total_runs: int
    :param max_concurrent_runs: Maximum number of runs to run concurrently. If None, all runs are launched in parallel.
    :type max_concurrent_runs: int
    :param max_duration_minutes: Maximum duration of the run. Once this time is exceeded, the run is cancelled.
    :type max_duration_minutes: int
    :param policy: The early termination policy to use. If None - the default,
                   no early termination policy will be used.
                   The MedianTerminationPolicy with delay_evaluation of 5
                   is a good termination policy to start with. These are conservative settings,
                   that can provide 25%-35% savings with no loss on primary metric (based on our evaluation data).
    :type policy: azureml.train.hyperdrive.EarlyTerminationPolicy
    :param estimator: An estimator that will be called with sampled hyper parameters.
    :type estimator: azureml.train.estimator.MMLBaseEstimator
    :param run_config: An object for setting up configuration for script/notebook runs.
                        Specify only one of the following parameters: ``estimator``, ``run_config``,
                        or ``pipeline``.
    :type run_config: azureml.core.ScriptRunConfig
    :param resume_from: A hyperdrive run or a list of hyperdrive runs that will be inherited as data points to
        warm start the new run.
    :type resume_from: azureml.train.hyperdrive.HyperDriveRun or list[azureml.train.hyperdrive.HyperDriveRun]
    :param resume_child_runs: A hyperdrive child run or a list of hyperdrive child runs that will be resumed as
        new child runs of the new hyperdrive run.
    :type resume_child_runs: azureml.core.run.Run or list[azureml.core.run.Run]
    :param pipeline: A pipeline object for setting up configuration for pipeline runs.
                        The pipeline object will be called with the sample hyperparameters to submit pipeline runs.
                        Specify only one of the following parameters: ``estimator``, ``run_config``,
                        or ``pipeline``.
    :type pipeline: azureml.pipeline.core.Pipeline
    """

    def __new__(cls,
                estimator,
                hyperparameter_sampling,
                primary_metric_name, primary_metric_goal,
                max_total_runs,
                max_concurrent_runs=None,
                max_duration_minutes=MAX_DURATION_MINUTES,
                policy=None
                ):
        """Initialize the HyperDriveRunConfig.

        This class is deprecated, please use :class:`azureml.train.hyperdrive.HyperDriveConfig` class.
        """
        warnings.formatwarning = _simple_warning
        warnings.warn("HyperDriveRunConfig is deprecated. Please use the new HyperDriveConfig class.")

        return HyperDriveConfig(hyperparameter_sampling=hyperparameter_sampling,
                                primary_metric_name=primary_metric_name,
                                primary_metric_goal=primary_metric_goal,
                                max_total_runs=max_total_runs,
                                max_concurrent_runs=max_concurrent_runs,
                                max_duration_minutes=max_duration_minutes,
                                policy=policy,
                                estimator=estimator)


def _simple_warning(message, category, filename, lineno, file=None, line=None):
    """Override detailed stack trace warning with just the message."""
    return str(message) + '\n'


def _get_tag_from_dict(tag_dict, key):
    """
    Return the value at data[tag_key].

    The new tags take precedance over legacy tags. The code tries to get the tag with
    "_aml_system_" prefix first. If this fails, tries again with the legacy key.

    :param tag_dict: The dictionary to get the value from.
    :type tag_dict: dict
    :param key: The key to index into the dictionary.
    :type key: str
    :return: The value at that key, or None otherwise.
    :rtype: str
    """
    if tag_dict is None:
        return None

    aml_system_prefix = "_aml_system_"
    if key.startswith(aml_system_prefix):
        legacy_key = key[len(aml_system_prefix):]
        new_key = key
    else:
        legacy_key = key
        new_key = aml_system_prefix + key

    return tag_dict.get(new_key) or tag_dict.get(legacy_key)
