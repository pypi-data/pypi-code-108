# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import time
import requests
import uuid
import random

from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.keyvault import KeyVaultManagementClient
from azureml._vendor.azure_resources import ResourceManagementClient
from azureml._base_sdk_common.common import fetch_tenantid_from_aad_token

from azureml.exceptions import ProjectSystemException, UserErrorException

from ._arm_deployment_orchestrator import ArmDeploymentOrchestrator
from .arm_template_builder import (
    ArmTemplateBuilder,
    build_storage_account_resource,
    build_keyvault_account_resource,
    build_application_insights_resource,
    build_workspace_resource
)


CONTAINER_REGISTRY = "ContainerRegistry"
STORAGE = "StorageAccount"
USERASSIGNEDIDENTITY = "ManagedIdentity"
KEY_VAULT = "KeyVault"
APP_INSIGHTS = "AppInsights"
# Another spelling of application insights, used in developer workspaces
APPLICATION_INSIGHTS = "ApplicationInsights"
WORKSPACE = "Workspace"


def get_application_insights_region(workspace_region):
    '''
    Application Insights is not available in all locations. This function handles such exceptions
    by providing an alternative region for Application Insights.
    Update according to https://azure.microsoft.com/en-us/global-infrastructure/services/?products=monitor
    '''
    return {
        # TODO: We should replace this map with fetching actual appinsight locations using ARM API
        # So that we would only need to main a list of exceptions, not a list where appinsight is present.
        "australiaeast": "australiaeast",
        "canadacentral": "canadacentral",
        "centraluseuap": "eastus",
        "chinaeast2": "chinaeast2",
        "eastus": "eastus",
        "eastus2": "eastus2",
        "eastus2euap": "eastus",
        "northeurope": "northeurope",
        "southcentralus": "southcentralus",
        "southeastasia": "southeastasia",
        "uksouth": "uksouth",
        "usgovvirginia": "usgovvirginia",
        "usgovarizona": "usgovarizona",
        "westcentralus": "westus2",
        "westeurope": "westeurope",
        "westus2": "westus2",
        "centralindia": "centralindia",
        "eastasia": "eastasia",
        "japaneast": "japaneast",
        "westus": "westus",
        "koreacentral": "koreacentral",
        "francecentral": "francecentral",
        "brazilsouth": "brazilsouth",
        "usseceast": "usseceast",
        "ussecwest": "ussecwest"
    }.get(workspace_region, "eastus")


class WorkspaceArmDeploymentOrchestrator(ArmDeploymentOrchestrator):

    def __init__(self, auth, resource_group_name, location,
                 subscription_id, workspace_name, deployment_name=None,
                 storage=None, keyVault=None, containerRegistry=None, adbWorkspace=None,
                 primary_user_assigned_identity=None,
                 appInsights=None, cmkKeyVault=None, resourceCmkUri=None,
                 hbiWorkspace=False,
                 sku='Basic', tags=None,
                 user_assigned_identity_for_cmk_encryption=None,
                 systemDatastoresAuthMode='accesskey',
                 api_version="2021-01-01"):

        deployment_name = deployment_name if deployment_name \
            else '{0}_{1}'.format('Microsoft.MachineLearningServices', random.randint(100, 99999))
        super().__init__(auth, resource_group_name, subscription_id, deployment_name)
        self.auth = auth
        self.subscription_id = subscription_id
        self.resource_group_name = resource_group_name
        self.workspace_name = workspace_name
        self.master_template = ArmTemplateBuilder()
        self.workspace_dependencies = []
        self.location = location.lower().replace(" ", "")
        self.sku = sku
        self.tags = tags
        try:
            from .workspace_location_resolver import get_workspace_dependent_resource_location
            self.dependent_resource_location = get_workspace_dependent_resource_location(location)
        except Exception:
            self.dependent_resource_location = location
        self.resources_being_deployed = {}

        self.vault_name = ''
        self.storage_name = ''
        self.insights_name = ''
        self.keyVault = keyVault
        self.storage = storage
        self.appInsights = appInsights
        self.containerRegistry = containerRegistry
        self.adbWorkspace = adbWorkspace
        self.cmkKeyVault = cmkKeyVault
        self.resourceCmkUri = resourceCmkUri
        self.userAssignedIdentityForCmkEncryption = user_assigned_identity_for_cmk_encryption
        self.hbiWorkspace = hbiWorkspace
        self.primary_user_assigned_identity = primary_user_assigned_identity
        self.systemDatastoresAuthMode = systemDatastoresAuthMode
        self.api_version = api_version
        self.error = None

    def deploy_workspace(self, show_output=True):
        try:
            # first handle resources that user doesn't bring themselves
            self._handle_nonexistant_resources()

            # add the workspace itself to the template
            self._add_workspace_to_template()
            # build the template
            template = self.master_template.build()

            # deploy the template
            self._arm_deploy_template(template)

            if show_output:
                while not self.poller.done():
                    self._check_deployment_status()
                    time.sleep(5)

                if self.poller._exception is not None:
                    self.error = self.poller._exception
                else:
                    # one last check to make sure all print statements make it
                    self._check_deployment_status()
            else:
                try:
                    self.poller.wait()
                except Exception:
                    self.error = self.poller._exception
        except Exception as ex:
            self.error = ex

        if self.error is not None:
            error_msg = "Unable to create the workspace. \n {}".format(self.error)
            print(error_msg)

    def _handle_nonexistant_resources(self):
        self.keyVault = self._generate_key_vault() if self.keyVault is None else self.keyVault
        self.storage = self._generate_storage() if self.storage is None else self.storage
        self.appInsights = self._generate_appInsights() if self.appInsights is None else self.appInsights

    def _generate_key_vault(self):
        # Vault name must only contain alphanumeric characters and dashes and cannot start with a number.
        # Vault name must be between 3-24 alphanumeric characters.
        # The name must begin with a letter, end with a letter or digit, and not contain consecutive hyphens.
        self.vault_name = get_name_for_dependent_resource(self.workspace_name, 'keyvault')
        token = self.auth._get_arm_token()
        tenantId = fetch_tenantid_from_aad_token(token)
        keyvault_account = build_keyvault_account_resource(self.vault_name,
                                                           self.dependent_resource_location,
                                                           tenantId,
                                                           self.tags)
        self.master_template.add_resource(keyvault_account)
        self.workspace_dependencies.append("[resourceId('{}/{}', '{}')]".format('Microsoft.KeyVault', 'vaults',
                                                                                self.vault_name))
        self.resources_being_deployed[self.vault_name] = (KEY_VAULT, None)
        return get_arm_resourceId(self.subscription_id, self.resource_group_name,
                                  'Microsoft.KeyVault/vaults', self.vault_name)

    def _generate_storage(self):
        self.storage_name = get_name_for_dependent_resource(self.workspace_name, 'storage')

        self.master_template.add_resource(build_storage_account_resource(self.storage_name,
                                                                         self.dependent_resource_location,
                                                                         self.tags))
        self.workspace_dependencies.append(
            "[resourceId('{}/{}', '{}')]".format('Microsoft.Storage', 'storageAccounts', self.storage_name))
        storage = get_arm_resourceId(
            self.subscription_id,
            self.resource_group_name,
            'Microsoft.Storage/storageAccounts',
            self.storage_name)
        self.resources_being_deployed[self.storage_name] = (STORAGE, None)
        return storage

    def _add_workspace_to_template(self):
        workspace_resource = build_workspace_resource(
            self.workspace_name,
            self.location,
            self.keyVault,
            self.containerRegistry,
            adbWorkspace=self.adbWorkspace,
            storageAccount=self.storage,
            appInsights=self.appInsights,
            primary_user_assigned_identity=self.primary_user_assigned_identity,
            cmkKeyVault=self.cmkKeyVault,
            resourceCmkUri=self.resourceCmkUri,
            hbiWorkspace=self.hbiWorkspace,
            sku=self.sku,
            tags=self.tags,
            userAssignedIdentityForCmkEncryption=self.userAssignedIdentityForCmkEncryption,
            systemDatastoresAuthMode=self.systemDatastoresAuthMode,
            api_version=self.api_version)
        workspace_resource['dependsOn'] = self.workspace_dependencies
        self.master_template.add_resource(workspace_resource)
        self.resources_being_deployed[self.workspace_name] = (WORKSPACE, None)

    def _generate_appInsights(self):
        # Application name only allows alphanumeric characters, periods, underscores,
        # hyphens and parenthesis and cannot end in a period
        self.insights_name = get_name_for_dependent_resource(self.workspace_name, 'insights')

        insights_location = get_application_insights_region(self.location)
        self.master_template.add_resource(
            build_application_insights_resource(self.insights_name, insights_location, self.tags))
        self.workspace_dependencies.append(
            "[resourceId('{}/{}', '{}')]".format('microsoft.insights', 'components', self.insights_name))
        appInsights = get_arm_resourceId(
            self.subscription_id,
            self.resource_group_name,
            'microsoft.insights/components',
            self.insights_name)
        self.resources_being_deployed[self.insights_name] = (APP_INSIGHTS, None)
        return appInsights


def get_name_for_dependent_resource(workspace_name, resource_type):
    alphabets_str = ""
    for char in workspace_name.lower():
        if char.isalpha() or char.isdigit():
            alphabets_str = alphabets_str + char
    rand_str = str(uuid.uuid4()).replace("-", "")
    resource_name = alphabets_str[:8] + resource_type[:8] + rand_str

    return resource_name[:24]


def delete_storage(auth, resource_group_name, storage_name, subscription_id):
    """Deletes storage account"""
    client = auth._get_service_client(StorageManagementClient, subscription_id)
    return client.storage_accounts.delete(resource_group_name, storage_name)


def delete_insights(auth, resource_group_name, insights_name, subscription_id):
    """Deletes application insights"""
    rg_scope = "subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}".format(
        subscriptionId=subscription_id, resourceGroupName=resource_group_name)
    app_insights_id = rg_scope + "/providers/microsoft.Insights/components/{name}".format(
        name=insights_name)
    host = auth._get_cloud_type().endpoints.resource_manager
    header = auth.get_authentication_header()
    url = host + app_insights_id + "?api-version=2015-05-01"
    requests.delete(url, headers=header)


def delete_keyvault(auth, resource_group_name, vault_name, subscription_id):
    """Deletes key vault"""
    client = auth._get_service_client(KeyVaultManagementClient, subscription_id)
    return client.vaults.delete(resource_group_name, vault_name)


def delete_kv_armId(auth, kv_armid, throw_exception=False):
    """Deletes kv account"""
    try:
        _check_valid_arm_id(kv_armid)
        subcription_id, resource_group, resource_name \
            = _get_subscription_id_resource_group_resource_name_from_arm_id(kv_armid)
        return delete_keyvault(auth, resource_group, resource_name, subcription_id)
    except Exception:
        if throw_exception:
            raise


def get_keyvault(auth, subscription_id, resource_group_name, keyvault_name):
    client = auth._get_service_client(KeyVaultManagementClient, subscription_id)
    return client.vaults.get(resource_group_name, keyvault_name)


def delete_insights_armId(auth, insights_armid, throw_exception=False):
    """Deletes insights account"""
    try:
        _check_valid_arm_id(insights_armid)
        subcription_id, resource_group, resource_name \
            = _get_subscription_id_resource_group_resource_name_from_arm_id(insights_armid)
        return delete_insights(auth, resource_group, resource_name, subcription_id)
    except Exception:
        if throw_exception:
            raise


def get_insights(auth, subscription_id, resource_group_name, insights_name):
    """Deletes application insights"""
    rg_scope = "subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}".format(
        subscriptionId=subscription_id, resourceGroupName=resource_group_name)
    app_insights_id = rg_scope + "/providers/microsoft.Insights/components/{name}".format(
        name=insights_name)
    host = auth._get_cloud_type().endpoints.resource_manager
    header = auth.get_authentication_header()
    url = host + app_insights_id + "?api-version=2015-05-01"
    return requests.get(url, headers=header)


def delete_storage_armId(auth, storage_armid, throw_exception=False):
    """Deletes storage account"""
    try:
        _check_valid_arm_id(storage_armid)
        subcription_id, resource_group, resource_name \
            = _get_subscription_id_resource_group_resource_name_from_arm_id(storage_armid)
        return delete_storage(auth, resource_group, resource_name, subcription_id)
    except Exception:
        if throw_exception:
            raise


def _get_subscription_id_resource_group_resource_name_from_arm_id(arm_id):
    parts = arm_id.split('/')
    sub_id = parts[2]
    rg_name = parts[4]
    resource_name = parts[-1]
    return sub_id, rg_name, resource_name


def get_storage_account(auth, subscription_id, resource_group_name, storage_name):
    """Get storage account"""
    client = auth._get_service_client(StorageManagementClient, subscription_id)
    return client.storage_accounts.get_properties(resource_group_name, storage_name)


def _check_valid_arm_id(resource_arm_id):
    parts = resource_arm_id.split('/')
    if len(parts) != 9:
        raise UserErrorException("Wrong format of the given arm id={}".format(resource_arm_id))


def get_arm_resourceId(subscription_id,
                       resource_group_name,
                       provider,
                       resource_name):

    return '/subscriptions/{}/resourceGroups/{}/providers/{}/{}'.format(
        subscription_id,
        resource_group_name,
        provider,
        resource_name)


def create_storage_account(auth, resource_group_name, workspace_name,
                           location, subscription_id):
    """
    Creates a storage account.
    :param auth: auth object.
    :type auth: azureml.core.authentication.AbstractAuthentication
    :param resource_group_name:
    :param workspace_name:
    :param location:
    :param subscription_id:
    :return: Returns storage account id.
    :rtype: str
    """
    if 'eastus2euap' == location.replace(' ', '').lower():
        location = 'eastus2'
    body = {'location': location,
            'sku': {'name': 'Standard_LRS'},
            'kind': 'Storage',
            'properties':
                {"encryption":
                    {"keySource": "Microsoft.Storage",
                     "services": {
                         "blob": {
                             "enabled": 'true'
                         }
                     }
                     },
                 "supportsHttpsTrafficOnly": True
                 }
            }
    rg_scope = "subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}".format(
        subscriptionId=subscription_id, resourceGroupName=resource_group_name)

    storage_account_id = rg_scope + "/providers/microsoft.Storage/storageAccounts/{workspaceName}".format(
        workspaceName=workspace_name)
    host = auth._get_cloud_type().endpoints.resource_manager
    header = auth.get_authentication_header()
    url = host + storage_account_id + "?api-version=2016-12-01"

    response = requests.put(url, headers=header, json=body)
    if response.status_code not in [200, 201, 202]:
        # This could mean name conflict or max quota or something else, print the error message
        raise ProjectSystemException("Failed to create the storage account "
                                     "resource_group_name={}, workspace_name={}, "
                                     "subscription_id={}.\n Response={}".format(resource_group_name, workspace_name,
                                                                                subscription_id, response.text))

    return storage_account_id


def get_storage_key(auth, storage_account_id, storage_api_version):
    """

    :param auth:
    :type auth: azureml.core.authentication.AbstractAuthentication
    :param storage_account_id:
    :param storage_api_version:
    :return:
    """
    host = auth._get_cloud_type().endpoints.resource_manager
    header = auth.get_authentication_header()
    url = host + storage_account_id + "/listkeys?api-version=" + storage_api_version
    polling_interval = 3 * 60  # 3 minutes
    start_time = time.time()
    response = None
    while True and (time.time() - start_time < polling_interval):
        time.sleep(0.5)
        response = requests.post(url, headers=header)
        if response.status_code in [200]:
            break
    if storage_api_version == '2016-12-01':
        keys = response.json()
        access_key = keys['keys'][0]['value']
    else:
        keys = response.json()
        access_key = keys['primaryKey']
    return access_key


def get_arm_resource_id(resource_group_name, provider, resource_name, subscription_id):

    return '/subscriptions/{}/resourceGroups/{}/providers/{}/{}'.format(
        subscription_id, resource_group_name, provider, resource_name)


def get_location_from_resource_group(auth, resource_group_name, subscription_id):
    """

    :param auth:
    :param resource_group_name:
    :param subscription_id:
    :type subscription_id: str
    :return:
    """
    group = auth._get_service_client(ResourceManagementClient,
                                     subscription_id).resource_groups.get(resource_group_name)
    return group.location
