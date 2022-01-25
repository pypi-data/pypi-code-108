# -*- encoding: utf-8 -*-
'''cli_clslq_pip

Usage: clslq pip [OPTIONS]

  The wrapper for pip, use local pypi as default.

Options:
  -t, --trusted-host TEXT  The trusted mirror host, default:
                           tuna mirror.
  -i, --pypi TEXT          The pypi mirror url, default use:
                           https://pypi.org/
  -h, --help               Show this message and exit.

'''



import click
import platform
import os

from clspy.utils import pipguess


@click.option(
    '--pypi',
    '-i',
    default='https://pypi.org/',
    help='The pypi mirror url, default use: https://pypi.org/')
@click.option('--trusted-host',
              '-t',
              default='gw.lovelacelee.com',
              help='The trusted mirror host, default: gw.lovelacelee.com.')
@click.command(context_settings=dict(
    allow_extra_args=True,
    ignore_unknown_options=True,
),
               help="The wrapper for pip, use local pypi as default.")
@click.pass_context
def pip(ctx, pypi, trusted_host):
    """Wrapper of pip

    Supported commands:
    ```
    # upgrade pip first
    # python -m pip uninstall pip -y
    # python -m ensurepip
    # python -m pip install -U pip
    # os.system(pipguess()+'install --upgrade pip')
    ```

    Args:
        pypi (<str>): Available pypi mirror url
        trusted_host (<str>): pypi mirror domain
    """
    #click.echo(ctx.args)
    _cmdline = pipguess()
    _change_pypi_cmds = ['install', 'download', 'list', 'search']
    _change_pypi = False
    for i in ctx.args:
        _cmdline += ' ' + i + ' '
        if i in _change_pypi_cmds:
            _change_pypi = True
    if _change_pypi:
        _cmdline += ' -i ' + pypi
        _cmdline += ' --trusted-host ' + trusted_host
    click.echo(_cmdline)
    click.echo('=W=H=A=T=R=E=T=U=R=N=E=D=B=Y=P=I=P=')
    os.system(_cmdline)
