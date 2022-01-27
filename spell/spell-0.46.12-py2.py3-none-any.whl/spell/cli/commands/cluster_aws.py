import ipaddress
import json
import random
import subprocess
import tempfile
import time
from packaging import version

import click

from spell.cli.exceptions import (
    api_client_exception_handler,
    ExitException,
)
from spell.cli.log import logger
from spell.cli.utils import is_installed, cluster_utils
from spell.cli.utils.kube_cluster_templates import (
    eks_cluster_aws_auth_template,
    generate_eks_cluster_autoscaler_yaml,
    generate_eks_cluster_secret_yaml,
)
from spell.cli.utils.command import docs_option
from spell.cli.utils.utils import acct_id_from_role_arn

from spell.cli.constants import WORKER_OPEN_PORTS

EKS_DEFAULT_NODEGROUP_TYPE = "m5.large"  # Instance type of default EKS node groups
BUCKET_LIFECYCLE_RULE_NAME = "Intelligent Tiering - Spell"

cluster_version = 4


@click.command(name="aws", short_help="Sets up an AWS VPC as a Spell cluster")
@click.pass_context
@click.option("-n", "--name", "name", help="This will be used by Spell for you to identify the cluster")
@click.option(
    "-p",
    "--profile",
    "profile",
    help="This AWS profile will be used to get your Access Key ID and Secret as well as your Region. "
    "You will be prompted to confirm the Key and Region are correct before continuing. "
    "This key will be used to create all the resources necessary for Spell to manage machines "
    "in your external VPC. It must have permissions to create these resources.",
)
# Hidden option for creating cluster inside an existing VPC
# Note this will use all subnets for spell workers
# A new security group will still be created
@click.option("-v", "--vpc", "vpc_id", hidden=True)
@docs_option("https://spell.ml/docs/aws_ownvpc_setup/")
def create_aws(ctx, name, profile, vpc_id):
    """
    This command sets an AWS VPC of your choosing as an external Spell cluster.
    This will let your organization run runs in that VPC, so your data never leaves
    your VPC. You set an S3 bucket of your choosing for all run outputs to be written to.
    After this cluster is set up you will be able to select the types and number of machines
    you would like Spell to create in this cluster.

    NOTE: This command uses your AWS credentials, found in ~/.aws/credentials to create the necessary
    AWS resources for Spell to access and manage those machines. Your AWS credentials will
    need permission to setup these resources.
    """

    # Verify the owner is the admin of an org and cluster name is valid
    spell_client = ctx.obj["client"]
    cluster_utils.validate_org_perms(spell_client, ctx.obj["owner"])

    if not name:
        name = click.prompt("Enter a display name for this AWS cluster within Spell")
    if not profile:
        profile = click.prompt("Enter the name of the AWS profile you would like to use", default="default")

    with api_client_exception_handler():
        spell_client.validate_cluster_name(name)

    try:
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError
    except ImportError:
        click.echo("Please pip install boto3 and rerun this command")
        return

    if version.parse(boto3.__version__) < version.parse("1.13.0"):
        click.echo(
            "Please `pip install --upgrade 'spell[cluster-aws]'`."
            " Your version is {}, whereas 1.13.0 is required as a minimum".format(boto3.__version__)
        )
        return

    # Setup clients with the provided profile
    try:
        session = boto3.session.Session(profile_name=profile)
        s3 = session.resource("s3")
        ec2 = session.resource("ec2")
        iam = session.resource("iam")
    except BotoCoreError as e:
        click.echo("Failed to set profile {} with error: {}".format(profile, e))
        return

    supports_gpu = session.region_name in (
        "ap-northeast-1",
        "ap-northeast-2",
        "ap-southeast-1",
        "ap-southeast-2",
        "ca-central-1",
        "cn-north-1",
        "cn-northwest-1",
        "eu-central-1",
        "eu-west-1",
        "eu-west-2",
        "eu-west-3",
        "us-east-1",
        "us-east-2",
        "us-west-2",
    )
    if not supports_gpu:
        if not click.confirm(
            "AWS does not support GPU types in {}. You can still create a cluster, but it will "
            "only have access to CPU types - continue?".format(session.region_name)
        ):
            return

    click.echo(
        """This command will help you
    - Set up an S3 bucket to store your run outputs in
    - Set up a VPC which Spell will spin up workers in to run your jobs
    - Ensure subnets in the VPC in multiple availability zones
    - Set up a Security Group providing Spell SSH and Docker access to workers
    - Set up a service-linked IAM role for AWS' spot instance service
    - Set up an IAM role allowing Spell to spin up and down machines and access the S3 bucket"""
    )
    if not click.confirm(
        "All of this will be done with your AWS profile '{}' which has "
        "Access Key ID '{}' and region '{}' - continue?".format(
            profile, session.get_credentials().access_key, session.region_name
        )
    ):
        return

    bucket_name = create_bucket(s3, session.region_name, name)
    if not vpc_id:
        vpc = create_vpc(ec2, name)
    else:
        vpc = verify_existing_vpc(ec2, vpc_id)
    security_group = create_security_group(ec2, vpc, spell_client)
    # Create spot instance service-linked role
    try:
        session.client("iam").create_service_linked_role(AWSServiceName="spot.amazonaws.com")
    except ClientError as e:
        if "InvalidInput" not in str(e):
            click.echo(str(e))
    # Create SpellAccess role

    # TODO(waldo) Can we use spell_node_role() directly instead of using this "root" arn?
    spell_node_role = spell_client.get_spell_node_role()
    spell_acct_id, _ = acct_id_from_role_arn(spell_node_role)
    spell_aws_arn = "arn:aws:iam::{}:root".format(spell_acct_id)

    role_arn, external_id, read_policy = create_role(iam, bucket_name, spell_aws_arn)

    with api_client_exception_handler():
        cluster = spell_client.create_aws_cluster(
            name,
            role_arn,
            external_id,
            read_policy,
            security_group.id,
            bucket_name,
            vpc.id,
            [s.id for s in vpc.subnets.all()],
            session.region_name,
        )
        cluster_utils.echo_delimiter()
        url = "{}/{}/clusters/{}".format(ctx.obj["web_url"], ctx.obj["owner"], cluster["name"])
        click.echo(
            "Your cluster {} is initialized! Head over to the web console to create machine types "
            "to execute your runs on - {}".format(name, url)
        )

    spell_client.update_cluster_version(cluster["name"], cluster_version)


def eks_update(ctx, session, cluster, eks_cluster_name, support_runs):
    is_public = cluster["is_serving_cluster_public"]

    return eks_configure_k8s(ctx, session, cluster, eks_cluster_name, is_public, support_runs)


def add_nvidia_device_driver():
    """Add NVIDIA's gpu device driver to k8s cluster so GPUs can be used in pods
    This is driver is cloud-agnostic but GKE has their own version"""
    click.echo("Setting up NVIDIA GPU Device Plugin...")
    subprocess.check_call(
        (
            "kubectl",
            "apply",
            "--filename",
            "https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.6.0/nvidia-device-plugin.yml",
        ),
    )
    click.echo("GPU Device Plugin set up!")


def add_eks_auth(spell_client):
    """Give Spell service account permission to access user's EKS cluster"""
    import kubernetes.client  # TODO(waldo) Either use Python client everywhere, or use kubectl everywhere

    spell_node_role_arn = spell_client.get_spell_node_role()
    try:
        kube_api = kubernetes.client.CoreV1Api()
        conf_map = kube_api.read_namespaced_config_map("aws-auth", "kube-system", exact=True, export=True)
        if spell_node_role_arn in conf_map.data["mapRoles"]:
            click.echo("Spell permissions already in the cluster! Skipping.")
        else:
            conf_map.data["mapRoles"] += eks_cluster_aws_auth_template.format(rolearn=spell_node_role_arn)
            kube_api.replace_namespaced_config_map("aws-auth", "kube-system", conf_map)
            click.echo("Spell permissions granted!")
    except Exception as e:
        raise ExitException(
            "Giving Spell permissions to the cluster failed. Please contact Spell Support. Error was {}".format(e),
        )


def add_eks_s3_permissions(cluster, aws_session):
    """Give EKS pods permission to load models from Spell's S3 bucket by creating special user"""
    # TODO(waldo): Should we create a Role that the Spell service account assumes
    # instead of creating a second user just for this?
    # Create SpellReadS3 IAM User
    cluster_utils.echo_delimiter()
    iam = aws_session.resource("iam")
    policy_name = cluster["role_credentials"]["aws"]["read_policy"]
    suffix = policy_name.split("-")[-1]  # Get the ID suffix off the policy name
    user_name = "SpellReadS3User-{}".format(suffix)
    click.echo("Creating and configuring {} IAM user...".format(user_name))
    try:
        existing_users = [u for u in iam.users.all() if user_name == u.name]
        if len(existing_users) > 0:
            user = existing_users[0]
            click.echo("Existing {} user found".format(user_name))
        else:
            user = iam.create_user(UserName=user_name)
            click.echo("New {} user created".format(user_name))
        if len([p for p in user.attached_policies.all() if p.policy_name == policy_name]) == 0:
            matching_policies = [p for p in iam.policies.all() if p.policy_name == policy_name]
            if len(matching_policies) != 1:
                raise ExitException(
                    "Found unexpected number of policies named " "'{}': {}".format(policy_name, len(matching_policies))
                )
            s3_read_policy = matching_policies[0]
            user.attach_policy(PolicyArn=s3_read_policy.arn)
            click.echo("Policy {} attached to user".format(policy_name))
        for existing_access_key in user.access_keys.all():
            existing_access_key.delete()
        access_key = user.create_access_key_pair()
        iam_access_key, iam_secret_key = access_key.access_key_id, access_key.secret_access_key
        click.echo("{} user new access key pair created".format(user_name))
    except Exception as e:
        raise ExitException(
            "Unable to create and attach IAM policies. Please contact Spell support. Error: {}".format(e)
        )

    # Create secrets on cluster with SpellReadS3 IAM user
    cluster_utils.echo_delimiter()
    click.echo("Setting secrets on the cluster...")
    try:
        secret_yaml = generate_eks_cluster_secret_yaml(iam_access_key, iam_secret_key)
        with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+") as f:
            f.write(secret_yaml)
            f.flush()
            subprocess.check_call(("kubectl", "apply", "--filename", f.name))
        click.echo("Cluster Secrets set up!")
    except Exception as e:
        raise ExitException("Unable to apply secrets to cluster. Error: {}".format(e))


def eks_configure_k8s(
    ctx,
    session,
    cluster,
    eks_cluster_name,
    is_public: bool,
    support_runs: bool = False,
    is_encrypted: bool = False,
) -> (str, bool):
    optional_features = cluster_utils.make_optional_serving_features(cluster)

    click.echo("Giving Spell permissions to the cluster...")
    arn = ctx.obj["client"].get_spell_node_role()
    eks_add_arn(session.profile_name, cluster, arn, kube_cluster_name=eks_cluster_name)

    cluster_utils.create_namespace("serving")
    add_eks_s3_permissions(cluster, session)

    if is_encrypted:  # Add service mesh
        cluster_utils.add_consul(cluster)
        optional_features["mTLS"] = True

    # Set up ClusterAutoscaling
    cluster_utils.echo_delimiter()
    click.echo("Setting up Cluster Autoscaling...")
    try:
        ca_yaml = generate_eks_cluster_autoscaler_yaml(eks_cluster_name)
        with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+") as f:
            f.write(ca_yaml)
            f.flush()
            subprocess.check_call(("kubectl", "apply", "--filename", f.name))
        click.echo("Cluster Autoscaling set up!")
    except Exception as e:
        optional_features["autoscaling"] = False
        logger.warn("Cluster Autoscaling failed to set up. Autoscaling will not be enabled! Error was: {}".format(e))

    # Set up metrics-server
    cluster_utils.echo_delimiter()
    click.echo("Setting up metrics-server for HPA...")
    try:
        subprocess.check_call(
            (
                "kubectl",
                "apply",
                "--filename",
                "https://github.com/kubernetes-sigs/metrics-server/releases/download/v0.3.6/components.yaml",
            ),
        )
        click.echo("metrics-server set up!")
    except Exception as e:
        logger.error("metrics-server failed to set up. Error was: {}".format(e))

    # Set up NVIDIA Device Plugin
    cluster_utils.echo_delimiter()
    try:
        add_nvidia_device_driver()
    except Exception as e:
        optional_features["gpu"] = False
        logger.error(
            "NVIDIA GPU Device Plugin failed to set up. GPU serving will not be enabled! Error was: {}".format(e)
        )

    # Give Spell permissions to the cluster
    cluster_utils.echo_delimiter()
    click.echo("Giving Spell permissions to the cluster...")
    add_eks_auth(ctx.obj["client"])

    add_eks_s3_permissions(cluster, session)

    # Create the serving priorityclass
    cluster_utils.echo_delimiter()
    cluster_utils.create_serving_priorityclass()

    # Add Ambassador to the 'ambassador' namespace
    cluster_utils.echo_delimiter()
    cluster_utils.add_ambassador(cluster, is_public)

    # Add kube-Prometheus to the monitoring stack.
    cluster_utils.add_monitoring_stack(cluster)

    cluster_utils.add_efk_stack(ctx, support_runs)

    return optional_features


def wait_for_cloudformation_stack_status(aws_profile, cloudformation_stack_name, session, state):
    cmd = [
        "aws",
        "cloudformation",
        "describe-stacks",
        "--profile",
        aws_profile,
        "--stack-name",
        cloudformation_stack_name,
        "--output",
        "json",
    ]
    for i in range(10):
        try:
            output = subprocess.check_output(cmd)
        except subprocess.CalledProcessError:
            raise ExitException(
                "Failed to run `{}`. Please clean up the cloudformation stack and try again.".format(" ".join(cmd))
            )
        try:
            stack_obj = json.loads(output)
        except json.JSONDecodeError:
            raise ExitException(
                (
                    "Failed to parse output of `{}`." "\n{}\n" "Please clean up the cloudformation stack and try again."
                ).format(" ".join(cmd), output)
            )
        if len(stack_obj["Stacks"]) == 1:
            if stack_obj["Stacks"][0]["StackStatus"] == state:
                return True
            else:
                click.echo(
                    "Cloudwatch stack in state {}, waiting for {}, sleeping 10s".format(
                        stack_obj["Stacks"][0]["StackStatus"], state
                    )
                )
                time.sleep(10)
    return False


def create_eks_cluster(
    cluster,
    aws_profile,
    eks_cluster_name,
    session,
    nodes_min,
    nodes_max,
    node_volume_size,
    zones,
):
    """
    Create a new EKS cluster for model serving using your current
    AWS credentials. Your profile must have privileges to EC2, EKS, IAM, and
    CloudFormation. You need to have both `kubectl` and `eksctl` installed.
    This command will walk you through the process and allows users to specify
    networking and security options.

    NOTE: This can take a very long time (15-20 minutes), so make sure you are on a
    computer with a stable Internet connection and power before beginning.
    """

    cmd = [
        "eksctl",
        "create",
        "cluster",
        "--profile",
        aws_profile,
        "--name",
        eks_cluster_name,
        "--region",
        cluster["networking"]["aws"]["region"],
        "--version",
        "1.18",
        "--nodegroup-name",
        "default",
        "--node-type",
        EKS_DEFAULT_NODEGROUP_TYPE,
        "--nodes-min",
        str(nodes_min),
        "--nodes-max",
        str(nodes_max),
        "--node-volume-size",
        str(node_volume_size),
        "--asg-access",
    ]
    vpc_subnets = cluster["networking"]["aws"]["subnets"]
    if zones:
        # filter out subnets in the wrong zones
        ec2 = session.resource("ec2")
        vpc_subnets = [subnet for subnet in vpc_subnets if ec2.Subnet(subnet).availability_zone in zones]
    cmd.append("--vpc-public-subnets={}".format(",".join(vpc_subnets)))

    try:
        click.echo("Creating the cluster. This can take a while...")
        subprocess.check_call(cmd)
        click.echo("Cluster created!")
    except subprocess.CalledProcessError:
        click.echo("Cluster creation failed. Waiting for cluster to be deleted...")
        cloudformation_stack_name = "eksctl-{}-cluster".format(eks_cluster_name)
        wait_for_cloudformation_stack_status(aws_profile, cloudformation_stack_name, session, "ROLLBACK_COMPLETE")

        click.echo("Rollback complete, deleting cloudformation stack...")
        cmd = [
            "aws",
            "cloudformation",
            "delete-stack",
            "--profile",
            aws_profile,
            "--region",
            session.region_name,
            "--stack-name",
            cloudformation_stack_name,
        ]
        try:
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError:
            raise ExitException(
                "Failed to run `{}`. Please clean up the cloudformation stack and try again.".format(" ".join(cmd))
            )
        click.echo("CloudFormation stack deletion initiated.")
        raise ExitException(
            "Failed to run `eksctl create cluster`. Make sure it's installed correctly and "
            "your inputs are valid. Error details are above in the `eksctl` output."
        )


def eks_add_arn(aws_profile, cluster, arn, kube_cluster_name=None):
    if kube_cluster_name:
        eks_cluster_name = kube_cluster_name
    else:
        eks_cluster_name = extract_eksctl_cluster_name(cluster.get("serving_cluster_name"))
    check = subprocess.run(
        [
            "eksctl",
            "--profile",
            aws_profile,
            "get",
            "iamidentitymapping",
            "--cluster",
            eks_cluster_name,
            "--region",
            cluster["networking"]["aws"]["region"],
            "--arn",
            arn,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if check.returncode != 0:
        try:
            subprocess.check_call(
                [
                    "eksctl",
                    "--profile",
                    aws_profile,
                    "create",
                    "iamidentitymapping",
                    "--cluster",
                    eks_cluster_name,
                    "--region",
                    cluster["networking"]["aws"]["region"],
                    "--arn",
                    arn,
                    "--group",
                    "system:masters",
                ]
            )
        except Exception as e:
            raise ExitException(str(e))


def eks_check_node_group_perms(cluster, aws_session, operation):
    """Check IAM permissions for K8s API permissions for this user before
    doing a node-group operation

    Args:
        operation: One of ["create", "scale", "delete"]
    """

    import botocore

    # Check if the user has IAM permissions to create a node-group
    eks = aws_session.client("eks")
    autoscaling = aws_session.client("autoscaling")  # see eks_scale_nodegroup
    try:
        if operation == "create":
            eks.create_nodegroup(
                clusterName=cluster["serving_cluster_name"],
                nodegroupName="fake",
                nodeRole="fake",
                subnets=["fake"],
            )
        elif operation == "scale":
            autoscaling.update_auto_scaling_group(AutoScalingGroupName="fake")
        elif operation == "delete":
            eks.delete_nodegroup(
                clusterName=cluster["serving_cluster_name"],
                nodegroupName="fake",
            )
    except botocore.exceptions.ClientError as e:
        if "AccessDeniedException" == e.response.get("Error").get("Code"):
            raise ExitException(
                f"The AWS profile {aws_session.profile_name} does not have AWS permissions to {operation} node groups"
            )

    # Check if the user can create new Node objects in the Kubernetes API
    # (required to register/deregistry new node-group into EKS cluster)
    if operation == "create" or operation == "delete":
        try:
            resp = subprocess.run(
                ("kubectl", "auth", "can-i", "create", "node"),
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )
            if "yes" not in str(resp.stdout):
                raise ExitException(
                    f"The AWS profile {aws_session.profile_name} does not have permission"
                    + " to update the Kubernetes cluster;"
                    + " Has `spell kube-cluster add-user` been run?"
                )

        except subprocess.CalledProcessError:
            raise ExitException(
                f"The AWS profile {aws_session.profile_name} does not have permission to access the Kubernetes cluster;"
                + " Has `spell kube-cluster add-user` been run?"
            )


def _convert_flag_value(val):
    if isinstance(val, (bool)):
        return val
    else:
        return str(val)


def eks_add_nodegroup(config: dict, cluster, aws_profile):
    config = {k: _convert_flag_value(v) for k, v in config.items()}
    subprocess.check_call(
        [
            "eksctl",
            "create",
            "nodegroup",
            "--managed",
            "--profile",
            aws_profile,
            "--region",
            cluster["networking"]["aws"]["region"],
            "--cluster",
            cluster["serving_cluster_short_name"],
            "--name",
            config["ng_name"],
            "--instance-types",
            config["instance_type"],
            "--nodes-min",
            config["min_nodes"],
            "--nodes-max",
            config["max_nodes"],
            "--node-volume-size",
            config["disk_size"],
            "--spot" if config["spot"] else "",
            "--node-labels",
            f"spell_serving_group={config['ng_name']}",
        ]
    )


def eks_scale_nodegroup(session, cluster, node_group_name, min_nodes, max_nodes):
    # EKS has no utility to scale the min/max nodes of a nodegroup. Their
    # existing `scale` command only allows you to adjust the desired count.
    # This implementation is modeled after a workaround from the following
    # issue comment:
    # https://github.com/weaveworks/eksctl/issues/809#issuecomment-546278651
    eks_cluster_name = extract_eksctl_cluster_name(cluster.get("serving_cluster_name"))

    click.echo("Retrieving autoscaling groups...")
    autoscaling = session.client("autoscaling")
    try:
        # Checks if it has the serving group name tagged as well as the eks cluster name
        def asg_has_matching_tags(asg):
            has_node_group_name = False
            has_eks_cluster_name = False
            for tag in group["Tags"]:
                key = tag.get("Key", "")
                value = tag.get("Value", "")
                if key.endswith("nodegroup-name") and value == node_group_name:
                    has_node_group_name = True
                if key.endswith("cluster-name") and value == eks_cluster_name:
                    has_eks_cluster_name = True
            return has_node_group_name and has_eks_cluster_name

        matching_asgs = []
        paginator = autoscaling.get_paginator("describe_auto_scaling_groups")
        for resp in paginator.paginate():
            for group in resp["AutoScalingGroups"]:
                if asg_has_matching_tags(group):
                    matching_asgs.append(group)

    except Exception as e:
        raise ExitException(str(e))

    if len(matching_asgs) == 0:
        raise ExitException("No autoscaling group found for serving group {}".format(node_group_name))
    if len(matching_asgs) > 1:
        raise ExitException("Not sure which of {} is the correct AWS autoscaling group".format(matching_asgs))

    click.echo("Updating autoscaling group...")
    try:
        autoscaling.update_auto_scaling_group(
            AutoScalingGroupName=matching_asgs[0]["AutoScalingGroupName"],
            MinSize=min_nodes,
            MaxSize=max_nodes,
        )
    except Exception as e:
        raise ExitException(str(e))


def eks_delete_nodegroup(aws_profile, kube_cluster_name, node_group_name):
    try:
        subprocess.check_call(
            [
                "eksctl",
                "delete",
                "nodegroup",
                "--profile",
                aws_profile,
                "--cluster",
                kube_cluster_name,
                "--name",
                node_group_name,
            ]
        )
    except Exception as e:
        raise ExitException(str(e))


# Returns the new buckets name
def create_bucket(s3, region, cluster_name):
    from botocore.exceptions import ClientError

    cluster_utils.echo_delimiter()

    bucket_name = click.prompt(
        "Please enter a name for the S3 Bucket Spell will create for run outputs",
        default="spell-{}".format(cluster_name.replace("_", "-").lower()),
    ).strip()
    if not bucket_name.islower():
        click.echo("AWS does not support capital letters in the bucket name")
        return create_bucket(s3, region, cluster_name)
    if "_" in bucket_name:
        click.echo("AWS does not allow underscores in the bucket name")
        return create_bucket(s3, region, cluster_name)

    try:
        if region == "us-east-1":
            bucket = s3.create_bucket(Bucket=bucket_name, ACL="private")
        else:
            bucket = s3.create_bucket(
                Bucket=bucket_name,
                ACL="private",
                CreateBucketConfiguration={"LocationConstraint": region},
            )

    except ClientError as e:
        click.echo("ERROR: Unable to create bucket. AWS error: {}".format(e))
        return create_bucket(s3, region, cluster_name)

    try:
        add_bucket_lifecycle_rule(bucket)
    except ClientError as e:
        click.echo(
            "WARNING: Unable to apply lifecycle rule to bucket. "
            "You can run 'cluster update' to try this again: {}".format(e)
        )

    try:
        add_bucket_encryption_setting(s3, bucket_name)
    except ClientError as e:
        click.echo(
            "WARNING: Unable to turn on bucket encryption. "
            "You can run 'cluster update' to try this again: {}".format(e)
        )

    try:
        add_bucket_versioning(bucket)
    except ClientError as e:
        click.echo(
            "WARNING: Unable to turn on bucket versioning. "
            "You can run 'cluster update' to try this again: {}".format(e)
        )

    click.echo("Created your new bucket {}!".format(bucket_name))

    return bucket_name


# Add lifecycle rule to move all objects to Intelligent Tiering which is cheaper than
# standard object storage. This should have no customer facing downsides, but if objects
# aren't accessed regularly AWS will put them in cheaper storage until they are used again.
# The rule moves objects after 30 days, the minimum possible.
def add_bucket_lifecycle_rule(bucket):
    bucket.LifecycleConfiguration().put(
        LifecycleConfiguration={
            "Rules": [
                {
                    "ID": BUCKET_LIFECYCLE_RULE_NAME,
                    "Filter": {"Prefix": ""},
                    "Status": "Enabled",
                    "Transitions": [{"Days": 30, "StorageClass": "INTELLIGENT_TIERING"}],
                }
            ]
        }
    )


def has_bucket_lifecycle_rule(bucket):
    from botocore.exceptions import ClientError

    try:
        return any([rule["ID"] == BUCKET_LIFECYCLE_RULE_NAME for rule in bucket.LifecycleConfiguration().rules])
    except ClientError as e:
        if "NoSuchLifecycleConfiguration" not in str(e):
            raise ExitException("Error checking bucket {} lifecycle rules: {}".format(bucket.name, e))
        else:
            return False


def add_bucket_encryption_setting(s3, bucket_name):
    rule = {"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}
    s3.meta.client.put_bucket_encryption(
        Bucket=bucket_name,
        ServerSideEncryptionConfiguration={"Rules": [rule]},
    )


def has_bucket_encryption_setting(s3, bucket_name):
    from botocore.exceptions import ClientError

    # resp takes the form if it exists
    # { ... 'ServerSideEncryptionConfiguration': {'Rules': [{"Apply...": {"SSEAlgorithm": "AES256"}}]}}
    # but this throws if it doesn't exist
    try:
        resp = s3.meta.client.get_bucket_encryption(Bucket=bucket_name)
    except ClientError as e:
        if "ServerSideEncryptionConfigurationNotFoundError" in str(e):
            return False
        raise e

    rules = resp.get("ServerSideEncryptionConfiguration", {}).get("Rules")
    if not rules:
        return False
    return any([r.get("ApplyServerSideEncryptionByDefault") == {"SSEAlgorithm": "AES256"} for r in rules])


def add_bucket_versioning(bucket):
    bucket.Versioning().enable()


def has_bucket_versioning(bucket):
    return bucket.Versioning().status == "Enabled"


def create_vpc(ec2, cluster_name):
    from botocore.exceptions import BotoCoreError, ClientError

    cluster_utils.echo_delimiter()
    click.echo("Creating new VPC")

    # Create VPC
    cidr = "10.0.0.0/16"
    try:
        vpc = ec2.create_vpc(CidrBlock=cidr)
    except (ClientError, BotoCoreError) as e:
        raise ExitException("Unable to create VPC. AWS error: {}".format(e))
    for i in range(5):
        try:
            vpc.wait_until_available()
            vpc.create_tags(Tags=[{"Key": "Name", "Value": "Spell-{}".format(cluster_name)}])
            vpc.modify_attribute(EnableDnsSupport={"Value": True})
            vpc.modify_attribute(EnableDnsHostnames={"Value": True})
            break
        except (ClientError, BotoCoreError) as e:
            if i == 4:
                raise ExitException("Unable to create VPC. AWS error: {}".format(e))
            else:
                time.sleep(1)

    click.echo("Created a new VPC with ID {}!".format(vpc.id))
    # Create subnets
    zones = [z["ZoneName"] for z in ec2.meta.client.describe_availability_zones()["AvailabilityZones"]]
    zones = zones[:8]  # Max at 8 since we use at most 3 bits of the cidr range for subnets
    subnet_bits = 3
    if len(zones) <= 4:
        subnet_bits = 2
    if len(zones) <= 2:
        subnet_bits = 1
    cidr_generator = ipaddress.ip_network(cidr).subnets(subnet_bits)
    subnets = []
    for zone in zones:
        subnet_cidr = str(next(cidr_generator))
        try:
            subnet = vpc.create_subnet(AvailabilityZone=zone, CidrBlock=subnet_cidr)
            # By default give instances launched in this subnet a public ip
            resp = subnet.meta.client.modify_subnet_attribute(SubnetId=subnet.id, MapPublicIpOnLaunch={"Value": True})
            if resp["ResponseMetadata"]["HTTPStatusCode"] != 200:
                click.echo(
                    "WARNING: Unable to set subnet {} to launch instances with "
                    "public ip address. This is required for Spell.".format(subnet.id)
                )
            subnets.append(subnet.id)
            click.echo("Created a new subnet {} in your new VPC in availability-zone {} ".format(subnet.id, zone))
        except BotoCoreError as e:
            click.echo(e)
    if len(subnets) == 0:
        raise ExitException("Unable to make any subnets in your new VPC. Contact Spell for support")

    # Create internet gateway
    gateway = ec2.create_internet_gateway()
    resp = vpc.attach_internet_gateway(InternetGatewayId=gateway.id)
    if resp["ResponseMetadata"]["HTTPStatusCode"] != 200:
        raise ExitException("Failed to attach internet gateway {} to vpc".format(gateway.id))
    route_tables = list(vpc.route_tables.all())
    if len(route_tables) == 0:
        raise ExitException("No route table found on VPC, unable to set route for internet gateway")
    route_table = route_tables[0]
    route_table.create_route(DestinationCidrBlock="0.0.0.0/0", GatewayId=gateway.id)
    click.echo("Created internet gateway {} for new VPC".format(gateway.id))

    return vpc


# Make sure the VPC exists and has subnets
def verify_existing_vpc(ec2, vpc_id):
    vpc = ec2.Vpc(vpc_id)
    if len(list(vpc.subnets.all())) == 0:
        raise ExitException(
            "VPC {} has no subnets. Subnets are required for creating " "spell worker machines".format(vpc_id)
        )
    if not click.confirm("Found vpc {} with subnets {}. Use these?".format(vpc_id, list(vpc.subnets.all()))):
        raise ExitException("Exiting")
    return vpc


def create_security_group(ec2, vpc, spell_client):
    from botocore.exceptions import BotoCoreError

    trusted_cidrs = spell_client.get_trusted_cidrs()
    try:
        security_group = vpc.create_security_group(
            GroupName="Spell-Ingress",
            Description="Allows the Spell API SSH and Docker access to worker machines",
        )
        for cidr_block in trusted_cidrs:
            for port in WORKER_OPEN_PORTS:
                security_group.authorize_ingress(CidrIp=cidr_block, FromPort=port, ToPort=port, IpProtocol="tcp")
        security_group.authorize_ingress(
            IpPermissions=[
                {
                    "IpProtocol": "-1",
                    "FromPort": 0,
                    "ToPort": 65355,
                    "UserIdGroupPairs": [{"GroupId": security_group.id, "VpcId": security_group.vpc_id}],
                }
            ]
        )
        click.echo("Successfully created security group {}".format(security_group.id))
        return security_group
    except BotoCoreError as e:
        raise ExitException("Unable to create new security group in VPC. AWS error: {}".format(e))


def create_role(iam, bucket_name, spell_aws_arn):
    """
    spell_aws_arn: The created external role ARN (SpellAccess-*)
    will use this to determine which AWS accounts can assume the role

    Returns a tuple of
    role_arn: the full ARN of the IAM role
    external_id: the external_id required to assume this role
    read_policy: the name of the s3 policy that allows read access to selected buckets
    """

    from botocore.exceptions import ClientError

    cluster_utils.echo_delimiter()
    click.echo("Creating new IAM role")

    write_bucket_arn = "arn:aws:s3:::{}".format(bucket_name)
    write_bucket_objects_arn = "arn:aws:s3:::{}/*".format(bucket_name)

    suffix = str(random.randint(10 ** 6, 10 ** 7))
    read_policy = "SpellReadS3-{}".format(suffix)
    policies = {
        "SpellEC2-{}".format(suffix): [
            {
                "Sid": "EC2",
                "Effect": "Allow",
                "Action": [
                    "s3:GetAccountPublicAccessBlock",
                    "s3:HeadBucket",
                    "ec2:DescribeInstances",
                    "ec2:DescribeImages",
                    "ec2:DescribeVolumes",
                    "ec2:DescribeSpotInstanceRequests",
                    "ec2:RequestSpotInstances",
                    "ec2:RunInstances",
                    "ec2:CreateKeyPair",
                    "ec2:DeleteKeyPair",
                    "ec2:CreateTags",
                    "ec2:DescribeVolumesModifications",
                    "ec2:ModifyVolume",
                    "ec2:AttachVolume",
                ],
                "Resource": "*",
            },
            {
                "Sid": "EC2Terminate",
                "Effect": "Allow",
                "Action": ["ec2:TerminateInstances", "ec2:DeleteVolume"],
                "Resource": "*",
                "Condition": {"StringEquals": {"ec2:ResourceTag/spell-machine": "true"}},
            },
        ],
        read_policy: {
            "Sid": "ReadS3",
            "Effect": "Allow",
            "Action": [
                "s3:ListBucketByTags",
                "s3:GetLifecycleConfiguration",
                "s3:GetBucketTagging",
                "s3:GetInventoryConfiguration",
                "s3:GetObjectVersionTagging",
                "s3:ListBucketVersions",
                "s3:GetBucketLogging",
                "s3:ListBucket",
                "s3:GetAccelerateConfiguration",
                "s3:GetBucketPolicy",
                "s3:GetObjectVersionTorrent",
                "s3:GetObjectAcl",
                "s3:GetEncryptionConfiguration",
                "s3:GetBucketRequestPayment",
                "s3:GetObjectVersionAcl",
                "s3:GetObjectTagging",
                "s3:GetMetricsConfiguration",
                "s3:GetBucketPublicAccessBlock",
                "s3:GetBucketPolicyStatus",
                "s3:ListBucketMultipartUploads",
                "s3:GetBucketWebsite",
                "s3:GetBucketVersioning",
                "s3:GetBucketAcl",
                "s3:GetBucketNotification",
                "s3:GetReplicationConfiguration",
                "s3:ListMultipartUploadParts",
                "s3:GetObject",
                "s3:GetObjectTorrent",
                "s3:GetBucketCORS",
                "s3:GetAnalyticsConfiguration",
                "s3:GetObjectVersionForReplication",
                "s3:GetBucketLocation",
                "s3:GetObjectVersion",
            ],
            "Resource": [write_bucket_arn, write_bucket_objects_arn],
        },
        "SpellWriteS3-{}".format(suffix): {
            "Sid": "WriteS3",
            "Effect": "Allow",
            "Action": [
                "s3:PutAnalyticsConfiguration",
                "s3:PutAccelerateConfiguration",
                "s3:DeleteObjectVersion",
                "s3:ReplicateTags",
                "s3:RestoreObject",
                "s3:ReplicateObject",
                "s3:PutEncryptionConfiguration",
                "s3:DeleteBucketWebsite",
                "s3:AbortMultipartUpload",
                "s3:PutBucketTagging",
                "s3:PutLifecycleConfiguration",
                "s3:PutObjectTagging",
                "s3:DeleteObject",
                "s3:PutBucketVersioning",
                "s3:DeleteObjectTagging",
                "s3:PutMetricsConfiguration",
                "s3:PutReplicationConfiguration",
                "s3:PutObjectVersionTagging",
                "s3:DeleteObjectVersionTagging",
                "s3:PutBucketCORS",
                "s3:PutInventoryConfiguration",
                "s3:PutObject",
                "s3:PutBucketNotification",
                "s3:PutBucketWebsite",
                "s3:PutBucketRequestPayment",
                "s3:PutBucketLogging",
                "s3:ReplicateDelete",
            ],
            "Resource": [write_bucket_arn, write_bucket_objects_arn],
        },
    }

    external_id = str(random.randint(10 ** 8, 10 ** 9))
    assume_role_policy = json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": spell_aws_arn},
                    "Action": "sts:AssumeRole",
                    "Condition": {"StringEquals": {"sts:ExternalId": external_id}},
                }
            ],
        }
    )

    try:
        role_name = "SpellAccess-{}".format(suffix)
        role = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=assume_role_policy,
            Description="Grants Spell EC2 and S3 access",
        )
    except ClientError as e:
        raise ExitException("Unable to create new IAM role. AWS error: {}".format(e))

    try:
        for name, statement in policies.items():
            iam_policy = iam.create_policy(
                PolicyName=name,
                PolicyDocument=json.dumps({"Version": "2012-10-17", "Statement": statement}),
            )
            role.attach_policy(PolicyArn=iam_policy.arn)
    except ClientError as e:
        raise ExitException("Unable to create and attach IAM policies. AWS error: {}".format(e))

    click.echo("Successfully created IAM role {}".format(role_name))
    return role.arn, external_id, read_policy


def get_session(profile, message=""):
    try:
        import boto3
        import botocore
    except ImportError:
        click.echo("Please pip install boto3 and rerun this command")
        return None
    try:
        session = boto3.session.Session(profile_name=profile)
    except botocore.exceptions.BotoCoreError as e:
        click.echo("Failed to set profile {} with error: {}".format(profile, e))
        return None
    if message:
        click.echo(message)
    if not click.confirm(
        "All of this will be done with your AWS profile '{}' which has "
        "Access Key ID '{}' and region '{}' - continue?".format(
            profile, session.get_credentials().access_key, session.region_name
        )
    ):
        return None
    return session


def add_s3_bucket(spell_client, aws_session, cluster, bucket_name, cross_account):
    """
    This command adds a cloud storage bucket to SpellFS, which enables interaction with the bucket objects
    via ls, cp, and mounts. It will also add bucket read permissions to the AWS role associated with the
    cluster.

    NOTE: This command uses your AWS credentials, found in ~/.aws/credentials to create the necessary
    AWS resources for Spell to access the remote storage bucket. Your AWS credentials will
    need permission to setup these resources.
    """
    cluster_name = cluster["name"]

    import botocore
    from botocore.exceptions import BotoCoreError

    # Set up clients with the provided profile
    try:
        s3 = aws_session.resource("s3")
        iam = aws_session.resource("iam")
    except BotoCoreError as e:
        raise ExitException("Failed to get clients with profile {}: {}".format(aws_session.profile_name, e))

    # Get all buckets
    click.echo("Retrieving buckets...")
    all_buckets = [bucket.name for bucket in s3.buckets.all()]

    # Prompt for bucket name
    if bucket_name is None:
        bucket_names = [bucket.name for bucket in s3.buckets.all()]
        for bucket in bucket_names:
            click.echo("- {}".format(bucket))
        bucket_name = click.prompt("Please choose a bucket")

    # Check if bucket is public if the bucket name is not one of the returned
    bucket_is_public = False
    if bucket_name not in all_buckets:
        # Set up an anonymous client
        anon_s3 = aws_session.resource("s3", config=botocore.client.Config(signature_version=botocore.UNSIGNED))
        try:
            list(anon_s3.Bucket(bucket_name).objects.limit(count=1))
        except botocore.exceptions.ClientError:
            if not cross_account:
                click.echo(f"Bucket {bucket_name} is not accessible")
                return
            bucket_is_public = False
        else:
            if cross_account:
                click.echo(
                    f"Bucket {bucket_name} is public, but the --cross-account flag is set. To "
                    f"proceed with adding this bucket to the cluster, remove this flag."
                )
                return
            bucket_is_public = True

    # Skip IAM role management logic if bucket is public
    if bucket_is_public:
        click.echo("Bucket {} is public, no IAM updates required.".format(bucket_name))
        with api_client_exception_handler():
            spell_client.add_bucket(bucket_name, cluster_name, "s3", cross_account=cross_account)
        click.echo("Bucket {} has been added to cluster {}!".format(bucket_name, cluster_name))
        return

    # Add bucket read permissions to policy
    policy, policy_document = extract_normalized_read_policy(iam, cluster)
    bucket_arn = "arn:aws:s3:::{}".format(bucket_name)
    if (
        policy_document["Statement"][0]["Resource"] != "*"
        and bucket_arn not in policy_document["Statement"][0]["Resource"]
    ):
        policy_document["Statement"][0]["Resource"] += [bucket_arn, bucket_arn + "/*"]
        update_iam_policy(policy, policy_document)
    else:
        click.echo("Policy {} has permissions to access {}".format(policy.arn, bucket_arn))

    # Register new bucket to cluster in API
    with api_client_exception_handler():
        spell_client.add_bucket(bucket_name, cluster_name, "s3", cross_account=cross_account)
    click.echo("Bucket {} has been added to cluster {}!".format(bucket_name, cluster_name))


def remove_s3_bucket(spell_client, aws_session, cluster, bucket_name):
    """
    This command removes an S3 cloud storage bucket from SpellFS.
    It will also remove bucket read permissions from the AWS role associated with the cluster.

    NOTE: This command uses your AWS credentials, found in ~/.aws/credentials to create the necessary
    AWS resources for Spell to access the remote storage bucket. Your AWS credentials will
    need permission to setup these resources.
    """
    cluster_name = cluster["name"]

    from botocore.exceptions import BotoCoreError

    # Set up clients with the provided profile
    try:
        iam = aws_session.resource("iam")
    except BotoCoreError as e:
        raise ExitException("Failed to get clients with profile {}: {}".format(aws_session.profile_name, e))

    # List existing buckets for cluster
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

    # Update cluster role policy
    policy, policy_document = extract_normalized_read_policy(iam, cluster)
    bucket_arn = "arn:aws:s3:::{}".format(bucket_name)
    if policy_document["Statement"][0]["Resource"] != "*" and bucket_arn in policy_document["Statement"][0]["Resource"]:
        policy_document["Statement"][0]["Resource"] = [
            r for r in policy_document["Statement"][0]["Resource"] if r not in [bucket_arn, bucket_arn + "/*"]
        ]
        update_iam_policy(policy, policy_document)
    else:
        click.echo(f"Policy {policy.arn} did not require updating")

    # Remove bucket from cluster in API
    with api_client_exception_handler():
        spell_client.remove_bucket(bucket_name, cluster_name, "s3")
    click.echo(f"Bucket {bucket_name} has been removed from cluster {cluster_name}!")


def extract_normalized_read_policy(iam, cluster):
    """
    Helper method to get the policy, policy_document from the input cluster's "read_policy"
    This will ensure that it's an array of exactly ONE statement.
    """
    policy_name = cluster["role_credentials"]["aws"]["read_policy"]
    policies = [p for p in iam.policies.all() if p.policy_name == policy_name]
    if len(policies) != 1:
        raise ExitException("Found {} policies with name {}".format(len(policies), policy_name))
    policy = policies[0]
    policy_document = policy.default_version.document
    statements = policy_document["Statement"]
    if isinstance(statements, list):
        if len(statements) != 1:
            raise ExitException(
                "Unexpected number of statements in policy document {}, "
                "expecting one. Statements:\n{}".format(policy_name, statements)
            )
            return
    else:
        policy_document["Statement"] = [statements]
    return policy, policy_document


def update_iam_policy(policy, policy_document):
    click.echo(f"Creating new version of policy {policy.arn}...")
    previous_version = policy.default_version
    policy.create_version(PolicyDocument=json.dumps(policy_document), SetAsDefault=True)
    click.echo(f"Created new version of policy {policy.arn}")
    previous_version.delete()
    click.echo(f"Pruned old version of policy {policy.arn}")


def set_custom_instance_role(spell_client, aws_session, cluster, iam_role_arn, instance_profile_arn):
    """
    This command sets a IAM Role that will be used as the IAM Instance Profile for all machines spun
    up within the cluster. The IAM Role must be match the IAM Instance Profile provided. More details
    here: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_switch-role-ec2_instance-profiles.html
    If there is already a custom instance profile on this cluster it will be replaced with the new one.

    NOTE: This command uses your AWS credentials, found in ~/.aws/credentials to create the necessary
    AWS resources for Spell to access the remote storage bucket. Your AWS credentials will
    need permission to setup these resources.
    """
    from botocore.exceptions import BotoCoreError

    # Set up clients with the provided profile
    try:
        iam = aws_session.resource("iam")
    except BotoCoreError as e:
        raise ExitException("Failed to get clients with profile {}: {}".format(aws_session.profile_name, e))

    # Add iam:passrole permissions to policy
    policy_name = cluster["role_credentials"]["aws"]["read_policy"].replace("SpellReadS3", "SpellEC2")
    policies = [p for p in iam.policies.all() if p.policy_name == policy_name]
    if len(policies) != 1:
        raise ExitException("Found {} policies with name {}".format(len(policies), policy_name))
    policy = policies[0]
    policy_document = policy.default_version.document
    statements = policy_document["Statement"]
    foundExistingStatement = False
    for statement in statements:
        if statement["Sid"] == "IAMPassRole":
            click.echo("Found existing IAMPassRole on policy: {}".format(policy.arn))
            foundExistingStatement = True
            if iam_role_arn:
                click.echo("Replacing it with new role...")
                statement["Resource"] = iam_role_arn
            else:
                click.echo("Removing it...")
                statements.remove(statement)
    if not foundExistingStatement and iam_role_arn:
        click.echo("Creating new IAMPassRole on policy {}".format(policy.arn))
        statements.append(
            {
                "Sid": "IAMPassRole",
                "Effect": "Allow",
                "Action": ["iam:PassRole"],
                "Resource": iam_role_arn,
            }
        )
    update_iam_policy(policy, policy_document)

    # Register new Instance Profile to cluster in API
    cluster_name = cluster["name"]
    with api_client_exception_handler():
        spell_client.set_instance_role_identifier(instance_profile_arn, cluster_name)
    if instance_profile_arn:
        click.echo(
            "Instance Profile {} (corresponding to IAM Role {}) has been added to cluster {}!".format(
                instance_profile_arn, iam_role_arn, cluster_name
            )
        )
    else:
        click.echo("Instance Profile has been UNSET from cluster {}!".format(cluster_name))


@click.pass_context
def add_ec_registry(ctx, repo_name, cluster, profile):
    """
    This command adds docker repository read permissions to the AWS role associated with the
    cluster.

    NOTE: This command uses your AWS credentials, found in ~/.aws/credentials to give
    Spell access to the docker images in a repository in your container registry.
    Your AWS credentials will need permission to setup these resources.
    """

    message = """This command will
    - Allow Spell to get authorization tokens to access your docker registry
    - If no repository is specified, list your repositories in the registry
    - Add read permissions for that repository to the IAM role associated with the cluster"""
    session = get_session(profile, message)
    if not session:
        return

    import botocore

    # Set up clients with the provided profile
    try:
        iam = session.resource("iam")
        ecr = session.client("ecr")
    except botocore.exceptions.BotoCoreError as e:
        click.echo("Failed to get clients with profile {}: {}".format(profile, e))
        return

    account_id = iam.CurrentUser().arn.split(":")[4]
    # Get all repositories
    all_repo_names = [repo["repositoryName"] for repo in ecr.describe_repositories()["repositories"]]
    valid_repo_name = repo_name in all_repo_names
    if repo_name and not valid_repo_name:
        click.echo("No repository named {} found".format(repo_name))
    # Get repos Spell has access to
    read_policy_name = cluster["role_credentials"]["aws"]["read_policy"]
    policy_name = read_policy_name.replace("SpellReadS3", "SpellReadECR")
    policies = [p for p in iam.policies.all() if p.policy_name == policy_name]
    read_resources = []
    repo_arn_prefix = "arn:aws:ecr:*:{}:repository/{}"
    if policies:
        policy = policies[0]
        current_policy_version = policy.default_version
        policy_document = current_policy_version.document
        read_resources = policy_document["Statement"]["Resource"]
        if repo_arn_prefix.format(account_id, repo_name) in read_resources:
            click.echo("Policy {} already has permissions to access {}".format(policy.arn, repo_name))
            return
    repo_names = [n for n in all_repo_names if repo_arn_prefix.format(account_id, n) not in read_resources]
    if not repo_names:
        click.echo("Spell already has access to all repos found in your AWS account")
        return
    # Prompt for repository name
    if not valid_repo_name:
        click.echo("Spell does not yet have access to the following repos found in your AWS account:")
        for repo in repo_names:
            click.echo("- {}".format(repo))
        while not valid_repo_name:
            repo_name = click.prompt("Please choose a repository")
            valid_repo_name = repo_name in repo_names
            if not valid_repo_name:
                if repo_name not in all_repo_names:
                    click.echo("No repository named {} found".format(repo_name))
                else:
                    click.echo("Spell already has permissions to access {}".format(repo_name))

    token_policy_name = read_policy_name.replace("SpellReadS3", "SpellAuthToken")
    roleArn = cluster["role_credentials"]["aws"]["role_arn"]
    role = iam.Role(roleArn.split("/")[-1])
    update_token_authorization_policy(iam, True, token_policy_name, role)

    # Add repository read permissions to policy
    repo_arn = repo_arn_prefix.format(account_id, repo_name)
    if len(policies) == 0:
        statement = {
            "Sid": "ReadECR",
            "Effect": "Allow",
            "Action": [
                "ecr:Get*",
                "ecr:List*",
                "ecr:Describe*",
                "ecr:BatchGetImage",
                "ecr:BatchCheckLayerAvailability",
            ],
            "Resource": [repo_arn],
        }
        try:
            policy = iam.create_policy(
                PolicyName=policy_name,
                PolicyDocument=json.dumps({"Version": "2012-10-17", "Statement": statement}),
            )
            role.attach_policy(PolicyArn=policy.arn)
            click.echo("You can now run using images from repository {}".format(repo_name))
        except botocore.exceptions.ClientError as e:
            raise ExitException(
                "Unable to create and attach read policy to repository {}." " AWS error: {}".format(repo_name, e)
            )
    else:
        if read_resources != "*" and repo_arn not in read_resources:
            read_resources.append(repo_arn)
            update_iam_policy(policy, policy_document)
            click.echo("Successfully added read permission to {}".format(repo_name))
        else:
            click.echo("Policy {} already has permissions to access {}".format(policy.arn, repo_name))


@click.pass_context
def delete_ec_registry(ctx, repo_name, cluster, profile):
    """
    This command removes docker repository read permissions to the AWS role associated with the
    cluster.

    NOTE: This command uses your AWS credentials, found in ~/.aws/credentials to remove
    Spell access to the docker images in a repository in your container registry.
    Your AWS credentials will need permission to setup these resources.
    """

    message = """This command will
    - Optionally disable Spell from getting authorization tokens to access your registry
    - If no repository is specified, list repositories Spell has access to
    - Remove read permissions for chosen repository from the IAM role associated with the cluster"""
    session = get_session(profile, message)
    if not session:
        return

    import botocore

    # Set up clients with the provided profile
    try:
        iam = session.resource("iam")
    except botocore.exceptions.BotoCoreError as e:
        click.echo("Failed to get clients with profile {}: {}".format(profile, e))
        return

    read_policy_name = cluster["role_credentials"]["aws"]["read_policy"]
    token_policy_name = read_policy_name.replace("SpellReadS3", "SpellAuthToken")
    roleArn = cluster["role_credentials"]["aws"]["role_arn"]
    role = iam.Role(roleArn.split("/")[-1])
    policy_name = read_policy_name.replace("SpellReadS3", "SpellReadECR")
    policies = [p for p in iam.policies.all() if p.policy_name == policy_name]
    if len(policies) == 0:
        click.echo("Spell does not have access to any docker repositories in your registry")
        return

    policy = policies[0]
    current_policy_version = policy.default_version
    policy_document = current_policy_version.document
    read_resources = policy_document["Statement"]["Resource"]
    # Get all repositories Spell has access to
    repo_names = [arn.split("/")[-1] for arn in read_resources]
    valid_repo_name = repo_name in repo_names
    if repo_name and not valid_repo_name:
        click.echo("Spell has no access to repository named {}".format(repo_name))
    # Prompt for repository name
    if not valid_repo_name:
        click.echo("Spell has access to the following repos:")
        for repo in repo_names:
            click.echo("- {}".format(repo))
        while not valid_repo_name:
            repo_name = click.prompt("Please choose a repository")
            valid_repo_name = repo_name in repo_names
            if not valid_repo_name:
                click.echo("Spell has no access to repository named {}".format(repo_name))

    # Remove repository read permissions to policy
    account_id = iam.CurrentUser().arn.split(":")[4]
    repo_arn = "arn:aws:ecr:*:{}:repository/{}".format(account_id, repo_name)
    if repo_arn in read_resources:
        read_resources.remove(repo_arn)
        if read_resources:
            update_iam_policy(policy, policy_document)
        else:
            role.detach_policy(PolicyArn=policy.arn)
            click.echo("Removing ECR policy and token generation policy as no remaining ECR repos are accessible.")
            policy.delete()
            update_token_authorization_policy(iam, False, token_policy_name, role)
        click.echo("Access to {} has been removed".format(repo_name))
    else:
        click.echo("Spell does not have permissions to access {}".format(repo_name))


def update_token_authorization_policy(iam, add, policy_name, role):
    from botocore.exceptions import ClientError

    matching_policies = [p for p in iam.policies.all() if p.policy_name == policy_name]
    if len(matching_policies) > 1:
        raise ExitException(
            "Found unexpected number of get authorization tokens policies named "
            "'{}': {}".format(policy_name, len(matching_policies))
        )
    if add:
        if len(matching_policies) == 1:
            return
        if not click.confirm(
            "Give Spell permission to get authorization tokens?"
            " Spell needs both token and read permission to pull private docker images from ECR."
        ):
            raise ExitException(
                "Spell cannot access docker registry without the ability to" " get authorization tokens"
            )
        statement = {
            "Sid": "GetAuthorizationToken",
            "Effect": "Allow",
            "Action": ["ecr:GetAuthorizationToken"],
            "Resource": "*",
        }
        try:
            iam_policy = iam.create_policy(
                PolicyName=policy_name,
                PolicyDocument=json.dumps({"Version": "2012-10-17", "Statement": statement}),
            )
            role.attach_policy(PolicyArn=iam_policy.arn)
        except ClientError as e:
            raise ExitException("Unable to create and attach token authorization policy. AWS error: {}".format(e))
    else:
        if len(matching_policies) == 1:
            policy = matching_policies[0]
            role.detach_policy(PolicyArn=policy.arn)
            policy.delete()


def update_aws_cluster(ctx, session, cluster):
    """
    This command idempotently makes sure that any updates needed since you ran cluster init are available.
    """
    from botocore.exceptions import BotoCoreError, ClientError

    spell_client = ctx.obj["client"]

    # Set up clients with the provided profile
    try:
        ec2 = session.resource("ec2")
        s3 = session.resource("s3")
    except BotoCoreError as e:
        click.echo("Failed to get clients with profile {}: {}".format(session.profile_name, e))
        return

    click.echo("Optimizing bucket configuration...")
    bucket_name = cluster["storage_uri"]
    bucket = s3.Bucket(bucket_name)
    try:
        if has_bucket_lifecycle_rule(bucket):
            click.echo("Bucket {} up to date with most cost effective configuration".format(bucket_name))
        else:
            add_bucket_lifecycle_rule(bucket)
            click.echo("Bucket {} updated to use most cost effective configuration".format(bucket_name))
    except ClientError as e:
        raise ExitException(
            "Unable to verify bucket {} has most cost effective configuration: {}".format(bucket_name, e)
        )
    try:
        if has_bucket_encryption_setting(s3, bucket_name):
            click.echo("Bucket {} encrypts new objects by default".format(bucket_name))
        else:
            add_bucket_encryption_setting(s3, bucket_name)
            click.echo("Bucket {} updated to encrypt new objects by default".format(bucket_name))
    except ClientError as e:
        raise ExitException("Unable to verify bucket {} encryption settings: {}".format(bucket_name, e))
    try:
        if has_bucket_versioning(bucket):
            click.echo("Bucket {} versioning enabled".format(bucket_name))
        else:
            add_bucket_versioning(bucket)
            click.echo("Bucket {} updated to enable versioning".format(bucket_name))
    except ClientError as e:
        raise ExitException("Unable to verify bucket {} has versioning enabled: {}".format(bucket_name, e))

    click.echo("Updating security group ingress rules...")
    security_group_id = cluster["networking"]["aws"]["security_group_id"]
    security_group = ec2.SecurityGroup(security_group_id)
    for port in WORKER_OPEN_PORTS:
        try:
            security_group.revoke_ingress(CidrIp="0.0.0.0/0", FromPort=port, ToPort=port, IpProtocol="tcp")
        except ClientError as e:
            if "InvalidPermission.NotFound" not in str(e):
                click.echo(str(e))
                return

    trusted_cidrs = spell_client.get_trusted_cidrs()
    for cidr_block in trusted_cidrs:
        for port in WORKER_OPEN_PORTS:
            try:
                security_group.authorize_ingress(CidrIp=cidr_block, FromPort=port, ToPort=port, IpProtocol="tcp")
            except ClientError as e:
                if "InvalidPermission.Duplicate" not in str(e):
                    click.echo(str(e))
                    return
    try:
        security_group.authorize_ingress(
            IpPermissions=[
                {
                    "IpProtocol": "-1",
                    "FromPort": 0,
                    "ToPort": 65355,
                    "UserIdGroupPairs": [{"GroupId": security_group.id, "VpcId": security_group.vpc_id}],
                }
            ]
        )
    except ClientError as e:
        if "InvalidPermission.Duplicate" not in str(e):
            click.echo(str(e))
            return

    # Ensure that DNS support and DNS hostnames are enabled so that pods can route
    # using AWS instance private DNS names. Note that both attributes are required
    # despite the fact that we don't depend on public DNS hostnames
    # https://docs.aws.amazon.com/vpc/latest/userguide/vpc-dns.html#vpc-dns-support
    click.echo("Updating VPC DNS configuration...")
    vpc_id = cluster["networking"]["aws"]["vpc_id"]
    vpc = ec2.Vpc(vpc_id)
    try:
        vpc.modify_attribute(EnableDnsSupport={"Value": True})
        vpc.modify_attribute(EnableDnsHostnames={"Value": True})
    except ClientError as e:
        raise ExitException("Failed to update DNS configuration for VPC: {}".format(e))

    spell_client.update_cluster_version(cluster["name"], cluster_version)

    click.echo("Congratulations, your cluster {} is up to date!".format(cluster["name"]))


def delete_aws_cluster(ctx, cluster, profile, keep_vpc):
    """
    Deletes an AWS cluster, including the Spell Cluster, Machine Types,
    Model Servers, VPC, IAM role, and IAM policies associated with this cluster.
    """

    spell_client = ctx.obj["client"]
    cluster_utils.validate_org_perms(spell_client, ctx.obj["owner"])

    try:
        import boto3
        from botocore.exceptions import BotoCoreError
    except ImportError:
        click.echo("Please pip install boto3 and rerun this command")
        return

    try:
        if not profile:
            profile = click.prompt("Enter the name of the AWS profile you would like to use", default="default")
        session = boto3.session.Session(profile_name=profile)
        s3 = session.resource("s3")
        ec2 = session.resource("ec2")
        iam = session.resource("iam")
    except BotoCoreError as e:
        click.echo("Failed to set profile {} with error: {}".format(profile, e))
        return
    click.echo(
        "This command will delete the Spell Cluster, Machine Types, Model Servers, "
        "VPC, IAM role, and IAM policies associated with this cluster. It will also "
        "prompt with the option to delete the output bucket."
    )
    if not click.confirm("Are you SURE you want to delete the spell cluster {}?".format(cluster["name"])):
        return

    if not click.confirm(
        "The deletion will use AWS profile '{}' which has "
        "Access Key ID '{}' and region '{}' - continue?".format(
            profile, session.get_credentials().access_key, session.region_name
        )
    ):
        return

    # Delete associated EKS cluster if it exists
    if cluster.get("serving_cluster_name"):
        if not is_installed("eksctl"):
            if not click.confirm(
                "Detected an associated Model Server EKS Cluster but `eksctl` "
                "is not installed. This command will not be able to delete the Model Server cluster. "
                "Would you like to skip this step and continue with deleting this cluster? "
                "Skipping will mean you must delete the EKS cluster manually."
            ):
                raise ExitException("`eksctl` is required, please install it at https://eksctl.io/")
        else:
            eks_delete_cluster(profile, cluster["serving_cluster_name"])

    # Delete Machine Types and Model Servers on cluster first
    with api_client_exception_handler():
        click.echo(
            "Sending message to Spell to remove all Machine Types " "from the cluster {}...".format(cluster["name"])
        )
        spell_client.delete_cluster_contents(cluster["name"])

    # Block until cluster is drained. This is necessary because the API will fail to
    # drain if we delete the IAM role before the machine types are marked as drained
    cluster_utils.block_until_cluster_drained(spell_client, cluster["name"])

    # Delete VPC
    if not keep_vpc:
        vpc_id = cluster["networking"]["aws"]["vpc_id"]
        click.echo("Deleting VPC {}".format(vpc_id))
        from botocore.exceptions import ClientError

        try:
            vpc = ec2.Vpc(vpc_id)
            # Delete subnets
            for subnet in vpc.subnets.all():
                subnet.delete()
                click.echo("Deleted subnet {}".format(subnet.id))
            # Delete internet gateway(s)
            for gateway in vpc.internet_gateways.all():
                vpc.detach_internet_gateway(InternetGatewayId=gateway.id)
                gateway.delete()
                click.echo("Deleted gateway {}".format(gateway.id))
            # Delete security group(s)
            for group in vpc.security_groups.all():
                if group.group_name == "default":
                    continue
                group.delete()
                click.echo("Deleted security group {}".format(group.id))
            # Delete VPC
            vpc.delete()
            click.echo("Deleted VPC {}".format(vpc.id))
        except ClientError as e:
            # If the VPC is already deleted return True for success
            if e.response["Error"]["Code"] == "InvalidVpcID.NotFound":
                click.echo("VPC {} is already deleted!".format(vpc.id))
            else:
                click.echo("Failed to delete VPC {}: {}".format(vpc.id, e))

    # Delete IAM
    def getNameFromArn(arn):
        return arn.split("/")[-1]

    roleArn = cluster["role_credentials"]["aws"]["role_arn"]
    roleName = getNameFromArn(roleArn)
    click.echo("Deleting Role {}".format(roleName))
    from botocore.exceptions import ClientError

    try:
        role = iam.Role(roleName)
        # Delete policies
        for policy in role.attached_policies.all():
            role.detach_policy(PolicyArn=policy.arn)
            policy.delete()
            click.echo("Deleted policy {}".format(getNameFromArn(policy.arn)))
        # Delete role
        role.delete()
        click.echo("Deleted role {}".format(roleName))
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchEntity":
            click.echo("Role {} is already deleted!".format(roleName))
        else:
            click.echo("Failed to delete role {}: {}".format(roleName, e))

    # Optionally delete the output bucket
    bucket = cluster["storage_uri"]
    if click.confirm("Delete bucket {}? WARNING: This will delete all the data in the bucket".format(bucket)):
        try:
            bucketObj = s3.Bucket(bucket)
            bucketObj.objects.all().delete()
            bucketObj.delete()
            click.echo("Deleted bucket {}".format(bucket))
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchBucket":
                click.echo("Bucket {} is already deleted!".format(bucket))
            else:
                click.echo("Failed to delete bucket {}: {}".format(bucket, e))

    # Last step is to mark the cluster as deleted
    with api_client_exception_handler():
        spell_client.delete_cluster(cluster["name"])
        click.echo("Successfully deleted cluster on Spell")


def eks_delete_cluster(profile, serving_cluster_name):
    eks_name = extract_eksctl_cluster_name(serving_cluster_name)
    if not click.confirm("Delete model serving cluster {}?".format(eks_name)):
        return

    click.echo("Deleting EKS cluster {}. This can take a while!".format(eks_name))
    cmd = ["eksctl", "delete", "cluster", "--name", eks_name, "--profile", profile]
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError:
        click.echo(
            "Failed to run `eksctl`. Make sure it's installed correctly and "
            "your inputs are valid. Error details are above in the `eksctl` output. "
            "You will need to delete your EKS cluster using `eksctl` manually."
        )


def extract_eksctl_cluster_name(cluster_name):
    # EKS cluster names take the form
    # CLUSTERNAME.REGION.eksctl.io
    pieces = cluster_name.split(".")
    return ".".join(pieces[:-3])
