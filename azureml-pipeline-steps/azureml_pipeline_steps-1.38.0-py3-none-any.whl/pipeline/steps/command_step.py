# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality to create an Azure ML Pipeline step that runs commands."""
import os
import sys
import shlex

from azureml.pipeline.core._python_script_step_base import _PythonScriptStepBase
from azureml.core.script_run_config import ScriptRunConfig


class CommandStep(_PythonScriptStepBase):
    r"""Create an Azure ML Pipeline step that runs a command.

    .. remarks::

        An CommandStep is a basic, built-in step to run a command on the given compute target. It takes
        a command as a parameter or from other parameters like runconfig. It also takes other optional
        parameters like compute target, inputs and outputs. You should use a :class:`azureml.core.ScriptRunConfig`
        or :class:`azureml.core.RunConfiguration` to specify requirements for the CommandStep, such as
        custom docker image.

        The best practice for working with CommandStep is to use a separate folder for the executable or
        script to run any dependent files associated with the step, and specify that folder with the
        ``source_directory`` parameter. Following this best practice has two benefits. First, it helps reduce
        the size of the snapshot created for the step because only what is needed for the step is snapshotted.
        Second, the step's output from a previous run can be reused if there are no changes to the
        ``source_directory`` that would trigger a re-upload of the snapshot.

        For the system-known commands ``source_directory`` is not required but you can still provide it with
        any dependent files associated with the step.

        The following code example shows how to use a CommandStep in a machine learning training scenario.
        To list files in linux:

        .. code-block:: python

            from azureml.pipeline.steps import CommandStep

            trainStep = CommandStep(name='list step',
                                    command='ls -lrt',
                                    compute_target=compute_target)

        To run a python script:

        .. code-block:: python

            from azureml.pipeline.steps import CommandStep

            trainStep = CommandStep(name='train step',
                                    command='python train.py arg1 arg2',
                                    source_directory=project_folder,
                                    compute_target=compute_target)

        To run a python script via ScriptRunConfig:

        .. code-block:: python

            from azureml.core import ScriptRunConfig
            from azureml.pipeline.steps import CommandStep

            train_src = ScriptRunConfig(source_directory=script_folder,
                                        command='python train.py arg1 arg2',
                                        environment=my_env)
            trainStep = CommandStep(name='train step',
                                    runconfig=train_src)

        See https://aka.ms/pl-first-pipeline
        for more details on creating pipelines in general.

    :param command: The command to run or path of the executable/script relative to ``source_directory``.
        It is required unless it is provided with runconfig. It can be specified with string arguments
        in a single string or with input/output/PipelineParameter in a list.
    :type command: builtin.list or str
    :param name: The name of the step. If unspecified, the first word in the ``command`` is used.
    :type name: str
    :param compute_target: The compute target to use. If unspecified, the target from
        the ``runconfig`` is used. This parameter may be specified as
        a compute target object or the string name of a compute target on the workspace.
        Optionally if the compute target is not available at pipeline creation time, you may specify a tuple of
        ('compute target name', 'compute target type') to avoid fetching the compute target object (AmlCompute
        type is 'AmlCompute' and RemoteCompute type is 'VirtualMachine').
    :type compute_target: azureml.core.compute.DsvmCompute
                        or azureml.core.compute.AmlCompute
                        or azureml.core.compute.RemoteCompute
                        or azureml.core.compute.HDInsightCompute
                        or str
                        or tuple
    :param runconfig: The optional configuration object which encapsulates the information necessary
        to submit a training run in an experiment.
    :type runconfig: azureml.core.ScriptRunConfig or azureml.core.runconfig.RunConfiguration
    :param runconfig_pipeline_params: Overrides of runconfig properties at runtime using key-value pairs
                    each with name of the runconfig property and PipelineParameter for that property.

        Supported values: 'NodeCount', 'MpiProcessCountPerNode', 'TensorflowWorkerCount',
        'TensorflowParameterServerCount'

    :type runconfig_pipeline_params: {str: PipelineParameter}
    :param inputs: A list of input port bindings.
    :type inputs: list[azureml.pipeline.core.graph.InputPortBinding
                    or azureml.data.data_reference.DataReference
                    or azureml.pipeline.core.PortDataReference
                    or azureml.pipeline.core.builder.PipelineData
                    or azureml.pipeline.core.pipeline_output_dataset.PipelineOutputDataset
                    or azureml.data.dataset_consumption_config.DatasetConsumptionConfig]
    :param outputs: A list of output port bindings.
    :type outputs: list[azureml.pipeline.core.builder.PipelineData
                        or azureml.data.output_dataset_config.OutputDatasetConfig
                        or azureml.pipeline.core.pipeline_output_dataset.PipelineOutputAbstractDataset
                        or azureml.pipeline.core.graph.OutputPortBinding]
    :param params: A dictionary of name-value pairs registered as environment variables with "AML_PARAMETER\_".
    :type params: dict
    :param source_directory: A folder that contains scripts, conda env, and other resources used in
        the step.
    :type source_directory: str
    :param allow_reuse: Indicates whether the step should reuse previous results when re-run with the same
        settings. Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
        parameters remain unchanged, the output from the previous run of this step is reused. When reusing
        the step, instead of submitting the job to compute, the results from the previous run are immediately
        made available to any subsequent steps. If you use Azure Machine Learning datasets as inputs, reuse is
        determined by whether the dataset's definition has changed, not by whether the underlying data has
        changed.
    :type allow_reuse: bool
    :param version: An optional version tag to denote a change in functionality for the step.
    :type version: str
    """

    def __init__(self, command=None, name=None, compute_target=None, runconfig=None,
                 runconfig_pipeline_params=None, inputs=None, outputs=None, params=None,
                 source_directory=None, allow_reuse=True, version=None):
        r"""Create an Azure ML Pipeline step that runs a command.

        .. remarks::

            An CommandStep is a basic, built-in step to run a command on the given compute target. It takes
            a command as a parameter or from other parameters like runconfig. It also takes other optional
            parameters like compute target, inputs and outputs. You should use a :class:`azureml.core.ScriptRunConfig`
            or :class:`azureml.core.RunConfiguration` to specify requirements for the CommandStep, such as
            custom docker image.

            The best practice for working with CommandStep is to use a separate folder for the executable or
            script to run any dependent files associated with the step, and specify that folder with the
            ``source_directory`` parameter. Following this best practice has two benefits. First, it helps reduce
            the size of the snapshot created for the step because only what is needed for the step is snapshotted.
            Second, the step's output from a previous run can be reused if there are no changes to the
            ``source_directory`` that would trigger a re-upload of the snapshot.

            For the system-known commands ``source_directory`` is not required but you can still provide it with
            any dependent files associated with the step.

            The following code example shows how to use a CommandStep in a machine learning training scenario.
            To list files in linux:

            .. code-block:: python

                from azureml.pipeline.steps import CommandStep

                trainStep = CommandStep(name='list step',
                                        command='ls -lrt',
                                        compute_target=compute_target)

            To run a python script:

            .. code-block:: python

                from azureml.pipeline.steps import CommandStep

                trainStep = CommandStep(name='train step',
                                        command='python train.py arg1 arg2',
                                        source_directory=project_folder,
                                        compute_target=compute_target)

            To run a python script via ScriptRunConfig:

            .. code-block:: python

                from azureml.core import ScriptRunConfig
                from azureml.pipeline.steps import CommandStep

                train_src = ScriptRunConfig(source_directory=script_folder,
                                            command='python train.py arg1 arg2',
                                            environment=my_env)
                trainStep = CommandStep(name='train step',
                                        runconfig=train_src)

            See https://aka.ms/pl-first-pipeline
            for more details on creating pipelines in general.

        :param command: The command to run or path of the executable/script relative to ``source_directory``.
            It is required unless it is provided with runconfig. It can be specified with string arguments
            in a single string or with input/output/PipelineParameter in a list.
        :type command: builtin.list or str
        :param name: The name of the step. If unspecified, the first word in the ``command`` is used.
        :type name: str
        :param compute_target: The compute target to use. If unspecified, the target from
            the ``runconfig`` is used. This parameter may be specified as
            a compute target object or the string name of a compute target on the workspace.
            Optionally if the compute target is not available at pipeline creation time, you may specify a tuple of
            ('compute target name', 'compute target type') to avoid fetching the compute target object (AmlCompute
            type is 'AmlCompute' and RemoteCompute type is 'VirtualMachine').
        :type compute_target: azureml.core.compute.DsvmCompute
                            or azureml.core.compute.AmlCompute
                            or azureml.core.compute.RemoteCompute
                            or azureml.core.compute.HDInsightCompute
                            or str
                            or tuple
        :param runconfig: The optional configuration object which encapsulates the information necessary
            to submit a training run in an experiment.
        :type runconfig: azureml.core.ScriptRunConfig or azureml.core.runconfig.RunConfiguration
        :param runconfig_pipeline_params: Overrides of runconfig properties at runtime using key-value pairs
                        each with name of the runconfig property and PipelineParameter for that property.

            Supported values: 'NodeCount', 'MpiProcessCountPerNode', 'TensorflowWorkerCount',
            'TensorflowParameterServerCount'

        :type runconfig_pipeline_params: {str: PipelineParameter}
        :param inputs: A list of input port bindings.
        :type inputs: list[azureml.pipeline.core.graph.InputPortBinding
                        or azureml.data.data_reference.DataReference
                        or azureml.pipeline.core.PortDataReference
                        or azureml.pipeline.core.builder.PipelineData
                        or azureml.pipeline.core.pipeline_output_dataset.PipelineOutputDataset
                        or azureml.data.dataset_consumption_config.DatasetConsumptionConfig]
        :param outputs: A list of output port bindings.
        :type outputs: list[azureml.pipeline.core.builder.PipelineData
                            or azureml.data.output_dataset_config.OutputDatasetConfig
                            or azureml.pipeline.core.pipeline_output_dataset.PipelineOutputAbstractDataset
                            or azureml.pipeline.core.graph.OutputPortBinding]
        :param params: A dictionary of name-value pairs registered as environment variables with "AML_PARAMETER\_".
        :type params: dict
        :param source_directory: A folder that contains scripts, conda env, and other resources used in
            the step.
        :type source_directory: str
        :param allow_reuse: Indicates whether the step should reuse previous results when re-run with the same
            settings. Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
            parameters remain unchanged, the output from the previous run of this step is reused. When reusing
            the step, instead of submitting the job to compute, the results from the previous run are immediately
            made available to any subsequent steps. If you use Azure Machine Learning datasets as inputs, reuse is
            determined by whether the dataset's definition has changed, not by whether the underlying data has
            changed.
        :type allow_reuse: bool
        :param version: An optional version tag to denote a change in functionality for the step.
        :type version: str
        """
        if runconfig:
            if isinstance(runconfig, ScriptRunConfig):
                source_directory = source_directory if source_directory else runconfig.source_directory
                if runconfig.command:
                    runconfig.run_config.command = runconfig.command
                runconfig = runconfig.run_config
            command = command if command else runconfig.command
            runconfig.command = None  # to serialize the runconfig in the later stage

        if not command:
            raise ValueError("command is required either from command directly or runconfig.")

        if not name:
            name = "CommandStep_" + (command[0] if isinstance(command, list) else command).split(' ', 1)[0]

        arguments = []
        if isinstance(command, list):
            split_command = shlex.split(command[0], posix='win' not in sys.platform)
            arguments = split_command[1:]
            arguments += command[1:]
        elif isinstance(command, str):
            split_command = shlex.split(command, posix='win' not in sys.platform)
            arguments = split_command[1:]
        command = split_command[0]

        if source_directory and not os.path.isdir(source_directory):
            raise ValueError("source_directory should be an existing directory "
                             "or None for commands already in the target system.")

        # setting default source directory to allow snapshot handling.
        if not source_directory:
            source_directory = os.getcwd()

        super(CommandStep, self).__init__(
            command=command, script_name=None, name=name, arguments=arguments, compute_target=compute_target,
            runconfig=runconfig, runconfig_pipeline_params=runconfig_pipeline_params, inputs=inputs, outputs=outputs,
            params=params, source_directory=source_directory, allow_reuse=allow_reuse, version=version)

    def create_node(self, graph, default_datastore, context):
        """
        Create a node for CommandStep and add it to the specified graph.

        This method is not intended to be used directly. When a pipeline is instantiated with this step,
        Azure ML automatically passes the parameters required through this method so that step can be added to a
        pipeline graph that represents the workflow.

        :param graph: The graph object to add the node to.
        :type graph: azureml.pipeline.core.graph.Graph
        :param default_datastore: The default datastore.
        :type default_datastore:  azureml.data.azure_storage_datastore.AbstractAzureStorageDatastore
                                or azureml.data.azure_data_lake_datastore.AzureDataLakeDatastore
        :param context: The graph context.
        :type context: _GraphContext

        :return: The created node.
        :rtype: azureml.pipeline.core.graph.Node
        """
        return super(CommandStep, self).create_node(
            graph=graph, default_datastore=default_datastore, context=context)
