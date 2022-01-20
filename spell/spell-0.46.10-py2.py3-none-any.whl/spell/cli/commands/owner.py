import click

from spell import deployment_constants
from spell.cli.exceptions import api_client_exception_handler, ExitException


@click.command(name="owner")
@click.argument("name", required=False)
@click.pass_context
def owner(ctx, name):
    """
    Command which both displays and allows for the selection of the current active owner,
    where an owner is defined as the scope for all Spell resources and actions.
    For example, a user's owners might include their team organization and their
    personal community account.

    Omitting the optional argument NAME will list out all available owners for the current user.

    Providing the optional argument NAME will update the current active owner to the provided one.
    """
    # Owner the CLI is currently configured to use
    current_owner = ctx.obj["owner"]

    # Generate the list of possible owners for the user
    with api_client_exception_handler():
        user = ctx.obj["client"].get_user_info()
    possible_owners = []
    if not deployment_constants.on_prem:
        # Community users don't exist in ONPREM
        possible_owners.append(user.user_name)
    if user.memberships:
        possible_owners.extend([m.organization.name for m in user.memberships])

    # Configure CLI to use a different owner
    if name and name != current_owner:
        if name not in possible_owners and not user.is_admin:
            raise ExitException("Invalid owner name: " + name)
        config_handler = ctx.obj["config_handler"]
        current_owner = ctx.obj["owner"] = config_handler.config.owner = name
        config_handler.write()

    prefix = "➔ " if ctx.obj["utf8"] else "* "

    # Specially display impersonated owner if user is impersonating
    if user.is_admin and current_owner not in possible_owners:
        click.echo(prefix + click.style(f"{current_owner} (impersonating)", fg="red"))

    # Display list of owners with the current one highlighted
    for owner in possible_owners:
        if owner == current_owner:
            click.echo(prefix + click.style(owner, fg="green"))
        else:
            click.echo("  " + owner)
