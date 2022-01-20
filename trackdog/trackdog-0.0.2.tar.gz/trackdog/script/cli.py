import click

from trackdog.script.get import get
from trackdog.script.view import view

@click.group()
def cli():
    pass


@click.command()
def run():
    """Run the experiment"""
    click.echo('run')


cli.add_command(view)
cli.add_command(run)
cli.add_command(get)

if __name__ == '__main__':
    cli()