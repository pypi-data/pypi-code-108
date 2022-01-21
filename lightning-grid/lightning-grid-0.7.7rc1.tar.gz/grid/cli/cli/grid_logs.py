from typing import Any, Dict, Optional

import click
import yaspin

from grid.cli import rich_click
from grid.cli.core import Experiment
from grid.cli.utilities import is_experiment


def _format_log_lines(line: Dict[str, Any]) -> str:
    """Formats a log line for the terminal"""
    # If no timestamps are returned, fill the field
    # with dashes.
    log_type = click.style(line["type"], fg="magenta")
    if not line['timestamp']:
        # Timestamps have 32 characters.
        timestamp = click.style("-" * 32, fg="green")
    else:
        timestamp = click.style(line["timestamp"], fg="green")

    return f"[{log_type}] [{timestamp}] {line['message']}"


@rich_click.command()
@rich_click.argument("experiment", help="Name of experiment you would like to fetch logs for.", type=str, nargs=1)
@click.option(
    "--show-build-logs", type=bool, help="Shows build logs if not shown by default.", default=None, is_flag=True
)
@click.option("-l", "--tail-lines", type=int, help="Number of lines to show from the end.")
def logs(experiment: str, show_build_logs: Optional[bool] = None, tail_lines: Optional[int] = None) -> None:
    """Shows stdout logs associated with some EXPERIMENT.

    This includes both build and experiment logs.
    """

    if not is_experiment(experiment):
        message = f"""
    Experiment ID not supplied, defaulting to {experiment}-exp0.
    To view all experiments for the run:

    `grid status {experiment}`
    """
        click.echo(message)
        experiment = experiment + "-exp0"

    spinner = yaspin.yaspin(text="Fetching logs ...", color="yellow")
    spinner.start()

    try:
        # get experiment with all its metadata
        experiment = Experiment(experiment)
        experiment.refresh()

        # fetch and print stdout logs
        spinner.stop()
        for line in experiment.logs(build_logs=show_build_logs, tail_lines=tail_lines):
            click.echo(_format_log_lines(line), nl=False)

        # let the user know that certain logs are only available if experiment has run
        if experiment.is_preparing:
            styled_status = click.style(experiment.status, fg="blue")
            click.echo(f"Experiment is {styled_status}. Logs will be available when experiment starts.")
            return

        if show_build_logs is False and experiment.is_queued:
            click.echo("\n\nBuild logs skipped. Use --show-build-logs to see them.\n")
            return

    # always stop spinner otherwise it'll keep running on a background thread
    finally:
        spinner.stop()
