# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
Utility functions for AML CLI
"""

from __future__ import print_function

import json
import os
import platform

import yaml

from azureml._cli_common.ml_cli_error import MlCliError
from azureml._base_sdk_common.cli_wrapper._common import get_workspace_or_default
from azureml.core.environment import Environment
from azureml.core.webservice import LocalWebservice
from azureml.exceptions import WebserviceException

try:
    # python 3
    from builtins import input
except ImportError:
    # python 2
    from __builtin__ import input

import subprocess
import re
import requests
from azure.cli.core._profile import Profile
from azure.cli.core.util import CLIError
from azureml._model_management._constants import MODEL_METADATA_FILE_ID_KEY, \
    CLI_METADATA_FILE_WORKSPACE_KEY, CLI_METADATA_FILE_RG_KEY
from azureml.core.model import InferenceConfig
from azureml.core.model import Model
from azureml.contrib.mir.webservice import MirWebservice
from knack.log import get_logger
logger = get_logger(__name__)

ice_base_url = 'https://amlacsagent.azureml-int.net'
acs_connection_timeout = 5
ice_connection_timeout = 15


# EXCEPTIONS
class InvalidConfError(Exception):
    """Exception raised when config read from file is not valid json."""
    pass


# CONTEXT CLASS
class CommandLineInterfaceContext(object):
    """
    Context object that handles interaction with shell, filesystem, and azure blobs
    """
    hdi_home_regex = r'(.*:\/\/)?(?P<cluster_name>[^\s]*)'
    aml_env_default_location = 'east us'
    model_dc_storage = os.environ.get('AML_MODEL_DC_STORAGE')
    model_dc_event_hub = os.environ.get('AML_MODEL_DC_EVENT_HUB')
    hdi_home = os.environ.get('AML_HDI_CLUSTER')
    base_name = os.environ.get('AML_ROOT_NAME')
    hdi_user = os.environ.get('AML_HDI_USER', '')
    hdi_pw = os.environ.get('AML_HDI_PW', '')
    env_is_k8s = os.environ.get('AML_ACS_IS_K8S', '').lower() == 'true'

    @property
    def app_insights_account_key(self):
        if not self._app_insights_account_key:
            self._app_insights_account_key = self.get_from_mlc(('app_insights', 'instrumentation_key'))
        return self._app_insights_account_key

    @property
    def app_insights_account_id(self):
        if not self._app_insights_account_id:
            self._app_insights_account_id = self.get_from_mlc(('app_insights', 'app_id'))
        return self._app_insights_account_id

    @property
    def az_account_name(self):
        if not self._account_name:
            self._account_name = self.get_from_mlc(('storage_account', 'resource_id'))
            if self._account_name and self._account_name.startswith('/subscriptions'):
                self._account_name = self._account_name.split('/')[-1]
        return self._account_name

    @property
    def az_account_key(self):
        if not self._account_key:
            self._account_key = self.get_from_mlc(('storage_account', 'primary_key'))
        return self._account_key

    @property
    def acr_home(self):
        if not self._acr_home:
            self._acr_home = self.get_from_mlc(('container_registry', 'login_server'))
        return self._acr_home

    @property
    def acr_pw(self):
        if not self._acr_pw:
            self._acr_pw = self.get_from_mlc(('container_registry', 'password'))
        return self._acr_pw

    @property
    def acr_user(self):
        if not self._acr_user:
            if not self.acr_home:
                self._acr_user = None
            else:
                self._acr_user = self.acr_home.split('.')[0]
        return self._acr_user

    def __init__(self):
        self.env_profile_path = os.path.join(get_home_dir(), '.azure', 'viennaOperationalizationComputeResource.json')
        self.az_container_name = 'azureml'
        if self.hdi_home:
            outer_match_obj = re.match(self.hdi_home_regex, self.hdi_home)
            if outer_match_obj:
                self.hdi_home = outer_match_obj.group('cluster_name')
        self.hdi_domain = self.hdi_home.split('.')[0] if self.hdi_home else None
        self.forwarded_port = None
        self.current_execution_mode = None
        self.current_compute_creds = None
        self.current_compute_name = None
        self.current_compute_resource_group = None
        self.current_compute_subscription_id = None
        self.current_env = self.read_config()
        if self.current_env:
            self.current_execution_mode = self.current_env['current_execution_mode']
            self.current_compute_resource_group = self.current_env['resource_group']
            self.current_compute_name = self.current_env['name']
            self.current_compute_subscription_id = self.current_env['subscription']
        self._account_name = None
        self._account_key = None
        self._acr_home = None
        self._acr_pw = None
        self._acr_user = None
        self._app_insights_account_key = None
        self._app_insights_account_id = None

    @staticmethod
    def get_active_subscription_id():
        return Profile().get_subscription()['id']

    @staticmethod
    def set_active_subscription_id(sub_id):
        Profile().set_active_subscription(sub_id)
        print('Active subscription set to {}'.format(sub_id))

    def set_compute(self, compute_resource):
        self.write_config(compute_resource)
        self.current_env = compute_resource
        self.current_compute_resource_group = compute_resource['resource_group']
        self.current_compute_name = compute_resource['name']
        self.current_compute_subscription_id = compute_resource['subscription']
        self.current_execution_mode = compute_resource['current_execution_mode']

    def unset_compute(self):
        os.remove(self.env_profile_path)
        self.current_env = None
        self.current_compute_resource_group = None
        self.current_compute_name = None
        self.current_compute_subscription_id = None
        self.current_execution_mode = None

    def validate_active_and_compute_subscriptions(self):
        if (self.current_compute_subscription_id
                is not None and self.current_compute_subscription_id != self.get_active_subscription_id()):
            print('Your current active subscription ({}) is not the same as the '
                  'subscription for your environment ({}). To proceed, you must '
                  'update your active environment.'.format(self.get_active_subscription_id(),
                                                           self.current_compute_subscription_id))
            result = input('Would you like to update your active subscription to {} [Y/n]? '
                           .format(self.current_compute_subscription_id)).lower()
            if result == 'n' or result == 'no':
                raise MlCliError('Unable to get current compute resource from different subscription.')

            self.set_active_subscription_id(self.current_compute_subscription_id)

    def populate_compute_creds(self):
        from ._env_util import get_compute_resource_keys
        if self.current_compute_creds is None:
            if self.current_compute_name and self.current_compute_resource_group:
                self.validate_active_and_compute_subscriptions()
                try:
                    # cache credentials
                    self.current_compute_creds = get_compute_resource_keys(self.current_compute_resource_group,
                                                                           self.current_compute_name)
                except CLIError:
                    self.unset_current_compute_and_warn_user()
                    raise

    def unset_current_compute_and_warn_user(self):
        logger.warning('Unable to find env with group {} and name {}. It may have been moved or deleted, '
                       'or you could have the wrong active subscription set. Unsetting current env.'.format(
                           self.current_compute_resource_group, self.current_compute_name))
        logger.warning("To see available environments in the subscription, run:\n"
                       "  az ml env list\n"
                       "To set an active environment, run:\n"
                       "  az ml env set -n <env_name> -g <env_group>\n"
                       "To see available subscriptions, run:\n"
                       "  az account show -o table\n"
                       "To set active accout, run:\n"
                       "  az account set -s <subscription_name>\n")
        self.unset_compute()

    def raise_for_missing_creds(self):
        raise MlCliError('Running in cluster mode is only supported with MLC RP environments. '
                         'You can provision a new environment by running: '
                         '\'az ml env setup -c -n <cluster name> -g <resource group>\'. '
                         'If you have already provisioned an environment set it as your active environment by running:'
                         '\'az ml env set -n <cluster name> -g <resource group>\'')

    def get_from_mlc(self, cred_path):
        self.populate_compute_creds()
        if self.current_compute_creds is None:
            raise MlCliError('Unable to determine current environment information. '
                             'Please run \'az ml env set\'')

        try:
            trav = self.current_compute_creds
            for step in cred_path:
                trav = getattr(trav, step)
        except AttributeError as exc:
            raise MlCliError('Encountered an issue parsing credentials for compute. '
                             'Please contact deployml@microsoft.com with this information '
                             'if this issue persists. Raw credentials: {}'.format(self.current_compute_creds),
                             content=exc)
        return trav

    @staticmethod
    def str_from_subprocess_communicate(output):
        """

        :param output: bytes or str object
        :return: str version of output
        """
        if isinstance(output, bytes):
            return output.decode('utf-8')
        return output

    def run_cmd(self, cmd_list):
        """

        :param cmd: str command to run
        :return: str, str - std_out, std_err
        """
        proc = subprocess.Popen(cmd_list, shell=(not self.os_is_unix()),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        output, err = proc.communicate()
        return self.str_from_subprocess_communicate(output), \
            self.str_from_subprocess_communicate(err)

    def read_config(self):
        """

        Tries to read in ~/.azure/viennaOperationalizationComputeResource.json as a dictionary.
        :return: dict - if successful, the config dictionary from
        : ~/.azure/viennaOperationalizationComputeResource.json, None otherwise
        :raises: InvalidConfError if the configuration read is not valid json, or is not a dictionary
        """
        try:
            with open(self.env_profile_path, 'r') as env_file:
                try:
                    current_env = json.load(env_file)
                except ValueError:
                    os.remove(self.env_profile_path)
                    raise MlCliError('Error retrieving currently set environment: invalid JSON. '
                                     'Please run \'az ml env set\'')
        except IOError:
            return None
        return current_env

    def write_config(self, compute_resource):
        """

        Writes out the given configuration dictionary to ~/.azure/viennaOperationalizationComputeResource.json
        :param compute_resource: Configuration dictionary.
        :return: 0 if success, -1 otherwise
        """
        try:
            with open(self.env_profile_path, 'w') as conf_file:
                conf_file.write(json.dumps(compute_resource))
        except IOError:
            return -1

        return 0

    def in_local_mode(self):
        """
        Determines if AML CLI is running in local mode
        :return: bool - True if in local mode, false otherwise
        """

        if self.current_execution_mode:
            return self.current_execution_mode == 'local'
        else:
            raise MlCliError('Error retrieving currently set environment. '
                             'Please run \'az ml env set\'')

    @staticmethod
    def http_call(http_method, url, **kwargs):
        """

        :param http_method: str: (post|get|put|delete)
        :param url: str url to perform http call on
        :return: requests.response object
        """
        http_method = http_method.lower()

        # raises AttributeError if not a valid method
        return getattr(requests, http_method)(url, **kwargs)

    @staticmethod
    def os_is_unix():
        return platform.system().lower() in ['linux', 'unix', 'darwin']

    @staticmethod
    def get_input(input_str):
        return input(input_str)

    def check_output(self, cmd, stderr=None):
        return subprocess.check_output(cmd, shell=(not self.os_is_unix()), stderr=stderr)

    def get_workspace(self, workspace_name=None, resource_group=None, path=None, subscription_id=None):
        # if path is not provide, use current directory (.) as default value
        if not path:
            path = "."
        return get_workspace_or_default(subscription_id=subscription_id,
                                        resource_group=resource_group,
                                        workspace_name=workspace_name,
                                        project_path=path,
                                        logger=logger)


# UTILITY FUNCTIONS
def get_local_or_cloud_environment(workspace, environment_name=None, environment_version=None,
                                   environment_directory=None):
    """
    Return an Environment object which is either a cloud (already registered) or a local (not
    registered) one, or if all inputs are None, return None.

    :param workspace: current AzML workspace
    :type workspace: azureml.core.Workspace
    :param environment_name: name of a cloud environment
    :type environment_name: string
    :param environment_version: version of a cloud environment
    :type environment_version: string
    :param environment_directory: directory of a local environment
    :type environment_directory: string
    :return: azureml.core.environment.Environment object or None
    :rtype: azureml.core.environment.Environment
    """
    # does caller provide name or directory for environment
    if environment_name is None and environment_directory is None:
        return None

    try:
        if environment_name is not None:
            # try to get registered environment by name and version
            environment = Environment.get(workspace, environment_name, environment_version)
        else:
            # try to get a local environment from input directory
            environment = Environment.load_from_directory(environment_directory)

        return environment
    except Exception as ex:
        # wrap with MlCliError
        raise MlCliError('Error getting Environment.', content=ex)


def create_inference_config(workspace, inference_config_file, entry_script, environment_name, environment_version,
                            environment_directory, runtime, conda_file, extra_docker_file_steps, source_directory,
                            enable_gpu, description, base_image, base_image_registry, cuda_version):
    # create Environment object based on the environment related inputs
    environment = get_local_or_cloud_environment(workspace, environment_name, environment_version,
                                                 environment_directory)

    inference_config = None
    if (not inference_config_file):
        # create InferenceConfig object from inline parameters
        inference_config = InferenceConfig(
            entry_script=entry_script, environment=environment, runtime=runtime, conda_file=conda_file,
            extra_docker_file_steps=extra_docker_file_steps, source_directory=source_directory, enable_gpu=enable_gpu,
            base_image=base_image, base_image_registry=base_image_registry, cuda_version=cuda_version,
            description=description)
    else:
        inference_config_from_file = file_to_inference_config(workspace, inference_config_file, description,
                                                              environment)
        inference_config = params_to_inference_config(entry_script, runtime, conda_file, extra_docker_file_steps,
                                                      source_directory, enable_gpu, description, base_image,
                                                      base_image_registry, cuda_version, inference_config_from_file)
    return inference_config


def create_deploy_config(deploy_config_file, compute_type, cpu_cores, memory_gb, tags_dict, properties_dict,
                         description, location, auth_enabled, ssl_enabled, enable_app_insights,
                         ssl_cert_pem_file, ssl_key_pem_file, ssl_cname, dns_name_label, autoscale_enabled,
                         autoscale_min_replicas, autoscale_max_replicas, autoscale_refresh_seconds,
                         autoscale_target_utilization, collect_model_data, scoring_timeout_ms,
                         replica_max_concurrent_requests, max_request_wait_time, num_replicas, primary_key,
                         secondary_key, tags, properties, gpu_cores, period_seconds,
                         initial_delay_seconds, timeout_seconds, success_threshold, failure_threshold, namespace, port,
                         token_auth_enabled, tls_mode, certificate_fingerprints, sku, osType):
    deploy_config = None
    if (not deploy_config_file):
        if compute_type == "mir":
            deploy_config = MirWebservice.deploy_configuration(
                autoscale_enabled=autoscale_enabled, autoscale_min_replicas=autoscale_min_replicas,
                autoscale_max_replicas=autoscale_max_replicas, autoscale_refresh_seconds=autoscale_refresh_seconds,
                autoscale_target_utilization=autoscale_target_utilization, collect_model_data=collect_model_data,
                auth_enabled=auth_enabled, cpu_cores=cpu_cores, memory_gb=memory_gb,
                scoring_timeout_ms=scoring_timeout_ms,
                replica_max_concurrent_requests=replica_max_concurrent_requests,
                max_request_wait_time=max_request_wait_time, num_replicas=num_replicas,
                tags=tags, properties=properties, description=description,
                tls_mode=tls_mode, certificate_fingerprints=certificate_fingerprints, sku=sku, gpu_cores=gpu_cores,
                osType=osType, enable_app_insights=enable_app_insights)
    else:
        deploy_config_from_file = file_to_deploy_config(deploy_config_file, tags_dict, properties_dict,
                                                        description, compute_type)
        if compute_type == "mir":
            deploy_config = params_to_mir_config(autoscale_enabled, autoscale_min_replicas, autoscale_max_replicas,
                                                 autoscale_refresh_seconds,
                                                 autoscale_target_utilization, collect_model_data, auth_enabled,
                                                 cpu_cores, memory_gb, scoring_timeout_ms,
                                                 replica_max_concurrent_requests, max_request_wait_time,
                                                 num_replicas, tags, properties, description, tls_mode,
                                                 certificate_fingerprints, sku, gpu_cores, osType, enable_app_insights,
                                                 deploy_config_from_file)
    return deploy_config


def file_to_inference_config(workspace, inference_config_file, description, environment_input=None):
    """Takes an inference_config_file and returns the InferenceConfig object
    :param workspace: current AzML workspace
    :type workspace: azureml.core.Workspace
    :param inference_config_file: Input file with InferenceConfig parameters
    :type inference_config_file: varies
    :param description: description for the InferenceConfig.
    :type description: string
    :param environment_input: Environment object to use for the image.
    :type environment_input: azureml.core.Environment or None
    :return: InferenceConfig object
    :rtype: azureml.core.model.InferenceConfig
    """
    try:
        with open(inference_config_file) as inference_file_stream:
            inference_config_obj = file_stream_to_object(inference_file_stream)

            # Retrieve Environment object from the InferenceConfig file
            inference_config_environment = inference_config_obj.get('environment')
            environment = None
            if inference_config_environment is None:
                environment = environment_input
            else:
                # deserialize into Environment object
                environment = Environment._deserialize_and_add_to_object(inference_config_environment)

            inference_config = InferenceConfig(
                entry_script=inference_config_obj.get('entryScript'),
                runtime=inference_config_obj.get('runtime'),
                conda_file=inference_config_obj.get('condaFile'),
                extra_docker_file_steps=inference_config_obj.get('extraDockerfileSteps'),
                source_directory=inference_config_obj.get('sourceDirectory'),
                enable_gpu=inference_config_obj.get('enableGpu'),
                base_image=inference_config_obj.get('baseImage'),
                base_image_registry=inference_config_obj.get('baseImageRegistry'),
                cuda_version=inference_config_obj.get('cudaVersion'),
                environment=environment,
                description=description)
            return inference_config
    except WebserviceException as web_service_ex:
        # InferenceConfig validation failure will raise WebserviceException, so we wrap it with MlCliError
        raise MlCliError('Invalid inference configuration.', content=web_service_ex)
    except Exception as ex:
        raise MlCliError('Error parsing --inference-config-file. Must be valid JSON or YAML file.', content=ex)


def file_stream_to_object(file_stream):
    """Expects a YAML or JSON file_stream and returns the file object
    :param file_stream: File stream from with open(file) as file_stream
    :type file_stream:
    :return: File dictionary
    :rtype: dict
    """
    file_data = file_stream.read()

    try:
        return yaml.safe_load(file_data)
    except Exception:
        pass

    try:
        return json.loads(file_data)
    except Exception as ex:
        raise MlCliError('Error while parsing file. Must be valid JSON or YAML file.', content=ex)


def collect_input_models(workspace, model_metadata_files, models):
    registered_models = []

    if model_metadata_files:
        for model_meta_file in model_metadata_files:
            with open(model_meta_file, 'r') as infile:
                model_metadata = json.load(infile)
                if model_metadata[CLI_METADATA_FILE_WORKSPACE_KEY] != workspace.name or \
                        model_metadata[CLI_METADATA_FILE_RG_KEY] != workspace.resource_group:
                    raise MlCliError('Model metadata file \'{}\' contains information for a model in a workspace '
                                     'that does not match the one provided for model packaging. If the model '
                                     'specified in the file is intended to be used, please either register it '
                                     'in the workspace provided to this command, or specify the corresponding '
                                     'workspace to this command.'.format(model_meta_file))
                registered_models.append(
                    Model(workspace, id=model_metadata[MODEL_METADATA_FILE_ID_KEY]))

    if models:
        for model_id in models:
            registered_models.append(Model(workspace, id=model_id))

    return registered_models


def parse_tags(tags):
    tags_dict = None
    if tags:
        tags_dict = dict()
        for tag in tags:
            if '=' not in tag:
                raise MlCliError('Error, tags must be entered in the following format: key=value')
            key, value = tag.partition("=")[::2]
            tags_dict[key] = value
    return tags_dict


def parse_properties(properties):
    properties_dict = None
    if properties:
        properties_dict = dict()
        for prop in properties:
            if '=' not in prop:
                raise MlCliError('Error, properties must be entered in the following format: key=value')
            key, value = prop.partition("=")[::2]
            properties_dict[key] = value
    return properties_dict


def get_home_dir():
    """
    Function to find home directory on windows or linux environment
    :return: str - path to home directory
    """
    return os.path.expanduser('~')


cli_context = CommandLineInterfaceContext()


def str_to_bool(str):
    try:
        str = str.lower()
        if str == 'true':
            return True
        elif str == 'false':
            return False
        else:
            return None
    except AttributeError as ae:
        logger.debug("str_to_bool({}) caught exception: {}".format(str, ae))
        return None


def try_get_local_service(workspace, name, raise_exception=False):
    """Check whether a local service exists

    This is for CLI layer to check whether same name local service exists in the workspace
    so it can handle the logic (e.g. name conflict in creation) accordingly

    :param workspace: The current AzureML Workspace object
    :type workspace: azureml.core.workspace.Workspace
    :param name: The service name to look up
    :type name: string
    :param name: Whether to propagate the exception to called
    :type name: bool
    :return: Service object, or None if no such exception exists
    :rtype: azureml.core.webservice.LocalWebservice
    """
    try:
        # Note: Because there are many scenarios in which Exception (or even WebserviceException)
        # is thrown but we don't know whether service exists or not. e.g. cannot get local docker
        # client, cannot get docker host container etc., we pass the must_exist param as True and
        # explicitly check exception type (== WebserviceException) and message (contains WebserviceNotFound)
        # to detect the scenario same name local service doesn't exist.
        service = LocalWebservice(workspace, name, must_exist=True)
        return service
    except Exception as e:
        if isinstance(e, WebserviceException) and 'WebserviceNotFound' in e.message:
            # Same name local service doesn't exist
            return None
        else:
            # This is the case we hit exception which is not because of nonexisted local service
            # Handle the exception as per the raise_exception parameter
            if raise_exception:
                raise e
            else:
                # don't propage the exception to caller. instead, just log warning and return None
                logger.warning("Failed to check LocalWebservice existence: {}".format(e))
                return None


def params_to_inference_config(entry_script, runtime, conda_file, extra_docker_file_steps, source_directory,
                               enable_gpu, description, base_image, base_image_registry, cuda_version,
                               config_from_file):
    """Takes inference config parameters and returns an InferenceConfig object.
    The parameters in this method will overwrite attributes from the config
    :param entry_script: Path to local file that contains the code to run for the image
    :type entry_script: str
    :param runtime: Which runtime to use for the image. Current supported runtimes are 'spark-py' and 'python'
    :type runtime: str
    :param conda_file: Path to local file containing a conda environment definition to use for the image
    :type conda_file: str
    :param extra_docker_file_steps: Path to local file containing extra Docker steps to run when setting up image
    :type extra_docker_file_steps: str
    :param source_directory: paths to folders that contains all files to create the image
    :type source_directory: : str
    :param enable_gpu: Whether or not to enable GPU support in the image. The GPU image must be used on
        Microsoft Azure Services such as Azure Container Instances, Azure Machine Learning Compute,
        Azure Virtual Machines, and Azure Kubernetes Service.  Defaults to False
    :type enable_gpu: bool
    :param description: A description to give this image
    :type description: str
    :param base_image: A custom image to be used as base image. If no base image is given then the base image
        will be used based off of given runtime parameter.
    :type base_image: str
    :param base_image_registry: Image registry that contains the base image.
    :type base_image_registry: azureml.core.container_registry.ContainerRegistry
    :param cuda_version: Version of CUDA to install for images that need GPU support. The GPU image must be used on
        Microsoft Azure Services such as Azure Container Instances, Azure Machine Learning Compute,
        Azure Virtual Machines, and Azure Kubernetes Service. Supported versions are 9.0, 9.1, and 10.0.
        If 'enable_gpu' is set, this defaults to '9.1'.
    :type cuda_version: str
    :param config_from_file: Attributes from this object will be used to create the new InferenceConfig object.
        Parameters provided to this method take precedence over the attributes given by this config object parameter
    :type config_from_file: azureml.core.model.InferenceConfig
    :return: InferenceConfig object
    :rtype: azureml.core.model.InferenceConfig
    """
    return InferenceConfig(
        entry_script=entry_script if entry_script else config_from_file.entry_script,
        runtime=runtime if runtime else config_from_file.runtime,
        conda_file=conda_file if conda_file else config_from_file.conda_file,
        extra_docker_file_steps=extra_docker_file_steps if extra_docker_file_steps
        else config_from_file.extra_docker_file_steps,
        source_directory=source_directory if source_directory else config_from_file.source_directory,
        enable_gpu=enable_gpu if enable_gpu is not None else config_from_file.enable_gpu,
        base_image=base_image if base_image else config_from_file.base_image,
        base_image_registry=base_image_registry if base_image_registry else config_from_file.base_image_registry,
        cuda_version=cuda_version if cuda_version else config_from_file.cuda_version,
        environment=config_from_file.environment,
        description=description if description else config_from_file.description)


def file_to_deploy_config(deploy_config_file, tags_dict, properties_dict, description, compute_type):
    """Takes a deploy_config_file and returns the deployment config object
    :param deploy_config_file: Input file with deployment config parameters
    :type deploy_config_file: varies
    :return: Deployment config object
    :rtype: varies
    """
    try:
        with open(deploy_config_file, 'r') as deploy_file_stream:
            deploy_config_obj = file_stream_to_object(deploy_file_stream)
            if (not compute_type):
                compute_type_key = 'computeType'
                if compute_type_key not in deploy_config_obj:
                    raise MlCliError(
                        "need to specify {} in --deploy-config-file".format(compute_type_key))
                deploy_compute_type = deploy_config_obj[compute_type_key].lower()
            deploy_compute_type = compute_type.lower()

            if deploy_compute_type == "mir":
                # mir deployment
                config = MirWebservice.deploy_configuration(
                    autoscale_enabled=deploy_config_obj.get('autoScaler', {}).get('autoscaleEnabled'),
                    autoscale_min_replicas=deploy_config_obj.get('autoScaler', {}).get('minReplicas'),
                    autoscale_max_replicas=deploy_config_obj.get('autoScaler', {}).get('maxReplicas'),
                    autoscale_refresh_seconds=deploy_config_obj.get('autoScaler', {}).get('refreshPeriodInSeconds'),
                    autoscale_target_utilization=deploy_config_obj.get('autoScaler', {}).get('targetUtilization'),
                    collect_model_data=deploy_config_obj.get('dataCollection', {}).get('storageEnabled'),
                    auth_enabled=deploy_config_obj.get('authEnabled'),
                    cpu_cores=deploy_config_obj.get('containerResourceRequirements', {}).get('cpu'),
                    memory_gb=deploy_config_obj.get('containerResourceRequirements', {}).get('memoryInGB'),
                    scoring_timeout_ms=deploy_config_obj.get('scoringTimeoutMs'),
                    replica_max_concurrent_requests=deploy_config_obj.get('maxConcurrentRequestsPerContainer'),
                    max_request_wait_time=deploy_config_obj.get('maxQueueWaitMs'),
                    num_replicas=deploy_config_obj.get('numReplicas'),
                    tags=tags_dict,
                    properties=properties_dict,
                    description=description,
                    tls_mode=deploy_config_obj.get('tlsMode'),
                    certificate_fingerprints=deploy_config_obj.get('certificateFingerprints'),
                    sku=deploy_config_obj.get('sku'),
                    gpu_cores=deploy_config_obj.get('containerResourceRequirements', {}).get('gpu'),
                    osType=deploy_config_obj.get('osType'),
                    enable_app_insights=deploy_config_obj.get('appInsightsEnabled')
                )
            else:
                raise MlCliError("unknown deployment type: {}".format(deploy_compute_type))
            return config
    except WebserviceException as web_service_ex:
        # Deployment config validation failure will raise WebserviceException, so we wrap it with MlCliError
        raise MlCliError('Invalid deployment configuration.', content=web_service_ex)
    except Exception as ex:
        raise MlCliError('Error parsing --deploy-config-file. Must be valid JSON or YAML file.', content=ex)


def params_to_mir_config(autoscale_enabled, autoscale_min_replicas, autoscale_max_replicas, autoscale_refresh_seconds,
                         autoscale_target_utilization, collect_model_data, auth_enabled, cpu_cores, memory_gb,
                         scoring_timeout_ms, replica_max_concurrent_requests, max_request_wait_time,
                         num_replicas, tags, properties, description, tls_mode, certificate_fingerprints,
                         sku, gpu_cores, osType, enable_app_insights, config_from_file):
    """Takes mir config parameters and returns an MirServiceDeploymentConfiguration object.
    The parameters in this method will overwrite attributes from the config
    :param autoscale_enabled: Whether or not to enable autoscaling for this Webservice.
        Defaults to True if num_replicas is None
    :type autoscale_enabled: bool
    :param autoscale_min_replicas: The minimum number of containers to use when autoscaling this Webservice.
        Defaults to 1
    :type autoscale_min_replicas: int
    :param autoscale_max_replicas: The maximum number of containers to use when autoscaling this Webservice.
        Defaults to 10
    :type autoscale_max_replicas: int
    :param autoscale_refresh_seconds: How often the autoscaler should attempt to scale this Webservice.
        Defaults to 1
    :type autoscale_refresh_seconds: int
    :param autoscale_target_utilization: The target utilization (in percent out of 100) the autoscaler should
        attempt to maintain for this Webservice. Defaults to 70
    :type autoscale_target_utilization: int
    :param auth_enabled: Whether or not to enable auth for this Webservice. Defaults to True
    :type auth_enabled: bool
    :param cpu_cores: The number of cpu cores to allocate for this Webservice. Can be a decimal. Defaults to 0.1
    :type cpu_cores: float
    :param memory_gb: The amount of memory (in GB) to allocate for this Webservice. Can be a decimal.
        Defaults to 0.5
    :type memory_gb: float
    :param scoring_timeout_ms: A timeout to enforce for scoring calls to this Webservice. Defaults to 60000
    :type scoring_timeout_ms: int
    :param replica_max_concurrent_requests: The number of maximum concurrent requests per node to allow for this
        Webservice. Defaults to 1
    :type replica_max_concurrent_requests: int
    :param max_request_wait_time: The maximum amount of time a request will stay in the queue (in milliseconds)
        before returning a 503 error. Defaults to 500
    :type max_request_wait_time: int
    :param num_replicas: The number of containers to allocate for this Webservice. No default, if this parameter
        is not set then the autoscaler is enabled by default.
    :type num_replicas: int
    :param tags: Dictionary of key value tags to give this Webservice
    :type tags: dict[str, str]
    :param properties: Dictionary of key value properties to give this Webservice. These properties cannot
        be changed after deployment, however new key value pairs can be added
    :type properties: dict[str, str]
    :param description: A description to give this Webservice
    :type description: str
    :param tls_mode: TLS mode for scoring authentication, options are "DISABLED", "SIMPLE", "MUTUAL"
    :type tls_mode: str
    :param certificate_fingerprints: List of fingerprints for scoring authentication
    :type certificate_fingerprints: :class:`list[str]`
    :param sku: Azure SKU type for MIR compute
    :type sku: str
    :param gpu_cores: The number of gpu cores to allocate for this Webservice. Defaults to 0.
    :type gpu_cores: int
    :param osType: OS type of the mir service, valid options are "Linux", "Windows"
    :type osType: str
    :param enable_app_insights: Whether or not to enable Application Insights logging for this Webservice.
        Defaults to False
    :type enable_app_insights: bool
    :param config_from_file: Attributes from this object will be used to create the new
        MirServiceDeploymentConfiguration object. Parameters provided to this method take precedence over the
        attributes given by this config object parameter
    :type config_from_file: azureml.contrib.mir.webservice.MirServiceDeploymentConfiguration
    :return: MirServiceDeploymentConfiguration object
    :rtype: azureml.contrib.mir.webservice.MirServiceDeploymentConfiguration
    """

    if not autoscale_min_replicas:
        autoscale_min_replicas = config_from_file.autoscale_min_replicas
    if not autoscale_max_replicas:
        autoscale_max_replicas = config_from_file.autoscale_max_replicas
    if not autoscale_refresh_seconds:
        autoscale_refresh_seconds = config_from_file.autoscale_refresh_seconds
    if not autoscale_target_utilization:
        autoscale_target_utilization = config_from_file.autoscale_target_utilization
    if collect_model_data is None:
        collect_model_data = config_from_file.collect_model_data
    if not replica_max_concurrent_requests:
        replica_max_concurrent_requests = config_from_file.replica_max_concurrent_requests
    if not max_request_wait_time:
        max_request_wait_time = config_from_file.max_request_wait_time
    if not max_request_wait_time:
        max_request_wait_time = config_from_file.max_request_wait_time

    return MirWebservice.deploy_configuration(
        autoscale_enabled=autoscale_enabled if autoscale_enabled is not None else config_from_file.autoscale_enabled,
        autoscale_min_replicas=autoscale_min_replicas,
        autoscale_max_replicas=autoscale_max_replicas,
        autoscale_refresh_seconds=autoscale_refresh_seconds,
        autoscale_target_utilization=autoscale_target_utilization,
        collect_model_data=collect_model_data,
        auth_enabled=auth_enabled if auth_enabled is not None else config_from_file.auth_enabled,
        cpu_cores=cpu_cores if cpu_cores else config_from_file.cpu_cores,
        memory_gb=memory_gb if memory_gb else config_from_file.memory_gb,
        scoring_timeout_ms=scoring_timeout_ms if scoring_timeout_ms else config_from_file.scoring_timeout_ms,
        replica_max_concurrent_requests=replica_max_concurrent_requests,
        max_request_wait_time=max_request_wait_time,
        num_replicas=num_replicas if num_replicas else config_from_file.num_replicas,
        tags=tags if tags else config_from_file.tags,
        properties=properties if properties else config_from_file.properties,
        description=description if description else config_from_file.description,
        tls_mode=tls_mode if tls_mode else config_from_file.tls_mode,
        certificate_fingerprints=certificate_fingerprints
        if certificate_fingerprints else config_from_file.certificate_fingerprints,
        sku=sku if sku else config_from_file.sku,
        gpu_cores=gpu_cores if gpu_cores else config_from_file.gpu_cores,
        osType=osType if osType else config_from_file.osType,
        enable_app_insights=enable_app_insights
        if enable_app_insights is not None else config_from_file.enable_app_insights)
