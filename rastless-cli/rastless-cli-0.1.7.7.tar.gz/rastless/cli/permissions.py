import click

from rastless.config import Cfg
from rastless.db.models import PermissionModel


@click.command()
@click.option('-p', '--permission', required=True, type=str,
              help='Role e.g role#<client>:<client_role>, user#<username>')
@click.option('-l', '--layer_ids', help='Layer id', required=True, type=str, multiple=True)
@click.pass_obj
def add_permission(cfg: Cfg, permission, layer_ids):
    """Add a role to one or multiple layers."""
    permissions = [PermissionModel(permission=permission, layer_id=layer) for layer in layer_ids]
    cfg.db.add_permissions(permissions)
    click.echo("Role was successfully added to layers")


@click.command()
@click.option('-p', '--permissions', help='Permission name e.g role#<client>:<client_role>, user#<username>',
              required=True, type=str, multiple=True)
@click.pass_obj
def delete_permission(cfg: Cfg, permissions):
    """Delete one or multiple permissions."""

    for permission in permissions:
        cfg.db.delete_permission(permission)

    click.echo("Roles were successfully deleted")
