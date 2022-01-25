from pathlib import Path
import click
from click import prompt

from indico_install.utils import run_cmd
from indico_install.infra.init import init
from indico_install.cluster_manager import ClusterManager

SCRIPT = Path(__file__).parent / "bin" / "indico_infra.sh"


@click.group("sn")
@click.pass_context
def single_node(ctx):
    """
    Create and validate Indico platform installation on a single node
    """
    ctx.ensure_object(dict)
    ctx.obj["TRACKER"] = ClusterManager()


single_node.command("init")(init(__name__))


@single_node.command("check")
@click.pass_context
def check(ctx):
    """Validate local MicroK8S cluster installation"""
    conf = ctx.obj["TRACKER"].cluster_config
    run_cmd([str(SCRIPT.resolve()), "check"], tty=True)

    rw_dir = Path(conf["clusterVolumes"]["rwx"]["hostPath"]["path"])
    ro_dir = Path(conf["clusterVolumes"]["rox"]["hostPath"]["path"])
    assert (
        rw_dir and rw_dir.is_dir()
    ), "Directory selected for read-write data does not exist!"
    assert (
        ro_dir and ro_dir.is_dir()
    ), "Directory selected for read-only data does not exist!"


@single_node.command("create")
@click.pass_context
def create(ctx):
    """Install local MicroK8S cluster"""
    conf = ctx.obj["TRACKER"].cluster_config
    run_cmd([str(SCRIPT.resolve()), "create"], tty=True)
    ask_for_infra_input(conf)
    ctx.obj["TRACKER"].save()

    rw_dir = Path(conf["clusterVolumes"]["rwx"]["hostPath"]["path"])
    ro_dir = Path(conf["clusterVolumes"]["rox"]["hostPath"]["path"])

    rw_dirs = " ".join(
        [
            str(rw_dir / sub_dir)
            for sub_dir in ("postgres_data", "rainbow", "finetune_models")
        ]
    )
    run_cmd(f"sudo mkdir -pm 777 {rw_dirs} {str(ro_dir)}".split(), tty=True)


def ask_for_infra_input(conf):
    click.secho(
        "Networking information.\n"
        "If connecting just from your local machine, use 127.0.0.1.\n"
        "For external access, use the computer hostname, and configure DNS to resolve this hostname.\n",
        fg="yellow",
    )
    conf["parentDomain"] = prompt(
        "Application domain", default=(conf["parentDomain"] or ".indico.io")
    )
    conf["publicIP"] = prompt(
        "The IP you want to use to connect. Example: 127.0.0.1",
        default=(conf["publicIP"] or "127.0.0.1"),
    )
    app_port = prompt(
        "Application port - must be greater than 30000",
        default=(
            conf["ingress"]["ports"]["https_port"] or 30001
        ),
    )
    curr_ports = conf["ingress"]["ports"]
    for i, port_name in enumerate(["https_port", "http_port", "http_api_port"]):
        curr_ports[port_name] = curr_ports[port_name] or app_port + i
    conf["ingress"]["ports"] = curr_ports

    conf["publicDomain"] = f"{conf['publicIP']}:{app_port}"

    click.secho("Volume paths to save data on your machine", fg="yellow")
    conf["clusterVolumes"]["rwx"]["hostPath"]["path"] = prompt(
        "Directory for all indico data - should have at least 800GB available",
        default=conf["clusterVolumes"]["rwx"]["hostPath"].get("path", None),
    )

    conf["clusterVolumes"]["rox"]["hostPath"]["path"] = prompt(
        "Directory for read-only-v10 API data - should have 120GB available",
        default=conf["clusterVolumes"]["rox"]["hostPath"].get("path", None),
    )
