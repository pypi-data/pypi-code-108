import click
import xnat

from .utils import unpack_context

from .download import download
from .importing import importing
from .listings import listings
from .search import search
from .rest import rest
from .scripts import script
from .prearchive import prearchive


@click.group()
@click.version_option()
@click.option('--jsession', envvar='XNATPY_JSESSION', help="JSESSION value")
@click.option('--user', '-u', help="Username to connect to XNAT with.")
@click.option('--host', '-h', envvar='XNATPY_HOST', help="XNAT host to connect to.")
@click.option('--netrc', '-n', help=".netrc file location.")
@click.option('--loglevel', envvar='XNATPY_LOGLEVEL', help="Logging verbosity level.")
@click.option('--output-format', envvar='XNATPY_OUTPUT', type=click.Choice(['raw', 'csv', 'human'], case_sensitive=False), help="Output format", default='human')
@click.option('--timeout', envvar="XNATPY_TIMEOUT", type=float, help="Timeout for the command in ms.")
@click.pass_context
def cli(ctx, host, jsession, user, netrc, loglevel, output_format, timeout):
    ctx.ensure_object(dict)
    ctx.obj['host'] = host
    ctx.obj['jsession'] = jsession
    ctx.obj['user'] = user
    ctx.obj['netrc'] = netrc
    ctx.obj['loglevel'] = loglevel
    ctx.obj['output_format'] = output_format
    ctx.obj['timeout'] = timeout


cli.add_command(download)
cli.add_command(listings)
cli.add_command(importing)
cli.add_command(search)
cli.add_command(rest)
cli.add_command(script)
cli.add_command(prearchive)


@cli.command()
@click.pass_context
def login(ctx):
    """
    Establish a connection to XNAT and print the JSESSIONID so it can be used in sequent calls.
    The session is purposefully not closed so will live for next commands to use until it will
    time-out.
    """
    ctx = unpack_context(ctx)
    with xnat.connect(ctx.host, user=ctx.user, netrc_file=ctx.netrc, cli=True, no_parse_model=True, loglevel=ctx.loglevel) as session:
        click.echo(session.jsession)


@cli.command()
@click.pass_context
def logout(ctx):
    """
    Close your current connection to XNAT.
    """
    ctx = unpack_context(ctx)
    with xnat.connect(ctx.host, user=ctx.user, netrc_file=ctx.netrc, jsession=ctx.jsession,
                      no_parse_model=True, loglevel=ctx.loglevel) as session:
        pass
    click.echo('Disconnected from {host}!'.format(host=ctx.host))


if __name__ == '__main__':
    cli()