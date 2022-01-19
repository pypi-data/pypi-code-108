"""
    lager.pip.commands

    Commands for running  pip in lager python container
"""
import sys
import click
from ..context import get_default_gateway
from ..util import (
    stream_python_output,
    FAILED_TO_RETRIEVE_EXIT_CODE,
    SIGTERM_EXIT_CODE,
    SIGKILL_EXIT_CODE,
    StreamDatatypes,
)
from ..exceptions import OutputFormatNotSupported

def _do_exit(exit_code):
    if exit_code == FAILED_TO_RETRIEVE_EXIT_CODE:
        click.secho('Failed to retrieve script exit code.', fg='red', err=True)
    elif exit_code == SIGTERM_EXIT_CODE:
        click.secho('Gateway script terminated due to timeout.', fg='red', err=True)
    elif exit_code == SIGKILL_EXIT_CODE:
        click.secho('Gateway script forcibly killed due to timeout.', fg='red', err=True)

    sys.exit(exit_code)

@click.command(context_settings={"ignore_unknown_options": True})
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected')
@click.argument('args', nargs=-1)
def pip(ctx, gateway, args):
    """
        Run pip in the lager python container
    """
    session = ctx.obj.session
    if gateway is None:
        gateway = get_default_gateway(ctx)

    resp = session.run_pip(gateway, args)
    try:
        for (datatype, content) in stream_python_output(resp):
            if datatype == StreamDatatypes.EXIT:
                _do_exit(content)
            elif datatype == StreamDatatypes.STDOUT:
                click.echo(content, nl=False)
            elif datatype == StreamDatatypes.STDERR:
                click.echo(content, nl=False, err=True)
            elif datatype == StreamDatatypes.OUTPUT:
                click.echo(content)
    except OutputFormatNotSupported:
        click.secho('Response format not supported. Please upgrade lager-cli', fg='red', err=True)
        sys.exit(1)
