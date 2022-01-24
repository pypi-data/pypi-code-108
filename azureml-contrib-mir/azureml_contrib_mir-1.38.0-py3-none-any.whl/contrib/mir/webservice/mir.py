# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for managing the Azure MIR Webservices in Azure Machine Learning."""

import logging
import json
from azureml.core.webservice import Webservice
from azureml.exceptions import WebserviceException
import copy
import requests
from ._util import mir_service_payload_template
from azureml._base_sdk_common.tracking import global_tracking_info_registry
from azureml._restclient.clientbase import ClientBase
from azureml._model_management._constants import MIR_WEBSERVICE_TYPE
from azureml._model_management._util import build_and_validate_no_code_environment_image_request
from azureml._model_management._util import convert_parts_to_environment
from azureml._model_management._util import get_requests_session
from azureml.core.environment import Environment
from azureml.core.model import Model
from azureml.core.webservice.webservice import WebserviceDeploymentConfiguration, ContainerResourceRequirements
from azureml.core.webservice.webservice import LivenessProbeRequirements, AutoScaler, DataCollection
from azureml.core.webservice.webservice import WebServiceAccessToken

module_logger = logging.getLogger(__name__)


class MirWebservice(Webservice):
    """Class for MIR Webservices."""

    _expected_payload_keys = Webservice._expected_payload_keys + ['autoScaler', 'authEnabled',
                                                                  'computeName',
                                                                  'containerResourceRequirements',
                                                                  'dataCollection',
                                                                  'maxConcurrentRequestsPerContainer',
                                                                  'numReplicas', 'scoringTimeoutMs',
                                                                  'scoringUri',
                                                                  'livenessProbeRequirements', 'sku',
                                                                  'deploymentStatus']
    _webservice_type = MIR_WEBSERVICE_TYPE

    def _initialize(self, workspace, obj_dict, **kwargs):
        """Initialize the Webservice instance.

        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :param obj_dict:
        :type obj_dict: dict
        :return:
        :rtype: None
        """
        # Validate obj_dict with _expected_payload_keys
        if ("validate_payload" not in kwargs or kwargs["validate_payload"]):
            MirWebservice._validate_get_payload(obj_dict)

        # Initialize common Webservice attributes
        super(MirWebservice, self)._initialize(workspace, obj_dict)

        # Initialize expected MIR specific attributes
        self.enable_app_insights = obj_dict.get('appInsightsEnabled')
        self.autoscaler = AutoScaler.deserialize(obj_dict['autoScaler'])
        self.compute_name = obj_dict.get('computeName')
        self.container_resource_requirements = \
            ContainerResourceRequirements.deserialize(obj_dict.get('containerResourceRequirements'))
        self.liveness_probe_requirements = \
            LivenessProbeRequirements.deserialize(obj_dict.get('livenessProbeRequirements'))
        self.data_collection = DataCollection.deserialize(obj_dict.get('dataCollection'))
        self.max_concurrent_requests_per_container = obj_dict.get('maxConcurrentRequestsPerContainer')
        self.num_replicas = obj_dict.get('numReplicas')
        self.scoring_timeout_ms = obj_dict.get('scoringTimeoutMs')
        self.scoring_uri = obj_dict.get('scoringUri')
        self.deployment_status = RevisionStatus.deserialize(obj_dict.get('deploymentStatus'))
        self.tls_mode = obj_dict.get('tlsMode')
        self.certificate_fingerprints = obj_dict.get('certificateFingerprints')
        self.sku = obj_dict.get('sku')
        self.osType = obj_dict.get('osType')
        env_image_request = obj_dict.get('environmentImageRequest')
        env_dict = env_image_request.get('environment') if env_image_request else None
        self.environment = Environment._deserialize_and_add_to_object(env_dict) if env_dict else None
        models = obj_dict.get('models')
        self.models = [Model.deserialize(workspace, model_payload) for model_payload in models] if models else []

    def __repr__(self):
        """Return the string representation of the MirWebservice object.

        :return: String representation of the MirWebservice object
        :rtype: str
        """
        return super().__repr__()

    @staticmethod
    def deploy_configuration(autoscale_enabled=None, autoscale_min_replicas=None, autoscale_max_replicas=None,
                             autoscale_refresh_seconds=None, autoscale_target_utilization=None,
                             collect_model_data=None, auth_enabled=None, cpu_cores=None, memory_gb=None,
                             scoring_timeout_ms=None, replica_max_concurrent_requests=None,
                             max_request_wait_time=None, num_replicas=None, tags=None, properties=None,
                             description=None, tls_mode=None, certificate_fingerprints=None, sku=None,
                             gpu_cores=None, osType=None, enable_app_insights=None):

        """Create a configuration object for deploying to an MIR compute target.

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
        :param collect_model_data: Whether or not to enable model data collection for this Webservice.
            Defaults to False
        :type collect_model_data: bool
        :param auth_enabled: Whether or not to enable key auth for this Webservice. Defaults to False. MIR does not
            currently support authorization.
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
        :param sku: Azure SKU type for MIR compute, valid options are "Standard_F4s_v2", & "Standard_F8s_v2"
        :type sku: str
        :param gpu_cores: The number of gpu cores to allocate for this Webservice. Defaults to 0
        :type gpu_cores: int
        :param osType: OS type of the mir service, valid options are "Linux", "Windows"
        :type osType: str
        :param enable_app_insights: Whether or not to enable Application Insights logging for this Webservice.
            Defaults to False.
        :type enable_app_insights: bool
        :return: A configuration object to use when deploying a Webservice object.
            The first and last characters cannot be hyphens.
        :rtype: MirServiceDeploymentConfiguration
        :raises: azureml.exceptions.WebserviceException
        """
        config = MirServiceDeploymentConfiguration(autoscale_enabled, autoscale_min_replicas, autoscale_max_replicas,
                                                   autoscale_refresh_seconds, autoscale_target_utilization,
                                                   collect_model_data, auth_enabled, cpu_cores, memory_gb,
                                                   scoring_timeout_ms, replica_max_concurrent_requests,
                                                   max_request_wait_time, num_replicas, tags, properties,
                                                   description, tls_mode, certificate_fingerprints, sku, gpu_cores,
                                                   osType, enable_app_insights)
        return config

    def _deploy(self, workspace, name, image, deployment_config, deployment_target, overwrite=False):
        """Deploy the Webservice.

        :raises: azureml.exceptions.WebserviceException
        """
        raise NotImplementedError("MIR Webservices does not support deployments without environment.")

    def run(self, input_data):
        """Call this Webservice with the provided input.

        :param input_data: The input to call the Webservice with
        :type input_data: varies
        :return: The result of calling the Webservice
        :rtype: dict
        :raises: azureml.exceptions.WebserviceException
        """
        if not self.scoring_uri:
            raise WebserviceException('Error attempting to call webservice, scoring_uri unavailable. '
                                      'This could be due to a failed deployment, or the service is not ready yet.\n'
                                      'Current State: {}\n'
                                      'Errors: {}'.format(self.state, self.error), logger=module_logger)

        resp = ClientBase._execute_func(self._webservice_session.post, self.scoring_uri, data=input_data)

        if resp.status_code == 401:
            if self.auth_enabled:
                raise WebserviceException("Auth not enabled in MIR")

            # If auth failed, append refreshed access token to headers for MIR (token auth is always enabled for MIR).
            access_token_obj = self.get_access_token()
            self._refresh_token_time = access_token_obj.refresh_after
            self._session.headers.update({'Authorization': 'Bearer ' + access_token_obj.access_token})
            resp = ClientBase._execute_func(self._webservice_session.post, self.scoring_uri, data=input_data)

        if resp.status_code == 200:
            return resp.json()
        else:
            raise WebserviceException('Received bad response from service:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content),
                                      logger=module_logger)

    def update(self, cpu_cores=None, gpu_cores=None, memory_gb=None, enable_app_insights=None,
               scoring_timeout_ms=None, replica_max_concurrent_requests=None,
               num_replicas=None, models=None, inference_config=None, sku=None,
               tags=None, properties=None, description=None):
        """Update the MirWebservice with provided properties.

        Values left as None will remain unchanged in this Webservice.

        :param cpu_cores: The number of cpu cores to allocate for this Webservice. Can be a decimal
        :type cpu_cores: float
        :param gpu_cores: The number of gpu cores to allocate for this Webservice. Must be an integer
        :type gpu_cores: int
        :param memory_gb: The amount of memory (in GB) to allocate for this Webservice. Can be a decimal
        :type memory_gb: float
        :param enable_app_insights: Whether or not to enable Application Insights logging for this Webservice.
            Defaults to False.
        :type enable_app_insights: bool
        :param scoring_timeout_ms: A timeout to enforce for scoring calls to this Webservice
        :type scoring_timeout_ms: int
        :param replica_max_concurrent_requests: The number of maximum concurrent requests per replica to allow for this
            Webservice.
        :type replica_max_concurrent_requests: int
        :param max_request_wait_time: The maximum amount of time a request will stay in the queue (in milliseconds)
            before returning a 503 error
        :type max_request_wait_time: int
        :param num_replicas: The number of containers to allocate for this Webservice
        :type num_replicas: int
        :param models: A list of Model objects to package with the updated service
        :type models: builtin.list[azureml.core.Model]
        :param inference_config: An InferenceConfig object used to provide the required model deployment properties.
        :type inference_config: azureml.core.model.InferenceConfig
        :param sku: Azure SKU type for MIR compute, valid options are "Standard_A2_v2", "Standard_F16", &
            "Standard_DS2_v2"
        :type sku: str
        :param tags: Dictionary of key value tags to give this Webservice. Will replace existing tags.
        :type tags: dict[str, str]
        :param properties: Dictionary of key value properties to add to existing properties dictionary
        :type properties: dict[str, str]
        :param description: A description to give this Webservice
        :type description: str
        :raises: :class:`azureml.exceptions.WebserviceException`
        """
        if not cpu_cores and not memory_gb \
                and not gpu_cores and enable_app_insights is None and not scoring_timeout_ms \
                and not replica_max_concurrent_requests and not num_replicas \
                and models is None and inference_config is None and sku is None \
                and tags is None and properties is None and not description:
            raise WebserviceException('No parameters provided to update.', logger=module_logger)

        headers = {'Content-Type': 'application/json-patch+json'}
        headers.update(self._auth.get_authentication_header())
        params = {}

        self._validate_update(cpu_cores, gpu_cores, memory_gb, enable_app_insights,
                              scoring_timeout_ms, replica_max_concurrent_requests,
                              num_replicas, models, inference_config, sku,
                              tags, properties, description)

        patch_list = []

        if inference_config:
            if not models:
                models = self.image.models if self.image else self.models

            if self.environment:  # Use the new environment handling
                inference_config, _ = convert_parts_to_environment(self.name, inference_config)

                environment_image_request = \
                    inference_config._build_environment_image_request(self.workspace, [model.id for model in models])
                patch_list.append({'op': 'replace', 'path': '/environmentImageRequest',
                                   'value': environment_image_request})
        elif models is not None:
            # No-code deploy.
            environment_image_request = build_and_validate_no_code_environment_image_request(models)
            patch_list.append({'op': 'replace', 'path': '/environmentImageRequest',
                               'value': environment_image_request})

        properties = properties or {}
        properties.update(global_tracking_info_registry.gather_all())

        if sku is not None:
            patch_list.append({'op': 'replace', 'path': '/sku', 'value': sku})

        if cpu_cores:
            patch_list.append({'op': 'replace', 'path': '/containerResourceRequirements/cpu', 'value': cpu_cores})
        if gpu_cores:
            patch_list.append({'op': 'replace', 'path': '/containerResourceRequirements/gpu', 'value': gpu_cores})
        if memory_gb:
            patch_list.append({'op': 'replace', 'path': '/containerResourceRequirements/memoryInGB',
                               'value': memory_gb})

        if enable_app_insights is not None:
            patch_list.append({'op': 'replace', 'path': '/appInsightsEnabled', 'value': enable_app_insights})
        if scoring_timeout_ms:
            patch_list.append({'op': 'replace', 'path': '/scoringTimeoutMs', 'value': scoring_timeout_ms})
        if replica_max_concurrent_requests:
            patch_list.append({'op': 'replace', 'path': '/maxConcurrentRequestsPerContainer',
                               'value': replica_max_concurrent_requests})

        if num_replicas:
            patch_list.append({'op': 'replace', 'path': '/numReplicas', 'value': num_replicas})

        if tags is not None:
            patch_list.append({'op': 'replace', 'path': '/kvTags', 'value': tags})
        if properties is not None:
            for key in properties:
                patch_list.append({'op': 'add', 'path': '/properties/{}'.format(key), 'value': properties[key]})
        if description:
            patch_list.append({'op': 'replace', 'path': '/description', 'value': description})

        resp = ClientBase._execute_func(get_requests_session().patch, self._mms_endpoint, headers=headers,
                                        params=params, json=patch_list)

        if resp.status_code == 200:
            content = resp.content
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            service_payload = json.loads(content)
            if 'operationId' in service_payload:
                create_operation_status_id = service_payload['operationId']
                base_url = '/'.join(self._mms_endpoint.split('/')[:-2])
                operation_url = base_url + '/operations/{}'.format(create_operation_status_id)
                self._operation_endpoint = operation_url
            self.update_deployment_state()
        elif resp.status_code == 202:
            if 'Operation-Location' in resp.headers:
                operation_location = resp.headers['Operation-Location']
            else:
                raise WebserviceException('Missing response header key: Operation-Location', logger=module_logger)
            create_operation_status_id = operation_location.split('/')[-1]
            base_url = '/'.join(self._mms_endpoint.split('/')[:-2])
            operation_url = base_url + '/operations/{}'.format(create_operation_status_id)
            self._operation_endpoint = operation_url
            self.update_deployment_state()
        else:
            raise WebserviceException('Received bad response from Model Management Service:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content),
                                      logger=module_logger)

    def _validate_update(self, cpu_cores=None, gpu_cores=None, memory_gb=None, enable_app_insights=None,
                         scoring_timeout_ms=None, replica_max_concurrent_requests=None,
                         num_replicas=None, models=None,
                         inference_config=None, sku=None, tags=None,
                         properties=None, description=None):
        """Validate the values provided to update the MIR Webservice.

        :param cpu_cores: The number of cpu cores to allocate for this Webservice. Can be a decimal
        :type cpu_cores: float
        :param gpu_cores: The number of gpu cores to allocate for this Webservice. Must be an integer
        :type gpu_cores: int
        :param memory_gb: The amount of memory (in GB) to allocate for this Webservice. Can be a decimal
        :type memory_gb: float
        :param enable_app_insights: Whether or not to enable Application Insights logging for this Webservice.
            Defaults to False.
        :type enable_app_insights: bool
        :param scoring_timeout_ms: A timeout to enforce for scoring calls to this Webservice
        :type scoring_timeout_ms: int
        :param replica_max_concurrent_requests: The number of maximum concurrent requests per replica to allow for this
            Webservice.
        :type replica_max_concurrent_requests: int
        :param num_replicas: The number of containers to allocate for this Webservice
        :type num_replicas: int
        :param models: A list of Model objects to package with the updated service
        :type models: builtin.list[azureml.core.Model]
        :param inference_config: An InferenceConfig object used to provide the required model deployment properties.
        :type inference_config: azureml.core.model.InferenceConfig
        :param sku: Azure SKU type for MIR compute, valid options are "Standard_A2_v2", "Standard_F16", &
            "Standard_DS2_v2"
        :type sku: str
        :param tags: Dictionary of key value tags to give this Webservice. Will replace existing tags.
        :type tags: dict[str, str]
        :param properties: Dictionary of key value properties to add to existing properties dictionary
        :type properties: dict[str, str]
        :param description: A description to give this Webservice
        :type description: str
        :raises: :class:`azureml.exceptions.WebserviceException`
        """
        error = ""
        if inference_config and inference_config.environment and self.image:
            error += 'Error, unable to use Environment object to update Webservice created with Image object.\n'
        if cpu_cores and cpu_cores <= 0:
            error += 'Error, cpu_cores must be greater than zero.\n'
        if memory_gb and memory_gb <= 0:
            error += 'Error, memory_gb must be greater than zero.\n'
        if gpu_cores and gpu_cores <= 0:
            error += 'Error, gpu_cores must be greater than zero.\n'
        if scoring_timeout_ms and scoring_timeout_ms <= 0:
            error += 'Error, scoring_timeout_ms must be greater than zero.\n'
        if replica_max_concurrent_requests and replica_max_concurrent_requests <= 0:
            error += 'Error, replica_max_concurrent_requests must be greater than zero.\n'
        if num_replicas and num_replicas <= 0:
            error += 'Error, num_replicas must be greater than zero.\n'
        if inference_config is None and models and \
                (len(models) != 1 or models[0].model_framework not in Model._SUPPORTED_FRAMEWORKS_FOR_NO_CODE_DEPLOY):
            error += 'Error, both "models" and "inference_config" inputs must be provided in order ' \
                     'to update the models.\n'
        if error:
            raise WebserviceException(error, logger=module_logger)

    def serialize(self):
        """Convert this Webservice into a json serialized dictionary.

        :return: The json representation of this Webservice
        :rtype: dict
        """
        properties = super(MirWebservice, self).serialize()
        autoscaler = self.autoscaler.serialize() if self.autoscaler else None
        container_resource_requirements = self.container_resource_requirements.serialize() \
            if self.container_resource_requirements else None
        data_collection = self.data_collection.serialize() if self.data_collection else None
        image = self.image.serialize() if self.image else None
        env_details = Environment._serialize_to_dict(self.environment) if self.environment else None
        model_details = [model.serialize() for model in self.models] if self.models else None
        deployment_status = self.deployment_status.serialize() if self.deployment_status else None
        mir_properties = {'appInsightsEnabled': self.enable_app_insights, 'autoScaler': autoscaler,
                          'computeName': self.compute_name, 'authEnabled': self.auth_enabled,
                          'containerResourceRequirements': container_resource_requirements,
                          'dataCollection': data_collection, 'imageId': self.image_id,
                          'imageDetails': image,
                          'maxConcurrentRequestsPerContainer': self.max_concurrent_requests_per_container,
                          'numReplicas': self.num_replicas, 'deploymentStatus': deployment_status,
                          'scoringTimeoutMs': self.scoring_timeout_ms, 'scoringUri': self.scoring_uri,
                          'tlsMode': self.tls_mode, 'certificateFingerprints': self.certificate_fingerprints,
                          'sku': self.sku, 'osType': self.osType, 'modelDetails': model_details,
                          'environmentDetails': env_details}
        properties.update(mir_properties)
        return properties

    def get_access_token(self):
        """Retrieve auth token for this Webservice.

        :return: An object describing the auth token for this Webservice.
        :rtype: :class:`azureml.core.webservice.webservice.WebServiceAccessToken`
        :raises: :class:`azureml.exceptions.WebserviceException`
        """
        return self._internal_get_access_token()

    def _internal_get_access_token(self):
        """Retrieve auth token for this Webservice.

        :return: An object describing the auth token for this Webservice.
        :class:`azureml.core.webservice.webservice.WebServiceAccessToken`
        :raises: :class:`azureml.exceptions.WebserviceException`
        """
        headers = self._auth.get_authentication_header()
        params = {}
        token_url = self._mms_endpoint + '/token'

        try:
            resp = ClientBase._execute_func(get_requests_session().post, token_url,
                                            params=params, headers=headers)

            content = resp.content
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            auth_token_result = json.loads(content)
            return WebServiceAccessToken.deserialize(auth_token_result)
        except requests.exceptions.HTTPError:
            raise WebserviceException('Received bad response from Model Management Service:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content),
                                      logger=module_logger)


class MirServiceDeploymentConfiguration(WebserviceDeploymentConfiguration):
    """Service deployment configuration object for services deployed on MIR compute.

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
    :param collect_model_data: Whether or not to enable model data collection for this Webservice.
        Defaults to False
    :type collect_model_data: bool
    :param auth_enabled: Whether or not to enable auth for this Webservice. Defaults to False. MIR does not currently
        support authorization.
    :type auth_enabled: bool
    :param cpu_cores: The number of cpu cores to allocate for this Webservice. Can be a decimal. Defaults to 0.1
    :type cpu_cores: float
    :param memory_gb: The amount of memory (in GB) to allocate for this Webservice. Can be a decimal.
        Defaults to 0.5
    :type memory_gb: float
    :param scoring_timeout_ms: A timeout to enforce for scoring calls to this Webservice. Defaults to 60000
    :type scoring_timeout_ms: int
    :param enable_app_insights: Whether or not to enable Application Insights logging for this Webservice.
        Defaults to False
    :type enable_app_insights: bool
    :param replica_max_concurrent_requests: The number of maximum concurrent requests per node to allow for this
        Webservice. Defaults to 1
    :type replica_max_concurrent_requests: int
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
    :param gpu_cores: The number of gpu cores to allocate for this Webservice. Defaults to 0
    :type gpu_cores: int
    :param osType: OS type of the mir service, valid options are "Linux", "Windows"
    :type osType: str
    :return: A configuration object to use when deploying a Webservice object.
    """

    def __init__(self, autoscale_enabled=None, autoscale_min_replicas=None, autoscale_max_replicas=None,
                 autoscale_refresh_seconds=None, autoscale_target_utilization=None, collect_model_data=None,
                 auth_enabled=None, cpu_cores=None, memory_gb=None, scoring_timeout_ms=None,
                 replica_max_concurrent_requests=None, max_request_wait_time=None, num_replicas=None, tags=None,
                 properties=None, description=None, tls_mode=None, certificate_fingerprints=None, sku=None,
                 gpu_cores=None, osType=None, enable_app_insights=None):
        """Initialize a configuration object for deploying to an MIR compute target.

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
        :param collect_model_data: Whether or not to enable model data collection for this Webservice.
            Defaults to False
        :type collect_model_data: bool
        :param auth_enabled: Whether or not to enable auth for this Webservice. Defaults to False. MIR does not
            currently support authorization.
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
        :param gpu_cores: The number of gpu cores to allocate for this Webservice. Defaults to 0
        :type gpu_cores: int
        :param osType: OS type of the mir service, valid options are "Linux", "Windows"
        :type osType: str
        :param enable_app_insights: Whether or not to enable Application Insights logging for this Webservice.
            Defaults to False
        :type enable_app_insights: bool
        :return: A configuration object to use when deploying a Webservice object.
        :raises: azureml.exceptions.WebserviceException
        """
        super(MirServiceDeploymentConfiguration, self).__init__(MirWebservice)
        self.autoscale_enabled = autoscale_enabled
        self.autoscale_min_replicas = autoscale_min_replicas
        self.autoscale_max_replicas = autoscale_max_replicas
        self.autoscale_refresh_seconds = autoscale_refresh_seconds
        self.autoscale_target_utilization = autoscale_target_utilization
        self.collect_model_data = collect_model_data
        self.auth_enabled = auth_enabled
        self.cpu_cores = cpu_cores
        self.memory_gb = memory_gb
        self.scoring_timeout_ms = scoring_timeout_ms
        self.replica_max_concurrent_requests = replica_max_concurrent_requests
        self.max_request_wait_time = max_request_wait_time
        self.num_replicas = num_replicas
        self.tags = tags
        self.properties = properties
        self.description = description
        self.tls_mode = tls_mode
        self.certificate_fingerprints = certificate_fingerprints
        self.sku = sku
        self.gpu_cores = gpu_cores
        self.osType = osType
        self.enable_app_insights = enable_app_insights
        self.validate_configuration()

    def validate_configuration(self):
        """Check that the specified configuration values are valid.

        Will raise a WebserviceException if validation fails.

        :raises: azureml.exceptions.WebserviceException
        """
        error = ""
        if self.cpu_cores and self.cpu_cores <= 0:
            error += 'Invalid configuration, cpu_cores must be greater than zero.\n'
        if self.gpu_cores and self.gpu_cores < 0:
            error += 'Invalid configuration, gpu_cores must be greater than or equal to zero.\n'
        if self.memory_gb and self.memory_gb <= 0:
            error += 'Invalid configuration, memory_gb must be greater than zero.\n'
        if self.scoring_timeout_ms and self.scoring_timeout_ms <= 0:
            error += 'Invalid configuration, scoring_timeout_ms must be greater than zero.\n'
        if self.replica_max_concurrent_requests and self.replica_max_concurrent_requests <= 0:
            error += 'Invalid configuration, replica_max_concurrent_requests must be greater than zero.\n'
        if self.num_replicas and self.num_replicas <= 0:
            error += 'Invalid configuration, num_replicas must be greater than zero.\n'
        if self.certificate_fingerprints and (not self.tls_mode or self.tls_mode.upper() != "MUTUAL"):
            error += 'Invalid configuration, if certificate fingerprints are provided the tls mode should be ' \
                     'MUTUAL.\n'
        if self.certificate_fingerprints and not all(isinstance(item, str) for item in self.certificate_fingerprints):
            error += 'Invalid configuration, certificate_fingerprints must be a list of strings.\n'

        if error:
            raise WebserviceException(error, logger=module_logger)

    def print_deploy_configuration(self):
        """Print the deployment configuration."""
        pass

    def _build_create_payload(self, name, environment_image_request, overwrite=False):
        json_payload = copy.deepcopy(mir_service_payload_template)
        base_payload = super(MirServiceDeploymentConfiguration,
                             self)._build_base_create_payload(name, environment_image_request)

        json_payload['numReplicas'] = self.num_replicas
        if self.collect_model_data:
            json_payload['dataCollection']['storageEnabled'] = self.collect_model_data
        else:
            del(json_payload['dataCollection'])
        if self.autoscale_enabled is not None:
            json_payload['autoScaler']['autoscaleEnabled'] = self.autoscale_enabled
            json_payload['autoScaler']['minReplicas'] = self.autoscale_min_replicas
            json_payload['autoScaler']['maxReplicas'] = self.autoscale_max_replicas
            json_payload['autoScaler']['targetUtilization'] = self.autoscale_target_utilization
            json_payload['autoScaler']['refreshPeriodInSeconds'] = self.autoscale_refresh_seconds
        else:
            del(json_payload['autoScaler'])
        if self.auth_enabled is not None:
            json_payload['authEnabled'] = self.auth_enabled
        else:
            del(json_payload['authEnabled'])
        json_payload['containerResourceRequirements']['cpu'] = self.cpu_cores
        json_payload['containerResourceRequirements']['memoryInGB'] = self.memory_gb
        json_payload['maxConcurrentRequestsPerContainer'] = self.replica_max_concurrent_requests
        json_payload['maxQueueWaitMs'] = self.max_request_wait_time
        json_payload['scoringTimeoutMs'] = self.scoring_timeout_ms
        json_payload['tlsMode'] = self.tls_mode
        json_payload['certificateFingerprints'] = self.certificate_fingerprints
        json_payload['sku'] = self.sku
        json_payload['osType'] = self.osType
        if self.enable_app_insights is not None:
            json_payload['appInsightsEnabled'] = self.enable_app_insights
        else:
            del(json_payload['appInsightsEnabled'])

        if self.gpu_cores:
            json_payload['containerResourceRequirements']['gpu'] = self.gpu_cores
        else:
            del (json_payload['containerResourceRequirements']['gpu'])
        if overwrite:
            json_payload['overwrite'] = overwrite
        else:
            del (json_payload['overwrite'])

        json_payload.update(base_payload)

        return json_payload


class RevisionStatus(object):
    """Revision deployment status object for a service deployed on MIR compute.

    :param last_created_revision: Revision of MIR last specified by user.
    :type last_created_revision: str
    :param last_ready_revision: Revision of MIR last reported ready and currently deployed.
    :type last_ready_revision: str
    """

    _last_created_revision_key = 'lastCreatedRevision'
    _last_ready_revision_key = 'lastReadyRevision'
    _expected_payload_keys = [_last_created_revision_key, _last_ready_revision_key]

    def __init__(self, last_created_revision=None, last_ready_revision=None):
        """Initialize the Revision instance.

        :param last_created_revision: Revision last specified by user. Default: None.
        :type last_created_revision: string
        :param last_ready_revision: Revision currently deployed. Default: None.
        :type last_ready_revision: string
        :return: RevisionStatus object.
        :rtype: azureml.contrib.mir.RevisionStatus
        """
        super().__init__()
        self.last_created_revision = last_created_revision
        self.last_ready_revision = last_ready_revision

    def serialize(self):
        """
        Convert this RevisionStatus object into a JSON serialized dictionary.

        Use :func:`deserialize` to convert back into a RevisionStatus object.

        :return: The JSON representation of this RevisionStatus.
        :rtype: dict
        """
        return {
            self._last_created_revision_key: self.last_created_revision,
            self._last_ready_revision_key: self.last_ready_revision
        }

    @classmethod
    def deserialize(cls, payload_obj):
        """Convert this json object into a RevisionStatus object.

        :return: The RevisionStatus representation of the provided JSON object.
        :rtype: azureml.contrib.mir.RevisionStatus
        """
        if payload_obj:
            cls._validate_get_payload(payload_obj)
            return RevisionStatus(
                payload_obj.get(cls._last_created_revision_key),
                payload_obj.get(cls._last_ready_revision_key)
            )

        return RevisionStatus()

    @classmethod
    def _validate_get_payload(cls, payload):
        """Validate the payload for this RevisionStatus.

        :param payload:
        :type payload: dict
        :return:
        :rtype:
        :raises: azureml.exceptions.WebserviceException
        """
        for key in cls._expected_payload_keys:
            if key not in payload:
                raise WebserviceException('Invalid MirRevisionStatus payload, missing "{}":\n'
                                          '{}'.format(key, payload),
                                          logger=module_logger)
