"""CLI interface to kfputils run commands."""
import click
from .run import Runner, _display_run
from .utils import read_params


@click.group()
def run():
    """Run pipeline(s)."""
    pass


@run.command()
@click.option(
    "-p", "--pipeline-version-id", required=True, help="ID of the pipeline version."
)
@click.option(
    "-e", "--experiment-name", required=True, help="Experiment name of the run."
)
@click.option(
    "-s",
    "--params-file",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to the params yaml file.",
    default="",
)
@click.pass_context
def submit(ctx, pipeline_version_id, experiment_name, params_file):
    """Upload a KFP pipeline."""
    client = ctx.obj["client"]
    namespace = ctx.obj["namespace"]
    runner = Runner(client)
    if params_file is not None:
        params = read_params(params_file)
    run = runner.run(pipeline_version_id, experiment_name, params)
    if run is None:
        raise Exception("run error")
    print("Run {} is submitted".format(run.id))
    _display_run(client, namespace, run.id, True)
