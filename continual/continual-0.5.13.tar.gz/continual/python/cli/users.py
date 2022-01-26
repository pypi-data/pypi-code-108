import typer
from continual import continual as c
from pprint import pprint
from continual.python.cli import utils

app = typer.Typer(help="Manage users.")

# use callback to run list command if nothing is passed in
@app.callback(invoke_without_command=True)
def default(ctx: typer.Context):
    if ctx.invoked_subcommand is not None:
        return
    else:
        list(n=30)


@app.command("list")
@utils.exit_on_error
def list(
    n: int = typer.Option(30, "--num", "-n", help="Number of records to show."),
):
    """List users."""
    print("ID - Name")
    for user in c.users.list_all():
        typer.echo("%s - %s %s" % (user.id, user.first_name, user.last_name))


@app.command("get")
@utils.exit_on_error
def get(
    user_id: str = typer.Argument(..., help="User ID."),
    json: bool = typer.Option(False, "--json", help="Print full details."),
):
    """Get user details."""
    user = c.users.get(user_id)
    if json:
        pprint(user.to_dict())
    else:
        typer.echo("ID: %s" % user.id)
        typer.echo("Name: %s %s" % (user.first_name, user.last_name))
        typer.echo("Email: %s" % user.email)
        typer.echo("Created: %s" % user.create_time)
        typer.echo("Updated: %s" % user.update_time)


@app.command("register")
@utils.exit_on_error
def register(
    first_name: str = typer.Argument(..., help="First name.", show_default=False),
    last_name: str = typer.Argument("", help="Last name.", show_default=False),
    email: str = typer.Option(
        ..., help="Email address.", prompt=True, show_default=False
    ),
    password: str = typer.Option(
        ..., help="Password.", prompt=True, hide_input=True, show_default=False
    ),
):
    """Create user."""
    user = c.register(first_name, last_name, email, password)
    print("Created user %s %s with id %s." % (first_name, last_name, user.id))


@app.command("delete")
@utils.exit_on_error
def delete(
    user_id: str = typer.Argument(..., help="User ID."),
):
    """Delete user."""
    try:
        user = c.users.get(user_id)
        user.delete()
        typer.echo("Successfully deleted user %s." % user_id)
    except Exception as e:
        typer.echo("Failed to deleted user %s: %s" % (user_id, str(e)))


@app.command("update")
@utils.exit_on_error
def update(
    user_id: str = typer.Argument(..., help="User ID."),
    first_name: str = typer.Option(..., help="First name."),
    last_name: str = typer.Option(..., help="Last name."),
):
    """Update Project Name"""
    try:
        user = c.users.get(user_id)
        user.update(first_name, last_name)
        typer.echo("Successfully updated user %s." % user_id)
    except Exception as e:
        typer.echo("Failed to update user %s: %s" % (user_id, str(e)))
