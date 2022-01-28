"""Command line interface."""

import typer

cli = typer.Typer()


@cli.command()
def hello(name: str) -> None:
    typer.echo(f"Hello {name}")


@cli.command()
def other_command() -> None:
    pass


if __name__ == "__main__":
    cli()
