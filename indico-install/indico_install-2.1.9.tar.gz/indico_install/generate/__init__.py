import click

from indico_install.generate.cluster_info import cluster_info
from indico_install.generate.update import update


@click.group("generate")
def generate():
    """Scale and configure cluster from dump"""
    pass


generate.add_command(update)
generate.add_command(cluster_info)
