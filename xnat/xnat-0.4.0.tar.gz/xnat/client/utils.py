import click

from collections import namedtuple

CLIContext = namedtuple('CLIContext', 'host user netrc jsession loglevel output_format timeout')


def unpack_context(ctx, require_host=True):
    if require_host and (ctx.obj['host'] is None):
        click.echo("Missing required option '--host' / 'h'.")
        exit(1)
    return CLIContext(ctx.obj['host'], ctx.obj['user'], ctx.obj['netrc'], ctx.obj['jsession'], ctx.obj['loglevel'], ctx.obj['output_format'], ctx.obj['timeout'])