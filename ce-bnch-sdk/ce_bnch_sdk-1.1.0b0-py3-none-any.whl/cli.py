import typer

from benchling_sdk.benchbots.cli import benchbots_cli

cli = typer.Typer()
cli.add_typer(
    benchbots_cli,
    name="benchbot",
    help="Benchbots are portable and transferable integrations administered within Benchling.",
)

if __name__ == "__main__":
    cli()
