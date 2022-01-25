"""CLI interface to kfputils."""
import click
from .pipeline import (
    list_pipelines,
    delete_multi,
)
from .run import _display_run
from .uploadrun import UploaderRunner
import json


@click.group()
def pipeline():
    """Pipeline helpers."""
    pass


@pipeline.command()
@click.pass_context
def delete_all(ctx):
    """Delete all current pipelines."""
    client = ctx.obj["client"]
    pipelines = list_pipelines(client)
    if len(pipelines):
        delete_multi(client, pipelines)
        print("[OK] successfully deleted all pipelines")
    else:
        print("[OK] no pipelines to delete")


@pipeline.command()
# @click.option("-p", "--pipeline-name", required=True, help="Name of the pipeline.")
@click.option(
    "-v", "--pipeline-version", help="Name of the pipeline version", default=""
)
@click.option(
    "-f",
    "--package-file",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to the pipeline package file.",
)
@click.option(
    "-e", "--experiment-name", required=True, help="Experiment name of the run."
)
@click.option(
    "-s",
    "--params-file",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to the pipeline yaml params file.",
)
@click.pass_context
def upload_run(
    ctx,
    # pipeline_name,
    package_file,
    experiment_name,
    params_file,
    # output,
    pipeline_version,
):
    """Upload and trigger a run of a KFP pipeline."""
    client = ctx.obj["client"]
    namespace = ctx.obj["namespace"]
    uploadRunner = UploaderRunner(client, package_file)
    # run_res, upload_res, is_first_version = uploadRunner.upload_run(
    run_res, _, _ = uploadRunner.upload_run(
        experiment_name,
        pipeline_version,
        params_file,
    )
    from pprint import pprint

    pprint("----------------------------")
    pprint(f"pipline name: {uploadRunner.pipeline_name}")
    pprint("----------------------------")
    # pprint(f"pipeline is first version: {is_first_version}")
    # pprint("----------------------------")
    # pprint("upload result")
    # pprint(upload_res)
    # pprint("----------------------------")
    # pprint("run result")
    # pprint(run_res)
    print("Run {} is submitted".format(run_res.id))
    _display_run(client, namespace, run_res.id, True)
    print(f"[OK ] pipeline run successfully for pipeline: {uploadRunner.pipeline_name}")


@pipeline.command()
# @click.option("-p", "--pipeline-name", required=True, help="Name of the pipeline.")
@click.option(
    "-v", "--pipeline-version", help="Name of the pipeline version", default=""
)
@click.option(
    "-f",
    "--package-file",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to the pipeline package file.",
)
@click.option(
    "-o",
    "--output",
    help="output format",
    type=click.Choice(["text", "json"], case_sensitive=False),
    default="text",
)
@click.pass_context
def upload(ctx, package_file, output, pipeline_version):
    """Upload a KFP pipeline."""
    client = ctx.obj["client"]
    uploadRunner = UploaderRunner(client, package_file)
    res, is_first_version = uploadRunner.upload(pipeline_version)
    if output == json:
        json.dumps(res)
        return

    if is_first_version:
        print(f"[OK] created first version of pipeline: {uploadRunner.pipeline_name}")
    else:
        print(
            f"[OK] created updated version of pipeline: {uploadRunner.pipeline_name}, version: {pipeline_version}"
        )

    # pprint("res")
    # pprint(res)
