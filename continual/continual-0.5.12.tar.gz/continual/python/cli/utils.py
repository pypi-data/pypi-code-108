import typer
import logging
import subprocess
import os
import yaml
import pandas as pd

from continual.python.sdk.exceptions import BaseException
from continual.rpc.management.v1 import types
from continual import Client

from enum import Enum
from functools import wraps
from git import Repo

from rich.table import Table
from rich.console import Console
from rich.style import Style
from rich.layout import Layout

logger = logging.getLogger("continual.cli.utils")

continual_style_green = Style(color="rgb(157,209,186)")
continual_style_blue = Style(color="rgb(96,238,252)")
continual_style_purple = Style(color="rgb(63,47,159)")
continual_style_dark_blue = Style(color="rgb(5,27,71)")
continual_style_black = Style(color="rgb(0,0,0)")
continual_style_white = Style(color="rgb(255,255,255)")


class ContinualStyle(Enum):
    WHITE = "WHITE"
    BLACK = "BLACK"
    BLUE = "BLUE"
    GREEN = "GREEN"
    PURPLE = "PURPLE"
    DARK_BLUE = "DARK_BLUE"


class PerformanceMetric(str, Enum):
    RMSE = "rmse"
    MAE = "mae"
    R2 = "r2"
    MAPE = "mape"
    SMAPE = "smape"
    PRECISION = "precision"
    RECALL = "recall"
    ACCURACY = "accuracy"
    ROCAUC = "roc_auc"
    F1 = "f1"
    LOGLOSS = "log_loss"


class SplitType(str, Enum):
    TRAIN = "train"
    VALI = "validation"
    TEST = "test"


def get_style(continual_style):
    if continual_style is None:
        c = Client()
        continual_style = c.config.style
    if not isinstance(continual_style, str):
        continual_style = continual_style.value
    if continual_style.upper() == "WHITE":
        return continual_style_white
    elif continual_style.upper() == "BLACK":
        return continual_style_black
    elif continual_style.upper() == "BLUE":
        return continual_style_blue
    elif continual_style.upper() == "GREEN":
        return continual_style_green
    elif continual_style.upper() == "PURPLE":
        return continual_style_purple
    elif continual_style.upper() == "DARK_BLUE":
        return continual_style_dark_blue


# wrapper function, mainly for convenience.
# but helps prevent calling get_project and get_environment in an undesirable order
def get_project_and_environment(project, environment):
    return (get_project(project), get_environment(project, environment))


# takes project and org display names
# returns project object
# creates project if it doesn't exist
def get_or_create_project(project_name, org_name, data_store, project_id=None):
    # Associate type string with a data store type
    data_store_map = {
        "snowflake": types.DataStoreSnowflake,
        "big_query": types.DataStoreBigQuery,
        "redshift": types.DataStoreRedshift,
        "postgres": types.DataStorePostgres,
    }
    type_name = data_store["type"]

    del data_store["type"]

    data_store_args_dict = {name: None for name in data_store_map}
    data_store_args_dict[type_name] = data_store_map[type_name](**data_store)

    # get project or create if does not exist
    c = Client()
    try:
        if not project_id:
            project_id = "projects/%s" % project_name
            project = get_project_from_display_name(project_name)
        else:
            project = c.projects.get(project_id)
    except Exception:
        org1 = get_or_create_org(org_name)
        ds = types.DataStore(type=type_name, **data_store_args_dict)
        project = c.projects.create(
            display_name=project_name,
            project_id=project_id,
            data_store=ds,
            organization=org1.name,
        )
    return project


# takes environment display names
# returns environment object
# creates environment if it doesn't exist
def get_or_create_environment(display_name, data_store, environment_name=None):
    c = Client()
    try:
        if not environment_name:
            env = get_environment_from_display_name(display_name)
        else:
            env = c.projects.get(environment_name)
    except Exception:
        env = c.environments.create(
            display_name=display_name,
            data_store=data_store,
        )
    return env


# returns proj obj of given display_name
# returns first found, if multiple exist w/ same name
# this exists because you can't re-use a project id once assigned,
### so the previous function may change your project id from projects/<project_name>
### to projects/<project_name>-#. This can be unexpected and lead to errors when trying
### to access the project downstream
# essentially, this imposes uniqueness of the display names
def get_project_from_display_name(project_name):
    c = Client()
    try:
        projs = c.projects.list()
        proj = [x for x in projs if x.display_name == project_name][0]
        return proj
    except:
        raise


def get_environment_from_display_name(project_name, environment_name):
    c = Client()
    try:
        envs = c.environments.list()
        env = [x for x in envs if x.display_name == environment_name][0]
        return env
    except:
        raise


# takes org display name or optionally id
# returns org object
# creates org if display_name doesn't exist
def get_or_create_org(display_name, id=None):
    c = Client()
    try:
        if not id:
            org = get_org_from_display_name(display_name)
        else:
            org = c.organizations.get(id)
    except Exception:
        org = c.organizations.create(display_name)
    return org


# quick fix for dev-464
# returns org id of given display_name
# returns first found, if multiple exist w/ same name
def get_org_from_display_name(org_name):
    c = Client()
    try:
        orgs = c.organizations.list()
        org = [x for x in orgs if x.display_name == org_name][0]
        return org
    except:
        raise


def get_project(project):
    if (project is None) or (project == ""):
        project = get_default_project()
    else:
        if "@" in project:
            project = project.split("@")[0]
    return project


def get_default_project():
    c = Client()
    proj = c.config.project
    if proj is None or proj == "":
        typer.secho(
            "No project set.  Use continual config set-project or --project to set a project.",
            fg="red",
        )
        exit(1)
    return proj.split("/")[-1]


##get environment
# first priority is to use environment variable if it's passed
# second, try to get env out of project string via project@env (either passed or via default project)
# third, get env from git branch
# 4th, use prod (default)
# note: master/main/production are all mapped to 'prod'
def get_environment(project, environment):
    if environment is None or environment == "":
        if project is not None and "@" in project:
            environment = project.split("@")[1]
        else:
            environment = get_default_environment()
    if (
        (environment.lower() == "master")
        or (environment.lower() == "main")
        or (environment.lower() == "production")
    ):  # prevent use of main/master/production, whether we got from git or passed in manually
        environment = "prod"
    if "@" in environment:
        environment = environment.split("@")[-1]
    return environment


##get default environment
# if no environment passed...
# check to see if config has it set.
# if not, get it from git branch
#  if no git branch, then use prod
def get_default_environment():
    c = Client()
    env = c.config.environment
    if env is None or env == "":
        repo = Repo(search_parent_directories=True)
        env = repo.active_branch.name
    if env is None or env == "":
        env = "prod"
    return env


def get_environment_name(project, environment) -> str:
    project = get_project(project)
    environment = get_environment(project, environment)
    if not project.startswith("projects/"):
        project = f"projects/{project}"
    return f"{project}@{environment}"


def get_endpoint():
    c = Client()
    endpoint = c.config.endpoint
    # Assume development with SSH port forwarding.
    if endpoint == "http://localhost":
        endpoint = "http://localhost:9999"
    else:
        endpoint = "https://cloud.continual.ai"
    return endpoint


def print_table(
    data,
    headers,
    print=True,
    style=continual_style_green,
    row_styles=["default", "dim"],
    title=None,
    caption=None,
):
    table = Table(
        expand=True, style=style, row_styles=row_styles, title=title, caption=caption
    )
    for x in headers:
        table.add_column(x, overflow="fold")
    if isinstance(data, pd.DataFrame):
        for i, row in data.iterrows():
            table.add_row(*[str(x) for x in row])
    else:
        for row in data:
            table.add_row(*[str(x) for x in row])
    if print:
        console = Console()
        console.print(table)
    return table


def print_info(
    data, show_index=False, headers="", tablefmt="plain", style=continual_style_blue
):
    # typer.echo(tabulate(data, headers=headers, showindex=show_index, tablefmt=tablefmt))
    table = Table(style=style).grid(expand=True)
    for x in headers:
        table.add_column(x, overflow="fold")
    if isinstance(data, pd.DataFrame):
        for i, row in data.iterrows():
            table.add_row(*[str(x) for x in row])
    else:
        for row in data:
            table.add_row(*[str(x) for x in row])
    console = Console()
    console.print(table)


def process_template(template, layout, split_direction):
    children = []
    next_split = {}
    for obj in template:
        data = obj.get("data", None)
        split = obj.get("children", None)
        if data is not None:
            children.append(
                Layout(
                    obj.get("data"),
                    name=obj.get("name"),
                    ratio=obj.get("ratio", 1),
                    minimum_size=5,
                )
            )
        elif split is not None:
            name = obj.get("name")
            direction = obj.get("direction", "horizontal")
            children.append(
                Layout(name=name, ratio=obj.get("ratio", 1), minimum_size=5)
            )
            next_split["%s:%s" % (name, direction)] = split

    if len(children) > 0:
        layout.split(direction=split_direction, *children)

    if len(next_split) > 0:
        for index in next_split:
            parts = index.split(":")
            name = parts[0]
            direction = parts[1]
            process_template(next_split[index], layout[name], direction)


# template is a list of dict. Each dict defines a split or renderable
# renderable: [{"name":"Top", "ratio": 1, data:<renderable>},
# split: {"name":"Bottom", "ratio": 1, "direction": "horizontal", children: [<next_template]}]
#
def build_dashboard(template, direction="horizontal"):
    layout = Layout()
    process_template(template, layout, direction)
    return layout


def execute_cmd(cmd, print_it=True):
    popen = subprocess.Popen(
        [cmd], stdout=subprocess.PIPE, universal_newlines=True, shell=True
    )
    output = popen.stdout.read()
    exit_code = popen.wait()
    if print_it:
        print(output)
        # print("exit code: %s" %exit_code)
    return (output, exit_code)


def split_large_csv(csv, output, max_chunk_size=209715200):
    if not os.path.exists(output):
        os.mkdir(output)
    execute_cmd(
        "split -C %s -d %s %s/%s" % (max_chunk_size, csv, output, csv.split("/")[-1])
    )
    return [file.path for file in os.scandir(output) if file.is_file()]


# for progress bar


def chunker(seq, size):
    return (seq[pos : pos + size] for pos in range(0, len(seq), size))


def exit_with_error(e):
    """Print error and exit.

    Args:
        e: An exception to print.
    """
    if isinstance(e, BaseException):
        typer.secho("Error: " + str(e.message), fg="red")
        if isinstance(e.details, dict) and len(e.details) > 0:
            typer.secho("Details:", fg="red")
            for key, value in e.details.items():
                typer.secho(f"  {key}: {value}", fg="red")
    else:
        typer.secho("Error: " + str(e), fg="red")
    exit(1)


def exit_on_error(func):
    """Decorator that prints and exits on exceptions.

    Args:
        func: Function to wrap.
    Returns:
        A function that prints error and exit(1) on any exception.
    """

    @wraps(func)
    def function_wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            logger.debug("an error occured in command", exc_info=e)
            exit_with_error(e)

    return function_wrapper


# formats yaml in more 'user-friendly' ordering, as the default ordering returned by API is alphabetical
def format_yaml(old_yaml):

    type = old_yaml.get("type")
    name = old_yaml.get("name")
    new_schema = {
        "type": type,
        "name": name,
    }

    description = old_yaml.get("description", None)
    if description:
        new_schema["description"] = description

    owners = old_yaml.get("owners", None)
    if owners:
        new_schema["owners"] = owners

    new_schema["index"] = old_yaml.get("index")

    time_index = old_yaml.get("time_index", None)
    if time_index:
        new_schema["time_index"] = time_index

    entity = old_yaml.get("entity", None)
    if entity:
        new_schema["entity"] = entity

    target = old_yaml.get("target", None)
    if target:
        new_schema["target"] = target

    split = old_yaml.get("split", None)
    if split:
        new_schema["split"] = split

    columns = old_yaml.get("columns", None)
    if columns:
        new_schema["columns"] = columns

    exclude_columns = old_yaml.get("exclude_columns", None)
    if exclude_columns:
        new_schema["exclude_columns"] = exclude_columns

    profile = old_yaml.get("profile", None)
    if profile:
        new_schema["profile"] = profile

    train = old_yaml.get("train", None)
    if train:
        new_schema["train"] = train

    predict = old_yaml.get("predict", None)
    if predict:
        new_schema["predict"] = predict

    promote = old_yaml.get("promote", None)
    if promote:
        new_schema["promote"] = promote

    table = old_yaml.get("table", None)
    if table:
        new_schema["table"] = table

    query = old_yaml.get("query", None)
    if query:
        new_schema["query"] = (
            query.replace("\n", " ").replace("\t", " ").replace("\\", " ")
        )  # remove stuff that breaks query

    return yaml.safe_dump(new_schema, sort_keys=False)


# takes list of yamls tuples (name,text) and saves them to file
def save_yamls(yamls, continual_dir, print_it=True):
    paths = []
    if not os.path.exists(continual_dir):
        os.makedirs(continual_dir)
    for yaml in yamls:
        path = "%s/%s.yaml" % (continual_dir, yaml[0])
        with open(path, "w+") as f:
            if print_it:
                typer.secho("Saving Continual yaml definition %s!" % path)
            f.write(yaml[1])
        paths.append(path)
    return paths


def print_change(push, project_id, environment_id, message, include_estimate=False):
    typer.secho(f"Updating ({project_id}@{environment_id}):", fg="magenta")
    typer.echo(f"  {message or ''}\n")
    name = push.name
    typer.secho(
        "Operations for %s in project %s, environment %s:"
        % (push.id, project_id, environment_id),
        fg="magenta",
    )
    if len(push.plan) > 0:
        steps = sorted(
            push.plan,
            key=lambda x: int(x.id),
            reverse=False,
        )
        typer.secho(
            f"\n  {'Operation':20s}{'State':20s}",
            fg="magenta",
        )
        old_resource = ""
        featuresets = []
        models = []
        # the id ordering we get back from continual is kind of wonky and has models listed first
        credits = {}
        for step in steps:
            if step.resource_name.split("/")[2] == "models":
                models.append(step)
            else:
                featuresets.append(step)
        for step in featuresets + models:
            step_id = step.resource_name.split("/")[-1]
            if step.resource_name.split("/")[2] == "models":
                step_type = "Model"
            else:
                step_type = "Feature Set"
            if not (old_resource == step_id):
                typer.secho("\n  %s: %s" % (step_type, step_id), fg="blue")
                old_resource = step_id
            typer.echo(f"  {step.operation:20s}{step.state:20s}")
            if include_estimate:
                if step.operation.value == "TRAIN":
                    credits_used = get_model_credit_estimate(step.resource_name)
                    credits["%s %s" % (step_id, step.operation.value)] = credits_used
                if step.operation.value == "PREDICT":
                    credits_used = get_batch_prediction_credit_estimate(
                        step.resource_name
                    )
                    credits["%s %s" % (step_id, step.operation.value)] = credits_used

        if include_estimate and len(credits) > 0:
            print_credit_estimate_summary(credits)

    else:
        typer.secho("\n  No changes detected.", fg="red")

    typer.secho("\nLink:", fg="magenta")
    push_id = name.split("/")[-1]
    endpoint = get_endpoint()

    if environment_id not in ("prod", "production"):
        typer.secho(
            f"  {endpoint}/projects/{project_id}@{environment_id}/changes/{push_id}\n",
            fg="blue",
        )
    else:
        typer.secho(
            f"  {endpoint}/projects/{project_id}/changes/{push_id}\n",
            fg="blue",
        )


def get_model_credit_estimate(model, project=None, environment=None, n=100):
    project, environment = get_project_and_environment(project, environment)
    c = Client(project=get_environment_name(project, environment))
    credits = "N/A"

    # get last successful mv. This should usually be latest_model_version, but there are cases where this won't happen.
    try:
        m = c.models.get(model)
        mv = c.model_versions.get(m.latest_model_version)
        if mv.state.value != "SUCCEEDED":
            # get last successful model version, resources are returned in reverse order, so take last one
            mv = m.model_versions.list(1000, filters=["state:SUCCEEDED"])[-1]
        credits = mv.credits_used
        if credits == 0:
            credits = "N/A"
    except:  # if we erorr out just return "N/A"
        pass

    return credits


def get_batch_prediction_credit_estimate(model, project=None, environment=None):
    project, environment = get_project_and_environment(project, environment)
    c = Client(project=get_environment_name(project, environment))
    credits = "N/A"

    # get last successful bpj. This should usually be latest_batch_prediction, but there are cases where this won't happen.
    try:
        m = c.models.get(model)
        bpj = c.batch_prediction_jobs.get(m.latest_batch_prediction)
        if bpj.state.value != "SUCCEEDED":
            # get last successful prediction, resources are returned in reverse order, so take last one
            bpj = m.batch_prediction_jobs.list(1000, filters=["state:SUCCEEDED"])[-1]
        credits = bpj.credits_used
        if credits == 0:
            credits = "N/A"
    except:  # if we hit an error, just return "N/A"
        pass

    return credits


def print_credit_estimate_summary(credits):
    estimates = {k: v for (k, v) in credits.items() if v != "N/A"}
    total_credit_usage = sum(estimates.values())
    if total_credit_usage == 0:
        total_credit_usage = "N/A"
    typer.secho(
        "\nTotal estimated credits to be used: %s " % total_credit_usage,
        fg="magenta",
    )
    typer.secho(
        f"\n  {'Resource':40s}{'Operation':20s}{'Estimated Credits':20s}",
        fg="magenta",
    )
    for operation, estimate in credits.items():
        [res, op] = operation.split(" ")
        typer.secho(f"  {res:40s}{op:20s}{estimate}", fg="white")

    if total_credit_usage == "N/A":
        typer.secho(
            f"\n  Unable to find any previous credit usage for affected reources. \n  You must train a model or run a batch prediction before estimates can be made.",
            fg="magenta",
        )


# print a push plan
def print_change_plan(push, project, environment):

    typer.secho(
        "Operations for %s in project %s, environment %s:"
        % (push.id, project, environment),
        fg="magenta",
    )
    typer.secho("\t" + push.message)
    if len(push.plan) > 0:
        steps = sorted(
            push.plan,
            key=lambda x: int(x.id),
            reverse=False,
        )
        typer.secho(
            f"\n  {'Operation':20s}{'State':20s}{'Duration(s)':12s}{'Start Time':30s}{'End Time':30s}",
            fg="magenta",
        )
        old_resource = ""
        featuresets = []
        models = []
        for step in steps:
            if step.resource_name.split("/")[2] == "models":
                models.append(step)
            else:
                featuresets.append(step)
        for step in featuresets + models:
            step_id = step.resource_name.split("/")[-1]
            if step.resource_name.split("/")[2] == "models":
                step_type = "Model"
            else:
                step_type = "Feature Set"
            start_time = step.start_time
            end_time = step.finish_time
            if start_time:
                start_time = step.start_time.replace(microsecond=0)
                if end_time:
                    end_time = end_time.replace(microsecond=0)
                    duration = (end_time - start_time).seconds
                else:
                    end_time = "N/A"
                    duration = "N/A"
            else:
                start_time = "N/A"
                end_time = "N/A"
                duration = "N/A"
            if not (old_resource == step_id):
                typer.secho("\n  %s: %s" % (step_type, step_id), fg="blue")
                old_resource = step_id
            typer.echo(
                f"  {step.operation:20s}{step.state:20s}{str(duration):12s}{str(start_time):30s}{str(end_time):30s}"
            )
    else:
        typer.secho("\n  No changes found.", fg="red")


def get_message(message, default):
    if not message:
        message = default
    if not message:
        try:
            repo = Repo(search_parent_directories=True)
            message = repo.git.log(n=1, oneline=True)
            if repo.is_dirty():
                message = message.split(" ")
                message[0] = message[0] + "+dirty"
                message = " ".join(message)
        except Exception:
            pass
    return message


def get_datastore_database_and_schema(data_store):
    fs_type = data_store.type

    if fs_type == "bigquery":
        db_schema = data_store.__getattribute__("big_query").dataset
        database = ""
    if fs_type == "databricks":
        db_schema = ""
        database = data_store.__getattribute__(fs_type).database
    else:
        db_schema = data_store.__getattribute__(fs_type).db_schema
        database = data_store.__getattribute__(fs_type).database

    return (db_schema, database)
