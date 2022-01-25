from typing import List

import click
import yaspin

from grid import Experiment, Run
from grid.cli import rich_click
from grid.sdk import env
from grid.sdk.rest.client import GridRestClient
from grid.sdk.client import create_swagger_client
from grid.sdk.rest.exceptions import GridException


@rich_click.group()
def delete() -> None:
    """Allows you to delete grid resources."""
    pass


def doublecheck(item: str):
    warning_str = click.style('WARNING!', fg='red')
    message = f"""

    {warning_str}

    Your are about to delete the {item}.
    This will delete all the associated artifacts, logs, and metadata.

    Are you sure you want to do this?

   """
    click.confirm(message, abort=True)


@delete.command()
@rich_click.argument('experiment_names', type=str, required=True, nargs=-1, help='Experiment names to delete.')
def experiment(experiment_names: List[str]):
    """Delete some set of EXPERIMENT_NAMES from grid.

    This process is immediate and irreversible, deletion permanently removes not only
    the record of the experiment, but all associated artifacts, metrics, logs, etc.
    """
    doublecheck(str(experiment_names))
    for name in experiment_names:
        spinner = yaspin.yaspin(text=f'Stopping experiment {name}...', color="yellow")
        spinner.start()
        try:
            exp = Experiment(name=name)
            if not exp.exists:
                raise RuntimeError(
                    f"Experiment {name} does not exist in the cluster {env.CONTEXT}. "
                    f"If you are trying to delete an experiment in another cluster, "
                    f"try setting the default cluster with "
                    f"`grid user set-default-cluster <cluster_name>` first"
                )
            exp.delete()
            spinner.ok("✔")
            styled_name = click.style(name, fg='blue')
            click.echo(f'Experiment {styled_name} was deleted successfully.')
        except GridException as e:
            if spinner:
                spinner.fail("✘")
            raise click.ClickException(str(e))
        except Exception as e:
            if spinner:
                spinner.fail("✘")
            raise click.ClickException(f"Deletion failed for experiment {name}: {e}")
        finally:
            spinner.stop()


@delete.command()
@rich_click.argument('run_names', type=str, required=True, nargs=-1, help='Run names to delete.')
def run(run_names: List[str]):
    """Delete some set of RUN_NAMES from grid.

    Deleting a run also deletes all experiments contained within the run.

    This process is immediate and irreversible, deletion permanently removes not only
    the record of the run, but all associated experiments, artifacts, metrics, logs, etc.
    """
    doublecheck(str(run_names))
    for name in run_names:
        spinner = yaspin.yaspin(text=f'Stopping run {name}...', color="yellow")
        spinner.start()
        try:
            run_obj = Run(name=name)
            if not run_obj.exists:
                raise RuntimeError(
                    f"Run {name} does not exist in the cluster {env.CONTEXT}. "
                    f"If you are trying to delete a run in another cluster, "
                    f"try setting the default cluster with "
                    f"`grid user set-default-cluster <cluster_name>` first"
                )
            run_obj.delete()
            spinner.ok("✔")
            styled_name = click.style(name, fg='blue')
            click.echo(f'Run {styled_name} was deleted successfully.')
        except GridException as e:
            if spinner:
                spinner.fail("✘")
            raise click.ClickException(str(e))
        except Exception as e:
            if spinner:
                spinner.fail("✘")
            raise click.ClickException(f"Deletion failed for run {name}: {e}")
        finally:
            spinner.stop()


@delete.command()
@rich_click.argument('cluster', type=str, help='Cluster id to delete.')
@click.option(
    '--force',
    'force',
    type=bool,
    required=False,
    default=False,
    is_flag=True,
    help='Force delete cluster from grid system. This does NOT delete any resources created by the cluster, '
    'just cleaning up the entry from the grid system. You should not use this under normal circumstances',
)
def cluster(cluster: str, force: bool = False):
    """Delete CLUSTER and all associated AWS resources.

    Deleting a run also deletes all Runs and Experiments which were started
    on the cluster. deletion permanently removes not only the record of all
    runs on a cluster, but all associated experiments, artifacts, metrics, logs, etc.

    This process may take a few minutes to complete, but once started is irriversable.
    Deletion permanently removes not only cluster from being managed by grid, but tears
    down every resource grid managed (for that cluster id) in the host cloud. All object
    stores, container registries, logs, compute nodes, volumes, etc. are deleted and
    cannot be recovered.
    """
    if force:
        click.echo(
            "Force deleting cluster. This will cause grid to forget "
            "about the cluster and any experiments, sessions, datastores, "
            "tensorboards and other resources running on it.\n"
            "WARNING: this will not clean up any resources managed by grid\n"
            "Check your cloud provider that any existing cloud resources are deleted"
        )
        click.confirm('Do you want to continue?', abort=True)

    client = GridRestClient(api_client=create_swagger_client())
    client.cluster_service_delete_cluster(id=cluster, force=force)
    click.echo("Cluster deletion triggered successfully")
