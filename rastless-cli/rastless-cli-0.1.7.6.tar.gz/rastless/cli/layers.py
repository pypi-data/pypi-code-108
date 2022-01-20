import click

from rastless.config import Cfg
from rastless.db.base import str_uuid
from rastless.db.models import LayerModel, LayerStepModel, PermissionModel
from rastless.core.cog import layer_is_valid_cog, create_s3_cog_info, upload_cog_file, transform_upload_cog,\
    get_layer_info


@click.command()
@click.pass_obj
@click.option("-cl", "--client", required=True, type=str)
@click.option("-pr", "--product", required=True, type=str)
@click.option("-t", "--title", required=True, type=str)
@click.option("-id", "--layer-id", default=str_uuid, type=str)
@click.option("-cm", "--colormap", type=str)
@click.option("-u", "--unit", type=str)
@click.option("-b", "--background-id", type=str)
@click.option("-d", "--description", type=str)
@click.option("-r", "--region-id", default=1, type=int)
@click.option("-pe", "--permissions", type=str, multiple=True)
def create_layer(cfg: Cfg, permissions, **kwargs):
    layer = LayerModel.parse_obj(kwargs)
    cfg.db.add_layer(layer)

    permission_models = [PermissionModel(permission=permission, layer_id=layer.layer_id) for permission in permissions]
    cfg.db.add_permissions(permission_models)

    click.echo(f"Created layer with id: {layer.layer_id}")
    return layer.layer_id


@click.command()
@click.pass_obj
@click.argument('filename', type=click.Path(exists=True))
@click.option("-d", "--datetime", required=True, type=str)
@click.option("-s", "--sensor", required=True, type=str)
@click.option("-l", "--layer-id", required=True, type=str)
@click.option("-t", "--temporal-resolution", default="daily", type=str)
@click.option("-p", "--profile", type=click.Choice(["deflate", "jpeg"]), default="deflate")
def create_timestep(cfg: Cfg, filename, datetime, sensor, layer_id, temporal_resolution, profile):
    s3_cog = create_s3_cog_info(cfg.s3.bucket_name, layer_id, filename)
    layer_info = get_layer_info(filename)

    if layer_is_valid_cog(filename):
        uploaded = upload_cog_file(s3_cog)
    else:
        uploaded = transform_upload_cog(s3_cog, profile)

    if not uploaded:
        raise click.ClickException(f"File {filename} could not be uploaded. Please try again.")

    layer_step = LayerStepModel(layer_id=layer_id, cog_filepath=s3_cog.s3_path, datetime=datetime, sensor=sensor,
                                temporal_resolution=temporal_resolution, maxzoom=layer_info.maxzoom,
                                minzoom=layer_info.minzoom,
                                bbox=layer_info.bbox_wgs84, resolution=layer_info.resolution)
    cfg.db.add_layer_step(layer_step)


@click.command()
@click.pass_obj
def list_layers(cfg: Cfg):
    """List all layers."""
    layers = cfg.db.list_layers()
    for layer in layers:
        click.echo(layer)


@click.command()
@click.pass_obj
@click.option("-l", "--layer-id", required=True, type=str)
def delete_layer(cfg: Cfg, layer_id):
    click.confirm(f'Do you really want to delete layer {layer_id}?', abort=True)

    layer_steps = cfg.db.get_layer_steps(layer_id)
    cfg.s3.delete_layer_steps(layer_steps)
    cfg.db.delete_layer(layer_id=layer_id)
