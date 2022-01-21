from typing import List

import click
import yaspin

from grid import Experiment, Run
from grid.cli import rich_click
from grid.sdk.rest.exceptions import GridException
from grid.sdk.sessions import Session


@rich_click.group()
def stop():
    """Stop Runs, Experiments, or Sessions."""
    pass


@stop.command()
@rich_click.argument('experiment_names', type=str, required=True, nargs=-1, help="The experiment names to stop.")
def experiment(experiment_names: List[str]):
    """Stop one or more EXPERIMENT_NAMES.

    This preserves progress completed up to this point, but stops
    further computations and any billing for the machines used.
    """
    for name in experiment_names:
        spinner = yaspin.yaspin(text=f'Stopping experiment {name}...', color="yellow")
        spinner.start()
        try:
            exp = Experiment(name=name)
            if not exp.exists:
                raise RuntimeError(
                    f"Experiment {name} does not exist in the cluster {env.CONTEXT}. "
                    f"If you are trying to cancel an experiment in another cluster, "
                    f"try setting the default cluster with "
                    f"`grid user set-default-cluster <cluster_name>` first"
                )
            if not exp.cancel():
                raise RuntimeError(f"Experiment {name} could not be stopped.")
            spinner.ok("✔")
            styled_name = click.style(name, fg='blue')
            click.echo(f'Experiment {styled_name} was stopped successfully.')
        except GridException as e:
            if spinner:
                spinner.fail("✘")
            raise click.ClickException(str(e))
        except Exception as e:
            if spinner:
                spinner.fail("✘")
            raise click.ClickException(f"Stopping failed for experiment {name}: {e}")
        finally:
            spinner.stop()


@stop.command()
@rich_click.argument('run_names', type=str, required=True, nargs=-1, help="The run names to stop.")
def run(run_names: List[str]):
    """Stop one or more RUN_NAMES.

    This preserves progress completed up to this point, but stops
    further computations and any billing for the machines used.
    """
    for name in run_names:
        spinner = yaspin.yaspin(text=f'Stopping run {name}...', color="yellow")
        spinner.start()
        try:
            run_obj = Run(name=name)
            if not run_obj.exists:
                raise RuntimeError(
                    f"Run {name} does not exist in the cluster {env.CONTEXT}. "
                    f"If you are trying to cancel a run in another cluster, "
                    f"try setting the default cluster with "
                    f"`grid user set-default-cluster <cluster_name>` first"
                )
            if not run_obj.cancel():
                raise RuntimeError(f"Run {name} could not be stopped.")
            spinner.ok("✔")
            styled_name = click.style(name, fg='blue')
            click.echo(f'Run {styled_name} was stopped successfully.')
        except GridException as e:
            if spinner:
                spinner.fail("✘")
            raise click.ClickException(str(e))
        except Exception as e:
            if spinner:
                spinner.fail("✘")
            raise click.ClickException(f"Stopping failed for run {name}: {e}")
        finally:
            spinner.stop()


@stop.command()
@rich_click.argument('session_names', type=str, required=True, nargs=-1, help="The session names to stop.")
def session(session_names: List[str]):
    """Stop one or more SESSION_NAMES.

    NOTE: stopping a session permanently removes not only the record of the session,
          but all generated artifacts, metrics, logs, etc.
    """
    for name in session_names:
        sess = Session(name=name)
        sess.delete()
