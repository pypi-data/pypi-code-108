import click
import os

from rastless.config import Cfg
from rastless.core.colormap import create_colormap


@click.command()
@click.argument('sld_file', type=click.Path(exists=True))
@click.option("-n", "--name", help="Name the colormap, otherwise take the filename")
@click.option("-d", "--description", help="Add description")
@click.pass_obj
def add_colormap(cfg: Cfg, sld_file, name, description):
    """Add a SLD file"""
    if not name:
        name = os.path.basename(sld_file.split(".")[0])
    try:
        color_map = create_colormap(name, sld_file, description)
        cfg.db.add_color_map(color_map)
    except Exception as e:
        click.echo(f"SLD File could not be converted. Reason: {e}")


@click.command()
@click.option("-n", "--name", help="Name the colormap, otherwise take the filename", required=True)
@click.pass_obj
def delete_colormap(cfg: Cfg, name):
    """Remove a SLD file"""
    cfg.db.delete_color_map(name)