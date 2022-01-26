import click
import re
from spell.cli.log import logger
from spell.cli.commands.cluster_aws import (
    create_aws,
    add_s3_bucket,
    remove_s3_bucket,
    update_aws_cluster,
    delete_aws_cluster,
    add_ec_registry,
    delete_ec_registry,
    set_custom_instance_role,
)
from spell.cli.commands.cluster_gcp import (
    create_gcp,
    add_gs_bucket,
    remove_gs_bucket,
    update_gcp_cluster,
    delete_gcp_cluster,
    add_gc_registry,
    delete_gc_registry,
    set_custom_instance_service_acct,
)
from spell.cli.commands.cluster_azure import (
    create_azure,
    delete_azure_cluster,
    add_az_bucket,
    rotate_az_storage_key,
    add_az_registry,
    delete_az_registry,
)
from spell.cli.commands.cluster_private import (
    create_private,
    delete_private_cluster,
)
from spell.cli.commands.machine_type import (
    list_machine_types,
    add_machine_type,
    scale_machine_type,
    delete_machine_type,
    get_machine_type_token,
)
from spell.cli.utils import (
    require_import,
    require_pip,
    cluster_utils,
    tabulate_rows,
)
from spell.cli.utils.command import docs_option
from spell.cli.exceptions import ExitException

# Regex used to extract various sections of an AWS ARN
ARN_RE = re.compile(r"^arn:aws:iam::(\d+):(role|instance-profile)/(.+)")


@click.group(
    name="cluster",
    short_help="Manage external clusters",
    help="Manage external clusters on Spell",
)
@click.pass_context
def cluster(ctx):
    """
    List all external clusters for current owner
    """


@click.command(name="list", short_help="List all clusters")
@click.pass_context
def list_clusters(ctx):
    spell_client = ctx.obj["client"]
    # TODO(ian) Allow read access to 'member' role
    cluster_utils.validate_org_perms(spell_client, ctx.obj["owner"])
    clusters = spell_client.list_clusters()
    if len(clusters) == 0:
        click.echo("There are no external clusters to display.")
        return

    def create_row(cluster):
        provider = cluster["cloud_provider"]
        networking = cluster["networking"][provider.lower()]
        role_creds = cluster["role_credentials"][provider.lower()]
        custom_instance_perms = "None set"
        if provider == "AWS" and "custom_instance_profile_arn" in role_creds:
            role_match = ARN_RE.match(role_creds["custom_instance_profile_arn"])
            if role_match is None or role_match.group(3) is None:
                logger.warning("PARSE ERROR! Cannot parse ARN {}".format(role_creds["custom_instance_profile_arn"]))
                custom_instance_perms = "PARSE ERROR"
            else:
                custom_instance_perms = role_match.group(3)
        if provider == "AWS":
            vpc = networking["vpc_id"]
        elif provider == "GCP":
            vpc = networking["vpc"]
        else:
            vpc = "spell-vnet"
        return (
            cluster["name"],
            provider,
            cluster["storage_uri"],
            vpc,
            networking["region"],
            cluster["version"],
            cluster.get("serving_cluster_name") is not None,
            custom_instance_perms,
        )

    tabulate_rows(
        [create_row(c) for c in clusters],
        headers=[
            "NAME",
            "PROVIDER",
            "BUCKET NAME",
            "VPC",
            "REGION",
            "CLUSTER VERSION",
            "MODEL SERVING ENABLED",
            "CUSTOM INSTANCE PERMS",
        ],
    )


@click.command(name="add-bucket", short_help="Adds a cloud storage bucket to SpellFS")
@click.pass_context
@cluster_utils.check_cli_version
@cluster_utils.pass_cluster
@click.option(
    "-p",
    "--profile",
    help="This AWS profile will be used to get your Access Key ID and Secret as well as your Region. "
    "You will be prompted to confirm the Key and Region are correct before continuing. "
    "This key will be used to adjust IAM permissions of the role associated with the cluster "
    "that the bucket is being added to.",
)
@click.option("--bucket", "bucket_name", help="Name of bucket")
@click.option("--cross-account", "cross_account", is_flag=True, help="Whether or not this is a cross account bucket")
@cluster_utils.for_gcp(
    require_import("google.cloud.storage", pkg_extras="cluster-gcp"),
    cluster_utils.handle_aws_profile_flag,
)
@cluster_utils.for_aws(
    cluster_utils.pass_aws_session(
        perms=[
            "List your buckets to generate an options menu of buckets that can be added to Spell",
            "Add list and read permissions for that bucket to the IAM role associated with the cluster",
        ],
    ),
)
@cluster_utils.for_azure(cluster_utils.handle_aws_profile_flag)
def add_bucket(ctx, cluster, bucket_name, cross_account=False, aws_session=None):
    """
    This command adds a cloud storage bucket (S3, GS, AzureStorage) to SpellFS, which enables interaction with the
    bucket objects via ls, cp, and mounts. It will also update the permissions of that bucket to allow
    Spell read access to it
    """
    spell_client = ctx.obj["client"]
    cluster_type = cluster["cloud_provider"]

    if cross_account and cluster_type != "AWS":
        raise ExitException("Cross-account bucket access is currently only supported on AWS clusters")

    if cluster_type == "AWS":
        add_s3_bucket(spell_client, aws_session, cluster, bucket_name, cross_account)
    elif cluster_type == "GCP":
        add_gs_bucket(spell_client, cluster, bucket_name)
    elif cluster_type == "Azure":
        add_az_bucket(spell_client, cluster, bucket_name)


@click.command(name="remove-bucket", short_help="Removes a cloud storage bucket that was added with add-bucket")
@click.pass_context
@cluster_utils.check_cli_version
@cluster_utils.pass_cluster
@click.option(
    "-p",
    "--profile",
    help="This AWS profile will be used to get your Access Key ID and Secret as well as your Region. "
    "You will be prompted to confirm the Key and Region are correct before continuing. "
    "This key will be used to adjust IAM permissions of the role associated with the cluster "
    "that the bucket is being removed from.",
)
@click.option("--bucket", "bucket_name", help="Name of bucket")
@cluster_utils.for_gcp(
    require_import("google.cloud.storage", pkg_extras="cluster-gcp"),
    cluster_utils.handle_aws_profile_flag,
)
@cluster_utils.for_aws(
    cluster_utils.pass_aws_session(
        perms=[
            "Remove list and read permissions for the chosen bucket from the IAM role associated with the cluster",
        ],
    ),
)
@cluster_utils.for_azure(cluster_utils.handle_aws_profile_flag)
def remove_bucket(ctx, cluster, bucket_name, aws_session=None):
    """
    This command removes a cloud storage bucket (S3, GS, Azure Blob) that had been added to SpellFS previously
    with `spell cluster add-bucket`. It will also updates the permissions of that bucket to remove Spell's access to it
    """
    spell_client = ctx.obj["client"]
    cluster_type = cluster["cloud_provider"]
    if cluster_type == "AWS":
        remove_s3_bucket(spell_client, aws_session, cluster, bucket_name)
    elif cluster_type == "GCP":
        remove_gs_bucket(spell_client, cluster, bucket_name)
    elif cluster_type == "Azure":
        raise ExitException("Azure remove-bucket is not yet implemented")


@click.command(
    name="set-instance-permissions",
    short_help="Sets the cloud machine instance permissions for the cluster",
)
@click.pass_context
@cluster_utils.check_cli_version
@cluster_utils.pass_cluster
@click.option(
    "-p",
    "--profile",
    help="This AWS profile will be used to get your Access Key ID and Secret as well as your Region. "
    "You will be prompted to confirm the Key and Region are correct before continuing. "
    "This key will be used to adjust IAM permissions of the role associated with the cluster "
    "that the bucket is being added to.",
)
@click.option(
    "--iam-role-arn",
    "iam_role_arn",
    help="AWS IAM Role ARN (Required for AWS Clusters, must match Instance Profile)",
)
@click.option(
    "--iam-instance-profile-arn",
    "iam_instance_profile_arn",
    help="AWS IAM Instance Profile ARN (Required for AWS Clusters, must match Role)",
)
@click.option(
    "--iam-service-account",
    "iam_service_account",
    help="GCP IAM Service Account (Required for GCP Clusters)",
)
@cluster_utils.for_gcp(
    require_import("google.cloud.storage", pkg_extras="cluster-gcp"),
    cluster_utils.handle_aws_profile_flag,
)
@cluster_utils.for_aws(
    cluster_utils.pass_aws_session(
        perms=["Update your Spell IAM Role to allow remove iam:passrole to the input IAM Role ARN"],
    ),
)
def set_instance_permissions(
    ctx,
    cluster,
    iam_role_arn,
    iam_instance_profile_arn,
    iam_service_account,
    aws_session=None,
):
    """
    This command sets the Instance Profile / Service Account Spell will give to cloud instances on your
    cluster. This can be useful for allowing your Spell runs to access cloud resources that are normally
    private like RDS or DynamoDB. If there is already a custom instance permission set on this cluster it
    will be replaced with the new one.

    For AWS this requires an IAM Role and an IAM Instance Profile that match (details here:
    https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_switch-role-ec2_instance-profiles.html)
    and an IAM Role which has "ec2.amazonaws.com" as a trusted entity (details here:
    https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-service.html)


    For GCP this can be any IAM Service Account within your GCP project. Note that this command will
    grant the iam.serviceAccountUser role on the input service account specifically to your Spell
    cluster's service account. More details available here: https://cloud.google.com/iam/docs/service-accounts#user-role
    """
    spell_client = ctx.obj["client"]
    cluster_type = cluster["cloud_provider"]
    if cluster_type == "AWS":
        # Validation on the ARNs
        if not iam_role_arn or not iam_instance_profile_arn:
            raise ExitException("Missing required --iam-role-arn and --iam-instance-profile-arn for AWS clusters")
        role_match = ARN_RE.match(iam_role_arn)
        if role_match is None or role_match.group(2) != "role":
            raise ExitException("Unexpected value for --iam-role-arn, it must be a valid ARN")
        ip_match = ARN_RE.match(iam_instance_profile_arn)
        if ip_match is None or ip_match.group(2) != "instance-profile":
            raise ExitException("Unexpected value for --iam-instance-profile-arn, it must be a valid ARN")
        if ip_match.group(1) != role_match.group(1):
            raise ExitException("The provided ARNs have different account IDs, they must be from the same account")

        set_custom_instance_role(spell_client, aws_session, cluster, iam_role_arn, iam_instance_profile_arn)
    elif cluster_type == "GCP":
        if cluster["version"] < 11:
            raise ExitException(
                "Cluster version {} is below the required version of 11 for this feature. "
                + "Please run `spell cluster update` in order to support custom instance permissions."
            )
        if not iam_service_account:
            raise ExitException("Missing required --iam-service-account for GCP clusters")
        set_custom_instance_service_acct(spell_client, cluster, iam_service_account)
    else:
        raise ExitException("Unknown cluster with provider {}, exiting.".format(cluster_type))


@click.command(
    name="unset-instance-permissions",
    short_help="Unsets the cloud machine instance permissions for the cluster",
)
@click.pass_context
@cluster_utils.check_cli_version
@cluster_utils.pass_cluster
@click.option(
    "-p",
    "--profile",
    help="This AWS profile will be used to get your Access Key ID and Secret as well as your Region. "
    "You will be prompted to confirm the Key and Region are correct before continuing. "
    "This key will be used to adjust IAM permissions of the role associated with the cluster "
    "that the bucket is being added to.",
)
@cluster_utils.for_gcp(
    require_import("google.cloud.storage", pkg_extras="cluster-gcp"),
    cluster_utils.handle_aws_profile_flag,
)
@cluster_utils.for_aws(
    cluster_utils.pass_aws_session(
        perms=["Update your Spell IAM Role to remove iam:passrole to the input IAM Role ARN"],
    ),
)
def unset_instance_permissions(
    ctx,
    cluster,
    aws_session=None,
):
    """
    This command unsets the Instance Profile / Service Account stored on your Spell Cluster.
    Please see the `spell cluster set-instance-permissions` command for more details.
    """
    spell_client = ctx.obj["client"]
    cluster_type = cluster["cloud_provider"]
    if cluster_type == "AWS":
        set_custom_instance_role(spell_client, aws_session, cluster, None, None)
        return
    elif cluster_type == "GCP":
        set_custom_instance_service_acct(spell_client, cluster, None)
    else:
        raise ExitException("Unknown cluster with provider {}, exiting.".format(cluster_type))


@click.command(
    name="add-docker-registry",
    short_help="Configures your cluster to enable runs with docker images in the private registry"
    " hosted by your cloud provider (ECR or GCR respectively)",
)
@click.pass_context
@cluster_utils.check_cli_version
@click.option(
    "--cluster-name",
    default=None,
    help="Name of cluster to add registry permissions to",
)
@click.option("--repo", "repo_name", help="Name of repository (ECR) or blob container (ACR)")
@click.option(
    "-p",
    "--profile",
    "profile",
    default="default",
    help="This AWS profile will be used to get your Access Key ID and Secret as well as your Region. "
    "You will be prompted to confirm the Key and Region are correct before continuing. "
    "This key will be used to adjust IAM permissions of the role associated with the cluster "
    "that needs access to the registry.",
)
def add_docker_registry(ctx, cluster_name, repo_name, profile):
    """
    This command enables pulling docker images from a private registry.
    Read permissions to the registry will be added to the IAM role associated with the cluster.
    """
    cluster = cluster_utils.deduce_cluster(ctx, cluster_name)

    cluster_type = cluster["cloud_provider"]
    if cluster_type == "AWS":
        ctx.invoke(add_ec_registry, repo_name=repo_name, cluster=cluster, profile=profile)
    elif cluster_type == "GCP":
        if profile != "default":
            click.echo("--profile is not a valid option for GCP clusters")
            ctx.exit(1)
        ctx.invoke(add_gc_registry, cluster=cluster)
    elif cluster_type == "Azure":
        if profile != "default":
            click.echo("--profile is not a valid option for Azure clusters")
            ctx.exit(1)
        if repo_name is None:
            click.echo("Must include --repo for Azure clusters")
            ctx.exit(1)
        ctx.invoke(add_az_registry, repo_name=repo_name, cluster=cluster)
    else:
        raise ExitException("Unknown cluster with provider {}, exiting.".format(cluster_type))


@click.command(
    name="rotate-storage-key",
    short_help="Rotates the storage key for storage accounts in Azure clusters",
)
@click.pass_context
@cluster_utils.check_cli_version
@click.option(
    "--cluster-name",
    default=None,
    help="Name of cluster to add registry permissions to",
)
def rotate_storage_key(ctx, cluster_name):
    """
    This command rotates the cluster storage key for Azure
    """
    cluster = cluster_utils.deduce_cluster(ctx, cluster_name)

    cluster_type = cluster["cloud_provider"]
    if cluster_type == "Azure":
        ctx.invoke(rotate_az_storage_key, ctx=ctx, cluster=cluster)
    else:
        raise ExitException("Storage key rotation only supported for Azure clusters.")


@click.command(
    name="delete-docker-registry",
    short_help="Removes your cluster's access to docker images in the private registry"
    " hosted by your cloud provider (ECR or GCR respectively).",
)
@click.pass_context
@cluster_utils.check_cli_version
@click.option("--repo", "repo_name", help="Name of repository. ECR only")
@click.option(
    "--cluster-name",
    default=None,
    help="Name of cluster to remove registry permissions from",
)
@click.option(
    "-p",
    "--profile",
    "profile",
    default="default",
    help="This AWS profile will be used to get your Access Key ID and Secret as well as your Region. "
    "You will be prompted to confirm the Key and Region are correct before continuing. "
    "This key will be used to adjust IAM permissions of the role associated with the cluster "
    "that has access to the registry.",
)
def delete_docker_registry(ctx, cluster_name, repo_name, profile):
    """
    This command removes your cluster's access to docker images in the private registry hosted by your cloud provider.
    """
    cluster = cluster_utils.deduce_cluster(ctx, cluster_name)

    cluster_type = cluster["cloud_provider"]
    if cluster_type == "AWS":
        ctx.invoke(delete_ec_registry, repo_name=repo_name, cluster=cluster, profile=profile)
    elif cluster_type == "GCP":
        if profile != "default":
            click.echo("--profile is not a valid option for GCP clusters")
            ctx.exit(1)
        ctx.invoke(delete_gc_registry, cluster=cluster)
    elif cluster_type == "Azure":
        if profile != "default":
            click.echo("--profile is not a valid option for Azure clusters")
            ctx.exit(1)
        if repo_name is None:
            click.echo("Must include --repo for Azure clusters")
            ctx.exit(1)
        ctx.invoke(delete_az_registry, repo_name=repo_name, cluster=cluster)
    else:
        raise ExitException("Unknown cluster with provider {}, exiting.".format(cluster_type))


@click.command(
    name="update",
    short_help="Makes sure your Spell cluster is fully up to date and able to support the latest features",
)
@click.pass_context
@cluster_utils.check_cli_version
@cluster_utils.pass_cluster
@click.option("-p", "--profile", help="AWS profile to pull credentials from")
@cluster_utils.for_aws(
    require_pip("boto3>=1.13.0", pkg_extras="cluster-aws"),
    cluster_utils.pass_aws_session(
        perms=[
            "Update security group ingress rules for the cluster VPC",
            "Update cluster bucket configuration",
            "Update DNS hostname configuration for the cluster VPC",
        ],
    ),
)
@cluster_utils.for_gcp(
    require_import("googleapiclient", pkg_extras="cluster-gcp"),
    require_pip("google-cloud-storage>=1.18.0", pkg_extras="cluster-gcp"),
    cluster_utils.pass_gcp_project_creds,
    cluster_utils.handle_aws_profile_flag,
)
def update(ctx, cluster, aws_session=None, gcp_project=None, gcp_creds=None):
    """
    This command makes sure your Spell cluster is fully up to date and able to support the latest features
    """
    cluster_type = cluster["cloud_provider"]
    if cluster_type == "AWS":
        update_aws_cluster(ctx, aws_session, cluster)
    elif cluster_type == "GCP":
        update_gcp_cluster(ctx, gcp_creds, cluster)


@click.command(
    name="delete",
    short_help="Deletes a given cluster",
    help="Facilitates the deletion of your Spell cluster by removing the associated "
    "infrastructure on Spell as well as deleting all associated cloud resources. "
    "It will OPTIONALLY delete the data in your output bucket - including run outputs.",
)
@click.pass_context
@cluster_utils.check_cli_version
@click.option(
    "-c",
    "--cluster",
    "cluster_name",
    type=str,
    help="The name of the Spell cluster that you would like to delete. "
    "If it's not specified, it will default to the ONE cluster the current owner has, "
    "or prompt if the current owner has more than one cluster.",
    hidden=True,
)
@click.option(
    "-p",
    "--profile",
    "profile",
    help="This AWS profile will be used to get your Access Key ID and Secret as well as your Region. "
    "You will be prompted to confirm the Key and Region are correct before continuing. "
    "This key will be used to destroy the VPC, IAM Roles, and optionally the S3 bucket "
    "created for the cluster.",
)
# If this cluster was constructed in an existing VPC (likely in on-prem mode) this option will prevent
# the vpc from being deleted
@click.option("--keep-vpc", "keep_vpc", is_flag=True, hidden=True)
def delete(ctx, cluster_name, profile, keep_vpc):
    cluster = cluster_utils.deduce_cluster(ctx, cluster_name)
    if cluster is None:
        return

    cluster_type = cluster["cloud_provider"]
    if cluster_type == "AWS":
        delete_aws_cluster(ctx, cluster, profile, keep_vpc)
    elif cluster_type == "GCP":
        if keep_vpc:
            click.echo("--keep-vpc is not currently supported for GCP. Contact Spell for support.")
        if profile:
            click.echo("--profile is not a valid option for GCP clusters")
            ctx.exit(1)
        delete_gcp_cluster(ctx, cluster)
    elif cluster_type == "Azure":
        if keep_vpc:
            click.echo("--keep-vpc is not currently supported for Azure. Contact Spell for support.")
        if profile:
            click.echo("--profile is not a valid option for Azure clusters")
            ctx.exit(1)
        delete_azure_cluster(ctx, cluster)
    elif cluster_type == "Customer":
        delete_private_cluster(ctx, cluster)
    else:
        raise Exception("Unknown cluster with provider {}, exiting.".format(cluster_type))


@cluster.group(
    name="init",
    short_help="Create a cluster",
    help="Create a new aws/gcp/azure cluster for your org account\n\n"
    "Set up a cluster to use machines in your own AWS/GCP/Azure account",
)
@click.pass_context
@cluster_utils.check_cli_version
def init(ctx):
    pass


@cluster.group(
    name="machine-type",
    short_help="Manage machine types",
    help="Manage groups of similar machines which can be used for training runs and workspaces on Spell",
)
@click.option(
    "-c",
    "--cluster",
    "cluster_name",
    type=str,
    help="The name of the Spell cluster",
    hidden=True,
)
@docs_option("https://spell.ml/docs/ownvpc_machine_types/")
@click.pass_context
def machine_type(ctx, cluster_name):
    # TODO(ian) Allow read access to 'member' role
    ctx.obj["cluster"] = cluster_utils.deduce_cluster(ctx, cluster_name)


# register generic subcommands
cluster.add_command(list_clusters)
cluster.add_command(add_bucket)
cluster.add_command(remove_bucket)
cluster.add_command(set_instance_permissions)
cluster.add_command(unset_instance_permissions)
cluster.add_command(add_docker_registry)
cluster.add_command(delete_docker_registry)
cluster.add_command(update)
cluster.add_command(delete)
cluster.add_command(rotate_storage_key)

# register init subcommands
init.add_command(create_aws)
init.add_command(create_gcp)
init.add_command(create_azure)
init.add_command(create_private)

# register machine-type subcommands
machine_type.add_command(list_machine_types)
machine_type.add_command(add_machine_type)
machine_type.add_command(scale_machine_type)
machine_type.add_command(delete_machine_type)
machine_type.add_command(get_machine_type_token)
