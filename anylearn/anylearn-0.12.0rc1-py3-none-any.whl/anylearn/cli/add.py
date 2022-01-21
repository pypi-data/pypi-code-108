import click

import anylearn.cli.add_algorithm
import anylearn.cli.add_dataset


@click.group("add")
def commands():
    """
    Add local algorithm or dataset to local Anylearn project.
    """
    pass

commands.add_command(anylearn.cli.add_algorithm.commands)
commands.add_command(anylearn.cli.add_dataset.commands)
