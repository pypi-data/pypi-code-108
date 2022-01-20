from typing import List, Any
import typer
import logging
import signal
from rich.logging import RichHandler
from rich.console import Console
from functools import partial

from fact_lake.config import get_logger
from fact_lake.server import Server

from os import environ as env


console = Console()
typer_app = typer.Typer()


FORMAT = "%(message)s"

log = get_logger("cli")

# * Allow client side forking
# c.f.: https://github.com/grpc/grpc/blob/master/doc/fork_support.md
env["GRPC_ENABLE_FORK_SUPPORT"] = "true"
env["GRPC_POLL_STRATEGY"] = "poll"


def sigusr1handler(server: Server, signum: int, frame: Any) -> None:
    server.print_process_status()


@typer_app.callback()
def main(
    ctx: typer.Context,
    verbose: List[bool] = typer.Option(
        [False],
        "--verbose",
        "-v",
        help="Output more details on what is happening. Use multiple times for more details.",
    ),
) -> None:
    level = "WARNING"
    if len(verbose) == 1:
        level = "INFO"
    if len(verbose) >= 2:
        level = "DEBUG"

    logging.basicConfig(
        level=level, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
    )


@typer_app.command()
def run() -> None:
    server = Server(console=console)
    signal.signal(signal.SIGUSR1, partial(sigusr1handler, server))
    server.run()


# TODO status command

if __name__ == "__main__":
    typer_app()
