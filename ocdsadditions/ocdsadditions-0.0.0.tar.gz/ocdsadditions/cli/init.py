import click

from ocdsadditions.library import init_repository


@click.command()
@click.argument("directory")
def cli(directory: str):
    click.echo("Initializing a data repository")
    init_repository(directory)


if __name__ == "__main__":
    cli()
