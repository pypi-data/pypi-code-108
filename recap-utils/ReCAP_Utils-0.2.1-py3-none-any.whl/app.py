import typer

from recap_utils import graph, text

cli = typer.Typer()
cli.add_typer(graph.cli, name="graph")
cli.add_typer(text.cli, name="text")

if __name__ == "__main__":
    cli()
