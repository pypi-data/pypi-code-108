import typer
import json
import pandas as pd
import rich

from continual.python.cli import utils
from continual import Client

from rich.console import Console
from typing import List

app = typer.Typer(help="Manage model versions.")


def format_model_version_data(mv, zipped=False, all_projects=False):
    try:
        experiment = mv.experiment.id
    except:
        experiment = "N/A"
    if mv.promoted:
        last_promoted = Client().promotions.get(mv.promotion).promoted_time
        if last_promoted:
            last_promoted = last_promoted.replace(microsecond=0)
    else:
        last_promoted = "N/A"
    update_time = mv.update_time.replace(microsecond=0)
    create_time = mv.create_time.replace(microsecond=0)
    if zipped:
        data = [
            mv.id,
            mv.name,
            mv.state.value,
            experiment,
            mv.performance_metric,
            mv.performance_metric_val,
            mv.promoted,
            mv.promotion,
            last_promoted,
            create_time,
            update_time,
        ]
        headers = [
            "ID",
            "Name",
            "State",
            "Winning Experiment",
            "Metric",
            "Metric Value",
            "Promoted",
            "Promotion",
            "Promoted Time",
            "Created",
            "Updated",
        ]
        return tuple(
            [x[0], x[1]] for x in (zip(headers, data))
        )  # for some reason list(zip) causes issues, so ...
    else:
        data = [
            mv.id,
            mv.state.value,
            mv.name.split("/")[3],
            experiment,
            mv.performance_metric,
            mv.performance_metric_val,
            mv.promoted,
            last_promoted,
            create_time,
            # update_time,
        ]
        headers = [
            "ID",
            "State",
            "Model",
            "Winning Experiment",
            "Metric",
            "Metric Value",
            "Promoted",
            "Promoted Time",
            "Created",
            # "Updated",
        ]
        if all_projects:
            data.insert(0, mv.parent.split("/")[1])
            headers.insert(0, "Project")
        return (data, headers)


# use callback to run list command if nothing is passed in
@app.callback(invoke_without_command=True)
def default(ctx: typer.Context):
    if ctx.invoked_subcommand is not None:
        return
    else:
        mv_list(
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
def mv_list(
    model: str = typer.Option(None, help="Model ID."),
    project: str = typer.Option(None, help="Project ID."),
    environment: str = typer.Option(None, "--env", help="Environment ID."),
    n: int = typer.Option(30, "--num", "-n", help="Number of records to show."),
    filters: List[str] = typer.Option([], "--filter", "-f", help="List of filters."),
    all_projects: bool = typer.Option(False, "--all", "-a", help="Show all projects."),
    style: utils.ContinualStyle = typer.Option(None, help="Color to use for list."),
):
    """List model versions.

    Filters can include:
        --state (i.e. state:FAILED)
    """
    project, environment = utils.get_project_and_environment(project, environment)
    c = Client(project=utils.get_environment_name(project, environment))

    model_snippet = ""
    filter_snippet = " (n=%s)" % n
    project_snippet = "project %s, environment %s" % (project, environment)
    if model is not None:
        c = c.models.get(model)
        model_snippet = "for model %s " % model
    if len(filters) > 0:
        filter_snippet = " with filter %s" % str(filters)
    if all_projects:
        project_snippet = "all accessible projects"
    data = []
    headers = []
    for mv in c.model_versions.list(n, filters=filters, all_projects=all_projects):
        (mv_data, headers) = format_model_version_data(mv, all_projects=all_projects)
        data.append(mv_data)
    typer.secho(
        "\nFound %s model versions %sin  %s%s: "
        % (len(data), model_snippet, project_snippet, filter_snippet),
        fg="blue",
    )
    utils.print_table(data, headers, style=utils.get_style(style))


@app.command("get")
@utils.exit_on_error
def get(
    model_version: str = typer.Argument(..., help="Model version ID."),
    project: str = typer.Option(None, help="Project ID."),
    environment: str = typer.Option(None, "--env", help="Environment ID."),
    to_json: bool = typer.Option(
        False, "--json", help="Show full JSON representation."
    ),
):
    """Get model version information."""
    project, environment = utils.get_project_and_environment(project, environment)
    c = Client(project=utils.get_environment_name(project, environment))

    mv = c.model_versions.get(model_version)
    console = Console()
    if to_json:
        console.print(mv.to_dict())
    else:
        data = format_model_version_data(mv, zipped=True)
        typer.secho("\nRetrieving model version %s: \n" % (model_version), fg="blue")
        utils.print_info(data)
        typer.secho("\nAdvanced Configuration:", fg="blue")
        console.print(json.loads(mv.fit_config))
        typer.secho("\nFeature Importance:", fg="blue")
        console.print(
            {
                k: v
                for k, v in sorted(
                    mv.experiment.feature_importance.items(),
                    key=lambda item: item[1],
                    reverse=True,
                )
            }
        )
        typer.secho("\nData Checks:", fg="blue")
        console.print(mv.data_checks.to_dict().get("results"))


@app.command("promote")
@utils.exit_on_error
def promote(
    model_version: str = typer.Argument(..., help="Model version ID."),
    project: str = typer.Option(None, help="Project ID."),
    environment: str = typer.Option(None, "--env", help="Environment ID."),
    model: str = typer.Option(None, help="Model ID."),
    wait: bool = typer.Option(False, "--wait", help="Wait for promotion to finish."),
    debug: bool = typer.Option(
        False, "--debug", help="Print full name of model version."
    ),
):
    """Promotes a model version."""
    project, environment = utils.get_project_and_environment(project, environment)
    c = Client(project=utils.get_environment_name(project, environment))

    mv = c.model_versions.get(model_version)
    d = mv.promote()
    if wait:
        d.wait()
        typer.secho(
            "Successfully promoted %s for model version %s." % (d.id, mv.id),
            fg="green",
        )
    else:
        typer.secho(
            "Started promotion %s for model version %s." % (d.id, mv.id),
            fg="green",
        )
    endpoint = utils.get_endpoint()
    model = mv.parent.split("/")[-1]
    typer.secho("You can review the promotion at: ", fg="blue")
    typer.secho(
        f"  {endpoint}/projects/{project}/model/{model}/promotions/\n", fg="blue"
    )

    if debug:
        typer.echo("DEBUG: Full name = %s." % d.name)


@app.command("cancel")
@utils.exit_on_error
def cancel(
    model_version: str = typer.Argument(..., help="Model version ID."),
    project: str = typer.Option(None, help="Project ID."),
    environment: str = typer.Option(None, "--env", help="Environment ID."),
    force: bool = typer.Option(
        False, "--force", help="Force deletion. Skips confirmation."
    ),
):
    """Cancel a model version that is currently training."""
    project, environment = utils.get_project_and_environment(project, environment)
    c = Client(project=utils.get_environment_name(project, environment))

    if not force:
        force = typer.confirm(
            "Are you sure you want to cancel training model version %s in project %s, environment %s?"
            % (model_version, project, environment)
        )
    if force:
        mv = c.model_versions.get(model_version)
        mv.cancel()
        typer.secho(
            "Successfully cancelled training for model version %s." % (mv.id),
            fg="green",
        )
    else:
        typer.secho("Skipping cancellation!", fg="blue")


@app.command("compare-across-model")
@utils.exit_on_error
def compare_across_model(
    model: str = typer.Argument(..., help="Model ID.", show_default=False),
    project: str = typer.Option(None, help="Project ID.", show_default=False),
    environment: str = typer.Option(None, "--env", help="Environment ID."),
    model_versions: str = typer.Option(
        None, help="Model Version IDs, comma separated list", show_default=False
    ),
    performance_metric: utils.PerformanceMetric = typer.Option(
        None, help="Performance Metric to use for comparison."
    ),
    split_type: utils.SplitType = typer.Option(
        utils.SplitType.TEST, help="Dataset to use for comparison."
    ),
    stacked: bool = typer.Option(
        True, "--report", help="Print information as a report."
    ),
    style: utils.ContinualStyle = typer.Option(None, help="Color to use for list."),
):
    """
    Compare model versions in a model.
    """
    project, environment = utils.get_project_and_environment(project, environment)
    c = Client(project=utils.get_environment_name(project, environment))

    try:
        m = c.models.get(model)
        if model_versions is not None:
            mvs = model_versions.split(",")
            mv_list = []
            for mv in mvs:
                model_version = m.model_versions.get(mv)
                mv_list.append(model_version)
        else:
            mv_list = c.model_versions.list_all()

        data = []
        metrics = {}
        fi = {}

        typer.secho(
            "Comparing model versions in model %s in project %s:" % (model, project)
        )
        for mv in mv_list:
            try:
                get_model_info(
                    project,
                    environment,
                    mv.id,
                    performance_metric,
                    split_type,
                    data,
                    metrics,
                    fi,
                )
            except:
                continue
        if len(data) > 1:
            print_mv_dashboard(
                data,
                metrics,
                fi,
                split_type,
                utils.get_style(style),
                include_project=False,
                stacked=stacked,
            )
        else:
            typer.secho(
                "Failed to find two or more successful model versions for model %s in project %s, environment %s."
                % (model, project, environment),
                fg="red",
            )

    except Exception as e:
        typer.secho(
            "Failed to compare model versions in model %s: %s" % (model, str(e)),
            fg="red",
        )


@app.command("compare")
@utils.exit_on_error
def compare(
    right_model_version: str = typer.Option(
        ...,
        "--right_model_version",
        "-rmv",
        help="Model Version ID.",
        show_default=False,
    ),
    right_project: str = typer.Option(
        None, "--right_project", "-rproj", help="Project ID.", show_default=False
    ),
    right_environment: str = typer.Option(
        None, "--right_environment", "-renv", help="Environment ID."
    ),
    left_model_version: str = typer.Option(
        ...,
        "--left_model_version",
        "-lmv",
        help="Model Version ID.",
        show_default=False,
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
        utils.SplitType.TEST, help="Data split to use for comparison."
    ),
    stacked: bool = typer.Option(
        True, "--report", help="Print information as a report."
    ),
    style: utils.ContinualStyle = typer.Option(None, help="Color to use for list."),
):
    """Compare two model versions across projects or environments."""
    data = []
    metrics = {}
    fi = {}
    get_model_info(
        right_project,
        right_environment,
        right_model_version,
        performance_metric,
        split_type,
        data,
        metrics,
        fi,
        include_project=True,
    )
    get_model_info(
        left_project,
        left_environment,
        left_model_version,
        performance_metric,
        split_type,
        data,
        metrics,
        fi,
        include_project=True,
    )

    print_mv_dashboard(
        data,
        metrics,
        fi,
        split_type,
        utils.get_style(style),
        include_project=True,
        stacked=stacked,
    )


def print_mv_dashboard(
    data,
    metrics,
    fi,
    split_type,
    style,
    include_project=False,
    include_model=False,
    stacked=True,
):
    if include_project and include_model:
        df = pd.DataFrame(
            data,
            columns=[
                "Project ID",
                "MID",
                "MVID",
                "Created",
                "Algo",
                "Perf Metric",
                "Perf Metric Value",
            ],
        ).sort_values(["Perf Metric Value"], ascending=False)
    elif include_project:
        df = pd.DataFrame(
            data,
            columns=[
                "Project ID",
                "MVID",
                "Created",
                "Algo",
                "Perf Metric",
                "Perf Metric Value",
            ],
        ).sort_values(["Perf Metric Value"], ascending=False)
    elif include_model:
        df = pd.DataFrame(
            data,
            columns=[
                "MID",
                "MVID",
                "Created",
                "Algo",
                "Perf Metric",
                "Perf Metric Value",
            ],
        ).sort_values(["Perf Metric Value"], ascending=False)
    else:
        df = pd.DataFrame(
            data,
            columns=["MVID", "Created", "Algo", "Perf Metric", "Perf Metric Value"],
        ).sort_values(["Perf Metric Value"], ascending=False)

    df["Lead Perf"] = df["Perf Metric Value"].shift(-1)
    df["% Perf Change"] = (
        (df["Perf Metric Value"] - df["Lead Perf"]) / df["Perf Metric Value"] * 100
    )

    df["Lead MVID"] = df["MVID"].shift(-1)
    df["Features Dropped"] = df.apply(
        lambda x: "\n".join(
            sorted(
                list(
                    set(fi.get(x["Lead MVID"], fi.get(x["MVID"])))
                    - set(fi.get(x["MVID"]))
                )
            )
        ),
        axis=1,
    )
    df["Features Added"] = df.apply(
        lambda x: "\n".join(
            sorted(
                list(
                    set(fi.get(x["MVID"]))
                    - set(fi.get(x["Lead MVID"], fi.get(x["MVID"])))
                )
            )
        ),
        axis=1,
    )
    df["Top Features"] = df.apply(
        lambda x: "\n".join(
            list(
                "%s\t%s" % (y[0], y[1])
                for y in sorted(
                    fi.get(x["MVID"]).items(), key=lambda item: item[1], reverse=True
                )[:5]
            )
        ),
        axis=1,
    )

    metrics_df = pd.DataFrame(metrics).T.reset_index().rename(columns={"index": "MVID"})
    if include_project and include_model:
        main_table = utils.print_table(
            df[
                [
                    "Project ID",
                    "MID",
                    "MVID",
                    "Created",
                    "Algo",
                    "Perf Metric",
                    "Perf Metric Value",
                    "% Perf Change",
                ]
            ],
            [
                "Project ID",
                "MID",
                "MVID",
                "Created",
                "Algo",
                "Perf Metric",
                "Perf Metric Value",
                "% Perf Change",
            ],
            style=style,
            print=stacked,
            title="Model Version Comparison in %s data set" % split_type.value,
        )
    elif include_project:
        main_table = utils.print_table(
            df[
                [
                    "Project ID",
                    "MVID",
                    "Created",
                    "Algo",
                    "Perf Metric",
                    "Perf Metric Value",
                    "% Perf Change",
                ]
            ],
            [
                "Project ID",
                "MVID",
                "Created",
                "Algo",
                "Perf Metric",
                "Perf Metric Value",
                "% Perf Change",
            ],
            style=style,
            print=stacked,
            title="Model Version Comparison in %s data set" % split_type.value,
        )
    elif include_model:
        main_table = utils.print_table(
            df[
                [
                    "MID",
                    "MVID",
                    "Created",
                    "Algo",
                    "Perf Metric",
                    "Perf Metric Value",
                    "% Perf Change",
                ]
            ],
            [
                "MID",
                "MVID",
                "Created",
                "Algo",
                "Perf Metric",
                "Perf Metric Value",
                "% Perf Change",
            ],
            style=style,
            print=stacked,
            title="Model Version Comparison in %s data set" % split_type.value,
        )
    else:
        main_table = utils.print_table(
            df[
                [
                    "MVID",
                    "Created",
                    "Algo",
                    "Perf Metric",
                    "Perf Metric Value",
                    "% Perf Change",
                ]
            ],
            [
                "MVID",
                "Created",
                "Algo",
                "Perf Metric",
                "Perf Metric Value",
                "% Perf Change",
            ],
            style=style,
            print=stacked,
            title="Model Version Comparison in %s data set" % split_type.value,
        )
    metrics_table = utils.print_table(
        metrics_df,
        metrics_df.columns,
        style=style,
        print=stacked,
        title="Metrics Comparison",
    )
    top_features_table = utils.print_table(
        df[["MVID", "Top Features"]],
        ["MVID", "Top Features"],
        style=style,
        print=stacked,
        title="Feature Importance Comparison",
    )
    features_diff_table = utils.print_table(
        df[["MVID", "Features Dropped", "Features Added"]],
        ["MVID", "Features Dropped", "Features Added"],
        style=style,
        print=stacked,
        title="Feature Comparison",
    )

    if not stacked:
        features_diff_table = utils.print_table(
            df[["MVID", "Features Dropped", "Features Added"]],
            ["MVID", "Features Dropped", "Features Added"],
            style=style,
            print=False,
            title="Feature Comparison",
        )
        top_features_table = utils.print_table(
            df[["MVID", "Top Features"]],
            ["MVID", "Top Features"],
            style=style,
            print=False,
            title="Feature Importance Comparison",
        )
        metrics_table = utils.print_table(
            metrics_df,
            metrics_df.columns,
            style=style,
            print=False,
            title="Metrics Comparison",
        )

        template = [
            {"name": "Top", "ratio": len(df), "data": main_table},
            {"name": "Middle", "ratio": len(metrics_df), "data": metrics_table},
            {
                "name": "Bottom",
                "ratio": max(len(df), 5),
                "direction": "horizontal",
                "children": [
                    {"name": "Feature Comparison", "data": features_diff_table},
                    {"name": "Top Features", "data": top_features_table},
                ],
            },
        ]

        layout = utils.build_dashboard(template, direction="vertical")
        rich.print(layout)


def get_model_info(
    project,
    environment,
    model_version,
    performance_metric,
    split_type,
    data=[],
    metrics={},
    fi={},
    include_project=False,
    include_model=False,
):
    project, environment = utils.get_project_and_environment(project, environment)
    c = Client(project=utils.get_environment_name(project, environment))

    mv = c.model_versions.get(model_version)

    if mv.state.value == "SUCCEEDED":  # filter out anything that didn't complete
        ex = mv.experiment

        perf_metric = "N/A"
        perf_metric_val = "N/A"
        if performance_metric is not None:
            perf_metric = performance_metric.value
            perf_metric_val = (
                ex.metrics.__getattribute__("%s_metrics" % (split_type.value))
                .__getattribute__(ex.model_type.value.lower())
                .__getattribute__(perf_metric)
            )
        else:
            perf_metric = mv.performance_metric
            perf_metric_val = mv.performance_metric_val
        arr = [
            mv.id,
            mv.update_time.strftime("%Y-%m-%d %H:%M:%S"),
            # mv.model_version_format,
            ex.type.split("/")[1],
            perf_metric,
            perf_metric_val,
        ]
        if include_model:
            arr.insert(0, mv.parent.split("/")[-1])
        if include_project:
            arr.insert(0, utils.get_environment_name(project, environment))
        data.append(arr)
        metrics[mv.id] = (
            ex.metrics.__getattribute__("%s_metrics" % (split_type.value))
            .__getattribute__(ex.model_type.value.lower())
            .to_dict()
        )
        fi[mv.id] = {
            ":".join(i.split(":")[1:]): j for i, j in ex.feature_importance.items()
        }

    return (data, metrics, fi)
