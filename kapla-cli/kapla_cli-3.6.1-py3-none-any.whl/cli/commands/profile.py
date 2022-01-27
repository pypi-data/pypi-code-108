from pathlib import Path
from shlex import quote
from typing import Optional

import typer
from kapla.cli.console import console
from kapla.cli.utils import run

app = typer.Typer(
    name="profile",
    add_completion=False,
    no_args_is_help=True,
    invoke_without_command=False,
    help="Application profiling toolkit",
)


@app.command("run")
def run_prof(
    script: Optional[str] = typer.Argument(None, help="Script to run"),
    module: Optional[str] = typer.Option(None, "-m", "--module", help="Module to run"),
    output: str = typer.Option(None, "-o", "--output", help="Output file"),
) -> None:
    out_opt = f" -o {output}" if output else ""
    if module:
        rest = " -m " + module
    elif script:
        rest = " " + quote(script)
        script = script
    else:
        console.print(
            "Wrong usage: Either [bold]-m[/bold]/[bold]--module[/bold] option or a [bold]positional argument[/bold] must be present",
            style="red",
        )
        raise typer.Exit(1)
    cmd = f"python -m cProfile {out_opt} {rest}"
    console.print(f"[bold blue]Profiling[/bold blue] with command: {cmd}")
    run(cmd)


@app.command("viz")
def viz_prof(
    profile_report: Path = typer.Argument(..., help="Path to .prof file")
) -> None:
    run(f"snakeviz {profile_report}")
