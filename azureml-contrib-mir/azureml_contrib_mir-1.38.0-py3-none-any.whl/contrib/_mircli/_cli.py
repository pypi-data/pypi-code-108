# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import json
from ._util import cli_context, collect_input_models, file_stream_to_object, parse_tags
from ._util import parse_properties, try_get_local_service, create_inference_config, create_deploy_config
from azureml._cli_common.ml_cli_error import MlCliError
from azureml.core.model import Model
from azureml.core.webservice import Webservice, LocalWebservice
from azureml.exceptions import WebserviceException
from azureml.core.image import Image
from azureml.contrib.mir.webservice import MirWebservice
from azureml._model_management._constants import MIR_WEBSERVICE_TYPE
from azureml._model_management._constants import PROFILE_METADATA_CPU_KEY, \
    PROFILE_METADATA_MEMORY_KEY

module_logger = logging.getLogger(__name__)


def model_deploy(name, overwrite, tags, properties, description, models, model_metadata_files, inference_config_file,
                 entry_script, runtime, conda_file, extra_docker_file_steps, source_directory, base_image,
                 base_image_registry, cuda_version, compute_type, cpu_cores, memory_gb, auth_enabled,
                 autoscale_enabled, autoscale_min_replicas, autoscale_max_replicas, autoscale_refresh_seconds,
                 autoscale_target_utilization, collect_model_data, scoring_timeout_ms,
                 replica_max_concurrent_requests, max_request_wait_time, num_replicas,
                 tls_mode, certificate_fingerprints, compute_target, deploy_config_file,
                 profile_metadata_file, path, workspace_name, resource_group, no_wait_flag, verbose_local,
                 environment_name, environment_version, environment_directory, sku, gpu_cores,
                 enable_app_insights, osType=None, context=cli_context):
    # user needs to provide either models, or model_metadata_files
    if (not models) and (not model_metadata_files):
        raise MlCliError('Error, need to specify either --model or --model-metadata-file '
                         'for model(s) to be deployed.')

    workspace = context.get_workspace(workspace_name, resource_group, path)

    # Collect all of the input models. Models can be specified via --model, or --model-metadata-file parameters.
    # In either case, the models need to be registered to MMS first
    registered_models = collect_input_models(workspace, model_metadata_files, models)

    # check whether same service already exists.
    # NOTE: This is a temporary solution for overwrite. We first figure out whether same service exists. This way
    #       we can fail fast if necessary, better than fails after image is created.
    #           If overwrite is true
    #               If same service exists
    #               Then we call service.update
    #               Else we call service.create
    #           Else
    #               If same service exists
    #               Then fail
    #               Else we call service.create
    #       This solution leaves some concurrency issues unaddressed. For example, same name service is created
    #       after the first read. But that's ok as we will be onboard to 'atomic' CreateOrUpdate REST API soon.
    service = None
    try:
        service = Webservice(workspace, name)
    except WebserviceException as e:
        if 'WebserviceNotFound' not in e.message:
            # 'WebserviceNotFound' in error message is the case that same name service doesn't exist, which is fine
            raise e

    if service is None:
        # same name cloud service doesn't exist, so we check whether same name local service exists.
        service = try_get_local_service(workspace, name)

    if (service and not overwrite):
        raise MlCliError('A service with name \'{}\' already exists. If you want to overwrite the existing service,'
                         ' please specify --overwrite option.'.format(name))

    tags_dict = parse_tags(tags)
    properties_dict = parse_properties(properties)

    # Create InferenceConfig object from input file and parameters
    # The parameter validations (e.g. entry_script is required, runtime cannot co-exist with environment etc.) are
    # delegated to SDK layer, InferenceConfig.validate_configuration
    inference_config = create_inference_config(workspace, inference_config_file, entry_script, environment_name,
                                               environment_version, environment_directory, runtime, conda_file,
                                               extra_docker_file_steps, source_directory, None, description,
                                               base_image, base_image_registry, cuda_version)

    # Create deployment config object from input file and parameters
    if (not deploy_config_file) and (not compute_type):
        raise MlCliError('Error, need to specify either --deploy-config-file or --compute-type '
                         'parameter for model(s) to be deployed.')

    if compute_type:
        deploy_compute_type = compute_type.lower()
    else:
        try:
            with open(deploy_config_file, 'r') as deploy_file_stream:
                deploy_config_obj = file_stream_to_object(deploy_file_stream)
                compute_type_key = 'computeType'
                if compute_type_key not in deploy_config_obj:
                    raise MlCliError('need to specify {} in --deploy-config-file or with '
                                     '--compute-type parameter'.format(compute_type_key))

                deploy_compute_type = deploy_config_obj[compute_type_key].lower()
        except Exception as ex:
            raise MlCliError('Error getting deploy compute type from config file.', content=ex)

    deploy_config = create_deploy_config(deploy_config_file, deploy_compute_type, cpu_cores, memory_gb, tags_dict,
                                         properties_dict, description, None, auth_enabled, None,
                                         enable_app_insights, None, None, None,
                                         None, autoscale_enabled, autoscale_min_replicas,
                                         autoscale_max_replicas, autoscale_refresh_seconds,
                                         autoscale_target_utilization, collect_model_data, scoring_timeout_ms,
                                         replica_max_concurrent_requests, max_request_wait_time, num_replicas,
                                         None, None, tags, properties, gpu_cores, None,
                                         None, None, None, None, None, None, None,
                                         tls_mode, certificate_fingerprints, sku, osType)

    # Get profiling results from input file
    profile_results = None
    if profile_metadata_file:
        with open(profile_metadata_file, 'r') as infile:
            profile_metadata = json.load(infile)
            if profile_metadata.get(PROFILE_METADATA_CPU_KEY) is None or \
               profile_metadata.get(PROFILE_METADATA_MEMORY_KEY) is None:
                raise MlCliError('Profile metadata file "{}" does not contain the parameters "{}" and "{}" '
                                 'which are needed to use the profile metadata file'
                                 .format(profile_metadata_file, PROFILE_METADATA_CPU_KEY,
                                         PROFILE_METADATA_MEMORY_KEY))
            profile_results = {PROFILE_METADATA_CPU_KEY: profile_metadata[PROFILE_METADATA_CPU_KEY],
                               PROFILE_METADATA_MEMORY_KEY: profile_metadata[PROFILE_METADATA_MEMORY_KEY]}
            module_logger.info("Using profiling results for deployment.")
            module_logger.info("CPU:{} MemoryInGB:{}".format(profile_results[PROFILE_METADATA_CPU_KEY],
                               profile_results[PROFILE_METADATA_MEMORY_KEY]))
            deploy_config.cpu_cores = profile_results[PROFILE_METADATA_CPU_KEY]
            deploy_config.memory_gb = profile_results[PROFILE_METADATA_MEMORY_KEY]

    # if service exists, need to create image here explicitly, except for Local service (they dont use Image.create())
    if service:
        raise MlCliError("Error: service already exists")

    if deploy_compute_type == "mir":
        # mir deployment
        module_logger.debug('Create MIR service \'{}\'.'.format(name))
        service = Model.deploy(workspace, name, registered_models, inference_config, deploy_config)
    else:
        raise MlCliError("Compute type invalid")

    if no_wait_flag:
        module_logger.debug('Service may take a few minutes to be created.')
        module_logger.debug('To see if your service is ready to use, run:')
        module_logger.debug('  az ml service show -n {}'.format(service.name))
    else:
        service.wait_for_deployment(verbose_local)
        if service.state == 'Healthy':
            module_logger.debug('Service Name: {}'.format(service.name))
            module_logger.debug(
                'Run your service using "az ml service run -n {} -d <input data>'.format(service.name))
        else:
            raise MlCliError('Polling for service creation ended with service in \'{}\' state and with error '
                             'field \'{}\'. \nMore information can be found using \"az ml service get-logs -n {}\"\n'
                             'Service name: {}\n'
                             'Workspace name: {}\n'
                             'Resource group: {}'.format(service.state, service.error, service.name,
                                                         service.name, workspace.name, workspace.resource_group))
    return service.serialize(), verbose_local


def service_list(workspace_name, model_name, model_id, tags, properties, resource_group, path,
                 verbose=False, context=cli_context):
    workspace = context.get_workspace(workspace_name, resource_group, path)
    services = Webservice.list(workspace, compute_type=MIR_WEBSERVICE_TYPE, model_name=model_name,
                               model_id=model_id, tags=tags, properties=properties)

    return [service.serialize() for service in services], verbose


def service_delete(service_name, path, workspace_name, resource_group, verbose_local, context=cli_context):
    workspace = context.get_workspace(workspace_name, resource_group, path)
    service = None
    try:
        service = MirWebservice(workspace, name=service_name)
    except WebserviceException as e:
        if 'WebserviceNotFound' in e.message:
            pass
        else:
            raise e

    if service is None:
        # same name cloud service doesn't exist, check local service now
        service = try_get_local_service(workspace, service_name)

    if service is None:
        # no service exists with the input name, cloud or local. raise error
        raise MlCliError('Error, no service with name {} found in workspace {} in '
                         'resource group {}.'.format(service_name, workspace.name, workspace.resource_group))

    # get the image ID for this service
    image_id = service.image_id

    # local webservice has no underlying image
    is_local_webservice = isinstance(service, LocalWebservice)
    service.delete()

    # do not try to delete image for local webservice as there is no cloud Image for local
    if not is_local_webservice and image_id:
        image = Image(workspace, id=image_id)
        if not image or not image.id:
            raise MlCliError('Error, no model package with id {} found in workspace {} in '
                             'resource group {}.'.format(image_id, workspace.name, workspace.resource_group))
        image.delete()

    module_logger.debug('Resource deletion successfully submitted.')
    module_logger.debug('Resources may take a few minutes to be completely deprovisioned.')

    return service.serialize(), verbose_local


def service_run(service_name, input_data, path, workspace_name, resource_group, verbose_local, context=cli_context):
    workspace = context.get_workspace(workspace_name, resource_group, path)
    service = None
    try:
        service = MirWebservice(workspace, name=service_name)
    except WebserviceException as e:
        if 'WebserviceNotFound' in e.message:
            pass
        else:
            raise e

    if service is None:
        # same name cloud service doesn't exist, check local service now
        service = try_get_local_service(workspace, service_name)

    if service is None:
        # no service exists with the input name, cloud or local. raise error
        raise MlCliError('Error, no service with name {} found in workspace {} in '
                         'resource group {}.'.format(service_name, workspace.name, workspace.resource_group))

    result = service.run(input_data)
    return result, verbose_local
