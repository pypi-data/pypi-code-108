# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from msrest.pipeline import ClientRawResponse

from .. import models


class ReinforcementLearningOperations(object):
    """ReinforcementLearningOperations operations.

    :param client: Client for service requests.
    :param config: Configuration of service client.
    :param serializer: An object model serializer.
    :param deserializer: An object model deserializer.
    """

    models = models

    def __init__(self, client, config, serializer, deserializer):

        self._client = client
        self._serialize = serializer
        self._deserialize = deserializer

        self.config = config

    def start_run(
            self, subscription_id, resource_group_name,
            workspace_name, experiment_name, run_id, config,
            custom_headers=None, raw=False, **operation_config):
        """Start a reinforcement learning run on a remote compute target with a
        specific run id.

        Starts a run using the provided run id and
        ReinforcementLearningConfiguration to define the run.
        The code for the run is retrieved using the snapshotId in
        ReinforcementLearningConfiguration.
        If the run with the same id already exists, a new run will not be
        started.

        :param subscription_id: The Azure Subscription ID.
        :type subscription_id: str
        :param resource_group_name: The Name of the resource group in which
         the workspace is located.
        :type resource_group_name: str
        :param workspace_name: The name of the workspace.
        :type workspace_name: str
        :param experiment_name: The experiment name.
        :type experiment_name: str
        :param run_id: The identifier to use for the run.
        :type run_id: str
        :param config: The configuration parameters for the reinforcement
         learning run.
        :type config: azureml.contrib.train.rl._rlconfig.ReinforcementLearningConfig
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: None or ClientRawResponse if raw=true
        :rtype: None or ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<swagger.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.start_run.metadata['url']
        path_format_arguments = {
            'subscriptionId': self._serialize.url("subscription_id", subscription_id, 'str'),
            'resourceGroupName': self._serialize.url("resource_group_name", resource_group_name, 'str'),
            'workspaceName': self._serialize.url("workspace_name", workspace_name, 'str'),
            'experimentName': self._serialize.url("experiment_name", experiment_name, 'str'),
            'runId': self._serialize.url("run_id", run_id, 'str', pattern=r'^[a-zA-Z0-9][\w-]{0,255}$')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        body_content = config

        # Construct and send request
        request = self._client.post(url, query_parameters, header_parameters, body_content)
        response = self._client.send(request, stream=False, **operation_config)

        if response.status_code not in [200, 201]:
            raise models.ErrorResponseException(self._deserialize, response)

        if raw:
            client_raw_response = ClientRawResponse(None, response)
            client_raw_response.add_headers({
                'Location': 'str',
            })
            return client_raw_response
    start_run.metadata = {'url': ('/reinforcementlearning/v1.0/subscriptions/{subscriptionId}'
                                  '/resourceGroups/{resourceGroupName}/providers/Microsoft.MachineLearningServices/'
                                  'workspaces/{workspaceName}/experiments/{experimentName}/startrun/{runId}')}

    def cancel_run(
            self, subscription_id, resource_group_name, workspace_name,
            experiment_name, run_id, custom_headers=None, raw=False, **operation_config):
        """Cancel a reinforcement learning run.

        Cancels a reinforcement learning run within an experiment.

        :param subscription_id: The Azure Subscription ID.
        :type subscription_id: str
        :param resource_group_name: The Name of the resource group in which
         the workspace is located.
        :type resource_group_name: str
        :param workspace_name: The name of the workspace.
        :type workspace_name: str
        :param experiment_name: The experiment name.
        :type experiment_name: str
        :param run_id: The id of the run to cancel.
        :type run_id: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: None or ClientRawResponse if raw=true
        :rtype: None or ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<swagger.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.cancel_run.metadata['url']
        path_format_arguments = {
            'subscriptionId': self._serialize.url("subscription_id", subscription_id, 'str'),
            'resourceGroupName': self._serialize.url("resource_group_name", resource_group_name, 'str'),
            'workspaceName': self._serialize.url("workspace_name", workspace_name, 'str'),
            'experimentName': self._serialize.url("experiment_name", experiment_name, 'str'),
            'runId': self._serialize.url("run_id", run_id, 'str', pattern=r'^[a-zA-Z0-9][\w-]{0,255}$')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.post(url, query_parameters, header_parameters)
        response = self._client.send(request, stream=False, **operation_config)

        if response.status_code not in [202]:
            raise models.ErrorResponseException(self._deserialize, response)

        if raw:
            client_raw_response = ClientRawResponse(None, response)
            client_raw_response.add_headers({
                'Operation-Location': 'str',
            })
            return client_raw_response
    cancel_run.metadata = {'url': ('/reinforcementlearning/v1.0/subscriptions/{subscriptionId}/'
                                   'resourceGroups/{resourceGroupName}/providers/Microsoft.MachineLearningServices/'
                                   'workspaces/{workspaceName}/experiments/{experimentName}/runId/{runId}/cancel')}

    def complete_run(
            self, subscription_id, resource_group_name, workspace_name,
            experiment_name, run_id, custom_headers=None, raw=False, **operation_config):
        """Complete a reinforcement learning run.

        Stops execution of a reinforcement learning run. Final status will be
        'Completed'.

        :param subscription_id: The Azure Subscription ID.
        :type subscription_id: str
        :param resource_group_name: The Name of the resource group in which
         the workspace is located.
        :type resource_group_name: str
        :param workspace_name: The name of the workspace.
        :type workspace_name: str
        :param experiment_name: The experiment name.
        :type experiment_name: str
        :param run_id: The id of the run to complete.
        :type run_id: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: None or ClientRawResponse if raw=true
        :rtype: None or ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<swagger.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.complete_run.metadata['url']
        path_format_arguments = {
            'subscriptionId': self._serialize.url("subscription_id", subscription_id, 'str'),
            'resourceGroupName': self._serialize.url("resource_group_name", resource_group_name, 'str'),
            'workspaceName': self._serialize.url("workspace_name", workspace_name, 'str'),
            'experimentName': self._serialize.url("experiment_name", experiment_name, 'str'),
            'runId': self._serialize.url("run_id", run_id, 'str', pattern=r'^[a-zA-Z0-9][\w-]{0,255}$')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.post(url, query_parameters, header_parameters)
        response = self._client.send(request, stream=False, **operation_config)

        if response.status_code not in [202]:
            raise models.ErrorResponseException(self._deserialize, response)

        if raw:
            client_raw_response = ClientRawResponse(None, response)
            client_raw_response.add_headers({
                'Operation-Location': 'str',
            })
    complete_run.metadata = {'url': ('/reinforcementlearning/v1.0/subscriptions/{subscriptionId}/'
                                     'resourceGroups/{resourceGroupName}/providers/Microsoft.MachineLearningServices'
                                     '/workspaces/{workspaceName}/experiments/{experimentName}/'
                                     'runId/{runId}/complete')}
