import typer
from rich.console import Console

console = Console()
app = typer.Typer()


@app.command()
def not_implemented() -> None:
    console.print("Noting implemented yet")


typer_click_object = typer.main.get_command(app)

if __name__ == "__main__":
    app()
