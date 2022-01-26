#!/usr/bin/env python
import json
import os
import re
import socketserver
import subprocess
import sys
import tempfile
from http.server import SimpleHTTPRequestHandler

import click
from cookiecutter.main import cookiecutter

from . import __version__
from .auth import (AUTH_ACTIONS, AUTH_ACTIONS_GET_TOKEN, AUTH_ACTIONS_LOGIN,
                   AUTH_ACTIONS_LOGOUT, ArchimedesAuth)
from .config import CONFIG_FILE_NAME, SAVED_CONFIG_PATH, environment

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
COOKIECUTTER_TEMPLATE_GIT_URL = "https://github.com/OptimeeringAS/archimedes-cookiecutter.git"


class ConfigNotFoundException(Exception):
    pass


def get_author_name(user):
    name = user.get("name")
    email = user.get("email")
    username = user.get("username")

    for author_name in [name, email]:
        if author_name:
            return author_name

    return username


def get_python_version():
    version_output = subprocess.run(["python3", "--version"], stdout=subprocess.PIPE)
    return re.search(r"(\d+\.\d+.\d+)", version_output.stdout.decode("utf-8")).group(1)


def get_config(project_name):
    """Create a config for the project"""
    if not os.path.exists(SAVED_CONFIG_PATH):
        raise ConfigNotFoundException(
            "User not logged in. Please log in using `arcl auth login <organization_id>`."
        )

    config = json.loads(open(SAVED_CONFIG_PATH, "r").read())

    return {
        "project_name": project_name,
        "author_name": get_author_name(config["user"]),
        "postgres_user": config["db"]["postgres_user"],
        "postgres_pass": config["db"]["postgres_pass"],
        "postgres_host": config["db"]["postgres_host"],
        "postgres_port": config["db"]["postgres_port"],
        "postgres_dbname": config["db"]["postgres_dbname"],
        "server_name": config["server_name"],
        "docker_registry": config["docker_registry"],
        "prefect_server_endpoint": config["prefect"]["server_endpoint"],
        "prefect_api_server": config["prefect"]["api_server"],
        "mlflow_tracking_url": config["mlflow"]["tracking_url"],
        "aws_access_key_id": config["mlflow"]["artifacts_aws_access_key_id"],
        "aws_secret_access_key": config["mlflow"]["artifacts_aws_secret_access_key"],
        "s3_endpoint_url": config["mlflow"]["artifacts_s3_endpoint_url"],
        "environment": environment,
        "python_version": get_python_version(),
    }


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """
    Welcome to The Archimedes CLI.

    \b
    Commands:
        arcl new         Create a new project
        arcl docs        Show the docs
        arcl auth        Handle Archimedes authentication
        arcl version     Print the version number
        arcl config      Print the current configuration
        arcl status      Get status of the current directory
    """
    pass


@cli.command(hidden=True)
@click.argument("action", type=click.Choice(AUTH_ACTIONS, case_sensitive=False), required=True)
@click.argument("organization", required=False)
def auth(action, organization):
    archimedes_auth = ArchimedesAuth()

    if action.lower() == AUTH_ACTIONS_LOGOUT:
        archimedes_auth.logout()
        return

    if action.lower() == AUTH_ACTIONS_LOGIN and not organization:
        raise click.BadParameter("Error: Must specify organization to login to")

    if action.lower() == AUTH_ACTIONS_LOGIN:
        archimedes_auth.login(organization)
        return

    if action.lower() == AUTH_ACTIONS_GET_TOKEN:
        click.echo(archimedes_auth.get_access_token())


# remove the examples flag
# create /production/sample.py instead from the other repo
# deploy basic version of price/load prediction
# does adding more PriceAreas increase the precision?
@cli.command(hidden=True)
@click.argument("name", required=True)
# @click.option(
#     "--examples",
#     is_flag=True,
#     help="Add this flag to include example files",
# )
# def new(name, examples):
@click.option(
    "--template-version",
    "-t",
    "template_version",
    help=f"Version of the template to use. It can be a branch, name or tag of the git repo of"
         f"{COOKIECUTTER_TEMPLATE_GIT_URL}",
    default=None,
)
def new(name, template_version):
    """"""
    # if examples == True:
    #     examples_ = "yes"
    # else:
    #     examples_ = "no"

    try:
        project_dir = cookiecutter(
            COOKIECUTTER_TEMPLATE_GIT_URL,
            checkout=template_version,
            extra_context=get_config(name),
            no_input=True,
        )
    except ConfigNotFoundException as e:
        click.echo(e)
        return

    # if examples:
    if False:
        click.echo(f"\nYour new project (and example files) has been created!")
    else:
        click.echo(f"\nYour new project has been created!")
    click.echo("")
    click.echo(f'$ cd "{project_dir}"')
    click.echo(f"$ arcl status")
    click.echo("")
    click.echo(f"to view more information.")
    click.echo("")
    click.echo(f'$ cd "{project_dir}"')
    click.echo(f"$ python -m pip install wheel pip --upgrade")
    click.echo(f"$ poetry update --lock")
    click.echo(f"$ poetry install")
    click.echo("")
    click.echo(f"to get started.")
    click.echo("")


@cli.command(hidden=True)
@click.option(
    "--template-version",
    "-t",
    "template_version",
    help=f"Version of the template to use. It can be a branch, name or tag of the git repo of"
         f"{COOKIECUTTER_TEMPLATE_GIT_URL}",
    default=None,
)
def init(template_version):
    """
    Initialize Archimedes in an existing directory
    """
    if CONFIG_FILE_NAME in os.listdir("."):
        click.echo(f"Project already initialized. Found existing {CONFIG_FILE_NAME}.")
        return
    click.echo("Please type the name of your project:")
    project_name = click.prompt("Project name")
    project_directory = os.getcwd()

    try:
        config = get_config(project_name)
    except ConfigNotFoundException as e:
        click.echo(e)
        return

    # Create a temporary project from cookiecutter and copy archimedes.toml from it to the current project directory
    with tempfile.TemporaryDirectory(dir=".") as tmp_dir_name:
        temporary_project_directory = cookiecutter(
            COOKIECUTTER_TEMPLATE_GIT_URL,
            checkout=template_version,
            extra_context=config,
            no_input=True,
            output_dir=tmp_dir_name,
        )
        os.rename(
            os.path.join(temporary_project_directory, CONFIG_FILE_NAME),
            os.path.join(project_directory, CONFIG_FILE_NAME),
        )

    click.echo(f"The project `{project_name}` was initialized!")


@cli.command(hidden=True)
def version():
    """
    Print the current version
    """
    click.echo(__version__)


@cli.command(hidden=True)
def status():
    """
    Get the status of the current project
    """
    # Check deployment
    if CONFIG_FILE_NAME in os.listdir("."):
        click.echo("Status: OK")
    else:
        click.echo("Missing Archimedes config file, try `arcl init`")


# Docs request handler, serving path ./docs
class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        docs_path = os.path.abspath((os.path.join(os.path.dirname(__file__), "docs")))
        super().__init__(*args, directory=docs_path, **kwargs)


@cli.command(hidden=True)
def docs():
    """
    Start local documentation server
    """
    try:
        httpd = socketserver.TCPServer(("", 0), Handler)
        port = httpd.server_address[1]
        print(f"Serving docs at: http://localhost:{port}")
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()
        httpd.server_close()
        print(f"Shutdown server: http://localhost:{port}")
        sys.exit(0)


if __name__ == "__main__":
    cli()
