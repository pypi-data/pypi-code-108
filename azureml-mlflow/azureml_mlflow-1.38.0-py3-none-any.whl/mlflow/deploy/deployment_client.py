# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality for deploying models to AzureML through MLFlow."""

import json
import logging
from azureml.core import Webservice, Model as AzureModel
from azureml.core.webservice import AciWebservice
from azureml.exceptions import WebserviceException
from azureml.mlflow._internal.utils import load_azure_workspace
from azureml._model_management._util import deploy_config_dict_to_obj, get_requests_session
from azureml._restclient.clientbase import ClientBase
from mlflow.deployments import BaseDeploymentClient
from mlflow.exceptions import MlflowException
from mlflow.utils.annotations import experimental
from mlflow.utils.file_utils import TempDir
from ._util import (file_stream_to_object, handle_model_uri, create_inference_config,
                    submit_update_call, get_deployments_import_error, submit_rest_request, get_and_poll_on_async_op,
                    convert_v2_deploy_config_to_rest_config, get_base_arm_request_route)


_logger = logging.getLogger(__name__)


class AzureMLDeploymentClient(BaseDeploymentClient):
    """Client object used to deploy MLFlow models to AzureML."""

    def __init__(self, target_uri):
        """
        Initialize the deployment client with the MLFlow target uri.

        :param target_uri: AzureML workspace specific target uri.
        :type target_uri: str
        """
        super(AzureMLDeploymentClient, self).__init__(target_uri)
        try:
            self.workspace = load_azure_workspace()
        except Exception as e:
            raise MlflowException("Failed to retrieve AzureML Workspace") from e

    @experimental
    def create_deployment(self, name, model_uri, flavor=None, config=None):
        """
        Deploy a model to the specified target.

        Deploy a model to the specified target. By default, this method should block until
        deployment completes (i.e. until it's possible to perform inference with the deployment).
        In the case of conflicts (e.g. if it's not possible to create the specified deployment
        without due to conflict with an existing deployment), raises a
        :py:class:`mlflow.exceptions.MlflowException`. See target-specific plugin documentation
        for additional detail on support for asynchronous deployment and other configuration.

        :param name: Unique name to use for deployment. If another deployment exists with the same
                     name, raises a :py:class:`mlflow.exceptions.MlflowException`
        :param model_uri: URI of model to deploy. AzureML supports deployments of 'models', 'runs', and 'file' uris.
        :param flavor: (optional) Model flavor to deploy. If unspecified, a default flavor
                       will be chosen.
        :param config: (optional) Dict containing updated target-specific configuration for the
                       deployment
        :return: Dict corresponding to created deployment, which must contain the 'name' key.
        """
        if flavor and flavor != 'python_function':
            raise MlflowException('Unable to use {} model flavor, '
                                  'AML currently only supports python_function.'.format(flavor))

        model_name, model_version = handle_model_uri(model_uri, name)

        try:
            aml_model = AzureModel(self.workspace, id='{}:{}'.format(model_name, model_version))
        except Exception as e:
            raise MlflowException('Failed to retrieve model to deploy') from e

        v1_deploy_config = None
        v2_deploy_config = None

        # Convert passed in file to deployment config
        if config and 'deploy-config-file' in config:
            with open(config['deploy-config-file'], 'r') as deploy_file_stream:
                deploy_config_obj = file_stream_to_object(deploy_file_stream)
                try:
                    if 'computeType' in deploy_config_obj:
                        v1_deploy_config = deploy_config_dict_to_obj(deploy_config_obj, deploy_config_obj.get('tags'),
                                                                     deploy_config_obj.get('properties'),
                                                                     deploy_config_obj.get('description'))
                    else:
                        if 'type' in deploy_config_obj and deploy_config_obj['type'].lower() != 'managed':
                            raise MlflowException('Unable to deploy MLFlow model to {} compute, currently only '
                                                  'supports Managed '
                                                  'compute.'.format(deploy_config_obj['endpointComputeType']))
                        if 'model' in deploy_config_obj:
                            raise MlflowException('Unable to provide model information in the deployment config file '
                                                  'when deploying through MLFlow. Please use the `model_uri` '
                                                  'parameter.')
                        else:
                            deploy_config_obj['model'] = \
                                '/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/' \
                                'Microsoft.MachineLearningServices/workspaces/{workspace_name}/models/{model_name}/' \
                                'versions/{model_version}'.format(subscription_id=self.workspace.subscription_id,
                                                                  resource_group=self.workspace.resource_group,
                                                                  workspace_name=self.workspace.name,
                                                                  model_name=model_name, model_version=model_version)
                        if 'code_configuration' in deploy_config_obj or 'environment' in deploy_config_obj or \
                                'endpoint_name' in deploy_config_obj:
                            raise MlflowException(
                                'code_configuration, environment, and endpoint_name are not used with '
                                'MLFlow deployments. Please remove from the deployment config and '
                                'try again.')
                        v2_deploy_config = deploy_config_obj
                except Exception as e:
                    raise MlflowException('Failed to parse provided configuration file') from e
        else:
            v1_deploy_config = AciWebservice.deploy_configuration()

        if v1_deploy_config:
            deployment = self._v1_create_deployment(name, model_name, model_version, aml_model, config,
                                                    v1_deploy_config)
        else:
            deployment = self._v2_create_deployment(name, model_name, model_version, v2_deploy_config)

        if 'flavor' not in deployment:
            deployment['flavor'] = flavor if flavor else 'python_function'
        return deployment

    def _v1_create_deployment(self, name, model_name, model_version, aml_model, create_deployment_config,
                              v1_deploy_config):
        with TempDir(chdr=True) as tmp_dir:
            inference_config = create_inference_config(tmp_dir, model_name, model_version, name)

            try:
                _logger.info("Creating an AzureML deployment with name: `%s`", name)

                # Deploy
                webservice = AzureModel.deploy(
                    workspace=self.workspace,
                    name=name,
                    models=[aml_model],
                    inference_config=inference_config,
                    deployment_config=v1_deploy_config,
                )

                if create_deployment_config and 'async' in create_deployment_config and \
                        create_deployment_config['async']:
                    _logger.info('AzureML deployment in progress, you can use get_deployment to check on the '
                                 'current deployment status.')
                else:
                    webservice.wait_for_deployment(show_output=True)
            except Exception as e:
                raise MlflowException('Error while creating deployment') from e

            return webservice.serialize()

    def _v2_create_deployment(self, name, model_name, model_version, v2_deploy_config):
        # Create Endpoint
        v2_api_version = '2021-10-01'
        base_uri = '{arm_base}/subscriptions/{subscription_id}/resourceGroups/' \
                   '{resource_group}/providers/Microsoft.MachineLearningServices/workspaces/' \
                   '{workspace_name}'.format(arm_base=get_base_arm_request_route(self.workspace),
                                             subscription_id=self.workspace.subscription_id,
                                             resource_group=self.workspace.resource_group,
                                             workspace_name=self.workspace.name)
        endpoint_request_uri = base_uri + '/onlineEndpoints/{endpoint_name}'.format(endpoint_name=name)
        endpoint_request_headers = {'Content-Type': 'application/json'}
        endpoint_request_headers.update(self.workspace._auth_object.get_authentication_header())
        endpoint_request_params = {'api-version': v2_api_version}

        endpoint_request_body = {
            "identity": {
                "type": "systemAssigned"
            },
            "properties": {
                "authMode": "AMLToken",
                "properties": {
                    "azureml.mlflow_client_endpoint": "True"
                }
            },
            "location": self.workspace.location
        }

        _logger.info('Starting endpoint request')
        resp = submit_rest_request(get_requests_session().put, endpoint_request_uri, endpoint_request_body,
                                   endpoint_request_params, endpoint_request_headers)
        get_and_poll_on_async_op(resp, self.workspace, 'Endpoint Create')

        # Create Deployment using v2_deploy_config
        deployment_request_uri = endpoint_request_uri + '/deployments/{deployment_name}'.format(deployment_name=name)
        deployment_request_headers = {'Content-Type': 'application/json'}
        deployment_request_headers.update(self.workspace._auth_object.get_authentication_header())
        deployment_request_params = {'api-version': v2_api_version}

        deployment_request_body = {
            "location": self.workspace.location,
            "properties": convert_v2_deploy_config_to_rest_config(self.workspace, v2_deploy_config, model_name,
                                                                  model_version),
            "sku": {
                "name": "default",
                "capacity": 1
            }
        }

        _logger.info('Starting deployment request')
        resp = submit_rest_request(get_requests_session().put, deployment_request_uri, deployment_request_body,
                                   deployment_request_params, deployment_request_headers)
        get_and_poll_on_async_op(resp, self.workspace, 'Deployment Create')

        # Update Endpoint traffic
        update_endpoint_request_headers = {'Content-Type': 'application/json'}
        update_endpoint_request_headers.update(self.workspace._auth_object.get_authentication_header())
        update_endpoint_request_params = {'api-version': v2_api_version}
        update_endpoint_request_body = {
            "properties": {
                "traffic": {
                    name: 100
                }
            }
        }

        resp = submit_rest_request(get_requests_session().patch, endpoint_request_uri,
                                   update_endpoint_request_body, update_endpoint_request_params,
                                   update_endpoint_request_headers)
        get_and_poll_on_async_op(resp, self.workspace, 'Endpoint Update')

        # Retrieve updated endpoint to return
        endpoint_request_headers = {'Content-Type': 'application/json'}
        endpoint_request_headers.update(self.workspace._auth_object.get_authentication_header())
        endpoint_request_params = {'api-version': v2_api_version}

        resp = submit_rest_request(get_requests_session().get, endpoint_request_uri, None, endpoint_request_params,
                                   endpoint_request_headers)
        return resp.json()

    @experimental
    def update_deployment(self, name, model_uri=None, flavor=None, config=None):
        """
        Update the deployment specified by name.

        Update the deployment with the specified name. You can update the URI of the model, the
        flavor of the deployed model (in which case the model URI must also be specified), and/or
        any target-specific attributes of the deployment (via `config`). By default, this method
        should block until deployment completes (i.e. until it's possible to perform inference
        with the updated deployment). See target-specific plugin documentation for additional
        detail on support for asynchronous deployment and other configuration.

        :param name: Unique name of deployment to update
        :param model_uri: URI of a new model to deploy.
        :param flavor: (optional) new model flavor to use for deployment. If provided,
                       ``model_uri`` must also be specified. If ``flavor`` is unspecified but
                       ``model_uri`` is specified, a default flavor will be chosen and the
                       deployment will be updated using that flavor.
        :param config: (optional) dict containing updated target-specific configuration for the
                       deployment
        :return: None
        """
        endpoint = self._get_v2_endpoint(name)
        if endpoint:
            self._v2_deployment_update(name, model_uri, flavor, config)
        else:
            service = self._get_v1_service(name)
            if service:
                self._v1_deployment_update(service, name, model_uri, flavor, config)
            else:
                raise MlflowException('No deployment with name {} found to update'.format(name))

    def _v1_deployment_update(self, service, name, model_uri=None, flavor=None, config=None):
        models = None
        inference_config = None

        deploy_config = None
        if config and 'deploy-config-file' in config:
            try:
                with open(config['deploy-config-file'], 'r') as deploy_file_stream:
                    deploy_config_obj = file_stream_to_object(deploy_file_stream)
                    deploy_config = deploy_config_dict_to_obj(
                        deploy_config_obj, deploy_config_obj.get('tags'),
                        deploy_config_obj.get('properties'), deploy_config_obj.get('description')
                    )
            except Exception as e:
                raise MlflowException('Failed to parse provided deployment config file') from e

        aks_endpoint_version_config = None
        if config and 'aks-endpoint-deployment-config' in config:
            aks_endpoint_version_config = config['aks-endpoint-deployment-config']

        with TempDir(chdr=True) as tmp_dir:
            if model_uri:
                model_name, model_version = handle_model_uri(model_uri, name)
                try:
                    aml_model = AzureModel(self.workspace, id='{}:{}'.format(model_name, model_version))
                except Exception as e:
                    raise MlflowException('Failed to retrieve model to deploy') from e
                models = [aml_model]

                inference_config = create_inference_config(tmp_dir, model_name, model_version, name)
            try:
                submit_update_call(service, models, inference_config, deploy_config, aks_endpoint_version_config)

                if config and config.get('async'):
                    _logger.info('AzureML deployment in progress, you can use get_deployment to check on the current '
                                 'deployment status.')
                else:
                    service.wait_for_deployment(show_output=True)
            except Exception as e:
                raise MlflowException('Error submitting deployment update') from e

    def _v2_deployment_update(self, name, model_uri=None, flavor=None, config=None):
        v2_api_version = '2021-10-01'
        base_uri = '{arm_base}/subscriptions/{subscription_id}/resourceGroups/{resource_group}/' \
                   'providers/Microsoft.MachineLearningServices/workspaces/' \
                   '{workspace_name}'.format(arm_base=get_base_arm_request_route(self.workspace),
                                             subscription_id=self.workspace.subscription_id,
                                             resource_group=self.workspace.resource_group,
                                             workspace_name=self.workspace.name)
        endpoint_request_uri = base_uri + '/onlineEndpoints/{endpoint_name}'.format(endpoint_name=name)
        deployment_request_uri = endpoint_request_uri + '/deployments/{deployment_name}'.format(deployment_name=name)
        deployment_request_headers = {'Content-Type': 'application/json'}
        deployment_request_headers.update(self.workspace._auth_object.get_authentication_header())
        deployment_request_params = {'api-version': v2_api_version}

        try:
            resp = submit_rest_request(get_requests_session().get, deployment_request_uri, None,
                                       deployment_request_params, deployment_request_headers)
        except MlflowException as e:
            raise MlflowException('Failure retrieving the deployment to update') from e

        existing_deployment = resp.json()

        v2_deploy_config = {}
        if model_uri:
            model_name, model_version = handle_model_uri(model_uri, name)
        else:
            model_parts_list = existing_deployment['properties']['model'].split('/')
            model_name = model_parts_list[-3]
            model_version = model_parts_list[-1]

        if config and 'deploy-config-file' in config:
            with open(config['deploy-config-file'], 'r') as deploy_file_stream:
                deploy_config_obj = file_stream_to_object(deploy_file_stream)
                if 'code_configuration' in deploy_config_obj or 'environment' in deploy_config_obj or \
                        'endpoint_name' in deploy_config_obj:
                    raise MlflowException('code_configuration, environment, and endpoint_name are not used with '
                                          'MLFlow deployments. Please remove from the deployment config and '
                                          'try again.')
                v2_deploy_config = deploy_config_obj

        deployment_request_body = {
            "location": self.workspace.location,
            "properties": convert_v2_deploy_config_to_rest_config(self.workspace, v2_deploy_config, model_name,
                                                                  model_version),
            "sku": {
                "name": "default",
                "capacity": 1
            }
        }

        _logger.info('Starting update request')
        resp = submit_rest_request(get_requests_session().put, deployment_request_uri, deployment_request_body,
                                   deployment_request_params, deployment_request_headers)
        get_and_poll_on_async_op(resp, self.workspace, 'Deployment Update')

    @experimental
    def delete_deployment(self, name):
        """
        Delete the deployment with name ``name``.

        :param name: Name of deployment to delete
        :return: None
        """
        endpoint = self._get_v2_endpoint(name)
        if endpoint:
            v2_api_version = '2021-10-01'
            base_uri = '{arm_base}/subscriptions/{subscription_id}/resourceGroups/' \
                       '{resource_group}/providers/Microsoft.MachineLearningServices/workspaces/' \
                       '{workspace_name}'.format(arm_base=get_base_arm_request_route(self.workspace),
                                                 subscription_id=self.workspace.subscription_id,
                                                 resource_group=self.workspace.resource_group,
                                                 workspace_name=self.workspace.name)
            endpoint_request_uri = base_uri + '/onlineEndpoints/{endpoint_name}'.format(endpoint_name=name)
            endpoint_request_headers = {'Content-Type': 'application/json'}
            endpoint_request_headers.update(self.workspace._auth_object.get_authentication_header())
            endpoint_request_params = {'api-version': v2_api_version}

            resp = submit_rest_request(get_requests_session().delete, endpoint_request_uri, None,
                                       endpoint_request_params, endpoint_request_headers)
            get_and_poll_on_async_op(resp, self.workspace, 'Deployment Delete')
        else:
            service = self._get_v1_service(name)
            if service:
                try:
                    service.delete()
                except WebserviceException as e:
                    raise MlflowException('There was an error deleting the deployment: \n{}'.format(e.message)) from e
            else:
                _logger.info('No deployment with name {} found to delete'.format(name))

    @experimental
    def list_deployments(self):
        """
        List deployments.

        :return: A list of dicts corresponding to deployments.
        """
        try:
            service_list = []
            services = Webservice.list(self.workspace, compute_type='ACI')
            services += Webservice.list(self.workspace, compute_type='AKS')
            for service in services:
                service_list.append(service.serialize())

            v2_api_version = '2021-10-01'
            base_uri = '{arm_base}/subscriptions/{subscription_id}/resourceGroups/' \
                       '{resource_group}/providers/Microsoft.MachineLearningServices/workspaces/' \
                       '{workspace_name}'.format(arm_base=get_base_arm_request_route(self.workspace),
                                                 subscription_id=self.workspace.subscription_id,
                                                 resource_group=self.workspace.resource_group,
                                                 workspace_name=self.workspace.name)
            endpoint_list_request_uri = base_uri + '/onlineEndpoints'
            endpoint_request_headers = {'Content-Type': 'application/json'}
            endpoint_request_headers.update(self.workspace._auth_object.get_authentication_header())
            endpoint_request_params = {'api-version': v2_api_version}

            resp = submit_rest_request(get_requests_session().get, endpoint_list_request_uri, None,
                                       endpoint_request_params, endpoint_request_headers)
            v2_list_response = resp.json()
            if 'value' in v2_list_response:
                endpoint_list = v2_list_response['value']
            else:
                endpoint_list = v2_list_response
            for endpoint in endpoint_list:
                if 'azureml.mlflow_client_endpoint' in endpoint['properties']['properties']:
                    service_list.append(endpoint)

            return service_list
        except WebserviceException as e:
            raise MlflowException('There was an error listing deployments: \n{}'.format(e.message)) from e

    @experimental
    def get_deployment(self, name):
        """
        Retrieve details for the specified deployment.

        Returns a dictionary describing the specified deployment. The dict is guaranteed to contain an 'name' key
        containing the deployment name.

        :param name: Name of deployment to retrieve
        """
        deployment = self._get_v2_deployment(name)
        if deployment:
            endpoint = self._get_v2_endpoint(name)
            deployment['properties']['scoringUri'] = endpoint['properties']['scoringUri']
            deployment['properties']['swaggerUri'] = endpoint['properties']['swaggerUri']
        else:
            service = self._get_v1_service(name)
            if service:
                deployment = service.serialize()
        if not deployment:
            raise MlflowException('No deployment with name {} found'.format(name))

        if 'flavor' not in deployment:
            deployment['flavor'] = 'python_function'
        return deployment

    def _get_v1_service(self, name):
        try:
            service = Webservice(self.workspace, name)
            return service
        except WebserviceException as e:
            if 'WebserviceNotFound' in e.message:
                return None
            raise MlflowException('There was an error retrieving the deployment: \n{}'.format(e.message)) from e

    def _get_v2_endpoint(self, name):
        v2_api_version = '2021-10-01'
        base_uri = '{arm_base}/subscriptions/{subscription_id}/resourceGroups/{resource_group}/' \
                   'providers/Microsoft.MachineLearningServices/workspaces/' \
                   '{workspace_name}'.format(arm_base=get_base_arm_request_route(self.workspace),
                                             subscription_id=self.workspace.subscription_id,
                                             resource_group=self.workspace.resource_group,
                                             workspace_name=self.workspace.name)
        endpoint_request_uri = base_uri + '/onlineEndpoints/{endpoint_name}'.format(endpoint_name=name)
        endpoint_request_headers = {'Content-Type': 'application/json'}
        endpoint_request_headers.update(self.workspace._auth_object.get_authentication_header())
        endpoint_request_params = {'api-version': v2_api_version}

        try:
            resp = submit_rest_request(get_requests_session().get, endpoint_request_uri, None, endpoint_request_params,
                                       endpoint_request_headers)
        except MlflowException as e:
            if 'Response Code: 404' in e.message:
                return None
            else:
                raise e

        endpoint_json = resp.json()
        if 'azureml.mlflow_client_endpoint' not in endpoint_json['properties']['properties']:
            return None

        return endpoint_json

    def _get_v2_deployment(self, name):
        v2_api_version = '2021-10-01'
        base_uri = '{arm_base}/subscriptions/{subscription_id}/resourceGroups/{resource_group}/' \
                   'providers/Microsoft.MachineLearningServices/workspaces/' \
                   '{workspace_name}'.format(arm_base=get_base_arm_request_route(self.workspace),
                                             subscription_id=self.workspace.subscription_id,
                                             resource_group=self.workspace.resource_group,
                                             workspace_name=self.workspace.name)
        deployment_request_uri = base_uri + '/onlineEndpoints/{endpoint_name}' \
                                            '/deployments/{deployment_name}'.format(endpoint_name=name,
                                                                                    deployment_name=name)
        deployment_request_headers = {'Content-Type': 'application/json'}
        deployment_request_headers.update(self.workspace._auth_object.get_authentication_header())
        deployment_request_params = {'api-version': v2_api_version}

        try:
            resp = submit_rest_request(get_requests_session().get, deployment_request_uri, None,
                                       deployment_request_params, deployment_request_headers)
        except MlflowException as e:
            if 'Response Code: 404' in e.message:
                return None
            else:
                raise e

        return resp.json()

    @experimental
    def predict(self, deployment_name, df):
        """
        Predict on the specified deployment using the provided dataframe.

        Compute predictions on the pandas DataFrame ``df`` using the specified deployment.
        Note that the input/output types of this method matches that of `mlflow pyfunc predict`
        (we accept a pandas DataFrame as input and return either a pandas DataFrame,
        pandas Series, or numpy array as output).

        :param deployment_name: Name of deployment to predict against
        :param df: Pandas DataFrame to use for inference
        :return: A pandas DataFrame, pandas Series, or numpy array
        """
        try:
            from mlflow.pyfunc.scoring_server import parse_json_input, _get_jsonable_obj
        except ImportError as exception:
            raise get_deployments_import_error(exception)

        service = None
        endpoint = self._get_v2_endpoint(deployment_name)
        if not endpoint:
            service = self._get_v1_service(deployment_name)
            if not service:
                raise MlflowException('No deployment with name {} found to predict against'.format(deployment_name))

        # Take in DF, parse to json using split orient
        input_data = _get_jsonable_obj(df, pandas_orient='split')

        if service:
            scoring_resp = self._v1_predict(service, input_data)
        else:
            scoring_resp = self._v2_predict(endpoint, input_data)

        if scoring_resp.status_code == 200:
            # Parse records orient json to df
            return parse_json_input(json.dumps(scoring_resp.json()), orient='records')
        else:
            raise MlflowException('Failure during prediction:\n'
                                  'Response Code: {}\n'
                                  'Headers: {}\n'
                                  'Content: {}'.format(scoring_resp.status_code, scoring_resp.headers,
                                                       scoring_resp.content))

    def _v1_predict(self, service, input_data):
        if not service.scoring_uri:
            raise MlflowException('Error attempting to call deployment, scoring_uri unavailable. '
                                  'This could be due to a failed deployment, or the service is not ready yet.\n'
                                  'Current State: {}\n'
                                  'Errors: {}'.format(service.state, service.error))

        # Pass split orient json to webservice
        # Take records orient json from webservice
        resp = ClientBase._execute_func(service._webservice_session.post, service.scoring_uri,
                                        data=json.dumps({'input_data': input_data}))

        if resp.status_code == 401:
            if service.auth_enabled:
                service_keys = service.get_keys()
                service._session.headers.update({'Authorization': 'Bearer ' + service_keys[0]})
            elif service.token_auth_enabled:
                service_token, refresh_token_time = service.get_access_token()
                service._refresh_token_time = refresh_token_time
                service._session.headers.update({'Authorization': 'Bearer ' + service_token})
            resp = ClientBase._execute_func(service._webservice_session.post, service.scoring_uri, data=input_data)

        return resp

    def _v2_predict(self, endpoint, input_data):
        v2_api_version = '2021-10-01'
        base_uri = '{arm_base}/subscriptions/{subscription_id}/resourceGroups/{resource_group}/' \
                   'providers/Microsoft.MachineLearningServices/workspaces/' \
                   '{workspace_name}'.format(arm_base=get_base_arm_request_route(self.workspace),
                                             subscription_id=self.workspace.subscription_id,
                                             resource_group=self.workspace.resource_group,
                                             workspace_name=self.workspace.name)
        endpoint_token_request_uri = base_uri + '/onlineEndpoints/{endpoint_name}/token'.format(
            endpoint_name=endpoint['name'])
        endpoint_request_headers = {'Content-Type': 'application/json'}
        endpoint_request_headers.update(self.workspace._auth_object.get_authentication_header())
        endpoint_request_params = {'api-version': v2_api_version}

        try:
            token_resp = submit_rest_request(get_requests_session().post, endpoint_token_request_uri, None,
                                             endpoint_request_params, endpoint_request_headers)
        except MlflowException as e:
            raise MlflowException('Received bad response attempting to retrieve deployment auth token') from e

        scoring_uri = endpoint['properties']['scoringUri']
        scoring_request_headers = {'Content-Type': 'application/json',
                                   'Authorization': 'Bearer {}'.format(token_resp.json()['accessToken'])}
        scoring_resp = submit_rest_request(get_requests_session().post, scoring_uri,
                                           {'input_data': input_data}, None, scoring_request_headers)
        return scoring_resp

    def _get_logs(self, name, get_init_container_logs=False):
        endpoint = self._get_v2_endpoint(name)
        if endpoint:
            v2_api_version = '2021-10-01'
            base_uri = '{arm_base}/subscriptions/{subscription_id}/resourceGroups/' \
                       '{resource_group}/providers/Microsoft.MachineLearningServices/workspaces/' \
                       '{workspace_name}'.format(arm_base=get_base_arm_request_route(self.workspace),
                                                 subscription_id=self.workspace.subscription_id,
                                                 resource_group=self.workspace.resource_group,
                                                 workspace_name=self.workspace.name)
            deployment_request_uri = base_uri + '/onlineEndpoints/{endpoint_name}' \
                                                '/deployments/{deployment_name}/getLogs'.format(endpoint_name=name,
                                                                                                deployment_name=name)
            deployment_request_headers = {'Content-Type': 'application/json'}
            deployment_request_headers.update(self.workspace._auth_object.get_authentication_header())
            deployment_request_params = {'api-version': v2_api_version}

            logs_body = {}
            if get_init_container_logs:
                logs_body = {"containerType": "storageInitializer"}

            resp = submit_rest_request(get_requests_session().post, deployment_request_uri, logs_body,
                                       deployment_request_params, deployment_request_headers)
            content = json.loads(resp.content)
            return content
        else:
            service = self._get_v1_service(name)
            if service:
                return service.get_logs(init=get_init_container_logs)
            else:
                raise MlflowException('No deployment with name {} found to get logs for'.format(name))
