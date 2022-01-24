import click

from redbeard_cli import snowflake_utils
from redbeard_cli.commands.init import (
    habu_setup as habu_setup_command
)


@click.group()
def init():
    pass


@init.command(
    help="""Initialize Full Habu Snowflake framework.\n
    This will create all the objects required to run the Habu Agent in the specified Snowflake account.\n
    This includes:\n
      * Databases:\n
        * HABU_CLEAN_ROOM_COMMON\n
        * HABU_DATA_CONNECTIONS\n
    """
)
@click.option('-o', '--organization_id', required=True, help='Habu Organization ID')
@click.option('-c', '--config-file', default="./habu_snowflake_config.yaml", help='Snowflake account configuration file')
@click.option('-h', '--habu-account-id', default="JYA07515", help='Habu Snowflake account Id used for orchestration')
@click.option('-r', '--share-restrictions', default="true", help='Enforce share restrictions')
def habu_framework(habu_account_id: str, config_file: str, organization_id: str, share_restrictions: bool):
    account_id, sf_connection = snowflake_utils.new_connection_from_yaml_file(config_file)
    habu_setup_command.init_framework(sf_connection, organization_id, account_id, share_restrictions, habu_account_id)

@init.command()
@click.option('-o', '--organization_id', required=True, help='Habu Organization ID')
@click.option('-c', '--config-file', default="./habu_snowflake_config.yaml")
@click.option('-h', '--habu-account-id', default="JYA07515", help='Habu Snowflake account Id used for orchestration')
def habu_shares(habu_account_id: str, config_file: str, organization_id: str):
    account_id, sf_connection = snowflake_utils.new_connection_from_yaml_file(config_file)
    habu_setup_command.init_habu_shares(sf_connection, organization_id, account_id, habu_account_id)
