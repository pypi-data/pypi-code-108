import click

from spell.cli.exceptions import api_client_exception_handler
from spell.cli.utils.command import docs_option


@click.command(name="unlink", short_help="Remove a link.")
@click.argument("alias", required=True)
@docs_option("https://spell.ml/docs/resources/#advanced-deleting-resource-links")
@click.pass_context
def unlink(ctx, alias):
    """
    Remove an existing symlink by referencing a particular link alias.
    """
    client = ctx.obj["client"]
    with api_client_exception_handler():
        client.remove_link(alias)
    click.echo("Successfully removed link with alias {}.".format(alias))
