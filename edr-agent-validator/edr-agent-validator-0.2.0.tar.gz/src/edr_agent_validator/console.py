from pathlib import Path
import socket
from typing import List, Optional

import typer

from edr_agent_validator.files import (
    create_file as new_file,
    delete_file as del_file,
    modify_file as append_file,
    schema as file_activity_schema,
)
from edr_agent_validator.network import (
    NetworkProtocol,
    schema as net_schema,
    send_data as transmit_data,
)
from edr_agent_validator.process import schema as proc_schema, start_process

from . import __version__

app = typer.Typer(add_completion=False)


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"EDR Agent Validator Version: {__version__}")
        raise typer.Exit()


@app.callback()
def cli(
    ctx: typer.Context,
    log_file: typer.FileTextWrite = typer.Option(
        "activity_log.txt",
        mode="a",
        help="The path to write the activity log to.",
        show_default=True,
    ),
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True
    ),
) -> None:
    """An EDR Agent Validator tool."""
    ctx.obj = log_file


@app.command(context_settings={"ignore_unknown_options": True})
def launch_process(
    ctx: typer.Context,
    executable: Path = typer.Argument(
        ...,
        exists=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
        help="Path to the binary to run",
    ),
    args: List[str] = typer.Argument(
        None, help="Any arguments to provide to the binary."
    ),
) -> None:
    """
    Launch a specified executable with arguments.
    """
    ctx.obj.write(f"{proc_schema.dump(start_process(executable, args))}\n")


@app.command()
def create_file(
    ctx: typer.Context,
    file: Path = typer.Argument(
        ...,
        exists=False,
        dir_okay=False,
        writable=True,
        readable=True,
        resolve_path=True,
        help="Path to the file to be created",
    ),
):
    """
    Create a file at the specified location.
    """
    ctx.obj.write(f"{file_activity_schema.dump(new_file(file))}\n")


@app.command()
def modify_file(
    ctx: typer.Context,
    file: Path = typer.Argument(
        ...,
        exists=True,
        dir_okay=False,
        writable=True,
        readable=True,
        resolve_path=True,
        help="Path to the file to be modified",
    ),
    contents: str = typer.Argument(
        ..., help="A string that you want to append to the file."
    ),
):
    """
    Modify a file by adding a given string.
    """
    ctx.obj.write(f"{file_activity_schema.dump(append_file(file, contents))}\n")


@app.command()
def delete_file(
    ctx: typer.Context,
    file: Path = typer.Argument(
        ...,
        exists=True,
        dir_okay=False,
        writable=True,
        readable=False,
        resolve_path=True,
        help="Path to the file to be deleted",
    ),
):
    """
    Delete a specified file.
    """
    ctx.obj.write(f"{file_activity_schema.dump(del_file(file))}\n")


@app.command()
def send_data(
    ctx: typer.Context,
    local_host: str = typer.Option(
        socket.gethostbyname(socket.gethostname()),
        "--local_host",
        "-lh",
        help="Local address to bind to.",
    ),
    local_port: int = typer.Option(
        8080,
        "--local_port",
        "-lp",
        min=0,
        max=65535,
        help="Local port to bind to.",
    ),
    dest_host: str = typer.Option(
        ..., "--dest_host", "-dh", help="Remote addess/hostname to connect to."
    ),
    dest_port: int = typer.Option(
        ...,
        "--dest_port",
        "-dp",
        min=0,
        max=65535,
        help="Remote port to connect to.",
    ),
    protocol: NetworkProtocol = typer.Option(
        NetworkProtocol.TCP.value, help="Network protocol to use to send data."
    ),
    data: str = typer.Argument(..., help="Data to transmit."),
):
    """
    Transmit arbitrary bytes over UDP or TCP from a source ip:port to a dest ip:port.
    """
    ctx.obj.write(
        f"{net_schema.dump(transmit_data(local_host, local_port, dest_host, dest_port, protocol, data))}\n"
    )
