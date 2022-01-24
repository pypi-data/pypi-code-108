import os
import shutil
import tempfile

import click
from indico_install.cluster_manager import ClusterManager
from indico_install.config import D_PATH, REMOTE_TEMPLATES_PATH, yaml
from indico_install.utils import options_wrapper, run_cmd
from indico_install.utils import run_cmd


def helm3_install(dependency):
    """
    Helm3 install a given chart
    """
    click.echo(f"Installing {dependency['name']}")
    if not all(key in dependency.keys() for key in ["name", "repository", "version"]):
        click.secho(
            f"Unable to install {dependency.get('name')}: expected keys not present"
        )
        return
    repo_name = dependency.get("repoName", f"{dependency['name']}-repository")
    namespace = (
        f"--namespace {dependency.get('namespace')}"
        if dependency.get("namespace")
        else ""
    )
    wait = "--wait" if dependency.get("wait", True) else ""
    command = "upgrade" if release_exists(dependency) else "install"
    args = dependency.get("args", "")
    with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as override_yaml:
        override_yaml.write(
            yaml.dump(dependency.get("values", {}), default_flow_style=False).encode(
                "utf-8"
            )
        )
        override_yaml.flush()
        run_cmd(f"helm3 repo add {repo_name} {dependency['repository']}")
        run_cmd("helm3 repo update", silent=True)
        run_cmd("helm3 dependency update", silent=True)
        import_existing_objects(dependency)
        run_cmd(
            f"helm3 {command} {namespace} {wait} {args} {dependency['name']} {repo_name}/{dependency['name']} --create-namespace -f {override_yaml.name} --version {dependency['version']}"
        )

def import_existing_objects(dependency):
    # Then check to see if the objects themselves are deployed
    # if they are, set labels and annotations on them so that helm can own them
    # NOTE: this will not update annotations/labels that already exist
    if release_exists(dependency):
        return
    name = dependency.get('name')
    namespace = dependency.get('namespace', 'default')
    repo_name = dependency.get('repoName', f"{name}-repository")
    args = dependency.get('args', '')
    version = dependency['version']

    with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as override_yaml:
        override_yaml.write(
            yaml.dump(dependency.get("values", {}), default_flow_style=False).encode(
                "utf-8"
            )
        )
        override_yaml.flush()
        output = run_cmd(
            f"helm3 template --namespace {namespace} {args} {name} {repo_name}/{name} -f {override_yaml.name} --version {version} --include-crds"
        )
        objects = yaml.load_all(output)
        for obj in objects:
            obj_kind = obj['kind']
            obj_name = obj['metadata']['name']
            obj_namespace = obj['metadata'].get('namespace', 'default')
            output = run_cmd(
                f"kubectl get {obj_kind} {obj_name} -n {obj_namespace}"
            )
            if len(output) > 0:
                run_cmd(f"kubectl annotate {obj_kind} {obj_name} -n {obj_namespace} meta.helm.sh/release-name={name}")
                run_cmd(f"kubectl annotate {obj_kind} {obj_name} -n {obj_namespace} meta.helm.sh/release-namespace={namespace}")
                run_cmd(f"kubectl label {obj_kind} {obj_name} -n {obj_namespace} app.kubernetes.io/managed-by=Helm")
    

def release_exists(dependency):
    """
    Given a dependency, return true if it is deployed, else return false
    """
    name = dependency.get('name')
    namespace = dependency.get('namespace', 'default')
    output = run_cmd(
        f"helm3 get all {name} -n {namespace}",
        silent=True,
    )
    if len(output) > 0:
        click.secho(
            f"Release {name} already exists; updating existing release"
        )
        return True
    return False


@click.command("install")
@click.argument("charts", required=False, nargs=-1)
@click.pass_context
@options_wrapper()
def install(ctx, cluster_manager=None, charts=None, yes=False):
    """
    Install helm charts from sources defined in the 'dependencies' section of the cluster manager config. Install any number of available charts with the CHART argument

    Example 1
    Install the cert-manager helm chart as specified in the cluster manager config:
    indico install cert-manager

    Example 2
    Install all helm charts specified in the cluster manager config:
    indico install
    """
    cluster_manager = cluster_manager or ClusterManager()
    deps = cluster_manager.cluster_config.get("dependencies", {})
    if not deps:
        click.secho(
            "No helm chart dependencies specified in the cluster manager configmap"
        )
        return
    for dependency in deps:
        if charts and not [
            chart for chart in charts if chart in dependency.get("name")
        ]:
            continue
        if yes or click.confirm(
            f"Ready to install/upgrade {dependency.get('name')} chart?"
        ):
            helm3_install(dependency)
