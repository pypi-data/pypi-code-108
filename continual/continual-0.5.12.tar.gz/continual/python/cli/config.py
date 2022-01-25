import typer
import os
from pathlib import Path

from continual.python.cli import utils
from continual import Client


app = typer.Typer(help="Manage CLI configuration.")

# use callback to run list command if nothing is passed in
@app.callback(invoke_without_command=True)
def default(ctx: typer.Context):
    if ctx.invoked_subcommand is not None:
        return
    else:
        show()


@app.command("init")
@utils.exit_on_error
def continual_init(
    project: str = typer.Option(..., help="Project ID."),
    environment: str = typer.Option(None, help="Environment Id"),
    style: utils.ContinualStyle = typer.Option(None, help="Display style."),
):
    """Set default project.

    Sets the default project for the SDK and CLI.  All future commands
    will use the default project if no project is explicitly passed. You may
    set the project and environment at the same time via project@environment.
    """
    try:
        config = Client().config
        Path(os.path.join(os.getcwd(), ".continual.yaml")).touch(exist_ok=True)
        c = Client()
        c.config.email = config.email
        c.config.endpoint = config.endpoint
        c.config.api_key = config.api_key
        c.config.save()
        set_project(project=project, print=False)
        if environment:
            set_environment(environment=environment, print=False)
        else:
            c.config.environment = config.environment
        if style:
            set_style(style=style, print=False)
        else:
            c.config.style = config.style
        c.config.show()
    except:
        typer.secho(
            "Project %s does not exist. Please create the project first!" % project,
            fg="red",
        )


@app.command("set-project")
@utils.exit_on_error
def set_project(
    project: str = typer.Argument(..., help="Project ID."),
    print: bool = typer.Option(True, help="Print config after modification."),
):
    """Set default project.

    Sets the default project for the SDK and CLI.  All future commands
    will use the default project if no project is explicitly passed. You may
    set the project and environment at the same time via project@environment.
    """
    try:
        c = Client(project=project)
        if project == "":
            project = None
        if project is not None and "/" not in project:
            project = "projects/" + project
        if "@" in project:
            environment = project.split("@")[1]
            c.config.environment = environment
            project = project.split("@")[0]
        c.projects.get(project)
        c.config.project = project
        c.config.save()
        if print:
            c.config.show()
    except:
        typer.secho(
            "Project %s does not exist. Please create the project first!" % project,
            fg="red",
        )


@app.command("set-endpoint")
@utils.exit_on_error
def set_endpoint(
    endpoint: str = typer.Argument(..., help="Continual environment endpoint"),
    print: bool = typer.Option(True, help="Print config after modification."),
):
    """Set default endpoint"""
    c = Client()
    old_endpoint = c.config.endpoint
    c.config.endpoint = endpoint
    c.config.save()

    # Reload client to check endpoint validity
    try:
        c = Client()
        typer.secho(f"Sucessfully set endpoint to {endpoint}", fg="green")
        if print:
            c.config.show()
    except ValueError as e:
        c.config.endpoint = old_endpoint
        c.config.save()
        typer.secho("Endpoint %s is not valid : %s" % (endpoint, e), fg="red")


@app.command("set-environment")
@utils.exit_on_error
def set_environment(
    environment: str = typer.Argument(..., help="Environment ID."),
    print: bool = typer.Option(True, help="Print config after modification."),
):
    """Set default environment.

    Sets the default environment for the SDK and CLI.  All future commands
    will use the default environment if no environment is explicitly passed.
    """
    try:
        c = Client()
        if environment == "":
            environment = None
        if environment and "@" in environment:
            environment = environment.split("@")[-1]
        c.environments.get(environment)
        c.config.environment = environment
        c.config.save()
        if print:
            c.config.show()
    except:
        typer.secho(
            "Environment %s does not exist. Please create the enviornment first!"
            % environment,
            fg="red",
        )


@app.command("set-style")
@utils.exit_on_error
def set_style(
    style: utils.ContinualStyle = typer.Argument(..., help="Display style."),
    print: bool = typer.Option(True, help="Print config after modification."),
):
    """Set default CLI display style."""
    c = Client()
    c.config.style = style.value
    c.config.save()
    if print:
        c.config.show()


@app.command("show")
@utils.exit_on_error
def show():
    """Show current config.

    Shows the current session configuration stored in
    ~/.continual/continual.yaml."
    """
    c = Client()
    c.config.show()
