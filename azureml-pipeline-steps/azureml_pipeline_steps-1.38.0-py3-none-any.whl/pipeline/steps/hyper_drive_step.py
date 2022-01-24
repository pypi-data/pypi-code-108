# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains funtionality for creating and managing Azure ML Pipeline steps that run hyperparameter tuning."""
import json
import logging
from azureml.data.data_reference import DataReference
from azureml.pipeline.core import PipelineStep, PipelineData, TrainingOutput
from azureml.pipeline.core._module_builder import _ModuleBuilder
from azureml.pipeline.core.graph import ParamDef, OutputPortBinding
from azureml.train.hyperdrive.run import HyperDriveRun


module_logger = logging.getLogger(__name__)


class HyperDriveStep(PipelineStep):
    """Creates an Azure ML Pipeline step to run hyperparameter tunning for Machine Learning model training.

    For an example of using HyperDriveStep, see the notebook https://aka.ms/pl-hyperdrive.

    .. remarks::

        Note that the arguments to the entry script used in the estimator object (e.g.,
        the :class:`azureml.train.dnn.TensorFlow` object)
        must be specified as *list* using the ``estimator_entry_script_arguments`` parameter when instantiating
        an HyperDriveStep. The estimator parameter ``script_params`` accepts a dictionary. However,
        ``estimator_entry_script_argument`` parameter expects arguments as a list.

        The HyperDriveStep initialization involves specifying a list of
        :class:`azureml.data.data_reference.DataReference` objects with the ``inputs`` parameter. In Azure ML
        Pipelines, a pipeline step can take another step's output or DataReference objects as input. Therefore,
        when creating an HyperDriveStep, the ``inputs`` and ``outputs`` parameters must be set explicitly, which
        overrides ``inputs`` parameter specified in the Estimator object.

        The best practice for working with HyperDriveStep is to use a separate folder for scripts and any dependent
        files associated with the step, and specify that folder as the estimator
        object's ``source_directory``. For example, see the ``source_directory`` parameter of the
        :class:`azureml.train.dnn.TensorFlow` class. Doing so has two benefits. First, it helps reduce the size
        of the snapshot created for the step because only what is needed for the step is snapshotted. Second,
        the step's output from a previous run can be reused if there are  no changes to the ``source_directory``
        that would trigger a re-upload of the snaphot.

        The following example shows how to use HyperDriveStep in an Azure Machine Learning Pipeline.

        .. code-block:: python

            metrics_output_name = 'metrics_output'
            metrics_data = PipelineData(name='metrics_data',
                                        datastore=datastore,
                                        pipeline_output_name=metrics_output_name,
                                        training_output=TrainingOutput("Metrics"))

            model_output_name = 'model_output'
            saved_model = PipelineData(name='saved_model',
                                        datastore=datastore,
                                        pipeline_output_name=model_output_name,
                                        training_output=TrainingOutput("Model",
                                                                       model_file="outputs/model/saved_model.pb"))

            hd_step_name='hd_step01'
            hd_step = HyperDriveStep(
                name=hd_step_name,
                hyperdrive_config=hd_config,
                inputs=[data_folder],
                outputs=[metrics_data, saved_model])

        Full sample is available from
        https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/machine-learning-pipelines/intro-to-pipelines/aml-pipelines-parameter-tuning-with-hyperdrive.ipynb


    :param name: [Required] The name of the step.
    :type name: str
    :param hyperdrive_config: [Required] A HyperDriveConfig that defines the configuration for the
        HyperDrive run.
    :type hyperdrive_config: azureml.train.hyperdrive.HyperDriveConfig
    :param estimator_entry_script_arguments: A list of command-line arguments for the
        estimator entry script. If the Estimator's entry script does not accept commandline arguments,
        set this parameter value to an empty list.
    :type estimator_entry_script_arguments: list
    :param inputs: A list of input port bindings.
    :type inputs: list[typing.Union[azureml.pipeline.core.graph.InputPortBinding,
                    azureml.pipeline.core.pipeline_output_dataset.PipelineOutputAbstractDataset,
                    azureml.data.data_reference.DataReference,
                    azureml.pipeline.core.PortDataReference,
                    azureml.pipeline.core.builder.PipelineData,
                    azureml.data.dataset_consumption_config.DatasetConsumptionConfig]]
    :param outputs: A list of output port bindings
    :type outputs: list[typing.Union[azureml.pipeline.core.builder.PipelineData,
                        azureml.data.output_dataset_config.OutputDatasetConfig,
                        azureml.pipeline.core.pipeline_output_dataset.PipelineOutputAbstractDataset,
                        azureml.pipeline.core.graph.OutputPortBinding]]
    :param metrics_output: Optional value specifying the location to store HyperDrive run metrics as a
                        JSON file.
    :type metrics_output: typing.Union[azureml.pipeline.core.builder.PipelineData,
                        azureml.data.data_reference.DataReference,
                        azureml.pipeline.core.graph.OutputPortBinding]
    :param allow_reuse: Indicates whether the step should reuse previous results when re-run with the same settings.
        Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
        parameters remain unchanged, the output from the previous run of this step is reused. When reusing
        the step, instead of submitting the job to compute, the results from the previous run are immediately
        made available to any subsequent steps.  If you use Azure Machine Learning datasets as inputs, reuse is
        determined by whether the dataset's definition has changed, not by whether the underlying data has
        changed.
    :type allow_reuse: bool
    :param version: An optional version tag to denote a change in functionality for the module.
    :type version: str
    """

    _run_config_param_name = 'HyperDriveRunConfig'
    _run_reuse_hashable_config = 'HDReuseHashableRunConfig'
    _primary_metric_goal = 'PrimaryMetricGoal'
    _primary_metric_name = 'PrimaryMetricName'

    def __init__(self, name, hyperdrive_config,
                 estimator_entry_script_arguments=None, inputs=None, outputs=None,
                 metrics_output=None, allow_reuse=True, version=None):
        """Create an Azure ML Pipeline step to run hyperparameter tunning for Machine Learning model training.

        :param name: [Required] The name of the step.
        :type name: str
        :param hyperdrive_config: [Required] A HyperDriveConfig that defines the configuration for the
            HyperDrive run.
        :type hyperdrive_config: azureml.train.hyperdrive.HyperDriveConfig
        :param estimator_entry_script_arguments: A list of command-line arguments for the
            estimator entry script. If the Estimator's entry script does not accept commandline arguments,
            set this parameter value to an empty list.
        :type estimator_entry_script_arguments: list
        :param inputs: A list of input port bindings.
        :type inputs: list[typing.Union[azureml.pipeline.core.graph.InputPortBinding,
                    azureml.pipeline.core.pipeline_output_dataset.PipelineOutputAbstractDataset,
                    azureml.data.data_reference.DataReference,
                    azureml.pipeline.core.PortDataReference,
                    azureml.pipeline.core.builder.PipelineData,
                    azureml.data.dataset_consumption_config.DatasetConsumptionConfig]]
        :param outputs: A list of output port bindings.
        :type outputs: list[typing.Union[azureml.pipeline.core.builder.PipelineData,
                    azureml.pipeline.core.pipeline_output_dataset.PipelineOutputAbstractDataset,
                    azureml.pipeline.core.graph.OutputPortBinding]]
        :param metrics_output: An optional value specifying the location to store HyperDrive run metrics as a
                    JSON file.
        :type metrics_output: typing.Union[azureml.pipeline.core.builder.PipelineData,
                            azureml.data.data_reference.DataReference,
                            azureml.pipeline.core.graph.OutputPortBinding]
        :param allow_reuse: Indicates whether the step should reuse previous results when re-run with the same
            settings. Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
            parameters remain unchanged, the output from the previous run of this step is reused. When reusing
            the step, instead of submitting the job to compute, the results from the previous run are immediately
            made available to any subsequent steps. If you use Azure Machine Learning datasets as inputs, reuse is
            determined by whether the dataset's definition has changed, not by whether the underlying data has
            changed.
        :type allow_reuse: bool
        :param version: version
        :type version: str
        """
        if name is None:
            raise ValueError('name is required')
        if not isinstance(name, str):
            raise ValueError('name must be a string')

        if hyperdrive_config is None:
            raise ValueError('hyperdrive_config is required')
        from azureml.train.hyperdrive import HyperDriveConfig
        if not isinstance(hyperdrive_config, HyperDriveConfig):
            raise ValueError('Unexpected hyperdrive_config type: {}'.format(type(hyperdrive_config)))

        if hyperdrive_config.pipeline is not None:
            raise ValueError('hyperdrive_config initiated with pipeline is not supported. Please use estimator.')

        using_script_run_config = False

        # resetting estimator args and data refs as we'll use the ones provided to HyperDriveStep
        if hyperdrive_config.estimator is not None:
            run_config = hyperdrive_config.estimator.run_config
        elif hyperdrive_config.run_config is not None:
            run_config = hyperdrive_config.run_config
            using_script_run_config = True
        else:
            raise ValueError('run_config has not been provided either from Estimator or HyperDriveConfig')

        if run_config.arguments and not using_script_run_config:
            raise ValueError('arguments in Estimator run_config should not be provided. '
                             'Please use arguments in the step')
        if hasattr(run_config, 'data_references') and run_config.data_references:
            raise ValueError('data_references in Estimator run_config should not be provided.'
                             'Please use inputs in the step')

        if estimator_entry_script_arguments is None and not using_script_run_config:
            # estimator_entry_script_arguments is not required for ScriptRunConfig
            raise ValueError('estimator_entry_script_arguments is a required parameter if using Estimator.'
                             'If the Estimator''s entry '
                             'script does not accept commandline arguments, set the parameter value to empty list')
        if estimator_entry_script_arguments is not None and not isinstance(estimator_entry_script_arguments, list):
            raise ValueError('estimator_entry_script_arguments expects arguments as a list.')

        if using_script_run_config:
            if estimator_entry_script_arguments is not None and run_config.arguments is not None:
                raise ValueError("Only one of estimator_entry_script_arguments and ScriptRunConfig.arguments "
                                 "should be set.")

            if run_config.arguments:
                if isinstance(run_config.arguments, str):
                    estimator_entry_script_arguments = [run_config.arguments]
                elif isinstance(run_config.arguments, list):
                    estimator_entry_script_arguments = run_config.arguments
                else:
                    raise ValueError("ScriptRunConfig arguments should be a list or a string.")

            if estimator_entry_script_arguments is None:
                estimator_entry_script_arguments = []

        PipelineStep._process_pipeline_io(estimator_entry_script_arguments, inputs, outputs)

        self._allow_reuse = allow_reuse
        self._version = version

        self._params = {}
        self._pipeline_params_implicit = PipelineStep._get_pipeline_parameters_implicit(
            arguments=estimator_entry_script_arguments)
        self._update_param_bindings()

        self._hyperdrive_config = hyperdrive_config

        if outputs is None:
            outputs = []

        if metrics_output is not None:
            if not isinstance(metrics_output, PipelineData) and not isinstance(metrics_output, DataReference) and \
                    not isinstance(metrics_output, OutputPortBinding):
                raise ValueError("Unexpected metrics_output type: %s" % type(metrics_output))

            if isinstance(metrics_output, DataReference):
                metrics_output = OutputPortBinding(
                    name=metrics_output.data_reference_name,
                    datastore=metrics_output.datastore,
                    bind_mode=metrics_output.mode,
                    path_on_compute=metrics_output.path_on_compute,
                    overwrite=metrics_output.overwrite,
                    training_output=TrainingOutput("Metrics"))
            else:
                metrics_output._training_output = TrainingOutput("Metrics")

            outputs.append(metrics_output)

        self._params[HyperDriveStep._primary_metric_goal] = hyperdrive_config._primary_metric_config['goal'].lower()
        self._params[HyperDriveStep._primary_metric_name] = hyperdrive_config._primary_metric_config['name']

        super(HyperDriveStep, self).__init__(name=name, inputs=inputs, outputs=outputs,
                                             arguments=estimator_entry_script_arguments)

    def create_node(self, graph, default_datastore, context):
        """Create a node from the HyperDrive step and add to the given graph.

        This method is not intended to be used directly. When a pipeline is instantiated with this step,
        Azure ML automatically passes the parameters required through this method so that step can be added to a
        pipeline graph that represents the workflow.

        :param graph: The graph object to add the node to.
        :type graph: azureml.pipeline.core.graph.Graph
        :param default_datastore: The default datastore.
        :type default_datastore:  typing.Union[azureml.data.azure_storage_datastore.AbstractAzureStorageDatastore,
                                    azureml.data.azure_data_lake_datastore.AzureDataLakeDatastore]
        :param context: The graph context.
        :type context: azureml.pipeline.core._GraphContext

        :return: The created node.
        :rtype: azureml.pipeline.core.graph.Node
        """
        hyperdrive_config, reuse_hashable_config = self._get_hyperdrive_config(context._workspace,
                                                                               context._experiment_name)
        self._params[HyperDriveStep._run_config_param_name] = json.dumps(hyperdrive_config)
        self._params[HyperDriveStep._run_reuse_hashable_config] = json.dumps(reuse_hashable_config)

        source_directory = self._hyperdrive_config.source_directory
        hyperdrive_snapshot_id = self._get_hyperdrive_snaphsot_id(hyperdrive_config)

        (resolved_arguments, annotated_arguments) = \
            self.resolve_input_arguments(self._arguments, self._inputs, self._outputs, self._params)

        if resolved_arguments is not None and len(resolved_arguments) > 0:
            # workaround to let the backend use the structured argument list in place
            # of the module parameter for arguments
            self._params['Arguments'] = "USE_STRUCTURED_ARGUMENTS"

        def _get_param_def(param_name):
            is_metadata_param = param_name in (HyperDriveStep._run_config_param_name,
                                               HyperDriveStep._run_reuse_hashable_config,
                                               HyperDriveStep._primary_metric_goal,
                                               HyperDriveStep._primary_metric_name)
            is_hashable = param_name != (HyperDriveStep._run_config_param_name)

            if param_name in self._pipeline_params_implicit:
                return ParamDef(param_name,
                                default_value=self._params[param_name],
                                is_metadata_param=is_metadata_param,
                                set_env_var=True,
                                calculate_hash=is_hashable,
                                env_var_override="AML_PARAMETER_{0}".format(param_name))
            else:
                return ParamDef(param_name,
                                default_value=self._params[param_name],
                                is_metadata_param=is_metadata_param,
                                calculate_hash=is_hashable)

        param_defs = [_get_param_def(param_name) for param_name in self._params]

        input_bindings, output_bindings = self.create_input_output_bindings(self._inputs, self._outputs,
                                                                            default_datastore)

        module_def = self.create_module_def(execution_type="HyperDriveCloud",
                                            input_bindings=input_bindings,
                                            output_bindings=output_bindings,
                                            param_defs=param_defs,
                                            allow_reuse=self._allow_reuse, version=self._version,
                                            arguments=annotated_arguments)

        module_builder = _ModuleBuilder(context=context,
                                        module_def=module_def,
                                        snapshot_root=source_directory,
                                        existing_snapshot_id=hyperdrive_snapshot_id,
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

    def _get_hyperdrive_config(self, workspace, experiment_name):
        from azureml.train.hyperdrive import _search

        telemetry_values = _search._get_telemetry_values(self._hyperdrive_config, workspace)

        if isinstance(telemetry_values, dict):
            telemetry_values['amlClientType'] = 'azureml-sdk-pipeline'
            telemetry_values['amlClientModule'] = __name__
            telemetry_values['amlClientFunction'] = self.create_node.__name__

        hyperdrive_dto = _search._create_experiment_dto(self._hyperdrive_config, workspace,
                                                        experiment_name, telemetry_values)

        hyperdrive_config = hyperdrive_dto.as_dict()
        hyperdrive_config_for_reuse_calculation = hyperdrive_dto.as_dict()

        definition = hyperdrive_config_for_reuse_calculation.get('platform_config', {}).get('Definition', {})
        if 'TelemetryValues' in definition:
            definition.pop('TelemetryValues')
        if 'SnapshotId' in definition:
            definition.pop('SnapshotId')

        return hyperdrive_config, hyperdrive_config_for_reuse_calculation

    def _update_param_bindings(self):
        for pipeline_param in self._pipeline_params_implicit.values():
            if pipeline_param.name not in self._params:
                self._params[pipeline_param.name] = pipeline_param
            else:
                raise Exception('Parameter name {0} is already in use'.format(pipeline_param.name))

    def _get_hyperdrive_snaphsot_id(self, hyperdrive_config):
        # if snapshot id is not present in config, raise error
        if ("platform_config" not in hyperdrive_config
                or "Definition" not in hyperdrive_config["platform_config"]
                or "SnapshotId" not in hyperdrive_config["platform_config"]["Definition"]):
            raise ValueError("SnaphsotId is not present")

        return hyperdrive_config["platform_config"]["Definition"]["SnapshotId"]


class HyperDriveStepRun(HyperDriveRun):
    """
    Manage, check status, and retrieve run details for a :class:`HyperDriveStep` pipeline step.

    HyperDriveStepRun provides the functionality of :class:`azureml.train.hyperdrive.HyperDriveRun` with
    the additional support of :class:`azureml.pipeline.core.StepRun`.
    The HyperDriveStepRun class enables you to  manage, check status, and retrieve run details for the HyperDrive
    run and each of its generated child runs. The StepRun class enables you to do this once the parent
    pipeline run is submitted and the pipeline has submitted the step run.

    :param step_run: The step run object created from submitting the pipeline.
    :type step_run: azureml.pipeline.core.StepRun
    """

    def __init__(self, step_run):
        """
        Initialize a HyperDriveStepRun.

        HyperDriveStepRun provides the functionality of :class:`azureml.train.hyperdrive.HyperDriveRun` with
        the additional support of :class:`azureml.pipeline.core.StepRun`.
        The HyperDriveRun class enables you to  manage, check status, and retrieve run details for the HyperDrive
        run and each of its generated child runs. The StepRun class enables you to do this once the parent
        pipeline run is submitted and the pipeline has submitted the step run.

        :param step_run: The step run object created from submitting the pipeline.
        :type step_run: azureml.pipeline.core.StepRun
        """
        step_type = step_run.properties.get('StepType', 'Unknown')
        if step_type != 'HyperDriveStep':
            message = 'Step run with wrong type has been provided. step_type: ' + step_type
            module_logger.error(message)
            raise ValueError(message)

        exp = step_run._experiment
        all_exp_runs = exp.get_runs(include_children=True)

        hyperdrive_run = None
        # TODO: only needed when runid is not linked b/w step and hyperdrive. can be removed after that
        for run in all_exp_runs:
            if run.name == step_run._run_id:
                hyperdrive_run = run

        if not hyperdrive_run:
            child_runs = list(step_run.get_children())
            if len(child_runs) == 1:
                hyperdrive_run = child_runs[0]

        if not hyperdrive_run:
            message = 'Cannot find hyperdrive run from the given step run: ' + step_run.name
            module_logger.error(message)
            raise ValueError(message)

        self._step_run = step_run

        super(self.__class__, self).__init__(exp, hyperdrive_run._run_id)
