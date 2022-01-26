import typer
import os

from continual.rpc.management.v1.types import BatchPredictionState
from continual.python.cli import utils
from continual import Client

from rich.console import Console
from enum import Enum
from pathlib import Path
from typing import List

app = typer.Typer(help="Manage batch predictions.")


class PredictionDestType(str, Enum):
    csv = "CSV"
    store = "STORE"


def format_batch_prediction_data(bpj, zipped=False, all_projects=False):
    name_parts = bpj.name.split("/")
    model = name_parts[3]
    model_version = name_parts[5]
    end_time = bpj.end_time
    start_time = bpj.start_time
    if start_time:
        start_time = start_time.replace(microsecond=0)
    if end_time and start_time:
        end_time = end_time.replace(microsecond=0)
        duration = (end_time - start_time).seconds
    else:
        end_time = "N/A"
        duration = "N/A"
    if zipped:
        data = [
            bpj.id,
            bpj.name,
            bpj.state.value,
            bpj.incremental,
            start_time,
            end_time,
            duration,
            bpj.prediction_count,
            model,
            model_version,
            bpj.prediction_model,
            bpj.table,
        ]
        headers = [
            "ID",
            "Name",
            "State",
            "Incremental",
            "Start Time",
            "End Time",
            "Duration (s)",
            "Predictions",
            "Model",
            "Model Version",
            "Prediction Model",
            "Data Warehosue Table",
        ]
        return tuple(
            [x[0], x[1]] for x in (zip(headers, data))
        )  # for some reason list(zip) causes issues, so ...
    else:
        data = [
            bpj.id,
            bpj.state.value,
            bpj.incremental,
            model,
            model_version,
            start_time,
            end_time,
            duration,
            bpj.prediction_count,
        ]
        headers = [
            "ID",
            "State",
            "Incremental",
            "Model",
            "Model Version",
            "Start Time",
            "End Time",
            "Duration (s)",
            "Predictions",
        ]
        if all_projects:
            data.insert(0, bpj.parent.split("/")[1])
            headers.insert(0, "Project")
        return (data, headers)


# use callback to run list command if nothing is passed in
@app.callback(invoke_without_command=True)
def default(ctx: typer.Context):
    if ctx.invoked_subcommand is not None:
        return
    else:
        list(
            model=None,
            project=None,
            environment=None,
            n=30,
            filters=[],
            all_projects=False,
            style=None,
        )


@app.command("list")
@utils.exit_on_error
def list(
    model: str = typer.Option(None, help="Model ID."),
    project: str = typer.Option(None, help="Project ID."),
    environment: str = typer.Option(None, "--env", help="Environment ID."),
    n: int = typer.Option(30, "--num", "-n", help="Number of records to show."),
    filters: List[str] = typer.Option([], "--filter", "-f", help="List of filters."),
    all_projects: bool = typer.Option(False, "--all", "-a", help="Show all projects."),
    style: utils.ContinualStyle = typer.Option(None, help="Color to use for list."),
):
    """List batch prediction jobs in a project.

    Filters can include:
        - state  (i.e. state:FAILED)
        - incremental (i.e. incremental: True)
    """
    project, environment = utils.get_project_and_environment(project, environment)
    c = Client(project=utils.get_environment_name(project, environment))

    data = []
    headers = []
    model_snippet = ""
    filter_snippet = " (n=%s)" % n
    project_snippet = "project %s, environment %s" % (project, environment)
    if model is not None:
        try:
            c = c.models.get(model)
            model_snippet = "for model %s " % model
        except Exception as e:
            typer.secho(
                "Failed to find model %s in project %s, environment %s. Please double check that your model id, project id, and environment id are correct. : %s"
                % (model, project, environment, str(e)),
                fg="red",
            )
            raise typer.Exit(code=1)
    if len(filters) > 0:
        filter_snippet = " with filter %s" % str(filters) + filter_snippet
    if all_projects:
        project_snippet = "all accessible projects & environments"
    for bpj in c.batch_prediction_jobs.list(
        n, filters=filters, all_projects=all_projects
    ):
        (bpj_data, headers) = format_batch_prediction_data(
            bpj, all_projects=all_projects
        )
        data.append(bpj_data)
    typer.secho(
        "\nFound %s batch prediction jobs %sin %s%s:"
        % (len(data), model_snippet, project_snippet, filter_snippet),
        fg="blue",
    )
    utils.print_table(data, headers, style=utils.get_style(style))


@app.command("get")
@utils.exit_on_error
def get(
    batch_prediction: str = typer.Argument(..., help="Batch prediction ID"),
    environment: str = typer.Option(None, "--env", help="Environment ID."),
    project: str = typer.Option(None, help="Project ID"),
    json: bool = typer.Option(False, "--json", help="Show full JSON representation."),
):
    """Get batch prediction job details."""
    project, environment = utils.get_project_and_environment(project, environment)
    c = Client(project=utils.get_environment_name(project, environment))

    try:
        bpj = c.batch_prediction_jobs.get(batch_prediction)
    except Exception as e:
        typer.secho(
            "Failed to find batch prediction job %s in project %s, environment %s. Please double check that your job id, project id, and environment id are correct. : %s"
            % (batch_prediction, project, environment, str(e)),
            fg="red",
        )
        raise typer.Exit(code=1)
    if json:
        console = Console()
        console.print(bpj.to_dict())
    else:
        data = format_batch_prediction_data(bpj, zipped=True)
        typer.secho(
            "\nRetrieving batch prediction job %s:\n" % batch_prediction, fg="blue"
        )
        utils.print_info(data)


@app.command("run")
@utils.exit_on_error
def run(
    model: str = typer.Argument(None, help="Model ID."),
    project: str = typer.Option(None, help="Project ID."),
    environment: str = typer.Option(None, "--env", help="Environment ID."),
    wait: bool = typer.Option(
        False, "--wait", help="Wait for batch prediction to finish."
    ),
    dest_type: PredictionDestType = typer.Option(
        PredictionDestType.store, help="Destination type.", hidden=True
    ),
    dest_path: Path = typer.Option(
        None, help="Destination path (CSV only)", hidden=True
    ),
    source_type: PredictionDestType = typer.Option(
        PredictionDestType.store, help="Source type.", hidden=True
    ),
    source_path: Path = typer.Option(None, help="Source path (CSV only).", hidden=True),
    debug: bool = typer.Option(False, help="Print full name of batch prediction job."),
    all: bool = typer.Option(False, "--all", help="Run all batch prediction jobs?"),
    state: BatchPredictionState = typer.Option(
        None, help="Only re-run batch predictions job with a certain state."
    ),
    prediction_model: str = typer.Option(None, help="Optional model type override"),
    incremental: bool = typer.Option(
        False, "--incremental", help="Run an incremental prediction job."
    ),
    include_estimate: bool = typer.Option(
        False, "--include-estimate", help="Include credit usage estimate for resources."
    ),
):
    """Runs a batch prediction job for a model.

    If --all or --state is used, it will bulk run all batch prediction jobs
    or all with the given state (i.e --state FAILED will rerun all failed batch prediction jobs)

    --all overrides --state if both are provided.
    """
    if all or state is not None:
        bulk_run(
            project=project,
            environment=environment,
            dest_type=dest_type,
            dest_path=dest_path,
            all=all,
            state=state,
            include_estimate=include_estimate,
        )
    elif model is not None:
        project, environment = utils.get_project_and_environment(project, environment)
        c = Client(project=utils.get_environment_name(project, environment))
        try:
            m = c.models.get(model)
        except Exception as e:
            typer.secho(
                "Failed to find model %s in project %s, environment %s. Please double check that your job id, project id, and environment id are correct. : %s"
                % (model, project, environment, str(e)),
                fg="red",
            )
            raise typer.Exit(code=1)
        if include_estimate:
            credits_used = utils.get_batch_prediction_credit_estimate(
                m.name, project, environment
            )
            typer.secho(
                "Estimated Credit Usage for Batch Prediction: %s\n" % credits_used,
                fg="white",
            )

        bpj = m.batch_predict(
            source_type.value,
            source_path,
            dest_type.value,
            prediction_model=prediction_model,
            incremental=incremental,
        )
        if wait:
            bpj.wait()
            typer.secho(
                "Successfully ran batch prediction job %s for model %s in project %s, environment %s"
                % (bpj.id, m.id, project, environment),
                fg="green",
            )
            if dest_type == PredictionDestType.csv:
                try:
                    os.remove(dest_path)
                except:
                    pass
                bpj.download(dest_path)
                typer.secho(
                    "Downloaded predictions to file %s" % (dest_path), fg="green"
                )
        else:
            typer.secho(
                "Started running batch prediction job %s for model %s in project %s, environment %s\n"
                % (bpj.id, m.id, project, environment),
                fg="green",
            )
            endpoint = utils.get_endpoint()
            p_slug = utils.get_environment_name(project, environment).split("/")[-1]
            typer.secho("You can access the batch prediction job at: ")
            typer.secho(
                f"  {endpoint}/projects/{p_slug}/models/{m.id}/batchPredictions/{bpj.id}\n",
                fg="blue",
            )

        if dest_type == PredictionDestType.store:
            typer.secho("Predictions can be found in feature store at")
            typer.secho("   %s" % (bpj.table), fg="blue")
        if debug:
            typer.echo("DEBUG: Full name = %s" % bpj.name)
    else:
        typer.secho(
            "Error: You must either provide model or one of --all or --state.", fg="red"
        )


def bulk_run(
    project: str = typer.Option(None, help="Project ID"),
    environment: str = typer.Option(None, "--env", help="Environment ID."),
    dest_type: PredictionDestType = typer.Option(
        PredictionDestType.store, help="Destination type.", hidden=True
    ),
    dest_path: Path = typer.Option(
        None, help="Destination path (CSV only)", hidden=True
    ),
    all: bool = typer.Option(False, "--all", help="Run all batch prediction jobs?"),
    state: BatchPredictionState = typer.Option(
        None, help="Only re-run batch predictions job with a certain state."
    ),
    include_estimate: bool = typer.Option(
        False, "--include-estimate", help="Include credit usage estimate for resources."
    ),
):
    """Bulk run batch prediction jobs."""
    if not (all or state is not None):
        typer.secho(
            "Error: You must specify either --all or --state <state> to specify which batch prediction jobs to run. ",
            fg="red",
        )
        raise typer.Exit(code=0)
    else:
        project, environment = utils.get_project_and_environment(project, environment)
        c = Client(project=utils.get_environment_name(project, environment))

        model_list = []

        if all == True:
            model_list = c.models.list_all().to_list()
        else:
            for m in c.models.list_all():
                try:
                    bpj = c.batch_prediction_jobs.get(m.latest_batch_prediction)
                    if bpj.state.value == state:
                        model_list.append(m)
                except:
                    continue  # if no batch prediction has been run yet, this will error, just skip and keep going

        if len(model_list) > 0:
            credits = {}
            endpoint = utils.get_endpoint()
            p_slug = utils.get_environment_name(project, environment).split("/")[-1]
            for model in model_list:
                try:
                    bpj = model.batch_predict(dest_type=dest_type)
                    typer.secho(
                        "Started running batch prediction job %s for model %s in project %s, environment %s.\n"
                        % (bpj.id, model.id, project, environment),
                        fg="green",
                    )
                    typer.secho("You can access the batch prediction job at: ")
                    typer.secho(
                        f"  {endpoint}/projects/{p_slug}/models/{model.id}/batchPredictions/{bpj.id}\n",
                        fg="blue",
                    )
                    if dest_type == PredictionDestType.store:
                        typer.secho("Predictions can be found in feature store at: ")
                        typer.secho(
                            "   %s\n" % (bpj.table),
                            fg="blue",
                        )
                    if include_estimate:
                        credits_used = utils.get_batch_prediction_credit_estimate(
                            model.name, project, environment
                        )
                        credits["%s %s" % (model.id, "PREDICT")] = credits_used
                except Exception as e:
                    typer.secho(
                        "Failed to start batch prediction for model %s in project %s, environment %s: %s"
                        % (model.id, project, environment, str(e)),
                        fg="red",
                    )
                    continue

            if include_estimate and len(credits) > 0:
                utils.print_credit_estimate_summary(credits)

        else:
            typer.secho("No batch prediction found to run.")


@app.command("cancel")
@utils.exit_on_error
def cancel(
    batch_prediction: str = typer.Argument(..., help="Batch prediction ID."),
    project: str = typer.Option(None, help="Project ID."),
    environment: str = typer.Option(None, "--env", help="Environment ID."),
    force: bool = typer.Option(
        False, "--force", help="Force cancellation. Skips confirmation."
    ),
):
    """Cancel a batch prediction that is currently running."""
    project, environment = utils.get_project_and_environment(project, environment)
    c = Client(project=utils.get_environment_name(project, environment))
    try:
        bpj = c.batch_prediction_jobs.get(batch_prediction)
    except Exception as e:
        typer.secho(
            "Failed to find batch prediction job %s in project %s, environment %s. Please double check that your job id, project id, and environment id are correct. : %s"
            % (batch_prediction, project, environment, str(e)),
            fg="red",
        )
        raise typer.Exit(code=1)
    if not force:
        force = typer.confirm(
            "Are you sure you want to cancel the batch prediction job %s?"
            % batch_prediction
        )
    if force:
        bpj.cancel()
    typer.secho("Successfully cancelled batch prediction %s" % (bpj.id), fg="green")


##dev-2222: removing because we no longer store csvs.
# We may later decide we want download funciton from the cli (might be nice for automation purposes), so leaving in
# @app.command("download")
# @utils.exit_on_error
# def download(
#    batch_prediction: str = typer.Argument(..., help="Batch prediction ID."),
#    project: str = typer.Option(None, help="Project ID."),
#    path: Path = typer.Option(..., help="Local path to save redictions."),
# ):
#    """Download a batch prediction job to CSV."""
#    c = Client(project=project)
#    if project is None:
#        project = utils.get_default_project()
#    bpj = c.batch_prediction_jobs.get(batch_prediction)
#    bpj.download("%s/%s_predictions.csv" % (path, bpj.id))
#    typer.secho(
#        "Successfully downloaded batch prediction job %s to path %s/%s_predictions.csv."
#        % (bpj.id, path, bpj.id),
#        fg="green",
#   )
