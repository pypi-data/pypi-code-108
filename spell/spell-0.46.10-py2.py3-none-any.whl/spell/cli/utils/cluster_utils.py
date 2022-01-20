from functools import wraps
import click
import jinja2
import os
from packaging import version
import random
import re
import subprocess
import string
import sys
import tempfile
import time
from typing import Optional, Tuple
import yaml

from spell.cli.constants import MIN_KUBE_API_VERSION, MAX_KUBE_API_VERSION
from spell.api.exceptions import BadRequest
from spell.cli.exceptions import (
    api_client_exception_handler,
    ExitException,
)
from spell.cli.log import logger
from spell.cli.utils import require_import
from spell.cli.utils.ambassador_templates import (
    generate_main_ambassador_yaml,
    generate_cert_manager_yaml,
    aes_crds_yaml,
    generate_ambassador_host_yaml,
)
from spell.cli.utils.efk_yamls import (
    elasticsearch_yaml,
    kibana_yaml,
    fluentd_yaml,
    fluentd_configmap_yaml,
    fluentd_elasticsearch_plugin_yaml,
    curator_yaml,
)
from spell.cli.utils.efk_yamls_runs import autossh_yaml
from spell.version import __version__ as CLI_VERSION

import spell.cli.utils  # for __file__ introspection

serving_manifests_dir = os.path.join(os.path.dirname(spell.cli.utils.__file__), "kube_manifests", "spell-serving")


def get_for_cloud_provider_decorator(cloud_provider):
    def for_cloud_provider(*decorators):
        def for_cloud_provider_wrapper(f):
            @wraps(f)
            def wrapped(*args, cluster=None, **kwargs):
                if cluster is None:
                    raise ExitException(
                        "No cluster defined in for_cloud_provider decorator on {0}! Make sure "
                        "{0} is also decorated with pass_cluster".format(f.__name__)
                    )
                maybe_decorated = f
                if cluster["cloud_provider"] == cloud_provider:
                    for decorator in decorators:
                        maybe_decorated = decorator(maybe_decorated)
                maybe_decorated(*args, cluster=cluster, **kwargs)

            return wrapped

        return for_cloud_provider_wrapper

    return for_cloud_provider


"""
Decorator that conditionally applies the decorators passed into it if the
cluster passed into the command is an AWS cluster

NOTE: Must be used in tandem with the pass_cluster decorator
"""
for_aws = get_for_cloud_provider_decorator("AWS")

"""
Decorator that conditionally applies the decorators passed into it if the
cluster passed into the command is a GCP cluster

NOTE: Must be used in tandem with the pass_cluster decorator
"""
for_gcp = get_for_cloud_provider_decorator("GCP")

"""
Decorator that conditionally applies the decorators passed into it if the
cluster passed into the command is a Azure cluster

NOTE: Must be used in tandem with the pass_cluster decorator
"""
for_azure = get_for_cloud_provider_decorator("Azure")


def deduce_cluster(ctx, cluster_name):
    spell_client = ctx.obj["client"]
    validate_org_perms(spell_client, ctx.obj["owner"])

    with api_client_exception_handler():
        clusters = spell_client.list_clusters()
    if len(clusters) == 0:
        raise ExitException("No clusters defined, please run `spell cluster init aws` or `spell cluster init gcp`")

    if cluster_name is not None:
        clusters = [c for c in clusters if c["name"] == cluster_name]
        if len(clusters) == 0:
            raise ExitException("No clusters with the name {}.".format(cluster_name))
        elif len(clusters) > 1:
            # This should never happen
            raise ExitException("More than one cluster with the name {}.".format(cluster_name))

    if len(clusters) == 1:
        return clusters[0]

    cluster_names = [c["name"] for c in clusters]
    cluster_name = click.prompt(
        "You have multiple clusters defined. Please select one.",
        type=click.Choice(cluster_names),
    ).strip()
    for c in clusters:
        if c["name"] == cluster_name:
            return c
    # This should never happen
    raise ExitException("No clusters with the name {}.".format(cluster_name))


def pass_cluster(f):
    """
    Decorator that deduces the org's cluster and passes it into the command
    """

    @click.option("--cluster-name", hidden=True)
    @wraps(f)
    def wrapped(ctx, *args, cluster_name=None, **kwargs):
        cluster = deduce_cluster(ctx, cluster_name)
        provider = cluster["cloud_provider"]
        if provider not in ("AWS", "GCP", "Azure"):
            raise ExitException("Cluster with unknown cloud provider {}".format(provider))
        f(ctx=ctx, *args, cluster=cluster, **kwargs)

    return wrapped


def check_cli_version(f):
    """
    Decorator that reaches out to the API to confirm there are no known bugs with the CLI version before
    allowing serve to proceed.
    """

    # Returns  string of subcommands separated by white space - omitting the `spell`
    # Ex: `spell kube-cluster describe` -> "kube-cluster describe"
    def get_command_list(ctx, current, commands):
        if current == "cli" or ctx.parent is None:
            return commands
        commands = current + " " + commands
        return get_command_list(ctx.parent, ctx.parent.command.name, commands)

    @wraps(f)
    def wrapped(ctx, *args, **kwargs):
        spell_client = ctx.obj["client"]
        cmds = get_command_list(ctx, ctx.command.name, "")
        with api_client_exception_handler():
            spell_client.check_version_cli(cmds, CLI_VERSION)
        f(ctx=ctx, *args, **kwargs)

    return wrapped


def pass_gcp_project_creds(f):
    """
    Decorator that attempts to grab gcloud project and credentials and passes
    them into the command
    """

    @wraps(f)
    @require_import("google.auth", pkg_extras="cluster-gcp")
    def wrapped(*args, **kwargs):
        import google.auth

        try:
            credentials, project = google.auth.default()
        except google.auth.exceptions.DefaultCredentialsError:
            raise ExitException(
                "No gcloud credentials found! Please run `gcloud auth application-default login` "
                "then rerun this command."
            )
        f(*args, gcp_project=project, gcp_creds=credentials, **kwargs)

    return wrapped


def handle_aws_profile_flag(f):
    """
    Decorator that handles the --profile flag in GCP/Azure by swallowing the kwarg
    and raising an error if it has a value
    """

    @wraps(f)
    def wrapped(*args, profile=None, **kwargs):
        if profile is not None:
            raise ExitException("Flag --profile is not a valid option for non-AWS clusters")
        f(*args, **kwargs)

    return wrapped


def pass_aws_session(perms=[]):
    """
    Decorator that creates and passes a boto session into the command
    queries for a user confirmation after printing permissions info
    """

    def pass_aws_session_wrapper(f):
        @wraps(f)
        @require_import("boto3", "botocore", pkg_extras="cluster-aws")
        def wrapped(*args, profile=None, **kwargs):
            import boto3
            import botocore

            profile = profile or "default"
            try:
                session = boto3.session.Session(profile_name=profile)
            except botocore.exceptions.BotoCoreError as e:
                raise ExitException("Failed to set profile {} with error: {}".format(profile, e))
            if perms:
                perms_msg = "This command will\n"
                perms_msg += "\n".join("    - {}".format(perm) for perm in perms)
                click.echo(perms_msg)
            confirmed = click.confirm(
                "This command will proceed using AWS profile '{}' which has "
                "Access Key ID '{}' in region '{}' - continue?".format(
                    profile,
                    session.get_credentials().access_key,
                    session.region_name,
                )
            )
            if not confirmed:
                sys.exit(1)
            f(*args, aws_session=session, **kwargs)

        return wrapped

    return pass_aws_session_wrapper


def echo_delimiter():
    click.echo("---------------------------------------------")


def validate_org_perms(spell_client, owner):
    with api_client_exception_handler():
        owner_details = spell_client.get_owner_details()
        if owner_details.type != "organization":
            raise ExitException(
                "Only organizations can use cluster features, use `spell owner` "
                "to switch current owner to an organization "
            )
        if owner_details.requestor_role not in ("admin", "manager"):
            raise ExitException("You must be a Manager or Admin with current org {} to proceed".format(owner))


def block_until_cluster_drained(spell_client, cluster_name, spinner=None):
    """
    Block until cluster is drained. This is necessary because the API will fail to
    drain if we delete the IAM role before the machine types are marked as drained
    """
    if spinner:
        spinner.text = "Draining cluster..."
        spinner.start()
    num_retries = 10
    retrying_copy = "Cluster is still draining all machine types. This can take a long time! Retrying in 30s..."
    for i in range(num_retries):
        try:
            spell_client.is_cluster_drained(cluster_name)
            if spinner:
                spinner.stop()
            click.echo("Cluster is drained!")
            return
        except BadRequest:
            # Don't sleep on the last iteration
            if i < num_retries - 1:
                if spinner:
                    spinner.text = retrying_copy
                else:
                    click.echo(retrying_copy)
                time.sleep(30)
    if spinner:
        spinner.stop()
    raise ExitException(
        "Timed out waiting for Spell to drain the cluster. Please try again or contact Spell if the problem persists."
    )


# List sourced from this table: https://aws.amazon.com/ec2/instance-types/#Accelerated_Computing
def is_gpu_instance_type(instance_type):
    gpu_prefixes = ("p3.", "p3dn.", "p2.", "inf1.", "g4dn.", "g3s.", "g3.", "f1.")
    return any(instance_type.startswith(prefix) for prefix in gpu_prefixes)


#########################
# Model-serving utilities
#########################


def generate_api_kubeconfig(cluster, aws_profile, kube_cluster_name):
    """Generate the kubeconfig used by the api to post up whatever"""
    with KubeClusterContext(cluster, aws_profile, kube_cluster_name=kube_cluster_name) as kubeconfig:
        parsed_yaml = yaml.safe_load(kubeconfig)

        if cluster["cloud_provider"] == "GCP":
            # update kubeconfig to use the custom `gcp-svc` auth-provider
            if (
                "users" not in parsed_yaml
                or len(parsed_yaml["users"]) != 1
                or "user" not in parsed_yaml["users"][0]
                or "auth-provider" not in parsed_yaml["users"][0]["user"]
            ):
                raise Exception("Unexpected kubeconfig yaml generated from gcloud command")
            parsed_yaml["users"][0]["user"]["auth-provider"] = {
                "name": "gcp-svc",
                "config": {"service-acct": cluster["role_credentials"]["gcp"]["service_account_id"]},
            }
        kubecfg_yaml = yaml.dump(parsed_yaml, default_flow_style=False)
    return kubecfg_yaml


class KubeClusterContext:
    def __init__(self, cluster, aws_profile, kube_cluster_name="", namespace="", kube_config_path=""):
        """creds is either aws or gcp creds - a kube config can also be specified via kube_config_path"""
        if kube_config_path:
            with open(kube_config_path, "r") as f:
                self.kubeconfig = f
            self.kubeconfig_name = kube_config_path
        else:
            self.kubeconfig = tempfile.NamedTemporaryFile(mode="r+", suffix=".yaml")
            self.kubeconfig_name = self.kubeconfig.name
            self.kube_name = cluster.get("serving_cluster_short_name", kube_cluster_name)
            self.provider = cluster.get("cloud_provider")
            if not self.kube_name:
                raise TypeError("Couldn't infer kubernetes cluster name")
            self.init_kubeconfig(cluster, aws_profile)
        if namespace:
            kubectl(
                "config",
                "set-context",
                "--current",
                "--kubeconfig",
                self.kubeconfig_name,
                f"--namespace={namespace}",
            )

    def __enter__(self):
        self.stored_env = os.environ.get("KUBECONFIG", "")
        os.environ["KUBECONFIG"] = self.kubeconfig_name
        return self.kubeconfig

    def __exit__(self, exc_type, exc_value, exc_traceback):
        os.environ["KUBECONFIG"] = self.stored_env
        self.stored_env = ""
        self.kubeconfig.close()

    def init_kubeconfig(self, cluster, aws_profile=None):
        env = os.environ.copy()
        env["KUBECONFIG"] = self.kubeconfig_name
        if self.provider == "AWS":
            cmd = (
                "eksctl",
                "utils",
                "write-kubeconfig",
                "--cluster",
                self.kube_name,
                "--profile",
                aws_profile,
                "--region",
                cluster["networking"]["aws"]["region"],
            )
        elif self.provider == "GCP":
            cmd = (
                "gcloud",
                "container",
                "clusters",
                "get-credentials",
                self.kube_name,
                "--zone",
                cluster["serving_cluster_location"],
                "--project",
                cluster["networking"]["gcp"]["project"],
            )
        else:
            raise TypeError("Invalid cluster provider")
        subprocess.check_call(cmd, env=env)


def kubectl(*args: Tuple[str], kubectl_context: Optional[str] = None, env=None, text=False):
    """*args is passed to kubectl"""
    if text:
        return subprocess.check_output(("kubectl", *args), env=env, text=text)
    if not kubectl_context:
        return subprocess.check_call(("kubectl", *args), env=env)
    # deprecated: use cluster_utils.KubeClusterContext class instead
    return subprocess.check_call(("kubectl", "--context", kubectl_context, *args), env=env)


def kubectl_apply(yaml: str, *args: Tuple[str], kubectl_context: Optional[str] = None, env=None):
    """*args are additional args to pass to kubectl, like namespace"""
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+") as f:
        f.write(yaml)
        f.flush()

        return kubectl("apply", "--filename", f.name, *args, kubectl_context=kubectl_context, env=env)


# must be executed with elevated permissions (namespace)
# does not fail if namespace already exists.
def create_namespace(namespace):
    import kubernetes.client
    import kubernetes.config

    echo_delimiter()
    click.echo(f"Creating '{namespace}' namespace...")

    try:
        kubernetes.config.load_kube_config()
        kube_api = kubernetes.client.CoreV1Api()
        if any(i.metadata.name == namespace for i in kube_api.list_namespace().items):
            click.echo(f"'{namespace}' namespace already exists!")
        else:
            kube_api.create_namespace(
                kubernetes.client.V1Namespace(metadata=kubernetes.client.V1ObjectMeta(name=namespace))
            )
            click.echo(f"'{namespace}' namespace created!")
    except Exception as e:
        raise ExitException(f"ERROR: Creating '{namespace}' namespace failed. Error was: {e}")


def create_serving_priorityclass(kubectl_context=None):
    kubectl(
        "apply",
        "--filename",
        os.path.join(serving_manifests_dir, "spell", "serving-priorityclass.yaml"),
        kubectl_context=kubectl_context,
    )


def check_if_model_servers_running():
    """Check if model serving pods still exist in this kube cluster."""
    pods = (
        subprocess.check_output(("kubectl", "get", "pods", "-n", "serving"), stderr=subprocess.DEVNULL)
        .decode("utf-8")
        .strip()
    )
    if pods.count("\n") != 0:
        return False
    return True


def prompt_grafana_password(generate=False) -> str:
    """Meant to be used from a click command"""
    _generated_pass = "".join((random.choice(string.ascii_letters + string.digits) for i in range(16)))
    if generate:
        return _generated_pass
    while True:
        grafana_password = click.prompt(
            "Choose a secure password for the Grafana admin, or leave empty to generate a random password",
            default=_generated_pass,
            hide_input=True,
            type=str,
            show_default=False,
        )
        # This is somewhat arbitrary because Grafana doesn't seem to document its password requirements
        if len(grafana_password) >= 6 and len(grafana_password) <= 20:
            break
        click.echo("Invalid password; please use a password between 6 and 20 characters in length")

    return grafana_password


def print_grafana_credentials(cluster, grafana_password):
    """Just pretty-print grafana creds at the end of a setup"""
    click.echo(f"Your Grafana Credentials:\n username: {cluster['name']}\n password: {grafana_password}")
    click.echo(f"Grafana is accessible at https://{cluster['serving_cluster_domain']}/grafana")


def update_grafana_configuration(cluster, password: Optional[str]):
    """Directly modifies grafana via kubectl"""
    if not password:
        return
    click.echo("Configuring user credentials for Grafana.")

    # delete existing configmap, if present
    kubectl(
        "delete",
        "secret",
        "--namespace",
        "monitoring",
        "spell-grafana-admin-password",
        "--ignore-not-found",
    )

    with tempfile.NamedTemporaryFile(suffix=".secret", mode="w+") as f:
        f.write(password)
        f.flush()
        kubectl(
            "create",
            "secret",
            "generic",
            "spell-grafana-admin-password",
            "--namespace",
            "monitoring",
            "--from-file=password.ini={}".format(f.name),
        )

    # grafana configmap changes don't get hot-reloaded
    kubectl("delete", "--namespace", "monitoring", "po", "-l", "app=grafana")


def create_reg_secret():
    docker_email = click.prompt("Enter your Dockerhub email")
    docker_username = click.prompt("Enter your Dockerhub username")
    docker_pass = click.prompt("Enter your Dockerhub password", hide_input=True)
    # Create secret used by Kaniko to push to a user's registry
    # Delete Secret if it exists
    kubectl(
        "delete",
        "secret",
        "docker-registry",
        "regcred",
        "-n",
        "spell-run",
        "--ignore-not-found",
    )
    kubectl(
        "create",
        "secret",
        "docker-registry",
        "regcred",
        "--docker-server=https://index.docker.io/v1/",
        f"--docker-username={docker_username}",
        f"--docker-password={docker_pass}",
        f"--docker-email={docker_email}",
        "-n",
        "spell-run",
    )

    # Create ConfigMap containing docker username
    # Delete if it exists
    kubectl("delete", "configmap", "dockerusername", "-n", "spell-run", "--ignore-not-found")
    kubectl(
        "create",
        "configmap",
        "dockerusername",
        f"--from-literal=username={docker_username}",
        "-n",
        "spell-run",
    )


def add_efk_stack(ctx, support_runs):
    """Adds:
    Elastic Operator (a kube CRD, Custom Resource Defintion) from ECK (Elastic Cloud on Kubernetes)
    Elastic search (deployment from ECK) to store and index logs (on a 50GB persistant volume)
    Kibana (service from ECK)
    Fluentd daemon set with custom configuration file to forward only model server pod logs
    Curator cron job to delete the oldest logs
    """

    echo_delimiter()
    click.echo("Setting up logging stack...")
    try:
        kubectl(
            "apply",
            "-f",
            "https://download.elastic.co/downloads/eck/1.2.1/all-in-one.yaml",
        )

        kubectl_apply(elasticsearch_yaml, "-n", "elastic-system")
        kubectl_apply(kibana_yaml, "-n", "elastic-system")
        if support_runs:
            # TODO(Benno): update this tag to be an explicit value when the updated autossh image is built
            autossh_tag = ""
            kafka_broker_ports = "-L *:32190:localhost:32190 -L *:32191:localhost:32191 -L *:32192:localhost:32192"
            tcpproxy_host = "localhost"
            if ctx.obj["stack"] == "local":
                autossh_tag = ":" + os.environ["SPELL_EMPLOYEE_NAME"]
                kafka_broker_ports = "-L *:29193:tcpproxy:29193"
                tcpproxy_host = "tcpproxy"
            kubectl_apply(
                autossh_yaml.format(autossh_tag, kafka_broker_ports, tcpproxy_host),
                "-n",
                "spell-run",
            )
        else:
            kubectl_apply(fluentd_configmap_yaml, "-n", "elastic-system")
            kubectl_apply(fluentd_elasticsearch_plugin_yaml, "-n", "elastic-system")
            kubectl_apply(fluentd_yaml, "-n", "elastic-system")
        kubectl_apply(curator_yaml, "-n", "elastic-system")

    except Exception as e:
        logger.error("Setting up logging stack failed. Error was: {}".format(e))


def add_ambassador(cluster, is_public):
    """Adds ambassador stack to the 'amabassador' namespace."""
    try:
        click.echo("Adding Ambassador custom resources...")
        with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+") as f:
            f.write(aes_crds_yaml)
            f.flush()
            subprocess.check_call(
                ("kubectl", "apply", "--filename", f.name),
            )

        subprocess.check_call(
            (
                "kubectl",
                "wait",
                "--for",
                "condition=established",
                "--timeout=90s",
                "crd",
                "-lproduct=aes",
            ),
        )
        click.echo("Setting up Ambassador deployment in 'ambassador' namespace...")
        with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+") as f:
            ambassador_yaml = generate_main_ambassador_yaml("AWS", is_public)
            f.write(ambassador_yaml)
            f.flush()
            subprocess.check_call(
                ("kubectl", "apply", "--filename", f.name),
            )

        subprocess.check_call(
            (
                "kubectl",
                "-n",
                "ambassador",
                "wait",
                "--for",
                "condition=available",
                "--timeout=90s",
                "deploy",
                "-lproduct=aes",
            ),
        )

        # TODO(waldo) cert-manager only gets added right now on public clusters,
        # but private clusters could also use cert-manager to manage certs from their private CA
        # if it were deployed on the cluster, which would allow auto-renewal
        uses_letsencrypt_cert = is_public
        if uses_letsencrypt_cert:
            add_cert_manage_and_get_cert(cluster)
        else:  # set a dummy secret so Host resource does not error
            subprocess.run(
                (
                    "kubectl",
                    "create",
                    "secret",
                    "generic",
                    "--from-literal=cert=dummy",
                    "ambassador-certs",
                    "-n",
                    "ambassador",
                ),
                stderr=subprocess.DEVNULL,
            )

        click.echo("Configuring network settings for Ambassador...")
        with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+") as f:
            ambassador_yaml = generate_ambassador_host_yaml(cluster["serving_cluster_domain"])
            f.write(ambassador_yaml)
            f.flush()
            subprocess.check_call(("kubectl", "apply", "--filename", f.name))
    except Exception as e:
        raise ExitException(f"Setting up Ambassador failed. Error was: {e}")

    click.echo("Ambassador set up!")


def add_consul(cluster):
    """Add consul connect service mesh, which sets up proxy sidecars for mTLS traffic"""
    echo_delimiter()
    click.echo("Setting up Consul connect service mesh...")
    try:
        kubectl("apply", "-f", os.path.join(serving_manifests_dir, "consul"))
    except Exception as e:
        raise ExitException(f"Setting up Consul failed. Please contact Spell support. Error was: {e}")


def add_monitoring_stack(cluster):
    """Adds prometheus to the 'monitoring' namespace."""
    echo_delimiter()
    click.echo("Setting up kube-prometheus monitoring stack...")
    try:
        click.echo("Adding Custom Resources for Prometheus...")
        kubectl("apply", "-f", os.path.join(serving_manifests_dir, "setup"))

        # Wait for ServiceMonitor to be created before applying Prometheus YAMLs
        kubectl(
            "wait",
            "--for",
            "condition=established",
            "--timeout=90s",
            "--filename",
            os.path.join(
                serving_manifests_dir,
                "setup",
                "prometheus-operator-0prometheusCustomResourceDefinition.yaml",
            ),
        )

        click.echo("Configuring Prometheus for Spell...")

        rule_template = None
        with open(os.path.join(serving_manifests_dir, "spell", "spell-prometheus-rules.j2"), "r") as f:
            rule_template = jinja2.Template(f.read())
        rule_yaml = rule_template.render(model_server_prefix="model-serving")
        kubectl_apply(rule_yaml)

        click.echo("Setting up Prometheus deployment in 'monitoring' namespace...")
        kubectl(
            "apply",
            "--filename",
            serving_manifests_dir,
        )

        click.echo("Hooking up Ambassador to Prometheus...")
        kubectl(
            "apply",
            "--filename",
            os.path.join(serving_manifests_dir, "ambassador"),
        )

        click.echo("Configuring Grafana...")
        kubectl(
            "apply",
            "--filename",
            os.path.join(serving_manifests_dir, "spell", "spell-grafana-home-dashboard.yaml"),
        )

        # delete existing configmap, if present
        kubectl(
            "delete",
            "configmap",
            "--namespace",
            "monitoring",
            "spell-grafana-config",
            "--ignore-not-found",
        )

        with open(os.path.join(serving_manifests_dir, "spell", "grafana.ini.j2")) as f:
            template = jinja2.Template(f.read())
        grafana_config = template.render(
            cluster_name=cluster["name"],
            model_serving_url=cluster["serving_cluster_domain"],
        )

        with tempfile.NamedTemporaryFile(suffix=".ini", mode="w+") as f:
            f.write(grafana_config)
            f.flush()
            kubectl(
                "create",
                "configmap",
                "spell-grafana-config",
                "--namespace",
                "monitoring",
                "--from-file=grafana.ini={}".format(f.name),
            )

        # this is required to configure prometheus as the default datasource
        kubectl(
            "delete",
            "secret",
            "--namespace",
            "monitoring",
            "grafana-datasources",
            "--ignore-not-found",
        )

        kubectl(
            "create",
            "secret",
            "generic",
            "grafana-datasources",
            "--namespace",
            "monitoring",
            "--from-file=datasources.yaml={}".format(os.path.join(serving_manifests_dir, "spell", "datasources.yaml")),
        )

        click.echo("Adding Grafana to routes...")
        kubectl(
            "apply",
            "--filename",
            os.path.join(serving_manifests_dir, "spell", "spell-grafana-mapping.yaml"),
        )

        click.echo("All done setting up Prometheus!")

    except Exception as e:
        raise ExitException(f"Setting up Prometheus failed. Please contact Spell support. Error was: {e}")


def finalize_kube_cluster(cluster_version):
    """Restart pods + deploys after reapplying yaml files, in case some pods are finnicky"""
    click.echo("Restarting prometheus adapter to load config changes...")
    kubectl("rollout", "restart", "deploy/prometheus-adapter", "-n", "monitoring")
    click.echo("Restarting grafana to load config changes...")
    kubectl("rollout", "restart", "deploy/grafana", "-n", "monitoring")

    v = version.parse(cluster_version)
    if v.major == 0 and v.minor < 26:
        click.echo("Restarting fluentd to load config changes...")
        kubectl("rollout", "restart", "ds/fluentd", "-n", "elastic-system")


# NOTE: Retries on error, logs peristent errors but does not raise them
def add_cert_manage_and_get_cert(cluster):
    click.echo("Setting up the TLS cert for your cluster...")
    try:
        kubectl(
            "apply",
            "--filename",
            "https://github.com/jetstack/cert-manager/releases/download/v1.0.2/cert-manager.yaml",
        )
    except Exception as e:
        logger.error("Setting up the TLS cert manager failed. Error was: {}".format(e))
        return

    max_retries = 12  # wait up to 1 minute
    for i in range(max_retries):
        try:
            with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+") as f:
                cert_yaml = generate_cert_manager_yaml(cluster["serving_cluster_domain"])
                f.write(cert_yaml)
                f.flush()
                subprocess.check_call(
                    ("kubectl", "apply", "--filename", f.name),
                    stderr=subprocess.DEVNULL,
                )
            break
        except Exception as e:
            if i == max_retries - 1:
                logger.error("Setting up the TLS cert manager failed. Error was: {}".format(e))
                return
            time.sleep(5)

    click.echo("Completed setting up the TLS cert for your cluster!")
    click.echo("NOTE: TLS cert may take a few minutes to be created")


def make_optional_serving_features(cluster):
    cloud = cluster["cloud_provider"]
    if cloud == "AWS":
        return {"autoscaling": True, "gpu": True, "mTLS": False}
    elif cloud == "GCP":
        return {"autoscaling": True, "gpu": True}
    else:
        raise ValueError("Invalid cloud provider")


# NOTE(waldo): The control plane and nodes need to be upgraded separately, so when we
# update manifests for a cluster we need to check that the api version
# is valid on the api _and_ on each user node-group.
def check_kube_cluster_version():
    # check control plane version
    version_str = subprocess.check_output(["kubectl", "version", "--short"], text=True)
    server_version = re.search(r"Server Version: v([0-9]*\.[0-9]*\.[0-9]*)", version_str).group(1)
    if not server_version:
        raise ExitException("Unable to determine kube control plane version")
    if version.parse(server_version) < version.parse(MIN_KUBE_API_VERSION) or version.parse(
        server_version
    ) > version.parse(MAX_KUBE_API_VERSION):
        raise ExitException(
            f"kube-cluster API version is {server_version}, which falls outside the supported version window"
        )

    # check node-groups
    custom_cols = (
        "custom-columns=version:status.nodeInfo.kubeletVersion,"
        + "ng:metadata.labels.spell_serving_group,name:metadata.name"
    )
    nodes = kubectl("get", "no", "-o", custom_cols, text=True).split("\n")[1:]
    for nodeinfo in nodes:
        if not nodeinfo:
            continue
        ver, nodegroup, name = nodeinfo.split()
        ver = re.match(r"v\d+.\d+.\d+", ver).group(0)
        if nodegroup == "<none>":
            nodegroup = "default"  # get correct ng name for old, unlabelled nodegroups

        if version.parse(ver) < version.parse(MIN_KUBE_API_VERSION) or version.parse(ver) > version.parse(
            MAX_KUBE_API_VERSION
        ):
            print(version.parse(ver))
            err = (
                f"Node {name} in nodegroup {nodegroup} has k8s version {ver}, which falls outside Spell's support"
                " window"
            )
            raise ExitException(err)
