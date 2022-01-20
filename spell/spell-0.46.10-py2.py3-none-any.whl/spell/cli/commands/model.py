import click

from spell.cli.exceptions import api_client_exception_handler, ExitException
from spell.cli.utils import (
    convert_to_local_time,
    format_multiline_table_output,
    prettify_time,
    tabulate_rows,
)
from spell.cli.utils.command import docs_option, group
from spell.shared.parse_utils import get_name_and_tag


@group(
    name="model",
    short_help="Manage Spell models",
    help="""Spell models are a way for you to track your progress as you work on training models.
    As you run new training runs you can push those outputs to existing model names, and we will
    track those over time for you or create new models. You can take any model version and serve it.""",
)
@docs_option("https://spell.ml/docs/model_servers/#core-concepts")
@click.pass_context
def model(ctx):
    pass


@model.command(name="list", help="List all existing models")
@docs_option("https://spell.ml/docs/model_servers/#listing-models")
@click.pass_context
def list_models(ctx):
    client = ctx.obj["client"]
    with api_client_exception_handler():
        models = client.list_models(ctx.obj["owner"])
        print_models_list(models)


def format_model_file(filepath):
    if filepath.destination_path == filepath.resource_path:
        return filepath.resource_path
    else:
        return f"{filepath.resource_path}:{filepath.destination_path}"


def print_model_versions_list(model):
    def create_row(v):
        formatted_files = [""]
        if len(v.files) != 1 or v.files[0].resource_path != ".":
            formatted_files = [format_model_file(f) for f in v.files]
        return (
            v.formatted_version,
            v.resource,
            ", ".join(formatted_files),
            prettify_time(v.created_at),
            v.creator.user_name,
        )

    tabulate_rows(
        [create_row(v) for v in model.model_versions],
        headers=["VERSION", "RESOURCE", "FILES", "CREATED", "CREATOR"],
    )


def print_models_list(models):
    def create_row(m):
        latest_version = max(m.model_versions, key=lambda x: x.created_at)
        return (
            m.name,
            latest_version.formatted_version,
            prettify_time(m.created_at),
            m.creator.user_name,
        )

    tabulate_rows([create_row(m) for m in models], headers=["NAME", "LATEST VERSION", "CREATED", "CREATOR"])


def print_model_version(model_name, version):
    lines = [
        ("Model", model_name),
        ("Version", version.formatted_version),
        ("Creator", version.creator.user_name),
        ("Resource", version.resource),
        ("Created At", convert_to_local_time(version.created_at)),
    ]
    lines.extend(format_multiline_table_output("Files", version.files, format_model_file))
    if version.description:
        lines.append(("Description", version.description))
    tabulate_rows(lines)


@model.command(short_help="Describe a model")
@click.argument("model", metavar="MODEL[:VERSION]")
@click.pass_context
def describe(ctx, model):
    """Describe a model or a model version"""
    client = ctx.obj["client"]
    model, version = parse_model_version_permissively(model)
    if not version:
        with api_client_exception_handler():
            model = client.get_model(ctx.obj["owner"], model)
            print_model_versions_list(model)
    else:
        with api_client_exception_handler():
            version = client.get_model_version(ctx.obj["owner"], model, version)
            print_model_version(model, version)


@model.command(
    name="create",
    short_help="Create a new model",
    help="""Specify a name for the model, if you use an existing model name a new version
    will be created for you, otherwise a new model will be created.

    If a version is specified in NAME:VERSION form, a model will be created with the given version
    name. If a version is omitted, it will be given an autoincremented integer version.

    Example creating a model from a run: 'spell model create runmodel runs/168'. Example creating a
    model from an upload: 'spell model create uploadmodel uploads/test'.
    """,
)
@click.pass_context
@click.argument("name", metavar="NAME[:VERSION]")
@click.argument("resource")
@click.option(
    "--file",
    "-f",
    "files",
    multiple=True,
    metavar="PATH WITHIN RESOURCE[:MOUNT PATH]",
    help="""If the run output contains unnecessary information (like intermediate checkpoint files),
    you can whitelist only the needed files with this flag. You can optionally specify a path for each to
    be mounted within a future model server as well. If you omit this we will just use
    '<MODEL NAME>/<PATH WITHIN RESOURCE>'""",
)
@click.option("--description", "-d", help="Description of the model")
@docs_option("https://spell.ml/docs/model_servers/#creating-models")
def create(ctx, name, resource, files, description):
    model, version = parse_model_version_permissively(name)
    client = ctx.obj["client"]
    with api_client_exception_handler():
        model = client.new_model(ctx.obj["owner"], model, resource, version, files, description)
    click.echo(f"Successfully created model: {model.model_name} {model.formatted_version}")


@model.command(
    name="rm",
    short_help="Deletes a model or model version",
    help="Marks a model version as deleted. If version is omitted the whole model is marked as deleted.",
)
@click.pass_context
@click.argument("name", metavar="NAME[:VERSION]")
@docs_option("https://spell.ml/docs/model_servers/#deleting-models")
def rm(ctx, name):
    model, version = parse_model_version_permissively(name)
    if not version:
        rm_model(ctx, model)
    else:
        rm_model_version(ctx, model, version)


def rm_model(ctx, name):
    if not click.confirm(
        "You didn't specify a version. This will delete all "
        f"versions of model {name}. Are you sure you want to proceed?"
    ):
        return

    client = ctx.obj["client"]
    with api_client_exception_handler():
        client.rm_model(ctx.obj["owner"], name)
    click.echo(f"Successfully deleted all versions of model {name}")


def rm_model_version(ctx, name, version):
    if not click.confirm(f"Are you sure you want to delete version {version} of model {name}?"):
        return

    client = ctx.obj["client"]
    with api_client_exception_handler():
        client.rm_model_version(ctx.obj["owner"], name, version)
    click.echo(f"Successfully deleted model {name} version {version}")


@model.command(name="update-description", short_help="Update a model's description")
@click.argument("model", metavar="MODEL:VERSION")
@click.argument("description")
@click.pass_context
def update(ctx, model, description):
    """Update a model's description"""
    model_name, model_version = get_name_and_tag(model)
    if model_version is None:
        raise ExitException("A model must be specified in the form model_name:version")
    client = ctx.obj["client"]
    with api_client_exception_handler():
        client.update_model_description(ctx.obj["owner"], model_name, model_version, description)
    click.echo(f"Successfully updated model: {model}")


@model.command(
    name="download",
    short_help="Downloads a model version to local disk",
)
@click.pass_context
@click.argument("name", metavar="NAME[:VERSION]")
@click.option("--dest", "-d", help="Directory to download to. Defaults to the current directory.", default="./")
def download(ctx, name, dest):
    model, version = parse_model_version_permissively(name)
    if not version:
        raise ExitException("A model must be specified in the form model_name:version. Version cannot be omitted.")
    client = ctx.obj["client"]

    with api_client_exception_handler():
        model_version = client.get_model_version(ctx.obj["owner"], model, version)

    click.echo("Downloading model. This may take some time...")

    with api_client_exception_handler():
        client.download_model_version(model_version, dest, click.echo, quiet=False)

    click.echo("Done!")


def parse_model_version_permissively(model):
    model, _, version = model.partition(":")
    if version == "":
        version = None
    return model, version
