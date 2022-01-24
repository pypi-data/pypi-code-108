# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml._cli_common.ml_cli_error import MlCliError
from azureml.core.model import Model
from azureml.core.compute import ComputeTarget
from azureml.exceptions import ComputeTargetException, WebserviceException
from azureml.contrib.core.webservice.iot import IotWebservice, IotModuleSettings, IotBaseModuleSettings
from azureml.core.container_registry import ContainerRegistry
from azureml.core.webservice import Webservice
from azureml.contrib.core.compute.iothub import IotHubCompute
import logging
from ..iot._cli import _parse_kv_list
import json
from azureml.core.model import InferenceConfig
from azureml._model_management._constants import MODEL_METADATA_FILE_ID_KEY, \
    CLI_METADATA_FILE_WORKSPACE_KEY, CLI_METADATA_FILE_RG_KEY, IOT_WEBSERVICE_TYPE
from azureml._base_sdk_common.cli_wrapper._common import get_workspace_or_default
import yaml

module_logger = logging.getLogger(__name__)


def model_deploy(service_name, tags, properties, description,
                 inference_config_file, compute_target, deploy_config_file, workspace_name,
                 resource_group, no_wait_flag, verbose, path, models=[], model_metadata_files=[]):
    # user needs to provide deployment config file
    if not deploy_config_file:
        raise MlCliError('Error, need to specify --deploy-config-file.')

    # user needs to provide compute target
    if not compute_target:
        raise MlCliError('Error, need to specify --compute-target.')

    if (not workspace_name and not resource_group) and (not path):
        raise MlCliError('Error, need to specify either 1. --workspace-name and resource_group '
                         ' 2. --path')
    workspace = get_workspace(workspace_name, resource_group, path)

    # user needs to provide either models, or model_metadata_files
    registered_models = []
    if len(models) == 0 and len(model_metadata_files) == 0:
        raise MlCliError('Error, need to specify either --model or --model-metadata-file '
                         'for model(s) to be deployed.')
    else:
        # Collect all of the input models. Models can be specified via --model, or --model-metadata-file parameters.
        # In either case, the models need to be registered to MMS first
        target_val = {CLI_METADATA_FILE_WORKSPACE_KEY: workspace.name,
                      CLI_METADATA_FILE_RG_KEY: workspace.resource_group}
        for model_meta_file in model_metadata_files:
            conf = _validate_config_file(model_meta_file, target_val)
            models.append(conf.get(MODEL_METADATA_FILE_ID_KEY))
        for _id in models:
            registered_models.append(Model(workspace, id=_id))

    service = None
    try:
        service = Webservice(workspace, service_name)
    except WebserviceException as e:
        if 'WebserviceNotFound' not in e.message:
            # 'WebserviceNotFound' in error message is the case that same name service doesn't exist, which is fine
            raise

    # TODO: once IoT deployment service support update operation,
    # if --overwrite is specified then we should not raise exception here,
    # instead, we should regard this as a service update operation
    if service:
        raise MlCliError('A service with name \'{}\' already exists.'.format(service_name))

    tags_dict = _parse_kv_list(tags, 'tags')
    properties_dict = _parse_kv_list(properties, 'properties')

    # Parse --inference-config-file input
    conf = _validate_config_file(inference_config_file, dict.fromkeys(['entryScript', 'runtime']))
    inference_config = InferenceConfig(entry_script=conf.get('entryScript'),
                                       runtime=conf.get('runtime'),
                                       conda_file=conf.get('condaFile'),
                                       extra_docker_file_steps=conf.get('extraDockerfileSteps'),
                                       source_directory=conf.get('sourceDirectory'),
                                       enable_gpu=conf.get('enableGpu'),
                                       base_image=conf.get('baseImage'),
                                       base_image_registry=conf.get('baseImageRegistry'),
                                       cuda_version=conf.get('cudaVersion'),
                                       description=description)

    # Extract deployment config from input --deploy-config-file
    try:
        with open(deploy_config_file, 'r') as deploy_file_stream:
            # validate required keys are exist
            deploy_config_obj = json.load(deploy_file_stream)
            compute_type_key = 'computeType'
            aml_mod_key = 'amlModule'
            external_mod_key = 'externalModules'
            routes_key = 'routes'
            device_key = 'iotDeviceId'
            registry_key = 'acrCredentials'
            _validate_not_empty([compute_type_key, aml_mod_key, routes_key, device_key],
                                deploy_config_obj, '--deploy-config-file')

            deploy_compute_type = deploy_config_obj[compute_type_key].lower()
            if deploy_compute_type == 'iot':
                _validate_not_empty(['moduleName'], deploy_config_obj.get(aml_mod_key), aml_mod_key)
                aml_module = IotBaseModuleSettings(
                    name=deploy_config_obj.get(aml_mod_key, {}).get('moduleName'),
                    create_option=deploy_config_obj.get(aml_mod_key, {}).get('createOptions'),
                    env=deploy_config_obj.get(aml_mod_key, {}).get('environmentVariables'),
                    properties_desired=deploy_config_obj.get(aml_mod_key, {}).get('propertiesDesired'))

                external_modules = []
                for mod in deploy_config_obj.get(external_mod_key, []):
                    _validate_not_empty(['moduleName', 'imageLocation'], mod, external_mod_key)
                    module = IotModuleSettings(
                        mod.get('moduleName'),
                        mod.get('imageLocation'),
                        mod.get('environmentVariables'),
                        mod.get('createOptions'),
                        mod.get('propertiesDesired'))
                    external_modules.append(module)

                registry_list = []
                for credential in deploy_config_obj.get(registry_key, []):
                    _validate_not_empty(['location', 'user', 'password'], credential, registry_key)
                    registry = ContainerRegistry()
                    registry.address = credential['location']
                    registry.username = credential['user']
                    registry.password = credential['password']
                    registry_list.append(registry)

                iot_deployment_config = IotWebservice.deploy_configuration(
                    routes=deploy_config_obj.get(routes_key, {}),
                    device_id=deploy_config_obj.get(device_key, {}),
                    aml_module=aml_module,
                    external_modules=external_modules,
                    acr_credentials=registry_list,
                    tags=tags_dict,
                    properties=properties_dict,
                    description=description,
                    compute_target_name=compute_target)

                if service:
                    raise MlCliError('Update service not supported yet')
                else:
                    try:
                        target = ComputeTarget(workspace, compute_target)
                        service = Model.deploy(workspace, service_name, registered_models, inference_config,
                                               iot_deployment_config, target)
                    except ComputeTargetException as e:
                        if 'ComputeTargetNotFound' in e.message:
                            raise MlCliError('Error, no compute target found with name {0}'.format(compute_target))
                        else:
                            raise
            else:
                raise MlCliError('Unknown deployment type: {}'.format(deploy_compute_type))
    except Exception as ex:
        raise MlCliError('Error deploying model.', content=ex)

    if no_wait_flag:
        module_logger.debug('Service may take a few minutes to be created.')
    else:
        service.wait_for_deployment(verbose)
        if service.state == 'Healthy':
            module_logger.debug('Service Name: {} deploy successfully'.format(service.name))
        else:
            raise MlCliError('Polling for service creation ended with service in \'{}\' state and with error '
                             'field \'{}\'. \nMore information can be found using "az ml service get-logs -n {}"\n'
                             'Service name: {}\n'
                             'Workspace name: {}\n'
                             'Resource group: {}'.format(service.state, service.error, service.name,
                                                         service.name, workspace.name, workspace.resource_group))

    # IoT service does not need scoringUri, here adding scoringUri just for consistance with other services
    objs = service.serialize()
    objs.update({'scoringUri': None})
    return objs, verbose


def _validate_not_empty(keys, dict_items, dict_name):
    for k in keys:
        if k not in dict_items:
            raise MlCliError('need to specify {0} for {1}'.format(k, dict_name))


def _validate_config_file(config_file, expected_vals):
    with open(config_file, 'r') as f:
        try:
            config_content = yaml.safe_load(f.read())
        except Exception:
            raise MlCliError('Error while parsing file. Must be valid JSON or YAML file.')

        for k in expected_vals.keys():
            v = config_content.get(k)
            if not v:
                raise MlCliError("Required field {0} is not found in {1}", k, config_file)

            if expected_vals[k] and v != expected_vals[k]:
                raise MlCliError("Required field {0} in {1} equals to {2}, but expected value is {3}",
                                 k, config_file, v, expected_vals[k])

        return config_content


def get_workspace(workspace_name=None, resource_group=None, path=None):
    # set current directory (.) as default value
    path = "." if not path else path
    return get_workspace_or_default(resource_group=resource_group,
                                    workspace_name=workspace_name,
                                    project_path=path)


def compute_attach(workspace_name, resource_group, connection_string, resource_id, iothub_name,
                   iothub_resource_group, compute_name, no_wait_flag, verbose, path):
    if (not resource_id and (not iothub_name or not iothub_resource_group)) or \
       (resource_id and (iothub_name or iothub_resource_group)):
        raise MlCliError('Error, need to specify either 1. --resource-id '
                         ' 2. --iothub-name and --iothub-resource-group'
                         'for compute target(s) to be attached.')

    if (not workspace_name and not resource_group) and (not path):
        raise MlCliError('Error, need to specify either 1. --workspace-name and resource_group '
                         ' 2. --path')
    workspace = get_workspace(workspace_name, resource_group, path)
    config = IotHubCompute.attach_configuration(resource_group=iothub_resource_group,
                                                name=iothub_name,
                                                resource_id=resource_id,
                                                connection_string=connection_string)
    target = IotHubCompute.attach(workspace, compute_name, config)

    if no_wait_flag:
        module_logger.debug('Compute target may take a few minutes to be created.')
        module_logger.debug('To see if your compute target is ready to use, run:')
        module_logger.debug('  az ml computetarget show --name {0} --workspace-name {1} --resource-group {2}'.format(
            compute_name, workspace_name, resource_group))
    else:
        target.wait_for_completion(verbose)
        if target.is_attached and target.type == 'IotHub':
            module_logger.debug('Compute target Name: {} deploy successfully'.format(compute_name))
        else:
            raise MlCliError('Creating target failed')

    return target.serialize(), verbose


def service_list(workspace_name, model_name, model_id, tags, properties,
                 resource_group, path, verbose):
    workspace = get_workspace(workspace_name, resource_group, path)
    services = Webservice.list(workspace, compute_type=IOT_WEBSERVICE_TYPE, model_name=model_name, model_id=model_id,
                               tags=tags, properties=properties)

    return [service.serialize() for service in services], verbose


def computetarget_list(workspace_name, resource_group, path, verbose=False):
    workspace = get_workspace(workspace_name, resource_group, path)
    target_list = ComputeTarget.list(workspace)
    targets = []
    for compute_target in target_list:
        if compute_target._compute_type == IotHubCompute._compute_type:
            targets.append(compute_target.serialize())
    return targets, verbose


def computetarget_detach(name, workspace_name, resource_group, path, verbose):
    workspace = get_workspace(workspace_name, resource_group, path)
    try:
        compute_target = ComputeTarget(workspace, name)
    except ComputeTargetException as e:
        if 'ComputeTargetNotFound' in e.message:
            raise MlCliError('Error, no computetarget with name {} in workspace {} in '
                             'resource group {} found to detach.'.format(name, workspace_name, resource_group))
        else:
            raise

    if compute_target._compute_type != IotHubCompute._compute_type:
        raise MlCliError('Error, {} is not an IoT computetarget, '
                         'it\'s type is {}.'.format(name, compute_target._compute_type))

    compute_target.detach()

    module_logger.debug('Resource detach successfully submitted.')
    module_logger.debug('Resources may take a few minutes to be completely detached.')

    return compute_target.serialize(), verbose
