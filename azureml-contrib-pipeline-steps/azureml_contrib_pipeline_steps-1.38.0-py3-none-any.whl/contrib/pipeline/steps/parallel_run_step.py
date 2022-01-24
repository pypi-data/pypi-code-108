# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality to add a step to run user script in parallel mode on multiple AmlCompute targets."""
import logging
import re
import json
import uuid
import os
import sys
import warnings

from azureml.contrib.pipeline.steps import ParallelRunConfig
import azureml.core
from azureml.core import Workspace
from azureml.core.runconfig import RunConfiguration
from azureml.core.compute import AmlCompute
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.datastore import Datastore
from azureml.data import TabularDataset, FileDataset
from azureml.data.azure_storage_datastore import AzureBlobDatastore
from azureml.data.data_reference import DataReference
from azureml.data.dataset_consumption_config import DatasetConsumptionConfig
from azureml.pipeline.core._python_script_step_base import _PythonScriptStepBase
from azureml.pipeline.core.graph import PipelineParameter
from azureml.pipeline.core.graph import ParamDef
from azureml.pipeline.core.pipeline_output_dataset import PipelineOutputFileDataset
from azureml.pipeline.core.pipeline_output_dataset import PipelineOutputTabularDataset

DEFAULT_BATCH_SCORE_MAIN_FILE_NAME = "driver/amlbi_main.py"
DEFAULT_MINI_BATCH_SIZE = 1
DEFAULT_MINI_BATCH_SIZE_FILEDATASET = 10
DEFAULT_MINI_BATCH_SIZE_TABULARDATASET = 1024 * 1024
FILE_TYPE_INPUT = "file"
TABULAR_TYPE_INPUT = "tabular"
ALLOWED_INPUT_TYPES = (DatasetConsumptionConfig, PipelineOutputFileDataset, PipelineOutputTabularDataset)
INPUT_TYPE_DICT = {
    TabularDataset: TABULAR_TYPE_INPUT,
    PipelineOutputTabularDataset: TABULAR_TYPE_INPUT,
    FileDataset: FILE_TYPE_INPUT,
    PipelineOutputFileDataset: FILE_TYPE_INPUT,
}
PARALLEL_RUN_FIELD_DEPRECATION_STATEMENT = (
    "The '{}' field has been deprecated, and will be removed when"
    " ParallelRunStep enters General Availability. ")
PARALLEL_RUN_GENERAL_DEPRECATION_STATEMENT = (
    "This package, azureml-contrib-pipeline-steps, has been deprecated and moved to azureml-pipeline-steps."
    " Please update to the new package and read the release notes.")


class ParallelRunStep(_PythonScriptStepBase):
    r"""
    Creates an Azure Machine Learning Pipeline step to process large amounts of data asynchronously and in parallel.

    .. note::

        This package, azureml-contrib-pipeline-steps, has been deprecated and moved to azureml-pipeline-steps.
        Please use the :class:`azureml.pipeline.steps.ParallelRunStep` class from new package.

    For an example of using ParallelRunStep, see the notebook https://aka.ms/batch-inference-notebooks.

    For troubleshooting guide, see https://aka.ms/prstsg. You can find more references there.

    .. remarks::

        The ParallelRunStep class can be used for any kind of processing job that involves large amounts of data and
        is not time-sensitive, such as batch training or batch scoring. The ParallelRunStep works by breaking up a
        large job into batches that are processed in parallel. The batch size and degree of parallel processing can be
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

    :param name: Name of the step. Must be unique to the workspace, only consist of lowercase letters,
        numbers, or dashes, start with a letter, and be between 3 and 32 characters long.
    :type name: str
    :param parallel_run_config: A ParallelRunConfig object used to determine required run properties.
    :type parallel_run_config: azureml.contrib.pipeline.steps.ParallelRunConfig
    :param inputs: List of input datasets. All datasets in the list should be of same type.
    :type inputs: list[azureml.data.dataset_consumption_config.DatasetConsumptionConfig]
    :param output: Output port binding, may be used by later pipeline steps.
    :type output: azureml.pipeline.core.builder.PipelineData, azureml.pipeline.core.graph.OutputPortBinding
    :param side_inputs: List of side input reference data.
    :type side_inputs: list[azureml.pipeline.core.builder.PipelineData]
    :param models: A list of zero or more model objects. This list is used to track pipeline to model version
        mapping only. Models are not copied to container. Use the :meth:`azureml.core.Model.get_model_path` method
        of the Model class to retrieve a model in the init function in entry_script.
    :type models: list[azureml.core.model.Model]
    :param arguments: List of command-line arguments to pass to the Python entry_script.
    :type arguments: list[str]
    :param allow_reuse: Whether the step should reuse previous results when run with the same settings/inputs.
        If this is false, a new run will always be generated for this step during pipeline execution.
    :type allow_reuse: bool
    :param tags: Dictionary of key value tags for this step.
    :type tags: dict[str, str]
    :param properties: Dictionary of key value properties for this step.
    :type properties: dict[str, str]
    :param add_parallel_run_step_dependencies: [Deprecated] Whether to add runtime dependencies for
        :class:`azureml.contrib.pipeline.steps.ParallelRunStep`. These include:

        - azure-storage-queue~=2.1
        - azure-storage-common~=2.1
        - azureml-core~=1.0
        - azureml-telemetry~=1.0
        - filelock~=3.0
        - azureml-dataset-runtime[fuse,pandas]~=1.1
        - psutil

    :type properties: bool
    """

    def __init__(
            self,
            name,
            parallel_run_config,
            inputs,
            output=None,
            side_inputs=None,
            models=None,
            arguments=None,
            allow_reuse=True,
            tags=None,
            properties=None,
            add_parallel_run_step_dependencies=True,
    ):
        r"""Create an Azure ML Pipeline step to process large amounts of data asynchronously and in parallel.

        For an example of using ParallelRunStep, see the notebook link https://aka.ms/batch-inference-notebooks.

        :param name: Name of the step. Must be unique to the workspace, only consist of lowercase letters,
            numbers, or dashes, start with a letter, and be between 3 and 32 characters long.
        :type name: str
        :param parallel_run_config: A ParallelRunConfig object used to determine required run properties.
        :type parallel_run_config: azureml.contrib.pipeline.steps.ParallelRunConfig
        :param inputs: List of input datasets. All datasets in the list should be of same type.
        :type inputs: list[azureml.data.dataset_consumption_config.DatasetConsumptionConfig]
        :param output: Output port binding, may be used by later pipeline steps.
        :type output: azureml.pipeline.core.builder.PipelineData, azureml.pipeline.core.graph.OutputPortBinding
        :param side_inputs: List of side input reference data.
        :type side_inputs: list[azureml.pipeline.core.builder.PipelineData]
        :param models: [Deprecated] A list of zero or more model objects. This list is used to track pipeline to
            model version mapping only. Models are not copied to container. Use the
            :meth:`azureml.core.Model.get_model_path` method of the Model class to retrieve a model in the init
            function in entry_script.
        :type models: list[azureml.core.model.Model]
        :param arguments: List of command-line arguments to pass to the Python entry_script.
        :type arguments: list[str]
        :param allow_reuse: Whether the step should reuse previous results when run with the same settings/inputs.
            If this is false, a new run will always be generated for this step during pipeline execution.
        :type allow_reuse: bool
        :param tags: [Deprecated] Dictionary of key value tags for this step.
        :type tags: dict[str, str]
        :param properties: [Deprecated] Dictionary of key value properties for this step.
        :type properties: dict[str, str]
        :param add_parallel_run_step_dependencies: [Deprecated] Whether to add runtime dependencies for
            :class:`azureml.contrib.pipeline.steps.ParallelRunStep`. These include:

            - azure-storage-queue~=2.1
            - azure-storage-common~=2.1
            - azureml-core~=1.0
            - azureml-telemetry~=1.0
            - filelock~=3.0
            - azureml-dataset-runtime[fuse,pandas]~=1.1
            - psutil

        :type properties: bool
        """
        self._name = name
        self._parallel_run_config = parallel_run_config
        self._inputs = inputs
        self._output = output
        self._side_inputs = side_inputs
        self._arguments = arguments
        self._models = models
        self._node_count = self._parallel_run_config.node_count
        self._process_count_per_node = self._parallel_run_config.process_count_per_node
        self._mini_batch_size = self._parallel_run_config.mini_batch_size
        self._error_threshold = self._parallel_run_config.error_threshold
        self._logging_level = self._parallel_run_config.logging_level
        self._run_invocation_timeout = self._parallel_run_config.run_invocation_timeout
        self._input_compute_target = self._parallel_run_config.compute_target
        self._tags = tags
        self._properties = properties
        self._pystep_inputs = []
        self._input_ds_type = None
        self._glob_syntax_pattern = re.compile(r"[\^\\\$\|\?\*\+\(\)\[\]\{\}]")
        self._module_logger = logging.getLogger(__name__)

        self._validate()
        self._get_pystep_inputs()

        pipeline_runconfig_params = self._get_pipeline_runconfig_params()
        prun_runconfig = self._generate_runconfig(add_parallel_run_step_dependencies)
        prun_main_file_args = self._generate_main_file_args()

        if self._side_inputs:
            self._pystep_inputs += self._side_inputs

        compute_target = self._input_compute_target
        if isinstance(compute_target, str):
            compute_target = (compute_target, AmlCompute._compute_type)

        super(ParallelRunStep, self).__init__(
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

    def _validate(self):
        """Validate input params to init parallel run step class."""
        self._validate_name()
        self._validate_inputs()
        self._validate_output()
        self._validate_parallel_run_config()
        self._validate_source_directory()
        self._validate_entry_script()
        self._warn_deprecated_fields()

    def _warn_deprecated_fields(self):
        """Warn that deprecated field(s) have been used."""
        if self._models is not None:
            warnings.warn(PARALLEL_RUN_FIELD_DEPRECATION_STATEMENT.format("models"), DeprecationWarning)
        if self._tags is not None:
            warnings.warn(PARALLEL_RUN_FIELD_DEPRECATION_STATEMENT.format("tags"), DeprecationWarning)
        if self._properties is not None:
            warnings.warn(PARALLEL_RUN_FIELD_DEPRECATION_STATEMENT.format("properties"), DeprecationWarning)
        warnings.warn(PARALLEL_RUN_GENERAL_DEPRECATION_STATEMENT, DeprecationWarning)

    def _validate_name(self):
        """Validate step name."""
        name_length = len(self._name)
        if name_length < 3 or name_length > 32:
            raise Exception("Step name must have 3-32 characters")

        pattern = re.compile("^[a-z]([-a-z0-9]*[a-z0-9])?$")
        if not pattern.match(self._name):
            raise Exception("Step name must follow regex rule ^[a-z]([-a-z0-9]*[a-z0-9])?$")

    def _validate_inputs(self):
        """Validate all inputs are same type and ensure they meet dataset requirement."""
        def _get_input_type(in_ds):
            input_type = type(in_ds)
            ds_mapping_type = None
            if input_type == DatasetConsumptionConfig:
                # Dataset mode needs to be direct except when we convert it to data reference.
                # This will be removed in next release.
                real_ds_obj = in_ds.dataset
                if isinstance(in_ds.dataset, PipelineParameter):
                    real_ds_obj = in_ds.dataset.default_value
                if isinstance(real_ds_obj, TabularDataset) and in_ds.mode != "direct":
                    raise Exception("Please ensure input dataset consumption mode is direct")
                ds_mapping_type = INPUT_TYPE_DICT[type(real_ds_obj)]
            elif input_type == PipelineOutputFileDataset or input_type == PipelineOutputTabularDataset:
                # Dataset mode needs to be direct except when we convert it to data reference.
                # This will be removed in next release.
                if input_type == PipelineOutputTabularDataset and in_ds._input_mode != "direct":
                    raise Exception("Please ensure pipeline input dataset consumption mode is direct")
                ds_mapping_type = INPUT_TYPE_DICT[input_type]
            else:
                raise Exception(
                    "Step input must be of any type: {}, found {}".format(INPUT_TYPE_DICT.keys(), input_type)
                )
            return ds_mapping_type

        assert isinstance(self._inputs, list) and self._inputs != [], \
            "The parameter 'inputs' must be a list and have at least one element."

        self._input_ds_type = _get_input_type(self._inputs[0])
        for input_ds in self._inputs:
            if self._input_ds_type != _get_input_type(input_ds):
                raise Exception("All inputs of step must be same type")

    def _validate_output(self):
        if self._parallel_run_config.output_action.lower() != "summary_only" and self._output is None:
            raise Exception("Please specify output parameter.")

        if self._output is not None:
            self._output = [self._output]

    def _validate_parallel_run_config(self):
        """Validate parallel run config."""
        if not isinstance(self._parallel_run_config, ParallelRunConfig):
            raise Exception("Param parallel_run_config must be a azureml.core.model.ParallelRunConfig")

        if self._parallel_run_config.mini_batch_size is None:
            if self._input_ds_type == FILE_TYPE_INPUT:
                self._parallel_run_config.mini_batch_size = DEFAULT_MINI_BATCH_SIZE_FILEDATASET
            elif self._input_ds_type == TABULAR_TYPE_INPUT:
                self._parallel_run_config.mini_batch_size = DEFAULT_MINI_BATCH_SIZE_TABULARDATASET

        if not isinstance(self._mini_batch_size, PipelineParameter):
            self._mini_batch_size = PipelineParameter(
                name="aml_mini_batch_size", default_value=self._parallel_run_config.mini_batch_size)

        if not isinstance(self._error_threshold, PipelineParameter):
            self._error_threshold = PipelineParameter(
                name="aml_error_threshold", default_value=self._parallel_run_config.error_threshold)

        if not isinstance(self._logging_level, PipelineParameter):
            self._logging_level = PipelineParameter(
                name="aml_logging_level", default_value=self._parallel_run_config.logging_level)

        if not isinstance(self._run_invocation_timeout, PipelineParameter):
            self._run_invocation_timeout = PipelineParameter(
                name="aml_run_invocation_timeout", default_value=self._parallel_run_config.run_invocation_timeout)

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

    def _get_pystep_inputs(self):
        """Process and convert inputs before adding to pystep_inputs."""
        def _convert_to_mount_mode(in_ds):
            if isinstance(in_ds, PipelineOutputFileDataset):
                if in_ds._input_mode != "mount" or in_ds._input_path_on_compute is None:
                    return in_ds.as_mount(str(uuid.uuid4()))
            elif isinstance(in_ds, DatasetConsumptionConfig):
                if in_ds.mode != "mount" or in_ds.path_on_compute is None:
                    return in_ds.as_mount(str(uuid.uuid4()))
            return in_ds

        def _convert_to_dataref(index, in_ds):
            constructed_df = []
            if isinstance(in_ds, DatasetConsumptionConfig) and not isinstance(in_ds.dataset, PipelineParameter):
                datastores = self._get_datastores_of_dataset(in_ds.dataset)
                # if workspace is available at dataset level then use that instead of constructing it
                # from datastore. Even though one dataset can refer to multiple datastore, all referenced
                # datastore must be from same workspace.
                ds_ws = None
                if in_ds.dataset._registration is not None:
                    ds_ws = in_ds.dataset._registration.workspace
                if datastores is not None:
                    for ds_index, ds in enumerate(datastores):
                        if not ds_ws:
                            ds_ws = Workspace(
                                subscription_id=ds["subscription"],
                                resource_group=ds["resourceGroup"],
                                workspace_name=ds["workspaceName"],
                            )

                        reg_ds = Datastore(ds_ws, name=ds["datastoreName"])

                        # Can only convert datastore if it is blob based and has no glob in path.
                        if not isinstance(reg_ds, AzureBlobDatastore) or self._glob_syntax_pattern.search(ds["path"]):
                            return None

                        mode = "mount" if reg_ds.account_key else "download"
                        if mode == "download":
                            self._module_logger.info(
                                (
                                    "An account key was not provided to the datastore, "
                                    "defaulting to download for {}"
                                ).format(in_ds.name)
                            )
                        input_df = DataReference(
                            datastore=reg_ds,
                            data_reference_name="{0}_{1}".format(in_ds.name, ds_index),
                            path_on_datastore=ds["path"],
                            mode=mode,
                        )
                        constructed_df.append(input_df)
            return constructed_df

        if self._input_ds_type == FILE_TYPE_INPUT:
            for index, input_ds in enumerate(self._inputs):
                mounted_ds = _convert_to_mount_mode(input_ds)
                self._pystep_inputs.append(mounted_ds)
                # Also add DataReferences if Dataset was converted.
                converted_df = _convert_to_dataref(index, input_ds)
                if converted_df:
                    self._pystep_inputs += converted_df
        elif self._input_ds_type == TABULAR_TYPE_INPUT:
            self._pystep_inputs = self._inputs

    def _get_datastores_of_dataset(self, in_ds):
        """Get data stores from file dataset."""
        steps = in_ds._dataflow._get_steps()
        if steps[0].step_type == "Microsoft.DPrep.GetDatastoreFilesBlock":
            return steps[0].arguments["datastores"]
        return None

    def _get_pipeline_runconfig_params(self):
        """
        Generate pipeline parameters for runconfig.

        :return: runconfig pipeline parameters
        :rtype: dict
        """
        prun_runconfig_pipeline_params = {}
        if not isinstance(self._node_count, PipelineParameter):
            self._node_count = PipelineParameter(name="aml_node_count", default_value=self._node_count)
        prun_runconfig_pipeline_params["NodeCount"] = self._node_count
        return prun_runconfig_pipeline_params

    def _generate_runconfig(self, add_parallel_run_step_dependencies):
        """
        Generate runconfig for parallel run step.

        :return: runConfig
        :rtype: RunConfig
        """
        run_config = RunConfiguration()
        run_config.node_count = self._node_count.default_value
        if isinstance(self._input_compute_target, AmlCompute):
            run_config.target = self._input_compute_target
        run_config.framework = "Python"
        # For AmlCompute we need to set run_config.docker.use_docker = True
        run_config.docker.use_docker = True

        run_config.environment = self._parallel_run_config.environment
        if run_config.environment.python.user_managed_dependencies:
            warnings.warn("""
ParallelRunStep will include its dependencies if conda_dependencies is being used.
For user_managed_dependencies, please ensure the following dependencies are installed:
  azure-storage-queue~=2.1
  azure-storage-common~=2.1
  azureml-core~=1.0
  azureml-telemetry~=1.0
  filelock~=3.0
  azureml-dataset-runtime[fuse,pandas]~=1.1
  psutil~=5.0""", UserWarning)

        if run_config.environment.python.conda_dependencies is None and add_parallel_run_step_dependencies:
            run_config.environment.python.conda_dependencies = CondaDependencies.create()

        if add_parallel_run_step_dependencies:
            run_config.environment.python.conda_dependencies.add_pip_package("azure-storage-queue~=2.1")
            run_config.environment.python.conda_dependencies.add_pip_package("azure-storage-common~=2.1")
            run_config.environment.python.conda_dependencies.add_pip_package("azureml-core~=1.0")
            run_config.environment.python.conda_dependencies.add_pip_package("azureml-telemetry~=1.0")
            run_config.environment.python.conda_dependencies.add_pip_package("filelock~=3.0")
            run_config.environment.python.conda_dependencies.add_pip_package("azureml-dataset-runtime[fuse,pandas]\
                ~=1.1")
            run_config.environment.python.conda_dependencies.add_channel("anaconda")
            run_config.environment.python.conda_dependencies.add_conda_package("psutil")

        return run_config

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
            "--input_format",
            self._parallel_run_config.input_format,
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
        ]

        if self._parallel_run_config.output_action.lower() == 'append_row' and \
                self._parallel_run_config.append_row_file_name is not None:
            main_args += ["--append_row_file_name", self._parallel_run_config.append_row_file_name]

        if self._output is not None:
            main_args += ["--output", self._output[0]]

        if self._process_count_per_node is not None:
            if not isinstance(self._process_count_per_node, PipelineParameter):
                self._process_count_per_node = PipelineParameter(
                    name="aml_process_count_per_node", default_value=self._process_count_per_node
                )
            main_args += ["--process_count_per_node", self._process_count_per_node]

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
        model_ids = []
        if self._models and isinstance(self._models, list):
            for model in self._models:
                model_ids.append(model.id)

        batch_inferencing_metadata = {
            "Name": self._name,
            "ComputeName": self._input_compute_target if isinstance(self._input_compute_target, str) else
            self._input_compute_target.name,
            "AppInsightsEnabled": False,
            "EventHubEnabled": False,
            "StorageEnabled": False,
            "EntryScript": self._parallel_run_config.entry_script,
            "NodeCount": self._node_count.default_value,
            "InputFormat": self._parallel_run_config.input_format,
            "MiniBatchSize": self._mini_batch_size.default_value,
            "ErrorThreshold": self._parallel_run_config.error_threshold,
            "OutputAction": self._parallel_run_config.output_action,
            "ModelIds": json.dumps(model_ids),
            "Tags": json.dumps(self._tags),
            "Properties": json.dumps(self._properties),
            "EnvironmentName": self._parallel_run_config.environment.name,
            "EnvironmentVersion": self._parallel_run_config.environment.version,
        }

        if self._process_count_per_node:
            batch_inferencing_metadata["ProcessCountPerNode"] = self._process_count_per_node.default_value

        return json.dumps(batch_inferencing_metadata)

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
        node = super(ParallelRunStep, self).create_node(graph, default_datastore, context)
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

        return super(ParallelRunStep, self).create_module_def(
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
