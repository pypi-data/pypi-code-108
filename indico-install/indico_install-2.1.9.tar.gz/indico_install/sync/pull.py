import json
import re

import click
from click import confirm, secho

from indico_install.config import ConfigsHolder, SERVICES_YAML
from indico_install.utils import (
    options_wrapper,
    get_non_matching_images,
    get_nginx_conf,
)


@click.group("pull")
@click.pass_context
def pull(ctx):
    """Pull the latest information from the cluster into services yaml file"""
    pass


@pull.command("all")
@click.pass_context
@options_wrapper()
def pull_all(ctx, **kwargs):
    """Pull both backend images and frontend hashes to your services yaml"""
    ctx.invoke(pull_images, **kwargs)
    ctx.invoke(pull_frontend_hash, **kwargs)


@pull.command("images")
@click.pass_context
@options_wrapper()
def pull_images(ctx, *, yes):
    """Pull images from cluster"""
    configs = ConfigsHolder(config=SERVICES_YAML)

    for app, _, _, saved_image, cluster_image in get_non_matching_images(
        configs, only_first=True
    ):
        secho(f"{app}:\nOn Cluster: {cluster_image}\nOn Disk: {saved_image}")
        if yes or confirm("Save these changes to disk?"):
            secho(f"Saving changes for {app}", fg="green")
            configs["images"][app] = cluster_image
            configs.save()
        else:
            secho(f"Skipping changes for {app}", fg="yellow")


@pull.command("client")
@click.pass_context
@options_wrapper()
def pull_frontend_hash(ctx, *, yes):
    """Pull frontend hash from cluster"""
    configs = ConfigsHolder(config=SERVICES_YAML)
    output = get_nginx_conf()
    output_string = json.loads(output)
    app_hash = configs["frontend"]["hash"]

    try:
        cluster_hash = (
            re.search(r"set \$clientversion [^;]*", output_string)
            .group(0)
            .split(" ")[-1]
        )
    except Exception:
        secho("Could not find client version in cluster app-edge nginx.conf", fg="red")
    else:
        if cluster_hash != app_hash.strip():
            secho(f"Frontend hash\nOn Cluster: {cluster_hash}\nOn Disk: {app_hash}")
            if yes or confirm("Save these changes to disk?"):
                secho("Saving changes for frontend", fg="green")
                configs["frontend"]["hash"] = cluster_hash
                configs.save()
            else:
                secho("Skipping frontend changes", fg="yellow")

    secho("Done syncing changes", fg="green")
