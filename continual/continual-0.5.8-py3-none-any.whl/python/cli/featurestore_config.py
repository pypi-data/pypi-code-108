#!/usr/bin/env python3

import typer
import json

from continual.python.sdk.featurestore_config import FeaturestoreConfig
from continual.python.cli import utils

from enum import Enum


app = typer.Typer(help="Manage local data warehouse configurations.")

allowed_fs_types = ["snowflake", "continual"]


class FeaturestoreType(str, Enum):
    snowflake = "snowflake"
    # continual = "continual"
    bigquery = "bigquery"
    redshift = "redshift"
    # synapse = "synapse"


@app.command("list")
@utils.exit_on_error
def list(
    details: bool = typer.Option(False, help="Print full details."),
    unmask: bool = typer.Option(
        False, help="Print passwords in plaintext", hidden=True
    ),
):
    """List all data warehosue configs."""
    fsconfig = FeaturestoreConfig()
    fsconfig.list(details, unmask)


@app.command("print")
@utils.exit_on_error
def print(
    name: str = typer.Argument(..., help="Data warehouse config name to retrieve.")
):
    """Print a single data warehouse config."""
    fsconfig = FeaturestoreConfig()
    fsconfig.get(name)


@app.command("create")
@utils.exit_on_error
def create(
    name: str = typer.Argument(..., help="Data warehouse config name to create."),
    type: FeaturestoreType = typer.Option(None, help="Data warehouse type."),
    dict_string: str = typer.Option(
        ..., help="String of dictionary values to use for data warehouse configuration."
    ),
):
    """
    Creates a data warehouse configuration with the dictionary string passed as parameters.
    The parameters needed are dependent upon your data warehouse type.

    Snowflake: DATABASE, USERNAME, PASSWORD, HOST, WAREHOUSE, DB_SCHEMA, ROLE

    BigQuery: AUTH_FILE, DATASET

    REDSHIFT: DATABASE, USERNAME, PASSWORD, HOST, PORT, DB_SCHEMA

    Example:

            continual warehouse-config myFS --type snowflake --dict-string '{"DATABASE" : "myDB", "USERNAME" : "myUser", "PASSWORD" : "myPass", "HOST" : "myHost", "WAREHOUSE" : "myWarehouse"}'

    Currently only types snowflake, bigquery, and redshift are supported.
    """
    fsconfig = FeaturestoreConfig()
    fsconfig.delete(name)
    if type.lower() in allowed_fs_types:
        config = json.loads(dict_string)
        config = {x.upper(): config[x] for x in config}
        config["TYPE"] = type.value.lower()
        fsconfig.create(name, config)
        typer.secho("Successfully created section %s" % name, fg="green")
    else:
        typer.secho("Featurestore type %s not supported." % type.value, fg="red")


@app.command("delete")
@utils.exit_on_error
def delete(
    name: str = typer.Argument(..., help="Data warehouse config name to delete.")
):
    """Deletes a single data warehouse config."""
    fsconfig = FeaturestoreConfig()
    fsconfig.delete(name)
    typer.secho("Successfully deleted section %s" % name, fg="green")


@app.command("update")
@utils.exit_on_error
def update(
    name: str = typer.Argument(..., help="Data warehouse config name to retrieve."),
    key: str = typer.Option(..., help="Data warehouse config key to set."),
    value: str = typer.Option(..., help="Data warehouse config value to use."),
):
    """Updates a single key-value pair in a data warehouse config."""

    fsconfig = FeaturestoreConfig()
    key = key.upper()
    fsconfig.update(name, key, value)
    typer.secho("Successfully updated section %s" % name, fg="green")
