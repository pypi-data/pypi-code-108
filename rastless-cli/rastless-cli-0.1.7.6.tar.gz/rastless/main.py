import click

from rastless.config import Cfg
from rastless.cli import management, layers, colormaps, permissions
from rastless import settings


@click.group()
@click.option('--dev', is_flag=True)
@click.pass_context
def cli(ctx, dev):
    table_name = settings.RASTLESS_TABLE_NAME_DEV if dev else settings.RASTLESS_TABLE_NAME
    bucket_name = settings.RASTLESS_BUCKET_NAME_DEV if dev else settings.RASTLESS_BUCKET_NAME

    ctx.obj = Cfg(table_name=table_name, bucket_name=bucket_name)


# Management
cli.add_command(management.check_aws_connection)

# Layers
cli.add_command(layers.create_layer)
cli.add_command(layers.create_timestep)
cli.add_command(layers.list_layers)
cli.add_command(layers.delete_layer)

# Colormaps
cli.add_command(colormaps.add_colormap)
cli.add_command(colormaps.delete_colormap)

# Permissions
cli.add_command(permissions.add_permission)
cli.add_command(permissions.delete_permission)

if __name__ == '__main__':
    cli()
