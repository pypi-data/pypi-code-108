# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from os import path
import logging
import copy

from azureml.data.dataset_consumption_config import DatasetConsumptionConfig
from azureml.core.workspace import WORKSPACE_DEFAULT_BLOB_STORE_NAME
from azureml.core.runconfig import DEFAULT_GPU_IMAGE, DEFAULT_CPU_IMAGE, MpiConfiguration, RunConfiguration, \
    ParallelTaskConfiguration, Data, OutputData, DockerConfiguration
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.compute import AmlCompute, HDInsightCompute, KubernetesCompute
from azureml.data.datapath import DataPathComputeBinding, DataPath
from azureml.data.output_dataset_config import OutputDatasetConfig
from azureml.exceptions import ComputeTargetException, UserErrorException, TrainingException
from azureml._base_sdk_common.utils import convert_dict_to_list, merge_list, \
    list_remove_empty_items
from azureml.data.data_reference import DataReference
from azureml.data.azure_storage_datastore import AbstractAzureStorageDatastore
from azureml.data.constants import _DATASET_ARGUMENT_TEMPLATE, _DATASET_OUTPUT_ARGUMENT_TEMPLATE
from azureml.train._distributed_training import _DistributedTraining, Mpi, ParameterServer
from azureml._project.project_manager import _get_tagged_image


module_logger = logging.getLogger(__name__)

OPENMPI_CPU_IMAGE = _get_tagged_image("mcr.microsoft.com/azureml/openmpi3.1.2-ubuntu16.04")
OPENMPI_GPU_IMAGE = _get_tagged_image("mcr.microsoft.com/azureml/openmpi3.1.2-cuda10.0-cudnn7-ubuntu16.04")


def _estimator_submit_method(estimator, workspace, experiment_name, **kwargs):
    """
    Submit an experiment using a generic estimator.

    :param estimator: The estimator object.
    :type estimator: azureml.train.estimator.Estimator
    :param workspace: The workspace object.
    :type workspace: azureml.core.workspace.Workspace
    :param experiment_name: The name of the experiment.
    :type experiment_name: str
    :param kwargs: Additional parameters used to override estimator properties.
    :return: A ScriptRun object which can be queried for status, output path, model path, etc.
    :rtype: azureml.core.script_run.ScriptRun
    """
    override_params = False
    if kwargs:
        unexpected_params = set(kwargs.keys()) - set(["script_params", "inputs", "source_directory_data_store"])
        if unexpected_params:
            raise TrainingException("{} parameters cannot be overridden. Allowed parameters are: script_params, "
                                    "inputs and source_directory_data_store.".format(list(unexpected_params)))
        override_params = True

    script_params = kwargs.get("script_params", None)
    inputs = kwargs.get("inputs", None)
    source_directory_data_store = kwargs.get("source_directory_data_store", None)
    if source_directory_data_store is None \
            and estimator._estimator_config.source_directory_data_store is None \
            and estimator._estimator_config.node_count > 1:
        # Try to use the workspace blob store as source directory store if we're multinode
        source_directory_data_store = workspace.datastores.get(WORKSPACE_DEFAULT_BLOB_STORE_NAME, None)
        if source_directory_data_store:
            override_params = True

    # TODO: Throw error if unexpected param?

    if override_params:
        estimator._original_config = copy.deepcopy(estimator._estimator_config)
        estimator._override_params(
            script_params=script_params,
            inputs=inputs,
            source_directory_data_store=source_directory_data_store)

    experiment_run = estimator._fit(workspace, experiment_name)

    if override_params:
        estimator._estimator_config = estimator._original_config

    return experiment_run


def _init_run_config(estimator, source_directory, compute_target, vm_size=None, vm_priority=None, entry_script=None,
                     script_params=None, node_count=1, process_count_per_node=1, distributed_backend=None,
                     distributed_training=None, use_gpu=None, use_docker=None, custom_docker_base_image=None,
                     custom_docker_image=None, image_registry_details=None, user_managed=False, conda_packages=None,
                     pip_packages=None, conda_dependencies_file_path=None, pip_requirements_file_path=None,
                     conda_dependencies_file=None, pip_requirements_file=None,
                     environment_variables=None, environment_definition=None, inputs=None,
                     source_directory_data_store=None, shm_size=None, resume_from=None, max_run_duration_seconds=None):

    _validate_run_config_parameters(estimator, compute_target, vm_size, node_count, process_count_per_node,
                                    distributed_backend, distributed_training, use_gpu, use_docker,
                                    custom_docker_base_image, custom_docker_image, image_registry_details,
                                    user_managed, conda_packages, pip_packages, conda_dependencies_file_path,
                                    pip_requirements_file_path, conda_dependencies_file, pip_requirements_file,
                                    environment_variables, environment_definition, shm_size)

    if conda_dependencies_file_path and (not conda_dependencies_file):
        conda_dependencies_file = conda_dependencies_file_path

    if pip_requirements_file_path and (not pip_requirements_file):
        pip_requirements_file = pip_requirements_file_path

    if not source_directory:
        source_directory = "."

    if resume_from:
        if not isinstance(resume_from, DataPath):
            raise UserErrorException("resume_from parameter should be of type DataPath. "
                                     "Found {}.".format(type(resume_from)))
        outputs_data_reference = resume_from. \
            create_data_reference(data_reference_name="MODEL_LOCATION",
                                  datapath_compute_binding=DataPathComputeBinding(mode="mount"))
        if not script_params:
            script_params = dict()
        script_params["--resume-from"] = outputs_data_reference

    arguments = _get_arguments(script_params)
    estimator_config = RunConfiguration(script=entry_script, arguments=arguments)

    # 1) data references and datasets...
    data_reference_inputs, dataset_inputs = _get_data_inputs(script_params)
    outputs = _get_outputs(script_params)
    data_references, data = _get_data_configuration(inputs, data_reference_inputs, dataset_inputs,
                                                    source_directory_data_store)
    estimator_config.data = data
    estimator_config.data_references = data_references
    estimator_config.output_data = (estimator_config.output_data or {})
    estimator_config.output_data.update(outputs)

    # 2) distributed training...
    estimator_config.node_count = node_count
    estimator_config.framework = "Python"

    if distributed_backend and distributed_backend.lower() == "mpi":
        estimator_config.communicator = "IntelMpi"
        estimator_config.mpi.process_count_per_node = process_count_per_node

    if distributed_training and isinstance(distributed_training, MpiConfiguration):
        estimator_config.communicator = "IntelMpi"
        estimator_config.mpi = distributed_training

    if distributed_training and isinstance(distributed_training, ParallelTaskConfiguration):
        estimator_config.communicator = "ParallelTask"
        estimator_config.paralleltask = distributed_training

    if distributed_training and isinstance(distributed_training, _DistributedTraining):
        estimator_config.communicator = distributed_training._get_communicator()
        estimator_config.framework = distributed_training._get_framework()

        if isinstance(distributed_training, Mpi):
            estimator_config.mpi = distributed_training._get_configuration()

        if isinstance(distributed_training, ParameterServer):
            estimator_config.tensorflow = distributed_training._get_configuration()

    # 3) compute target...
    estimator_config.amlcompute.vm_size = vm_size
    estimator_config.amlcompute.vm_priority = vm_priority
    estimator_config.amlcompute._cluster_max_node_count = node_count
    estimator_config.target = compute_target if compute_target else "amlcompute"

    if not custom_docker_image:
        custom_docker_image = custom_docker_base_image

    # 4) environment...
    if environment_definition:
        estimator_config.environment = environment_definition
        if environment_definition.docker:
            # Docker configuration in run config is higher priority than docker settings
            # in environment docker section, explicitly assign the setting values here
            # to keep backward compatibility.
            estimator_config.docker = DockerConfiguration(
                use_docker=environment_definition.docker._enabled,
                shm_size=environment_definition.docker._shm_size,
                shared_volumes=environment_definition.docker._shared_volumes,
                arguments=environment_definition.docker._arguments)
    else:
        conda_dependencies = _create_conda_dependencies(pip_packages, conda_packages, pip_requirements_file,
                                                        conda_dependencies_file, source_directory)
        estimator_config.docker = DockerConfiguration(
            use_docker=use_docker,
            shm_size=shm_size)

        _update_environment(environment=estimator_config.environment,
                            use_gpu=use_gpu,
                            custom_docker_image=custom_docker_image,
                            image_registry_details=image_registry_details,
                            user_managed=user_managed,
                            conda_dependencies=conda_dependencies)

    estimator_config.environment_variables = environment_variables

    # throw TrainingException if using KubernetesCompute and docker is not enabled
    if estimator_config.environment.docker.enabled is False and \
            compute_target and isinstance(compute_target, KubernetesCompute):
        raise TrainingException("KubernetesCompute type doesn't support non-Docker runs.")

    # 5) others...
    estimator_config.max_run_duration_seconds = max_run_duration_seconds

    # Super constructor overrides source_directory_data_store to None, so overriding it back here.
    # Now that we've added the datastore to the reference list, we only want the name
    estimator_config.source_directory_data_store = source_directory_data_store.name \
        if source_directory_data_store else None

    return estimator_config


def _validate_run_config_parameters(estimator, compute_target, vm_size, node_count, process_count_per_node,
                                    distributed_backend, distributed_training, use_gpu, use_docker,
                                    custom_docker_base_image, custom_docker_image, image_registry_details,
                                    user_managed, conda_packages, pip_packages, conda_dependencies_file_path,
                                    pip_requirements_file_path, conda_dependencies_file, pip_requirements_file,
                                    environment_variables, environment_definition, shm_size):
    # For deprecation purposes
    conda_output_str = "conda_dependencies_file"
    pip_output_str = "pip_requirements_file"

    if conda_dependencies_file_path and conda_dependencies_file:
        logging.warning(
            "Either 'conda_dependencies_file' or 'conda_dependencies_file_path' should be used. "
            "'conda_dependencies_file' will take precedence since 'conda_dependencies_file_path' "
            "will be deprecated.")
    elif conda_dependencies_file_path:
        logging.warning(
            "'conda_dependencies_file_path' parameter will be deprecated. Please use 'conda_dependencies_file' "
            "instead")
        conda_dependencies_file = conda_dependencies_file_path
        conda_output_str = "conda_dependencies_file_path"

    if pip_requirements_file_path and pip_requirements_file:
        logging.warning(
            "Either 'pip_requirements_file' or 'pip_requirements_file_path' should be used. "
            "'pip_requirements_file' will take precedence since 'pip_requirements_file_path' "
            "will be deprecated.")
    elif pip_requirements_file_path:
        logging.warning(
            "'pip_requirements_file_path' parameter will be deprecated. Please use 'pip_requirements_file' "
            "instead")
        pip_requirements_file = pip_requirements_file_path
        pip_output_str = "pip_requirements_file_path"

    if process_count_per_node != 1:
        logging.warning("'process_count_per_node' parameter will be deprecated. Please use it as part of "
                        "'distributed_training' parameter.")
        if distributed_backend is None:
            logging.warning("'process_count_per_node' parameter will be used only in combination with "
                            "'distributed_backend' parameter. As both these parameters are to be deprecated, "
                            "please use 'distributed_training' parameter and set "
                            "'process_count_per_node' on that object.")

    if use_docker is False:
        logging.warning("'use_docker' parameter will be deprecated. Please use 'environment_definition' "
                        "instead.")
        if custom_docker_image or custom_docker_base_image:
            raise TrainingException('If use_docker parameter is set to false, custom_docker_image or '
                                    'custom_docker_base_image parameter is not allowed')

    if environment_definition and (pip_packages or pip_requirements_file or conda_packages
                                   or conda_dependencies_file or custom_docker_image
                                   or image_registry_details or use_gpu or user_managed or shm_size
                                   or environment_variables):
        raise TrainingException('If environment_definition parameter is specified, the following parameters cannot '
                                'be specified: pip_packages, {}, conda_packages, '
                                '{}, custom_docker_image, image_registry_details, '
                                'use_gpu, user_managed, shm_size'.format(pip_output_str,
                                                                         conda_output_str))

    if conda_dependencies_file and (pip_packages or pip_requirements_file or conda_packages):
        raise TrainingException('If {} parameter is specified, the following parameters '
                                'cannot be specified: pip_packages, {}, conda_packages'.format(conda_output_str,
                                                                                               pip_output_str))

    if node_count < 1:
        raise TrainingException("Node count should be at least 1.")
    if process_count_per_node < 1:
        raise TrainingException("Process count per node should be at least 1.")
    if distributed_backend:
        logging.warning("'distributed_backend' parameter will be deprecated. Please use "
                        "'distributed_training' instead.")
        if estimator is not None:
            supported_backends = estimator._get_supported_backends()
            if distributed_backend.lower() not in supported_backends:
                raise TrainingException("Unsupported distributed backend value: "
                                        "{}. Supported backend(s): {}.".format(distributed_backend,
                                                                               supported_backends))
            if all([supported_backends == ["mpi"], distributed_training, not isinstance(distributed_training,
                                                                                        MpiConfiguration)]):
                raise TrainingException("Unsupported distributed backend value: "
                                        "{}. Supported backend: mpi.".format(distributed_backend))

    if distributed_training and isinstance(distributed_training, _DistributedTraining):
        distributed_training.validate(estimator.__class__.__name__.lower())

    if user_managed and (conda_packages or pip_packages or conda_dependencies_file
                         or pip_requirements_file):
        raise UserErrorException("If user_managed is True, then conda_packages, {}, "
                                 "pip_packages or {} cannot be specified.".format(conda_output_str, pip_output_str))

    if not distributed_backend and not distributed_training and (node_count > 1 or process_count_per_node > 1):
        raise TrainingException("'distributed_backend' or 'distributed_training' must be specified when "
                                "node_count > 1 or process_count_per_node > 1.")

    if compute_target and isinstance(compute_target, HDInsightCompute):
        raise ComputeTargetException("Unsupported compute target type. Type={}".format(type(compute_target)))

    if vm_size is None and compute_target is None:
        raise TrainingException("Either compute target or VM size should be specified.")

    if node_count > 1 and compute_target and not isinstance(compute_target, (AmlCompute, KubernetesCompute)):
        raise TrainingException("Compute target should be AmlCompute or KubernetesCompute for "
                                "distributed training (node_count > 1).")

    if custom_docker_base_image:
        if custom_docker_image:
            raise TrainingException("'custom_docker_base_image' parameter will be deprecated. Please use "
                                    "'custom_docker_image' only.")
        else:
            module_logger.warning("'custom_docker_base_image' parameter will be deprecated. Please use "
                                  "'custom_docker_image' instead.")


def _update_config_for_notebook_run(run_config, use_gpu, custom_docker_image):
    # If no custom image was specified and not user managed use openmpi images for notebook run
    if not _is_user_managed_environment(run_config.environment) and custom_docker_image is None:
        if use_gpu:
            run_config.environment.docker.base_image = OPENMPI_GPU_IMAGE
        else:
            run_config.environment.docker.base_image = OPENMPI_CPU_IMAGE


def _update_environment(environment, use_gpu, custom_docker_image,
                        image_registry_details, user_managed, conda_dependencies):
    # dependencies...
    environment.python.user_managed_dependencies = user_managed
    environment.python.conda_dependencies = conda_dependencies
    environment.spark.precache_packages = False

    if custom_docker_image:
        environment.docker.base_image = custom_docker_image
    else:
        environment.docker.base_image = DEFAULT_GPU_IMAGE if use_gpu else DEFAULT_CPU_IMAGE

    if image_registry_details:
        environment.docker.base_image_registry = image_registry_details


def _create_conda_dependencies(pip_packages, conda_packages, pip_requirements_file, conda_dependencies_file,
                               source_directory):
    # combined_pip_requirements gathers all entries from pip_packages and pip_requirements_file; it might include
    # both pip packages and pip options.
    combined_pip_requirements = pip_packages

    if pip_requirements_file:
        full_pip_requirements_path = path.normpath(
            path.join(source_directory, pip_requirements_file))

        if not path.isfile(full_pip_requirements_path):
            raise UserErrorException("{} path doesn't exist. "
                                     "The pip requirements file should be inside the project "
                                     "folder".format(full_pip_requirements_path))

        combined_pip_requirements = _merge_pip_packages_and_requirements(full_pip_requirements_path,
                                                                         combined_pip_requirements)

    # No package merge should happen if conda_dependencies_file is provided
    conda_dependencies = CondaDependencies()
    if conda_dependencies_file:
        if pip_packages or conda_packages or pip_requirements_file:
            logging.warning("When using the parameter 'conda_dependencies_file' "
                            "the following parameters are ignored: "
                            "'pip_packages', 'conda_packages', 'pip_requirements_file'")

        full_conda_dependencies_path = path.normpath(
            path.join(source_directory, conda_dependencies_file))

        if not path.isfile(full_conda_dependencies_path):
            raise UserErrorException("{} path doesn't exist. "
                                     "The conda dependencies file should be inside the project "
                                     "folder".format(full_conda_dependencies_path))

        conda_dependencies = CondaDependencies(full_conda_dependencies_path)
    else:
        if combined_pip_requirements:
            # CondaDependencies() contains azureml-defaults. Make sure it's still there.
            combined_pip_requirements.insert(0, "azureml-defaults")
            conda_dependencies.set_pip_requirements(combined_pip_requirements)

        if conda_packages:
            for conda_dependency in conda_packages:
                conda_dependencies.add_conda_package(conda_dependency)

    return conda_dependencies


def _merge_pip_packages_and_requirements(pip_requirements_file_path=None, pip_packages=None):
    if not pip_requirements_file_path:
        return pip_packages

    requirements_list = []
    with open(pip_requirements_file_path) as in_file:
        requirements_list = in_file.read().splitlines()

    return CondaDependencies.merge_requirements(merge_list(requirements_list, pip_packages, True))


def _is_user_managed_environment(environment_definition):
    if environment_definition and environment_definition.python is not None:
        return environment_definition.python.user_managed_dependencies

    return False


def _is_notebook_run(entry_script):
    return entry_script and entry_script.lower().endswith(".ipynb")


def _get_data_configuration(inputs, data_reference_inputs, dataset_inputs, source_directory_data_store):
    merged_inputs = merge_list(inputs, data_reference_inputs, True)
    merged_inputs = merge_list(merged_inputs, dataset_inputs, True)
    if source_directory_data_store:
        merged_inputs.append(source_directory_data_store)
    data_references = {}
    data = {}
    for item in merged_inputs:
        if isinstance(item, AbstractAzureStorageDatastore):
            item_ref = item._get_data_reference()
            data_references[item_ref.data_reference_name] = item_ref.to_config()
        elif isinstance(item, DataReference):
            data_references[item.data_reference_name] = item.to_config()
        elif isinstance(item, DatasetConsumptionConfig):
            data[item.name] = item
        else:
            raise UserErrorException("Type {0} is not supported for inputs.".format(type(item)))
    return data_references, data


def _get_data_inputs(script_params):
    from azureml.data.azure_storage_datastore import AbstractAzureStorageDatastore
    data_reference_inputs = []
    dataset_inputs = []

    def process_arg(input):
        if isinstance(input, DataReference) or isinstance(input, AbstractAzureStorageDatastore):
            data_reference_inputs.append(input)
        elif isinstance(input, DatasetConsumptionConfig):
            dataset_inputs.append(input)

    if script_params:
        for key, value in script_params.items():
            process_arg(key)
            process_arg(value)

    return data_reference_inputs, dataset_inputs


def _get_outputs(script_params):
    outputs = {}

    if not script_params:
        return outputs

    def process_arg(output):
        if isinstance(output, OutputDatasetConfig):
            outputs[output.name] = output._to_output_data()

    for key, value in script_params.items():
        process_arg(key)
        process_arg(value)

    return outputs


def _get_arguments(script_params):
    from azureml.data.azure_storage_datastore import AbstractAzureStorageDatastore

    script_params_copy = {}

    def process_argument(argument):
        if isinstance(argument, DataReference):
            return str(argument)
        elif isinstance(argument, AbstractAzureStorageDatastore):
            return str(argument._get_data_reference())
        elif isinstance(argument, DatasetConsumptionConfig):
            # if the mode is not download or mount, keep dataset consumption configuration in the arguments,
            # which will be transferred to dataset.id when start_run.

            if argument.mode.lower() == 'download' or \
                    argument.mode.lower() == 'mount':
                # For File dataset, args.key should be a path which is produced in the server.
                # Here, we give the a special identifier + input name of DatasetConsumptionConfig
                return _DATASET_ARGUMENT_TEMPLATE.format(argument.name)
        elif isinstance(argument, OutputDatasetConfig):
            return _DATASET_OUTPUT_ARGUMENT_TEMPLATE.format(argument.name)
        elif isinstance(argument, Data):
            raise UserErrorException(
                "You cannot use a Data directly. Please call as_mount or as_download on Dataset to convert "
                "it into a DatasetConsumptionConfig and pass that into the estimator."
            )
        elif isinstance(argument, OutputData):
            raise UserErrorException(
                "You cannot use a OutputData directly. Please create a OutputFileDatasetConfig by calling its "
                "constructor and pass that into the estimator."
            )
        return argument

    if not script_params:
        return convert_dict_to_list(script_params_copy)

    for key, value in script_params.items():
        key = process_argument(key)
        value = process_argument(value)
        script_params_copy[key] = value

    return list_remove_empty_items(convert_dict_to_list(script_params_copy))
