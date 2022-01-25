from datetime import datetime, timezone
from shlex import split
from typing import Optional, List

import click

from grid.cli.client import Grid
from grid.cli.observables.base import create_table
from grid.cli.types import ObservableType
from grid.sdk import env
from grid.sdk.experiments import Experiment, ExperimentState
from grid.sdk.runs import list_runs, Run, RunState
from rich.console import Console
from rich.table import Table
from grid.cli import rich_click
from yaspin import yaspin
from grid.cli.utilities import is_experiment, get_abs_time_difference, string_format_timedelta, get_param_values, \
    get_experiment_duration_string, get_experiment_queued_duration_string
from grid.sdk.rest.exceptions import GridException


def _check_is_experiment(ctx, _param, value):
    """Callback that checks if a value is an experiment."""
    if not value:
        return value

    if is_experiment(value):
        raise click.BadArgumentUsage(f"Must pass a Run name, not Experiment: {value}")

    return value


@rich_click.command()
@rich_click.argument('run', type=str, nargs=1, required=False, callback=_check_is_experiment)
@click.option(
    '--global', 'is_global', type=bool, is_flag=True, help='Fetch status from all collaborators when flag is passed'
)
def status(run: Optional[str] = None, is_global: Optional[bool] = False) -> None:
    """Checks the status of Runs, Experiments, and Sessions."""
    # Initializing variables
    spinner_load_type = "Runs"
    history_runs = []
    if run:
        spinner_load_type = "Experiments"
    spinner = yaspin(text=f"Loading {spinner_load_type} in {env.CONTEXT}...", color="yellow")
    console = Console()

    # Fetching runs/experiments and printing them onto the terminal
    try:
        spinner.start()
        runs = list_runs(is_global=is_global)
        if not run:
            table = render_runs(runs, is_global=is_global)
            history_runs = len(runs) - len(table.rows)
        else:
            for run_obj in runs:
                if run_obj.name == run:
                    if len(run_obj.experiments) == 0:
                        raise RuntimeError(f"Run {run} has no experiments")
                    # TODO - this is working because of the order which is_unshallow
                    #   and is_delted being called. We should deprecate is_deleted and
                    #   instead use _status on all resources
                    non_deleted_exps = [exp for exp in run_obj.experiments if exp.status != ExperimentState.DELETED]
                    table = render_experiments(non_deleted_exps)
                    break
            else:
                # if break hasn't been called, then the run wasn't found
                raise RuntimeError(
                    f"Run {run} not found in the cluster {env.CONTEXT}. If you are "
                    f"looking for a run in a different cluster, try setting the default "
                    f"cluster with `grid user set_default_cluster <cluster-name>` first"
                )

        spinner.text = 'Done!'
        spinner.ok("✔")
        console.print(table)
    except GridException as e:
        spinner.fail("✘")
        raise click.ClickException(str(e))
    except Exception as e:
        spinner.fail("✘")
        raise click.ClickException(str(e))
    finally:
        spinner.stop()

    # Optionally fetching sessions, if run name is not passed
    if not run:
        if history_runs > 0:
            click.echo(f'{history_runs} Run(s) are not active. Use `grid history` ' 'to view your Run history.\n')
        client = Grid()
        client.status(kind=ObservableType.INTERACTIVE, identifiers=[], is_global=is_global)


def render_runs(runs: List['Run'], is_global: bool) -> Table:
    if is_global:
        table_cols = [
            'Run',
            'Status',
            'Created By',
            'Duration',
            'Experiments',
            'Running',
            'Queued',
            'Completed',
            'Failed',
            'Stopped',
        ]
    else:
        table_cols = [
            'Run',
            'Status',
            'Duration',
            'Experiments',
            'Running',
            'Queued',
            'Completed',
            'Failed',
            'Stopped',
        ]

    table = create_table(table_cols)
    table_rows = 0
    for run in runs:
        # we only have 3 statuses for runs
        # running (if something is running)
        is_running = run.status == RunState.RUNNING

        # We classify queued and pending into queued
        n_queued = run.experiment_counts.get(RunState.PENDING.value, 0)
        n_running = run.experiment_counts.get(RunState.RUNNING.value, 0)
        n_failed = run.experiment_counts.get(RunState.FAILED.value, 0)
        n_succeeded = run.experiment_counts.get(RunState.SUCCEEDED.value, 0)
        n_cancelled = run.experiment_counts.get(RunState.CANCELLED.value, 0)

        # If anything is queued, the the status of the entire
        # run is queued. All other statuses are running in
        # all other conditions.
        if n_queued > 0:
            run_status = "queued"

        # If you have anything running (and nothing queued)
        # then, mark the run as running.
        elif is_running:
            run_status = "running"

        # If it doesn't match the conditions above, just
        # skip this row and add the row and put it in history.
        else:
            # don't render table because it should be in history
            continue

        # Calculate the duration column
        delta = get_abs_time_difference(datetime.now(timezone.utc), run.created_at)
        duration_str = string_format_timedelta(delta)

        if is_global:
            table.add_row(
                run.name, run_status, run.user.username, duration_str, str(len(run.experiments)), str(), str(n_queued),
                str(n_succeeded), str(n_failed), str(n_cancelled)
            )
        else:
            table.add_row(
                run.name, run_status, duration_str, str(len(run.experiments)), str(n_running), str(n_queued),
                str(n_succeeded), str(n_failed), str(n_cancelled)
            )
        #  Let's count how many rows have been added.
        table_rows += 1
    return table


def render_experiments(experiments: List['Experiment']) -> Table:
    base_columns = [
        'Experiment',
        'Command',
        'Status',
        'Queued Duration',
        'Run Duration',
    ]
    if not experiments:
        return create_table(base_columns)
    command = experiments[0].command
    hparams = [tok.replace('--', '') for tok in command if '--' in tok]

    table_columns = base_columns + hparams
    table = create_table(table_columns)

    for experiment in experiments:
        # Split hparam vals
        command = experiment.command
        base_command, *hparam_vals = get_param_values(" ".join(command))

        duration_str = get_experiment_duration_string(
            created_at=experiment.created_at,
            started_running_at=experiment.start_timestamp,
            finished_at=experiment.finish_timestamp
        )
        queued_duration_str = get_experiment_queued_duration_string(
            created_at=experiment.created_at,
            started_running_at=experiment.start_timestamp,
        )
        table.add_row(
            experiment.name, base_command, experiment.status.value, queued_duration_str, duration_str, *hparam_vals
        )
    return table
