# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Manages AmlWindowsCompute compute targets in Azure Machine Learning service."""

import copy
import json
import requests
import uuid
from abc import ABC
from pkg_resources import resource_string
from azureml._compute._constants import MLC_WORKSPACE_API_VERSION
from azureml._base_sdk_common.user_agent import get_user_agent
from azureml._base_sdk_common import _ClientSessionId
from azureml._compute._util import get_requests_session, get_paginated_compute_results
from azureml.core.compute import ComputeTarget
from azureml.core.compute.amlcompute import AmlCompute, ScaleSettings, AmlComputeNodeStateCounts, \
    AmlComputeStatus, AmlComputeProvisioningConfiguration
from azureml.exceptions import ComputeTargetException, UserErrorException
from azureml._restclient.clientbase import ClientBase
from dateutil.parser import parse
from azureml._restclient.constants import RequestHeaders

_OS_TYPE = 'Windows'
_OS_TYPE_KEY_NAME = 'osType'
_VM_IMAGE_KEY_NAME = 'virtualMachineImage'
_COMPUTE_TYPE = 'AmlCompute'
amlwindowscompute_payload_template = json.loads(resource_string(__name__, 'amlwindowscompute_cluster_template.json')
                                                .decode('ascii'))


class AmlWindowsCompute(AmlCompute):

    """This is an experimental class for managing AmlWindowsCompute compute target objects.

    An Azure Machine Learning Windows Compute (AmlWindowsCompute) is a managed-compute infrastructure that
    allows you to easily create a single or multi-node compute. The compute is created within your workspace
    region as a resource that can be shared with other users. AmlWindowsCompute supports only Azure Files as
    mounted storage and does not support environment definition for the experiment run.

    :param workspace: The workspace object containing the AmlWindowsCompute object to retrieve.
    :type workspace: azureml.core.Workspace
    :param name: The name of the of the AmlWindowsCompute object to retrieve.
    :type name: str
    """

    _compute_type = _COMPUTE_TYPE

    def __new__(cls, workspace, name):
        """Return an instance of a compute target.

        AmlWindowsCompute constructor is used to retrieve a cloud representation of a Windows Compute object associated
        with the provided workspace. Will return an instance of AmlWindowsCompute, the child class corresponding to the
        type of the retrieved Compute object.

        :param workspace: The workspace object containing the AmlWindowsCompute object to retrieve.
        :type workspace: azureml.core.Workspace
        :param name: The name of the AmlWindowsCompute object to retrieve.
        :type name: str
        :return: An instance of :class:`azureml.contrib.compute.AmlWindowsCompute` corresponding to the
            specific type of the retrieved Compute object.
        :rtype: azureml.contrib.compute.AmlWindowsCompute
        :raises: azureml.exceptions.ComputeTargetException.
        """
        if workspace and name:
            compute_payload = cls._get(workspace, name)
            if compute_payload:
                compute_type = compute_payload['properties']['computeType']
                os_type = compute_payload['properties']['properties'][_OS_TYPE_KEY_NAME] \
                    if compute_payload['properties']['properties'] else None

                if compute_type.lower() == _COMPUTE_TYPE.lower() and os_type.lower() == _OS_TYPE.lower():
                    compute_target = ABC.__new__(AmlWindowsCompute)
                    compute_target._initialize(workspace, compute_payload)
                    return compute_target
            else:
                raise ComputeTargetException('ComputeTargetNotFound: Compute Target with name {} not found in '
                                             'provided workspace'.format(name))
        else:
            return ABC.__new__(AmlWindowsCompute)

    def _initialize(self, workspace, obj_dict):
        super()._initialize(workspace, obj_dict)
        provisioning_state = obj_dict['properties']['provisioningState']
        status = AmlWindowsComputeStatus.deserialize(obj_dict['properties']) \
            if provisioning_state in ["Succeeded", "Updating"] else None
        os_type = obj_dict['properties']['properties'][_OS_TYPE_KEY_NAME] \
            if obj_dict['properties']['properties'] else None
        vm_image = obj_dict['properties']['properties'][_VM_IMAGE_KEY_NAME] \
            if obj_dict['properties']['properties'] else None
        self.os_type = os_type
        self.vm_image = vm_image
        self.status = status

    def __repr__(self):
        """Return the string representation of the AmlWindowsCompute object.

        :return: String representation of the AmlWindowsCompute object.
        :rtype: str
        """
        return super().__repr__()

    @staticmethod
    def create(workspace, name, provisioning_configuration):
        """Provision an AmlWindowsCompute cluster.

        :param workspace: The workspace object to create the Compute object under.
        :type workspace: azureml.core.Workspace
        :param name: The name to associate with the Compute object.
        :type name: str
        :param provisioning_configuration: An AmlWindowsComputeProvisioningConfiguration object that defines
            how to configure the Windows cluster.
        :type provisioning_configuration: azureml.contrib.compute.AmlWindowsComputeProvisioningConfiguration
        :return: An instance of AmlWindowsCompute.
        :rtype: azureml.contrib.compute.AmlWindowsCompute
        :raises: azureml.exceptions.ComputeTargetException
        """
        if name in ["amlcompute", "local", "containerinstance"]:
            raise UserErrorException("Please specify a different target name. {} is a reserved name.".format(name))
        return AmlWindowsCompute._create(workspace, name, provisioning_configuration)

    @staticmethod
    def _create(workspace, name, provisioning_configuration):
        compute_create_payload = AmlWindowsCompute._build_create_payload(provisioning_configuration,
                                                                         workspace.location, workspace.subscription_id)
        return ComputeTarget._create_compute_target(workspace, name, compute_create_payload, AmlWindowsCompute)

    @staticmethod
    def provisioning_configuration(vm_size='', vm_priority="dedicated", vm_image=None, min_nodes=0,
                                   max_nodes=None, idle_seconds_before_scaledown=None,
                                   admin_username=None, admin_user_password=None,
                                   vnet_resourcegroup_name=None, vnet_name=None, subnet_name=None,
                                   tags=None, description=None, remote_login_port_public_access="NotSpecified"):
        """Create a configuration object for provisioning an AmlWindowsCompute target.

        :param vm_size: Size of agent VMs. More details can be found here: https://aka.ms/azureml-vm-details.
            Note that not all sizes are available in all regions, as detailed in the previous link.
            Defaults to Standard_NC6.
        :type vm_size: str
        :param vm_priority: The VM priority, either "dedicated" or "lowpriority" VMs.
            If not specified, defaults to "dedicated".
        :type vm_priority: str
        :param vm_image: Virtual machine image to be used for the Windows compute target.
            Example : { "id" : "<image_id>/versions/<version>"}. Please refer to `Create an image definition
            <https://docs.microsoft.com/en-us/azure/virtual-machines/windows/shared-images-portal#create-an-image-definition>`_.
            If not specified, will default to DSVM Windows Server 2016 image.
        :type vm_image: dict
        :param min_nodes: Minimum number of nodes to use on the cluster. If not specified, will default to 0.
        :type min_nodes: int
        :param max_nodes: Maximum number of nodes to use on the cluster. Defaults to 4.
        :type max_nodes: int
        :param idle_seconds_before_scaledown: Node idle time in seconds before scaling down the cluster.
            Defaults to 120.
        :type idle_seconds_before_scaledown: int
        :param admin_username: Name of the administrator user account which can be used to login into nodes.
        :type admin_username: str
        :param admin_user_password: Password of the administrator user account.
        :type admin_user_password: str
        :param vnet_resourcegroup_name: Name of the resource group where the virtual network is located.
        :type vnet_resourcegroup_name: str
        :param vnet_name: Name of the virtual network.
        :type vnet_name: str
        :param subnet_name: Name of the subnet inside the vnet.
        :type subnet_name: str
        :param tags: A dictionary of key value tags to provide to the compute object.
        :type tags: dict[str, str]
        :param description: A description to provide to the compute object.
        :type description: str
        :param remote_login_port_public_access: The state of the public RDP port. Possible values are:

            * Disabled - Indicates that the public RDP port is closed on all nodes of the cluster.
            * Enabled - Indicates that the public RDP port is open on all nodes of the cluster.
            * NotSpecified - Indicates that the public RDP port is closed on all nodes of the cluster if
              VNet is defined, else is open on all nodes. It can be this default value only during
              cluster creation time. After creation, it will be either enabled or disabled.
        :type remote_login_port_public_access: str
        :return: A configuration object to be used when creating a Compute object.
        :rtype: azureml.contrib.compute.AmlWindowsComputeProvisioningConfiguration
        :raises: :class:`azureml.exceptions.ComputeTargetException`
        """
        config = AmlWindowsComputeProvisioningConfiguration(vm_size, vm_priority, vm_image, min_nodes,
                                                            max_nodes, idle_seconds_before_scaledown,
                                                            admin_username, admin_user_password,
                                                            vnet_resourcegroup_name, vnet_name, subnet_name,
                                                            tags, description, remote_login_port_public_access)
        return config

    @staticmethod
    def _build_create_payload(config, location, subscription_id):
        json_payload = copy.deepcopy(amlwindowscompute_payload_template)
        del(json_payload['properties']['resourceId'])
        del(json_payload['properties']['computeLocation'])
        json_payload['location'] = location
        if not config.vm_size and not config.vm_priority and not config.admin_username and not \
                config.vnet_resourcegroup_name and not config.vnet_name and not config.subnet_name \
                and not config.remote_login_port_public_access and not config.os_type and not config.vm_image:
            del(json_payload['properties']['properties'])
        else:
            if not config.vm_size:
                del(json_payload['properties']['properties']['vmSize'])
            else:
                json_payload['properties']['properties']['vmSize'] = config.vm_size
            if not config.os_type:
                del (json_payload['properties']['properties'][_OS_TYPE_KEY_NAME])
            else:
                json_payload['properties']['properties'][_OS_TYPE_KEY_NAME] = config.os_type

            if not config.vm_image:
                del (json_payload['properties']['properties'][_VM_IMAGE_KEY_NAME])
            else:
                json_payload['properties']['properties'][_VM_IMAGE_KEY_NAME] = config.vm_image
            if not config.vm_priority:
                del(json_payload['properties']['properties']['vmPriority'])
            else:
                json_payload['properties']['properties']['vmPriority'] = config.vm_priority
            json_payload['properties']['properties']['scaleSettings'] = config.scale_settings.serialize()
            if not config.admin_username:
                del(json_payload['properties']['properties']['userAccountCredentials'])
            else:
                json_payload['properties']['properties']['userAccountCredentials']['adminUserName'] = \
                    config.admin_username
                if config.admin_user_password:
                    json_payload['properties']['properties']['userAccountCredentials']['adminUserPassword'] = \
                        config.admin_user_password
                else:
                    del(json_payload['properties']['properties']['userAccountCredentials']['adminUserPassword'])

            if not config.vnet_name:
                del(json_payload['properties']['properties']['subnet'])
            else:
                json_payload['properties']['properties']['subnet'] = \
                    {"id": "/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.Network/virtualNetworks"
                     "/{2}/subnets/{3}".format(subscription_id, config.vnet_resourcegroup_name,
                                               config.vnet_name, config.subnet_name)}
            if not config.remote_login_port_public_access:
                del(json_payload['properties']['properties']['remoteLoginPortPublicAccess'])
            else:
                json_payload['properties']['properties']['remoteLoginPortPublicAccess'] = \
                    config.remote_login_port_public_access

        if config.tags:
            json_payload['tags'] = config.tags
        else:
            del(json_payload['tags'])
        if config.description:
            json_payload['properties']['description'] = config.description
        else:
            del(json_payload['properties']['description'])

        return json_payload

    def wait_for_completion(self, show_output=False, min_node_count=None, timeout_in_minutes=20):
        """Wait for the AmlWindowsCompute cluster to finish provisioning.

        This can be configured to wait for a minimum number of nodes, and to timeout after a set period of time.

        :param show_output: Boolean to provide more verbose output. Defaults to False.
        :type show_output: bool
        :param min_node_count: Minimum number of nodes to wait for before considering provisioning to be complete. This
            doesn't have to equal the minimum number of nodes that the compute was provisioned with, however it should
            not be greater than that.
        :type min_node_count: int
        :param timeout_in_minutes: The duration in minutes to wait before considering provisioning to have failed.
            Defaults to 20.
        :type timeout_in_minutes: int
        :raises: azureml.exceptions.ComputeTargetException
        """
        min_nodes_reached, timeout_reached, terminal_state_reached, status_errors_present = \
            self._wait_for_nodes(min_node_count, timeout_in_minutes, show_output)
        if show_output:
            print('AmlWindowsCompute wait for completion finished')
        if min_nodes_reached:
            if show_output:
                print('Minimum number of nodes requested have been provisioned')
        elif timeout_reached:
            if show_output:
                print('Wait timeout has been reached')
                if self.status:
                    print('Current provisioning state of AmlWindowsCompute is "{0}" and current node count is "{1}"'.
                          format(self.status.provisioning_state.capitalize(), self.status.current_node_count))
                else:
                    print('Current provisioning state of AmlWindowsCompute is "{}"'.
                          format(self.provisioning_state.capitalize()))
        elif terminal_state_reached:
            if self.status:
                state = self.status.provisioning_state.capitalize()
            else:
                state = self.provisioning_state.capitalize()
            if show_output:
                print('Terminal state of "{}" has been reached'.format(state))
                if state == 'Failed':
                    print('Provisioning errors: {}'.format(self.provisioning_errors))
        elif status_errors_present:
            if self.status:
                errors = self.status.errors
            else:
                errors = self.provisioning_errors
            if show_output:
                print('There were errors reported from AmlWindowsCompute:\n{}'.format(errors))

    def refresh_state(self):
        """Perform an in-place update of the properties of the object.

        Based on the current state of the corresponding cloud object.

        Primarily useful for manual polling of compute state.
        """
        cluster = AmlWindowsCompute(self.workspace, self.name)
        self.modified_on = cluster.modified_on
        self.provisioning_state = cluster.provisioning_state
        self.provisioning_errors = cluster.provisioning_errors
        self.cluster_resource_id = cluster.cluster_resource_id
        self.cluster_location = cluster.cluster_location
        self.vm_size = cluster.vm_size
        self.vm_priority = cluster.vm_priority
        self.scale_settings = cluster.scale_settings
        self.status = cluster.status
        self.remote_login_port_public_access = cluster.remote_login_port_public_access

    def get_status(self):
        """Retrieve the current detailed status for the AmlWindowsCompute cluster.

        :return: A detailed status object for the cluster.
        :rtype: azureml.contrib.compute.AmlWindowsComputeStatus
        """
        self.refresh_state()
        if not self.status:
            state = self.provisioning_state.capitalize()
            if state == 'Creating':
                print('AmlWindowsCompute is getting created. Consider calling wait_for_completion() first')
            elif state == 'Failed':
                print('AmlWindowsCompute is in a failed state, try deleting and recreating')
            else:
                print('Current provisioning state of AmlWindowsCompute is "{}"'.format(state))
            return None

        return self.status

    def delete(self):
        """Remove the AmlWindowsCompute object from its associated workspace.

        .. remarks::

            If this object was created through Azure ML,
            the corresponding cloud based objects will also be deleted. If this object was created externally
            and only attached to the workspace, it will raise exception and nothing will be changed.

        :raises: azureml.exceptions.ComputeTargetException
        """
        self._delete_or_detach('delete')

    def detach(self):
        """Detach is not supported for AmlWindowsCompute object. Try to use delete instead.

        :raises: azureml.exceptions.ComputeTargetException
        """
        raise ComputeTargetException('Detach is not supported for AmlWindowsCompute object. '
                                     'Try to use delete instead.')

    def serialize(self):
        """Convert this AmlWindowsCompute object into a JSON serialized dictionary.

        :return: The JSON representation of this AmlWindowsCompute object.
        :rtype: dict
        """
        scale_settings = self.scale_settings.serialize() if self.scale_settings else None
        subnet_id = None
        if self.vnet_resourcegroup_name and self.vnet_name and self.subnet_name:
            subnet_id = "/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.Network/virtualNetworks" \
                        "/{2}/subnets/{3}".format(self.workspace.subscription_id, self.vnet_resourcegroup_name,
                                                  self.vnet_name, self.subnet_name)

        amlcompute_properties = {'vmSize': self.vm_size, 'vmPriority': self.vm_priority,
                                 _OS_TYPE_KEY_NAME: self.os_type, _VM_IMAGE_KEY_NAME: self.vm_image,
                                 'scaleSettings': scale_settings,
                                 'userAccountCredentials': {'adminUserName': self.admin_username,
                                                            'adminUserPassword': self.admin_user_password},
                                 'subnet': {'id': subnet_id},
                                 'remoteLoginPortPublicAccess': self.remote_login_port_public_access}
        amlcompute_status = self.status.serialize() if self.status else None
        cluster_properties = {'description': self.description, 'resourceId': self.cluster_resource_id,
                              'computeType': self.type, 'computeLocation': self.cluster_location,
                              'provisioningState': self.provisioning_state,
                              'provisioningErrors': self.provisioning_errors,
                              'properties': amlcompute_properties, 'status': amlcompute_status}
        return {'id': self.id, 'name': self.name, 'location': self.location, 'tags': self.tags,
                'properties': cluster_properties}

    @staticmethod
    def deserialize(workspace, object_dict):
        """Convert a JSON object into an AmlWindowsCompute object.

        Will fail if the provided workspace is not the workspace the Compute is associated with.

        :param workspace: The workspace object the AmlWindowsCompute object is associated with.
        :type workspace: azureml.core.Workspace
        :param object_dict: A JSON object to convert to an AmlWindowsCompute object.
        :type object_dict: dict
        :return: The AmlWindowsCompute representation of the provided JSON object.
        :rtype: azureml.contrib.compute.AmlWindowsCompute
        :raises: azureml.exceptions.ComputeTargetException
        """
        AmlWindowsCompute._validate_get_payload(object_dict)
        target = AmlWindowsCompute(None, None)
        target._initialize(workspace, object_dict)
        return target

    @staticmethod
    def _validate_get_payload(payload):
        AmlCompute._validate_get_payload(payload)
        if payload['properties']['properties']:
            if "osType" not in payload['properties']['properties']:
                raise ComputeTargetException('Invalid cluster payload, missing '
                                             '["properties"]["properties"]["osType"]:\n'
                                             '{}'.format(payload))
            elif payload['properties']['properties']["osType"].lower() != _OS_TYPE.lower():
                raise ComputeTargetException('Invalid cluster payload. ["properties"]["properties"]["osType"] '
                                             'should be {} to create an AmlWindowsCompute cluster.'.format(_OS_TYPE))

    def get(self):
        """Return compute object."""
        return ComputeTarget._get(self.workspace, self.name)

    @staticmethod
    def list_windows_compute_targets(workspace):
        """List all AmlWindowsCompute objects within the workspace.

        :param workspace: The workspace object containing the objects to list.
        :type workspace: azureml.core.Workspace
        :return: List of compute targets within the workspace.
        :rtype: builtin.list[azureml.contrib.compute.AmlWindowsCompute]
        :raises: azureml.exceptions.ComputeTargetException
        """
        envs = []
        endpoint = 'https://management.azure.com/subscriptions/{}/resourceGroups/{}/providers/' \
                   'Microsoft.MachineLearningServices/workspaces/{}/computes'.format(workspace.subscription_id,
                                                                                     workspace.resource_group,
                                                                                     workspace.name)
        headers = workspace._auth.get_authentication_header()
        AmlWindowsCompute.__add_request_tracking_headers(headers)
        params = {'api-version': MLC_WORKSPACE_API_VERSION}
        resp = ClientBase._execute_func(get_requests_session().get, endpoint, params=params, headers=headers)

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            raise ComputeTargetException('Error occurred retrieving targets:\n'
                                         'Response Code: {}\n'
                                         'Headers: {}\n'
                                         'Content: {}'.format(resp.status_code, resp.headers, resp.content))
        content = resp.content
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        result_list = json.loads(content)
        paginated_results = get_paginated_compute_results(result_list, headers)
        for env in paginated_results:
            if 'properties' in env and 'computeType' in env['properties']:
                compute_type = env['properties']['computeType']
                env_obj = None
                if compute_type.lower() == _COMPUTE_TYPE.lower():
                    if _OS_TYPE_KEY_NAME in env['properties']['properties'] \
                            and env['properties']['properties'][_OS_TYPE_KEY_NAME].lower() == 'windows':
                        env_obj = AmlWindowsCompute.deserialize(workspace, env)
                else:
                    pass

                if env_obj:
                    envs.append(env_obj)
        return envs

    @staticmethod
    def __add_request_tracking_headers(headers):
        if RequestHeaders.CLIENT_REQUEST_ID not in headers:
            headers[RequestHeaders.CLIENT_REQUEST_ID] = str(uuid.uuid4())

        if RequestHeaders.CLIENT_SESSION_ID not in headers:
            headers[RequestHeaders.CLIENT_SESSION_ID] = _ClientSessionId

        if RequestHeaders.USER_AGENT not in headers:
            headers[RequestHeaders.USER_AGENT] = get_user_agent()


class AmlWindowsComputeProvisioningConfiguration(AmlComputeProvisioningConfiguration):
    """Provisioning configuration object for AmlWindowsCompute targets.

    This objects is used to define the configuration parameters for provisioning AmlWindowsCompute objects.

    :param vm_size: Size of agent VMs. More details can be found here: https://aka.ms/azureml-vm-details.
        Note that not all sizes are available in all regions, as detailed in the previous link.
        Defaults to Standard_NC6.
    :type vm_size: str
    :param vm_priority: dedicated or lowpriority VMs. If not specified, will default to dedicated.
    :type vm_priority: str
    :param vm_image: Virtual machine image to be used for the Windows compute target.
        Example : { "id" : "<image_id>/versions/<version>"}. Please refer to `Create an image definition
        <https://docs.microsoft.com/en-us/azure/virtual-machines/windows/shared-images-portal#create-an-image-definition>`_.
        If not specified, will default to DSVM Windows Server 2016 image.
    :type vm_image: dict
    :param min_nodes: Minimum number of nodes to use on the cluster. If not specified, will default to 0.
    :type min_nodes: int
    :param max_nodes: Maximum number of nodes to use on the cluster. Defaults to 4.
    :type max_nodes: int
    :param idle_seconds_before_scaledown: Node idle time in seconds before scaling down the cluster.
        Defaults to 120
    :type idle_seconds_before_scaledown: int
    :param admin_username: Name of the administrator user account which can be used to login into nodes.
    :type admin_username: str
    :param admin_user_password: Password of the administrator user account.
    :type admin_user_password: str
    :param vnet_resourcegroup_name: Name of the resource group where the virtual network is located.
    :type vnet_resourcegroup_name: str
    :param vnet_name: Name of the virtual network.
    :type vnet_name: str
    :param subnet_name: Name of the subnet inside the vnet.
    :type subnet_name: str
    :param tags: A dictionary of key value tags to provide to the compute object.
    :type tags: dict[str, str]
    :param description: A description to provide to the compute object.
    :type description: str
    :param remote_login_port_public_access: State of the public RDP. Possible values are:
        Disabled - Indicates that the public RDP port is closed on all nodes of the cluster.
        Enabled - Indicates that the public RDP port is open on all nodes of the cluster.
        Defaults to NotSpecified - Indicates that the public RDP port is closed on all nodes of the cluster if
        VNet is defined, else is open on all nodes. It can be default only during cluster creation time,
        after creation it will be either enabled or disabled.
    :type remote_login_port_public_access: str
    """

    def __init__(self, vm_size='', vm_priority="dedicated", vm_image=None, min_nodes=0,
                 max_nodes=None, idle_seconds_before_scaledown=None,
                 admin_username=None, admin_user_password=None, vnet_resourcegroup_name=None,
                 vnet_name=None, subnet_name=None, tags=None, description=None,
                 remote_login_port_public_access="NotSpecified"):
        """Create a configuration object for provisioning an AmlWindowsCompute target.

        :param vm_size: Size of agent VMs. More details can be found here: https://aka.ms/azureml-vm-details.
            Note that not all sizes are available in all regions, as detailed in the previous link.
            Defaults to Standard_NC6.
        :type vm_size: str
        :param vm_priority: dedicated or lowpriority VMs. If not specified, will default to dedicated.
        :type vm_priority: str
        :param vm_image: Virtual machine image to be used for the Windows compute target.
            Example : { "id" : "<image_id>/versions/<version>"}. Please refer to `Create an image definition
            <https://docs.microsoft.com/en-us/azure/virtual-machines/windows/shared-images-portal#create-an-image-definition>`_.
            If not specified, will default to DSVM Windows Server 2016 image.
        :type vm_image: dict
        :param min_nodes: Minimum number of nodes to use on the cluster. If not specified, will default to 0.
        :type min_nodes: int
        :param max_nodes: Maximum number of nodes to use on the cluster. Defaults to 4.
        :type max_nodes: int
        :param idle_seconds_before_scaledown: Node idle time in seconds before scaling down the cluster.
            Defaults to 120
        :type idle_seconds_before_scaledown: int
        :param admin_username: Name of the administrator user account which can be used to login into nodes.
        :type admin_username: str
        :param admin_user_password: Password of the administrator user account
        :type admin_user_password: str
        :param vnet_resourcegroup_name: Name of the resource group where the virtual network is located.
        :type vnet_resourcegroup_name: str
        :param vnet_name: Name of the virtual network.
        :type vnet_name: str
        :param subnet_name: Name of the subnet inside the vnet.
        :type subnet_name: str
        :param tags: A dictionary of key value tags to provide to the compute object.
        :type tags: dict[str, str]
        :param description: A description to provide to the compute object.
        :type description: str
        :param remote_login_port_public_access: State of the public RDP. Possible values are:
            Disabled - Indicates that the public RDP port is closed on all nodes of the cluster.
            Enabled - Indicates that the public RDP port is open on all nodes of the cluster.
            Defaults to NotSpecified - Indicates that the public RDP port is closed on all nodes of the cluster if
            VNet is defined, else is open on all nodes. It can be default only during cluster creation time,
            after creation it will be either enabled or disabled.
        :type remote_login_port_public_access: str
        :return: A configuration object to be used when creating a Compute object.
        :rtype: azureml.contrib.compute.AmlWindowsComputeProvisioningConfiguration
        :raises: azureml.exceptions.ComputeTargetException
        """
        super().__init__(vm_size, vm_priority, min_nodes, max_nodes, idle_seconds_before_scaledown,
                         admin_username, admin_user_password,
                         vnet_resourcegroup_name=vnet_resourcegroup_name,
                         vnet_name=vnet_name, subnet_name=subnet_name, tags=tags, description=description,
                         remote_login_port_public_access=remote_login_port_public_access)
        self.vm_image = vm_image
        self.os_type = _OS_TYPE


class AmlWindowsComputeStatus(AmlComputeStatus):
    """Detailed status for an AmlWindowsCompute object.

    .. remarks::

        Initialize an AmlWindowsComputeStatus object.

    :param allocation_state: String description of the current allocation state.
    :type allocation_state: str
    :param allocation_state_transition_time: Time of the most recent allocation state change.
    :type allocation_state_transition_time: datetime.datetime
    :param creation_time: Cluster creation time.
    :type creation_time: datetime.datetime
    :param current_node_count: The current number of nodes used by the cluster.
    :type current_node_count: int
    :param errors: A list of error details, if any.
    :type errors: builtin.list
    :param modified_time: Cluster modification time.
    :type modified_time: datetime.datetime
    :param node_state_counts: An object containing counts of the various current node states in the cluster.
    :type node_state_counts: azureml.contrib.core.AmlComputeNodeStateCounts
    :param provisioning_state: Current provisioning state of the cluster.
    :type provisioning_state: str
    :param provisioning_state_transition_time: Time of the most recent provisioning state change.
    :type provisioning_state_transition_time: datetime.datetime
    :param scale_settings: An object containing the specified scale settings for the cluster.
    :type scale_settings: ScaleSettings
    :param target_node_count: The target number of nodes for by the cluster.
    :type target_node_count: int
    :param vm_priority: dedicated or lowpriority VMs.
    :type vm_priority: str
    :param vm_size: Size of agent VMs. More details can be found here: https://aka.ms/azureml-vm-details.
        Note that not all sizes are available in all regions, as detailed in the previous link.
    :type vm_size: str
    :param vm_image: Virtual machine image to be used for the Windows compute target.
        Example : { "id" : "<image_id>/versions/<version>"}. Please refer to `Create an image definition
        <https://docs.microsoft.com/en-us/azure/virtual-machines/windows/shared-images-portal#create-an-image-definition>`_.
        If not specified, will default to DSVM Windows Server 2016 image.
    :type vm_image: dict
    :param os_type: OS type of the compute target. It should be set to Windows for AmlWindowsCompute type.
    :type os_type: str
    """

    def __init__(self, allocation_state, allocation_state_transition_time, creation_time, current_node_count,
                 errors, modified_time, node_state_counts, provisioning_state, provisioning_state_transition_time,
                 scale_settings, target_node_count, vm_priority, vm_size, vm_image, os_type):
        """Initialize an AmlWindowsComputeStatus object.

        :param allocation_state: String description of the current allocation state.
        :type allocation_state: str
        :param allocation_state_transition_time: Time of the most recent allocation state change.
        :type allocation_state_transition_time: datetime.datetime
        :param creation_time: Cluster creation time.
        :type creation_time: datetime.datetime
        :param current_node_count: The current number of nodes used by the cluster.
        :type current_node_count: int
        :param errors: A list of error details, if any.
        :type errors: builtin.list
        :param modified_time: Cluster modification time.
        :type modified_time: datetime.datetime
        :param node_state_counts: An object containing counts of the various current node states in the cluster.
        :type node_state_counts: azureml.contrib.compute.AmlComputeNodeStateCounts
        :param provisioning_state: Current provisioning state of the cluster.
        :type provisioning_state: str
        :param provisioning_state_transition_time: Time of the most recent provisioning state change.
        :type provisioning_state_transition_time: datetime.datetime
        :param scale_settings: An object containing the specified scale settings for the cluster.
        :type scale_settings: ScaleSettings
        :param target_node_count: The target number of nodes for by the cluster.
        :type target_node_count: int
        :param vm_priority: dedicated or lowpriority VMs.
        :type vm_priority: str
        :param vm_size: Size of agent VMs. More details can be found here: https://aka.ms/azureml-vm-details.
            Note that not all sizes are available in all regions, as detailed in the previous link.
        :type vm_size: str
        :param vm_image: Virtual machine image to be used for the Windows compute target.
            Example : { "id" : "<image_id>/versions/<version>"}. Please refer to `Create an image definition
            <https://docs.microsoft.com/en-us/azure/virtual-machines/windows/shared-images-portal#create-an-image-definition>`_.
            If not specified, will default to DSVM Windows Server 2016 image.
        :type vm_image: dict
        :param os_type: OS type of the compute target. It should be set to Windows for AmlWindowsCompute type.
        :type os_type: str
        """
        super().__init__(allocation_state, allocation_state_transition_time, creation_time, current_node_count,
                         errors, modified_time, node_state_counts, provisioning_state,
                         provisioning_state_transition_time, scale_settings, target_node_count,
                         vm_priority, vm_size)
        self.vm_image = vm_image
        self.os_type = os_type

    def serialize(self):
        """Convert this AmlWindowsComputeStatus object into a JSON serialized dictionary.

        :return: The JSON representation of this AmlWindowsComputeStatus object.
        :rtype: dict
        """
        allocation_state_transition_time = self.allocation_state_transition_time.isoformat() \
            if self.allocation_state_transition_time else None
        creation_time = self.creation_time.isoformat() if self.creation_time else None
        modified_time = self.modified_time.isoformat() if self.modified_time else None
        node_state_counts = self.node_state_counts.serialize() if self.node_state_counts else None
        provisioning_state_transition_time = self.provisioning_state_transition_time.isoformat() \
            if self.provisioning_state_transition_time else None
        scale_settings = self.scale_settings.serialize() if self.scale_settings else None
        return {'currentNodeCount': self.current_node_count, 'targetNodeCount': self.target_node_count,
                'nodeStateCounts': node_state_counts, 'allocationState': self.allocation_state,
                'allocationStateTransitionTime': allocation_state_transition_time, 'errors': self.errors,
                'creationTime': creation_time, 'modifiedTime': modified_time,
                'provisioningState': self.provisioning_state,
                'provisioningStateTransitionTime': provisioning_state_transition_time,
                'scaleSettings': scale_settings,
                'vmPriority': self.vm_priority, 'vmSize': self.vm_size,
                _OS_TYPE_KEY_NAME: self.os_type, _VM_IMAGE_KEY_NAME: self.vm_image}

    @staticmethod
    def deserialize(object_dict):
        """Convert a JSON object into an AmlWindowsComputeStatus object.

        :param object_dict: A JSON object to convert to an AmlWindowsComputeStatus object.
        :type object_dict: dict
        :return: The AmlWindowsComputeStatus representation of the provided JSON object.
        :rtype: azureml.contrib.compute.AmlWindowsComputeStatus
        :raises: azureml.exceptions.ComputeTargetException
        """
        if not object_dict:
            return None
        allocation_state = object_dict['properties']['allocationState'] \
            if 'allocationState' in object_dict['properties'] else None
        allocation_state_transition_time = parse(object_dict['properties']['allocationStateTransitionTime']) \
            if 'allocationStateTransitionTime' in object_dict['properties'] else None
        creation_time = parse(object_dict['createdOn']) \
            if 'createdOn' in object_dict else None
        current_node_count = object_dict['properties']['currentNodeCount'] \
            if 'currentNodeCount' in object_dict['properties'] else None
        errors = object_dict['properties']['errors'] \
            if 'errors' in object_dict['properties'] else None
        modified_time = parse(object_dict['modifiedOn']) \
            if 'modifiedOn' in object_dict else None
        node_state_counts = AmlComputeNodeStateCounts.deserialize(object_dict['properties']['nodeStateCounts']) \
            if 'nodeStateCounts' in object_dict['properties'] else None
        provisioning_state = object_dict['provisioningState'] \
            if 'provisioningState' in object_dict else None
        provisioning_state_transition_time = parse(object_dict['provisioningStateTransitionTime']) \
            if 'provisioningStateTransitionTime' in object_dict else None
        scale_settings = ScaleSettings.deserialize(object_dict['properties']['scaleSettings']) \
            if 'scaleSettings' in object_dict['properties'] else None
        target_node_count = object_dict['properties']['targetNodeCount'] \
            if 'targetNodeCount' in object_dict['properties'] else None
        vm_priority = object_dict['properties']['vmPriority'] if 'vmPriority' in object_dict['properties'] else None
        vm_size = object_dict['properties']['vmSize'] if 'vmSize' in object_dict['properties'] else None
        os_type = object_dict['properties'][_OS_TYPE_KEY_NAME] \
            if _OS_TYPE_KEY_NAME in object_dict['properties'] else None
        vm_image = object_dict['properties'][_VM_IMAGE_KEY_NAME] \
            if _VM_IMAGE_KEY_NAME in object_dict['properties'] else None

        return AmlWindowsComputeStatus(allocation_state, allocation_state_transition_time, creation_time,
                                       current_node_count, errors, modified_time, node_state_counts,
                                       provisioning_state, provisioning_state_transition_time, scale_settings,
                                       target_node_count, vm_priority, vm_size, vm_image, os_type)
