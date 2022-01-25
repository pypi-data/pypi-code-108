import typer
import yamale
import os
import yaml

from continual.python.cli import utils
from continual import Client

from pathlib import Path
from rich.console import Console
from typing import List

app = typer.Typer(help="Manage feature set.")


def format_feature_set_data(fs, zipped=False, all_projects=False):
    create_time = fs.create_time.replace(microsecond=0)
    update_time = fs.update_time.replace(microsecond=0)
    if zipped:
        data = [
            fs.id,
            fs.name,
            fs.schema.entity,
            len(fs.schema.columns),
            create_time,
            update_time,
            fs.schema.description[:50],
        ]
        headers = [
            "ID",
            "Name",
            "Entity",
            "Columns",
            "Created",
            "Last Updated",
            "Description",
        ]
        return tuple(
            [x[0], x[1]] for x in (zip(headers, data))
        )  # for some reason list(zip) causes issues, so ...
    else:
        data = [
            fs.id,
            fs.schema.entity,
            len(fs.schema.columns),
            create_time,
            update_time,
            fs.schema.description[:50],
        ]
        headers = [
            "ID",
            "Entity",
            "Columns",
            "Created",
            "Last Updated",
            "Description",
        ]
        if all_projects:
            data.insert(0, fs.parent.split("/")[1])
            headers.insert(0, "Project")
        return (data, headers)


# use callback to run list command if nothing is passed in
@app.callback(invoke_without_command=True)
def default(ctx: typer.Context):
    if ctx.invoked_subcommand is not None:
        return
    else:
        list(
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
    project: str = typer.Option(None, help="Project ID."),
    environment: str = typer.Option(None, "--env", help="Environment ID."),
    n: int = typer.Option(30, "--num", "-n", help="Number of records to show."),
    filters: List[str] = typer.Option(
        [],
        "--filter",
        "-f",
        help="List of filters",
    ),
    all_projects: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Show all projects",
    ),
    style: utils.ContinualStyle = typer.Option(None, help="Color to use for list."),
):
    """List feature sets."""
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
    for fs in c.feature_sets.list(n, filters=filters, all_projects=all_projects):
        (fs_data, headers) = format_feature_set_data(fs, all_projects=all_projects)
        data.append(fs_data)
    typer.secho(
        "\nFound %s feature sets in %s%s:"
        % (len(data), project_snippet, filter_snippet),
        fg="blue",
    )
    utils.print_table(data, headers, style=utils.get_style(style))


@app.command("get")
@utils.exit_on_error
def get(
    feature_set: str = typer.Argument(..., help="Feature set ID."),
    project: str = typer.Option(None, help="Project ID."),
    environment: str = typer.Option(None, "--env", help="Environment ID."),
    json: bool = typer.Option(
        False, "--json", help="Display full JSON representation."
    ),
):
    """Get feature set details."""
    project, environment = utils.get_project_and_environment(project, environment)
    c = Client(project=utils.get_environment_name(project, environment))

    fs = c.feature_sets.get(feature_set)
    console = Console()
    if json:
        console.print(fs.to_dict())
    else:
        data = format_feature_set_data(fs, zipped=True)
        typer.secho("\nRetrieving feature set %s: \n" % (feature_set), fg="blue")
        utils.print_info(data)
        typer.secho("\nFeature set schema:\n", fg="blue")
        console.print(fs.schema.to_dict())


# dev-2222: removing until we have a better way of downloading data
# @app.command("get-data")
# @utils.exit_on_error
# def get_data(
#     feature_set: str = typer.Argument(..., help="Feature set ID."),
#     project: str = typer.Option(None, help="Project ID."),
#     environment: str = typer.Option(None, "--env", help="Environment ID."),
#     path: Path = typer.Option(..., help="Path to save CSV file."),
#     num_rows: int = typer.Option(None, "--n", help="Number of rows to fetch."),
# ):
#     """Get feature set data."""
#     project, environment = utils.get_project_and_environment(project, environment)
#     c = Client(project=utils.get_environment_name(project, environment))
#     fs = c.feature_sets.get(feature_set)
#     path = str(path)

#     try:
#         typer.secho("Starting download of feature set %s." % feature_set, fg="blue")
#         (df, _) = fs.get_data(page_size=num_rows)
#         if path[-4:] != ".csv":
#             path = "%s/%s.csv" % (path, feature_set)
#         if df is not None:
#             df.to_csv(path, index=False)
#             typer.secho(
#                 "Successfully saved data for featureset %s to %s"
#                 % (feature_set, str(path)),
#                 fg="green",
#             )
#         else:
#             typer.secho(
#                 "Failed to download data for feature set %s" % feature_set, fg="red"
#             )
#     except Exception as e:
#         typer.secho(
#             "Failed to get data for feature set %s in project %s, environment %s:%s"
#             % (feature_set, project, environment, str(e)),
#             fg="red",
#         )


@app.command("delete")
@utils.exit_on_error
def delete(
    feature_set: str = typer.Argument(..., help="Feature set ID."),
    project: str = typer.Option(None, help="Project ID."),
    environment: str = typer.Option(None, "--env", help="Environment ID."),
    force: bool = typer.Option(
        False, "--force", help="Force deletion. Skips confirmation."
    ),
):
    """Delete feature set."""
    project, environment = utils.get_project_and_environment(project, environment)
    c = Client(project=utils.get_environment_name(project, environment))
    if not force:
        force = typer.confirm(
            "Are you sure you want to delete feature set %s in project %s, environment %s?"
            % (feature_set, project, environment)
        )
    if force:
        fs = c.feature_sets.get(feature_set)
        fs.delete()
        typer.secho("Successfully deleted feature set %s" % fs.name, fg="green")
    else:
        typer.secho("Deletion Cancelled!", fg="blue")


@app.command("validate")
@utils.exit_on_error
def validate_yaml(
    path: Path = typer.Argument(..., help="Full path of YAML file."),
):
    """Validate feature set YAML file."""
    path = str(path)
    try:
        with open(path, "r") as file:
            text = yaml.load(file, Loader=yaml.FullLoader)
            yaml_type = text.get("type", "").lower()

        if yaml_type == "featureset" or yaml_type == "model":
            schema = yamale.make_schema(
                "%s/%s"
                % (
                    os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                    "extras/%s_reference_schema.yaml" % yaml_type,
                )
            )
            data = yamale.make_data(path)
            yamale.validate(schema, data)
            typer.secho("Schema %s validated. No Errors found!" % path, fg="green")
            return True
        else:
            typer.secho(
                "Given schema does not have a valid type field. Cannot validate. type: %s"
                % yaml_type,
                fg="red",
            )
            return False
    except Exception as e:
        typer.secho("Schema validation for %s failed: \n%s" % (path, str(e)), fg="red")
        return False


@app.command("export")
@utils.exit_on_error
def export_yaml(
    feature_set: str = typer.Argument(..., help="Feature set ID."),
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

    fs = c.feature_sets.get(feature_set)
    fs_text = yaml.load(fs.schema_text, Loader=yaml.FullLoader)
    yaml_text = utils.format_yaml(fs_text)
    if path == "print":
        typer.secho(
            "Successfully extracted YAML file from feature set %s." % feature_set,
            fg="green",
        )
        print(yaml_text)
    else:
        utils.save_yamls([(feature_set, yaml_text)], path)
        typer.secho(
            "Successfully extracted YAML file from feature set %s. Location is %s."
            % (feature_set, path),
            fg="green",
        )


@app.command("diff")
@utils.exit_on_error
def diff(
    right_yaml: str = typer.Option(None, "--ryaml", help="YAML location."),
    right_project: str = typer.Option(None, "--rproj", help="Right project."),
    right_environment: str = typer.Option(None, "--renv", help="Environment ID."),
    right_feature_set: str = typer.Option(None, "--rfs", help="Right feature set."),
    left_yaml: str = typer.Option(None, "--lyaml", help="YAML location."),
    left_project: str = typer.Option(None, "--lproj", help="Left project."),
    left_environment: str = typer.Option(None, "--lenv", help="Environment ID."),
    left_feature_set: str = typer.Option(None, "--lfs", help="Left feature set"),
    models: bool = typer.Option(
        False, hidden=True, help="Diff models instead of feature sets"
    ),
):
    """Diff feature sets.

    Diff feature sets can either provide a local YAML file
    or a feature set id already contained in continual. To use YAML files,
    use the *_yaml options, otherwise specify the continual resources
    via *_project and *_feature_set
    """
    if not ((right_yaml or right_feature_set) and (left_yaml or left_feature_set)):
        typer.secho(
            "Error: You must either provide 2 YAML files or 2 feature-sets. See continual feature-sets diff --help."
        )
    else:
        c = Client()
        (right, left, diff_text) = c.feature_sets.diff(
            right_yaml,
            right_project,
            right_environment,
            right_feature_set,
            left_yaml,
            left_project,
            left_environment,
            left_feature_set,
            models,
        )
        typer.secho(
            "Diffing \n\tleft = %s with \n\tright = %s" % (left, right), fg="blue"
        )
        if len(diff_text) > 0:
            typer.secho(diff_text)
        else:
            typer.secho("No changes found.", fg="blue")
