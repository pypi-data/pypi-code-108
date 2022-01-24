import shutil
import tarfile
import time
from pathlib import Path

import click
from click import secho

from indico_install.config import CLUSTER_NAME, yaml, D_PATH
from indico_install.infra.input_utils import auth_with_gsutil
from indico_install.utils import current_user, run_cmd
from indico_install.cluster_manager import ClusterManager, get_default_namespace


default_namespace = get_default_namespace(ClusterManager().cluster_config, "defaultNamespace")


@click.command("cluster-info")
@click.pass_context
@click.option(
    "--upload/--no-upload",
    default=True,
    show_default=True,
    help="Upload the cluster dump TAR to a private Google Storage bucket shared with Indico",
)
@click.option(
    "--sudo/--no-sudo",
    default=False,
    show_default=False,
    help="Use sudo to run cluster dump (useful if running into permission issues)",
)
def cluster_info(ctx, *, upload, sudo):
    """
    Load and package all the information on the running cluster
    into a local TAR file.
    """
    dumpdir = D_PATH / f"cluster_info_{time.strftime('%Y%m%d-%H%M%S')}"
    secho("Pulling cluster info...", fg="blue")
    sudo = "sudo " if sudo else ""
    run_cmd(
        f"""
        {sudo}kubectl cluster-info dump -o yaml --output-directory={dumpdir};
        {sudo}kubectl get configmaps --namespace={default_namespace} -o yaml > {dumpdir}/configmaps.yaml;
        {sudo}kubectl get ingress --namespace={default_namespace} -o yaml > {dumpdir}/ingress.yaml;
        {sudo}kubectl get pv --namespace={default_namespace} -o yaml > {dumpdir}/pv.yaml;
        {sudo}kubectl get pvc --namespace={default_namespace} -o yaml > {dumpdir}/pvc.yaml;
        """,
        silent=True,
    )
    # Remove cluster mananger from CMs
    with open(f"{dumpdir}/configmaps.yaml", "r") as f:
        _configs = yaml.safe_load(f)
    with open(f"{dumpdir}/configmaps.yaml", "w") as f:
        try:
            cm_index = next(
                i
                for i, cm in enumerate(_configs["items"])
                if cm["metadata"]["name"].startswith("cluster-manager")
            )
            _configs["items"].pop(cm_index)
            yaml.dump(_configs, f, default_flow_style=False)
        except Exception:
            pass

    dump_tar = str(dumpdir.resolve()) + ".tar.gz"
    with tarfile.open(dump_tar, "w:gz") as tar:
        tar.add(dumpdir, arcname="")

    secho(f"Cluster information saved to {dump_tar}", fg="green")
    shutil.rmtree(dumpdir, ignore_errors=True)
    if not upload:
        return

    cluster_user = (
        current_user(clean=True) if auth_with_gsutil() else CLUSTER_NAME
    )
    if not cluster_user:
        secho(
            "Cannot authenticate with Google - please upload cluster info manually",
            fg="yellow",
        )
        return

    result = run_cmd(
        f"gsutil cp {dump_tar} gs://client_{cluster_user}/{Path(dump_tar).name} 2>&1",
        silent=True,
    )
    msgs = (
        (
            "Operation completed",
            "Cluster information successfully shared with Indico",
            "green",
        ),
        (
            "BucketNotFoundException",
            f"Bucket for user {cluster_user} does not exist. Please ask Indico to create this and try sharing again, or manually share your cluster info TAR",
            "yellow",
        ),
        (
            "",
            "Unable to share cluster info with Indico. Please share the cluster info TAR manually",
            "red",
        ),
    )
    for res, msg, color in msgs:
        if res in result:
            secho(msg, fg=color)
            break
