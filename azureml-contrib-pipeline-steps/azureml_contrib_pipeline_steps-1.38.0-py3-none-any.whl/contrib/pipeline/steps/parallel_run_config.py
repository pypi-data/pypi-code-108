# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality for configuring a :class:`azureml.contrib.pipeline.steps.ParallelRunStep`."""
import os
import re
import logging

from azureml.core import Environment
from azureml.core.compute import AmlCompute
from azureml.pipeline.core.graph import PipelineParameter
import azureml._vendor.ruamel.yaml as ruamelyaml

module_logger = logging.getLogger(__name__)


class ParallelRunConfig(object):
    """
    Defines configuration for a :class:`azureml.contrib.pipeline.steps.ParallelRunStep` object.

    .. note::

        This package, azureml-contrib-pipeline-steps, has been deprecated and moved to azureml-pipeline-steps.
        Please use the :class:`azureml.pipeline.steps.ParallelRunConfig` class from new package.

    For an example of using ParallelRunStep, see the notebook https://aka.ms/batch-inference-notebooks.

    For troubleshooting guide, see https://aka.ms/prstsg. You can find more references there.

    .. remarks::

        The ParallelRunConfig class is used to specify configuration for the
        :class:`azureml.contrib.pipeline.steps.ParallelRunStep` class. The ParallelRunConfig and ParallelRunStep
        classes together can be used for any kind of processing job that involves large amounts of data and
        is not time-sensitive, such as training or scoring. The ParallelRunStep works by breaking up a large job
        into batches that are processed in parallel. The batch size and degree of parallel processing can be
        controlled with the :class:`azureml.contrib.pipeline.steps.ParallelRunConfig` class. ParallelRunStep
        can work with either :class:`azureml.data.TabularDataset` or :class:`azureml.data.FileDataset` as input.

        To work with the ParallelRunStep class the following pattern is typical:

        * Create a :class:`azureml.contrib.pipeline.steps.ParallelRunConfig` object to specify how batch
          processing is performed, with parameters to control batch size, number of nodes per compute target,
          and a reference to your custom Python script.

        * Create a ParallelRunStep object that uses the ParallelRunConfig object, defines inputs and
          outputs for the step, and list of models to use.

        * Use the configured ParallelRunStep object in a :class:`azureml.pipeline.core.Pipeline`
          just as you would with pipeline step types defined in the :mod:`azureml.pipeline.steps` package.

        Examples of working with ParallelRunStep and ParallelRunConfig classes for batch inference are discussed in
        the following articles:

        * `Tutorial: Build an Azure Machine Learning pipeline for batch
          scoring <https://docs.microsoft.com/azure/machine-learning/tutorial-pipeline-batch-scoring-classification>`_.
          This article shows how to use these two classes for asynchronous batch scoring in a pipeline and enable a
          REST endpoint to run the pipeline.

        * `Run batch inference on large amounts of data by using Azure Machine
          Learning <https://docs.microsoft.com/azure/machine-learning/how-to-use-parallel-run-step>`_. This article
          shows how to process large amounts of data asynchronously and in parallel with a custom inference script
          and a pre-trained image classification model based on the MNIST dataset.

        .. code:: python

            from azureml.contrib.pipeline.steps import ParallelRunStep, ParallelRunConfig

            parallel_run_config = ParallelRunConfig(
                source_directory=scripts_folder,
                entry_script=script_file,
                mini_batch_size="5",
                error_threshold=10,
                output_action="append_row",
                environment=batch_env,
                compute_target=compute_target,
                node_count=2)

            parallelrun_step = ParallelRunStep(
                name="predict-digits-mnist",
                parallel_run_config=parallel_run_config,
                inputs=[ named_mnist_ds ],
                output=output_dir,
                models=[ model ],
                arguments=[ ],
                allow_reuse=True
            )

        For more information about this example, see the notebook https://aka.ms/batch-inference-notebooks.

    :param environment: The environment definition that configures the Python environment.
        It can be configured to use an existing Python environment or to set up a temp environment
        for the experiment. The definition is also responsible for setting the required application
        dependencies.
    :type environment: azureml.core.Environment
    :param entry_script: User script which will be run in parallel on multiple nodes. This is
        specified as local file path. If ``source_directory`` is specified, then ``entry_script`` is
        a relative path inside. Otherwise, it can be any path accessible on the machine.
    :type entry_script: str
    :param error_threshold: The number of record failures for :class:`azureml.data.TabularDataset`
        and file failures for :class:`azureml.data.FileDataset` that should be ignored during
        processing. If the error count goes above this value, then the job will be aborted. Error
        threshold is for the entire input and not for individual mini-batches sent to run() method.
        The range is [-1, int.max]. -1 indicates ignore all failures during processing.
    :type error_threshold: int
    :param output_action: How the output is to be organized. Currently supported values
        are 'append_row' and 'summary_only'.
        1. 'append_row' – All values output by run() method invocations will be aggregated into
        one unique file named parallel_run_step.txt that is created in the output location.
        2. 'summary_only' – User script is expected to store the output by itself. An output row
        is still expected for each successful input item processed. The system uses this output
        only for error threshold calculation (ignoring the actual value of the row).
    :type output_action: str
    :param compute_target: Compute target to use for ParallelRunStep. This parameter may be specified as
        a compute target object or the string name of a compute target in the workspace.
    :type compute_target: azureml.core.compute.AmlCompute or str
    :param node_count: Number of nodes in the compute target used for running the ParallelRunStep.
    :type node_count: int
    :param process_count_per_node: Number of processes executed on each node.
        (optional, default value is number of cores on node.)
    :type process_count_per_node: int
    :param mini_batch_size: For FileDataset input, this field is the number of files user script can process
        in one run() call. For TabularDataset input, this field is the approximate size of data the user script
        can process in one run() call. Example values are 1024, 1024KB, 10MB, and 1GB.
        (optional, default value is 10 files for FileDataset and 1MB for TabularDataset.)
    :type mini_batch_size: str
    :param source_directory: Paths to folders that contains the ``entry_script`` and supporting files used
        to execute on compute target.
    :type source_directory: str
    :param description: A description to give the batch service used for display purposes.
    :type description: str
    :param logging_level: A string of the logging level name, which is defined in 'logging'.
        Possible values are 'WARNING', 'INFO', and 'DEBUG'. (optional, default value is 'INFO'.)
    :type logging_level: str
    :param run_invocation_timeout: Timeout in seconds for each invocation of the run() method.
        (optional, default value is 60.)
    :type run_invocation_timeout: int
    :param input_format: Deprecated.
    :type input_format: str
    """

    def __init__(self, environment, entry_script, error_threshold, output_action, compute_target,
                 node_count, process_count_per_node=None, mini_batch_size=None,
                 source_directory=None, description=None, logging_level=None,
                 run_invocation_timeout=None, input_format=None, append_row_file_name=None):
        """Initialize the config object.

        :param environment: The environment definition that configures the Python environment.
            It can be configured to use an existing Python environment or to set up a temp environment
            for the experiment. The definition is also responsible for setting the required application
            dependencies.
        :type environment: azureml.core.Environment
        :param entry_script: User script which will be run in parallel on multiple nodes. This is
            specified as local file path. If ``source_directory`` is specified, then ``entry_script`` is
            a relative path inside. Otherwise, it can be any path accessible on the machine.
        :type entry_script: str
        :param error_threshold: The number of record failures for :class:`azureml.data.TabularDataset`
            and file failures for :class:`azureml.data.FileDataset` that should be ignored during
            processing. If the error count goes above this value, then the job will be aborted. Error
            threshold is for the entire input and not for individual mini-batches sent to run() method.
            The range is [-1, int.max]. -1 indicates ignore all failures during processing.
        :type error_threshold: int
        :param output_action: How the output is to be organized. Currently supported values
            are 'append_row' and 'summary_only'.
            1. 'append_row' – All values output by run() method invocations will be aggregated into
            one unique file named parallel_run_step.txt that is created in the output location.
            2. 'summary_only' – User script is expected to store the output by itself. An output row
            is still expected for each successful input item processed. The system uses this output
            only for error threshold calculation (ignoring the actual value of the row).
        :type output_action: str
        :param compute_target: Compute target to use for ParallelRunStep. This parameter may be specified as
            a compute target object or the string name of a compute target on the workspace.
        :type compute_target: azureml.core.compute.AmlCompute or str
        :param node_count: Number of nodes in the compute target used for running the ParallelRunStep.
        :type node_count: int
        :param process_count_per_node: Number of processes executed on each node.
            (optional, default value is number of cores on node.)
        :type process_count_per_node: int
        :param mini_batch_size: For FileDataset input, this field is the number of files user script can process
            in one run() call. For TabularDataset input, this field is the approximate size of data the user script
            can process in one run() call. Example values are 1024, 1024KB, 10MB, and 1GB.
            (optional, default value is 10 files for FileDataset and 1MB for TabularDataset.)
        :type mini_batch_size: str
        :param source_directory: Paths to folders that contains the ``entry_script`` and supporting files used
            to execute on compute target.
        :type source_directory: str
        :param description: A description to give the batch service used for display purposes.
        :type description: str
        :param logging_level: A string of the logging level name, which is defined in 'logging'.
            Possible values are 'WARNING', 'INFO', and 'DEBUG'. (optional, default value is 'INFO'.)
        :type logging_level: str
        :param run_invocation_timeout: Timeout in seconds for each invocation of the run() method.
            (optional, default value is 60.)
        :type run_invocation_timeout: int
        :param input_format: Deprecated.
        :type input_format: str
        """
        self.input_format = input_format
        self.mini_batch_size = mini_batch_size
        self.error_threshold = error_threshold
        self.output_action = output_action
        self.logging_level = "INFO" if logging_level is None else logging_level
        self.compute_target = compute_target
        self.node_count = node_count
        self.process_count_per_node = process_count_per_node
        self.entry_script = entry_script if entry_script is None else entry_script.strip()
        self.source_directory = source_directory if source_directory is None else source_directory.strip()
        self.description = description
        self.environment = environment
        self.run_invocation_timeout = 60 if run_invocation_timeout is None else run_invocation_timeout
        self.append_row_file_name = append_row_file_name

        if self.environment is None:
            raise ValueError('Parameter environment is required. It should be instance of azureml.core.Environment.')

        if not isinstance(self.environment, Environment):
            raise ValueError(
                "Parameter environment must be an instance of azureml.core.Environment."
                " The actual value is {0}.".format(self.environment)
            )

        if self.output_action.lower() not in ['summary_only', 'append_row']:
            raise ValueError('Parameter output_action must be summary_only or append_row')

        if not isinstance(self.error_threshold, int) or self.error_threshold < -1:
            raise ValueError('Parameter error_threshold must be an int value greater than or equal to -1')

        if self.mini_batch_size is not None:
            if not isinstance(self.mini_batch_size, PipelineParameter):
                self._mini_batch_size_to_int()

        if self.process_count_per_node is not None:
            if not isinstance(self.process_count_per_node, PipelineParameter) and self.process_count_per_node < 1:
                raise ValueError("Parameter process_count_per_node must be a greater than 0")

        if not isinstance(self.compute_target, str) and \
                self.compute_target.type.lower() != AmlCompute._compute_type.lower():
            raise ValueError(
                "Compute compute_target {0} is not supported in ParallelRunStep. "
                "AmlCompute is the only supported compute_target."
                .format(self.compute_target))

        if not isinstance(self.compute_target, str) and not isinstance(self.node_count, PipelineParameter):
            if (self.node_count > self.compute_target.scale_settings.maximum_node_count or self.node_count <= 0):
                raise ValueError(
                    "Parameter node_count must be between 1 and max_nodes {}"
                    .format(self.compute_target.scale_settings.maximum_node_count))

        if not isinstance(self.run_invocation_timeout, PipelineParameter):
            if self.run_invocation_timeout <= 0:
                raise ValueError('Parameter run_invocation_timeout must be an integer greater than 0')

        if self.output_action.lower() == 'append_row' and self.append_row_file_name is not None:
            pattern = re.compile(r'[~"#%&*:<>?\/\\{|}]+')
            if pattern.search(self.append_row_file_name):
                raise ValueError('Parameter append_row_file_name must be a valid UNIX file name')

    def _mini_batch_size_to_int(self):
        """Convert str to int."""
        pattern = re.compile(r"^\d+([kKmMgG][bB])*$")
        if not pattern.match(self.mini_batch_size):
            raise ValueError(r"Parameter mini_batch_size must follow regex rule ^\d+([kKmMgG][bB])*$")

        try:
            self.mini_batch_size = int(self.mini_batch_size)
        except ValueError:
            unit = self.mini_batch_size[-2:].lower()
            if unit == 'kb':
                self.mini_batch_size = int(self.mini_batch_size[0:-2]) * 1024
            elif unit == 'mb':
                self.mini_batch_size = int(self.mini_batch_size[0:-2]) * 1024 * 1024
            elif unit == 'gb':
                self.mini_batch_size = int(self.mini_batch_size[0:-2]) * 1024 * 1024 * 1024

    def save_to_yaml(self, path):
        """Export parallel run configuration data to a YAML file.

        :param path: The path to save the file to.
        :type path: str
        """
        env_output_dir = os.path.join(os.path.dirname(os.path.abspath(path)), "parallel_run_env")
        self.environment.save_to_directory(env_output_dir)

        mini_batch_size = self.mini_batch_size
        if isinstance(self.mini_batch_size, PipelineParameter):
            mini_batch_size = self.mini_batch_size.default_value

        process_count_per_node = self.process_count_per_node
        if isinstance(self.process_count_per_node, PipelineParameter):
            process_count_per_node = self.process_count_per_node.default_value

        run_invocation_timeout = self.run_invocation_timeout
        if isinstance(self.run_invocation_timeout, PipelineParameter):
            run_invocation_timeout = self.run_invocation_timeout.default_value

        logging_level = self.logging_level
        if isinstance(self.logging_level, PipelineParameter):
            logging_level = self.logging_level.default_value

        node_count = self.node_count
        if isinstance(self.node_count, PipelineParameter):
            node_count = self.node_count.default_value

        config = {"input_format": self.input_format,
                  "mini_batch_size": mini_batch_size,
                  "error_threshold": self.error_threshold,
                  "output_action": self.output_action,
                  "logging_level": logging_level,
                  "compute_target_name": self.compute_target if isinstance(self.compute_target, str) else
                  self.compute_target.name,
                  "node_count": node_count,
                  "process_count_per_node": process_count_per_node,
                  "entry_script": self.entry_script,
                  "source_directory": self.source_directory,
                  "description": self.description,
                  "run_invocation_timeout": run_invocation_timeout,
                  "append_row_file_name": self.append_row_file_name,
                  "environment_name": self.environment.name,
                  "environment_dir_path": env_output_dir}
        with open(path, 'w') as f:
            ruamelyaml.round_trip_dump({"parallel_run_config": config}, f)

    @staticmethod
    def load_yaml(workspace, path):
        """Load parallel run configuration data from a YAML file.

        :param workspace: The workspace to read the configuration data from.
        :type workspace: azureml.core.Workspace
        :param path: The path to load the configuration from.
        :type path: str
        """
        with open(path, 'r') as f:
            config = ruamelyaml.round_trip_load(f)["parallel_run_config"]
            compute_target = ParallelRunConfig._get_target(workspace, config["compute_target_name"])

            if "environment_dir_path" in config.keys() and config["environment_dir_path"] is not None:
                env = Environment.load_from_directory(config["environment_dir_path"])
            else:
                env = Environment.get(workspace, name=config["environment_name"])

            if "mini_batch_size" in config.keys() and config["mini_batch_size"] is not None:
                mini_batch_size = "{0}".format(config["mini_batch_size"])
            else:
                mini_batch_size = None

            return ParallelRunConfig(environment=env,
                                     entry_script=config.get("entry_script"),
                                     error_threshold=config.get("error_threshold"),
                                     output_action=config.get("output_action"),
                                     compute_target=compute_target,
                                     node_count=config.get("node_count"),
                                     process_count_per_node=config.get("process_count_per_node"),
                                     mini_batch_size=mini_batch_size,
                                     source_directory=config.get("source_directory"),
                                     description=config.get("description"),
                                     logging_level=config.get("logging_level"),
                                     run_invocation_timeout=config.get("run_invocation_timeout"),
                                     input_format=config.get("input_format"),
                                     append_row_file_name=config.get("append_row_file_name"))

    @staticmethod
    def _get_target(ws, target_name):
        return AmlCompute(ws, target_name)
