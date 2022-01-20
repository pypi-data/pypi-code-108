#!/usr/bin/env python3

import typer
import os
import yaml

from continual.python.cli import utils
from continual.python.sdk.featurestore_config import FeaturestoreConfig
from continual import Client
from continual.rpc.management.v1.types import FieldType

from rich.console import Console
from typing import List
from pathlib import Path
from enum import Enum

app = typer.Typer(help="Manage projects.")


class SchemaType(str, Enum):
    FeatureSet = "FeatureSet"
    Model = "Model"


def format_project_data(p, zipped=False):
    create_time = p.create_time.replace(microsecond=0)
    update_time = p.update_time.replace(microsecond=0)
    org = p.organization.split("/")[-1]
    fs_type = p.data_store.type
    c = Client()
    project_id = p.id
    current_project = c.config.project
    if current_project and current_project == p.name:
        project_id = f"{project_id} (active)"
    data = [
        project_id,
        p.display_name,
        org,
        fs_type,
        p.summary.feature_set_count,
        p.summary.feature_count,
        p.summary.model_count,
        p.summary.model_version_count,
        p.summary.prediction_count,
        create_time,
        # update_time,
    ]
    headers = [
        "ID",
        "Display Name",
        "Organization",
        "Data Warehouse",
        "Feature Sets",
        "Features",
        "Models",
        "Model Versions",
        "Predictions",
        "Created",
        # "Updated",
    ]

    if zipped:
        return tuple(
            [x[0], x[1]] for x in (zip(headers, data))
        )  # for some reason list(zip) causes issues, so ...
    else:
        return (data, headers)


# use callback to run list command if nothing is passed in
@app.callback(invoke_without_command=True)
def default(ctx: typer.Context):
    if ctx.invoked_subcommand is not None:
        return
    else:
        list(n=30, filters=[], style=None)


@app.command("list")
@utils.exit_on_error
def list(
    n: int = typer.Option(30, "--num", "-n", help="Number of records to show."),
    filters: List[str] = typer.Option([], "--filter", "-f", help="List of filters."),
    style: utils.ContinualStyle = typer.Option(None, help="Color to use for list."),
):
    """List projects."""
    c = Client()
    data = []
    headers = []
    filter_snippet = " (n=%s)" % n
    if len(filters) > 0:
        filter_snippet = " with filter %s" % str(filters) + filter_snippet
    for p in c.projects.list(n, filters=filters):
        (p_data, headers) = format_project_data(p)
        data.append(p_data)
    typer.secho("Found %s projects%s:" % (len(data), filter_snippet), fg="blue")
    utils.print_table(data, headers, style=utils.get_style(style))


@app.command("get")
@utils.exit_on_error
def get(
    project_id: str = typer.Argument(..., help="Project ID."),
    json: bool = typer.Option(False, "--json", help="Print full JSON representation."),
):
    """Get project details."""
    project_id = utils.get_project(project_id)  # handle passing in project@env
    c = Client(project=project_id)
    project = c.projects.get(project_id)
    if json:
        console = Console()
        console.print(project.to_dict())
    else:
        data = format_project_data(project, zipped=True)
        typer.secho("\nRetrieving project %s: \n" % (project_id), fg="blue")
        utils.print_info(data)


@app.command("create")
@utils.exit_on_error
def create(
    project: str = typer.Argument(..., help="Name of project."),
    org: str = typer.Option(..., help="Name of organization.", show_default=False),
    feature_store: str = typer.Option(
        ..., help="Feature store config name.", show_default=False
    ),
):
    """Create project."""
    try:
        c = Client()
        c.projects.get(project)
        typer.secho(
            "Project %s already exists. Please try another name.\n" % project, fg="red"
        )
    except:
        fs_config = FeaturestoreConfig()

        try:
            feature_store_dict = dict(fs_config._cp[feature_store])
        except:
            typer.secho(
                "Unable to look up feature store configuration for %s. Exiting..."
                % feature_store,
                fg="red",
            )
            raise typer.Exit(code=1)
        try:
            proj = utils.get_or_create_project(project, org, feature_store_dict)
            typer.secho(
                "Successfully created project %s with feature store %s."
                % (proj.id, feature_store),
                fg="green",
            )
        except Exception as e:
            typer.secho(
                "Error building project with feature store configuration %s: %s"
                % (feature_store, str(e)),
                fg="red",
            )
            raise typer.Exit(code=1)


@app.command("delete")
@utils.exit_on_error
def delete(
    project_id: str = typer.Argument(..., help="Project ID."),
    force: bool = typer.Option(
        False, "--force", help="Force deletion. Skips confirmation."
    ),
    delete_schema: bool = typer.Option(
        False,
        "--delete-schema",
        help="Delete the underlying data warehouse schema (in BigQuery, the schema corresponds to the 'dataset').",
    ),
):
    """Delete project."""
    project_id = utils.get_project(project_id)
    if not force:
        force = typer.confirm(
            "Are you sure you want to delete the project %s?" % project_id
        )
    if force:
        c = Client(project=project_id)
        project = c.projects.get(project_id)
        project.delete(delete_schema=delete_schema)
        typer.secho("Successfully deleted project %s." % project_id, fg="green")
    else:
        typer.secho("Skipping deletion!")


@app.command("update")
@utils.exit_on_error
def update(
    project_id: str = typer.Argument(..., help="Project ID."),
    new_name: str = typer.Option(None, help="New project name"),
    feature_store: str = typer.Option(
        None, help="Feature store config name.", show_default=False
    ),
):
    """Update project."""
    project_id = utils.get_project(project_id)
    c = Client(project=project_id)
    project = c.projects.get(project_id)
    feature_store_dict = project.data_store
    if feature_store:
        fs_config = FeaturestoreConfig()

        try:
            feature_store_dict = dict(fs_config._cp[feature_store])
        except:
            typer.secho(
                "Unable to look up feature store configuration for %s. Exiting..."
                % feature_store,
                fg="red",
            )
            raise typer.Exit(code=1)
    if new_name is None:
        new_name = project.display_name
    project.update(display_name=new_name, data_store=feature_store_dict)
    typer.secho("Successfully updated project %s." % project_id, fg="green")


@app.command("seed")
@utils.exit_on_error
def seed(
    paths: List[Path] = typer.Argument(
        ..., exists=True, dir_okay=True, help="Path to CSV file(s)."
    ),
    project_id: str = typer.Option(None, "--project", help="Project ID."),
    environment: str = typer.Option(None, "--env", hidden=True, help="Environment ID."),
    table: str = typer.Option(None, help="Table name to create and store data into. "),
):
    """Upload data to data warehouse.

    Uploads all given CSV files to the project and create tables loaded with data.
    The PATHS can be a list of CSV files to be uploaded.
    """

    project, environment = utils.get_project_and_environment(project_id, environment)
    client = Client(project=utils.get_environment_name(project, environment))
    env = client.environments.get(environment)

    if len(env.data_store.type) == 0:
        typer.secho(
            "No datastore set for %s. Please update via `continual environments update` or `continual projects update` or in the Environments menu in the UI."
            % env.id,
            fg="red",
        )
        raise typer.Exit(code=1)

    # typer path type is PosixPath, which our SDK doesn't expect. Only works w/ strings or list of strings.
    if len(paths) > 0:
        paths = [str(path) for path in paths]

    for path in paths:
        typer.secho("Seeding file %s" % path, fg="blue")
        try:
            (_, new_table) = env.seed(path, table_name=table)
            (schema, database) = utils.get_datastore_database_and_schema(env.data_store)
            if database:
                database = database + "."
            if schema:
                schema = schema + "."
            typer.secho(
                "Successfully seeded file %s to %s%s%s"
                % (
                    path,
                    database,
                    schema,
                    new_table,
                ),
                fg="green",
            )
        except Exception as e:
            typer.secho("Failed to seed file %s: %s" % (path, str(e)), fg="red")
            continue


@app.command("infer-schema")
@utils.exit_on_error
def infer_schema(
    schema_type: SchemaType = typer.Argument(..., help="Schema type to create."),
    project: str = typer.Option(None, help="Project ID."),
    index: str = typer.Option(
        ..., help="Column that corresponds to the model/feature set index."
    ),
    time_index: str = typer.Option(
        None, help="Column that corresponds to the model/feature set time index."
    ),
    split: str = typer.Option(
        None,
        help="Column that corresponds to the model user-defined split (model only)",
    ),
    target: str = typer.Option(None, help="Target column to predict (models only)."),
    entity: str = typer.Option(None, help="Entity to associate resource with."),
    table: str = typer.Option(None, help="Table name."),
    query: str = typer.Option(None, help="SQL query."),
    file: str = typer.Option(None, hidden=True, help="File name."),
    path: Path = typer.Option(None, help="Path to save schema."),
):
    """
    Infers schema from a table or SQL query.
    """
    project = utils.get_project(project)
    c = Client(project=project)
    schema = c.infer_schema(
        project=project, table=table, query=query, file=file, type=schema_type.value
    )

    ##we should probably generalize utils.format_yaml and then use it here as well.
    if table is not None:
        name = table.replace(".", "_")
    elif query is not None:
        name = "SQL_QUERY_INFERRED"
    else:
        name = file.split("/")[-1].split(".")[0]

    columns = []
    for col in schema:
        columns.append(
            {
                "name": col.name,
                "type": FieldType.from_proto(col.type).value,
                # "description" : col.description,
            }
        )

    new_schema = {
        "type": schema_type.value,
        "name": name,
        "description": "Inferred via Continual CLI.",
        "owners": [c.config.email],
        "index": index,
    }

    if time_index:
        new_schema["time_index"] = time_index

    if entity:
        new_schema["entity"] = entity

    if schema_type == SchemaType.Model:
        if target:
            new_schema["target"] = target
        else:
            typer.secho(
                "No target column found. You will need to declare a target before attemping a push.",
                fg="yellow",
            )

        if split:
            new_schema["split"] = split

    new_schema["columns"] = columns

    if table:
        new_schema["table"] = table
    elif query:
        new_schema["query"] = query
    else:
        typer.secho(
            "No table or query found. One of these is required before attemping a push.",
            fg="yellow",
        )

    yaml_text = yaml.dump(new_schema, sort_keys=False)

    if path is None:
        typer.secho("Successfully inferred schema for %s: \n" % table, fg="green")
        print(yaml_text)
    else:
        path = str(path)
        if (path[-4:] != ".yml") and (path[-5:] != ".yaml"):
            path = "%s/%s.yaml" % (path, name)
        with open(path, "w+") as f:
            f.write(yaml_text)
        typer.secho(
            "Successfully inferred schema for %s and saved to file %s." % (table, path),
            fg="green",
        )

        typer.secho(
            "You may can push this file into continual via 'continual push %s`." % path,
            fg="blue",
        )


@app.command("export")
@utils.exit_on_error
def export(
    project_id: str = typer.Option(None, "--project", help="Project ID."),
    path: Path = typer.Option(
        None,
        help="Directory to save projects resources into. Defaults to ./<project_id> if not provided.",
    ),
    # include_predictions: bool = typer.Option(False, "--predictions", hidden=True, help="Include csv of latest predictions for each model"),
):
    """
    Exports project YAMLs to a directory. Akin to 'git clone' for continual.
    If you wish to export a single feature set or model, see
    `continual feature-sets export` or `continual model export` instead.
    """
    project_id = utils.get_project(project_id)
    client = Client(project=project_id)
    project = client.projects.get(project_id)

    export_project(path, project_id, project)


def export_project(path, project_id, project):

    # use cwd/project_id if no path provided
    if path is None:
        path = os.path.join(os.getcwd(), project_id)
        if not os.path.exists(path):
            os.mkdir(path)

    fs_dir = os.path.join(path, "feature_sets")
    model_dir = os.path.join(path, "models")
    # ßbpj_dir = os.path.join(path,"predictions")

    try:
        fs_yamls = []
        if len(project.feature_sets.list()) > 0:
            if not os.path.exists(fs_dir):
                os.mkdir(fs_dir)
            for fs in project.feature_sets.list_all():
                typer.secho("Fetching feature set %s ..." % fs.name, fg="blue")
                fs_text = yaml.load(fs.schema_text, Loader=yaml.FullLoader)
                fs_yaml = utils.format_yaml(fs_text)
                fs_yamls.append((fs.id, fs_yaml))
            utils.save_yamls(fs_yamls, fs_dir)
            typer.secho(
                "Successfully saved feature set yamls in directory: %s \n" % fs_dir,
                fg="green",
            )
        else:
            typer.secho("No feature sets found!", fg="blue")
    except Exception as e:
        typer.secho(
            "Failed to get all feature set yamls:%s \n" % (str(e)),
            fg="red",
        )
    try:
        m_yamls = []
        if len(project.models.list()) > 0:
            if not os.path.exists(model_dir):
                os.mkdir(model_dir)
            for m in project.models.list_all():
                typer.secho("Fetching model %s ... " % m.name, fg="blue")
                m_text = yaml.load(m.schema_text, Loader=yaml.FullLoader)
                m_yaml = utils.format_yaml(m_text)
                m_yamls.append((m.id, m_yaml))
            utils.save_yamls(m_yamls, model_dir)
            typer.secho(
                "Successfully saved model yamls in directory: %s \n" % model_dir,
                fg="green",
            )
        else:
            typer.secho("No models found!", fg="blue")
    except Exception as e:
        typer.secho(
            "Failed to get all model yamls:%s \n" % (str(e)),
            fg="red",
        )
    typer.secho("Export finished!", fg="green")

    # try:
    #     if include_predictions:
    #         if not os.path.exists(bpj_dir):
    #             os.mkdir(bpj_dir)
    #         for m in project.models.list_all():
    #             if m.latest_batch_prediction is not None:
    #                 typer.secho("Fetching latest batch prediction for model %s ... \n" %
    #                             m.name, fg="blue")
    #                 bpj = client.batch_prediction_jobs.get(m.latest_batch_prediction)
    #                 bpj.download(os.path.join(path,"%s_%s.csv" %(m.id, bpj.id)))
    #         typer.secho("Successfully saved latest predictions in directory %s: \n" %
    #                             bpj_dir, fg="green")
    # except Exception as e:
    #     typer.secho("Failed to get all latest predictions. Failed at prediction %s:%s \n" %
    #             (bpj.name, str(e)), fg="red")
