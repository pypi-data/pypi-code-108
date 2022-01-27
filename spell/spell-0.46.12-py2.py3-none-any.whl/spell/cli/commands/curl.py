import click
import os


@click.command(
    name="curl",
    short_help="Interact directly with the Spell API via `curl`",
    context_settings=dict(ignore_unknown_options=True),
)
@click.argument("args", nargs=-1)
@click.pass_context
def curl(ctx, args):
    """
    Interact directly with the Spell API via `curl`.

    Spell automatically adds Authentication and Content-Type headers.
    URL path arguments are prependend with the API protocol and host.
    Other arguments are passed to `curl` as-is.

    Example: spell curl /v1/users/me
    """
    client = ctx.obj["client"]

    # Prepend API base URL to absolute path without host
    args = [client.base_url + arg if arg.startswith("/v1") else arg for arg in args]

    header_args = [
        "--header",
        f"Authorization: Bearer {client.token}",
        "--header",
        "Content-Type: application/json",
    ]
    admin_token = getattr(client, "spell_admin_token", None)
    cookie_args = ["--cookie", f"SpellAdminAuthorization={admin_token}"] if admin_token else []

    os.execvp(
        "curl",
        [
            "curl",
            *header_args,
            *cookie_args,
            *args,
        ],
    )
