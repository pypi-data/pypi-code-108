import typer
import pandas as pd

from continual.python.cli import utils
from continual import Client
from continual.python.cli.models import format_model_data
from continual.python.cli.batch_predictions import format_batch_prediction_data
from continual.python.cli.promotions import format_promotion_data
from continual.python.cli.experiments import format_experiments_data
from continual.python.cli.feature_sets import format_feature_set_data
from continual.python.cli.model_versions import format_model_version_data
from continual.python.cli.projects import format_project_data
from continual.python.cli.changes import format_changes_data

from rich.panel import Panel
from rich.padding import Padding
import rich

from typing import List
from enum import Enum

app = typer.Typer(help="Run reports.")


class GenericReportType(Enum):
    ALL = "ALL"
    ACTIVE = "ACTIVE"
    FAILED = "FAILED"
    SUCCEEDED = "SUCCEEDED"


class ModelReportType(Enum):
    ALL = "ALL"
    ACTIVE = "ACTIVE"
    FAILED = "FAILED"
    SUCCEEDED = "SUCCEEDED"
    HEALTHY = "HEALTHY"
    UNHEALTHY = "UNHEALTHY"
    OFFLINE = "OFFLINE"


class PromotionReportType(Enum):
    ALL = "ALL"
    FAILED = "FAILED"
    SUCCEEDED = "SUCCEEDED"


@app.command("models")
@utils.exit_on_error
def model_report(
    project: str = typer.Option(None, help="Project ID."),
    report_type: ModelReportType = typer.Argument(
        "ALL", help="Status to filter report on."
    ),
    all_projects: bool = typer.Option(False, "--all", "-a", help="Show all projects."),
    n: int = typer.Option(30, "--num", "-n", help="Number of records to show."),
    filters_in: List[str] = typer.Option(
        [], "--filter", "-f", help="List of filters.", hidden=True
    ),
    style: utils.ContinualStyle = typer.Option(None, help="Color to use for report."),
):
    c = Client(project=project)
    if project is None:
        project = utils.get_default_project()
    project_snippet = " in ALL projects"
    if not all_projects:
        project_snippet = " in project %s" % project
    if style is None:
        style = c.config.style
    style = utils.get_style(style)

    filters = list(filters_in)  # typer actually passes the List in as a tuple...
    if report_type == ModelReportType.ACTIVE:
        filters.append("latest_mv_state:CREATED")
        filters.append("latest_mv_state:PENDING")
        filters.append("latest_mv_state:PREPROCESSING")
        filters.append("latest_mv_state:TRAINING")
        filters.append("latest_mv_state:POSTPROCESSING")
    elif report_type == ModelReportType.FAILED:
        filters.append("latest_mv_state:CANCELLING")
        filters.append("latest_mv_state:FAILED")
        filters.append("latest_mv_state:CANCELLED")
        filters.append("latest_mv_state:STATE_UNSPECIFIED")
    elif report_type == ModelReportType.SUCCEEDED:
        filters.append("latest_mv_state:SUCCEEDED")
    elif report_type == ModelReportType.HEALTHY:
        filters.append("state:HEALTHY")
    elif report_type == ModelReportType.UNHEALTHY:
        filters.append("state:UNHEALTHY")
    elif report_type == ModelReportType.OFFLINE:
        filters.append("state:OFFLINE")

    data = []
    headers = []
    for m in c.models.list(n, filters=filters, all_projects=all_projects):
        (m_data, headers) = format_model_data(m, all_projects=all_projects)
        data.append(m_data)

    df = pd.DataFrame(data, columns=headers)
    if len(df) > 0:
        main_table = utils.print_table(
            df,
            headers=headers,
            print=False,
            title="%s Models found for report type %s (n=%s) %s"
            % (len(df), report_type.value, n, project_snippet),
            style=style,
        )
        type_df = df.groupby(["Model Version Type"]).count()[["ID"]].reset_index()
        type_df.columns = ["Model Version Type", "Count"]
        type_table = utils.print_table(
            type_df,
            headers=type_df.columns.tolist(),
            print=False,
            title="Count by Type",
            style=style,
        )
        entity_df = df.groupby(["Entity"]).count()[["ID"]].reset_index()
        entity_df.columns = ["Entity", "Count"]
        entity_table = utils.print_table(
            entity_df,
            headers=entity_df.columns.tolist(),
            print=False,
            title="Count by Entity",
            style=style,
        )
        mv_count = df[["# Model Versions"]].sum()[0]
        pred_count = df[["# Batch Predictions"]].sum()[0]
        pro_count = df[["# Promotions"]].sum()[0]
        health_count = df[df["State"] == "HEALTHY"].count()[["ID"]][0]
        summary_panel = Padding(
            Panel(
                "%s Healthy Models out of %s\nTotal # of Model Versions: %s\nTotal # of Promotions: %s\nTotal # of Batch Prediction Jobs: %s"
                % (health_count, len(df), mv_count, pred_count, pro_count),
                style=style,
                title="Summary Stats",
                height=6,
            ),
            (1, 0, 0, 0),
        )

        # help text: the template below is equivalent to:
        # layout = Layout()
        # layout.split(
        #     Layout(main_table,name="Top", ratio=len(df)),
        #     Layout(name="Bottom", ratio=len(type_df)),
        # )
        # if all_projects:
        #     layout["Bottom"].split(
        #         Layout(project_table, name="Projects"),
        #         Layout(type_table,name="Types"),
        #         Layout(summary_panel,name="Summary Information"),
        #         direction= "horizontal"
        #     )
        template = [
            {"name": "Top", "ratio": len(df), "data": main_table},
            {
                "name": "Bottom",
                "ratio": max(len(type_df), len(entity_df)),
                "direction": "horizontal",
                "children": [
                    {"name": "Types", "data": type_table},
                    {"name": "Entities", "data": entity_table},
                    {"name": "Summary", "data": summary_panel},
                ],
            },
        ]
        if all_projects:
            project_df = df.groupby(["Project"]).count()[["ID"]].reset_index()
            project_df.columns = ["Project", "Count"]
            project_table = utils.print_table(
                project_df,
                headers=project_df.columns.tolist(),
                print=False,
                title="Count by Project",
                style=style,
            )
            template[1]["children"].insert(
                0, {"name": "Projects", "data": project_table}
            )

        layout = utils.build_dashboard(template, direction="vertical")
        rich.print(layout)
    else:
        typer.secho(
            "No models found for report type %s" % (report_type.value), fg="blue"
        )


@app.command("batch-predictions")
@utils.exit_on_error
def batch_prediction_report(
    project: str = typer.Option(None, help="Project to run report on"),
    report_type: GenericReportType = typer.Argument(
        "ALL", help="Status to filter report on"
    ),
    all_projects: bool = typer.Option(False, "--all", "-a", help="Show all projects"),
    n: int = typer.Option(30, "--num", "-n", help="Number of records to show"),
    filters_in: List[str] = typer.Option(
        [], "--filter", "-f", help="List of filters", hidden=True
    ),
    style: utils.ContinualStyle = typer.Option(None, help="Color to use for report"),
):
    c = Client(project=project)
    if project is None:
        project = utils.get_default_project()
    project_snippet = " in ALL projects"
    if not all_projects:
        project_snippet = " in project %s" % project
    if style is None:
        style = c.config.style
    style = utils.get_style(style)

    # typer actually passes the List in as a tuple...
    filters = list(filters_in)
    if report_type == GenericReportType.ACTIVE:
        filters.append("state:CREATED")
        filters.append("state:PENDING")
        filters.append("state:PREPROCESSING")
        filters.append("state:PROCESSING")
        filters.append("state:POSTPROCESSING")
    elif report_type == GenericReportType.FAILED:
        filters.append("state:CANCELLING")
        filters.append("state:FAILED")
        filters.append("state:CANCELLED")
        filters.append("state:STATE_UNSPECIFIED")
    elif report_type == GenericReportType.SUCCEEDED:
        filters.append("state:SUCCEEDED")

    data = []
    headers = []
    for bpj in c.batch_prediction_jobs.list(
        n, filters=filters, all_projects=all_projects
    ):
        (bpj_data, headers) = format_batch_prediction_data(
            bpj, all_projects=all_projects
        )
        data.append(bpj_data)

    df = pd.DataFrame(data, columns=headers)
    if len(df) > 0:
        main_table = utils.print_table(
            df,
            headers=headers,
            print=False,
            title="%s Batch Prediction Jobs found for report type %s (n=%s) %s"
            % (len(df), report_type.value, n, project_snippet),
            style=style,
        )
        model_df = df.groupby(["Model"]).count()[["ID"]].reset_index()
        model_df.columns = ["Model", "Count"]
        model_table = utils.print_table(
            model_df,
            headers=model_df.columns.tolist(),
            print=False,
            title="Count by Model",
            style=style,
        )
        # inc_df = df.groupby(["Incremental"]).count()[["ID"]].reset_index()
        # inc_df.columns = ["Incremental", "Count"]
        # inc_table = utils.print_table(
        #    inc_df, headers=inc_df.columns.tolist(), print=False, title="Count by Type")
        model_dur_df = df.groupby(["Model"]).mean()[["Duration (s)"]].reset_index()
        model_dur_df.columns = ["Model", "Average Duration"]
        model_dur_table = utils.print_table(
            model_dur_df,
            headers=model_dur_df.columns.tolist(),
            print=False,
            title="Avg Duration by Model",
            style=style,
        )
        pred_count = df[["# Predictions"]].sum()[0]
        duration = df[["Duration (s)"]].sum()[0]
        health_count = df[df["State"] == "SUCCEEDED"].count()[["ID"]][0]
        size = len(df)
        summary_panel = Padding(
            Panel(
                "%s Successful Jobs out of %s\nTotal # of Predictions: %s\nAvg # of Predictions: %s\nTotal Time Spent Predicting: %s\nAvg Time Spent Predicting: %s"
                % (
                    health_count,
                    size,
                    pred_count,
                    pred_count / size,
                    duration,
                    duration / size,
                ),
                style=style,
                title="Summary Stats",
                height=7,
            ),
            (1, 0, 0, 0),
        )

        template = [
            {"name": "Top", "ratio": len(df), "data": main_table},
            {
                "name": "Bottom",
                "ratio": max(len(model_df), len(model_dur_df)),
                "direction": "horizontal",
                "children": [
                    {"name": "Models", "data": model_table},
                    {"name": "Duration", "data": model_dur_table},
                    # {"name": "Type", "data": inc_table},
                    {"name": "Summary", "data": summary_panel},
                ],
            },
        ]
        if all_projects:
            project_df = df.groupby(["Project"]).count()[["ID"]].reset_index()
            project_df.columns = ["Project", "Count"]
            project_table = utils.print_table(
                project_df,
                headers=project_df.columns.tolist(),
                print=False,
                title="Count by Project",
                style=style,
            )
            template[1]["children"].insert(
                0, {"name": "Projects", "data": project_table}
            )

        layout = utils.build_dashboard(template, direction="vertical")
        rich.print(layout)
    else:
        typer.secho(
            "No batch predictions found for report type %s" % (report_type.value),
            fg="blue",
        )


@app.command("promotions")
@utils.exit_on_error
def promotion_report(
    project: str = typer.Option(None, help="Project to run report on"),
    report_type: PromotionReportType = typer.Argument(
        "ALL", help="Status to filter report on"
    ),
    all_projects: bool = typer.Option(False, "--all", "-a", help="Show all projects"),
    n: int = typer.Option(30, "--num", "-n", help="Number of records to show"),
    filters_in: List[str] = typer.Option(
        [], "--filter", "-f", help="List of filters", hidden=True
    ),
    style: utils.ContinualStyle = typer.Option(None, help="Color to use for report"),
):
    c = Client(project=project)
    if project is None:
        project = utils.get_default_project()
    project_snippet = " in ALL projects"
    if not all_projects:
        project_snippet = " in project %s" % project
    if style is None:
        style = c.config.style
    style = utils.get_style(style)

    # typer actually passes the List in as a tuple...
    filters = list(filters_in)
    if report_type == GenericReportType.FAILED:
        filters.append("state:FAILED")
        filters.append("state:INVALID")
    elif report_type == GenericReportType.SUCCEEDED:
        filters.append("state:SUCCEEDED")

    data = []
    headers = []
    for pr in c.promotions.list(n, filters=filters, all_projects=all_projects):
        (pr_data, headers) = format_promotion_data(pr, all_projects=all_projects)
        data.append(pr_data)

    df = pd.DataFrame(data, columns=headers)
    if len(df) > 0:
        main_table = utils.print_table(
            df,
            headers=headers,
            print=False,
            title="%s Promotions found for report type %s (n=%s) %s"
            % (len(df), report_type.value, n, project_snippet),
            style=style,
        )
        model_df = df.groupby(["Model"]).count()[["ID"]].reset_index()
        model_df.columns = ["Model", "Count"]
        model_table = utils.print_table(
            model_df,
            headers=model_df.columns.tolist(),
            print=False,
            title="Count by Model",
            style=style,
        )
        health_count = df[df["State"] == "SUCCEEDED"].count()[["ID"]][0]
        size = len(df)
        summary_panel = Padding(
            Panel(
                "%s Successful Promotions out of %s" % (health_count, size),
                style=style,
                title="Summary Stats",
                height=3,
            ),
            (1, 0, 0, 0),
        )

        template = [
            {"name": "Top", "ratio": len(df), "data": main_table},
            {
                "name": "Bottom",
                "ratio": len(model_df),
                "direction": "horizontal",
                "children": [
                    {"name": "Models", "data": model_table},
                    {"name": "Summary", "data": summary_panel},
                ],
            },
        ]
        if all_projects:
            project_df = df.groupby(["Project"]).count()[["ID"]].reset_index()
            project_df.columns = ["Project", "Count"]
            project_table = utils.print_table(
                project_df,
                headers=project_df.columns.tolist(),
                print=False,
                title="Count by Project",
                style=style,
            )
            template[1]["children"].insert(
                0, {"name": "Projects", "data": project_table}
            )

        layout = utils.build_dashboard(template, direction="vertical")
        rich.print(layout)
    else:
        typer.secho(
            "No promotions found for report type %s" % (report_type.value), fg="blue"
        )


@app.command("experiments")
@utils.exit_on_error
def experiment_report(
    project: str = typer.Option(None, help="Project to run report on"),
    report_type: GenericReportType = typer.Argument(
        "ALL", help="Status to filter report on"
    ),
    all_projects: bool = typer.Option(False, "--all", "-a", help="Show all projects"),
    n: int = typer.Option(30, "--num", "-n", help="Number of records to show"),
    filters_in: List[str] = typer.Option(
        [], "--filter", "-f", help="List of filters", hidden=True
    ),
    style: utils.ContinualStyle = typer.Option(None, help="Color to use for report"),
):
    c = Client(project=project)
    if project is None:
        project = utils.get_default_project()
    project_snippet = " in ALL projects"
    if not all_projects:
        project_snippet = " in project %s" % project
    if style is None:
        style = c.config.style
    style = utils.get_style(style)

    # typer actually passes the List in as a tuple...
    filters = list(filters_in)
    if report_type == GenericReportType.ACTIVE:
        filters.append("state:CREATED")
        filters.append("state:PENDING")
        filters.append("state:PREPROCESSING")
        filters.append("state:TRAINING")
        filters.append("state:POSTPROCESSING")
    elif report_type == GenericReportType.FAILED:
        filters.append("state:CANCELLING")
        filters.append("state:FAILED")
        filters.append("state:CANCELLED")
        filters.append("state:STATE_UNSPECIFIED")
    elif report_type == GenericReportType.SUCCEEDED:
        filters.append("state:SUCCEEDED")

    data = []
    headers = []
    for e in c.experiments.list(n, filters=filters, all_projects=all_projects):
        (e_data, headers) = format_experiments_data(e, all_projects=all_projects)
        data.append(e_data)

    df = pd.DataFrame(data, columns=headers)
    if len(df) > 0:
        main_table = utils.print_table(
            df,
            headers=headers,
            print=False,
            title="%s Experiments found for report type %s (n=%s) %s"
            % (len(df), report_type.value, n, project_snippet),
            style=style,
        )
        model_df = df.groupby(["Model"]).count()[["ID"]].reset_index()
        model_df.columns = ["Model", "Count"]
        model_table = utils.print_table(
            model_df,
            headers=model_df.columns.tolist(),
            print=False,
            title="Count by Model",
            style=style,
        )
        model_dur_df = df.groupby(["Model"]).mean()[["Duration (s)"]].reset_index()
        model_dur_df.columns = ["Model", "Average Duration"]
        model_dur_table = utils.print_table(
            model_dur_df,
            headers=model_dur_df.columns.tolist(),
            print=False,
            title="Avg Duration by Model",
            style=style,
        )
        # algo_dur_df = df.groupby(["Algorithm"]).mean()[
        #    ["Duration (s)"]].reset_index()
        # algo_dur_df.columns = ["Algorithm", "Average Duration"]
        # algo_dur_table = utils.print_table(
        #    algo_dur_df, headers=model_dur_df.columns.tolist(), print=False, title="Avg Duration by Algorithm")
        duration = df[["Duration (s)"]].sum()[0]
        health_count = df[df["State"] == "SUCCEEDED"].count()[["ID"]][0]
        size = len(df)
        summary_panel = Padding(
            Panel(
                "%s Successful Experiments out of %s\nTotal Experiment Time: %s s\nAverage Experiment Time:%s s"
                % (health_count, size, duration, duration / size),
                style=style,
                title="Summary Stats",
                height=5,
            ),
            (1, 0, 0, 0),
        )

        template = [
            {"name": "Top", "ratio": len(df), "data": main_table},
            {
                "name": "Bottom",
                "ratio": max(len(model_df), len(model_dur_df)),
                "direction": "horizontal",
                "children": [
                    {"name": "Models", "data": model_table},
                    {"name": "Models", "data": model_dur_table},
                    # {"name": "Models", "data": algo_dur_table},
                    {"name": "Summary", "data": summary_panel},
                ],
            },
        ]
        if all_projects:
            project_df = df.groupby(["Project"]).count()[["ID"]].reset_index()
            project_df.columns = ["Project", "Count"]
            project_table = utils.print_table(
                project_df,
                headers=project_df.columns.tolist(),
                print=False,
                title="Count by Project",
                style=style,
            )
            template[1]["children"].insert(
                0, {"name": "Projects", "data": project_table}
            )

        layout = utils.build_dashboard(template, direction="vertical")
        rich.print(layout)
    else:
        typer.secho(
            "No experiments found for report type %s" % (report_type.value), fg="blue"
        )


@app.command("feature-sets")
@utils.exit_on_error
def feature_set_report(
    project: str = typer.Option(None, help="Project to run report on"),
    all_projects: bool = typer.Option(False, "--all", "-a", help="Show all projects"),
    n: int = typer.Option(30, "--num", "-n", help="Number of records to show"),
    filters_in: List[str] = typer.Option(
        [], "--filter", "-f", help="List of filters", hidden=True
    ),
    style: utils.ContinualStyle = typer.Option(None, help="Color to use for report"),
):
    c = Client(project=project)
    if project is None:
        project = utils.get_default_project()
    project_snippet = " in ALL projects"
    if not all_projects:
        project_snippet = " in project %s" % project
    if style is None:
        style = c.config.style
    style = utils.get_style(style)

    # typer actually passes the List in as a tuple...
    filters = list(filters_in)

    data = []
    headers = []
    for fs in c.feature_sets.list(n, filters=filters, all_projects=all_projects):
        (fs_data, headers) = format_feature_set_data(fs, all_projects=all_projects)
        data.append(fs_data)

    df = pd.DataFrame(data, columns=headers)
    if len(df) > 0:
        main_table = utils.print_table(
            df,
            headers=headers,
            print=False,
            title="%s Feature Sets found (n=%s) %s" % (len(df), n, project_snippet),
            style=style,
        )
        entity_df = df.groupby(["Entity"]).sum()[["# Columns", "# Rows"]].reset_index()
        entity_df.columns = ["Entity", "# Columns", "# Rows"]
        entity_table = utils.print_table(
            entity_df,
            headers=entity_df.columns.tolist(),
            print=False,
            title="Stats by Entity",
            style=style,
        )
        feature_count = df[["# Columns"]].sum()[0]
        size = len(df)
        summary_panel = Padding(
            Panel(
                "%s Total Feature Sets \nTotal Number of Entities: %s\nTotal \nTotal Number of Columns: %s"
                % (size, len(entity_df), feature_count),
                style=style,
                title="Summary Stats",
                height=5,
            ),
            (1, 0, 0, 0),
        )

        template = [
            {"name": "Top", "ratio": len(df), "data": main_table},
            {
                "name": "Bottom",
                "ratio": len(entity_df),
                "direction": "horizontal",
                "children": [
                    {"name": "Entities", "data": entity_table},
                    {"name": "Stats", "data": summary_panel},
                ],
            },
        ]
        if all_projects:
            project_df = df.groupby(["Project"]).count()[["ID"]].reset_index()
            project_df.columns = ["Project", "Count"]
            project_table = utils.print_table(
                project_df,
                headers=project_df.columns.tolist(),
                print=False,
                title="Count by Project",
                style=style,
            )
            template[1]["children"].insert(
                0, {"name": "Projects", "data": project_table}
            )

        layout = utils.build_dashboard(template, direction="vertical")
        rich.print(layout)
    else:
        typer.secho("No feature sets found", fg="blue")


# # ingestions
# @app.command("ingestion-report")
# @utils.exit_on_error
# def ingestion_report(
#     project: str = typer.Option(None, help="Project to run report on."),
#     report_type: GenericReportType = typer.Argument(
#         "ALL", help="Status to filter report on"
#     ),
#     all_projects: bool = typer.Option(
#         False, "--all", "-a", help="Filter on current project?"
#     ),
#     n: int = typer.Option(30, "--num", "-n", help="Number of records to show"),
#     filters_in: List[str] = typer.Option(
#         [], "--filter", "-f", help="List of filters", hidden=True
#     ),
# ):
#     c = Client(project=project)
#     if project is None:
#         project = utils.get_default_project()
#     project_snippet = " in ALL projects"
#     if not all_projects:
#         project_snippet = " in project %s" % project

#     # typer actually passes the List in as a tuple...
#     filters = list(filters_in)
#     if report_type == GenericReportType.ACTIVE:
#         filters.append("state:PENDING")
#         filters.append("state:RUNNING")
#     elif report_type == GenericReportType.FAILED:
#         filters.append("state:CANCELLING")
#         filters.append("state:FAILED")
#         filters.append("state:CANCELLED")
#         filters.append("state:STATE_UNSPECIFIED")
#     elif report_type == GenericReportType.SUCCEEDED:
#         filters.append("state:SUCCEEDED")

#     data = []
#     headers = []
#     for i in c.ingestions.list(n, filters=filters, all_projects=all_projects):
#         (i_data, headers) = format_ingestion_data(i, all_projects=all_projects)
#         data.append(i_data)

#     df = pd.DataFrame(data, columns=headers)
#     if len(df) > 0:
#         main_table = utils.print_table(
#             df,
#             headers=headers,
#             print=False,
#             title="%s Ingestions found for report type %s (n=%s) %s"
#             % (len(df), report_type.value, n, project_snippet),
#         )
#         fs_df = df.groupby(["Feature Set"]).count()[["ID"]].reset_index()
#         fs_df.columns = ["Feature Set", "Count"]
#         fs_table = utils.print_table(
#             fs_df,
#             headers=fs_df.columns.tolist(),
#             print=False,
#             title="Count by Feature Set",
#         )
#         ing_dur_df = df.groupby(["Feature Set"]).mean()[["Duration (s)"]].reset_index()
#         ing_dur_df.columns = ["Feature Set", "Average Duration"]
#         ing_dur_table = utils.print_table(
#             ing_dur_df,
#             headers=ing_dur_df.columns.tolist(),
#             print=False,
#             title="Avg Duration by Feature Set",
#         )
#         duration = df[["Duration (s)"]].sum()[0]
#         rows = df[["Ingested Rows"]].sum()[0]
#         health_count = df[df["State"] == "SUCCEEDED"].count()[["ID"]][0]
#         size = len(df)
#         summary_panel = Padding(
#             Panel(
#                 "%s Successful Ingestions out of %s\nTotal Ingestion Time: %s s\nAverage Ingestion Time:%s s\nTotal Rows Ingested: %s \nAverage Rows Ingested: %s"
#                 % (health_count, size, duration, duration / size, rows, rows / size),
#                 style=utils.continual_style_blue,
#                 title="Summary Stats",
#                 height=7,
#             ),
#             (1, 0, 0, 0),
#         )

#         template = [
#             {"name": "Top", "ratio": len(df), "data": main_table},
#             {
#                 "name": "Bottom",
#                 "ratio": max(len(fs_df), len(ing_dur_df)),
#                 "direction": "horizontal",
#                 "children": [
#                     {"name": "Models", "data": fs_table},
#                     {"name": "Models", "data": ing_dur_table},
#                     {"name": "Summary", "data": summary_panel},
#                 ],
#             },
#         ]
#         if all_projects:
#             project_df = df.groupby(["Project"]).count()[["ID"]].reset_index()
#             project_df.columns = ["Project", "Count"]
#             project_table = utils.print_table(
#                 project_df,
#                 headers=project_df.columns.tolist(),
#                 print=False,
#                 title="Count by Project",
#             )
#             template[1]["children"].insert(
#                 0, {"name": "Projects", "data": project_table}
#             )

#         layout = utils.build_dashboard(template, direction="vertical")
#         rich.print(layout)
#     else:
#         typer.secho(
#             "No ingestions found for report type %s" % (report_type.value), fg="blue"
#         )


# model versions
@app.command("model-versions")
@utils.exit_on_error
def model_version_report(
    project: str = typer.Option(None, help="Project to run report on"),
    report_type: GenericReportType = typer.Argument(
        "ALL", help="Status to filter report on"
    ),
    all_projects: bool = typer.Option(False, "--all", "-a", help="Show all projects"),
    n: int = typer.Option(30, "--num", "-n", help="Number of records to show"),
    filters_in: List[str] = typer.Option(
        [], "--filter", "-f", help="List of filters", hidden=True
    ),
    style: utils.ContinualStyle = typer.Option(None, help="Color to use for report"),
):
    c = Client(project=project)
    if project is None:
        project = utils.get_default_project()
    project_snippet = " in ALL projects"
    if not all_projects:
        project_snippet = " in project %s" % project
    if style is None:
        style = c.config.style
    style = utils.get_style(style)

    # typer actually passes the List in as a tuple...
    filters = list(filters_in)
    if report_type == GenericReportType.ACTIVE:
        filters.append("state:CREATED")
        filters.append("state:PENDING")
        filters.append("state:PREPROCESSING")
        filters.append("state:TRAINING")
        filters.append("state:POSTPROCESSING")
    elif report_type == GenericReportType.FAILED:
        filters.append("state:CANCELLING")
        filters.append("state:FAILED")
        filters.append("state:CANCELLED")
        filters.append("state:STATE_UNSPECIFIED")
    elif report_type == GenericReportType.SUCCEEDED:
        filters.append("state:SUCCEEDED")

    data = []
    headers = []
    for mv in c.model_versions.list(n, filters=filters, all_projects=all_projects):
        (mv_data, headers) = format_model_version_data(mv, all_projects=all_projects)
        data.append(mv_data)

    df = pd.DataFrame(data, columns=headers)
    if len(df) > 0:
        main_table = utils.print_table(
            df,
            headers=headers,
            print=False,
            title="%s Model Versions found for report type %s (n=%s) %s"
            % (len(df), report_type.value, n, project_snippet),
            style=style,
        )
        model_df = df.groupby(["Model"]).count()[["ID"]].reset_index()
        model_df.columns = ["Model", "Count"]
        model_table = utils.print_table(
            model_df,
            headers=model_df.columns.tolist(),
            print=False,
            title="Count by Model",
            style=style,
        )
        metric_df = (
            df.groupby(["Model", "Metric"])[["Metric Val"]]
            .agg(["min", "max"])
            .reset_index()
        )
        metric_df.columns = ["Model", "Metric", "Min", "Max"]
        metric_table = utils.print_table(
            metric_df,
            headers=metric_df.columns.tolist(),
            print=False,
            title="Min/Max Metric by Model",
            style=style,
        )
        promoted = len(df[df["Promoted"] == True])
        health_count = len(df[df["State"] == "SUCCEEDED"])
        size = len(df)
        summary_panel = Padding(
            Panel(
                "%s Successful Model Versions out of %s\nTotal Promoted Model Versions: %s"
                % (health_count, size, promoted),
                style=style,
                title="Summary Stats",
                height=4,
            ),
            (1, 0, 0, 0),
        )

        template = [
            {"name": "Top", "ratio": len(df), "data": main_table},
            {
                "name": "Bottom",
                "ratio": max(len(metric_df), len(model_df)),
                "direction": "horizontal",
                "children": [
                    {"name": "Models", "data": model_table},
                    {"name": "Metrics", "data": metric_table},
                    {"name": "Summary", "data": summary_panel},
                ],
            },
        ]
        if all_projects:
            project_df = df.groupby(["Project"]).count()[["ID"]].reset_index()
            project_df.columns = ["Project", "Count"]
            project_table = utils.print_table(
                project_df,
                headers=project_df.columns.tolist(),
                print=False,
                title="Count by Project",
                style=style,
            )
            template[1]["children"].insert(
                0, {"name": "Projects", "data": project_table}
            )

        layout = utils.build_dashboard(template, direction="vertical")
        rich.print(layout)
    else:
        typer.secho(
            "No model versions found for report type %s" % (report_type.value),
            fg="blue",
        )


# proj
@app.command("projects")
@utils.exit_on_error
def project_report(
    n: int = typer.Option(30, "--num", "-n", help="Number of records to show"),
    filters_in: List[str] = typer.Option(
        [], "--filter", "-f", help="List of filters", hidden=True
    ),
    style: utils.ContinualStyle = typer.Option(None, help="Color to use for report"),
):
    c = Client()
    if style is None:
        style = c.config.style
    style = utils.get_style(style)

    # typer actually passes the List in as a tuple...
    filters = list(filters_in)

    data = []
    headers = []
    for p in c.projects.list(n, filters=filters):
        (p_data, headers) = format_project_data(p)
        data.append(p_data)

    df = pd.DataFrame(data, columns=headers)
    if len(df) > 0:
        main_table = utils.print_table(
            df,
            headers=headers,
            print=False,
            title="%s Projects Found (n=%s)" % (len(df), n),
            style=style,
        )
        org_df = df.groupby(["Organization"]).count()[["ID"]].reset_index()
        org_df.columns = ["Organizaiton", "Count"]
        org_table = utils.print_table(
            org_df,
            headers=org_df.columns.tolist(),
            print=False,
            title="Count by Organization",
            style=style,
        )
        fstore_df = df.groupby(["FStore Type"]).count()[["ID"]].reset_index()
        fstore_df.columns = ["Feature Store Type", "Count"]
        fstore_table = utils.print_table(
            fstore_df,
            headers=fstore_df.columns.tolist(),
            print=False,
            title="Count by Feature Store Type",
            style=style,
        )
        fs_count = df[["# Feature Sets"]].sum()[0]
        feature_count = df[["# Features"]].sum()[0]
        model_count = df[["# Models"]].sum()[0]
        mv_count = df[["# Model Versions"]].sum()[0]
        prediction_count = df[["# Predictions"]].sum()[0]
        size = len(df)
        summary_panel = Padding(
            Panel(
                "%s Projects Total\nTotal Feature Sets: %s\nTotal Features: %s\nTotal Models: %s\nTotal Model Versions: %s \nTotal Predictions: %s"
                % (
                    size,
                    fs_count,
                    feature_count,
                    model_count,
                    mv_count,
                    prediction_count,
                ),
                style=style,
                title="Summary Stats",
                height=8,
            ),
            (1, 0, 0, 0),
        )

        template = [
            {"name": "Top", "ratio": len(df), "data": main_table},
            {
                "name": "Bottom",
                "ratio": max(len(fstore_df), len(org_df)),
                "direction": "horizontal",
                "children": [
                    {"name": "Models", "data": org_table},
                    {"name": "Metrics", "data": fstore_table},
                    {"name": "Summary", "data": summary_panel},
                ],
            },
        ]

        layout = utils.build_dashboard(template, direction="vertical")
        rich.print(layout)
    else:
        typer.secho("No projects found", fg="blue")


# changes


@app.command("changes")
@utils.exit_on_error
def changes_report(
    project: str = typer.Option(None, help="Project to run report on"),
    report_type: GenericReportType = typer.Argument(
        "ALL", help="Status to filter report on"
    ),
    all_projects: bool = typer.Option(False, "--all", "-a", help="Show all projects"),
    n: int = typer.Option(30, "--num", "-n", help="Number of records to show"),
    filters_in: List[str] = typer.Option(
        [], "--filter", "-f", help="List of filters", hidden=True
    ),
    style: utils.ContinualStyle = typer.Option(None, help="Color to use for report"),
):
    c = Client(project=project)
    if project is None:
        project = utils.get_default_project()
    project_snippet = " in ALL projects"
    if not all_projects:
        project_snippet = " in project %s" % project
    if style is None:
        style = c.config.style
    style = utils.get_style(style)

    # typer actually passes the List in as a tuple...
    filters = list(filters_in)
    if report_type == GenericReportType.ACTIVE:
        filters.append("state:PENDING")
        filters.append("state:EXECUTING")
    elif report_type == GenericReportType.FAILED:
        filters.append("state:CANCELLING")
        filters.append("state:FAILED")
        filters.append("state:CANCELLED")
        filters.append("state:STATE_UNSPECIFIED")
    elif report_type == GenericReportType.SUCCEEDED:
        filters.append("state:SUCCEEDED")

    data = []
    headers = []
    pushes = c.changes.list(n, filters=filters, all_projects=all_projects)
    (data, headers) = format_changes_data(pushes, project, n, filters, all_projects)

    df = pd.DataFrame(data, columns=headers)
    if len(df) > 0:
        main_table = utils.print_table(
            df,
            headers=headers,
            print=False,
            title="%s Changes found for report type %s (n=%s) %s"
            % (len(df), report_type.value, n, project_snippet),
            style=style,
        )
        health_count = len(df[df["State"] == "SUCCEEDED"])
        size = len(df)
        summary_panel = Padding(
            Panel(
                "%s Successful Changes out of %s" % (health_count, size),
                style=style,
                title="Summary Stats",
                height=3,
            ),
            (1, 0, 0, 0),
        )

        template = [
            {"name": "Top", "ratio": len(df), "data": main_table},
            {
                "name": "Bottom",
                "ratio": 1,
                "direction": "horizontal",
                "children": [{"name": "Summary", "data": summary_panel}],
            },
        ]
        if all_projects:
            project_df = df.groupby(["Project"]).count()[["ID"]].reset_index()
            project_df.columns = ["Project", "Count"]
            project_table = utils.print_table(
                project_df,
                headers=project_df.columns.tolist(),
                print=False,
                title="Count by Project",
                style=style,
            )
            template[1]["children"].insert(
                0, {"name": "Projects", "data": project_table}
            )

        layout = utils.build_dashboard(template, direction="vertical")
        rich.print(layout)
    else:
        typer.secho(
            "No changes found for report type %s" % (report_type.value), fg="blue"
        )


# users
## TODO
# @app.command("user-report")
# @utils.exit_on_error
# def user_report(

# org
## TODO
# @app.command("organization-report")
# @utils.exit_on_error
# def organization_report(

# events
## TODO
# @app.command("event-report")
# @utils.exit_on_error
# def event_report(


# feature store
## TODO
# @app.command("feature-store-report")
# @utils.exit_on_error
# def feature_store_report(
