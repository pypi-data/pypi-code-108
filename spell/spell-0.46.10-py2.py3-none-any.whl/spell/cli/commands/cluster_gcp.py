import json
from packaging import version
import os
import random
import subprocess
import warnings

import click

from spell.cli.constants import WORKER_OPEN_PORTS

from spell.cli.exceptions import (
    api_client_exception_handler,
    ExitException,
)
from spell.cli.log import logger
from spell.cli.utils import is_installed, cluster_utils
from spell.cli.utils.kube_cluster_templates import generate_gke_cluster_rbac_yaml
from spell.cli.utils.command import docs_option
from spell.configs.config_handler import default_config_dir

warnings.filterwarnings("ignore", "Your application has authenticated using end user credentials")

SPELL_SERVICE_ACCOUNT = "193976455398-compute@developer.gserviceaccount.com"
GKE_DEFAULT_NODEGROUP_TYPE = "n1-standard-2"  # Instance type of default GKE node groups

required_permissions = [
    "compute.disks.create",
    "compute.disks.delete",
    "compute.disks.get",
    "compute.disks.list",
    "compute.disks.resize",
    "compute.disks.setLabels",
    "compute.disks.use",
    "compute.globalOperations.get",
    "compute.instances.attachDisk",
    "compute.instances.create",
    "compute.instances.delete",
    "compute.instances.get",
    "compute.instances.list",
    "compute.instances.setLabels",
    "compute.instances.setMetadata",
    "compute.instances.setServiceAccount",
    "compute.subnetworks.use",
    "compute.subnetworks.useExternalIp",
    "compute.zoneOperations.get",
    "compute.zoneOperations.list",
    "compute.zones.list",
    "compute.regions.get",
    "container.nodes.list",
    "container.pods.list",
]

cluster_version = 12


@click.command(name="gcp", short_help="Sets up GCP VPC as a Spell cluster")
@click.pass_context
@click.option("-n", "--name", "name", help="Name used by Spell for you to identify this GCP cluster")
@docs_option("https://spell.ml/docs/gcp_ownvpc_setup/")
def create_gcp(ctx, name):
    """
    This command creates a Spell cluster within a GCP VPC of your choosing as an external Spell cluster.
    This will let your organization run runs in that VPC, so your data never leaves
    your VPC. You set an GCS bucket of your choosing for all run outputs to be written to.
    After this cluster is set up you will be able to select the types and number of machines
    you would like Spell to create in this cluster.

    NOTE: This command uses your GCP credentials, activated by running `gcloud auth application-default login`,
    to create the necessary GCP resources for Spell to access and manage those machines. Your GCP credentials will
    need permission to set up these resources.
    """

    # Verify the owner is the admin of an org and cluster name is valid
    spell_client = ctx.obj["client"]
    cluster_utils.validate_org_perms(spell_client, ctx.obj["owner"])
    with api_client_exception_handler():
        spell_client.validate_cluster_name(name)

    try:
        import google.oauth2
        import google.auth
        from googleapiclient import discovery
    except ImportError:
        click.echo("Please `pip install --upgrade 'spell[cluster-gcp]'` and rerun this command")
        return

    try:
        from google.cloud import storage
    except ImportError:
        click.echo("Please `pip install --upgrade 'spell[cluster-gcp]'` and rerun this command")
        return
    if version.parse(storage.__version__) < version.parse("1.18.0"):
        click.echo(
            "Please `pip install --upgrade 'spell[cluster-gcp]'` to include HMAC functionality."
            " Your version is {}, whereas 1.18.0 is required as a minimum".format(storage.__version__)
        )
        return

    if not is_installed("gcloud"):
        raise ExitException(
            "`gcloud` is required, please install it before proceeding. "
            "See https://cloud.google.com/pubsub/docs/quickstart-cli"
        )

    try:
        credentials, project_id = google.auth.default()
    except google.auth.exceptions.DefaultCredentialsError:
        click.echo(
            """Please run `gcloud auth application-default login` to allow Spell
        to use your user credentials to set up a cluster, and rerun this command"""
        )
        return

    compute_service = discovery.build("compute", "v1", credentials=credentials)
    iam_service = discovery.build("iam", "v1", credentials=credentials)
    resource_service = discovery.build("cloudresourcemanager", "v1", credentials=credentials)

    click.echo(
        """This command will help you
    - Set up a Google Storage bucket to store your run outputs in
    - Setup a VPC network which Spell will spin up workers in to run your jobs
    - Create a subnet in the VPC
    - Setup a Service Account allowing Spell to spin up and down machines and access the GS bucket"""
    )

    if name is None:
        name = click.prompt("Enter a display name for this cluster within Spell")

    # Normalize the name here
    name = name.replace("_", "-").lower()
    project_id = get_project(resource_service, project_id)
    region = get_region(compute_service, project_id)

    supports_no_gpu = region in (
        "asia-east2",
        "asia-northeast1",
        "asia-northeast2",
        "asia-south1",
        "asia-southeast1",
        "europe-north1",
        "europe-west2",
        "europe-west3",
        "europe-west6",
        "northamerica-northeast1",
        "southamerica-east1",
        "us-east4",
        "us-west2",
    )

    supports_no_V100 = region in (
        "us-east1",
        "europe-west1",
    )

    supports_no_K80 = region in ("europe-west4",)

    supports_no_K80V100 = region in ("australia-southeast1",)

    if supports_no_gpu:
        if not click.confirm(
            "GCP does not support ANY GPU types in {}. You can still create a cluster, but it will"
            " only have access to CPU types - continue?".format(region)
        ):
            return
    elif supports_no_K80V100:
        if not click.confirm(
            "GCP does not support V100 and K80 GPU types in {}. You can still create a cluster, "
            "but it will not have access to V100 and K80 GPU types - continue?".format(region)
        ):
            return
    elif supports_no_V100:
        if not click.confirm(
            "GCP does not support V100 GPU types in {}. You can still create a cluster, but it"
            " will not have access to V100 GPU types - continue?".format(region)
        ):
            return

    elif supports_no_K80:
        if not click.confirm(
            "GCP does not support K80 GPU types in {}. You can still create a cluster, but it will"
            " not have access to K80 GPU types - continue?".format(region)
        ):
            return

    service_account = get_service_account(iam_service, resource_service, project_id)
    if service_account is None:
        return

    # creates a new bucket and endows the service account with permissions.
    bucket_name = get_bucket_with_permissions(ctx, storage, service_account, name, project_id)
    if bucket_name is None:
        return

    network_name, subnet_name = create_vpc(compute_service, name, project_id, region, spell_client)

    gs_hmac_key_id, gs_hmac_access_key = get_interoperable_s3_access_keys(storage, project_id, service_account["email"])

    gs_service_acct_api_key = create_api_key(iam_service, service_account["email"])

    with api_client_exception_handler():
        cluster = spell_client.create_gcp_cluster(
            name,
            service_account["email"],
            bucket_name,
            network_name,
            subnet_name,
            region,
            project_id,
            gs_hmac_key_id,
            gs_hmac_access_key,
            gs_service_acct_api_key,
        )
        cluster_utils.echo_delimiter()
        url = "{}/{}/clusters/{}".format(ctx.obj["web_url"], ctx.obj["owner"], cluster["name"])
        click.echo(
            "Your cluster {} is initialized! Head over to the web console to create machine types "
            "to execute your runs on - {}".format(name, url)
        )

    spell_client.update_cluster_version(cluster["name"], cluster_version)


def gke_update(ctx, credentials, cluster, gke_cluster_name, support_runs):
    from googleapiclient import discovery

    compute_service = discovery.build("compute", "v1", credentials=credentials)
    gcp_project_name = cluster["networking"]["gcp"]["project"]
    region = cluster["networking"]["gcp"]["region"]
    cluster_zone = cluster.get("serving_cluster_location")
    if not cluster_zone:  # TODO(waldo) Remove this after backfilling db
        cluster_zone = get_zone_from_region(compute_service, gcp_project_name, region)
    service_account = cluster["role_credentials"]["gcp"]["service_account_id"]

    if gke_cluster_name and not click.confirm("Are you sure you want to use {}?".format(gke_cluster_name)):
        raise ExitException("Please specify a different --kube-cluster-name")

    cmd = [
        "gcloud",
        "container",
        "clusters",
        "get-credentials",
        "--project",
        gcp_project_name,
        "--zone",
        cluster_zone,
        gke_cluster_name,
    ]
    subprocess.check_call(cmd)

    return gke_configure_k8s(
        ctx,
        service_account,
        cluster,
        cluster["is_serving_cluster_public"],
        support_runs,
    )


def add_gke_rbac(service_account):
    # This creates a Cluster Role Binding for the Spell service account on the user's GKE cluser
    try:
        # we delete the clusterrolebinding because the clusterrole that the clusterrolebinding binds to
        # can't be mutated after creation; to update the cluterrolebinding we need to delete and recreate it
        cluster_utils.kubectl("delete", "clusterrolebinding", "spell-api-access-binding", "--ignore-not-found")

        # this clusterrole no longer exists; we delete it here to clean up after ourselves on old clusters
        cluster_utils.kubectl("delete", "clusterrole", "spell-api-access", "--ignore-not-found")

        rbac_yaml = generate_gke_cluster_rbac_yaml(service_account)
        cluster_utils.kubectl_apply(rbac_yaml, kubectl_context=None)
        click.echo("RBAC permissions granted!")
    except Exception as e:
        raise ExitException(f"Giving Spell RBAC permissions failed. Error was: {e}")


def add_gke_gpu():
    """Add gpu driver support to user's GKE cluster"""
    subprocess.check_call(
        (
            "kubectl",
            "apply",
            "--filename",
            "https://raw.githubusercontent.com/GoogleCloudPlatform/"
            "container-engine-accelerators/master/"
            "nvidia-driver-installer/cos/daemonset-preloaded.yaml",
        )
    )
    click.echo("GPU support for GKE added!")


def gke_configure_k8s(ctx, service_account, cluster, is_public, support_runs=False):

    optional_features = cluster_utils.make_optional_serving_features(cluster)

    cluster_utils.create_namespace("serving")

    # Give Spell permissions to the cluster (via RBAC)
    cluster_utils.echo_delimiter()
    click.echo("Giving Spell RBAC permissions to GKE cluster...")
    add_gke_rbac(service_account)

    # Create the serving priorityclass
    cluster_utils.echo_delimiter()
    cluster_utils.create_serving_priorityclass()

    # Add Ambassador to the 'ambassador' namespace
    cluster_utils.add_ambassador(cluster, is_public)

    # Set up the GKE GPU Driver daemonset
    cluster_utils.echo_delimiter()
    click.echo("Setting up GPU support for GKE...")
    try:
        add_gke_gpu()
    except Exception as e:
        logger.error("Couldn't add GKE GPU driver Daemonset. Error was: {}".format(e))
        optional_features["gpu"] = False

    # Add kube-Prometheus to the monitoring stack.
    cluster_utils.add_monitoring_stack(cluster)

    cluster_utils.add_efk_stack(ctx, support_runs)

    return optional_features


def get_bucket_with_permissions(ctx, storage_api, service_account, cluster_name, project_id):
    storage_client = storage_api.Client(project=project_id)

    cluster_utils.echo_delimiter()
    response = click.prompt(
        "We recommend using an empty GS Bucket for Spell outputs. Would "
        "you like to make a new bucket or use an existing",
        type=click.Choice(["new", "existing"]),
    ).strip()
    if response == "new":
        bucket_name = click.prompt(
            "Please enter a name for the GS Bucket Spell will create for run outputs",
            default="spell-{}".format(cluster_name.replace("_", "-").lower()),
        ).strip()
        while not all([bucket_name[0].isalnum(), bucket_name[-1].isalnum()]):
            click.echo("GCP only allows bucket names that start and end with a number or letter")
            bucket_name = click.prompt(
                "Please enter a name for the GS Bucket Spell will create for run outputs"
            ).strip()
        bucket = storage_client.create_bucket(bucket_name)
        click.echo("Created your new bucket {}!".format(bucket_name))
    else:
        req = storage_client.list_buckets()
        buckets = [bucket.name for bucket in req]
        bucket_name = click.prompt("Enter existing bucket name", type=click.Choice(buckets))
    # set bucket permissions
    bucket = storage_client.bucket(bucket_name)
    policy = bucket.get_iam_policy()
    service_account_tag = "serviceAccount:{}".format(service_account["email"])
    role_name = "roles/storage.admin"
    for role, value in policy.items():
        if role == role_name and service_account_tag in value:
            return bucket_name
    if not policy.get(role_name):
        policy[role_name] = set()
    policy[role_name].add(service_account_tag)
    bucket.set_iam_policy(policy)
    return bucket_name


def get_region(compute_service, project):
    # Try fetching the default project region
    request = compute_service.projects().get(project=project)
    response = request.execute()

    items = response.get("commonInstanceMetadata", {}).get("items", [])
    region = None
    for item in items:
        if item.get("key") == "google-compute-default-region":
            region = item.get("value")
    if region is not None:
        if click.confirm(
            "All of this will be done within this project's region '{}' - continue?".format(region),
            default=True,
        ):
            return region
    request = compute_service.regions().list(project=project)
    regions = []
    while request is not None:
        response = request.execute()
        for region in response["items"]:
            regions.append(region["name"])
        request = compute_service.regions().list_next(previous_request=request, previous_response=response)
    return click.prompt(
        "Please choose a region for your cluster. This might affect machine availability",
        type=click.Choice(regions),
    )


def create_vpc(compute_service, cluster_name, project, region, spell_client):
    cluster_utils.echo_delimiter()

    # Create VPC
    network_body = {"name": cluster_name, "autoCreateSubnetworks": False}

    click.echo("Creating network...")
    req = compute_service.networks().insert(project=project, body=network_body)
    response = req.execute()
    global_progress_bar(project, compute_service, response)
    click.echo("Created a new VPC/network with name {}!".format(cluster_name))

    network_url = response["targetLink"]
    network_name = cluster_name
    cidr = "10.0.0.0/16"

    # Add firewall rules
    click.echo("Creating firewall rule to allow ingress on ports {}...".format(WORKER_OPEN_PORTS))
    trusted_cidrs = spell_client.get_trusted_cidrs()
    request = compute_service.firewalls().insert(
        project=project,
        body={
            "name": "{}-spell-api".format(cluster_name),
            "description": "Ingress from Spell API for ssh (22), docker (2376), and jupyter (9999) traffic",
            "network": network_url,
            "sourceRanges": trusted_cidrs,
            "allowed": [{"IPProtocol": "TCP", "ports": [str(port) for port in WORKER_OPEN_PORTS]}],
        },
    )
    response = request.execute()
    global_progress_bar(project, compute_service, response)

    click.echo("Creating firewall rule to allow communication between instances within VPC...")
    request = compute_service.firewalls().insert(
        project=project,
        body={
            "name": "{}-internal".format(cluster_name),
            "description": "Allow traffic between all instances within VPC",
            "network": network_url,
            "sourceRanges": [cidr],
            "allowed": [{"IPProtocol": "TCP"}, {"IPProtocol": "UDP"}],
        },
    )
    response = request.execute()
    global_progress_bar(project, compute_service, response)
    click.echo("Firewall rules ready!")

    # Create subnet
    subnetwork_body = {
        "name": cluster_name,
        "network": network_url,
        "ipCidrRange": cidr,
    }

    click.echo("Creating subnetwork...")
    request = compute_service.subnetworks().insert(project=project, body=subnetwork_body, region=region)
    response = request.execute()
    region_progress_bar(project, compute_service, response, region)
    subnet_name = cluster_name

    click.echo("Created a new subnet {} within network {} in region {}!".format(cluster_name, cluster_name, region))

    return network_name, subnet_name


def get_project(resource_service, project_id):
    cluster_utils.echo_delimiter()
    projects = resource_service.projects().list().execute()

    if project_id is None or not click.confirm(
        "All of this will be done within your project '{}' - continue?".format(project_id),
        default=True,
    ):
        return click.prompt(
            "Please choose a project id",
            type=click.Choice([p["projectId"] for p in projects["projects"]]),
        )
    return project_id


def get_zone_from_region(compute_service, project, region):
    request = compute_service.regions().get(project=project, region=region)
    region_self_link = request.execute()["selfLink"]

    request = compute_service.zones().list(project=project, filter='region = "{}"'.format(region_self_link))
    response = request.execute()
    if "items" not in response or len(response["items"]) == 0:
        raise ExitException("No compute zones found for region {}".format(region))
    return response["items"][0]["name"]


def get_interoperable_s3_access_keys(storage_api, project, service_account):
    storage_client = storage_api.Client(project=project)
    metadata, secret = storage_client.create_hmac_key(service_account)
    return metadata.access_id, secret


def create_api_key(iam_service, service_account_email):
    """Create a new api key for this service acct, if none exists. Return empty str if we've already created one."""
    existing_api_keys = (
        iam_service.projects()
        .serviceAccounts()
        .keys()
        .list(name="projects/-/serviceAccounts/{account_email}".format(account_email=service_account_email))
        .execute()
        .get("keys")
    )
    spell_api_key_exists = len([k for k in existing_api_keys if k.get("keyType") == "USER_MANAGED"]) > 0

    if spell_api_key_exists:
        return ""

    # NOTE: The python iam client doesn't return API keys in a nicely marshalled format, so just use the gcloud CLI
    spell_dir = os.environ.get("SPELL_DIR", default_config_dir())
    local_keyfile = os.path.join(spell_dir, ".cluster_api_key")
    gcloud_auth_cmd = "gcloud iam service-accounts keys create --iam-account {account_email} {keyfile}".format(
        account_email=service_account_email, keyfile=local_keyfile
    )
    subprocess.run(gcloud_auth_cmd, shell=True)
    with open(local_keyfile) as f:
        key_content = f.read()
    os.remove(local_keyfile)

    return key_content


def get_service_account(iam_service, resource_service, project):
    """Creates a new service account."""
    cluster_utils.echo_delimiter()
    suffix = str(random.randint(10 ** 6, 10 ** 7))
    service_account_name = "spell-access-{}".format(suffix)
    service_account = (
        iam_service.projects()
        .serviceAccounts()
        .create(
            name="projects/{}".format(project),
            body={
                "accountId": service_account_name,
                "serviceAccount": {"displayName": "spell-access"},
            },
        )
        .execute()
    )
    service_account_name = service_account["name"]
    service_account_email = service_account["email"]
    try:
        # Allow Spell service account to create keys for external service account
        policy = iam_service.projects().serviceAccounts().getIamPolicy(resource=service_account_name).execute()
        # Service account needs to have access to use itself to attach itself to an instance
        account_user_binding = {
            "role": "roles/iam.serviceAccountUser",
            "members": [
                "serviceAccount:{}".format(SPELL_SERVICE_ACCOUNT),
                "serviceAccount:{}".format(service_account_email),
            ],
        }
        token_create_binding = {
            "role": "roles/iam.serviceAccountTokenCreator",
            "members": ["serviceAccount:{}".format(SPELL_SERVICE_ACCOUNT)],
        }
        policy["bindings"] = [account_user_binding, token_create_binding]
        policy = (
            iam_service.projects()
            .serviceAccounts()
            .setIamPolicy(
                resource=service_account_name,
                body={"resource": service_account_name, "policy": policy},
            )
            .execute()
        )
    except Exception as e:
        raise ExitException("Unable to create and attach IAM policies. GCP error: {}".format(e))

    suffix = str(random.randint(10 ** 6, 10 ** 7))
    role_name = "SpellAccess_{}".format(suffix)

    create_role_request_body = {
        "roleId": role_name,
        "role": {"title": role_name, "includedPermissions": required_permissions},
    }

    click.echo(
        "Creating role {} with the following permissions: \n{} \n...".format(
            role_name, "\n".join("\t" + p for p in required_permissions)
        )
    )
    request = iam_service.projects().roles().create(parent="projects/{}".format(project), body=create_role_request_body)
    response = request.execute()
    role_id = response["name"]

    click.echo("Assigning role {} to service account {}...".format(role_name, service_account_email))
    request = resource_service.projects().getIamPolicy(resource=project, body={})
    response = request.execute()

    response["bindings"].append({"members": ["serviceAccount:{}".format(service_account_email)], "role": role_id})

    set_iam_policy_body = {"policy": response}

    request = resource_service.projects().setIamPolicy(resource=project, body=set_iam_policy_body)
    response = request.execute()

    click.echo("Successfully set up service account {}".format(service_account_email))
    return service_account


def create_gke_cluster(
    cluster_name,
    gcp_project_name,
    service_account_id,
    cluster_zone,
    nodes_min,
    nodes_max,
    node_disk_size,
    network,
    subnet,
):
    """
    Create a GKE cluster for model serving using your current
    `gcloud` credentials. You need to have both `kubectl` and `gcloud` installed.
    This command will install the necessary deployments and services to host
    model servers.
    """

    try:
        # NOTE(waldo): We pin the GKE K8s cluster version here. 1.16+ is necessary for Prometheus.
        cmd = [
            "gcloud",
            "container",
            "clusters",
            "create",
            cluster_name,
            "--project",
            gcp_project_name,
            "--zone",
            cluster_zone,
            "--addons=HorizontalPodAutoscaling",
            "--enable-autoscaling",
            "--enable-ip-alias",
            "--machine-type",
            GKE_DEFAULT_NODEGROUP_TYPE,
            "--num-nodes",
            "1",
            "--min-nodes",
            str(nodes_min),
            "--max-nodes",
            str(nodes_max),
            "--service-account",
            service_account_id,
            "--disk-size",
            str(node_disk_size),
            "--no-enable-autoupgrade",
            "--labels=spell=model_serving",
            "--no-enable-basic-auth",
            "--release-channel=stable",
            "--network",
            network,
            "--subnetwork",
            subnet,
        ]
        click.echo("Creating the cluster. This can take a while...")
        subprocess.check_call(cmd)
        click.echo("Cluster created!")

        click.echo("Giving current gcloud user cluster-admin...")
        cmd = ["gcloud", "config", "list", "account", "--format", "value(core.account)"]
        gcloud_user = subprocess.check_output(cmd).decode("utf-8").strip()
        cmd = [
            "kubectl",
            "create",
            "clusterrolebinding",
            "cluster-admin-binding",
            "--clusterrole",
            "cluster-admin",
            "--user",
            gcloud_user,
        ]
        subprocess.check_call(cmd)
        click.echo("Current gcloud user {} granted cluster-admin".format(gcloud_user))

    except subprocess.CalledProcessError:
        raise ExitException(
            "Failed to run `gcloud`. Make sure it's installed correctly and "
            "your inputs are valid. Error details are above in the `gcloud` output."
        )


def gke_scale_nodepool(credentials, node_group, min_nodes, max_nodes):
    from googleapiclient import discovery
    from googleapiclient.errors import HttpError

    service = discovery.build("container", "v1", credentials=credentials).projects().locations().clusters().nodePools()

    config = json.loads(node_group.config)
    name_path = "{}/nodePools/{}".format(config["parent"], node_group.name)

    if node_group.min_nodes is None:
        node_group.min_nodes = 0
    if node_group.max_nodes is None:
        node_group.max_nodes = 2

    new_min_nodes = min_nodes if min_nodes is not None else node_group.min_nodes
    new_max_nodes = max_nodes if max_nodes is not None else node_group.max_nodes
    autoscaling_cfg = {
        "autoscaling": {
            "enabled": True,
            "minNodeCount": new_min_nodes,
            "maxNodeCount": new_max_nodes,
        },
    }
    request = service.setAutoscaling(name=name_path, body=autoscaling_cfg)
    click.echo("Updating autoscaling...")
    try:
        request.execute()
    except HttpError as e:
        err = json.loads(e.content)["error"]
        raise ExitException(err["message"])
    except Exception as e:
        raise ExitException("Error scaling node pool: {}".format(str(e)))

    # Set the initial node count
    # Note that GCP doesn't automatically scale the node numbers to be between
    # the minimum and maximum node counts if the current count is outside of
    # the range. This operation manually adjusts the node counts to conform
    # https://cloud.google.com/kubernetes-engine/docs/concepts/cluster-autoscaler#minimum_and_maximum_node_pool_size
    request = service.get(name=name_path)
    click.echo("Checking current size of node pool...")
    try:
        resp = request.execute()
    except HttpError as e:
        err = json.loads(e.content)["error"]
        raise ExitException(err["message"])
    except Exception as e:
        raise ExitException("Error retrieving node pool: {}".format(str(e)))
    curr_nodes = resp.get("initialNodeCount", 0)

    resize_body = None
    if curr_nodes < new_min_nodes:
        click.echo(
            "Current node count {} is below the new minimum {}, resizing...".format(
                curr_nodes,
                new_min_nodes,
            )
        )
        resize_body = {"nodeCount": new_min_nodes}
    elif curr_nodes > new_max_nodes:
        click.echo(
            "Current node count {} is above the new maximum {}, resizing...".format(
                curr_nodes,
                new_max_nodes,
            )
        )
        resize_body = {"nodeCount": new_max_nodes}
    if resize_body is not None:
        request = service.setSize(name=name_path, body=resize_body)
        try:
            request.execute()
        except HttpError as e:
            err = json.loads(e.content)["error"]
            raise ExitException(err["message"])
        except Exception as e:
            raise ExitException("Error adjusting node pool size: {}".format(str(e)))


def gke_delete_nodepool(credentials, node_group):
    from googleapiclient import discovery
    from googleapiclient.errors import HttpError

    service = discovery.build("container", "v1", credentials=credentials).projects().locations().clusters().nodePools()

    config = json.loads(node_group.config)
    name_path = "{}/nodePools/{}".format(config["parent"], node_group.name)
    request = service.delete(name=name_path)
    click.echo("Deleting...")
    try:
        request.execute()
    except HttpError as e:
        err = json.loads(e.content)["error"]
        raise ExitException(err["message"])
    except Exception as e:
        raise ExitException("Error deleting node pool: {}".format(str(e)))


def gke_add_nodepool(node_group_name, config_contents, gcp_service_account, gcp_creds):
    from googleapiclient import discovery
    from googleapiclient.errors import HttpError

    service = discovery.build("container", "v1", credentials=gcp_creds).projects().locations().clusters().nodePools()

    config = json.loads(config_contents)

    # Apply spell_serving_group label to config
    if "labels" not in config["nodePool"]["config"].keys():
        config["nodePool"]["config"]["labels"] = {}
    config["nodePool"]["config"]["labels"]["spell_serving_group"] = node_group_name

    # Scopes used by the cluster service account. These are defaults in the gcloud CLI equivalent,
    # but must be explicitly passed in to the API
    config["nodePool"]["config"]["oauthScopes"] = [
        "https://www.googleapis.com/auth/cloud-platform",
        "https://www.googleapis.com/auth/userinfo.email",
    ]
    config["nodePool"]["config"]["serviceAccount"] = gcp_service_account

    parent = config["parent"]
    request = service.create(parent=parent, body=config)
    click.echo("Creating node pool...")
    try:
        request.execute()
    except HttpError as e:
        err = json.loads(e.content)["error"]
        raise ExitException(err["message"])
    except Exception as e:
        raise ExitException("Error creating node pool: {}".format(str(e)))


def is_gs_bucket_public(bucket_name):
    """
    This command checks if a gs bucket is accessible without credentials - i.e. if the bucket is public.
    """
    import requests

    PERMISSIONS = ["storage.objects.get", "storage.objects.list"]
    # appropriated from https://github.com/RhinoSecurityLabs/GCPBucketBrute/blob/master/gcpbucketbrute.py#L186
    query_str = "&".join("permissions={}".format(p) for p in PERMISSIONS)
    requestURI = "https://www.googleapis.com/storage/v1/b/{}/iam/testPermissions?{}"
    unauthenticated_permissions = requests.get(requestURI.format(bucket_name, query_str)).json()
    permissions = unauthenticated_permissions.get("permissions", [])
    if len(permissions) == len(PERMISSIONS):
        return True
    return False


@click.pass_context
def get_container_registry_bucket_name(ctx, storage_service):
    """
    Get a list of gs image buckets for this google cloud project.

    Google's container registry service supports image buckets for multiple multi-regions.
    See https://cloud.google.com/container-registry/docs/pushing-and-pulling#pushing_an_image_to_a_registry

    Args:
        storage_service: an instance of google.cloud.storage.client.Client
    """
    try:
        from google.api_core.exceptions import NotFound
    except ImportError:
        click.echo("Please `pip install --upgrade 'spell[cluster-gcp]'` and rerun this command")
        return

    multi_region_prefixes = ["", "us.", "eu.", "asia."]
    buckets = []
    for prefix in multi_region_prefixes:
        bucket_url = "{}artifacts.{}.appspot.com".format(prefix, storage_service.project)
        try:
            buckets.append(storage_service.get_bucket(bucket_url))
        except NotFound:
            continue

    if len(buckets) == 0:
        click.echo("Couldn't find any container registries for your Google project.")
        return
    elif len(buckets) == 1:
        bucket_number = 0
    else:
        click.echo(
            "Spell found multiple container registries associated with your Google project:\n"
            + "\n".join(["{} : {}".format(i, b.location) for i, b in enumerate(buckets)])
        )
        bucket_number = click.prompt(
            "Enter the number for the registry which you would like to select",
            type=click.IntRange(0, len(buckets) - 1),
            default=0,
        )

    return buckets[bucket_number].name


def check_import_and_authenticate():
    try:
        import google.oauth2
        import google.auth
    except ImportError:
        click.echo("Please `pip install --upgrade 'spell[cluster-gcp]'` and rerun this command")
        return False

    try:
        google.auth.default()
    except google.auth.exceptions.DefaultCredentialsError:
        click.echo(
            """Please run `gcloud auth application-default login` to allow Spell
        to use your user credentials to set up a cluster, and rerun this command"""
        )
        return False
    return True


def add_gs_bucket(spell_client, cluster, bucket_name):
    """
    This command adds a cloud storage bucket to SpellFS, which enables interaction with the bucket objects
    via ls, cp, and mounts. It will also add bucket read permissions to the IAM role associated with the
    cluster.

    NOTE: This command uses your GCP credentials, configued through `gcloud auth application-default login`
    Your GCP credentials will need permission to setup these resources.
    """
    from google.cloud import storage

    cluster_name = cluster["name"]
    project_id = cluster["networking"]["gcp"]["project"]
    storage_service = storage.Client(project=project_id)

    click.echo(
        """This command will
    - List your buckets to generate an options menu of buckets that can be added to Spell
    - Add list and read permissions for that bucket to the service account associated with the cluster
    - Ensure that the service account is able to read this bucket."""
    )

    # Get all buckets
    bucket_names = [bucket.name for bucket in storage_service.list_buckets()]

    # Prompt for bucket name
    if bucket_name is None:
        for bucket in bucket_names:
            click.echo("- {}".format(bucket))
        bucket_name = click.prompt("Please choose a bucket")

    # Check if bucket is public if the bucket name is not one of the returned
    bucket_is_public = False
    if bucket_name not in bucket_names:
        b = storage_service.lookup_bucket(bucket_name)
        if b is None or not b.exists():
            raise ExitException("Bucket {} doesn't exist.".format(bucket_name))

        if not is_gs_bucket_public(bucket_name):
            raise ExitException(
                "Bucket {} is neither publicly accessible nor " "part of project {}.".format(bucket_name, project_id)
            )
        bucket_is_public = True

    # Skip IAM role management logic if bucket is public
    if bucket_is_public:
        click.echo("Bucket {} is public, no IAM updates required.".format(bucket_name))
        with api_client_exception_handler():
            spell_client.add_bucket(bucket_name, cluster["name"], "gs")
        click.echo("Bucket {} has been added to cluster {}!".format(bucket_name, cluster_name))
        return

    bucket = storage_service.lookup_bucket(bucket_name)
    # Add bucket read permissions to policy
    policy = bucket.get_iam_policy()
    service_account_email = cluster["role_credentials"]["gcp"]["service_account_id"]
    service_account_tag = "serviceAccount:{}".format(service_account_email)
    role_name = "roles/storage.objectViewer"
    if not policy.get(role_name):
        policy[role_name] = set()
    policy[role_name].add(service_account_tag)
    bucket.set_iam_policy(policy)

    # Register new bucket to cluster in API
    with api_client_exception_handler():
        spell_client.add_bucket(bucket_name, cluster_name, "gs")
    click.echo("Bucket {} has been added to cluster {}!".format(bucket_name, cluster_name))


def remove_gs_bucket(spell_client, cluster, bucket_name):
    """
    This command removes a GS cloud storage bucket from SpellFS.
    It will also remove bucket read permissions from the IAM role associated with the cluster.

    NOTE: This command uses your GCP credentials, configued through `gcloud auth application-default login`
    Your GCP credentials will need permission to setup these resources.
    """
    from google.cloud import storage

    cluster_name = cluster["name"]
    project_id = cluster["networking"]["gcp"]["project"]
    storage_service = storage.Client(project=project_id)

    # List existing buckets for cluster, and prompt for bucket_name if necessary
    with api_client_exception_handler():
        existing_buckets = spell_client.list_buckets(cluster_name)

    if len(existing_buckets) == 0:
        raise ExitException(f"Cluster {cluster_name} has no buckets to remove")

    existing_bucket_names = [b.name for b in existing_buckets]
    if bucket_name is None:
        click.echo(f"Found {len(existing_buckets)} exiting bucket(s):")
        for bn in existing_bucket_names:
            click.echo("- {}".format(bn))
        bucket_name = click.prompt("Please choose a bucket to remove", type=click.Choice(existing_bucket_names))
    if bucket_name not in existing_bucket_names:
        raise ExitException(f"Bucket name {bucket_name} has not been added to cluster {cluster_name}")

    # Check if bucket is public if the bucket name is not one of the returned
    all_gs_buckets = [bucket.name for bucket in storage_service.list_buckets()]
    if bucket_name not in all_gs_buckets:
        # Either the Bucket is public or not accessible, either way we treat it as public
        # and IAM role management logic
        click.echo(f"Bucket {bucket_name} is either public or inaccessible, no IAM updates required.")
        with api_client_exception_handler():
            spell_client.remove_bucket(bucket_name, cluster_name, "gs")
        click.echo(f"Bucket {bucket_name} has been removed from cluster {cluster_name}!")
        return

    # Remove Service Account read permissions from bucket policy
    bucket = storage_service.lookup_bucket(bucket_name)
    policy = bucket.get_iam_policy()
    service_account_email = cluster["role_credentials"]["gcp"]["service_account_id"]
    service_account_tag = "serviceAccount:{}".format(service_account_email)
    role_name = "roles/storage.objectViewer"
    if policy.get(role_name) and service_account_tag in policy[role_name]:
        policy[role_name].remove(service_account_tag)
    else:
        click.echo(
            f"Could not find Service Account {service_account_tag} in bucket policy. "
            "This may mean it's already been removed, or the policy was updated elsewhere."
        )
    bucket.set_iam_policy(policy)

    # Remove bucket from cluster in API
    with api_client_exception_handler():
        spell_client.remove_bucket(bucket_name, cluster_name, "gs")
    click.echo(f"Bucket {bucket_name} has been removed from cluster {cluster_name}!")


def set_custom_instance_service_acct(spell_client, cluster, custom_instance_service_acct):
    if custom_instance_service_acct:
        try:
            import google.auth
            from googleapiclient import discovery
        except ImportError:
            click.echo("Please `pip install --upgrade 'spell[cluster-gcp]'` and rerun this command")
            return
        try:
            credentials, project_id = google.auth.default()
        except google.auth.exceptions.DefaultCredentialsError:
            click.echo(
                """Please run `gcloud auth application-default login` to allow Spell
            to use your user credentials to ensure the correct configuration of the input
            custom instance service account, and then rerun this command"""
            )
            return

        # Allow Spell cluster service acct to create instances with input service acct
        iam_service = discovery.build("iam", "v1", credentials=credentials)
        try:
            custom_instance_svc_acct_resource = "projects/{}/serviceAccounts/{}".format(
                cluster["networking"]["gcp"]["project"],
                custom_instance_service_acct,
            )
            # First query existing policy for input service account
            policy = (
                iam_service.projects()
                .serviceAccounts()
                .getIamPolicy(resource=custom_instance_svc_acct_resource)
                .execute()
            )
            account_user_binding = None
            if "bindings" not in policy:
                policy["bindings"] = []
            for binding in policy["bindings"]:
                if binding["role"] == "roles/iam.serviceAccountUser":
                    account_user_binding = binding
                    break

            # See if we need to update the policy by looking for the role/member binding
            needs_updating = True
            cluster_svc_acct_prefixed = "serviceAccount:{}".format(
                cluster["role_credentials"]["gcp"]["service_account_id"]
            )
            if account_user_binding is None:
                account_user_binding = {
                    "role": "roles/iam.serviceAccountUser",
                    "members": [cluster_svc_acct_prefixed],
                }
                policy["bindings"].append(account_user_binding)
            else:
                for member in account_user_binding["members"]:
                    if member == cluster_svc_acct_prefixed:
                        needs_updating = False
                        break
                if needs_updating:
                    account_user_binding["members"].append(cluster_svc_acct_prefixed)

            # Update the input service account with the role/member binding if necessary
            if needs_updating:
                iam_service.projects().serviceAccounts().setIamPolicy(
                    resource=custom_instance_svc_acct_resource,
                    body={"resource": custom_instance_svc_acct_resource, "policy": policy},
                ).execute()

        except Exception as e:
            raise ExitException("Unable to create and attach IAM policies. GCP error: {}".format(e))

    # Register new custom instance svc acct to cluster in API
    cluster_name = cluster["name"]
    with api_client_exception_handler():
        spell_client.set_instance_role_identifier(custom_instance_service_acct, cluster_name)
    if custom_instance_service_acct:
        click.echo(
            "Instance Service Account {} has been set for cluster {}!".format(
                custom_instance_service_acct, cluster_name
            )
        )
    else:
        click.echo("Instance Service Account has been UNSET from cluster {}!".format(cluster_name))


@click.pass_context
def add_gc_registry(ctx, cluster):
    """
    This command enables pulling docker images from Google Container Registry.
    Read permissions for the bucket the registry is stored at will be added to
    the IAM role associated with the cluster.

    NOTE: This command uses your GCP credentials, configued through `gcloud auth application-default login`
    Your GCP credentials will need permission to setup these resources.
    """
    if not check_import_and_authenticate():
        return
    project_id = cluster["networking"]["gcp"]["project"]
    try:
        from google.cloud import storage
    except ImportError:
        click.echo("Please `pip install --upgrade 'spell[cluster-gcp]'` and rerun this command")
        return
    storage_service = storage.Client(project=project_id)
    registry_bucket_name = get_container_registry_bucket_name(storage_service)

    # Check if registry is public
    if is_gs_bucket_public(registry_bucket_name):
        click.echo(
            "Registry is public, no IAM updates required."
            " This cluster can pull images from {} registry.".format(project_id)
        )
        return

    answer = click.confirm(
        "Docker images for this project are stored in bucket '{}'.\n"
        "Grant list and read permissions to this bucket?".format(registry_bucket_name)
    )
    if not answer:
        raise ExitException("Granting these permissions are required to pull images from the private GCR")

    bucket = storage_service.get_bucket(registry_bucket_name)
    # Add bucket read permissions to policy
    policy = bucket.get_iam_policy()
    service_account_email = cluster["role_credentials"]["gcp"]["service_account_id"]
    service_account_tag = "serviceAccount:{}".format(service_account_email)
    role_name = "roles/storage.objectViewer"
    if not policy.get(role_name):
        policy[role_name] = set()
    policy[role_name].add(service_account_tag)
    bucket.set_iam_policy(policy)
    click.echo("Successfully added permissions, you can now run jobs using your own docker images from GCR!")


@click.pass_context
def delete_gc_registry(ctx, cluster):
    """
    This command removes access to private Google Container Registry.

    NOTE: This command uses your GCP credentials, configued through `gcloud auth application-default login`
    Your GCP credentials will need permission to setup these resources.
    """
    if not check_import_and_authenticate():
        return
    try:
        from google.cloud import storage
    except ImportError:
        click.echo("Please `pip install --upgrade 'spell[cluster-gcp]'` and rerun this command")
        return
    project_id = cluster["networking"]["gcp"]["project"]
    storage_service = storage.Client(project=project_id)
    registry_bucket_name = get_container_registry_bucket_name(storage_service)

    # Check if registry is public
    if is_gs_bucket_public(registry_bucket_name):
        click.echo("Registry is public, no IAM updates required.")
        return

    answer = click.confirm("Comfirm removing access to registry?")
    if not answer:
        click.echo("Access to registry not removed.")
        return

    bucket = storage_service.get_bucket(registry_bucket_name)
    # Add bucket read permissions to policy
    policy = bucket.get_iam_policy()
    service_account_email = cluster["role_credentials"]["gcp"]["service_account_id"]
    service_account_tag = "serviceAccount:{}".format(service_account_email)
    if service_account_tag not in policy["roles/storage.objectViewer"]:
        click.echo("Spell does not have access to registry, no IAM updates required.")
        return
    policy["roles/storage.objectViewer"].remove(service_account_tag)
    bucket.set_iam_policy(policy)
    click.echo("Access to registry removed successfully.")


def update_gcp_cluster(ctx, credentials, cluster):
    """
    This command idempotently makes sure that any updates needed since you ran `cluster init gcp` are available.
    """
    from googleapiclient import discovery
    from googleapiclient.errors import HttpError
    from google.cloud import storage

    spell_client = ctx.obj["client"]

    cloud_service = discovery.build("cloudresourcemanager", "v1", credentials=credentials)
    project_id = cluster["networking"]["gcp"]["project"]
    policy = cloud_service.projects().getIamPolicy(resource=project_id, body={}).execute()
    service_account_id = cluster["role_credentials"]["gcp"]["service_account_id"]

    for binding in policy["bindings"]:
        for member in binding["members"]:
            if member.endswith(service_account_id):
                role_name = binding["role"]

    iam_service = discovery.build("iam", "v1", credentials=credentials)
    role = iam_service.projects().roles().get(name=role_name).execute()

    need_to_add = list(set(required_permissions) - set(role["includedPermissions"]))
    need_to_remove = set(role["includedPermissions"]) - set(required_permissions)
    if len(need_to_add) > 0 or len(need_to_remove) > 0:
        click.echo("Your cluster needs to be updated to have the most recent set of role permissions.\n")
        if len(need_to_add) > 0:
            answer = click.confirm(
                "Role {} is currently missing these permissions:\n{}\n"
                "Is it ok to add these permissions?".format(role_name, "\n".join(["- " + s for s in need_to_add]))
            )
            if not answer:
                raise ExitException(
                    "You will not have the ability to use all of the most up to "
                    "date Spell features until you update your cluster"
                )

            role["includedPermissions"] = role["includedPermissions"] + need_to_add
            iam_service.projects().roles().patch(name=role_name, body=role).execute()
            # refresh role for removal step
            role = iam_service.projects().roles().get(name=role_name).execute()
            click.echo("Successfully updated role {}".format(role_name))
        if len(need_to_remove):
            answer = click.confirm(
                "Role {} currently has unnecessary permissions:\n{}\n"
                "Is it ok to remove these permissions?".format(role_name, "\n".join(["- " + s for s in need_to_remove]))
            )
            if not answer:
                raise ExitException(
                    "You will not have the ability to use all of the most up to "
                    "date Spell features until you update your cluster"
                )

            role["includedPermissions"] = [perm for perm in role["includedPermissions"] if perm not in need_to_remove]
            iam_service.projects().roles().patch(name=role_name, body=role).execute()
            click.echo("Successfully updated role {}".format(role_name))

    # verify that S3 key is of service account, not user, fetch otherwise
    storage_client = storage.Client(project=project_id)
    key_id = cluster["role_credentials"]["gcp"]["gs_access_key_id"]
    service_account_email = cluster["role_credentials"]["gcp"]["service_account_id"]
    hmac_keys = storage_client.list_hmac_keys(service_account_email=service_account_email)
    hmac_key_ids = [metadata.access_id for metadata in hmac_keys if metadata.state == "ACTIVE"]
    if len(hmac_key_ids) == 0 or key_id not in set(hmac_key_ids):
        answer = click.confirm(
            "Spell previously used the user-specific S3 Interoperable Access Keys for Google Storage"
            " access, but now uses the more secure HMAC key of the service account."
            " Is it ok to create these keys and update your cluster?"
        )
        if answer:
            gs_access_key_id, gs_secret_access_key = get_interoperable_s3_access_keys(
                storage, project_id, service_account_email
            )
            spell_client.update_gcp_cluster_credentials(
                cluster["name"], access_key=gs_access_key_id, secret=gs_secret_access_key
            )

    # Add an API key to the external service account, if doesn't already exist.
    gs_service_acct_api_key = create_api_key(iam_service, service_account_id)
    if gs_service_acct_api_key:
        click.echo("Created a new API key for spell service account {acct}".format(acct=service_account_id))
        spell_client.update_gcp_cluster_credentials(cluster["name"], api_key=gs_service_acct_api_key)

    # Add firewall rule for internal traffic
    current_version = cluster["version"]
    if current_version < 5:
        click.echo("Ensuring firewall rules are up to date...")

        compute_service = discovery.build("compute", "v1", credentials=credentials)

        region = cluster["networking"]["gcp"]["region"]
        subnet_name = cluster["networking"]["gcp"]["subnet"]
        request = compute_service.subnetworks().get(project=project_id, region=region, subnetwork=subnet_name)
        subnet = request.execute()

        cidr = subnet["ipCidrRange"]
        network_url = subnet["network"]
        rule_name = "{}-internal".format(cluster["name"])
        body = {
            "name": rule_name,
            "description": "Allow traffic between all instances within VPC",
            "network": network_url,
            "sourceRanges": [cidr],
            "allowed": [{"IPProtocol": "TCP"}, {"IPProtocol": "UDP"}],
        }

        request = compute_service.firewalls().insert(project=project_id, body=body)
        try:
            response = request.execute()
            global_progress_bar(project_id, compute_service, response)
            click.echo("Firewall rules updated!")
        # If this rule already exists update it because due to a bug in version 4
        # the source IPs are incorrect
        except HttpError as err:
            if err.resp.status != 409:
                raise

            request = compute_service.firewalls().update(project=project_id, firewall=rule_name, body=body)
            response = request.execute()
            global_progress_bar(project_id, compute_service, response)

    spell_client.update_cluster_version(cluster["name"], cluster_version)

    click.echo("Congratulations, your cluster {} is up to date!".format(cluster["name"]))


def delete_gcp_cluster(ctx, cluster):
    """
    Deletes an GCP cluster, including the Spell Cluster, Machine Types,
    Model Servers, VPC, IAM role, and IAM policies associated with this cluster.
    """

    # Verify the owner is the admin of an org and cluster name is valid
    spell_client = ctx.obj["client"]
    cluster_utils.validate_org_perms(spell_client, ctx.obj["owner"])

    try:
        import google.oauth2
        import google.auth
        from google.api_core.exceptions import NotFound
        from googleapiclient import discovery
        from googleapiclient.errors import HttpError
    except ImportError:
        click.echo("Please `pip install --upgrade 'spell[cluster-gcp]'` and rerun this command")
        return

    try:
        from google.cloud import storage
    except ImportError:
        click.echo("Please `pip install --upgrade 'spell[cluster-gcp]'` and rerun this command")
        return
    if version.parse(storage.__version__) < version.parse("1.18.0"):
        click.echo(
            "Please `pip install --upgrade 'spell[cluster-gcp]'` to include HMAC functionality."
            " Your version is {}, whereas 1.18.0 is required as a minimum".format(storage.__version__)
        )
        return

    if not is_installed("gcloud"):
        raise ExitException(
            "`gcloud` is required, please install it before proceeding. "
            "See https://cloud.google.com/pubsub/docs/quickstart-cli"
        )

    try:
        credentials, project_id = google.auth.default()
    except google.auth.exceptions.DefaultCredentialsError:
        click.echo(
            """Please run `gcloud auth application-default login` to allow Spell
        to use your user credentials to delete the cluster, and rerun this command"""
        )
        return

    compute_service = discovery.build("compute", "v1", credentials=credentials)
    iam_service = discovery.build("iam", "v1", credentials=credentials)
    resource_service = discovery.build("cloudresourcemanager", "v1", credentials=credentials)

    click.echo(
        """This command will help you delete your Spell cluster. It will
    - Delete the VPC network which Spell created to spin up workers in
    - Delete all subnets in the VPC
    - Delete the IAM Service Account and roles allowing Spell to spin up and down
      machines and access the GS bucket
    - IF EXISTS Delete Model Server GKE cluster
    - OPTIONALLY Delete the Google Storage bucket used to store your run outputs
      (you will be prompted to choose to keep or delete the bucket)"""
    )
    if not click.confirm("Are you SURE you want to delete the spell cluster {}?".format(cluster["name"])):
        return

    project_id = get_project(resource_service, project_id)

    # Delete Machine Types and Model Servers on cluster first
    with api_client_exception_handler():
        click.echo(
            "Sending message to Spell to remove all Machine Types " "from the cluster {}...".format(cluster["name"])
        )
        spell_client.delete_cluster_contents(cluster["name"])

    # Delete associated GKE cluster if it exists
    if cluster.get("serving_cluster_name"):
        gke_delete_cluster(
            project_id,
            cluster,
        )

    # Block until cluster is drained. This is necessary because the API will fail to
    # drain if we delete the IAM role before the machine types are marked as drained
    cluster_utils.block_until_cluster_drained(spell_client, cluster["name"])

    # Delete Firewalls
    delete_firewall(compute_service, project_id, "{}-spell-api".format(cluster["name"]))
    delete_firewall(compute_service, project_id, "{}-internal".format(cluster["name"]))

    # Delete Subnets
    try:
        subnet_name = cluster["name"]
        region = cluster["networking"]["gcp"]["region"]
        click.echo("Deleting subnetwork {}...".format(subnet_name))
        response = (
            compute_service.subnetworks().delete(project=project_id, region=region, subnetwork=subnet_name).execute()
        )
        region_progress_bar(project_id, compute_service, response, region)
        click.echo("Deleted subnetwork {}".format(subnet_name))
    except HttpError as err:
        if err.resp.status == 404:
            click.echo("subnetwork {} is already deleted".format(subnet_name))
        else:
            raise ExitException("Error attempting to delete subnetwork {}. " "Err was {}".format(subnet_name, err))

    # Delete VPC
    try:
        vpc_name = cluster["networking"]["gcp"]["vpc"]
        click.echo("Deleting VPC {}...".format(vpc_name))
        response = compute_service.networks().delete(project=project_id, network=vpc_name).execute()
        global_progress_bar(project_id, compute_service, response)
        click.echo("VPC {} deleted".format(vpc_name))
    except HttpError as err:
        if err.resp.status == 404:
            click.echo("VPC {} is already deleted".format(vpc_name))
        else:
            raise ExitException("Error attempting to delete VPC {}. " "Err was {}".format(vpc_name, err))

    # Delete Role
    iam_policies = resource_service.projects().getIamPolicy(resource=project_id, body={}).execute()
    binding_to_remove = None
    for binding in iam_policies["bindings"]:
        if "serviceAccount:{}".format(cluster["role_credentials"]["gcp"]["service_account_id"]) in binding["members"]:
            binding_to_remove = binding
            break
    if binding_to_remove is None:
        click.echo("Could not find role to delete, skipping")
    else:
        role_name = binding_to_remove["role"]
        click.echo("Found role {} to delete, deleting".format(role_name))
        try:
            response = iam_service.projects().roles().delete(name=role_name).execute()
        except HttpError as err:
            if "already deleted" in err._get_reason():
                click.echo("Role {} is already deleted".format(role_name))
            else:
                raise ExitException("Error attempting to delete role {}. " "Err was {}".format(role_name, err))
        # Delete binding
        click.echo("Deleting binding for role {}...".format(role_name))
        iam_policies["bindings"].remove(binding_to_remove)
        set_iam_policy_body = {"policy": iam_policies}
        resource_service.projects().setIamPolicy(resource=project_id, body=set_iam_policy_body).execute()
        click.echo("Deleted binding for role {}".format(role_name))

    # Delete Service Account
    try:
        service_acct_name = "projects/{}/serviceAccounts/{}".format(
            project_id, cluster["role_credentials"]["gcp"]["service_account_id"]
        )
        iam_service.projects().serviceAccounts().delete(name=service_acct_name).execute()
    except HttpError as err:
        if err.resp.status == 404:
            click.echo("Service account {} is already deleted".format(service_acct_name))
        else:
            raise ExitException(
                "Error attempting to delete service account {}. " "Err was {}".format(service_acct_name, err)
            )

    # Optionally delete the output bucket
    bucket_name = cluster["storage_uri"]
    if click.confirm("Delete bucket {}? WARNING: This will delete all the data in the bucket".format(bucket_name)):
        try:
            storage_client = storage.Client(project=project_id)
            bucketObj = storage_client.get_bucket(bucket_name)
            bucketObj.delete(force=True)
            click.echo("Deleted bucket {}".format(bucket_name))
        except NotFound:
            click.echo("Bucket {} is already deleted!".format(bucket_name))
        except Exception as err:
            raise ExitException("Failed to delete bucket {}." "Err was {}".format(bucket_name, err))

    # Last step is to mark the cluster as deleted
    with api_client_exception_handler():
        spell_client.delete_cluster(cluster["name"])
        click.echo("Successfully deleted cluster on Spell")


def delete_firewall(compute_service, project_id, firewall_name):
    from googleapiclient.errors import HttpError

    try:
        click.echo("Deleting Firewall {}...".format(firewall_name))
        response = compute_service.firewalls().delete(project=project_id, firewall=firewall_name).execute()
        global_progress_bar(project_id, compute_service, response)
        click.echo("Deleted Firewall {}".format(firewall_name))
    except HttpError as err:
        if err.resp.status == 404:
            click.echo("Firewall {} is already deleted".format(firewall_name))
        else:
            raise ExitException("Error attempting to delete Firewall {}. " "Err was {}".format(firewall_name, err))


def gke_delete_cluster(project_id, cluster):

    gke_name, zone = (
        cluster.get("serving_cluster_short_name"),
        cluster.get("serving_cluster_location"),
    )
    if not gke_name or not zone:  # TODO(waldo) remove this fallback after backfilling serving_cluster_location in db
        zone, gke_name = extract_gke_cluster_info(project_id, cluster.get("serving_cluster_name"))

    cmd = [
        "gcloud",
        "container",
        "clusters",
        "delete",
        gke_name,
        "--project",
        project_id,
        "--quiet",
        "--zone",
        zone,
    ]

    if not click.confirm("Delete model serving cluster {}?".format(gke_name)):
        return
    click.echo("Deleting GKE cluster {}. This can take a while!".format(gke_name))
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError:
        click.echo(
            "Failed to run `gcloud`. Make sure it's installed correctly and "
            "your inputs are valid. Error details are above in the `gcloud` output. "
            "You will need to delete your GKE cluster using `gcloud` manually."
        )


def extract_gke_cluster_info(project_id, cluster_name):
    # GKE cluster names take the form
    # gke_PROJECT_ZONE_CLUSTERNAME for zonal clusters

    zone_clustername = cluster_name[len("gke_{}_".format(project_id)) :]
    zone, _, cluster_name = zone_clustername.partition("_")
    return zone, cluster_name


def global_progress_bar(project, compute_service, response):
    with click.progressbar(length=100, show_eta=False) as bar:
        while response["status"] != "DONE":
            bar.update(response["progress"])
            response = compute_service.globalOperations().get(project=project, operation=response["name"]).execute()
        if "error" in response and "errors" in response["error"]:
            first_error = response["error"]["errors"][0]
            raise GcpException("Error with GCP API {}: {}".format(first_error["code"], first_error["message"]))
        bar.update(100)


def region_progress_bar(project, compute_service, response, region):
    with click.progressbar(length=100, show_eta=False) as bar:
        while response["status"] != "DONE":
            bar.update(response["progress"])
            response = (
                compute_service.regionOperations()
                .get(project=project, region=region, operation=response["name"])
                .execute()
            )
        if "error" in response and "errors" in response["error"]:
            first_error = response["error"]["errors"][0]
            raise GcpException("Error with GCP API {}: {}".format(first_error["code"], first_error["message"]))
        bar.update(100)


class GcpException(click.ClickException):
    def __init__(self, message):
        super(GcpException, self).__init__(message)

    def show(self):
        logger.error(self.message)
