"""
    lager.debug.commands

    Debug an elf file
"""
import click
from ..context import get_default_gateway
from ..debug.gdb import debug


@click.group(name='debug')
def _debug():
    """
        Lager gateway commands
    """
    pass

@_debug.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected')
@click.option('--interpreter', '-i', required=False, default='default', help='Select a specific interpreter / user interface')
@click.option('--verbose', '-v', is_flag=True, default=False, help='Print verbose debug info')
@click.option('--tty', required=False, help='Use TTY for input/output by the program being debugged.')
@click.option('--quiet', '--silent', '-q', is_flag=True, default=False, help='Do not print the introductory and copyright messages. These messages are also suppressed in batch mode.')
@click.option('--args', required=False, help='Arguments passed to debugger')
@click.option('--ignore-missing/--no-ignore-missing', is_flag=True, default=False, help='Ignore missing files')
@click.option('--cwd', default=None, type=click.Path(exists=True, file_okay=False, resolve_path=True), help='Set current working directory')
@click.option('--cache/--no-cache', default=True, is_flag=True, help='Use cached source if ELF file unchanged', show_default=True)
@click.argument('elf_file', type=click.Path())
def gdb(ctx, gateway, interpreter, verbose, tty, quiet, args, ignore_missing, cwd, cache, elf_file):
    """
        Debug a DUT using an ELF file
    """
    debug(ctx, gateway, interpreter, verbose, tty, quiet, args, ignore_missing, cwd, cache, elf_file)


@_debug.command()
@click.pass_context
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False, help='MCU to connect')
def connect(ctx, dut, mcu):
    if dut is None:
        dut = get_default_gateway(ctx)
    session = ctx.obj.session
    resp = session.debug_connect(dut, mcu).json()
    if resp.get('start') == 'ok':
        click.secho('Connected!', fg='green')
    elif resp.get('already_running') == 'ok':
        click.secho('Debugger already connected, ignoring', fg='green')
