# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""_pipeline_yaml_parser.py, class for parsing pipeline yaml."""
from azureml.pipeline.core import _yaml_keys
from azureml.pipeline.core.graph import InputPortBinding, PipelineParameter, PipelineDataset
from azureml.pipeline.core.graph import StoredProcedureParameter, StoredProcedureParameterType
from azureml.pipeline.core._data_transfer_step_base import _DataTransferStepBase as DataTransferStep
from azureml.pipeline.core.pipeline_output_dataset import PipelineOutputFileDataset
from azureml.pipeline.core.module import Module
from azureml.pipeline.core.builder import PipelineData
from azureml.core import Datastore, Dataset, RunConfiguration
from azureml.core.model import Model
from azureml.pipeline.core._python_script_step_base import _PythonScriptStepBase as PythonScriptStep
from azureml.pipeline.core._parallel_run_config_base import _ParallelRunConfigBase as ParallelRunConfig
from azureml.pipeline.core._parallel_run_step_base import _ParallelRunStepBase as ParallelRunStep
from azureml.pipeline.core._adla_step_base import _AdlaStepBase as AdlaStep
from azureml.pipeline.core._databricks_step_base import _DatabricksStepBase as DatabricksStep
from azureml.pipeline.core._azurebatch_step_base import _AzureBatchStepBase as AzureBatchStep
from azureml.data.datapath import DataPath, DataPathComputeBinding
from azureml.data.data_reference import DataReference
from azureml.data.sql_data_reference import SqlDataReference
from azureml.pipeline.core.module_step_base import ModuleStepBase
import logging

_ADLA_STEP = 'adla_step'
_ADLA_STEP_TYPE = 'AdlaStep'
_ARGUMENTS = 'arguments'
_ARGUMENT_SIDE_INPUT = 'side_input:'
_ARGUMENT_INPUT = 'input:'
_ARGUMENT_OUTPUT = 'output:'
_ALLOWREUSE = 'allow_reuse'
_AS_DATASET = 'as_dataset'
_AZUREBATCH_STEP = 'azurebatch_step'
_AZUREBATCH_STEP_TYPE = 'AzureBatchStep'
_BOOL = 'bool'
_BOOLEAN_KEYS = "boolean"
_CLUSTER_LOG_DBFS_PATH = 'cluster_log_dbfs_path'
_COMPUTE = 'compute'
_CREATE_POOL = 'create_pool'
_DATABRICKS_STEP = 'databricks_step'
_DATABRICKS_STEP_TYPE = 'DatabricksStep'
_DATAPATH = 'datapath'
_DATASTORE = 'datastore'
_DATA_REFERENCES = 'data_references'
_DATASET_ID = 'dataset_id'
_DATASET_NAME = 'dataset_name'
_DATATRANSFER_STEP = 'data_transfer_step'
_DATATRANSFER_STEP_TYPE = 'DataTransferStep'
_DEFAULT = 'default'
_DEFAULT_COMPUTE = 'default_compute'
_DEGREE_OF_PARALLELISM = 'degree_of_parallelism'
_DELETE_BATCH_JOB_AFTER_FINISH = 'delete_batch_job_after_finish'
_DELETE_BATCH_POOL_AFTER_FINISH = 'delete_batch_pool_after_finish'
_DESCRIPTION = 'description'
_DESTINATION = 'destination'
_DESTINATION_DATA_REFERENCE = 'destination_data_reference'
_DESTINATION_REFERENCE_TYPE = 'destination_reference_type'
_DOWNLOAD = 'download'
_EGGLIBRARY = 'egg_libraries'
_EXISTING_CLUSTER_ID = 'existing_cluster_id'
_PERMIT_CLUSTER_RESTART = 'permit_cluster_restart'
_EXECUTABLE = 'executable'
_FLOAT = 'float'
_HASHPATHS = 'hash_paths'
_ID = 'id'
_INIT_SCRIPTS = 'init_scripts'
_INPUTS = 'inputs'
_INPUT_DATASETS = 'input_datasets'
_INT = 'int'
_INTEGER_KEYS = 'integer'
_INSTANCE_POOL_ID = 'instance_pool_id'
_IS_POSITIVE_EXIT_CODE_FAILURE = 'is_positive_exit_code_failure'
_JAR_PARAMS = 'jar_params'
_JARLIBRARY = 'jar_libraries'
_MIN_WORKERS = 'min_workers'
_MAX_WORKERS = 'max_workers'
_MAIN_CLASS_NAME = 'main_class_name'
_MAVEN_LIBRARIES = 'maven_libabries'
_MODELS_ID = 'models_id'
_MODULE = 'module'
_MODULE_STEP_TYPE = 'ModuleStep'
_MOUNT = 'mount'
_NAME = 'name'
_NODE_TYPE = 'node_type'
_NOTEBOOK_PARAMS = 'notebook_params'
_NOTEBOOK_PATH = 'notebook_path'
_NUM_WORKERS = 'num_workers'
_OUTPUTS = 'outputs'
_OVERWRITE = 'overwrite'
_PARAMETERS = 'parameters'
_PATH_ON_COMPUTE = 'path_on_compute'
_PIPELINE = 'pipeline'
_POOL_ID = 'pool_id'
_PATH_ON_DATASTORE = 'path_on_datastore'
_PRIORITY = 'priority'
_PYPILIBRARY = 'pypi_libraries'
_PYTHON_SCRIPT_NAME = 'python_script_name'
_PYTHON_SCRIPT_PATH = 'python_script_path'
_PYTHON_SCRIPT_PARAMS = 'python_script_params'
_PYTHONSCRIPT_STEP = 'python_script_step'
_PYTHONSCRIPT_STEP_TYPE = 'PythonScriptStep'
_PARALLEL_RUN_CONFIG = 'parallel_run_config'
_PARALLEL_RUN_STEP = 'parallel_run_step'
_PARALLEL_RUN_STEP_TYPE = 'ParallelRunStep'
_RCRANLIBRARY = 'rcran_libabries'
_RUNCONFIG = 'runconfig'
_RUNCONFIG_PARAMETERS = 'runconfig_parameters'
_RUN_NAME = 'run_name'
_RUN_TASK_AS_ADMIN = 'run_task_as_admin'
_RUNTIME_VERSION = 'runtime_version'
_SCRIPT_NAME = 'script_name'
_SIDE_INPUTS = "side_inputs"
_SOURCE = 'source'
_SOURCE_DATA_REFERENCE = 'source_data_reference'
_SOURCE_REFERENCE_TYPE = "source_reference_type"
_SOURCEDIRECTORY = 'source_directory'
_STRING_KEYS = 'string'
_SPARK_CONF = 'spark_conf'
_SPARK_ENV_VARIABLES = 'spark_env_variables'
_SPARK_VERSION = 'spark_version'
_STEPS = 'steps'
_STRING = 'string'
_SQL_TABLE = 'sql_table'
_SQL_QUERY = 'sql_query'
_SQL_STORED_PROCEDURE = 'sql_stored_procedure'
_SQL_STORED_PROCEDURE_PARAMS = 'sql_stored_procedure_params'
_TARGET_COMPUTE_NODES = 'target_compute_nodes'
_TIMEOUT_SECONDS = 'timeout_seconds'
_TYPE = 'type'
_BIND_MODE = 'bind_mode'
_UPLOAD = 'upload'
_VERSION = 'version'
_VALUE = 'value'
_VM_IMAGE_URN = 'vm_image_urn'
_VM_SIZE = 'vm_size'


class _PipelineYamlParser(object):
    """
    A Pipeline Yaml parser, to parse yaml files.
    """

    @staticmethod
    def load_yaml(workspace, filename, _workflow_provider=None, _service_endpoint=None):
        r"""
                Load a Pipeline from the specified Yaml file.
        """
        import azureml._vendor.ruamel.yaml as ruamelyaml
        with open(filename, "r") as input:
            pipeline_yaml = ruamelyaml.round_trip_load(input)

        if _PIPELINE not in pipeline_yaml:
            raise ValueError('Pipeline Yaml file must have a "pipeline:" section')
        pipeline_section = pipeline_yaml[_PIPELINE]

        description = None
        if _NAME in pipeline_section:
            description = pipeline_section[_NAME]
            logging.warning("Pipeline yaml parameter name is being deprecated. "
                            "Use description instead.")

        if _DESCRIPTION in pipeline_section:
            description = pipeline_section[_DESCRIPTION]

        pipeline_parameters = _PipelineYamlParser._get_pipeline_parameters(workspace, pipeline_section)

        default_compute = None
        if _DEFAULT_COMPUTE in pipeline_section:
            default_compute = pipeline_section[_DEFAULT_COMPUTE]

        data_references = _PipelineYamlParser._get_data_references(workspace, pipeline_section)

        step_objects = []
        pipeline_data_objects = {}

        if _STEPS not in pipeline_section:
            raise ValueError('Pipeline Yaml file must have at least one step defined')

        steps_section = pipeline_section[_STEPS]
        for step_name in steps_section:
            step = steps_section[step_name]

            parameter_assignments = {}
            if _PARAMETERS in step:
                parameters_section = step[_PARAMETERS]
                for param_name in parameters_section:
                    current_parameter = parameters_section[param_name]
                    if isinstance(current_parameter, ruamelyaml.comments.CommentedMap) \
                            and _SOURCE in current_parameter:
                        source_name = current_parameter[_SOURCE]
                        if source_name not in pipeline_parameters:
                            raise ValueError(
                                "Parameter %s for step %s is assigned to source %s, which doesn't exist"
                                % (param_name, step_name, source_name))
                        parameter_assignments[param_name] = pipeline_parameters[current_parameter[_SOURCE]]
                    else:
                        parameter_assignments[param_name] = current_parameter

            runconfig_parameter_assignments = {}
            if _RUNCONFIG_PARAMETERS in step:
                parameters_section = step[_RUNCONFIG_PARAMETERS]
                for param_name in parameters_section:
                    current_parameter = parameters_section[param_name]
                    if isinstance(current_parameter, ruamelyaml.comments.CommentedMap) \
                            and _SOURCE in current_parameter:
                        source_name = current_parameter[_SOURCE]
                        if source_name not in pipeline_parameters:
                            raise ValueError(
                                "Runconfig Parameter %s for step %s is assigned to source %s, which doesn't exist"
                                % (param_name, step_name, source_name))
                        runconfig_parameter_assignments[param_name] = pipeline_parameters[current_parameter[_SOURCE]]
                    else:
                        runconfig_parameter_assignments[param_name] = current_parameter

            compute = default_compute
            if _COMPUTE in step:
                compute = step[_COMPUTE]

            runconfig = None
            if _RUNCONFIG in step:
                runconfig_file = step[_RUNCONFIG]
                runconfig = RunConfiguration.load(runconfig_file)

            inputs = {}
            source_data_reference = {}
            destination_data_reference = {}
            if _INPUTS in step:
                inputs = _PipelineYamlParser._get_inputs(
                    step, step_name, _INPUTS, pipeline_parameters, data_references, pipeline_data_objects)
            if _SOURCE_DATA_REFERENCE in step:
                source_data_reference = _PipelineYamlParser._get_inputs(
                    step, step_name, _SOURCE_DATA_REFERENCE, pipeline_parameters,
                    data_references, pipeline_data_objects)
            if _DESTINATION_DATA_REFERENCE in step:
                destination_data_reference = _PipelineYamlParser._get_inputs(
                    step, step_name, _DESTINATION_DATA_REFERENCE, pipeline_parameters,
                    data_references, pipeline_data_objects)

            outputs = {}
            if _OUTPUTS in step:
                outputs_section = step[_OUTPUTS]
                for output_name in outputs_section:
                    output = outputs_section[output_name]
                    if _DESTINATION not in output:
                        raise ValueError('Output %s for step %s must have a destination assignment'
                                         % (output_name, step_name))
                    destination_name = output[_DESTINATION]
                    datastore = None
                    output_mode = _MOUNT
                    path_on_compute = None
                    as_dataset = False
                    overwrite = None
                    if _DATASTORE in output:
                        datastore = Datastore(workspace, output[_DATASTORE])

                    if _AS_DATASET in output:
                        as_dataset = output[_AS_DATASET]

                    if _TYPE in output:
                        output_mode = output[_TYPE]
                        logging.warning("Output yaml parameter type is being deprecated. "
                                        "Use bind_mode instead.")
                    if _BIND_MODE in output:
                        output_mode = output[_BIND_MODE]

                    if output_mode != _MOUNT and output_mode != _UPLOAD:
                        raise ValueError('Output bind_mode/type %s for output %s in step %s must be mount or upload'
                                         % (output_mode, output_name, step_name))
                    if _PATH_ON_COMPUTE in output:
                        path_on_compute = output[_PATH_ON_COMPUTE]
                    if _OVERWRITE in output:
                        overwrite = output[_OVERWRITE]
                    if destination_name in pipeline_data_objects:
                        # Already saw this pipeline data from a step input, need to fix the properties
                        if as_dataset:
                            pipeline_data_objects[destination_name] = PipelineData(
                                name=destination_name, datastore=datastore, output_name=output_name,
                                output_mode=output_mode, output_path_on_compute=path_on_compute,
                                output_overwrite=overwrite).as_dataset()
                        else:
                            pipeline_data_objects[destination_name]._output_name = output_name
                            pipeline_data_objects[destination_name]._datastore = datastore
                            pipeline_data_objects[destination_name]._output_mode = output_mode
                            pipeline_data_objects[destination_name]._output_path_on_compute = path_on_compute
                            pipeline_data_objects[destination_name]._output_overwrite = overwrite
                    else:
                        pipeline_data = PipelineData(
                            name=destination_name, datastore=datastore, output_name=output_name,
                            output_mode=output_mode, output_path_on_compute=path_on_compute,
                            output_overwrite=overwrite)
                        if as_dataset:
                            pipeline_data_objects[destination_name] = pipeline_data.as_dataset()
                        else:
                            pipeline_data_objects[destination_name] = pipeline_data
                    outputs[output_name] = pipeline_data_objects[destination_name]

            side_inputs = {}
            if _SIDE_INPUTS in step:
                side_inputs = _PipelineYamlParser._get_inputs(
                    step, step_name, _SIDE_INPUTS, pipeline_parameters, data_references, pipeline_data_objects)

            arguments = []
            if _ARGUMENTS in step:
                argument_section = step[_ARGUMENTS]
                if isinstance(argument_section, ruamelyaml.comments.CommentedSeq):
                    argument_section = list(argument_section)
                arguments = argument_section

            resolved_arguments = []
            for arg in arguments:
                if arg.startswith(_ARGUMENT_INPUT):
                    input_name = arg.split(_ARGUMENT_INPUT)[1]
                    if input_name in inputs.keys():
                        resolved_arguments.append(inputs[input_name])
                    else:
                        resolved_arguments.append(arg)
                elif arg.startswith(_ARGUMENT_SIDE_INPUT):
                    input_name = arg.split(_ARGUMENT_SIDE_INPUT)[1]
                    if input_name in side_inputs.keys():
                        resolved_arguments.append("{}".format(side_inputs[input_name]))
                    else:
                        resolved_arguments.append(arg)
                elif arg.startswith(_ARGUMENT_OUTPUT):
                    output_name = arg.split(_ARGUMENT_OUTPUT)[1]
                    if output_name in outputs.keys():
                        resolved_arguments.append(outputs[output_name])
                    else:
                        resolved_arguments.append(arg)
                else:
                    resolved_arguments.append(arg)

            step_type_enabled = False
            step_type = None
            if _TYPE in step:
                step_type = step.get(_TYPE, default=_MODULE)
                if step_type and not isinstance(step_type, str):
                    raise ValueError('step_type for step %s must be a string' % step_name)
                step_type_enabled = True

            step_object = None
            if _MODULE_STEP_TYPE == step_type or _MODULE in step:
                if step_type_enabled:
                    module_section = step
                else:
                    module_section = step[_MODULE]
                    logging.warning("module is being deprecated. "
                                    "Use 'type' instead.")

                if _ID not in module_section and _NAME not in module_section:
                    raise ValueError('Step %s does not contain a '
                                     'module ID or name (one must be specified)' % step_name)
                module_id = module_section.get(_ID, default=None)
                if module_id and not isinstance(module_id, str):
                    raise ValueError('Module ID for step %s must be a string' % step_name)
                module_name = module_section.get(_NAME, default=None)
                if module_name and not isinstance(module_name, str):
                    raise ValueError('Module name for step %s must be a string' % step_name)

                module_version = module_section.get(_VERSION, default=None)
                if module_version and not isinstance(module_version, str):
                    raise ValueError('Module version for step %s must be a string' % step_name)

                module = Module.get(workspace, module_id=module_id, name=module_name,
                                    _workflow_provider=_workflow_provider)

                step_object = ModuleStepBase(module=module, version=module_version,
                                             inputs_map=inputs, outputs_map=outputs,
                                             compute_target=compute, runconfig=runconfig,
                                             runconfig_pipeline_params=runconfig_parameter_assignments,
                                             arguments=resolved_arguments, params=parameter_assignments,
                                             name=step_name, _workflow_provider=_workflow_provider)

            if _PYTHONSCRIPT_STEP_TYPE == step_type or _PYTHONSCRIPT_STEP in step:
                input_list = list(inputs.values())
                output_list = list(outputs.values())

                common_parameters = _PipelineYamlParser._get_step_parameters(step, _PYTHONSCRIPT_STEP,
                                                                             step_type_enabled)

                step_object = PythonScriptStep(script_name=common_parameters[_SCRIPT_NAME],
                                               name=common_parameters[_NAME],
                                               arguments=resolved_arguments,
                                               compute_target=compute, runconfig=runconfig,
                                               runconfig_pipeline_params=runconfig_parameter_assignments,
                                               inputs=input_list, outputs=output_list, params=parameter_assignments,
                                               source_directory=common_parameters[_SOURCEDIRECTORY],
                                               allow_reuse=common_parameters[_ALLOWREUSE],
                                               version=common_parameters[_VERSION],
                                               hash_paths=common_parameters[_HASHPATHS])

            if _PARALLEL_RUN_STEP_TYPE == step_type or _PARALLEL_RUN_STEP in step:
                side_input_list = list(side_inputs.values())
                output_list = list(outputs.values())
                input_list = []
                for input_ds_name in inputs.keys():
                    if isinstance(inputs[input_ds_name].bind_object, PipelineOutputFileDataset):
                        input_ds = inputs[input_ds_name].bind_object.as_named_input(input_ds_name)
                    else:
                        input_ds = inputs[input_ds_name].bind_object.dataset.as_named_input(input_ds_name)
                    input_list.append(input_ds)

                parallel_run_config = None
                if _PARALLEL_RUN_CONFIG in step:
                    runconfig_file = step[_PARALLEL_RUN_CONFIG]
                    parallel_run_config = ParallelRunConfig.load_yaml(workspace, runconfig_file)

                model_list = []
                if _MODELS_ID in step:
                    for model_id in step[_MODELS_ID]:
                        model = Model(workspace, id=model_id)
                        model_list.append(model)

                common_parameters = _PipelineYamlParser._get_step_parameters(step, _PARALLEL_RUN_STEP,
                                                                             step_type_enabled)

                step_object = ParallelRunStep(name=common_parameters[_NAME],
                                              arguments=resolved_arguments,
                                              parallel_run_config=parallel_run_config,
                                              inputs=input_list,
                                              output=output_list[0],
                                              side_inputs=side_input_list,
                                              allow_reuse=common_parameters[_ALLOWREUSE])

            if _ADLA_STEP_TYPE == step_type or _ADLA_STEP in step:
                input_list = list(inputs.values())
                output_list = list(outputs.values())

                common_parameters = _PipelineYamlParser._get_step_parameters(step, _ADLA_STEP, step_type_enabled)

                step_object = AdlaStep(script_name=common_parameters[_SCRIPT_NAME], name=common_parameters[_NAME],
                                       compute_target=compute,
                                       inputs=input_list, outputs=output_list,
                                       params=parameter_assignments,
                                       degree_of_parallelism=common_parameters[_DEGREE_OF_PARALLELISM],
                                       priority=common_parameters[_PRIORITY],
                                       runtime_version=common_parameters[_RUNTIME_VERSION],
                                       source_directory=common_parameters[_SOURCEDIRECTORY],
                                       hash_paths=common_parameters[_HASHPATHS],
                                       allow_reuse=common_parameters[_ALLOWREUSE],
                                       version=common_parameters[_VERSION])

            if _DATATRANSFER_STEP_TYPE == step_type or _DATATRANSFER_STEP in step:
                common_parameters = _PipelineYamlParser._get_step_parameters(step, _DATATRANSFER_STEP,
                                                                             step_type_enabled)
                datatransfer_parameters = _PipelineYamlParser._get_datatransferstep_parameters(step)
                step_object = DataTransferStep(
                    name=common_parameters[_NAME],
                    source_data_reference=next(iter(source_data_reference.values())),
                    destination_data_reference=next(iter(destination_data_reference.values())),
                    source_reference_type=datatransfer_parameters[_SOURCE_REFERENCE_TYPE],
                    destination_reference_type=datatransfer_parameters[_DESTINATION_REFERENCE_TYPE],
                    compute_target=compute,
                    allow_reuse=common_parameters[_ALLOWREUSE])

            if _DATABRICKS_STEP_TYPE == step_type or _DATABRICKS_STEP in step:
                input_list = list(inputs.values())
                output_list = list(outputs.values())

                common_parameters = _PipelineYamlParser._get_step_parameters(step, _DATABRICKS_STEP,
                                                                             step_type_enabled)
                databrick_parameters = _PipelineYamlParser._get_databrickstep_parameter(step)

                step_object = DatabricksStep(
                    name=common_parameters[_NAME],
                    inputs=input_list,
                    outputs=output_list,
                    existing_cluster_id=databrick_parameters[_EXISTING_CLUSTER_ID],
                    permit_cluster_restart=databrick_parameters[_PERMIT_CLUSTER_RESTART],
                    spark_version=databrick_parameters[_SPARK_VERSION],
                    node_type=databrick_parameters[_NODE_TYPE],
                    instance_pool_id=databrick_parameters[_INSTANCE_POOL_ID],
                    num_workers=databrick_parameters[_NUM_WORKERS],
                    min_workers=databrick_parameters[_MIN_WORKERS],
                    max_workers=databrick_parameters[_MAX_WORKERS],
                    spark_env_variables=databrick_parameters[_SPARK_ENV_VARIABLES],
                    spark_conf=databrick_parameters[_SPARK_CONF],
                    init_scripts=databrick_parameters[_INIT_SCRIPTS],
                    cluster_log_dbfs_path=databrick_parameters[_CLUSTER_LOG_DBFS_PATH],
                    notebook_path=databrick_parameters[_NOTEBOOK_PATH],
                    notebook_params=databrick_parameters[_NOTEBOOK_PARAMS],
                    python_script_path=databrick_parameters[_PYTHON_SCRIPT_PATH],
                    python_script_params=databrick_parameters[_PYTHON_SCRIPT_PARAMS],
                    main_class_name=databrick_parameters[_MAIN_CLASS_NAME],
                    jar_params=databrick_parameters[_JAR_PARAMS],
                    python_script_name=databrick_parameters[_PYTHON_SCRIPT_NAME],
                    source_directory=common_parameters[_SOURCEDIRECTORY],
                    hash_paths=common_parameters[_HASHPATHS],
                    run_name=databrick_parameters[_RUN_NAME],
                    timeout_seconds=databrick_parameters[_TIMEOUT_SECONDS],
                    runconfig=runconfig,
                    compute_target=compute,
                    allow_reuse=common_parameters[_ALLOWREUSE],
                    version=common_parameters[_VERSION])

            if _AZUREBATCH_STEP_TYPE == step_type or _AZUREBATCH_STEP in step:
                input_list = list(inputs.values())
                output_list = list(outputs.values())
                common_parameters = _PipelineYamlParser._get_step_parameters(step, _AZUREBATCH_STEP, step_type_enabled)
                azurestep_parameters = _PipelineYamlParser._get_azurestep_parameters(step)
                step_object = AzureBatchStep(
                    name=common_parameters[_NAME],
                    inputs=input_list,
                    outputs=output_list,
                    create_pool=azurestep_parameters[_CREATE_POOL],
                    arguments=resolved_arguments,
                    pool_id=azurestep_parameters[_POOL_ID],
                    delete_batch_job_after_finish=azurestep_parameters[_DELETE_BATCH_JOB_AFTER_FINISH],
                    delete_batch_pool_after_finish=azurestep_parameters[_DELETE_BATCH_POOL_AFTER_FINISH],
                    is_positive_exit_code_failure=azurestep_parameters[_IS_POSITIVE_EXIT_CODE_FAILURE],
                    run_task_as_admin=azurestep_parameters[_RUN_TASK_AS_ADMIN],
                    target_compute_nodes=azurestep_parameters[_TARGET_COMPUTE_NODES],
                    vm_size=azurestep_parameters[_VM_SIZE],
                    source_directory=common_parameters[_SOURCEDIRECTORY],
                    executable=azurestep_parameters[_EXECUTABLE],
                    compute_target=compute,
                    allow_reuse=common_parameters[_ALLOWREUSE])

            step_objects.append(step_object)

        return step_objects, description

    @staticmethod
    def _get_inputs(step, step_name, input_type, pipeline_parameters, data_references, pipeline_data_objects):
        inputs = {}
        inputs_section = step[input_type]
        for input_name in inputs_section:
            input = inputs_section[input_name]
            if _SOURCE not in input:
                raise ValueError('Input %s for step %s must have a source assignment'
                                 % (input_name, step_name))
            source_name = input[_SOURCE]
            input_mode = _MOUNT
            path_on_compute = None
            overwrite = None

            if _TYPE in input:
                input_mode = input[_TYPE]
                logging.warning("Input yaml parameter type is being deprecated. "
                                "Use bind_mode instead.")
            if _BIND_MODE in input:
                input_mode = input[_BIND_MODE]

            if input_mode != _MOUNT and input_mode != _DOWNLOAD:
                raise ValueError('Input bind_mode/type %s for input %s in step %s must be mount or download'
                                 % (input_mode, input_name, step_name))
            if _PATH_ON_COMPUTE in input:
                path_on_compute = input[_PATH_ON_COMPUTE]
            if _OVERWRITE in input:
                overwrite = input[_OVERWRITE]
            if source_name in pipeline_parameters and \
                    isinstance(pipeline_parameters[source_name].default_value, DataPath):
                data_binding = DataPathComputeBinding(mode=input_mode, path_on_compute=path_on_compute,
                                                      overwrite=overwrite)
                inputs[input_name] = (pipeline_parameters[source_name], data_binding)
            else:
                if source_name in data_references:
                    input_source_object = data_references[source_name]
                else:
                    if source_name not in pipeline_data_objects:
                        pipeline_data_objects[source_name] = PipelineData(name=source_name)
                    input_source_object = pipeline_data_objects[source_name]
                input_binding = InputPortBinding(name=input_name, bind_object=input_source_object,
                                                 bind_mode=input_mode, path_on_compute=path_on_compute,
                                                 overwrite=overwrite)
                inputs[input_name] = input_binding
        return inputs

    @staticmethod
    def _get_step_parameters(step, step_type, step_type_enable):

        if step_type_enable:
            step_section = step
        else:
            step_section = step[step_type]
            logging.warning("%s is being deprecated. "
                            "Use type instead." % step_type)
        common_parameters = {}
        if step_type in [_ADLA_STEP, _PYTHONSCRIPT_STEP]:
            if _SCRIPT_NAME not in step_section:
                raise ValueError('Step %s does not contain a script name ' % step_type)
            script_name = _PipelineYamlParser._get_string_value(step_section, _SCRIPT_NAME, step_type)
            common_parameters[_SCRIPT_NAME] = script_name

        step_name = _PipelineYamlParser._get_string_value(step_section, _NAME, step_type)
        common_parameters[_NAME] = step_name

        step_version = _PipelineYamlParser._get_string_value(step_section, _VERSION, step_type)
        common_parameters[_VERSION] = step_version

        runtime_version = _PipelineYamlParser._get_string_value(step_section, _RUNTIME_VERSION, step_type)
        common_parameters[_RUNTIME_VERSION] = runtime_version

        priority = _PipelineYamlParser._get_int_value(step_section, _PRIORITY, step_type)
        common_parameters[_PRIORITY] = priority

        degree_of_parallelism = _PipelineYamlParser._get_int_value(step_section, _DEGREE_OF_PARALLELISM, step_type)
        common_parameters[_DEGREE_OF_PARALLELISM] = degree_of_parallelism

        source_directory = _PipelineYamlParser._get_string_value(step_section, _SOURCEDIRECTORY, step_type)
        common_parameters[_SOURCEDIRECTORY] = source_directory

        allow_reuse = True
        if _ALLOWREUSE in step_section:
            allow_reuse = step_section.get(_ALLOWREUSE, default=None)
            if allow_reuse and not isinstance(allow_reuse, bool):
                raise ValueError('allow_reuse for step %s must be a bool' % step_type)
        common_parameters[_ALLOWREUSE] = allow_reuse

        hash_paths_list = None
        if _HASHPATHS in step_section:
            hash_paths = step_section.get(_HASHPATHS, default=None)
            hash_paths_list = list(hash_paths)
        common_parameters[_HASHPATHS] = hash_paths_list

        return common_parameters

    @staticmethod
    def _get_string_value(step_section, key_name, step_type):
        yaml_value = None
        if key_name in step_section:
            yaml_value = step_section.get(key_name)
            if yaml_value and not isinstance(yaml_value, str):
                raise ValueError('%s for step %s must be a string' % (key_name, step_type))
        return yaml_value

    @staticmethod
    def _get_int_value(step_section, key_name, step_type):
        yaml_value = None
        if key_name in step_section:
            yaml_value = step_section.get(key_name)
            if yaml_value and not isinstance(yaml_value, int):
                raise ValueError('%s for step %s must be a integer' % (key_name, step_type))
        return yaml_value

    @staticmethod
    def _get_list_value(step_section, key_name):
        yaml_value = None
        if key_name in step_section:
            yaml_value_list = step_section.get(key_name)
            yaml_value = list(yaml_value_list)
        return yaml_value

    @staticmethod
    def _get_dict_value(step_section, key_name):
        yaml_value = None
        if key_name in step_section:
            yaml_value_list = step_section.get(key_name)
            yaml_value = dict(yaml_value_list)
        return yaml_value

    @staticmethod
    def _get_datatransferstep_parameters(step):
        step_type = _DATATRANSFER_STEP

        step_section = step
        datatransferstep_param = {}

        source_reference_type = _PipelineYamlParser._get_string_value(step_section, _SOURCE_REFERENCE_TYPE, step_type)
        datatransferstep_param[_SOURCE_REFERENCE_TYPE] = source_reference_type

        destination_reference_type = _PipelineYamlParser._get_string_value(
            step_section, _DESTINATION_REFERENCE_TYPE, step_type)
        datatransferstep_param[_DESTINATION_REFERENCE_TYPE] = destination_reference_type

        return datatransferstep_param

    @staticmethod
    def _get_azurestep_parameters(step):
        step_section = step

        azurestep_parameters = {}
        azurestep_parameters.update(_PipelineYamlParser._get_check_yaml_keys(
            step_section, _AZUREBATCH_STEP, _STRING_KEYS, _yaml_keys.AzurebatchStepYamlKeys.get(_STRING_KEYS)))
        azurestep_parameters.update(_PipelineYamlParser._get_check_yaml_keys(
            step_section, _AZUREBATCH_STEP, _BOOLEAN_KEYS, _yaml_keys.AzurebatchStepYamlKeys.get(_BOOLEAN_KEYS)))
        return azurestep_parameters

    @staticmethod
    def _get_databrickstep_parameter(step):
        step_section = step
        databrick_parameters = {}
        databrick_parameters.update(_PipelineYamlParser._get_check_yaml_keys(
            step_section, _DATABRICKS_STEP, _STRING_KEYS, _yaml_keys.DatabrickStepYamlKeys.get(_STRING_KEYS)))
        databrick_parameters.update(_PipelineYamlParser._get_check_yaml_keys(
            step_section, _DATABRICKS_STEP, _INTEGER_KEYS, _yaml_keys.DatabrickStepYamlKeys.get(_INTEGER_KEYS)))

        spark_env_variables_dict = _PipelineYamlParser._get_dict_value(step_section, _SPARK_ENV_VARIABLES)
        databrick_parameters[_SPARK_ENV_VARIABLES] = spark_env_variables_dict

        spark_conf_dict = _PipelineYamlParser._get_dict_value(step_section, _SPARK_CONF)
        databrick_parameters[_SPARK_CONF] = spark_conf_dict

        init_scripts = _PipelineYamlParser._get_list_value(step_section, _INIT_SCRIPTS)
        databrick_parameters[_INIT_SCRIPTS] = init_scripts

        notebook_params_dict = _PipelineYamlParser._get_dict_value(step_section, _NOTEBOOK_PARAMS)
        databrick_parameters[_NOTEBOOK_PARAMS] = notebook_params_dict

        python_script_params_list = _PipelineYamlParser._get_list_value(step_section, _PYTHON_SCRIPT_PARAMS)
        databrick_parameters[_PYTHON_SCRIPT_PARAMS] = python_script_params_list

        jar_params_list = _PipelineYamlParser._get_list_value(step_section, _JAR_PARAMS)
        databrick_parameters[_JAR_PARAMS] = jar_params_list

        if _MAVEN_LIBRARIES in step_section or _PYPILIBRARY in step_section or _EGGLIBRARY in step_section \
                or _JARLIBRARY in step_section or _RCRANLIBRARY in step_section:
            raise ValueError('Yaml support is not implemented')
        return databrick_parameters

    @staticmethod
    def _get_check_yaml_keys(step_section, step_type, keys_type, yaml_keys):
        databrick_parameters = {}
        for key in yaml_keys:
            value = None
            if key in step_section:
                value = step_section.get(key)
                if keys_type == 'string':
                    if value and not isinstance(value, str):
                        raise ValueError('%s for step: %s must be a string' % (key, step_type))
                if keys_type == 'integer':
                    if value and not isinstance(value, int):
                        raise ValueError('%s for step: %s must be a integer' % (key, step_type))
                if keys_type == 'boolean':
                    if value and not isinstance(value, bool):
                        raise ValueError('%s for step: %s must be a boolean' % (key, step_type))

            databrick_parameters[key] = value
        return databrick_parameters

    @staticmethod
    def _get_pipeline_parameters(workspace, pipeline_section):
        pipeline_parameters = {}
        if _PARAMETERS in pipeline_section:
            parameters_section = pipeline_section[_PARAMETERS]
            if parameters_section is not None:
                for parameter_name in parameters_section:
                    current_parameter_section = parameters_section[parameter_name]
                    if _TYPE not in current_parameter_section:
                        raise ValueError('Parameter %s must specify a type of string, int, float, bool, or datapath'
                                         % parameter_name)
                    if _TYPE in current_parameter_section:
                        type = current_parameter_section[_TYPE]
                        default_value = None
                        if type == _STRING:
                            if _DEFAULT in current_parameter_section:
                                default_value = str(current_parameter_section[_DEFAULT])
                        elif type == _INT:
                            if _DEFAULT in current_parameter_section:
                                default_value = int(current_parameter_section[_DEFAULT])
                            else:
                                default_value = 0
                        elif type == _FLOAT:
                            if _DEFAULT in current_parameter_section:
                                default_value = float(current_parameter_section[_DEFAULT])
                            else:
                                default_value = 0.0
                        elif type == _BOOL:
                            if _DEFAULT in current_parameter_section:
                                default_value = bool(current_parameter_section[_DEFAULT])
                            else:
                                default_value = False
                        elif type == _DATAPATH:
                            if _DEFAULT in current_parameter_section:
                                default_section = current_parameter_section[_DEFAULT]
                                if _DATASTORE not in default_section or _PATH_ON_DATASTORE not in default_section:
                                    raise ValueError(
                                        "Default value for datapath parameter %s must specify "
                                        "datastore and path_on_datastore"
                                        % parameter_name)
                                datastore = Datastore(workspace, default_section[_DATASTORE])
                                name = None
                                if _NAME in default_section:
                                    name = default_section[_NAME]
                                default_value = DataPath(datastore=datastore,
                                                         path_on_datastore=default_section[_PATH_ON_DATASTORE],
                                                         name=name)
                        else:
                            raise ValueError("Parameter type %s currently unsupported" % type)
                        pipeline_parameter_object = PipelineParameter(name=parameter_name, default_value=default_value)
                        pipeline_parameters[parameter_name] = pipeline_parameter_object
        return pipeline_parameters

    @staticmethod
    def _get_data_references(workspace, pipeline_section):
        data_references = {}
        if _DATA_REFERENCES in pipeline_section:
            dataref_section = pipeline_section[_DATA_REFERENCES]
            for dataref_name in dataref_section:
                dataref = dataref_section[dataref_name]
                if _DATASTORE in dataref:
                    datastore = Datastore(workspace, dataref[_DATASTORE])
                    if _PATH_ON_DATASTORE in dataref:
                        dataref_object = DataReference(datastore=datastore, data_reference_name=dataref_name,
                                                       path_on_datastore=dataref[_PATH_ON_DATASTORE])
                        data_references[dataref_name] = dataref_object
                    elif _SQL_TABLE in dataref or _SQL_QUERY in dataref or _SQL_STORED_PROCEDURE in dataref or \
                            _SQL_STORED_PROCEDURE_PARAMS in dataref:
                        sql_table = None
                        sql_query = None
                        sql_stored_procedure = None
                        sql_stored_procedure_params = []

                        if _SQL_TABLE in dataref:
                            sql_table = dataref[_SQL_TABLE]
                        if _SQL_QUERY in dataref:
                            sql_query = dataref[_SQL_QUERY]
                        if _SQL_STORED_PROCEDURE in dataref:
                            sql_stored_procedure = dataref[_SQL_STORED_PROCEDURE]

                        if _SQL_STORED_PROCEDURE_PARAMS in dataref:
                            procedure_params_section = dataref[_SQL_STORED_PROCEDURE_PARAMS]
                            for param_name in procedure_params_section:
                                param_section = procedure_params_section[param_name]
                                if _VALUE not in param_section:
                                    raise ValueError('Sql Parameter %s does not contain a "value:" '
                                                     'definition' % param_name)
                                param_value = param_section[_VALUE]
                                param_type = None
                                if _TYPE in param_section:
                                    param_type = StoredProcedureParameterType(param_section[_TYPE])

                                param = StoredProcedureParameter(name=param_name, value=param_value, type=param_type)
                                sql_stored_procedure_params.append(param)

                        sql_dataref = SqlDataReference(datastore=datastore, data_reference_name=dataref_name,
                                                       sql_table=sql_table, sql_query=sql_query,
                                                       sql_stored_procedure=sql_stored_procedure,
                                                       sql_stored_procedure_params=sql_stored_procedure_params)
                        data_references[dataref_name] = sql_dataref
                    else:
                        raise ValueError('Unrecognized data reference type for data reference', dataref_name)
                elif _DATASET_ID in dataref or _DATASET_NAME in dataref:
                    dataset_id = None
                    dataset_name = None

                    if _DATASET_ID in dataref:
                        dataset_id = dataref[_DATASET_ID]
                    if _DATASET_NAME in dataref:
                        dataset_name = dataref[_DATASET_NAME]

                    if dataset_name:
                        dataset = Dataset.get_by_name(workspace=workspace, name=dataset_name)
                    elif dataset_id:
                        dataset = Dataset.get_by_id(workspace=workspace, id=dataset_id)
                    else:
                        raise ValueError('You must either provide a dataset name or a dataset ID.')
                    data_references[dataref_name] = PipelineDataset.create(
                        dataset.as_named_input(dataref_name).as_mount())
                else:
                    raise ValueError('Unrecognized data reference type for data reference', dataref_name)
        return data_references
