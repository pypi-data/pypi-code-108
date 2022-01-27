import sys
from dotenv import load_dotenv

sys.path.append(".")
sys.path.append("..")

import click

from redbeard_cli.commands.lookups import cli as lookup_cli
from redbeard_cli.commands.idgraph import cli as idgraph_cli
from redbeard_cli.commands.init import cli as init_cli
from redbeard_cli.commands.data_connections import cli as data_connections_cli
from redbeard_cli.commands.generate import cli as generator_cli


@click.group()
def cli():
    pass


load_dotenv(dotenv_path="./.env", override=True)
cli.add_command(lookup_cli.lookup)
cli.add_command(idgraph_cli.habu_id_graph)
cli.add_command(init_cli.init)
cli.add_command(data_connections_cli.data_connections)
cli.add_command(generator_cli.data_generator)


