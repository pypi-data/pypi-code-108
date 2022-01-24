# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality to add a step to run user script in parallel mode on multiple AmlCompute targets."""
import argparse
import logging
import re
import json
import os
import sys
import warnings
from itertools import chain

import azureml.core
from azureml.core.runconfig import RunConfiguration
from azureml.core.compute import AmlCompute
from azureml.data import TabularDataset, FileDataset
from azureml.data.constants import UPLOAD_MODE
from azureml.data.data_reference import DataReference
from azureml.data.dataset_consumption_config import DatasetConsumptionConfig
from azureml.data.output_dataset_config import (
    OutputTabularDatasetConfig,
    OutputFileDatasetConfig,
    OutputDatasetConfig,
    LinkFileOutputDatasetConfig,
    LinkTabularOutputDatasetConfig,
)
from azureml.pipeline.core._parallel_run_config_base import _ParallelRunConfigBase
from azureml.pipeline.core._python_script_step_base import _PythonScriptStepBase
from azureml.pipeline.core.graph import PipelineParameter
from azureml.pipeline.core.graph import ParamDef
from azureml.pipeline.core.pipeline_output_dataset import PipelineOutputFileDataset
from azureml.pipeline.core.pipeline_output_dataset import PipelineOutputTabularDataset
from azureml.pipeline.core.builder import PipelineData

DEFAULT_BATCH_SCORE_MAIN_FILE_NAME = "driver/amlbi_main.py"
DEFAULT_MINI_BATCH_SIZE = 1
DEFAULT_MINI_BATCH_SIZE_FILEDATASET = 10
DEFAULT_MINI_BATCH_SIZE_TABULARDATASET = 1024 * 1024
FILE_TYPE_INPUT = "file"
TABULAR_TYPE_INPUT = "tabular"
REQUIRED_DATAPREP_EXTRAS = {
    TABULAR_TYPE_INPUT: "fuse,pandas",
    FILE_TYPE_INPUT: "fuse",
}
ALLOWED_INPUT_TYPES = (
    DatasetConsumptionConfig,
    PipelineOutputFileDataset,
    PipelineOutputTabularDataset,
    OutputFileDatasetConfig,
    OutputTabularDatasetConfig,
    LinkFileOutputDatasetConfig,
    LinkTabularOutputDatasetConfig,
)

INPUT_TYPE_DICT = {
    TabularDataset: TABULAR_TYPE_INPUT,
    PipelineOutputTabularDataset: TABULAR_TYPE_INPUT,
    OutputTabularDatasetConfig: TABULAR_TYPE_INPUT,
    LinkTabularOutputDatasetConfig: TABULAR_TYPE_INPUT,
    FileDataset: FILE_TYPE_INPUT,
    PipelineOutputFileDataset: FILE_TYPE_INPUT,
    OutputFileDatasetConfig: FILE_TYPE_INPUT,
    LinkFileOutputDatasetConfig: FILE_TYPE_INPUT,
}
PARALLEL_RUN_VERSION = "v1"

# current packages which also install azureml-dataprep[fuse,pandas]
DATAPREP_FUSE_PANDAS_PACKAGES = [
    "azureml-dataprep[fuse,pandas]",
    "azureml-dataprep[pandas,fuse]",
    "azureml-automl-runtime",
    "azureml-contrib-dataset",
    "azureml-datadrift",
    "azureml-dataset-runtime[pandas,fuse]",
    "azureml-dataset-runtime[fuse,pandas]",
    "azureml-opendatasets",
    "azureml-train-automl",
    "azureml-train-automl-runtime",
]

# current packages which also install azureml-dataprep[fuse]
DATAPREP_FUSE_ONLY_PACKAGES = [
    "azureml-dataprep[fuse]",
    "azureml-dataset-runtime[fuse]",
    "azureml-defaults",
    "azureml-sdk",
]

DATAPREP_FUSE_PACKAGES = list(chain(DATAPREP_FUSE_PANDAS_PACKAGES, DATAPREP_FUSE_ONLY_PACKAGES))

REQUIRED_DATAPREP_PACKAGES = {
    TABULAR_TYPE_INPUT: DATAPREP_FUSE_PANDAS_PACKAGES,
    FILE_TYPE_INPUT: DATAPREP_FUSE_PACKAGES,
}


class _ParallelRunStepBase(_PythonScriptStepBase):
    r"""
    Creates an Azure Machine Learning Pipeline step to process large amounts of data asynchronously and in parallel.

    For an example of using ParallelRunStep, see the notebook https://aka.ms/batch-inference-notebooks.

    .. remarks::

        _ParallelRunStepBase can be used for processing large amounts of data in parallel. Common use cases are
        training an ML model or running offline inference to generate predictions on a batch of observations.
        _ParallelRunStepBase works by breaking up your data into batches that are processed in parallel. The batch
        size node count, and other tunable parameters to speed up your parallel processing can be controlled with
        the :class:`azureml.pipeline.steps.ParallelRunConfig` class. _ParallelRunStepBase can work with either
        :class:`azureml.data.TabularDataset` or :class:`azureml.data.FileDataset` as input.

        To use _ParallelRunStepBase:

        * Create a :class:`azureml.pipeline.steps.ParallelRunConfig` object to specify how batch
          processing is performed, with parameters to control batch size, number of nodes per compute target,
          and a reference to your custom Python script.

        * Create a _ParallelRunStepBase object that uses the ParallelRunConfig object, define inputs and
          outputs for the step.

        * Use the configured _ParallelRunStepBase object in a :class:`azureml.pipeline.core.Pipeline`
          just as you would with pipeline step types defined in the :mod:`azureml.pipeline.steps` package.

        Examples of working with _ParallelRunStepBase and ParallelRunConfig classes for batch inference are
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
                mini_batch_size="5",
                error_threshold=10,         # Optional, allowed failed count on mini batch items
                allowed_failed_count=15,    # Optional, allowed failed count on mini batches
                allowed_failed_percent=10,  # Optional, allowed failed percent on mini batches
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

    :param name: Name of the step. Must be unique to the workspace, only consist of lowercase letters,
        numbers, or dashes, start with a letter, and be between 3 and 32 characters long.
    :type name: str
    :param parallel_run_config: A _ParallelRunConfigBase object used to determine required run properties.
    :type parallel_run_config: azureml.pipeline.core._ParallelRunConfigBase
    :param inputs: List of input datasets. All datasets in the list should be of same type.
        Input data will be partitioned for parallel processing. Each dataset in the list is partitioned
        into mini-batches separately, and each of the mini-batches is treated equally in the parallel processing.
    :type inputs: list[azureml.data.dataset_consumption_config.DatasetConsumptionConfig
                    or azureml.data.dataset_consumption_config.PipelineOutputFileDataset
                    or azureml.data.dataset_consumption_config.PipelineOutputTabularDataset]
    :param output: Output port binding, may be used by later pipeline steps.
    :type output: azureml.pipeline.core.builder.PipelineData, azureml.pipeline.core.graph.OutputPortBinding
    :param side_inputs: List of side input reference data. Side inputs will not be partitioned as input data.
    :type side_inputs: list[azureml.pipeline.core.graph.InputPortBinding
                    or azureml.data.data_reference.DataReference
                    or azureml.pipeline.core.PortDataReference
                    or azureml.pipeline.core.builder.PipelineData
                    or azureml.pipeline.core.pipeline_output_dataset.PipelineOutputFileDataset
                    or azureml.pipeline.core.pipeline_output_dataset.PipelineOutputTabularDataset
                    or azureml.data.dataset_consumption_config.DatasetConsumptionConfig]
    :param arguments: List of command-line arguments to pass to the Python entry_script.
    :type arguments: list[str]
    :param allow_reuse: Whether the step should reuse previous results when run with the same settings/inputs.
        If this is false, a new run will always be generated for this step during pipeline execution.
    :type allow_reuse: bool
    """

    def __init__(
        self,
        name,
        parallel_run_config,
        inputs,
        output=None,
        side_inputs=None,
        arguments=None,
        allow_reuse=True,
    ):
        r"""Create an Azure ML Pipeline step to process large amounts of data asynchronously and in parallel.

        For an example of using ParallelRunStep, see the notebook link https://aka.ms/batch-inference-notebooks.

        :param name: Name of the step. Must be unique to the workspace, only consist of lowercase letters,
            numbers, or dashes, start with a letter, and be between 3 and 32 characters long.
        :type name: str
        :param parallel_run_config: A ParallelRunConfig object used to determine required run properties.
        :type parallel_run_config: azureml.pipeline.steps.ParallelRunConfig
        :param inputs: List of input datasets. All datasets in the list should be of same type.
            Input data will be partitioned for parallel processing.
        :type inputs: list[azureml.data.dataset_consumption_config.DatasetConsumptionConfig
                        or azureml.data.dataset_consumption_config.PipelineOutputFileDataset
                        or azureml.data.dataset_consumption_config.PipelineOutputTabularDataset]
        :param output: Output port binding, may be used by later pipeline steps.
        :type output: azureml.pipeline.core.builder.PipelineData, azureml.pipeline.core.graph.OutputPortBinding
        :param side_inputs: List of side input reference data. Side inputs will not be partitioned as input data.
        :type side_inputs: list[azureml.pipeline.core.graph.InputPortBinding
                        or azureml.data.data_reference.DataReference
                        or azureml.pipeline.core.PortDataReference
                        or azureml.pipeline.core.builder.PipelineData
                        or azureml.pipeline.core.pipeline_output_dataset.PipelineOutputFileDataset
                        or azureml.pipeline.core.pipeline_output_dataset.PipelineOutputTabularDataset
                        or azureml.data.dataset_consumption_config.DatasetConsumptionConfig]
        :param arguments: List of command-line arguments to pass to the Python entry_script.
        :type arguments: list[str]
        :param allow_reuse: Whether the step should reuse previous results when run with the same settings/inputs.
            If this is false, a new run will always be generated for this step during pipeline execution.
        :type allow_reuse: bool
        """
        self._name = name
        self._parallel_run_config = parallel_run_config
        self._inputs = inputs
        self._output = output
        self._side_inputs = side_inputs
        self._arguments = arguments
        self._node_count = self._parallel_run_config.node_count
        self._process_count_per_node = self._parallel_run_config.process_count_per_node
        self._mini_batch_size = self._parallel_run_config.mini_batch_size
        self._partition_keys = self._parallel_run_config.partition_keys
        self._error_threshold = self._parallel_run_config.error_threshold
        self._allowed_failed_count = self._parallel_run_config.allowed_failed_count
        self._allowed_failed_percent = self._parallel_run_config.allowed_failed_percent
        self._logging_level = self._parallel_run_config.logging_level
        self._run_invocation_timeout = self._parallel_run_config.run_invocation_timeout
        self._run_max_try = self._parallel_run_config.run_max_try
        self._input_compute_target = self._parallel_run_config.compute_target
        self._pystep_inputs = []
        self._pystep_side_inputs = []
        self._input_ds_type = None
        self._glob_syntax_pattern = re.compile(r"[\^\\\$\|\?\*\+\(\)\[\]\{\}]")
        self._module_logger = logging.getLogger(__name__)
        self._rank_mini_batch_count = self._get_rank_mini_batch_count()
        self._platform = self._get_os_type_from_env(self._parallel_run_config.environment)

        self._process_inputs_output_dataset_configs()
        self._validate()
        self._get_pystep_inputs()

        if self._side_inputs:
            self._handle_side_inputs()

        pipeline_runconfig_params = self._get_pipeline_runconfig_params()
        prun_runconfig = self._generate_runconfig()
        prun_main_file_args = self._generate_main_file_args()

        if self._side_inputs:
            self._pystep_inputs += self._pystep_side_inputs

        compute_target = self._input_compute_target
        if isinstance(compute_target, str):
            compute_target = (compute_target, AmlCompute._compute_type)

        super(_ParallelRunStepBase, self).__init__(
            name=self._name,
            source_directory=self._parallel_run_config.source_directory,
            script_name=self._parallel_run_config.entry_script,
            runconfig=prun_runconfig,
            runconfig_pipeline_params=pipeline_runconfig_params,
            arguments=prun_main_file_args,
            compute_target=compute_target,
            inputs=self._pystep_inputs,
            outputs=self._output,
            allow_reuse=allow_reuse,
        )

    @staticmethod
    def _get_os_type_from_env(env):
        """Return os of the given Environment, return either "windows" or "linux".

        If no os specified in given env, defaults to "Linux".
        """
        if env is not None and env.docker is not None and env.docker.platform is not None:
            os_type = env.docker.platform.os
            if os_type and isinstance(os_type, str):
                return os_type.lower()

        return "linux"

    @property
    def running_on_windows(self):
        """Return True if the platform is windows."""
        return self._platform.lower() == "windows"

    def _get_rank_mini_batch_count(self):
        """Return the number of rank mini batch."""
        if not self._arguments:
            return 0
        parser = argparse.ArgumentParser(description="Parallel Run Step")
        parser.add_argument(
            "--rank_mini_batch_count",
            type=int,
            required=False,
            default=0,
            help="The number of rank mini batches to create."
            " A rank mini batch doesn't take any input. It is used to run entry script without any input dataset."
            " For example, start N processes to run the entry script."
            " The default value is '0', where there is no rank mini batch. A negative value will be considered as '0'."
            " If this value is greater than 0, other input will be ignored .",
        )
        args, _ = parser.parse_known_args([str(arg) for arg in self._arguments])
        return args.rank_mini_batch_count

    def _validate(self):
        """Validate input params to init parallel run step class."""
        self._validate_arguments()
        self._validate_inputs()
        self._validate_output()
        self._validate_parallel_run_config()
        self._validate_source_directory()
        self._validate_entry_script()

    def _validate_arguments(self):
        """Validate the additional arguments."""
        reserved_args = [
            "mini_batch_size",
            "error_threshold",
            "allowed_failed_count",
            "allowed_failed_percent",
            "output",
            "output_action",
            "logging_level",
            "process_count_per_node",
            "run_invocation_timeout",
            "run_max_try",
            "append_row_file_name",
            "partition_keys",
        ]
        if not self._arguments:
            return

        # Ensure the first one start with "-"
        if not self._arguments[0].startswith("-"):
            raise ValueError(
                "Found invalid argument '{}'."
                " As your arguments will be merged with reserved argument,"
                " you can only use keyword argument.".format(self._arguments[0])
            )

        for item in self._arguments:
            # Check argument with "--"
            if isinstance(item, str) and item.startswith("--"):
                name = item[2:]
                parts = name.split("=")
                if len(parts) > 1:
                    name = parts[0]

                if name in reserved_args:
                    raise ValueError(
                        "'{}' is a reserved argument in ParallelRunStep, "
                        "please use another argument name instead.".format(name)
                    )

    def _get_input_type(self, in_ds, is_primary_input=True):
        input_type = type(in_ds)
        ds_mapping_type = None
        if input_type == DatasetConsumptionConfig:
            # Dataset mode needs to be direct except when we convert it to data reference.
            # This will be removed in next release.
            real_ds_obj = in_ds.dataset
            if isinstance(in_ds.dataset, PipelineParameter):
                real_ds_obj = in_ds.dataset.default_value
            if (
                isinstance(real_ds_obj, (TabularDataset, OutputTabularDatasetConfig, LinkTabularOutputDatasetConfig))
            ) and in_ds.mode != "direct":
                raise Exception("Please ensure input dataset consumption mode is direct")
            if isinstance(real_ds_obj, FileDataset) and self._partition_keys and in_ds.mode != "direct":
                if is_primary_input:
                    raise Exception("Please ensure input dataset consumption mode is direct for partitioned dataset")
            ds_mapping_type = INPUT_TYPE_DICT[type(real_ds_obj)]
        elif input_type == PipelineOutputFileDataset or input_type == PipelineOutputTabularDataset:
            # Dataset mode needs to be direct except when we convert it to data reference.
            # This will be removed in next release.
            if input_type == PipelineOutputTabularDataset and in_ds._input_mode != "direct":
                raise Exception("Please ensure pipeline input dataset consumption mode is direct")
            ds_mapping_type = INPUT_TYPE_DICT[input_type]
        else:
            raise Exception("Step input must be of any type: {}, found {}".format(ALLOWED_INPUT_TYPES, input_type))
        return ds_mapping_type

    def _validate_inputs(self):
        """Validate all inputs are same type and ensure they meet dataset requirement."""
        assert (isinstance(self._inputs, list) and self._inputs != []) or self._rank_mini_batch_count > 0, (
            "The parameter 'inputs' must be a list and have at least one element"
            " or rank_mini_batch_count must be greater than zero."
        )

        if self._inputs:
            self._input_ds_type = self._get_input_type(self._inputs[0])
            for input_ds in self._inputs:
                if self._input_ds_type != self._get_input_type(input_ds):
                    raise Exception("All inputs of step must be same type")
        else:  # self._rank_mini_batch_count > 0 Set to FileDataset for void tasks.
            self._input_ds_type = FILE_TYPE_INPUT

    def _validate_output(self):
        if self._parallel_run_config.output_action.lower() != "summary_only" and self._output is None:
            raise Exception("Please specify output parameter.")

        if self._output is not None:
            self._output = [self._output]

    def _validate_parallel_run_config(self):
        """Validate parallel run config."""
        if not isinstance(self._parallel_run_config, _ParallelRunConfigBase):
            raise Exception("Param parallel_run_config must be a azureml.pipeline.steps.ParallelRunConfig")

        if self._parallel_run_config.mini_batch_size is None:
            if self._input_ds_type == FILE_TYPE_INPUT:
                self._mini_batch_size = DEFAULT_MINI_BATCH_SIZE_FILEDATASET
            elif self._input_ds_type == TABULAR_TYPE_INPUT:
                self._mini_batch_size = DEFAULT_MINI_BATCH_SIZE_TABULARDATASET

    def _validate_source_directory(self):
        """Validate the source_directory param."""
        source_dir = self._parallel_run_config.source_directory
        if source_dir and source_dir != "":
            if not os.path.exists(source_dir):
                raise ValueError("The value '{0}' specified in source_directory doesn't exist.".format(source_dir))
            if not os.path.isdir(source_dir):
                raise ValueError(
                    "The value '{0}' specified in source_directory is not a directory.".format(source_dir)
                )

            full_path = os.path.abspath(source_dir)
            if full_path not in sys.path:
                sys.path.insert(0, full_path)

    def _validate_entry_script(self):
        """Validate the entry script."""
        source_dir = self._parallel_run_config.source_directory
        entry_script = self._parallel_run_config.entry_script

        # In validation of ParallelRunConfig, verify if the entry_script is required.
        # Here we don't verify again.
        if entry_script and entry_script != "":
            if source_dir and source_dir != "":
                # entry script must be in this directory
                full_path = os.path.join(source_dir, entry_script)
                if not os.path.exists(full_path):
                    raise ValueError("The value '{0}' specified in entry_script doesn't exist.".format(entry_script))
                if not os.path.isfile(full_path):
                    raise ValueError("The value '{0}' specified in entry_script is not a file.".format(entry_script))

    def _convert_to_mount_mode(self, in_ds):
        """Convert inputs into mount mode."""
        if isinstance(in_ds, PipelineOutputFileDataset):
            if in_ds._input_mode != "mount" or in_ds._input_path_on_compute is None:
                return in_ds.as_mount()
        elif isinstance(in_ds, DatasetConsumptionConfig):
            if in_ds.mode != "mount" or in_ds.path_on_compute is None:
                return in_ds.as_mount()
        return in_ds

    def _get_pystep_inputs(self):
        """Process and convert inputs before adding to pystep_inputs."""

        def _process_file_dataset(file_ds):
            """Process file dataset."""
            if self.running_on_windows:
                self._pystep_inputs.append(file_ds)
            else:
                mounted_ds = self._convert_to_mount_mode(file_ds)
                self._pystep_inputs.append(mounted_ds)

        if self._partition_keys:
            self._pystep_inputs = self._inputs
        else:
            if self._input_ds_type == FILE_TYPE_INPUT:
                for input_ds in self._inputs:
                    _process_file_dataset(input_ds)
            elif self._input_ds_type == TABULAR_TYPE_INPUT:
                self._pystep_inputs = self._inputs

    def _handle_side_inputs(self):
        """Handle side inputs."""
        for input_ds in self._side_inputs:
            if type(input_ds) != PipelineData and type(input_ds) != DataReference:
                input_type = self._get_input_type(input_ds, is_primary_input=False)
                if input_type == FILE_TYPE_INPUT:
                    mounted_ds = self._convert_to_mount_mode(input_ds)
                    self._pystep_side_inputs.append(mounted_ds)
                    # Update original DatasetConsumptionConfig reference in arguments to
                    # new DatasetConsumptionConfig with mount
                    if self._arguments is not None and isinstance(self._arguments, list):
                        for arg_index, side_input_arg in enumerate(self._arguments):
                            if side_input_arg == input_ds:
                                self._arguments[arg_index] = mounted_ds
                                break
                    continue
            self._pystep_side_inputs.append(input_ds)

    def _get_pipeline_runconfig_params(self):
        """
        Generate pipeline parameters for runconfig.

        :return: runconfig pipeline parameters
        :rtype: dict
        """
        prun_runconfig_pipeline_params = {}
        if isinstance(self._node_count, PipelineParameter):
            prun_runconfig_pipeline_params["NodeCount"] = self._node_count
        return prun_runconfig_pipeline_params

    def _generate_runconfig(self):
        """
        Generate runconfig for parallel run step.

        :return: runConfig
        :rtype: RunConfig
        """
        run_config = RunConfiguration()
        if isinstance(self._node_count, PipelineParameter):
            run_config.node_count = self._node_count.default_value
        else:
            run_config.node_count = self._node_count
        if isinstance(self._input_compute_target, AmlCompute):
            run_config.target = self._input_compute_target
        run_config.framework = "Python"
        # For AmlCompute we need to set run_config.docker.use_docker = True
        run_config.docker.use_docker = True
        run_config.environment = self._parallel_run_config.environment
        run_config.environment_variables.update(self._parallel_run_config.environment_variables)

        if self.running_on_windows:
            # For windows compute, always use "ParallelTask".
            run_config.communicator = "ParallelTask"

        conda_dependencies = run_config.environment.python.conda_dependencies
        pip_packages = list(conda_dependencies.pip_packages) if conda_dependencies else []

        self._check_required_pip_packages(pip_packages)

        return run_config

    def _check_required_pip_packages(self, pip_packages):
        """Check whether required pip package added"""
        findings_core = [
            pip for pip in pip_packages if pip.startswith("azureml") and not pip.startswith("azureml-dataset-runtime")
        ]

        if not findings_core:
            warnings.warn(
                """
ParallelRunStep requires azureml-core package to provide the functionality.
Please add azureml-core package in CondaDependencies.""",
                UserWarning,
            )

        # search to see if any other package may have included it as direct or transitive dependency
        required_dataprep_packages = REQUIRED_DATAPREP_PACKAGES[self._input_ds_type]
        findings_dataprep = filter(
            lambda x: [pip for pip in pip_packages if pip.startswith(x)], required_dataprep_packages
        )
        if not next(findings_dataprep, False):
            extra = REQUIRED_DATAPREP_EXTRAS[self._input_ds_type]
            warnings.warn(
                """
ParallelRunStep requires azureml-dataset-runtime[{}] for {} dataset.
Please add relevant package in CondaDependencies.""".format(
                    extra, self._input_ds_type
                ),
                UserWarning,
            )

    def _generate_main_file_args(self):
        """
        Generate main args for entry script.

        :return: The generated main args for entry script.
        :rtype: array
        """
        main_args = [
            "--client_sdk_version",
            azureml.core.VERSION,
            "--scoring_module_name",
            self._parallel_run_config.entry_script,
            "--mini_batch_size",
            self._mini_batch_size,
            "--error_threshold",
            self._error_threshold,
            "--output_action",
            self._parallel_run_config.output_action,
            "--logging_level",
            self._logging_level,
            "--run_invocation_timeout",
            self._run_invocation_timeout,
            "--run_max_try",
            self._run_max_try,
            "--create_snapshot_at_runtime",
            "True",
        ]

        if self._allowed_failed_count is not None:
            main_args += ["--allowed_failed_count", self._allowed_failed_count]

        if self._allowed_failed_percent is not None:
            main_args += ["--allowed_failed_percent", self._allowed_failed_percent]

        # Use this variable to dismiss: W503 line break before binary operator
        is_append_row = self._parallel_run_config.output_action.lower() == "append_row"
        if is_append_row and self._parallel_run_config.append_row_file_name is not None:
            main_args += ["--append_row_file_name", self._parallel_run_config.append_row_file_name]

        if self._output is not None:
            main_args += ["--output", self._output[0]]

        if self._process_count_per_node is not None:
            main_args += ["--process_count_per_node", self._process_count_per_node]

        if self._partition_keys is not None:
            main_args += ["--partition_keys"]
            if isinstance(self._partition_keys, PipelineParameter):
                main_args += [self._partition_keys]
            else:
                main_args += [json.dumps(self._partition_keys)]

        if self._arguments is not None and isinstance(self._arguments, list):
            main_args += self._arguments

        if self._input_ds_type == TABULAR_TYPE_INPUT:
            for index, in_ds in enumerate(self._pystep_inputs):
                ds_name = in_ds.input_name if isinstance(in_ds, PipelineOutputTabularDataset) else in_ds.name
                main_args += ["--input_ds_{0}".format(index), ds_name]
        elif self._input_ds_type == FILE_TYPE_INPUT:
            for index, in_ds in enumerate(self._pystep_inputs):
                if isinstance(in_ds, DatasetConsumptionConfig) or isinstance(in_ds, PipelineOutputFileDataset):
                    ds_name = in_ds.input_name if isinstance(in_ds, PipelineOutputFileDataset) else in_ds.name
                    main_args += ["--input_fds_{0}".format(index), ds_name]
                else:
                    main_args += ["--input{0}".format(index), in_ds]

        # In order make dataset as pipeline parameter works, we need add it as a param in main_args
        for index, in_ds in enumerate(self._pystep_inputs):
            if isinstance(in_ds, DatasetConsumptionConfig) and isinstance(in_ds.dataset, PipelineParameter):
                main_args += ["--input_pipeline_param_{0}".format(index), in_ds]

        return main_args

    def _generate_batch_inference_metadata(self):
        """
        Generate batch inference metadata which will be register to MMS service.

        :return: The generated batch inference metadata.
        :rtype: str
        """

        def _get_default_value(in_param):
            default_value = in_param
            # partition_keys is of list type and need to be json dumped
            if isinstance(in_param, list):
                default_value = json.dumps(in_param)
            if isinstance(in_param, PipelineParameter):
                default_value = in_param.default_value
            return default_value

        batch_inferencing_metadata = {
            "Name": self._name,
            "ComputeName": self._input_compute_target
            if isinstance(self._input_compute_target, str)
            else self._input_compute_target.name,
            "EntryScript": self._parallel_run_config.entry_script,
            "NodeCount": _get_default_value(self._node_count),
            "ProcessCountPerNode": _get_default_value(self._process_count_per_node),
            "MiniBatchSize": _get_default_value(self._mini_batch_size),
            "PartitionKeys": _get_default_value(self._partition_keys),
            "ErrorThreshold": _get_default_value(self._parallel_run_config.error_threshold),
            "OutputAction": self._parallel_run_config.output_action,
            "EnvironmentName": self._parallel_run_config.environment.name,
            "EnvironmentVersion": self._parallel_run_config.environment.version,
            "version": PARALLEL_RUN_VERSION,
            "platform": self._platform,
            "RunInvocationTimeout": _get_default_value(self._run_invocation_timeout),
            "RunMaxTry": _get_default_value(self._run_max_try),
            "LoggingLevel": _get_default_value(self._logging_level),
        }

        val = _get_default_value(self._parallel_run_config.allowed_failed_count)
        if val is not None:
            batch_inferencing_metadata["AllowedFailedCount"] = val

        val = _get_default_value(self._parallel_run_config.allowed_failed_percent)
        if val is not None:
            batch_inferencing_metadata["AllowedFailedPercent"] = val

        return json.dumps(batch_inferencing_metadata)

    def _process_inputs_output_dataset_configs(self):
        if not self._inputs:
            return

        for i in range(len(self._inputs)):
            input = self._inputs[i]
            if isinstance(input, OutputDatasetConfig):
                self._inputs[i] = input.as_input()
                if self._arguments and input in self._arguments:
                    arg_index = self._arguments.index(input)
                    self._arguments[arg_index] = self._inputs[i]

        if self._side_inputs:
            for i in range(len(self._side_inputs)):
                side_input = self._side_inputs[i]
                if isinstance(side_input, OutputDatasetConfig):
                    self._side_inputs[i] = side_input.as_input()
                    if self._arguments and side_input in self._arguments:
                        arg_index = self._arguments.index(side_input)
                        self._arguments[arg_index] = self._side_inputs[i]

        if isinstance(self._output, OutputFileDatasetConfig):
            # Windows compute does not support mount, set to upload mode here.
            if self.running_on_windows:
                if self._output.mode != UPLOAD_MODE:
                    self._output = self._output.as_upload()

    def create_node(self, graph, default_datastore, context):
        """
        Create a node for :class:`azureml.pipeline.steps.PythonScriptStep` and add it to the specified graph.

        This method is not intended to be used directly. When a pipeline is instantiated with ParallelRunStep,
        Azure Machine Learning automatically passes the parameters required through this method so that the step
        can be added to a pipeline graph that represents the workflow.

        :param graph: Graph object.
        :type graph: azureml.pipeline.core.graph.Graph
        :param default_datastore: Default datastore.
        :type default_datastore: azureml.data.azure_storage_datastore.AbstractAzureStorageDatastore or
            azureml.data.azure_data_lake_datastore.AzureDataLakeDatastore
        :param context: Context.
        :type context: azureml.pipeline.core._GraphContext

        :return: The created node.
        :rtype: azureml.pipeline.core.graph.Node
        """
        node = super(_ParallelRunStepBase, self).create_node(graph, default_datastore, context)
        node.get_param("BatchInferencingMetaData").set_value(self._generate_batch_inference_metadata())
        node.get_param("Script").set_value(DEFAULT_BATCH_SCORE_MAIN_FILE_NAME)
        return node

    def create_module_def(
        self,
        execution_type,
        input_bindings,
        output_bindings,
        param_defs=None,
        create_sequencing_ports=True,
        allow_reuse=True,
        version=None,
        arguments=None,
    ):
        """
        Create the module definition object that describes the step.

        This method is not intended to be used directly.

        :param execution_type: The execution type of the module.
        :type execution_type: str
        :param input_bindings: The step input bindings.
        :type input_bindings: list
        :param output_bindings: The step output bindings.
        :type output_bindings: list
        :param param_defs: The step param definitions.
        :type param_defs: list
        :param create_sequencing_ports: If true, sequencing ports will be created for the module.
        :type create_sequencing_ports: bool
        :param allow_reuse: If true, the module will be available to be reused in future Pipelines.
        :type allow_reuse: bool
        :param version: The version of the module.
        :type version: str
        :param arguments: Annotated arguments list to use when calling this module.
        :type arguments: builtin.list

        :return: The module def object.
        :rtype: azureml.pipeline.core.graph.ModuleDef
        """
        if param_defs is None:
            param_defs = []
        else:
            param_defs = list(param_defs)

        batch_inference_metadata_param_def = ParamDef(
            name="BatchInferencingMetaData",
            set_env_var=False,
            is_metadata_param=True,
            default_value="None",
            env_var_override=False,
        )
        param_defs.append(batch_inference_metadata_param_def)

        return super(_ParallelRunStepBase, self).create_module_def(
            execution_type=execution_type,
            input_bindings=input_bindings,
            output_bindings=output_bindings,
            param_defs=param_defs,
            create_sequencing_ports=create_sequencing_ports,
            allow_reuse=allow_reuse,
            version=version,
            module_type="BatchInferencing",
            arguments=arguments,
        )
