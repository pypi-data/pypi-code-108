import click
import uuid
import json
import requests
import subprocess
import re
import time

from spell.api import models
from halo import Halo

from spell.cli.constants import WORKER_OPEN_PORTS

from spell.cli.exceptions import (
    api_client_exception_handler,
    ExitException,
)
from spell.cli.utils import (
    cluster_utils,
    sentry,
    get_star_spinner_frames,
)
from spell.cli.utils.command import docs_option

CLUSTER_VERSION = 1
DEFAULT_REGION = "westus2"
CONTAINER_NAME = "spell-blob-container"
VNET_NAME = "spell-vnet"
SUBNET_NAME = "spell-subnet"
SECURITY_GROUP_NAME = "spell-security-group"
NUM_RETRIES = 15  # Retries for getting sp/app
# SSH, Docker Daemon, and Jupyter respectively

required_permissions = [
    "Microsoft.Compute/*",
    "Microsoft.Network/*",
    "Microsoft.Storage/*",
    "Microsoft.Support/*",
    "Microsoft.Authorization/*/read",
    "Microsoft.Resources/deployments/*",
    "Microsoft.Resources/subscriptions/resourceGroups/read",
]


@click.command(name="az", short_help="Sets up an Azure VNet as a Spell cluster")
@click.pass_context
@click.option("-n", "--name", "name", help="This will be used for you to identify the cluster")
@click.option(
    "-r",
    "--resource-group",
    "resource_group_name",
    help="This will be the name of the Resource Group Spell will create and "
    "store all its resources in within your Azure account",
    default="rg-spell",
)
@click.option(
    "-s",
    "--service-principal",
    "service_principal_name",
    help="Optionally give custom name to created Service Principal",
)
@docs_option("https://spell.ml/docs/az_ownvpc_setup/")
def create_azure(ctx, name, resource_group_name, service_principal_name):
    """
    This command creates an Azure VNet of your choosing as an external Spell cluster.
    This will let your organization create runs in that VNet, so your data never leaves
    your VNet. You create an Azure Blob Container of your choosing for all run outputs to be written to.
    After this cluster is set up you will be able to select the types and number of machines
    you would like Spell to create in this cluster.
    """

    # Verify the owner is the admin of an org
    spell_client = ctx.obj["client"]
    cluster_utils.validate_org_perms(spell_client, ctx.obj["owner"])

    try:
        from azure.graphrbac import GraphRbacManagementClient
        from azure.mgmt.resource import ResourceManagementClient
        from azure.mgmt.authorization import AuthorizationManagementClient
        from azure.mgmt.resource.subscriptions import SubscriptionClient
        from azure.mgmt.storage import StorageManagementClient
        from azure.mgmt.storage.models import StorageAccountCreateParameters, Sku, SkuName, Kind
        from spell.cli.utils.azure_credential_wrapper import AzureIdentityCredentialAdapter
        from azure.core.exceptions import ClientAuthenticationError, AzureError
        from azure.storage.blob import BlobServiceClient
        from azure.mgmt.network import NetworkManagementClient
        from azure.identity import DefaultAzureCredential

    except ImportError:
        click.echo("Please `pip install --upgrade 'spell[cluster-azure]'` and rerun this command")
        return

    click.echo(
        """This command will help you
        - Select a region to create resources in and a subscription for billing
        - Create an App and Service Principal
        - Create a Resource group in the specified region to manage your resources
        - Assign a role to your Service Principal that allows Spell to spin up and
            down machines and access your Blobs
        - Create a uniquely-named storage account
        - Set up an Blob Container to store your run outputs in
        - Set up a VNet and Subnet which Spell will spin up workers in to run your jobs
        - Set up a Security Group providing Spell SSH and Docker access to workers """
    )

    # Create Credentials
    """
    DefaultAzureCredential is the new credential that Microsoft recommends. However,
    this credential only works for packages with the prefix `azure-mgmt`.
    The hope is that eventually everything will use this credential. Until that happens,
    they recommend using the wrapper AzureIdentityCredentialAdapter().

    The resource id argument supplied to the wrapper dictates which token is returned. Different
    APIs require different tokens.

    credentials (Default Azure Credential): Azure's new credential that uses the azure identity
    library.
    management_creds (wrapper/default resource id): used for tenant id and authorization client
    graph_rbac_creds (wrapper/graph.windows.net resource id): used to create app/sp - library is
    being deprecated and will eventually use the following credential
    microsoft_graph_creds (wrapper/graph.microsoft.com resource id): This uses the new Microsoft
    Graph API to set client secret.

    https://docs.microsoft.com/en-us/azure/developer/python/azure-sdk-authenticate?tabs=cmd
    """
    # TODO(sruthi): Figure out a better way to authenticate
    try:
        credentials = DefaultAzureCredential(
            exclude_environment_credential=True,
            exclude_managed_identity_credential=True,
            exclude_visual_studio_code_credential=True,
            exclude_shared_token_cache_credential=True,
        )
        management_cred = AzureIdentityCredentialAdapter()
        management_cred.set_token()
        graph_rbac_creds = AzureIdentityCredentialAdapter(resource_id="https://graph.windows.net/")
        graph_rbac_creds.set_token()
        microsoft_graph_creds = AzureIdentityCredentialAdapter(resource_id="https://graph.microsoft.com/")
        microsoft_graph_creds.set_token()
    except ClientAuthenticationError:
        # NOTE: Default Azure Credential raises its own error
        raise ExitException("Please try again after logging into azure in your terminal")
    except AzureError as e:
        # This handles an "az login expiration exception"
        raise ExitException(f"Unexpected Azure error: {e}")

    # Validate cluster name
    if not name:
        cluster_utils.echo_delimiter()
        name = click.prompt("Enter a display name for this Azure cluster within Spell")

    if not service_principal_name:
        service_principal_name = f"sp-spell-{ctx.obj['owner']}"

    with api_client_exception_handler():
        spell_client.validate_cluster_name(name)

    # Queries for Subscription ID
    subscription_client = SubscriptionClient(credentials)
    subscription_id = get_subscription(subscription_client)
    if subscription_id is None:
        raise ExitException("No active subscriptions found")
    tenant_id = get_tenant_id(name)

    # Get Region
    cluster_utils.echo_delimiter()
    available_regions = [
        location.name for location in subscription_client.subscriptions.list_locations(subscription_id)
    ]
    region = click.prompt(
        "Please choose a region for your cluster. This might affect machine availability",
        type=click.Choice(available_regions),
        default=DEFAULT_REGION,
    )
    supports_no_gpu = region in (
        "canadaeast",
        "centralus",
        "westcentralus",
        "southafricawest",
        "eastasia",
        "australiacentral",
        "australiacentral2",
        "australiasoutheast",
        "brazilsoutheast",
        "chinaeast",
        "chinanorth",
        "francesouth",
        "germany",
        "germanycentral",
        "germanynorth",
        "germanywestcentral",
        "southindia",
        "westindia",
        "japanwest",
        "koreasouth",
        "switzerlandnorth",
        "switzerlandwest",
        "uaecentral",
        "ukwest",
    )
    if supports_no_gpu:
        if not click.confirm(
            f"Azure does not support GPU types in {region}. You can still create a cluster, but it will "
            "only have access to CPU types - continue?"
        ):
            return

    if ctx.obj["interactive"]:
        spinner = Halo(spinner=get_star_spinner_frames(ctx.obj["utf8"]))

    # Create Service Principal
    cluster_utils.echo_delimiter()
    client = GraphRbacManagementClient(graph_rbac_creds, tenant_id)
    client_id, sp_object_id, app_object_id = create_service_principal(client, service_principal_name, spinner)
    client_secret = set_client_secret(microsoft_graph_creds, app_object_id, spinner)
    set_api_permissions(microsoft_graph_creds, app_object_id, spinner)

    # Create Resource Group
    resource_client = ResourceManagementClient(credentials, subscription_id)
    resource_group = create_resource_group(resource_client, resource_group_name, region, spinner)

    # Creates and Assigns Custom Role to Service Principal
    authorization_client = AuthorizationManagementClient(management_cred, subscription_id)
    assign_contributor_role(authorization_client, resource_group.id, sp_object_id, subscription_id, spinner)

    # Create Networking
    network_client = NetworkManagementClient(credentials, subscription_id)
    create_network(network_client, resource_group_name, region, spinner)

    # Creates Storage Account
    storage_client = StorageManagementClient(credentials, subscription_id)
    params = StorageAccountCreateParameters(
        sku=Sku(name=SkuName.standard_ragrs),
        kind=Kind.storage_v2,
        location=region,
    )
    storage_account, storage_account_name = create_storage_account(
        storage_client, name, resource_group_name, params, spinner
    )

    # Get Storage Key
    click.echo(f"Fetching Storage Account `{storage_account_name}` access key...")
    list_keys = storage_client.storage_accounts.list_keys(resource_group_name, storage_account_name)
    storage_keys = {v.key_name: v.value for v in list_keys.keys}
    storage_key = storage_keys["key1"]

    # Creates Blob Container
    blob_service_client = BlobServiceClient(account_url=storage_account.primary_endpoints.blob, credential=storage_key)
    create_blob_container(storage_account_name, blob_service_client, spinner)

    cluster_utils.echo_delimiter()
    click.echo("Uploading cluster information to Spell...")
    with api_client_exception_handler():
        cluster = spell_client.create_azure_cluster(
            name,
            app_object_id,
            client_id,
            client_secret,
            region,
            resource_group_name,
            sp_object_id,
            storage_account_name,
            storage_key,
            subscription_id,
            tenant_id,
            CLUSTER_VERSION,
        )
    click.echo("Successfully uploaded cluster to Spell")

    # All done here, but warn them about Spell's setup requirement
    cluster_utils.echo_delimiter()
    url = f"{ctx.obj['web_url']}/{ctx.obj['owner']}/clusters/{cluster['name']}"
    click.echo(click.style("Almost done! Spell authorization required:", fg="yellow", bold=True))
    click.echo(
        "In order to fully authorize your new cluster, Spell must grant VM Image Read permissions to your App.\n"
        "Please contact your Spell representative and have them grant these permissions now.\n"
        "Once your Spell representative has confirmed that this is done, "
        f"your cluster {cluster['name']} will be initialized!\n"
        f"You may then head over to the web console to create machine types to execute your runs on - {url}"
    )


def get_tenant_id(name):
    """
    Shells out to Azure CLI to get Tenant ID
    """
    try:
        process = subprocess.run(["az", "account", "show"], check=True, stdout=subprocess.PIPE, universal_newlines=True)
        output = process.stdout
        data = json.loads(output)
        tenant_id = data["tenantId"]
    except Exception as e:
        # TODO(sruthi): Remove for customer when we are finished developing
        click.echo(f"ERROR: While extracting tenant id. Error was: {e}", err=True)
        sentry.capture_message(
            f"Error occured when extracting tenant id using the Azure CLI for cluster {name}: " f"Error was '{e}''"
        )
        tenant_id = click.prompt("Enter tenant id of Azure Active Directory")
    return tenant_id


def get_subscription(client):
    cluster_utils.echo_delimiter()
    click.echo("Querying for Subscription ID...")
    sub_ids = [sub.subscription_id for sub in client.subscriptions.list() if sub.state == "Enabled"]
    if not sub_ids:
        return None
    elif len(sub_ids) == 1:
        click.echo(f"One Subscription found: {sub_ids[0]}. " "Defaulting to this subscription for this cluster")
        return sub_ids[0]
    else:
        return click.prompt(
            "Please choose a subscription id from your active subscriptions",
            type=click.Choice(sub_ids),
        )


def create_service_principal(client, service_principal_name, spinner):
    """
    Prompts user for the pre-created Application/Service Principal IDs needed for mgmt
    Returns the client id (aka appID), sp object id and app object id
    """
    from azure.graphrbac.models.graph_error import GraphErrorException

    if spinner:
        spinner.text = "Creating Service Principal..."
        spinner.start()
    else:
        click.echo("Creating Service Principal...")
    try:
        app = client.applications.create(
            {
                "available_to_other_tenants": True,
                "display_name": service_principal_name,
                "reply_urls": ["https://spell.ml"],
            }
        )
        sp = client.service_principals.create({"app_id": app.app_id, "account_enabled": True})
    except GraphErrorException as e:
        sentry.capture_message(
            f"Error occured when attempting to create Service Principal {service_principal_name}: " f"Error was '{e}'"
        )
        raise ExitException(
            "Please ensure that your user has the appropriate Azure Active Directory Admin Role "
            "needed to create service principals in your local tenant."
        )

    # Waits for App and Service Principal to be created
    for i in range(NUM_RETRIES):
        if spinner:
            spinner.text = "Verifying Service Principal was created..."
        try:
            client.applications.get(app.object_id)
            client.service_principals.get(sp.object_id)
        except GraphErrorException as e:
            is_app_exception = f"Resource '{app.object_id}' does not exist" in str(e)
            is_sp_exception = f"Resource '{sp.object_id}' does not exist" in str(e)
            if not is_app_exception and not is_sp_exception:
                sentry.capture_exception(e)
                raise ExitException(f"Was not able to read newly created Service Principal `{service_principal_name}`")
            if i == NUM_RETRIES - 1:
                sentry.capture_message(
                    f"Retried {NUM_RETRIES} times to get service principal `{service_principal_name}`. "
                    f"Error was '{e}'"
                )
                raise ExitException(f"Was not able to Get Service Principal `{service_principal_name}`")
            time.sleep(3)
        else:
            break
    if spinner:
        spinner.stop()
    click.echo(f"Successfully created Service Principal `{service_principal_name}`")
    return app.app_id, sp.object_id, app.object_id


def set_client_secret(credentials, app_object_id, spinner):
    """
    Uses Microsoft Graph REST API to generate a client secret
    Returns the client secret and the end date (date the client secret expires)

    NOTE: There is no Python client library for this, so we do raw HTTP requests to the API.
    In the future we will use the python client API that has not yet been released.
    """

    if spinner:
        spinner.text = "Creating SP Client secret..."
        spinner.start()
    else:
        click.echo("Creating SP Client secret...")
    # Create Request
    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {credentials.token['access_token']}",
    }
    url = f"https://graph.microsoft.com/v1.0/applications/{app_object_id}/addPassword"
    payload = {
        "passwordCredential": {
            "displayName": "spellClientSecret",
            "endDateTime": "2222-01-01T00:00:00Z",  # Never expires
        },
    }

    # Execute request (with retries):
    for i in range(NUM_RETRIES):
        try:
            response = requests.post(url, data=json.dumps(payload), headers=header)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            text = e.response.text
            is_app_exception = f"Resource '{app_object_id}' does not exist" in text
            if not is_app_exception:
                sentry.capture_exception(e)
                raise ExitException(f"Error setting client secret: {text}")
            if i == NUM_RETRIES - 1:
                sentry.capture_message(
                    f"Retried {NUM_RETRIES} times to set client secret for `{app_object_id}`. " f"Error was '{text}'"
                )
                raise ExitException(f"Error setting client secret: {text}")
            time.sleep(3)
        else:
            break

    # Return Client Secret
    secret_info = json.loads(response.text)
    if spinner:
        spinner.stop()
    click.echo("Successfully created App client secret")
    return secret_info["secretText"]


def set_api_permissions(credentials, object_id, spinner):
    """
    Uses Microsoft Graph REST API to set 'User.Read' API Permissions
    """

    # Create Request
    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {credentials.token['access_token']}",
    }
    url = f"https://graph.microsoft.com/v1.0/applications/{object_id}"
    payload = {
        "requiredResourceAccess": [
            {
                # "Microsoft.Graph"
                "resourceAppId": "00000003-0000-0000-c000-000000000000",
                # "User.Read"
                "resourceAccess": [{"id": "e1fe6dd8-ba31-4d61-89e7-88639da4683d", "type": "Scope"}],
            },
        ]
    }

    # Execute request (with retries):
    for i in range(NUM_RETRIES):
        try:
            response = requests.patch(url, data=json.dumps(payload), headers=header)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            text = e.response.text
            is_app_exception = f"Resource '{object_id}' does not exist" in text
            if not is_app_exception:
                sentry.capture_exception(e)
                raise ExitException(f"Error setting API permissions: {text}")
            if i == NUM_RETRIES - 1:
                sentry.capture_message(
                    f"Retried {NUM_RETRIES} times to set API permissions for `{object_id}`. " f"Error was '{text}'"
                )
                raise ExitException(f"Error setting API permissions: {text}")
            time.sleep(3)
        else:
            break


def create_resource_group(resource_client, resource_group_name, region, spinner):
    cluster_utils.echo_delimiter()
    if spinner:
        spinner.text = "Creating Resource Group..."
        spinner.start()
    else:
        click.echo("Creating Resource Group...")

    if resource_client.resource_groups.check_existence(resource_group_name):
        if spinner:
            spinner.stop()
        raise ExitException(
            f"Resource group `{resource_group_name}` already exists - " "please select a different name"
        )
    resource_group = resource_client.resource_groups.create_or_update(resource_group_name, {"location": region})
    if spinner:
        spinner.stop()
    click.echo(f"Successfully created Resource Group `{resource_group_name}`")
    return resource_group


def assign_contributor_role(
    authorization_client,
    rg_id,
    sp_object_id,
    subscription_id,
    spinner,
):
    """Assigns `Contributor` role for the RG to SP"""
    cluster_utils.echo_delimiter()
    if spinner:
        spinner.text = "Assigning `Contributor` Role to Service Principal..."
        spinner.start()
    else:
        click.echo("Assigning `Contributor` Role to Service Principal...")

    # Assign Contributor Role to Service Principal
    authorization_client.role_assignments.create(
        rg_id,
        uuid.uuid4(),
        {
            "role_definition_id": f"/subscriptions/{subscription_id}/providers/"
            + "Microsoft.Authorization/roleDefinitions/b24988ac-6180-42a0-ab88-20f7382dd24c",
            "principal_id": sp_object_id,
            "principal_type": "ServicePrincipal",
        },
    )
    if spinner:
        spinner.stop()
    click.echo(f"Successfully assigned `Contributor` Role to Service Principal `{sp_object_id}`")


def assign_acr_roles(
    authorization_client,
    reg_id,
    sp_object_id,
    subscription_id,
):
    """Assigns `ACR Push` and `ACR Pull` roles for the Registry to SP"""
    cluster_utils.echo_delimiter()
    click.echo("Assigning `ACR Push and ACR Pull` Role to Service Principal...")

    # ACR Push Role has id 7f951dda-4ed3-4680-a7ca-43fe172d538d
    authorization_client.role_assignments.create(
        reg_id,
        uuid.uuid4(),
        {
            "role_definition_id": f"/subscriptions/{subscription_id}/providers/"
            + "Microsoft.Authorization/roleDefinitions/7f951dda-4ed3-4680-a7ca-43fe172d538d",
            "principal_id": sp_object_id,
            "principal_type": "ServicePrincipal",
        },
    )

    # ACR Pull Role has id 8311e382-0749-4cb8-b61a-304f252e45ec
    authorization_client.role_assignments.create(
        reg_id,
        uuid.uuid4(),
        {
            "role_definition_id": f"/subscriptions/{subscription_id}/providers/"
            + "Microsoft.Authorization/roleDefinitions/8311e382-0749-4cb8-b61a-304f252e45ec",
            "principal_id": sp_object_id,
            "principal_type": "ServicePrincipal",
        },
    )
    click.echo(f"Successfully assigned `ACR Push and ACR Pull` Role to Service Principal `{sp_object_id}`")


def delete_acr_roles(authorization_client, reg_scope):
    """Deletes `ACR Push` and `ACR Pull` roles for the Registry to SP"""
    cluster_utils.echo_delimiter()
    click.echo("Deleting `ACR Push and ACR Pull` Role to Service Principal...")

    role_assignments = authorization_client.role_assignments.list_for_scope(reg_scope)
    for role in role_assignments:
        if role.scope == reg_scope:
            authorization_client.role_assignments.delete_by_id(role.id)
    click.echo("Successfully deleted `ACR Push and ACR Pull` Role to Service Principal")


def create_network(network_client, resource_group_name, region, spinner):
    from azure.mgmt.network.v2020_06_01.models import SecurityRule
    from azure.mgmt.network.v2020_06_01.models import NetworkSecurityGroup
    from azure.core.exceptions import HttpResponseError

    cluster_utils.echo_delimiter()
    if spinner:
        spinner.text = "Creating VNet..."
        spinner.start()
    else:
        click.echo("Creating VNet...")

    # Create VPC
    cidr = "10.0.0.0/16"
    async_vnet_creation = network_client.virtual_networks.begin_create_or_update(
        resource_group_name,
        VNET_NAME,
        {"location": region, "address_space": {"address_prefixes": [cidr]}},
    )
    async_vnet_creation.wait()

    # Create Subnet
    if spinner:
        spinner.text = "Creating Subnet..."
    else:
        click.echo("Creating Subnet...")
    async_subnet_creation = network_client.subnets.begin_create_or_update(
        resource_group_name, VNET_NAME, SUBNET_NAME, {"address_prefix": cidr}
    )
    async_subnet_creation.result()

    # Create Security Group
    if spinner:
        spinner.text = "Creating Security Group..."
    else:
        click.echo("Creating Security Group...")
    nsg_params = NetworkSecurityGroup(id=SECURITY_GROUP_NAME, location=region, tags={"name": VNET_NAME})
    try:
        nsg = network_client.network_security_groups.begin_create_or_update(
            resource_group_name, SECURITY_GROUP_NAME, parameters=nsg_params
        )
    except HttpResponseError as e:
        raise ExitException(f"Unable to create new security group. Azure error: {e}")

    # Add Outbound Security Rules for Ingress Ports
    if spinner:
        spinner.text = "Adding Ingress/Egress rules to Security Group..."
    else:
        click.echo("Adding Ingress/Egress rules to Security Group...")
    priority = 100  # Determines the order in which Security Rules get processed, lower numbers have higher priority
    for port in WORKER_OPEN_PORTS:
        security_rule_name = f"spell-security-rule-{port}"
        security_rule_parameters = SecurityRule(
            name=security_rule_name,
            description="Allows the Spell API SSH and Docker access to worker machines",
            protocol="Tcp",
            source_port_range="*",
            destination_port_range=port,
            source_address_prefix="*",
            destination_address_prefix="*",
            access="Allow",
            direction="Inbound",
            priority=priority,
        )
        try:
            network_client.security_rules.begin_create_or_update(
                resource_group_name,
                SECURITY_GROUP_NAME,
                security_rule_name,
                security_rule_parameters,
            )
        except HttpResponseError as e:
            raise ExitException(f"Error creating Security Rule. Azure error: {e}")
        priority += 1

    if spinner:
        spinner.stop()
    click.echo(f"Successfully created Security Group `{nsg.result().name}`")


def create_storage_account(storage_client, cluster_name, resource_group_name, params, spinner):
    from azure.core.exceptions import HttpResponseError
    from azure.mgmt.storage.v2019_06_01.models import StorageAccountCheckNameAvailabilityParameters

    """Creates a Storage Account and returns Storage Client, Storage Account"""

    cluster_utils.echo_delimiter()
    default_name = "".join(filter(str.isalnum, f"spell{cluster_name[:13].lower()}storage"))
    storage_account_name = click.prompt(
        "Please enter a name for the Azure Storage Account Spell will create to store run outputs.\n"
        "NOTE: Storage account names must be between 3 and 24 characters in length and may only contain "
        "numbers and lowercase letters.\nYour storage account name must be UNIQUE within Azure. "
        "No two storage accounts can have the same name.",
        default=default_name,
    ).strip()
    if spinner:
        spinner.text = "Validating name..."
        spinner.start()
    account_name = StorageAccountCheckNameAvailabilityParameters(name=storage_account_name)
    # Built in Azure Storage Account name validator
    availability = storage_client.storage_accounts.check_name_availability(account_name)
    if not availability.name_available:
        click.echo(f"Azure does not support this name for the following reason: {availability.reason}")
        if spinner:
            spinner.stop()
        return create_storage_account(storage_client, cluster_name, resource_group_name, params, spinner)

    # Create Storage Account
    try:
        if spinner:
            spinner.text = f"Creating Storage Account `{storage_account_name}`"
        storage_async_operation = storage_client.storage_accounts.begin_create(
            resource_group_name,
            storage_account_name,
            params,
        )
        storage_account = storage_async_operation.result()
    except HttpResponseError as e:
        if spinner:
            spinner.stop()
        click.echo(f"Unable to create storage account. Azure error: {e}", err=True)
        return create_storage_account(storage_client, cluster_name, resource_group_name, params, spinner)

    if spinner:
        spinner.stop()
    click.echo(
        f"Successfully created Storage Account `{storage_account_name}` under resource group `{resource_group_name}`"
    )
    return storage_account, storage_account_name


def create_blob_container(storage_account_name, blob_service_client, spinner):
    """Creates a Blob Container and returns the Container Client"""
    if spinner:
        spinner.text = "Creating Blob Container..."
        spinner.start()
    else:
        click.echo("Creating Blob Container...")

    for i in range(3):
        try:
            blob_service_client.create_container(storage_account_name)
            if spinner:
                spinner.stop()
            click.echo(f"Created your new blob container `{storage_account_name}`!")
            return
        except Exception as e:
            click.echo(f"Unable to create blob container. Azure error: {e}", err=True)

    if spinner:
        spinner.stop()
    raise ExitException("Could not create blob container after three retries.")


def delete_azure_cluster(ctx, cluster):
    """
    Deletes an Azure cluster, including the Spell Cluster, Machine Types,
    Security Principal, Resource Group, Vnet, Storage Accounts, and Roles associated with this cluster.
    """

    spell_client = ctx.obj["client"]
    cluster_utils.validate_org_perms(spell_client, ctx.obj["owner"])

    try:
        from azure.graphrbac import GraphRbacManagementClient
        from azure.mgmt.resource import ResourceManagementClient
        from spell.cli.utils.azure_credential_wrapper import AzureIdentityCredentialAdapter
        from azure.core.exceptions import ClientAuthenticationError
        from azure.identity import DefaultAzureCredential

    except ImportError:
        click.echo("Please `pip install --upgrade 'spell[cluster-azure]'` and rerun this command")
        return

    click.echo(
        "This command will delete the Spell Cluster, Machine Types, Service Principal, "
        "VNet, Custom Role, Resource Group, and Storage Account associated with this cluster. "
    )
    if not click.confirm(f"Are you SURE you want to delete the spell cluster {cluster['name']}?"):
        return
    # Create Credentials
    try:
        credentials = DefaultAzureCredential(
            exclude_environment_credential=True,
            exclude_managed_identity_credential=True,
            exclude_visual_studio_code_credential=True,
            exclude_shared_token_cache_credential=True,
        )
        management_cred = AzureIdentityCredentialAdapter()
        management_cred.set_token()
        graph_rbac_creds = AzureIdentityCredentialAdapter(resource_id="https://graph.windows.net/")
        graph_rbac_creds.set_token()
    except ClientAuthenticationError:
        # NOTE: Default Azure Credential raises its own error
        raise ExitException("Please try again after logging into azure in your terminal")

    if ctx.obj["interactive"]:
        spinner = Halo(spinner=get_star_spinner_frames(ctx.obj["utf8"]))

    # Delete Machine Types and Model Servers on cluster first
    cluster_utils.echo_delimiter()
    with api_client_exception_handler():
        click.echo("Sending message to Spell to remove all Machine Types " f"from the cluster {cluster['name']}...")
        spell_client.delete_cluster_contents(cluster["name"])

    # Block until cluster is drained. This is necessary because the API will fail to
    # drain if we delete the IAM role before the machine types are marked as drained
    cluster_utils.block_until_cluster_drained(spell_client, cluster["name"], spinner)

    subscription_id = cluster["role_credentials"]["azure"]["subscription_id"]
    tenant_id = cluster["role_credentials"]["azure"]["tenant_id"]
    resource_client = ResourceManagementClient(credentials, subscription_id)
    rg_name = cluster["networking"]["azure"]["resource_group_name"]

    # Delete Resource group and everything in it
    cluster_utils.echo_delimiter()
    if not click.confirm(
        "WARNING: All the stored run outputs and uploads will be deleted with this command, as they are within "
        "the cluster's resource group. If you would like to save this data, please copy it to a different storage "
        "account in a different resource group before re-running this command. Continue?"
    ):
        return
    if spinner:
        spinner.text = f"Deleting Resource Group `{rg_name}`... "
        spinner.start()
    else:
        click.echo(f"Deleting Resource Group `{rg_name}`... ")
    try:
        delete_async_operation = resource_client.resource_groups.begin_delete(rg_name)
        delete_async_operation.wait()
        if spinner:
            spinner.stop()
        click.echo(f"Resource Group `{rg_name}` deleted")
    except Exception:
        click.echo(f"Failed to delete RG `{rg_name}`. Please delete it manually in the Azure console.")

    # Delete App/SP
    cluster_utils.echo_delimiter()
    if spinner:
        spinner.text = "Deleting App and Service Principal... "
        spinner.start()
    else:
        click.echo("Deleting App and Service Principal... ")
    try:
        client = GraphRbacManagementClient(graph_rbac_creds, tenant_id)
        client.service_principals.delete(cluster["role_credentials"]["azure"]["sp_object_id"])
        client.applications.delete(cluster["role_credentials"]["azure"]["app_object_id"])
        if spinner:
            spinner.stop()
        click.echo("Deleted App and Service Principal")
    except Exception:
        click.echo(
            "Failed to delete Spell Application/Service Principal. Please delete it manually in the Azure console."
        )
    # Last step is to mark the cluster as deleted
    cluster_utils.echo_delimiter()
    click.echo("Deleting cluster on Spell...")
    with api_client_exception_handler():
        spell_client.delete_cluster(cluster["name"])
        click.echo("Successfully deleted cluster on Spell")


def add_az_bucket(spell_client, cluster, account_name):
    """
    This command adds a cloud storage bucket to SpellFS, which enables interaction with the bucket objects
    via ls, cp, and mounts.

    NOTE: This command uses your Azure credentials - you will need to set the proper AD Admin Role on the portal
    """
    from azure.core.exceptions import ClientAuthenticationError
    from azure.identity import DefaultAzureCredential
    from azure.mgmt.storage import StorageManagementClient
    from azure.mgmt.resource.subscriptions import SubscriptionClient
    from azure.storage.blob import BlobServiceClient

    # Create Credentials
    try:
        credentials = DefaultAzureCredential(
            exclude_environment_credential=True,
            exclude_managed_identity_credential=True,
            exclude_visual_studio_code_credential=True,
            exclude_shared_token_cache_credential=True,
        )
    except ClientAuthenticationError:
        # NOTE: Default Azure Credential raises its own error
        raise ExitException("Please try again after logging into azure in your terminal")

    cluster_name = cluster["name"]
    subscription_client = SubscriptionClient(credentials)
    subscription_id = get_subscription(subscription_client)

    click.echo(
        """This command will
    - List your storage accounts to generate an options menu of storage accounts thatcan be added to Spell
    - Get the storage account access key so Spell can access your storage account"""
    )
    # Get storage client
    storage_client = StorageManagementClient(credentials, subscription_id)

    # Get storage account name
    click.echo(f"Available storage accounts in subscription {subscription_id}")
    account_names = {}
    for account in storage_client.storage_accounts.list():
        account_names[account.name] = account.id
    if account_name is None:
        for account in account_names.keys():
            click.echo(f"- {account}")
        account_name = click.prompt(
            "Please choose a storage account",
            type=click.Choice(account_names),
            show_choices=False,
        )
    # Get resource group from storage account id
    rg_name = get_rg_from_sa_id(account_names[account_name])
    # Get storage key
    list_keys = storage_client.storage_accounts.list_keys(rg_name, account_name)
    storage_keys = {v.key_name: v.value for v in list_keys.keys}
    storage_key = storage_keys["key1"]

    blob_service_client = BlobServiceClient.from_connection_string(get_connection_string(account_name, storage_key))
    # Get all containers
    click.echo(f"\nAvailable blob containers in storage account {account_name}")
    container_names = [container.name for container in blob_service_client.list_containers()]
    # Prompt for container name
    for container in container_names:
        click.echo("- {}".format(container))
    container_name = click.prompt(
        "Please choose a container",
        type=click.Choice(container_names),
        show_choices=False,
    )
    bucket_name = account_name + "_" + container_name

    # Register new bucket to cluster in API
    with api_client_exception_handler():
        spell_client.add_bucket(bucket_name, cluster_name, "azblob", storage_key)
    click.echo(
        f"Blob container {container_name} from storage account {account_name} has been added to cluster {cluster_name}!"
    )


def get_rg_from_sa_id(id):
    """
    This helper parses the resource group name from the storage account id

    Storage Account ids are of the form '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/
        providers/{resourceProviderNamespace}/{resourceType}/{resourceName}.'
    """
    result = re.findall("resourceGroups/(.*?)/providers/", id)
    if len(result) > 1:
        return ExitException("Unexpected parsing")
    else:
        return result[0]


def get_connection_string(storage_account_name, storage_key):
    """
    This helper creates a connection string from the storage account name and storage key which can
    be used to authenticate a Blob Service Client (needed to list containers)
    """
    connection_str = (
        "DefaultEndpointsProtocol=https;"
        + f"AccountName={storage_account_name};"
        + f"AccountKey={storage_key};"
        + "EndpointSuffix=core.windows.net"
    )
    return connection_str


def rotate_az_storage_key(ctx, cluster):
    """This command rotates the storage key for the customer's storage account"""
    from azure.core.exceptions import ClientAuthenticationError
    from azure.identity import DefaultAzureCredential
    from azure.mgmt.storage import StorageManagementClient

    # Create Credentials
    try:
        credentials = DefaultAzureCredential(
            exclude_environment_credential=True,
            exclude_managed_identity_credential=True,
            exclude_visual_studio_code_credential=True,
            exclude_shared_token_cache_credential=True,
        )
    except ClientAuthenticationError:
        # NOTE: Default Azure Credential raises its own error
        raise ExitException("Please try again after logging into azure in your terminal")
    click.echo("""This command will let you rotate your storage keys for your Storage Accounts""")
    spell_client = ctx.obj["client"]
    subscription_id = cluster["role_credentials"]["azure"]["subscription_id"]
    primary_bucket = cluster["storage_uri"]
    storage_client = StorageManagementClient(credentials, subscription_id)
    added_buckets = get_added_buckets(spell_client)
    if len(added_buckets) == 0:
        # Don't have added buckets - assume they want to rotate cluster storage account
        rotate_cluster_storage_key(cluster, spell_client, storage_client)
    else:
        added_buckets.append(primary_bucket)
        bucket_name = click.prompt(
            "Enter the name of the bucket_name whose keys you would like to rotate"
            f"\n({cluster['storage_uri']} is your primary bucket)",
            type=click.Choice(added_buckets),
            show_choices=True,
        )
        if bucket_name == primary_bucket:
            rotate_cluster_storage_key(cluster, spell_client, storage_client)
        else:
            account_name = bucket_name.split("_")[0]
            for account in storage_client.storage_accounts.list():
                if account.name == account_name:
                    account_id = account.id
                    break
            if account_id is None:
                raise ExitException(f"Unexpectedly could not find storage account {account_name}")
            # Get resource group from storage account id
            rg_name = get_rg_from_sa_id(account_id)
            key_rotate, new_storage_key = change_storage_keys(storage_client, rg_name, account_name)
            # Rotate added storage account keys
            with api_client_exception_handler():
                spell_client.azure_rotate_storage_key(cluster["name"], new_storage_key, bucket_name)
            click.echo(
                f"Storage account {account_name} is updated to use new {key_rotate} for cluster {cluster['name']}!"
            )


def get_added_buckets(client):
    """Returns a list of the added buckets in the cluster"""
    added_buckets = []
    try:
        for line in client.get_ls("azblob"):
            if isinstance(line, models.Error):
                raise ExitException(line.status)
            else:
                added_buckets.append(line.path)
    except Exception as e:
        if e == "Unknown resource type azblob":
            return added_buckets
    return added_buckets


def change_storage_keys(storage_client, rg_name, account_name):
    # Get storage key
    list_keys = storage_client.storage_accounts.list_keys(rg_name, account_name)
    storage_keys = {v.key_name: v.value for v in list_keys.keys}
    key_rotate = click.prompt(
        "Enter 'key1' to use Key 1 or 'key2' to use Key 2?",
        type=click.Choice(["key1", "key2"]),
        show_choices=False,
    )
    new_storage_key = storage_keys[key_rotate]
    return key_rotate, new_storage_key


def rotate_cluster_storage_key(cluster, client, storage_client):
    account_name = cluster["storage_uri"]
    rg_name = cluster["networking"]["azure"]["resource_group_name"]
    key_rotate, new_storage_key = change_storage_keys(storage_client, rg_name, account_name)
    # Rotate cluster storage account keys
    with api_client_exception_handler():
        client.azure_rotate_storage_key(cluster["name"], new_storage_key)
    click.echo(f"Storage account {account_name} is updated to use new {key_rotate} for cluster {cluster['name']}!")


def add_az_registry(repo_name, cluster):
    """
    This command enables pulling docker images from Azure Container Registry.
    Read permissions for the resource group the registry is stored at will be added to
    the SP role associated with the cluster.

    """
    try:
        from azure.mgmt.authorization import AuthorizationManagementClient
        from azure.core.exceptions import ClientAuthenticationError, AzureError
        from spell.cli.utils.azure_credential_wrapper import AzureIdentityCredentialAdapter
    except ImportError:
        click.echo("Please `pip install --upgrade 'spell[cluster-azure]'` and rerun this command")
        return

    try:
        management_cred = AzureIdentityCredentialAdapter()
        management_cred.set_token()
    except ClientAuthenticationError:
        # NOTE: Default Azure Credential raises its own error
        raise ExitException("Please try again after logging into Azure in your terminal")
    except AzureError as e:
        # This handles an "az login expiration exception"
        raise ExitException(f"Unexpected Azure error: {e}")

    resource_group_name = click.prompt("Enter the name of the Resource Group you registry falls under")
    # If registry is in the Spell RG, we automatically have permissions
    if resource_group_name == cluster["networking"]["azure"]["resource_group_name"]:
        click.echo("This is the same resource group for your Spell resources, permissions already granted!")
        return

    subscription_id = cluster["role_credentials"]["azure"]["subscription_id"]
    authorization_client = AuthorizationManagementClient(management_cred, subscription_id)
    reg_scope = (
        f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}"
        f"/providers/Microsoft.ContainerRegistry/registries/{repo_name}"
    )
    sp_object_id = cluster["role_credentials"]["azure"]["sp_object_id"]

    assign_acr_roles(authorization_client, reg_scope, sp_object_id, subscription_id)
    return


def delete_az_registry(repo_name, cluster):
    """
    This command removes access to private Azure Container Registry.
    """
    resource_group_name = click.prompt("Enter the the name of the Resource Group you registry falls under")
    # If registry is in the Spell RG, we automatically have permissions
    if resource_group_name == cluster["networking"]["azure"]["resource_group_name"]:
        return
    try:
        from azure.mgmt.authorization import AuthorizationManagementClient
        from azure.core.exceptions import ClientAuthenticationError, AzureError
        from spell.cli.utils.azure_credential_wrapper import AzureIdentityCredentialAdapter
    except ImportError:
        click.echo("Please `pip install --upgrade 'spell[cluster-azure]'` and rerun this command")
        return

    try:
        management_cred = AzureIdentityCredentialAdapter()
        management_cred.set_token()
    except ClientAuthenticationError:
        # NOTE: Default Azure Credential raises its own error
        raise ExitException("Please try again after logging into Azure in your terminal")
    except AzureError as e:
        # This handles an "az login expiration exception"
        raise ExitException(f"Unexpected Azure error: {e}")

    subscription_id = cluster["role_credentials"]["azure"]["subscription_id"]
    authorization_client = AuthorizationManagementClient(management_cred, subscription_id)
    reg_scope = (
        f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}"
        f"/providers/Microsoft.ContainerRegistry/registries/{repo_name}"
    )

    delete_acr_roles(authorization_client, reg_scope)
    return
