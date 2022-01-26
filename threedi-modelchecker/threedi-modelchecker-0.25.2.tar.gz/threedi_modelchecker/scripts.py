from threedi_modelchecker import exporters
from threedi_modelchecker.checks.base import CheckLevel
from threedi_modelchecker.model_checks import ThreediModelChecker
from threedi_modelchecker.schema import ModelSchema
from threedi_modelchecker.threedi_database import ThreediDatabase

import click


@click.group()
@click.option(
    "-s",
    "--sqlite",
    type=click.Path(exists=True, readable=True),
    help="Path to an sqlite (spatialite) file",
)
@click.option("-d", "--database", help="PostGIS database name to connect to")
@click.option("-h", "--host", help="PostGIS database server host")
@click.option("-p", "--port", default=5432, help="PostGIS database server port")
@click.option("-u", "--username", help="PostGIS database username")
@click.option("-u", "--password", help="PostGIS database password")
@click.pass_context
def threedi_modelchecker(ctx, sqlite, database, host, port, username, password):
    """Checks the threedi-model for errors / warnings / info messages"""
    ctx.ensure_object(dict)

    if sqlite:
        sqlite_settings = {"db_path": sqlite, "db_file": sqlite}
        db = ThreediDatabase(
            connection_settings=sqlite_settings, db_type="spatialite", echo=False
        )
    else:
        postgis_settings = {
            "host": host,
            "port": port,
            "database": database,
            "username": username,
            "password": password,
        }
        db = ThreediDatabase(
            connection_settings=postgis_settings, db_type="postgres", echo=False
        )
    ctx.obj["db"] = db


@threedi_modelchecker.command()
@click.option("-f", "--file", help="Write errors to file, instead of stdout")
@click.option(
    "-l",
    "--level",
    type=click.Choice([x.name for x in CheckLevel], case_sensitive=False),
    default="ERROR",
    help="Minimum check level.",
)
@click.pass_context
def check(ctx, file, level):
    """Checks the threedi model schematisation for errors."""
    level = level.upper()
    if level == "ERROR":
        msg = "errors"
    elif level == "WARNING":
        msg = "errors or warnings"
    else:
        msg = "errors, warnings or info messages"
    click.echo("Parsing threedi-model for any %s" % msg)
    if file:
        click.echo("Model errors will be written to %s" % file)

    mc = ThreediModelChecker(ctx.obj["db"])
    model_errors = mc.errors(level=level)

    if file:
        exporters.export_to_file(model_errors, file)
    else:
        exporters.print_errors(model_errors)

    click.echo("Finished processing model")


@threedi_modelchecker.command()
@click.option(
    "-r", "--revision", default="head", help="The schema revision to migrate to"
)
@click.pass_context
def migrate(ctx, revision):
    """Migrate the threedi model schematisation to the latest version."""
    schema = ModelSchema(ctx.obj["db"])
    click.echo("The current schema revision is: %s" % schema.get_version())
    click.echo("Running alembic upgrade script...")
    schema.upgrade(revision=revision)
    click.echo("The migrated schema revision is: %s" % schema.get_version())


if __name__ == "__main__":
    threedi_modelchecker()
