# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Contains functionality for adding and managing an automated ML pipeline step in Azure Machine Learning."""
import json
import logging
import ntpath
import os

from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import ArgumentBlankOrEmpty, ArgumentInvalid
from azureml.automl.core import dataprep_utilities, dataset_utilities
from azureml._execution import _commands
from azureml.automl.core.shared._diagnostics.automl_error_definitions import InvalidArgumentType
from azureml.core import Experiment
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.runconfig import RunConfiguration
from azureml.data import TabularDataset
from azureml.data.constants import DIRECT_MODE
from azureml.data.dataset_consumption_config import DatasetConsumptionConfig
from azureml.data.output_dataset_config import OutputTabularDatasetConfig
from azureml.pipeline.core import PipelineStep, PipelineData, TrainingOutput
from azureml.pipeline.core._module_builder import _ModuleBuilder
from azureml.pipeline.core.graph import ParamDef
from azureml.pipeline.core.pipeline_output_dataset import PipelineOutputTabularDataset
from azureml.train.automl import constants
from azureml.train.automl._experiment_drivers import driver_utilities
from azureml.train.automl._azureautomlsettings import AzureAutoMLSettings
from azureml.train.automl._environment_utilities import modify_run_configuration, validate_non_prod_env_exists
from azureml.train.automl._azure_experiment_state import AzureExperimentState
from azureml.train.automl.automlconfig import AutoMLConfig
from azureml.train.automl.exceptions import ConfigException
from azureml.train.automl.run import AutoMLRun


logger = logging.getLogger(__name__)


class AutoMLStep(PipelineStep):
    """Creates an Azure ML Pipeline step that encapsulates an automated ML run.

    For an example of using AutoMLStep, see the notebook https://aka.ms/pl-automl.

    .. remarks::

        With the AutoMLStep class you can run your automated ML workflow in an Azure Machine Learning pipeline.
        Pipelines provide benefits such as repeatability, unattended runs, versioning and tracking, and
        modularity for your automated ML workflow. For more informaton, see `What are Azure Machine
        Learning pipelines? <https://docs.microsoft.com/azure/machine-learning/concept-ml-pipelines>`_.

        When your automated ML workflow is in a pipeline, you can schedule the pipeline to run on a time-based
        schedule or on a change-based schedule. Time-based schedules are useful for routine tasks such as monitoring
        data drift, while change-based schedules are useful for irregular or unpredictable changes such as when data
        changes. For example, your schedule might poll a blob store where the data is being uploaded and then run
        the pipeline again if data changes and then register new version of the model once the run is complete.
        For more information, see `Schedule machine learning
        pipelines <https://docs.microsoft.com/azure/machine-learning/how-to-schedule-pipelines>`_ and `Trigger a run
        of a Machine Learning pipeline from a Logic
        App <https://docs.microsoft.com/azure/machine-learning/how-to-trigger-published-pipeline>`_.

        The following example shows how to create an AutoMLStep.

        .. code-block:: python

            automl_step = AutoMLStep(
                name='automl_module',
                automl_config=automl_config,
                outputs=[metrics_data, model_data],
                allow_reuse=True)

        Full sample is available from
        https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/machine-learning-pipelines/intro-to-pipelines/aml-pipelines-with-automated-machine-learning-step.ipynb


        The following example show how to use the AutoMLStep object in a :class:`azureml.pipeline.core.Pipeline`.

        .. code-block:: python

            from azureml.pipeline.core import Pipeline
            pipeline = Pipeline(
                description="pipeline_with_automlstep",
                workspace=ws,
                steps=[automl_step])

        Full sample is available from
        https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/machine-learning-pipelines/intro-to-pipelines/aml-pipelines-with-automated-machine-learning-step.ipynb


        The above example shows one step in the pipeline. However, when using AutoMLStep in a real-world
        automated ML workflow, you will have a least one pipeline step that performs data preparation
        before the AutoMLStep, and another pipeline step after that registers the model. For example of this type
        of workflow, see the notebook https://aka.ms/automl-retrain-pipeline.

        To manage, check status, and get
        run details from the pipeline run, use the :class:`azureml.pipeline.steps.AutoMLStepRun` class.

        For more information about automated machine learning in Azure, see the article `What is automated
        machine learning? <https://docs.microsoft.com/azure/machine-learning/concept-automated-ml>`_.
        For more information about setting up an automated ML experiment without using a pipeline, see the
        article `Configure automated ML experiment in
        Python <https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train>`_.

    :param name: The name of the step.
    :type name: str
    :param automl_config: An AutoMLConfig object that defines the configuration for this AutoML run.
    :type automl_config: azureml.train.automl.automlconfig.AutoMLConfig
    :param inputs: A list of input port bindings.
    :type inputs: list[typing.Union[azureml.pipeline.core.graph.InputPortBinding,
        azureml.data.data_reference.DataReference,
        azureml.pipeline.core.PortDataReference,
        azureml.pipeline.core.builder.PipelineData]]
    :param outputs: A list of output port bindings.
    :type outputs: list[typing.Union[azureml.pipeline.core.builder.PipelineData,
        azureml.pipeline.core.graph.OutputPortBinding]]
    :param script_repl_params: Optional parameters to be replaced in a script, for example
        {'param1': 'value1', 'param2': 'value2'}.
    :type script_repl_params: dict
    :param allow_reuse: Indicates whether the step should reuse previous results when re-run with the same
        settings.

        Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
        parameters remain unchanged, the output from the previous run of this step is reused. When reusing
        the step, instead of submitting the job to compute, the results from the previous run are immediately
        made available to any subsequent steps. If you use Azure Machine Learning datasets as inputs, reuse is
        determined by whether the dataset's definition has changed, not by whether the underlying data has
        changed.
    :type allow_reuse: bool
    :param version: A version to assign to the step.
    :type version: str
    :param hash_paths: DEPRECATED. A list of paths to hash when checking for changes to the pipeline
        step contents.

        By default, all files under the ``path`` parameter in
        :class:`azureml.train.automl.automlconfig.AutoMLConfig` are hashed except files listed in
        .amlignore or .gitignore under ``path``. If there are no changes detected, the pipeline reuses
        the step contents from a previous run.
    :type hash_paths: list
    :param enable_default_model_output: Indicates whether or not the best model will be added as
        a default output. This can be used to retrieve the best model after the run has completed
        using the :class:`azureml.pipeline.steps.AutoMLStepRun` class.
        Note, if the default model output is not required, it is recommended to set this parameter to ``False``.
    :type enable_default_model_output: bool
    :param enable_default_metrics_output: Indicates whether or not all child run metrics will be added as
        a default output. This can be used to retrieve the child run metrics after the run has completed
        using the :class:`azureml.pipeline.steps.AutoMLStepRun` class.
        Note, if the default metrics output is not required, it is recommended to set this
        parameter to ``False``.
    :type enable_default_metrics_output: bool
    """

    DEFAULT_METRIC_PREFIX = 'default_metrics_'
    DEFAULT_MODEL_PREFIX = 'default_model_'
    AUTOML_CONFIG_PARAM_NAME = 'AutoMLConfig'

    _INTERMEDIATE_DATASET = 'intermediate_datasets'

    def __init__(self,
                 name,
                 automl_config,
                 inputs=None,
                 outputs=None,
                 script_repl_params=None,
                 allow_reuse=True,
                 version=None,
                 hash_paths=None,
                 enable_default_model_output=True,
                 enable_default_metrics_output=True,
                 **kwargs):
        """Initialize an AutoMLStep.

        :param name: The name of the step.
        :type name: str
        :param automl_config: An AutoMLConfig that defines the configuration for this AutoML run.
        :type automl_config: azureml.train.automl.automlconfig.AutoMLConfig
        :param inputs: A list of input port bindings.
        :type inputs: list[typing.Union[azureml.pipeline.core.graph.InputPortBinding,
            azureml.data.data_reference.DataReference,
            azureml.pipeline.core.PortDataReference,
            azureml.pipeline.core.builder.PipelineData]]
        :param outputs: A list of output port bindings.
        :type outputs: list[typing.Union[azureml.pipeline.core.builder.PipelineData,
            azureml.pipeline.core.graph.OutputPortBinding]]
        :param script_repl_params: Optional parameters to be replaced in a script, for example
            {'param1': 'value1', 'param2': 'value2'}.
        :param script_repl_params: Optional parameters to be replaced in a script.
        :type script_repl_params: dict
        :param allow_reuse: Indicates whether the step should reuse previous results when re-run with the same
            settings.

            Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
            parameters remain unchanged, the output from the previous run of this step is reused. When reusing
            the step, instead of submitting the job to compute, the results from the previous run are immediately
            made available to any subsequent steps. If you use Azure Machine Learning datasets as inputs, reuse is
            determined by whether the dataset's definition has changed, not by whether the underlying data has
            changed.
        :type allow_reuse: bool
        :param version: A version to assign to the step.
        :type version: str
        :param hash_paths: DEPRECATED. A list of paths to hash when checking for changes to the pipeline
            step contents.

            By default, all files under the ``path`` parameter in
            :class:`azureml.train.automl.automlconfig.AutoMLConfig` are hashed except files listed in
            .amlignore or .gitignore under ``path``. If there are no changes detected, the pipeline reuses
            the step contents from a previous run.
        :type hash_paths: list
        :param enable_default_model_output: Indicates whether or not the best model will be added as
            a default output. This can be used to retrieve the best model after the run has completed
            using the :class:`azureml.pipeline.steps.AutoMLStepRun` class.
            Note, if the default model output is not required, it is recommended to set this parameter to ``False``.
        :type enable_default_model_output: bool
        :param enable_default_metrics_output: Indicates whether or not all child run metrics will be added as
            a default output. This can be used to retrieve the child run metrics after the run has completed
            using the :class:`azureml.pipeline.steps.AutoMLStepRun` class.
            Note, if the default metrics output is not required, it is recommended to set this
            parameter to ``False``.
        :type enable_default_metrics_output: bool
        """
        if name is None:
            raise ConfigException._with_error(
                AzureMLError.create(ArgumentBlankOrEmpty, target="name", argument_name="name")
            )
        if not isinstance(name, str):
            raise ConfigException._with_error(
                AzureMLError.create(ArgumentInvalid, target="name", argument_name="name", expected_type="str")
            )
        if automl_config is None:
            raise ConfigException._with_error(
                AzureMLError.create(ArgumentBlankOrEmpty, target="automl_config", argument_name="automl_config")
            )
        if not isinstance(automl_config, AutoMLConfig):
            raise ConfigException._with_error(
                AzureMLError.create(
                    ArgumentInvalid, target="automl_config", argument_name="automl_config",
                    expected_type="azureml.train.automl.automlconfig.AutoMLConfig"
                )
            )

        PipelineStep._process_pipeline_io(None, inputs, outputs)

        self._allow_reuse = allow_reuse
        self._version = version

        self._params = {}
        self._pipeline_params_implicit = PipelineStep._get_pipeline_parameters_implicit()
        self._update_param_bindings()

        self._automl_config = automl_config
        self._passthru_automl_config = True

        self._enable_default_model_output = enable_default_model_output
        self._enable_default_metrics_output = enable_default_metrics_output

        self._source_directory = self._automl_config.user_settings['path']

        if hash_paths:
            logging.warning("Parameter 'hash_paths' is deprecated, will be removed. " +
                            "All files under  `path` and the `data_script` file specified " +
                            "in `AutoMLConfig` is hashed except files listed in " +
                            ".amlignore or .gitignore under `path`.")

        self._script_name = None
        if self._automl_config.user_settings.get("data_script") is not None:
            head, tail = ntpath.split(self._automl_config.user_settings.get("data_script"))
            self._script_name = tail or ntpath.basename(head)
            script_path = os.path.join(self._source_directory, self._script_name)
            self._process_script(script_path, script_repl_params)

        self._default_metrics_output = None
        self._default_model_output = None

        inputs = inputs or []
        inputs = inputs[:]
        AutoMLStep._update_inputs(automl_config, inputs)

        super(AutoMLStep, self).__init__(name=name, inputs=inputs, outputs=outputs)

    def _process_script(self, script_path, script_repl_params):
        import re
        pattern = re.compile(r"@@(?P<param_name>\w+)@@")

        def resolve_input_path(matchobj):
            replacement_str = script_repl_params.get(matchobj.group('param_name'))
            if replacement_str:
                return replacement_str
            else:
                print('found pattern:', matchobj.group('param_name'), ', but no replacement has been provided')

        self._sub_params_in_script(script_path, pattern, resolve_input_path)

    def create_node(self, graph, default_datastore, context):
        """Create a node from this AutoML step and add to the given graph.

        This method is not intended to be used directly. When a pipeline is instantiated with this step, Azure ML
        automatically passes the parameters required through this method so that step can be added to a pipeline
        graph that represents the workflow.

        :param graph: The graph object to add the node to.
        :type graph: azureml.pipeline.core.graph.Graph
        :param default_datastore: The default datastore.
        :type default_datastore: typing.Union[azureml.data.azure_storage_datastore.AbstractAzureStorageDatastore,
            azureml.data.azure_data_lake_datastore.AzureDataLakeDatastore]
        :param context: The graph context.
        :type context: azureml.pipeline.core._GraphContext

        :return: The created node.
        :rtype: azureml.pipeline.core.graph.Node
        """
        # Aether does not allow spaces in PipelineData name so we convert
        # whitespace to _
        safe_name = self.name.replace(" ", "_")
        if self._enable_default_metrics_output:
            self._default_metrics_output = PipelineData(name=AutoMLStep.DEFAULT_METRIC_PREFIX + safe_name,
                                                        datastore=default_datastore,
                                                        pipeline_output_name='_default_metrics_' + safe_name,
                                                        training_output=TrainingOutput(type='Metrics'))
            self._default_metrics_output._set_producer(self)
            self._outputs.append(self._default_metrics_output)

        if self._enable_default_model_output:
            self._default_model_output = PipelineData(name=AutoMLStep.DEFAULT_MODEL_PREFIX + safe_name,
                                                      datastore=default_datastore,
                                                      pipeline_output_name='_default_model_' + safe_name,
                                                      training_output=TrainingOutput(type='Model'))
            self._default_model_output._set_producer(self)
            self._outputs.append(self._default_model_output)

        input_bindings, output_bindings = self.create_input_output_bindings(self._inputs, self._outputs,
                                                                            default_datastore)

        settings = self._get_automl_settings(context)
        self._params.update(settings)

        (resolved_arguments, annotated_arguments) = \
            self.resolve_input_arguments(self._arguments, self._inputs, self._outputs, list(self._params))

        if resolved_arguments is not None and len(resolved_arguments) > 0:
            # workaround to let the backend use the structured argument list in place
            # of the module parameter for arguments
            self._params['Arguments'] = "USE_STRUCTURED_ARGUMENTS"

        def _get_param_def(param_name):
            is_metadata_param = param_name in AutoMLStep.AUTOML_CONFIG_PARAM_NAME

            if param_name in self._pipeline_params_implicit:
                return ParamDef(param_name,
                                default_value=self._params[param_name],
                                is_metadata_param=is_metadata_param,
                                set_env_var=True,
                                env_var_override="AML_PARAMETER_{0}".format(param_name))
            else:
                return ParamDef(param_name,
                                default_value=self._params[param_name],
                                is_metadata_param=is_metadata_param,
                                is_optional=True)

        param_defs = [_get_param_def(param_name) for param_name in self._params]

        module_def = self.create_module_def(execution_type="AutoMLCloud",
                                            input_bindings=input_bindings,
                                            output_bindings=output_bindings,
                                            param_defs=param_defs,
                                            allow_reuse=self._allow_reuse, version=self._version)

        module_builder = _ModuleBuilder(
            snapshot_root=self._source_directory,
            context=context,
            module_def=module_def,
            arguments=annotated_arguments)

        node = graph.add_module_node(
            self.name,
            input_bindings=input_bindings,
            output_bindings=output_bindings,
            param_bindings=self._params,
            module_builder=module_builder)

        PipelineStep._configure_pipeline_parameters(graph, node,
                                                    pipeline_params_implicit=self._pipeline_params_implicit)

        return node

    def _get_automl_settings(self, context):

        self._automl_config._validate_config_settings(context._workspace)
        fit_params = self._automl_config._get_fit_params()
        user_settings = {k: v for (k, v) in self._automl_config.user_settings.items() if k not in fit_params}

        # The experiment object contained in the graph context is not actually the user's experiment.
        # The string "placeholder" will be used until the pipeline is submitted and the experiment gets
        # replaced by the real experiment.
        experiment = Experiment(context._workspace, context.experiment_name, _create_in_cloud=False)
        settings_obj = AzureAutoMLSettings(experiment, **user_settings)
        experiment_state = AzureExperimentState(
            experiment,
            settings_obj,
            _create_partial_client=True
        )

        settings = experiment_state.automl_settings.as_serializable_dict()

        if not self._source_directory:
            self._source_directory = settings['path']

        # parameters for run configuration
        run_configuration = fit_params['run_configuration']
        if isinstance(run_configuration, str):
            run_config_object = RunConfiguration.load(
                experiment_state.automl_settings.path, run_configuration)
        else:
            run_config_object = run_configuration

        compute_target = fit_params.get('compute_target')
        if compute_target is None:
            raise ConfigException._with_error(
                AzureMLError.create(ArgumentBlankOrEmpty, target="compute_target", argument_name="compute_target")
            )
        try:
            settings['MLCComputeType'] = compute_target.type
        except AttributeError:
            raise ConfigException._with_error(
                AzureMLError.create(ArgumentInvalid, target="compute_target", argument_name="compute_target",
                                    expected_type="ComputeTarget")
            )

        scenario = experiment_state.automl_settings.scenario

        if scenario in constants.Scenarios.VISION_SET:
            # Retrieve curated environment from JOS for vision scenarios
            logger.info("Vision scenario using JOS to retrieve CE.")
            environment = experiment_state.jasmine_client.get_curated_environment(
                scenario=scenario,
                enable_dnn=experiment_state.automl_settings.enable_dnn,
                enable_gpu=True,
                compute=compute_target.name,
                compute_sku=compute_target.vm_size
            )
            run_config_object.environment = environment
        else:
            # Retrieve a default environment to check against users submitted environment.
            # If the submitted environment doesnt have any custom logic, leverage CE.
            default_env_unpinned = CondaDependencies.create(pin_sdk_version=False).__dict__
            default_env_pinned = CondaDependencies.create(pin_sdk_version=True).__dict__
            default_rc_env = RunConfiguration().environment.python.conda_dependencies.__dict__
            user_env = run_config_object.environment.python.conda_dependencies.__dict__
            if user_env == default_env_unpinned or user_env == default_env_pinned or user_env == default_rc_env:
                logger.info("Default environment using JOS to retrieve CE.")
                # Validate non-prod scenario requirements are met.
                if scenario == constants.Scenarios._NON_PROD:
                    validate_non_prod_env_exists(context._workspace)

                # enable_gpu will be used as a fallback is JOS fails to parse compute_sku.
                # We will always set it to false as we don't want fallback behavior to use
                # gpu if it isn't present.
                environment = experiment_state.jasmine_client.get_curated_environment(
                    scenario=scenario,
                    enable_dnn=experiment_state.automl_settings.enable_dnn,
                    enable_gpu=False,
                    compute=compute_target.name,
                    compute_sku=compute_target.vm_size
                )
                run_config_object.environment = environment
            else:
                # If user modified their environment for job submission, we should honor their dependencies
                # so we cannot use CE.
                logger.info("Non-default environment using environment utilities.")
                run_config_object = modify_run_configuration(
                    experiment_state.automl_settings,
                    run_config_object,
                    logger
                )

        run_config_params = self._get_runconfig_as_dict(run_config_object)

        # TODO: refactor this to avoid duplicate code and more closely
        # match the code path of the non-pipeline remote submit.
        # Set the compute_target to fix hyperdrive runs. This matches
        # what is done inside of AzureAutoMLClient.fit().
        if compute_target.name != constants.ComputeTargets.LOCAL:
            experiment_state.automl_settings.compute_target = compute_target.name

        X = fit_params.get('X', None)
        y = fit_params.get('y', None)
        X_valid = fit_params.get('X_valid', None)
        y_valid = fit_params.get('y_valid', None)
        sample_weight = fit_params.get('sample_weight', None)
        sample_weight_valid = fit_params.get('sample_weight_valid', None)
        cv_splits_indices = fit_params.get('cv_splits_indices', None)
        training_data = fit_params.get('training_data', None)
        validation_data = fit_params.get('validation_data', None)
        test_data = fit_params.get('test_data', None)

        dataset_utilities.ensure_saved(
            context._workspace, X=X, y=y, sample_weight=sample_weight, X_valid=X_valid, y_valid=y_valid,
            sample_weight_valid=sample_weight_valid, training_data=training_data, validation_data=validation_data,
            test_data=test_data
        )
        dataset_utilities.collect_usage_telemetry(
            compute=run_configuration.target,
            spark_context=self._automl_config.user_settings.get('spark_context', None),
            X=X, y=y, sample_weight=sample_weight,
            X_valid=X_valid, y_valid=y_valid, sample_weight_valid=sample_weight_valid,
            training_data=training_data, validation_data=validation_data, test_data=test_data
        )

        X, y, sample_weight, X_valid, y_valid, sample_weight_valid = dataset_utilities.convert_inputs(
            X, y, sample_weight,
            X_valid, y_valid, sample_weight_valid
        )

        X, y, sample_weight, X_valid, y_valid, sample_weight_valid, \
            training_data, validation_data, test_data = \
            self._handle_intermediate_dataset(
                settings, X=X, y=y, sample_weight=sample_weight, X_valid=X_valid, y_valid=y_valid,
                sample_weight_valid=sample_weight_valid, training_data=training_data,
                validation_data=validation_data, test_data=test_data
            )

        if training_data is not None:
            if dataprep_utilities.is_dataflow(training_data):
                dataprep_json = dataprep_utilities.\
                    get_dataprep_json_dataset(training_data=training_data,
                                              validation_data=validation_data,
                                              test_data=test_data)
            else:
                dataprep_json = dataset_utilities.\
                    get_datasets_json(training_data=training_data,
                                      validation_data=validation_data,
                                      test_data=test_data)
        else:
            dataprep_json = dataprep_utilities.get_dataprep_json(X=X, y=y,
                                                                 sample_weight=sample_weight,
                                                                 X_valid=X_valid,
                                                                 y_valid=y_valid,
                                                                 sample_weight_valid=sample_weight_valid,
                                                                 cv_splits_indices=cv_splits_indices)

        if dataprep_json is not None:
            # escape quotations in json_str before sending to jasmine
            dataprep_json = dataprep_json.replace('\\', '\\\\').replace('"', '\\"')

        if self._passthru_automl_config:
            # CreateParentRunDto which will be passed through Jasmine
            parent_run_dto = driver_utilities.create_parent_run_dto(experiment_state, dataprep_json)
            driver_utilities.validate_input(experiment_state, parent_run_dto)

            settings[AutoMLStep.AUTOML_CONFIG_PARAM_NAME] = json.dumps(parent_run_dto.as_dict())
            logging.info('passthru automl config: {}'.format(settings[AutoMLStep.AUTOML_CONFIG_PARAM_NAME]))

        # parameters for CreateParentRunDto
        timeout = None
        if experiment_state.automl_settings.iteration_timeout_minutes:
            timeout = experiment_state.automl_settings.iteration_timeout_minutes * 60
        settings['max_time_seconds'] = timeout
        settings['target'] = run_config_object.target
        settings['targettype'] = 'mlc'
        settings['num_iterations'] = experiment_state.automl_settings.iterations
        settings['training_type'] = None
        settings['acquisition_function'] = None
        settings['metrics'] = 'accuracy'
        settings['primary_metric'] = experiment_state.automl_settings.primary_metric
        settings['train_split'] = experiment_state.automl_settings.validation_size
        settings['acquisition_parameter'] = 0.0
        settings['num_cross_validation'] = experiment_state.automl_settings.n_cross_validations
        settings['data_prep_json_string'] = dataprep_json
        settings['enable_subsampling'] = experiment_state.automl_settings.enable_subsampling

        settings.update(run_config_params)

        # reformatting list to comma separated string for backend until we have comprehensive solution
        for key in ['whitelist_models', 'blacklist_models', 'DockerArguments', 'SparkRepositories']:
            value = settings.get(key, None)
            if isinstance(value, list):
                settings[key] = ",".join([str(x) for x in value])

        return settings

    def _get_runconfig_as_dict(self, run_config=None):
        """Set runconfig for AutoML step.

        :param run_config: run config object
        :type run_config: RunConfiguration

        :return: run config params
        :rtype: Dictionary
        """
        if not isinstance(run_config, RunConfiguration):
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentType, target="run_configuration",
                    argument="run_configuration", actual_type=type(run_config),
                    expected_types="azureml.core.runconfig.RunConfiguration")
            )

        spark_maven_packages = []
        for package in run_config.environment.spark.packages:
            package_dict = {'artifact': package.artifact, 'group': package.group, 'version': package.version}
            spark_maven_packages.append(package_dict)

        spark_configuration = ';'.join(["{0}={1}".format(key, val) for key, val
                                        in run_config.spark.configuration.items()])

        environment_variables = ';'.join(["{0}={1}".format(key, val) for key, val
                                          in run_config.environment.environment_variables.items()])

        serialized = _commands._serialize_run_config_to_dict(run_config)

        conda_dependencies = None
        try:
            conda_dependencies = serialized['environment']['python']['condaDependencies']
        except KeyError:
            pass

        docker_arguments = None
        if len(run_config.environment.docker.arguments) > 0:
            docker_arguments = ",".join([str(x) for x in run_config.environment.docker.arguments])

        run_config_params = {'Script': run_config.script,
                             'Framework': run_config.framework,
                             'Communicator': run_config.communicator,
                             'DockerEnabled': run_config.environment.docker.enabled,
                             'BaseDockerImage': run_config.environment.docker.base_image,
                             'SharedVolumes': run_config.environment.docker.shared_volumes,
                             'DockerArguments': docker_arguments,
                             'SparkRepositories': run_config.environment.spark.repositories,
                             'SparkMavenPackages': spark_maven_packages,
                             'SparkConfiguration': spark_configuration,
                             'InterpreterPath': run_config.environment.python.interpreter_path,
                             'UserManagedDependencies': run_config.environment.python.user_managed_dependencies,
                             'MaxRunDurationSeconds': run_config.max_run_duration_seconds,
                             'EnvironmentVariables': environment_variables,
                             'PrecachePackages': run_config.environment.spark.precache_packages,
                             'HistoryOutputCollection': run_config.history.output_collection,
                             'NodeCount': run_config.node_count,
                             'YarnDeployMode': run_config.hdi.yarn_deploy_mode,
                             'CondaDependencies': json.dumps(conda_dependencies),
                             'MpiProcessCountPerNode': run_config.mpi.process_count_per_node,
                             'TensorflowWorkerCount': run_config.tensorflow.worker_count,
                             'TensorflowParameterServerCount': run_config.tensorflow.parameter_server_count,
                             'AMLComputeName': run_config.amlcompute._name,
                             'AMLComputeVmSize': run_config.amlcompute.vm_size,
                             'AMLComputeVmPriority': run_config.amlcompute.vm_priority,
                             'AMLComputeLocation': None,
                             'AMLComputeRetainCluster': run_config.amlcompute._retain_cluster,
                             'AMLComputeNodeCount': run_config.amlcompute._cluster_max_node_count,
                             'SourceDirectoryDataStore': run_config.source_directory_data_store,
                             'DirectoriesToWatch': run_config.history.directories_to_watch
                             }

        return run_config_params

    def _update_param_bindings(self):
        for pipeline_param in self._pipeline_params_implicit.values():
            if pipeline_param.name not in self._params:
                self._params[pipeline_param.name] = pipeline_param
            else:
                raise Exception('Parameter name {0} is already in use'.format(pipeline_param.name))

    @staticmethod
    def _update_inputs(automl_config, inputs):
        settings = automl_config.user_settings
        existing_tabular_input_names = set([
            dataset.input_name for dataset in
            filter(lambda input: isinstance(input, PipelineOutputTabularDataset) or
                   isinstance(input, OutputTabularDatasetConfig), inputs)
        ])

        for arg in ['X', 'y', 'sample_weight', 'X_valid', 'y_valid', 'sample_weight_valid', 'training_data',
                    'validation_data', 'test_data']:
            arg_value = settings.get(arg, None)

            if not isinstance(arg_value, PipelineOutputTabularDataset)\
                    and not isinstance(arg_value, TabularDataset)\
                    and not isinstance(arg_value, OutputTabularDatasetConfig)\
                    and not isinstance(arg_value, DatasetConsumptionConfig):
                continue

            if arg in existing_tabular_input_names:
                continue

            if isinstance(arg_value, DatasetConsumptionConfig):
                if not isinstance(arg_value.dataset, TabularDataset)\
                        and not isinstance(arg_value.dataset, OutputTabularDatasetConfig):
                    raise ValueError("The DatasetConsumptionConfig for {} must be constructed with a ".format(arg) +
                                     "TabularDataset or OutputTabularDatasetConfig.")
                if arg_value.mode != DIRECT_MODE:
                    raise ValueError("The DatasetConsumptionConfig for {} must be set to 'direct' mode.")
                if arg_value.name != arg:
                    logging.warning("The DatasetConsumptionConfig originally named {} will be renamed to {}.".format(
                        arg_value.name, arg
                    ))
                    arg_value.name = arg
                inputs.append(arg_value)
            else:
                try:
                    inputs.append(arg_value.as_named_input(arg))
                except AttributeError:
                    inputs.append(arg_value.as_input(arg))

    def _handle_intermediate_dataset(self, settings, X=None, y=None, sample_weight=None, X_valid=None,
                                     y_valid=None, sample_weight_valid=None, training_data=None,
                                     validation_data=None, test_data=None):
        updated_args = []
        args = [
            ('X', X), ('y', y), ('sample_weight', sample_weight), ('X_valid', X_valid), ('y_valid', y_valid),
            ('sample_weight_valid', sample_weight_valid), ('training_data', training_data),
            ('validation_data', validation_data), ('test_data', test_data)
        ]
        for arg_name, arg_value in args:
            if isinstance(arg_value, PipelineOutputTabularDataset)\
                    or (isinstance(arg_value, DatasetConsumptionConfig) and
                        isinstance(arg_value.dataset, OutputTabularDatasetConfig))\
                    or isinstance(arg_value, OutputTabularDatasetConfig):
                updated_args.append(None)
                settings[AutoMLStep._INTERMEDIATE_DATASET] = \
                    [*settings.get(AutoMLStep._INTERMEDIATE_DATASET, []), arg_name]
            else:
                updated_args.append(arg_value)

        if AutoMLStep._INTERMEDIATE_DATASET in settings:
            settings[AutoMLStep._INTERMEDIATE_DATASET] = ';'.join(settings[AutoMLStep._INTERMEDIATE_DATASET])

        return updated_args


class AutoMLStepRun(AutoMLRun):
    """
    Provides information about an automated ML experiment run and methods for retrieving default outputs.

    The AutoMLStepRun class is used to manage, check status, and retrieve run details once an automated ML run is
    submitted in a pipeline. In addition, this class can be used to get the default outputs of the
    :class:`azureml.pipeline.steps.AutoMLStep` via the :class:`azureml.pipeline.core.StepRun` class.

    :param step_run: The step run object which created from a pipeline.
    :type step_run: azureml.pipeline.core.StepRun
    """

    def __init__(self, step_run):
        """
        Initialize a automl step run.

        :param step_run: The step run object which created from a pipeline.
        :type step_run: azureml.pipeline.core.StepRun
        """
        self._step_run = step_run
        self._safe_name = step_run._run_name.replace(" ", "_")

        super(self.__class__, self).__init__(step_run._context._experiment, step_run._run_id)

    def get_default_metrics_output(self):
        """
        Return the default metrics output of the current run.

        :return: The default metrics output of the current run.
        :rtype: azureml.pipeline.core.StepRunOutput
        """
        default_metrics_output_name = AutoMLStep.DEFAULT_METRIC_PREFIX + self._safe_name
        return self._step_run.get_output(default_metrics_output_name)

    def get_default_model_output(self):
        """
        Return the default model output of the current run.

        :return: The default model output of the current run.
        :rtype: azureml.pipeline.core.StepRunOutput
        """
        default_model_output_name = AutoMLStep.DEFAULT_MODEL_PREFIX + self._safe_name
        return self._step_run.get_output(default_model_output_name)
