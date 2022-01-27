import typer

from ingeniictl.cli import infra

app = typer.Typer()
app.add_typer(infra.app, name="infra")
