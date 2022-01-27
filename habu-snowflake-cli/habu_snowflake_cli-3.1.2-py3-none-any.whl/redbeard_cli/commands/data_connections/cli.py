import click

from redbeard_cli import snowflake_utils
from redbeard_cli.commands.data_connections import (
    data_connections as data_connections_command
)
from redbeard_cli.commands.lookups import lookups


@click.group()
def data_connections():
    pass


@data_connections.command()
@click.option('-c', '--config-file', default="./habu_snowflake_config.yaml")
def ls(config_file: str):
    # list all data connections that have been shared with habu
    account_id, sf_connection = snowflake_utils.new_connection_from_yaml_file(config_file)
    data_connections_command.ls(sf_connection)


@data_connections.command()
@click.option('-d', '--db', required=True, help='Snowflake Database that contains the source table or view')
@click.option('-s', '--schema', required=True, help='Snowflake Schema that contains the source table or view')
@click.option('-t', '--table', required=True, help='Snowflake Source Table or View')
@click.option('-c', '--config-file', default="./habu_snowflake_config.yaml")
def inspect(config_file: str, db: str, schema: str, table: str):
    account_id, sf_connection = snowflake_utils.new_connection_from_yaml_file(config_file)
    data_connections_command.inspect(
        sf_connection, db.upper(), schema.upper(), table.upper()
    )

@data_connections.command()
@click.option('-o', '--organization_id', required=True, help='Habu Organization ID')
@click.option('-d', '--db', required=True, help='Snowflake Database that contains the source table or view')
@click.option('-s', '--schema', required=True, help='Snowflake Schema that contains the source table or view')
@click.option('-t', '--table', required=True, help='Snowflake Source Table or View')
@click.option(
    '-y', '--dataset-type', required=True, type=click.Choice(lookups.DATASET_TYPE_NAMES, case_sensitive=True),
    help='The dataset types.  For available types, please run redbeard datasets ls'
)
@click.option(
    '-l', '--lookup-columns', required=True,
    help='Comma separated list of columns from table or view that are lookup (or dimension) columns in questions'
)
@click.option(
    '-i', '--identity-type-column', required=False,
    help="""the type and name of the identity column in the data connection table 
    (e.g., SHA256:email_sh256 or MAID:maid.
    For a full list of Identities, run `redbeard lookups identity-types`"""
)
@click.option('-c', '--config-file', default="./habu_snowflake_config.yaml")
def add(config_file: str, organization_id: str, db: str, schema: str, table: str,
        dataset_type: str, identity_type_column: str, lookup_columns: str):
    if not lookups.valid_dataset(dataset_type):
        print("*** invalid dataset type ***")
        lookups.ls_datasets()

    id_type_parts = identity_type_column.split(':')
    if len(id_type_parts) != 2:
        print("*** invalid format for identity type column.  please use 'TYPE:COL_NAME, e.g., SHA_256:email_sha256, or MAID:maid ***")
        return

    identity_type = id_type_parts[0]
    identity_column = id_type_parts[1]
    if not lookups.valid_identity_type(identity_type):
        print("*** invalid identity type ***")
        lookups.ls_identity_types()
        return

    account_id, sf_connection = snowflake_utils.new_connection_from_yaml_file(config_file)
    added = data_connections_command.add(
        sf_connection, organization_id,
        db.upper(), schema.upper(), table.upper(),
        dataset_type, identity_type, identity_column.upper(),
        [c.upper() for c in lookup_columns.split(',')]
    )
    if added:
        data_connections_command.ls(sf_connection)
