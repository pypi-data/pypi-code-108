import click

from spell.cli.utils import (
    tabulate_rows,
    command,
    prettify_time,
    convert_to_local_time,
    echo_raw,
)
from spell.cli.exceptions import api_client_exception_handler


@click.group(
    name="access-tokens",
    short_help="Manage access tokens",
    help="Create, List, and Revoke user access tokens. This is often helpful for customers using the python API",
)
@click.pass_context
def access_tokens(ctx):
    pass


@command(
    name="list",
    short_help="Lists all access tokens for the current user.",
    help="""Lists all of the active access tokens for the logged in user.
    NOTE: The Token itself will only be available during creation. If lost, delete the
    access token and create a new one.""",
)
@click.option("--raw", is_flag=True, help="Display output in raw format", hidden=True)
@click.pass_context
def list_access_tokens(ctx, raw):
    client = ctx.obj["client"]

    with api_client_exception_handler():
        access_tokens = client.list_access_tokens()

    if len(access_tokens) == 0:
        if not raw:
            click.echo("No access tokens found. Use `spell access-tokens create` to create one.")
        return

    for cs in access_tokens:
        cs.created_at = prettify_time(cs.created_at)
        if cs.last_used_at is None:
            cs.last_used_at = "<unused>"
        else:
            cs.last_used_at = prettify_time(cs.last_used_at)
    tabulate_rows(
        access_tokens,
        headers=["name", "created at", "last used at"],
        columns=["name", "created_at", "last_used_at"],
        raw=raw,
    )


@command(
    name="create",
    short_help="Creates a new access token with the given name and returns the new auth token",
    help="""Creates a new access token with the given name and returns the new auth token.
    NOTE: This auth token CANNOT BE RETRIEVED after this, so keep it secret, keep it safe!""",
)
@click.argument("name")
@click.option("--raw", is_flag=True, help="Display output in raw format", hidden=True)
@click.pass_context
def create_access_token(ctx, name, raw):
    client = ctx.obj["client"]

    with api_client_exception_handler():
        access_token = client.create_access_token(name)
    if raw:
        echo_raw([[access_token["token"]]])
        return
    local_time = convert_to_local_time(access_token["created_at"], include_seconds=False)
    click.echo(f"New Access Token '{name}' created on {local_time}")
    click.echo(f"Token is: {access_token['token']}")
    click.echo("NOTE: this token is not recoverable, so save it somewhere safe.")


@command(
    name="delete",
    short_help="Deletes an access token with the given name",
    help="Deletes an access token with the given name",
)
@click.argument("name")
@click.pass_context
def delete_access_token(ctx, name):
    client = ctx.obj["client"]

    with api_client_exception_handler():
        client.delete_access_token(name)
    click.echo(f"Access token '{name}' successfully deleted")


access_tokens.add_command(list_access_tokens)
access_tokens.add_command(create_access_token)
access_tokens.add_command(delete_access_token)
