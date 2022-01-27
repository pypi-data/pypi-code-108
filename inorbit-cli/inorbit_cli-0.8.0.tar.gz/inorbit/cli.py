# Copyright (c) 2021, InOrbit, Inc.
# All rights reserved.
import json
import logging
import os
import sys
from datetime import datetime

import click
import inorbit.exceptions
from inorbit import client
from tabulate import tabulate

logger = logging.getLogger(__name__)
logging_handler = logging.StreamHandler(sys.stderr)
logging_handler.setFormatter(logging.Formatter("%(levelname)s %(funcName)s:%(lineno)d %(message)s"))
logger.addHandler(logging_handler)

client.set_logger(logger)


def get_id_to_name_mapping(resource_name):
    """Returns a dictionary mapping resource id to resource name

    Args:
        resource_name (string): name of the resource to generate the mapping

    Returns:
        dict: dictionary mapping resource id to resource name
    """

    endpoint_raw_response = client.http_get(f"/{resource_name}").json()
    resource_id_to_name_mapping = {res["id"]: res["name"] for res in endpoint_raw_response}
    return resource_id_to_name_mapping


# This is the CLI entrypoint. It's hooked by `setup.py` (see `entry_points` parameter).
@click.group()
@click.option("--verbose", default=False, is_flag=True)
def cli(verbose):
    """InOrbit Command Line Interface tool

    The InOrbit CLI tool enable roboteers to interact
    with the InOrbit Cloud platform in order to manage
    robot configuration as code.
    """

    if verbose or "INORBIT_CLI_VERBOSE" in os.environ:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.ERROR)


@cli.group()
def get():
    """Get objects basic information."""
    pass


@cli.group()
def describe():
    """Describe objects and provide detailed information."""
    pass


@cli.group(invoke_without_command=True)
@click.option("-f", "filename", type=click.Path(exists=True, resolve_path=True))
@click.pass_context
def delete(ctx, filename):
    """Delete an object by id or by providing a configuration file."""

    # `delete` is used both as a command and as a command group. The command
    # accepts an option that is required but we cannot enforce it because other
    # commands under the `delete` group (e.g. `inorbit delete config foo`) fails.

    # Handle missing filename option. If there's invoked subcommand, it means
    # the `delete` was called with no option, so we show help and return.
    # If this gets executed as a callback for a subcommand, just ignore it.
    if not filename:
        if not ctx.invoked_subcommand:
            click.echo(ctx.get_help())
        return

    logger.debug(f"Reading file '{click.format_filename(filename)}'")

    # $ inorbit config delete -f sample_config.json
    # TODO: Add support for multidocument YAML files
    with open(file=filename, mode="r") as fd:
        file_config = json.loads(fd.read())

    logger.debug(f"Configuration read: {file_config}")
    config_objects_list = file_config if isinstance(file_config, list) else [file_config]
    for config_object in config_objects_list:
        required_keys = ["kind", "apiVersion", "metadata"]
        delete_config = {k: config_object[k] for k in required_keys}

        logger.debug(f"Object required data: {delete_config}")

        try:
            logger.debug("Clearing configuration")
            _ = client.http_post("/configuration/clear", post_data=delete_config)
        except inorbit.exceptions.InOrbitError as ex:
            raise click.ClickException(ex)

    click.echo(f"Configuration {filename} deleted successfully.")


@click.command(name="tags")
def get_tags():
    """Get all tags and relevant tag data."""
    response = client.http_get("/tags").json()
    response = [
        {
            "name": r["name"],
            "id": r["id"],
            "description": r.get("description", ""),
        }
        for r in response
    ]
    click.echo(tabulate(response, headers="keys"))


get.add_command(get_tags)


@click.command(name="collections")
def get_collections():
    """
    Get all collections and relevant collection data.

    Instead of showing all tags associated to a particular collection,
    it only shows the number of tags under each collection. To get more
    detailed data about collections use `describe_collections`.
    """

    response = client.http_get("/collections").json()
    response = [
        {
            "name": r["name"],
            "id": r["id"],
            "tags count": len(r["tags"]),
        }
        for r in response
    ]
    click.echo(tabulate(response, headers="keys"))


get.add_command(get_collections)


@click.command(name="robots")
def get_robots():
    """Get all robots and relevant robot data."""
    response = client.http_get("/robots").json()
    response = [
        {
            "name": r["name"],
            "id": r["id"],
            "agent version": r.get("agentVersion", ""),
        }
        for r in response
    ]
    click.echo(tabulate(response, headers="keys"))


get.add_command(get_robots)


@click.command(name="tags")
def describe_tags():
    """
    Describe all tags and detailed tag data.

    It also gathers the collection names so the collection id a tag is
    associated to it not shown alone.
    """

    # generate a `collection id` to `collection name` mapping to show
    # the collection name the tag is associated to.
    collection_id_to_name_mapping = get_id_to_name_mapping("collections")

    tags_raw_response = client.http_get("/tags").json()
    response = [
        {
            "name": r["name"],
            "description": r.get("description", ""),
            "collection id": r["collectionId"],
            "collection name": collection_id_to_name_mapping[r["collectionId"]],
        }
        for r in tags_raw_response
    ]

    click.echo(tabulate(response, headers="keys"))


describe.add_command(describe_tags)


@click.command(name="collections")
def describe_collections():
    """Describe all collections and detailed collection data."""
    collections_raw_response = client.http_get("/collections").json()
    for collection in collections_raw_response:
        click.echo(f"Collection '{collection['name']}' has {len(collection['tags'])} tags")
        collection_tags = [
            {"tag name": collection_tag["name"], "tag id": collection_tag["id"]}
            for collection_tag in collection["tags"]
        ]
        # Here `rst` table format has better appeareance and helps to understand
        # the data better. Consider using the same format for all `tabulate` calls.
        click.echo(tabulate(collection_tags, headers="keys", tablefmt="rst"))
        click.echo()


describe.add_command(describe_collections)


@click.command(name="robots")
def describe_robots():
    """Describe all robots and detailed robot data."""
    response = client.http_get("/robots").json()
    response = [
        {
            "name": r["name"],
            "id": r["id"],
            "agent version": r.get("agentVersion", ""),
            "online": r["agentOnline"],
            # TODO: decide which is the best date format and refactor to allow
            # changing it for all outputs or as a command parameter
            "last seen": datetime.fromtimestamp(r["updatedTs"] / 1000).isoformat(),
        }
        for r in response
    ]
    click.echo(tabulate(response, headers="keys"))


describe.add_command(describe_robots)


@click.command(name="apply")
@click.option("-f", "filename", required=True, type=click.Path(exists=True, resolve_path=True))
def apply_config(filename):
    """Apply configuration read from file."""
    logger.debug(f"Reading file '{click.format_filename(filename)}'")

    # TODO: Add support for multidocument YAML files
    with open(file=filename, mode="r") as fd:
        file_config = json.loads(fd.read())

    logger.debug(file_config)
    config_objects_list = file_config if isinstance(file_config, list) else [file_config]
    for config_object in config_objects_list:
        try:
            logger.info("Applying configuration")
            _ = client.http_post("/configuration/apply", post_data=config_object)
        except inorbit.exceptions.InOrbitError as ex:
            raise click.ClickException(ex)

    click.echo(f"Configuration {filename} applied successfully.")


# TODO: consider moving apply_config to CLI `config` group
# to unify UX e.g. `inorbit config apply`, `inorbit config list`
# (lean/mike) after first discussion we decided to use `$ inorbit apply -f`, `$ inorbit delete -f`
cli.add_command(apply_config)


@click.command(name="config")
@click.option(
    "--kind",
    "kind",
    type=str,
    required=True,
    help="Configuration kind.",
)
@click.option("--scope", "scope", type=str, default="account", help="Configuration object scope.")
@click.option("--dump/--summary", "dump", default=False, help="Dumps full objects to standard \
output or just a table with summary info.")
@click.argument("config_id", type=str, required=False)
def get_config(kind, scope, dump, config_id):
    """List all configurations."""

    query_data = {"kind": kind, "scope": scope, "format": "full" if dump else "short"}

    # configuration ID is optional, so if it's provided we add it as query parameter.
    if config_id:
        query_data["id"] = config_id

    response = client.http_get(
        path="/configuration/list",
        query_data=query_data,
    ).json()

    if dump:
        print(json.dumps(response["items"], indent=2))
        return

    response = [
        {
            "id": r["id"],
            "kind": r["kind"],
            "label": r["label"],
            "scope": r["scope"],
            "suppressed": r.get("suppressed", False),
        }
        for r in response["items"]
    ]
    click.echo(tabulate(response, headers="keys"))


get.add_command(get_config)


@click.command(name="config")
@click.argument("config_id", type=str)
@click.option(
    "--kind",
    "kind",
    type=str,
    required=True,
    help="Configuration kind.",
)
@click.option("--scope", "scope", type=str, default="account", help="Configuration object scope.")
def delete_config(config_id, kind, scope):
    """Clear configuration with the provided id. The default `account` scope
    can be overwritten by providing the `--scope` option."""

    response = client.http_post(
        path="/configuration/clear",
        post_data={
            "kind": kind,
            "apiVersion": "v0.1",
            "metadata": {"id": config_id, "scope": scope},
        },
    ).json()

    logger.debug(response)

    # TODO: improve response
    click.echo("OK")


delete.add_command(delete_config)
