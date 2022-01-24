# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality for configuring a :class:`azureml.pipeline.steps.ParallelRunStep`."""
from azureml.pipeline.core._parallel_run_config_base import _ParallelRunConfigBase


class ParallelRunConfig(_ParallelRunConfigBase):
    """
    Defines configuration for a :class:`azureml.pipeline.steps.ParallelRunStep` object.

    For an example of using ParallelRunStep, see the notebook https://aka.ms/batch-inference-notebooks.

    For troubleshooting guide, see https://aka.ms/prstsg. You can find more references there.

    .. remarks::

        The ParallelRunConfig class is used to provide configuration for the
        :class:`azureml.pipeline.steps.ParallelRunStep` class. ParallelRunConfig and ParallelRunStep can be used
        together for processing large amounts of data in parallel. Common use cases are training an ML model or
        running offline inference to generate predictions on a batch of observations. ParallelRunStep works by
        breaking up your data into batches that are processed in parallel. The batch size, node count,
        and other tunable parameters to speed up your parallel processing can be controlled with the
        :class:`azureml.pipeline.steps.ParallelRunConfig` class. ParallelRunStep can work with either
        :class:`azureml.data.TabularDataset` or :class:`azureml.data.FileDataset` as input.

        To use ParallelRunStep and ParallelRunConfig:

        * Create a :class:`azureml.pipeline.steps.ParallelRunConfig` object to specify how batch
          processing is performed, with parameters to control batch size, number of nodes per compute target,
          and a reference to your custom Python script.

        * Create a ParallelRunStep object that uses the ParallelRunConfig object, defines inputs and
          outputs for the step.

        * Use the configured ParallelRunStep object in a :class:`azureml.pipeline.core.Pipeline`
          just as you would with other pipeline step types.

        Examples of working with ParallelRunStep and ParallelRunConfig classes for batch inference are discussed in
        the following articles:

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
        threshold is for the entire input and not for individual mini-batches sent to run() method.
        The range is [-1, int.max]. -1 indicates ignore all failures during processing.
    :type error_threshold: int
    :param output_action: How the output should be organized. Current supported values
        are 'append_row' and 'summary_only'.
        1. 'append_row' – All values output by run() method invocations will be aggregated into
        one unique file named parallel_run_step.txt which is created in the output location.
        2. 'summary_only' – User script is expected to store the output itself. An output row
        is still expected for each successful input item processed. The system uses this output
        only for error threshold calculation (ignoring the actual value of the row).
    :type output_action: str
    :param compute_target: Compute target to use for ParallelRunStep execution. This parameter may be specified as
        a compute target object or the name of a compute target in the workspace.
    :type compute_target: azureml.core.compute.AmlCompute or str
    :param node_count: Number of nodes in the compute target used for running the ParallelRunStep.
    :type node_count: int
    :param process_count_per_node: The number of worker processes per node to run the entry script in parallel.
        For GPU machine, the default value is 1.
        For CPU machine, the default value is the number of cores.
        A worker process will call ``run()`` repeatedly by passing the mini batch it gets.
        The total number of worker processes in your job is ``process_count_per_node * node_count``,
        which decides the max number of ``run()`` to execute in parallel.
    :type process_count_per_node: int
    :param mini_batch_size: For FileDataset input, this field is the number of files a user script can process
        in one run() call. For TabularDataset input, this field is the approximate size of data the user script
        can process in one run() call. Example values are 1024, 1024KB, 10MB, and 1GB.
        (optional, default value is 10 files for FileDataset and 1MB for TabularDataset.)
    :type mini_batch_size: typing.Union[str, int]
    :param source_directory: Path to folder that contains the ``entry_script`` and supporting files used
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
    :param run_max_try: The number of maximum tries for a failed or timeout mini batch.
        The range is [1, int.max]. The default value is 3.
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
        logging_level="INFO",
        run_invocation_timeout=60,
        run_max_try=3,
        append_row_file_name=None,
        allowed_failed_count=None,
        allowed_failed_percent=None,
        partition_keys=None,
        environment_variables=None,
    ):
        """Initialize the config object.

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
            each returned output element indicates one successful inference of input element in the
            input mini-batch.
            Each parallel worker process will call `init` once and then loop over `run` function until all mini-batches
            are processed.
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
            one unique file named parallel_run_step.txt which is created in the output location.
            2. 'summary_only' – User script is expected to store the output itself. An output row
            is still expected for each successful input item processed. The system uses this output
            only for error threshold calculation (ignoring the actual value of the row).
        :type output_action: str
        :param compute_target: Compute target to use for ParallelRunStep execution. This parameter may be specified as
            a compute target object or the name of a compute target in the workspace.
        :type compute_target: azureml.core.compute.AmlCompute or str
        :param node_count: Number of nodes in the compute target used for running the ParallelRunStep.
        :type node_count: int
        :param process_count_per_node: The number of worker processes per node to run the entry script in parallel.
            For a GPU machine, the default value is 1.
            For a CPU machine, the default value is the number of cores.
            A worker process will call ``run()`` repeatedly by passing the mini batch it gets.
            The total number of worker processes in your job is ``process_count_per_node * node_count``,
            which decides the max number of ``run()`` to execute in parallel.
        :type process_count_per_node: int
        :param mini_batch_size: For FileDataset input, this field is the number of files a user script can process
            in one run() call. For TabularDataset input, this field is the approximate size of data the user script
            can process in one run() call. Example values are 1024, 1024KB, 10MB, and 1GB.
            (optional, default value is 10 files for FileDataset and 1MB for TabularDataset.)
        :type mini_batch_size: str or int
        :param source_directory: Path to folder that contains the ``entry_script`` and supporting files used
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
        :param run_max_try: The number of maximum tries for a failed or timeout mini batch.
            The range is [1, int.max]. The default value is 3.
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
        super(ParallelRunConfig, self).__init__(
            environment=environment,
            entry_script=entry_script,
            error_threshold=error_threshold,
            allowed_failed_count=allowed_failed_count,
            allowed_failed_percent=allowed_failed_percent,
            output_action=output_action,
            compute_target=compute_target,
            node_count=node_count,
            process_count_per_node=process_count_per_node,
            mini_batch_size=mini_batch_size,
            source_directory=source_directory,
            description=description,
            logging_level=logging_level,
            run_invocation_timeout=run_invocation_timeout,
            run_max_try=run_max_try,
            append_row_file_name=append_row_file_name,
            partition_keys=partition_keys,
            environment_variables=environment_variables,
        )

    def save_to_yaml(self, path):
        """Export parallel run configuration data to a YAML file.

        :param path: The path to save the file to.
        :type path: str
        """
        super(ParallelRunConfig, self).save_to_yaml(path)

    @staticmethod
    def load_yaml(workspace, path):
        """Load parallel run configuration data from a YAML file.

        :param workspace: The workspace to read the configuration data from.
        :type workspace: azureml.core.Workspace
        :param path: The path to load the configuration from.
        :type path: str
        """
        return _ParallelRunConfigBase.load_yaml(workspace, path)
