import click

from grid.cli import rich_click
from grid.cli.client import Grid
from grid.cli.utilities import is_experiment
import grid.sdk.env as env


@rich_click.command()
@rich_click.argument('run_or_experiment', type=str, nargs=1, required=True)
def view(run_or_experiment: str):
    """Grid view opens a web UI page details the output of some RUN_OR_EXPERIMENTS."""
    if is_experiment(run_or_experiment):
        view_experiment(experiment_name=run_or_experiment)
    else:
        view_run(run_name=run_or_experiment)


def view_experiment(experiment_name: str) -> None:
    client = Grid()
    experiment_id = client.get_experiment_id(experiment_name=experiment_name)
    experiment_details = client.experiment_details(experiment_id=experiment_id)
    run_name = experiment_details['getExperimentDetails']['run']['name']

    url = env.GRID_URL + '#'
    launch_url = '/'.join([url, f'runs?runName={run_name}&expId={experiment_id}'])

    click.echo()
    click.echo(f'Opening URL: {launch_url}')

    click.launch(launch_url)


def view_run(run_name: str) -> None:
    url = env.GRID_URL + '#'
    launch_url = '/'.join([url, 'view', 'run', run_name])

    click.echo()
    click.echo(f'Opening URL: {launch_url}')

    click.launch(launch_url)
