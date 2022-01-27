import click

from redbeard_cli import snowflake_utils
from redbeard_cli.commands.idgraph import (
    habu_share as habu_share_command
)


@click.group()
@click.option('--config', default="./habu_snowflake_config.yaml")
def habu_id_graph():
    pass


@habu_id_graph.command()
def init(config_file: str):
    account_id, sf_connection = snowflake_utils.new_connection_from_yaml_file(config_file)
    habu_share_command.init(sf_connection)


@habu_id_graph.command()
@click.argument("account_id")
def share(config_file: str):
    account_id, sf_connection = snowflake_utils.new_connection_from_yaml_file(config_file)
    habu_share_command.share_id_graph_with_account(sf_connection, account_id)
