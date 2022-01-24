import click
from indico_install.kube.svc.restart import restart
from indico_install.kube.svc.scale import scale, delete, enable
from indico_install.kube.svc.manage import put_resource
from indico_install.cluster_manager import ClusterManager


@click.group("svc")
@click.pass_context
def svc(ctx):
    """Commands for cluster services"""
    ctx.ensure_object(dict)
    ctx.obj["TRACKER"] = ClusterManager()


for command in [restart, scale, delete, enable, put_resource]:
    svc.add_command(command)
