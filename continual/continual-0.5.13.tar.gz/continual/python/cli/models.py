import typer
import yaml

from continual.python.cli import utils, feature_sets, model_versions
from continual import Client
from continual.rpc.management.v1.types import ModelVersionState

from pathlib import Path
from rich.console import Console
from typing import List

app = typer.Typer(help="Manage models.")


def get_linked_entities(columns):
    entities = {}
    for c in columns:
        entity = c.entity
        if entity is not None and len(entity) > 0:
            entities[c.name] = entity
    return "\n".join(["%s : %s" % (k, v) for k, v in entities.items()])


def format_model_data(m, zipped=False, all_projects=False):
    create_time = m.create_time.replace(microsecond=0)
    update_time = m.update_time.replace(microsecond=0)
    num_bpj = len(m.batch_prediction_jobs.list(1000))
    num_d = len(m.promotions.list(1000))
    num_mv = len(m.model_versions.list(1000))
    latest_version = m.latest_model_version.split("/")[-1]
    if latest_version:
        mv_state = m.model_versions.get(latest_version).state.value
    else:
        mv_state = "N/A"
    current_version = m.current_version.split("/")[-1]
    mv_type = "N/A"
    mv_perf_metric = "N/A"
    mv_perf_metric_val = "N/A"
    if current_version:
        mv = m.model_versions.get(current_version)
        try:
            mv_type = mv.experiment.type.split("/")[1]
        except:
            mv_type = "N/A"
        mv_perf_metric = mv.performance_metric
        mv_perf_metric_val = round(mv.performance_metric_val, 4)
    linked_entities = get_linked_entities(m.schema.columns)
    project = m.parent.split("/")[-1]
    if zipped:
        data = [
            m.id,
            m.name,
            m.state,
            project,
            latest_version,
            mv_state,
            current_version,
            mv_type,
            mv_perf_metric,
            mv_perf_metric_val,
            m.latest_batch_prediction,
            linked_entities,
            num_mv,
            num_d,
            num_bpj,
            create_time,
            update_time,
        ]
        headers = [
            "ID",
            "Name",
            "State",
            "Project",
            "Latest Model Version",
            "Latest Version State",
            "Current Version",
            "Current Version Type",
            "Current Version Performance Metric",
            "Current Version Performance Metric Value",
            "Latest Batch Prediction",
            "Linked Entities",
            "Model Versions",
            "Promotions",
            "Batch Predictions",
            "Created",
            "Updated",
        ]
        return tuple(
            [x[0], x[1]] for x in (zip(headers, data))
        )  # for some reason list(zip) causes issues, so ...
    else:
        data = [
            m.id,
            m.state,
            latest_version,
            mv_state,
            current_version,
            mv_type,
            mv_perf_metric,
            mv_perf_metric_val,
            linked_entities,
            num_mv,
            num_d,
            num_bpj,
            create_time,
            # update_time,
        ]
        headers = [
            "ID",
            "State",
            "Latest Version",
            "Latest Version State",
            "Current Version",
            "Current Version Type",
            "Current Version Perf Metric",
            "Current Version Perf Metric Val",
            "Linked Entities",
            "Model Versions",
            "Promotions",
            "Batch Predictions",
            "Created",
            # "Updated",
        ]
        if all_projects:
            data.insert(0, m.parent.split("/")[1])
            headers.insert(0, "Project")
        return (data, headers)


# use callback to run list command if nothing is passed in
@app.callback(invoke_without_command=True)
def default(ctx: typer.Context):
    if ctx.invoked_subcommand is not None:
        return
    else:
        model_list(
            project=None,
            environment=None,
            n=30,
            filters=[],
            all_projects=False,
            style=None,
        )


@app.command("list")
@utils.exit_on_error
def model_list(
    project: str = typer.Option(None, help="Project ID."),
    environment: str = typer.Option(None, "--env", help="Environment ID."),
    n: int = typer.Option(30, "--num", "-n", help="Number of records to show."),
    filters: List[str] = typer.Option([], "--filter", "-f", help="List of filters."),
    all_projects: bool = typer.Option(False, "--all", "-a", help="Show all projects."),
    style: utils.ContinualStyle = typer.Option(None, help="Color to use for list."),
):
    """List models.

    Filter can include:
        - state  (i.e. state:HEALTHY)
        - latest_mv_state (i.e. latest_mv_state:SUCCEEDED)
    """
    project, environment = utils.get_project_and_environment(project, environment)
    c = Client(project=utils.get_environment_name(project, environment))

    filter_snippet = " (n=%s)" % n
    project_snippet = "project %s, environment %s" % (project, environment)
    if all_projects:
        project_snippet = "all accessible projects"
    if len(filters) > 0:
        filter_snippet = " with filter %s" % str(filters) + filter_snippet
    data = []
    headers = []
    for m in c.models.list(n, filters=filters, all_projects=all_projects):
        (m_data, headers) = format_model_data(m, all_projects=all_projects)
        data.append(m_data)
    typer.secho(
        "\nFound %s models in %s%s:" % (len(data), project_snippet, filter_snippet),
        fg="blue",
    )
    utils.print_table(data, headers, style=utils.get_style(style))


@app.command("get")
@utils.exit_on_error
def get(
    model: str = typer.Argument(..., help="Model ID."),
    project: str = typer.Option(None, help="Project ID."),
    environment: str = typer.Option(None, "--env", help="Environment ID."),
    to_json: bool = typer.Option(
        False, "--json", help="Show full JSON representation."
    ),
):
    """Get model details."""
    project, environment = utils.get_project_and_environment(project, environment)
    c = Client(project=utils.get_environment_name(project, environment))

    m = c.models.get(model)
    console = Console()
    if to_json:
        console.print(m.to_dict())
    else:
        data = format_model_data(m, zipped=True)
        typer.secho("\nRetrieving model %s: \n" % (model), fg="blue")
        utils.print_info(data)
        typer.secho("\nModel schema:\n", fg="blue")
        console.print(m.schema.to_dict())


@app.command("train")
@utils.exit_on_error
def train(
    model: str = typer.Argument(None, help="Model ID."),
    project: str = typer.Option(None, help="Project ID."),
    environment: str = typer.Option(None, "--env", help="Environment ID."),
    wait: bool = typer.Option(False, "--wait", help="Wait for training to finish."),
    debug: bool = typer.Option(False, "--debug", help="Print full name of model."),
    all: bool = typer.Option(False, "--all", help="Train all models."),
    state: ModelVersionState = typer.Option(
        None, help="Only train models with a certain state."
    ),
    include_estimate: bool = typer.Option(
        False, "--include-estimate", help="Include credit usage estimate for resources."
    ),
):
    """Train model."""
    project, environment = utils.get_project_and_environment(project, environment)
    p_slug = utils.get_environment_name(project, environment)
    c = Client(project=p_slug)
    if all or state is not None:
        model_list = []
        if all == True:
            model_list = c.models.list_all().to_list()
        else:
            for m in c.models.list_all():
                try:
                    mv = c.model_versions.get(m.latest_model_version)
                    if mv.state.value == state:
                        model_list.append(m)
                except:
                    continue

        credits = {}
        if len(model_list) > 0:
            endpoint = utils.get_endpoint()
            for model in model_list:
                try:
                    mv = model.train()
                    typer.secho(
                        "Started training model version %s for model %s.\n"
                        % (mv.id, model.id),
                        fg="green",
                    )
                    typer.secho("You can access the model version at: ", fg="white")
                    typer.secho(
                        f"  {endpoint}/projects/{p_slug}/model/{model.id}/versions/{mv.id}\n",
                        fg="blue",
                    )
                    if include_estimate:
                        credits_used = utils.get_model_credit_estimate(
                            model.name, project, environment
                        )
                        credits["%s %s" % (model.id, "TRAIN")] = credits_used
                except Exception as e:
                    typer.secho(
                        "Failed to train model %s: %s" % (model.id, str(e)), fg="red"
                    )
                    continue

            if include_estimate and len(credits) > 0:
                utils.print_credit_estimate_summary(credits)

        else:
            typer.secho("No models found to train.")

    elif model is not None:
        m = c.models.get(model)
        if include_estimate:
            credits_used = utils.get_model_credit_estimate(m.name, project, environment)
            typer.secho(
                "Estimated Credit Usage for Model: %s\n" % credits_used, fg="white"
            )

        mv = m.train()
        if wait:
            mv.wait()
            typer.secho(
                "Successfully trained model version %s for model %s.\n" % (m.id, mv.id),
                fg="green",
            )
        else:
            typer.secho(
                "Started training model version %s for model %s." % (m.id, mv.id),
                fg="green",
            )
        endpoint = utils.get_endpoint()
        typer.secho("You can access the model version at: ", fg="white")
        typer.secho(
            f"  {endpoint}/projects/{p_slug}/model/{m.id}/versions/{mv.id}\n",
            fg="blue",
        )
        if debug:
            typer.echo("DEBUG: Full name = %s." % mv.name)
    else:
        typer.secho(
            "Error: You must either provide model or one of --all or --state.", fg="red"
        )


@app.command("delete")
@utils.exit_on_error
def delete(
    model: str = typer.Argument(..., help="Model ID."),
    project: str = typer.Option(None, help="Project ID."),
    environment: str = typer.Option(None, "--env", help="Environment ID."),
    force: bool = typer.Option(
        False, "--force", help="Force deletion. Skips confirmation."
    ),
):
    """Delete model."""
    project, environment = utils.get_project_and_environment(project, environment)
    c = Client(project=utils.get_environment_name(project, environment))

    if not force:
        force = typer.confirm(
            "Are you sure you want to delete model %s in project %s, environment %s?"
            % (model, project, environment),
            fg="blue",
        )
    if force:
        m = c.projects.get(project).models.get(model)
        m.delete()
        typer.echo("Successfully deleted model %s." % m.id, fg="green")
    else:
        typer.echo("Cancelled model deletion!", fg="blue")


# dev-2222: removing until we have a better way to download data
# @app.command("get-training-data")
# @utils.exit_on_error
# def get_training_data(
#     model: str = typer.Argument(..., help="Model ID."),
#     project: str = typer.Option(None, help="Project ID."),
#     environment: str = typer.Option(None, "--env", help="Environment ID."),
#     path: str = typer.Option(..., help="Path to save training data CSV into."),
#     num_records: int = typer.Option(
#         None, "--num-records", "-n", help="Number of records to retrieve."
#     ),
#     normalized: bool = typer.Option(
#         False,
#         "--normalized",
#         help="Only return base model data (normalized).",
#         hidden=True,
#     ),
#     fetch_metadata: bool = typer.Option(
#         False, "--fetch-metadata", help="Fetch metadata fields ", hidden=True
#     ),
#     latest: bool = typer.Option(
#         False, "--latest", help="Return latest record for each ID.", hidden=True
#     ),
# ):
#     """Get training data for model."""
#     project, environment = utils.get_project_and_environment(project, environment)
#     c = Client(project=utils.get_environment_name(project, environment))

#     typer.secho(
#         "Getting training data for model %s in project %s, environment %s."
#         % (model, project, environment),
#         fg="blue",
#     )
#     try:
#         m = c.models.get(model)
#         (df, _) = m.get_training_data(
#             n=num_records, normalized=normalized, metadata=fetch_metadata, latest=latest
#         )
#         if path[-4:] != ".csv":
#             path = "%s/%s.csv" % (path, model)
#         if df is not None and df.shape[0] > 0:
#             df.to_csv(path, index=False)
#             typer.secho(
#                 "Saved training data for model %s to %s." % (model, path), fg="green"
#             )
#             typer.echo(df.head())
#         else:
#             typer.secho(
#                 "Failed to download data for model %s: Returned no results." % model,
#                 fg="red",
#             )
#     except Exception as e:
#         typer.secho(
#             "Failed to get training data for model %s in project %s environment %s: %s"
#             % (model, project, environment, str(e)),
#             fg="red",
#         )


@app.command("diff")
@utils.exit_on_error
def diff(
    right_yaml: str = typer.Option(None, "--ryaml", help="YAML location."),
    right_project: str = typer.Option(None, "--rproj", help="Right project."),
    right_environment: str = typer.Option(None, "--renv", help="Environment ID."),
    right_model: str = typer.Option(None, "--rmodel", help="Right model."),
    left_yaml: str = typer.Option(None, "--lyaml", help="YAML location."),
    left_project: str = typer.Option(None, "--lproj", help="Left project."),
    left_environment: str = typer.Option(None, "--lenv", help="Environment ID."),
    left_model: str = typer.Option(None, "--lmodel", help="Left model"),
):
    """
    Diff model configuration.

    Can either provide a local YAML file or a model ID already
    contained in Continual. To use local YAML files, use the
    *_yaml options. Otherwise use *_project and *_model options.
    """
    if not ((right_yaml or right_model) and (left_yaml or left_model)):
        typer.secho(
            "Error: You must either provide 2 model references or 2 YAML files to diff models."
        )
    else:
        feature_sets.diff(
            right_yaml,
            right_project,
            right_environment,
            right_model,
            left_yaml,
            left_project,
            left_environment,
            left_model,
            models=True,
        )


@app.command("validate")
@utils.exit_on_error
def validate_yaml(
    path: Path = typer.Argument(..., help="Full path of YAML file."),
):
    """Validate model YAML file."""
    feature_sets.validate_yaml(path)


@app.command("export")
@utils.exit_on_error
def export_yaml(
    model: str = typer.Argument(..., help="Model ID."),
    project: str = typer.Option(None, help="Project ID."),
    environment: str = typer.Option(None, "--env", help="Environment ID."),
    path: str = typer.Option(
        "print",
        help="Path to save YAML (local). Default = print to console.",
        show_default=False,
    ),
):
    """Export YAML file for feature set."""
    project, environment = utils.get_project_and_environment(project, environment)
    c = Client(project=utils.get_environment_name(project, environment))

    m = c.models.get(model)
    m_text = yaml.load(m.schema_text, Loader=yaml.FullLoader)
    yaml_text = utils.format_yaml(m_text)
    if path == "print":
        typer.secho(
            "Successfully extracted YAML file from feature set %s." % model,
            fg="green",
        )
        print(yaml_text)
    else:
        utils.save_yamls([(model, yaml_text)], path)
        typer.secho(
            "Successfully extracted YAML file from feature set %s. Location is %s."
            % (model, path),
            fg="green",
        )


@app.command("compare-across-project")
@utils.exit_on_error
def compare_across_project(
    project: str = typer.Argument(None, help="Project ID.", show_default=False),
    environment: str = typer.Option(None, "--env", help="Environment ID."),
    models: str = typer.Option(
        None, help="Model IDs, comma separated list", show_default=False
    ),
    performance_metric: utils.PerformanceMetric = typer.Option(
        None, help="Performance Metric to use for comparison."
    ),
    split_type: utils.SplitType = typer.Option(
        utils.SplitType.TEST, help="Performance Metric to use for comparison."
    ),
    stacked: bool = typer.Option(
        True, "--report", help="Print information as a report."
    ),
    style: utils.ContinualStyle = typer.Option(None, help="Color to use for list."),
):
    """
    Compare models in a project or environment.
    """
    project, environment = utils.get_project_and_environment(project, environment)
    c = Client(project=utils.get_environment_name(project, environment))

    mv_list = []
    try:
        if models is not None:
            ms = models.split(",")
            for model in ms:
                m = c.models.get(model)
                try:
                    model_version = m.model_versions.get(m.current_version)
                except:
                    model_version = m.model_versions.get(m.latest_model_version)
                mv_list.append(model_version)
        else:
            for m in c.models.list_all():
                try:
                    model_version = m.model_versions.get(m.current_version)
                except:
                    model_version = m.model_versions.get(m.latest_model_version)
                mv_list.append(model_version)

        data = []
        metrics = {}
        fi = {}

        typer.secho("Comparing models in project %s:" % (project))
        for mv in mv_list:
            try:
                model_versions.get_model_info(
                    project,
                    environment,
                    mv.id,
                    performance_metric,
                    split_type,
                    data,
                    metrics,
                    fi,
                    include_model=True,
                )
            except:
                print("failure!")
                continue

        if len(data) > 1:
            model_versions.print_mv_dashboard(
                data,
                metrics,
                fi,
                split_type,
                utils.get_style(style),
                include_project=False,
                include_model=True,
                stacked=stacked,
            )
        else:
            typer.secho(
                "Failed to find two or more models that have a successful current or latest model version in project %s, environment %s."
                % (project, environment),
                fg="red",
            )

    except Exception as e:
        typer.secho(
            "Failed to compare models in project %s: %s" % (project, str(e)), fg="red"
        )


@app.command("compare")
@utils.exit_on_error
def compare(
    right_model: str = typer.Option(
        ..., "--right_model", "-rmodel", help="Model ID.", show_default=False
    ),
    right_project: str = typer.Option(
        None, "--right_project", "-rproj", help="Project ID.", show_default=False
    ),
    right_environment: str = typer.Option(
        None, "--right_environment", "-renv", help="Environment ID."
    ),
    left_model: str = typer.Option(
        ..., "--left_model", "-lmodel", help="Model ID.", show_default=False
    ),
    left_project: str = typer.Option(
        None, "--left_project", "-lproj", help="Project ID.", show_default=False
    ),
    left_environment: str = typer.Option(
        None, "--left_environment", "-lenv", help="Environment ID."
    ),
    performance_metric: utils.PerformanceMetric = typer.Option(
        None, help="Performance Metric to use for comparison."
    ),
    split_type: utils.SplitType = typer.Option(
        utils.SplitType.TEST, help="Performance Metric to use for comparison."
    ),
    do_diff: bool = typer.Option(True, help="Diff model schemas."),
    stacked: bool = typer.Option(
        True, "--report", help="Print information as a report."
    ),
    style: utils.ContinualStyle = typer.Option(None, help="Color to use for list."),
):
    """Compare two model versions across projects or environments."""
    data = []
    metrics = {}
    fi = {}

    right_project, right_environment = utils.get_project_and_environment(
        right_project, right_environment
    )
    rc = Client(project=utils.get_environment_name(right_project, right_environment))
    try:
        right_mv_id = rc.models.get(right_model).current_version
    except:
        right_mv_id = rc.models.get(right_model).latest_model_version

    left_project, left_environment = utils.get_project_and_environment(
        left_project, left_environment
    )
    c = Client(project=utils.get_environment_name(left_project, left_environment))
    try:
        left_mv_id = rc.models.get(left_model).current_version
    except:
        left_mv_id = rc.models.get(left_model).latest_model_version

    model_versions.get_model_info(
        right_project,
        right_environment,
        right_mv_id,
        performance_metric,
        split_type,
        data,
        metrics,
        fi,
        include_project=True,
        include_model=True,
    )
    model_versions.get_model_info(
        left_project,
        left_environment,
        left_mv_id,
        performance_metric,
        split_type,
        data,
        metrics,
        fi,
        include_project=True,
        include_model=True,
    )

    model_versions.print_mv_dashboard(
        data,
        metrics,
        fi,
        split_type,
        utils.get_style(style),
        include_project=True,
        include_model=True,
        stacked=stacked,
    )

    if do_diff:
        diff(
            None,
            right_project,
            right_environment,
            right_model,
            None,
            left_project,
            left_environment,
            left_model,
        )
