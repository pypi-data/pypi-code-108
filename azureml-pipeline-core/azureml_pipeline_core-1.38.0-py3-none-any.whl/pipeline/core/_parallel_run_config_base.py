# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality for configuring a :class:`azureml.pipeline.steps.ParallelRunStep`."""
import json
import re
import logging
from json.decoder import JSONDecodeError

from azureml.core import Environment
from azureml.core.compute import AmlCompute
from azureml.core.environment import EnvironmentReference
from azureml.pipeline.core.graph import PipelineParameter
import azureml._vendor.ruamel.yaml as ruamelyaml

module_logger = logging.getLogger(__name__)


class _ParallelRunConfigBase(object):
    """
    Defines configuration for a :class:`azureml.pipeline.core._ParallelRunStepBase` object.

    For an example of using ParallelRunStep, see the notebook https://aka.ms/batch-inference-notebooks.

    .. remarks::

        The _ParallelRunConfigBase class is used to provide configuration for the
        :class:`azureml.pipeline.core._ParallelRunStepBase` class. _ParallelRunConfigBase and _ParallelRunStepBase
        can be used together for processing large amounts of data in parallel. Common use cases are training an ML
        model or running offline inference to generate predictions on a batch of observations. ParallelRunStep works
        by breaking up your data into batches that are processed in parallel. The batch size, node count,
        and other tunable parameters to speed up your parallel processing can be controlled with the
        :class:`azureml.pipeline.core._ParallelRunConfigBase` class. ParallelRunStep can work with either
        :class:`azureml.data.TabularDataset` or :class:`azureml.data.FileDataset` as input.

        To use ParallelRunStep and ParallelRunConfig:

        * Create a :class:`azureml.pipeline.core._ParallelRunConfigBase` object to specify how batch
          processing is performed, with parameters to control batch size, number of nodes per compute target,
          and a reference to your custom Python script.

        * Create a ParallelRunStep object that uses the _ParallelRunConfigBase object, defines inputs and
          outputs for the step.

        * Use the configured ParallelRunStep object in a :class:`azureml.pipeline.core.Pipeline`
          just as you would with pipeline step types defined in the :mod:`azureml.pipeline.steps` package.

        Examples of working with ParallelRunStep and _ParallelRunConfigBase classes for batch inference are
        discussed in the following articles:

        * `Tutorial: Build an Azure Machine Learning pipeline for batch
          scoring <https://docs.microsoft.com/azure/machine-learning/tutorial-pipeline-batch-scoring-classification>`_.
          This article shows how to use these two classes for asynchronous batch scoring in a pipeline and enable a
          REST endpoint to run the pipeline.

        * `Run batch inference on large amounts of data by using Azure Machine
          Learning <https://docs.microsoft.com/azure/machine-learning/how-to-use-parallel-run-step>`_. This article
          shows how to process large amounts of data asynchronously and in parallel with a custom inference script
          and a pre-trained image classification model bases on the MNIST dataset.

        .. code:: python

            from azureml.pipeline.steps import ParallelRunStep, ParallelRunConfig

            parallel_run_config = ParallelRunConfig(
                source_directory=scripts_folder,
                entry_script=script_file,
                mini_batch_size="5",        # or partition_keys=["key1", "key2"], which is another way to partition the
                                            # input to mini-batches, refer to the parameter description for details
                error_threshold=10,         # Optional, allowed failed count on mini batch items
                allowed_failed_count=15,    # Optional, allowed failed count on mini batches
                allowed_failed_percent=10,  # Optional, allowed failed percent on mini batches
                run_max_try=3,
                output_action="append_row",
                environment=batch_env,
                compute_target=compute_target,
                node_count=2)

            parallelrun_step = ParallelRunStep(
                name="predict-digits-mnist",
                parallel_run_config=parallel_run_config,
                inputs=[ named_mnist_ds ],
                output=output_dir,
                arguments=[ "--extra_arg", "example_value" ],
                allow_reuse=True
            )

        For more information about this example, see the notebook https://aka.ms/batch-inference-notebooks.

    :param environment: The environment definition that configures the Python environment.
        It can be configured to use an existing Python environment or to set up a temp environment
        for the experiment. The environment definition is responsible for defining the required application
        dependencies, such as conda or pip packages.
    :type environment: azureml.core.Environment
    :param entry_script: User script which will be run in parallel on multiple nodes. This is
        specified as a local file path. If ``source_directory`` is specified, then ``entry_script`` is
        a relative path inside the directory. Otherwise, it can be any path accessible on the machine.
        The entry_script should contain two functions:
        ``init()``: this function should be used for any costly or common preparation for subsequent inferences,
        e.g., deserializing and loading the model into a global object.
        ``run(mini_batch)``: The method to be parallelized. Each invocation will have one mini-batch.
        'mini_batch': Batch inference will invoke run method and pass either a list or a Pandas DataFrame as an
        argument to the method. Each entry in min_batch will be a filepath if input is a FileDataset,
        a Pandas DataFrame if input is a TabularDataset.
        run() method should return a Pandas DataFrame or an array.
        For append_row output_action, these returned elements are appended into the common output file.
        For summary_only, the contents of the elements are ignored. For all output actions,
        each returned output element indicates one successful inference of input element in the input mini-batch.
        Each parallel worker process will call `init` once and then loop over `run` function until all mini-batches
        are processed.
    :type entry_script: str
    :param error_threshold: The number of record failures for :class:`azureml.data.TabularDataset`
        and file failures for :class:`azureml.data.FileDataset` that should be ignored during
        processing. If the error count goes above this value, then the job will be aborted. Error
        threshold is for the entire input rather than the individual mini-batch sent to run() method.
        The range is [-1, int.max]. -1 indicates ignore all failures during processing.
        The argument --error_threshold, --allowed_failed_count and --allowed_failed_percent can work together.
        If more than one specified, the job will be aborted if it exceeds any of them.
    :type error_threshold: int
    :param output_action: How the output should be organized. Current supported values
        are 'append_row' and 'summary_only'.
        1. 'append_row' – All values output by run() method invocations will be aggregated into
        one unique file which is created in the output location.
        2. 'summary_only' – User script is expected to store the output itself. An output row
        is still expected for each successful input item processed. The system uses this output
        only for error threshold calculation (ignoring the actual value of the row).
    :type output_action: str
    :param compute_target: Compute target to use for ParallelRunStep execution. This parameter may be specified as
        a compute target object or the name of a compute target in the workspace.
    :type compute_target: azureml.core.compute.AmlCompute or str
    :param node_count: Number of nodes in the compute target used for running the ParallelRunStep.
        This value could be set through PipelineParameter.
    :type node_count: int
    :param process_count_per_node: Number of processes executed on each node.
        (optional, default value is 1.) This value could be set through PipelineParameter.
    :type process_count_per_node: int
    :param mini_batch_size: For FileDataset input, this field is the number of files a user script can process
        in one run() call. For TabularDataset input, this field is the approximate size of data the user script
        can process in one run() call. Example values are 1024, 1024KB, 10MB, and 1GB.
        (optional, default value is 10 files for FileDataset and 1MB for TabularDataset.) This value could be set
        through PipelineParameter.
    :type mini_batch_size: Union[str, int]
    :param source_directory: Path to folder that contains the ``entry_script`` and supporting files used
        to execute on compute target.
    :type source_directory: str
    :param description: A description to give the batch service used for display purposes.
    :type description: str
    :param logging_level: A string of the logging level name, which is defined in 'logging'.
        Possible values are 'WARNING', 'INFO', and 'DEBUG'. (optional, default value is 'INFO'.)
        This value could be set through PipelineParameter.
    :type logging_level: str
    :param run_invocation_timeout: Timeout in seconds for each invocation of the run() method.
        (optional, default value is 60.) This value could be set through PipelineParameter.
    :type run_invocation_timeout: int
    :param run_max_try: The number of maximum tries for a failed or timeout mini batch.
        The range is [1, int.max]. The default value is 3. This value could be set through PipelineParameter.
        A mini batch with dequeue count greater than this won't be processed again and will be deleted directly.
    :type run_max_try: int
    :param append_row_file_name: The name of the output file if the ``output_action`` is 'append_row'.
            (optional, default value is 'parallel_run_step.txt')
    :type append_row_file_name: str
    :param allowed_failed_count: The number of failed mini batches that should be ignored during
        processing. If the failed count goes above this value, the job will be aborted. This
        threshold is for the entire input rather than the individual mini-batch sent to run() method.
        The range is [-1, int.max]. -1 indicates ignore all failures during processing.
        A mini batch may fail on the first time it's processed and then succeed on the second try.
        Checking between the first and second time will count it as failed.
        Checking after the second time won't count it as failed.
        The argument --error_threshold, --allowed_failed_count and --allowed_failed_percent can work together.
        If more than one specified, the job will be aborted if it exceeds any of them.
    :type allowed_failed_count: int
    :param allowed_failed_percent: The percent of failed mini batches that should be ignored during
        processing. If the failed percent goes above this value, then the job will be aborted. This
        threshold is for the entire input rather than the individual mini-batch sent to run() method.
        The range is [0, 100]. 100 or 100.0 indicates ignore all failures during processing.
        The check starts after all mini batches have been scheduled.
        The argument --error_threshold, --allowed_failed_count and --allowed_failed_percent can work together.
        If more than one specified, the job will be aborted if it exceeds any of them.
    :type allowed_failed_percent: float
    :param partition_keys: The keys used to partition dataset into mini-batches. If specified, the data with
        the same key will be partitioned into the same mini-batch. If both partition_keys and mini_batch_size
        are specified, error would be raised. It should be a list of str elements each being a key used to
        partition the input dataset. However, if promoted to PipelineParameter, the default values should be
        the json dump str of the list because list type is not supported in PipelineParameter for now.
        The input(s) must be partitioned dataset(s), and the partition_keys must be a subset of the keys of
        every input dataset for this to work.
    :type partition_keys: List[str]
    :param environment_variables: A dictionary of environment variables names and values.
        These environment variables are set on the process where user script is being executed.
    :type environment_variables: Dict[str, str]
    """

    def __init__(
        self,
        environment,
        entry_script,
        error_threshold,
        output_action,
        compute_target,
        node_count,
        process_count_per_node=None,
        mini_batch_size=None,
        source_directory=None,
        description=None,
        logging_level=None,
        run_invocation_timeout=None,
        run_max_try=None,
        append_row_file_name=None,
        allowed_failed_count=None,
        allowed_failed_percent=None,
        partition_keys=None,
        environment_variables=None,
    ):
        """
        Initialize the config object.

        :param environment: The environment definition that configures the Python environment.
            It can be configured to use an existing Python environment or to set up a temp environment
            for the experiment. The environment definition is responsible for defining the required application
            dependencies, such as conda or pip packages.
        :type environment: azureml.core.Environment
        :param entry_script: User script which will be run in parallel on multiple nodes. This is
            specified as a local file path. If ``source_directory`` is specified, then ``entry_script`` is
            a relative path inside the directory. Otherwise, it can be any path accessible on the machine.
        :type entry_script: str
        :param error_threshold: The number of record failures for :class:`azureml.data.TabularDataset`
            and file failures for :class:`azureml.data.FileDataset` that should be ignored during
            processing. If the error count goes above this value, then the job will be aborted. Error
            threshold is for the entire input and not for individual mini-batches sent to run() method.
            The range is [-1, int.max]. -1 indicates ignore all failures during processing.
        :type error_threshold: int
        :param output_action: How the output should be organized. Current supported values
            are 'append_row' and 'summary_only'.
            1. 'append_row' – All values output by run() method invocations will be aggregated into
            one unique file which is created in the output location.
            2. 'summary_only' – User script is expected to store the output itself. An output row
            is still expected for each successful input item processed. The system uses this output
            only for error threshold calculation (ignoring the actual value of the row).
        :type output_action: str
        :param compute_target: Compute target to use for ParallelRunStep execution. This parameter may be specified as
            a compute target object or the name of a compute target in the workspace.
        :type compute_target: azureml.core.compute.AmlCompute or str
        :param node_count: Number of nodes in the compute target used for running the ParallelRunStep.
            This value could be set through PipelineParameter.
        :type node_count: int
        :param process_count_per_node: Number of processes executed on each node.
            (optional, default value is 1.) This value could be set through PipelineParameter.
        :type process_count_per_node: int
        :param mini_batch_size: For FileDataset input, this field is the number of files a user script can process
            in one run() call. For TabularDataset input, this field is the approximate size of data the user script
            can process in one run() call. Example values are 1024, 1024KB, 10MB, and 1GB.
            This value could be set through PipelineParameter.
            (optional, default value is 10 files for FileDataset and 1MB for TabularDataset.)
        :type mini_batch_size: Union[str, int]
        :param source_directory: Path to folder that contains the ``entry_script`` and supporting files used
            to execute on compute target.
        :type source_directory: str
        :param description: A description to give the batch service used for display purposes.
        :type description: str
        :param logging_level: A string of the logging level name, which is defined in 'logging'.
            Possible values are 'WARNING', 'INFO', and 'DEBUG'. (optional, default value is 'INFO'.)
            This value could be set through PipelineParameter.
        :type logging_level: str
        :param run_invocation_timeout: Timeout in seconds for each invocation of the run() method.
            (optional, default value is 60.) This value could be set through PipelineParameter.
        :type run_invocation_timeout: int
        :param run_max_try: The number of maximum tries for a failed or timeout mini batch.
            The range is [1, int.max]. The default value is 3. This value could be set through PipelineParameter.
            A mini batch with dequeue count greater than this won't be processed again and will be deleted directly.
        :type run_max_try: int
        :param append_row_file_name: The name of the output file if the ``output_action`` is 'append_row'.
                (optional, default value is 'parallel_run_step.txt')
        :type append_row_file_name: str
        :param allowed_failed_count: The number of failed mini batches that should be ignored during
            processing. If the failed count goes above this value, the job will be aborted. This
            threshold is for the entire input rather than the individual mini-batch sent to run() method.
            The range is [-1, int.max]. -1 indicates ignore all failures during processing.
            A mini batch may fail on the first time it's processed and then succeed on the second try.
            Checking between the first and second time will count it as failed.
            Checking after the second time won't count it as failed.
            The argument --error_threshold, --allowed_failed_count and --allowed_failed_percent can work together.
            If more than one specified, the job will be aborted if it exceeds any of them.
        :type allowed_failed_count: int
        :param allowed_failed_percent: The percent of failed mini batches that should be ignored during
            processing. If the failed percent goes above this value, then the job will be aborted. This
            threshold is for the entire input rather than the individual mini-batch sent to run() method.
            The range is [0, 100]. 100 or 100.0 indicates ignore all failures during processing.
            The check starts after all mini batches have been scheduled.
            The argument --error_threshold, --allowed_failed_count and --allowed_failed_percent can work together.
            If more than one specified, the job will be aborted if it exceeds any of them.
        :type allowed_failed_percent: float
        :param partition_keys: The keys used to partition dataset into mini-batches. If specified, the data with
            the same key will be partitioned into the same mini-batch. If both partition_keys and mini_batch_size
            are specified, error would be raised. It should be a list of str elements each being a key used to
            partition the input dataset. However, if promoted to PipelineParameter, the default values should be
            the json dump str of the list because list type is not supported in PipelineParameter for now.
            The input(s) must be partitioned dataset(s), and the partition_keys must be a subset of the keys of
            every input dataset for this to work.
        :type partition_keys: List[str]
        :param environment_variables: A dictionary of environment variables names and values.
            These environment variables are set on the process where user script is being executed.
        :type environment_variables: Dict[str, str]
        """
        self.mini_batch_size = mini_batch_size
        self.error_threshold = error_threshold
        self.allowed_failed_count = allowed_failed_count
        self.allowed_failed_percent = allowed_failed_percent
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
        self.run_max_try = 3 if run_max_try is None else run_max_try
        self.append_row_file_name = append_row_file_name
        self.partition_keys = partition_keys
        self._environment_variables = {} if environment_variables is None else environment_variables

        if self.environment is None:
            raise ValueError("Parameter environment is required. It should be instance of azureml.core.Environment.")

        if not isinstance(self.environment, Environment):
            raise ValueError(
                "Parameter environment must be an instance of azureml.core.Environment."
                " The actual value is {0}.".format(self.environment)
            )

        if output_action.lower() not in ["summary_only", "append_row"]:
            raise ValueError("Parameter output_action must be summary_only or append_row.")

        if not isinstance(error_threshold, int) or error_threshold < -1:
            raise ValueError(
                "error_threshold '{}' is not an int value greater than or equal to -1.".format(error_threshold)
            )

        if allowed_failed_count is not None:
            if not isinstance(allowed_failed_count, int) or allowed_failed_count < -1:
                raise ValueError(
                    "allowed_failed_count '{}' is not an int value greater than or equal to -1.".format(
                        allowed_failed_count
                    )
                )

        if allowed_failed_percent is not None:
            if not isinstance(allowed_failed_percent, (int, float)):
                raise ValueError("allowed_failed_percent '{}' is not an int or float.".format(allowed_failed_percent))

            if allowed_failed_percent < 0 or allowed_failed_percent > 100:
                raise ValueError(
                    "allowed_failed_percent '{}' is not between 0 and 100.".format(allowed_failed_percent)
                )

        if mini_batch_size is not None and partition_keys is not None:
            raise ValueError(
                "Parameters mini_batch_size and partition_keys are mutually exclusive, "
                "because they specify different ways to partition the input datasets into mini-batches."
            )

        if mini_batch_size is not None:
            if not isinstance(mini_batch_size, PipelineParameter):
                if not isinstance(mini_batch_size, (int, str)):
                    raise ValueError("Parameter mini_batch_size must be of type int or str.")
                if isinstance(self.mini_batch_size, str):
                    self._mini_batch_size_to_int()

        if self.partition_keys is not None:
            if not isinstance(self.partition_keys, PipelineParameter):
                if not isinstance(self.partition_keys, list):
                    raise ValueError("Parameter partition_keys must be of type list.")
                for key in self.partition_keys:
                    if not isinstance(key, str):
                        raise ValueError("Element {0} in partition_keys is not a str.".format(key))
            else:
                try:
                    try_loading_result = json.loads(self.partition_keys.default_value)
                except JSONDecodeError:
                    raise ValueError(
                        "default_value of PipelineParameter partition_keys must be json dump result of a list of str, "
                        "try json.loads the value to validate."
                    )

                if not isinstance(try_loading_result, list):
                    raise ValueError(
                        "default_value of PipelineParameter partition_keys must be json dump result of a list of str."
                    )

                for key in try_loading_result:
                    if not isinstance(key, str):
                        raise ValueError(
                            "Element {0} in default_value of PipelineParameter partition_keys is not a str.".format(
                                key
                            )
                        )

        if self.process_count_per_node is not None:
            if not isinstance(self.process_count_per_node, PipelineParameter) and self.process_count_per_node < 1:
                raise ValueError("Parameter process_count_per_node must be an integer greater than 0.")

        if isinstance(self.compute_target, AmlCompute) and not isinstance(self.node_count, PipelineParameter):
            if self.node_count > self.compute_target.scale_settings.maximum_node_count or self.node_count <= 0:
                raise ValueError(
                    "node_count '{}' is not between 1 and max_nodes {}.".format(
                        self.node_count, self.compute_target.scale_settings.maximum_node_count
                    )
                )

        if not isinstance(self.run_invocation_timeout, PipelineParameter):
            if self.run_invocation_timeout <= 0:
                raise ValueError("Parameter run_invocation_timeout must be an integer greater than 0.")

        if not isinstance(self.run_max_try, PipelineParameter):
            if self.run_max_try <= 0:
                raise ValueError("Parameter run_max_try must be an integer greater than 0.")

        if self.output_action.lower() == "append_row" and self.append_row_file_name is not None:
            pattern = re.compile(r'[~"#%&*:<>?\/\\{|}]+')
            if pattern.search(self.append_row_file_name):
                raise ValueError("Parameter append_row_file_name must be a valid UNIX file name.")

    @property
    def environment_variables(self):
        return self._environment_variables

    @environment_variables.setter
    def environment_variables(self, value):
        self._environment_variables = value

    def _mini_batch_size_to_int(self):
        """Convert str to int."""
        pattern = re.compile(r"^\d+([kKmMgG][bB])*$")
        if not pattern.match(self.mini_batch_size):
            raise ValueError(r"Parameter mini_batch_size must follow regex rule ^\d+([kKmMgG][bB])*$.")

        try:
            self.mini_batch_size = int(self.mini_batch_size)
        except ValueError:
            unit = self.mini_batch_size[-2:].lower()
            if unit == "kb":
                self.mini_batch_size = int(self.mini_batch_size[0:-2]) * 1024
            elif unit == "mb":
                self.mini_batch_size = int(self.mini_batch_size[0:-2]) * 1024 * 1024
            elif unit == "gb":
                self.mini_batch_size = int(self.mini_batch_size[0:-2]) * 1024 * 1024 * 1024

    def save_to_yaml(self, path):
        """Export parallel run configuration data to a YAML file.

        :param path: The path to save the file to.
        :type path: str
        """
        mini_batch_size = self.mini_batch_size
        if isinstance(self.mini_batch_size, PipelineParameter):
            mini_batch_size = self.mini_batch_size.default_value

        partition_keys = self.partition_keys
        if isinstance(self.partition_keys, PipelineParameter):
            partition_keys = json.loads(self.partition_keys.default_value)

        process_count_per_node = self.process_count_per_node
        if isinstance(self.process_count_per_node, PipelineParameter):
            process_count_per_node = self.process_count_per_node.default_value

        run_invocation_timeout = self.run_invocation_timeout
        if isinstance(self.run_invocation_timeout, PipelineParameter):
            run_invocation_timeout = self.run_invocation_timeout.default_value

        run_max_try = self.run_max_try
        if isinstance(self.run_max_try, PipelineParameter):
            run_max_try = self.run_max_try.default_value

        logging_level = self.logging_level
        if isinstance(self.logging_level, PipelineParameter):
            logging_level = self.logging_level.default_value

        node_count = self.node_count
        if isinstance(self.node_count, PipelineParameter):
            node_count = self.node_count.default_value

        _serialized_env = Environment._serialize_to_dict(self.environment)

        config = {
            "mini_batch_size": mini_batch_size,
            "partition_keys": partition_keys,
            "error_threshold": self.error_threshold,
            "output_action": self.output_action,
            "logging_level": logging_level,
            "compute_target_name": self.compute_target
            if isinstance(self.compute_target, str)
            else self.compute_target.name,
            "node_count": node_count,
            "process_count_per_node": process_count_per_node,
            "entry_script": self.entry_script,
            "source_directory": self.source_directory,
            "description": self.description,
            "run_invocation_timeout": run_invocation_timeout,
            "run_max_try": run_max_try,
            "append_row_file_name": self.append_row_file_name,
            "environment": _serialized_env,
            "environment_variables": self.environment_variables,
        }
        with open(path, "w") as f:
            ruamelyaml.round_trip_dump({"parallel_run_config": config}, f)

    @staticmethod
    def load_yaml(workspace, path):
        """Load parallel run configuration data from a YAML file.

        :param workspace: The workspace to read the configuration data from.
        :type workspace: azureml.core.Workspace
        :param path: The path to load the configuration from.
        :type path: str
        """
        with open(path, "r") as f:
            config = ruamelyaml.round_trip_load(f)["parallel_run_config"]
        compute_target = _ParallelRunConfigBase._get_target(workspace, config["compute_target_name"])

        env = _ParallelRunConfigBase._deserialize_environment(config, workspace)

        if "mini_batch_size" in config.keys() and config["mini_batch_size"] is not None:
            mini_batch_size = "{0}".format(config["mini_batch_size"])
        else:
            mini_batch_size = None

        return _ParallelRunConfigBase(
            environment=env,
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
            run_max_try=config.get("run_max_try"),
            append_row_file_name=config.get("append_row_file_name"),
            allowed_failed_count=config.get("allowed_failed_count"),
            allowed_failed_percent=config.get("allowed_failed_percent"),
            partition_keys=config.get("partition_keys"),
            environment_variables=config.get("environment_variables"),
        )

    @staticmethod
    def _deserialize_environment(config, workspace):
        """Handle deserialization of an environment from YAML.

        :param config: Loaded dict from ruamel
        :type config: ordereddict
        :param workspace: The workspace to read the configuration data from.
        :type workspace: azureml.core.Workspace
        """
        serialized_env = config.get("environment")
        if serialized_env is None:
            # The two following checks are to maintain backwards compatibility with our old way of loading
            # environments from YAML. Remove eventually because they don't match the rest of AML's yaml envs
            if "environment_dir_path" in config:
                return Environment.load_from_directory(config["environment_dir_path"])
            elif "environment_name" in config:
                return Environment.get(workspace, name=config["environment_name"])
            else:
                raise ValueError("Parameter error: an environment must be provided")
        elif isinstance(serialized_env, str):
            with open(serialized_env, "r") as env_file:
                serialized_env = ruamelyaml.round_trip_load(env_file)
        env = Environment._deserialize_and_add_to_object(serialized_env)
        if isinstance(env, EnvironmentReference):
            env = env.get_environment(workspace)
        return env

    @staticmethod
    def _get_target(ws, target_name):
        return AmlCompute(ws, target_name)
