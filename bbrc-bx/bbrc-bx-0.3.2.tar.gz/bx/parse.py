import os.path as op
import os
import tempfile
import argparse
import pkgutil
import inspect
import logging as log
from rich.console import Console
from rich.theme import Theme
t = Theme()
t.styles.pop('repr.number')
t.styles.pop('repr.str')
console = Console(theme=t)
print = console.print


def __get_modules__(m):
    modules = []
    prefix = m.__name__ + '.'
    log.info('prefix : %s' % prefix)
    for importer, modname, ispkg in pkgutil.iter_modules(m.__path__, prefix):
        module = __import__(modname, fromlist='dummy')
        if not ispkg:
            modules.append(module)
        else:
            modules.extend(__get_modules__(module))
    return modules


def __find_all_commands__(m):
    """Browses bx and looks for any class named as a Command"""
    modules = []
    classes = []
    modules = __get_modules__(m)
    forbidden_classes = []  # Test, ScanTest, ExperimentTest]
    for m in modules:
        for name, obj in inspect.getmembers(m):
            if inspect.isclass(obj) and 'Command' in name \
                    and obj not in forbidden_classes:
                classes.append(obj)
    return classes


class ReadableDir(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        prospective_dir = values
        if not os.path.isdir(prospective_dir):
            msg = "readable_dir:{0} is not a valid path".format(prospective_dir)
            raise argparse.ArgumentTypeError(msg)
        if os.access(prospective_dir, os.R_OK):
            setattr(namespace, self.dest, prospective_dir)
        else:
            msg = "readable_dir:{0} is not a readable dir".format(prospective_dir)
            raise argparse.ArgumentTypeError(msg)


def __stylize_help__(doc):
    ln = doc.split('\n')
    sep = ':\t'
    subcommands = [e.split(sep)[0].strip(' ') for e in ln if sep in e]
    msg = '[italic]%s[/italic]\n%s' % (ln[0], '\n'.join(ln[1:]))
    for e in subcommands:
        msg = msg.replace(' %s:' % e, ' [bold cyan]%s[/bold cyan]:' % e)
    i = ln.index([e for e in ln if 'Usage:' in e][0])
    msg = msg.replace(ln[i+1],
                      '[bright_white on black]%s[/bright_white on black]' % ln[i+1])
    return msg


def parse(parser, command):
    c = command(parser.command, parser.args, parser.xnat, parser.destdir)

    if len(c.args) == 0:
        msg = __stylize_help__(c.__doc__)
        cn = parser.command
        msg = '\n[bold]Help for command `[cyan]%s[/cyan]`:[/bold]'\
              '\n\n%s' % (cn, msg)
        print(msg)

    elif len(c.args) == command.nargs:
        if command.nargs == 1 or c.args[0] in command.subcommands:
            c.parse()
        else:
            subcommands = ['[bold cyan]%s[/bold cyan]' % e
                           for e in command.subcommands]
            subcommands = '\n - '.join(subcommands)
            args = (c.args[0], subcommands)
            msg = '\n`[yellow]%s[/yellow]` is an invalid subcommand.\n\nAvailable subcommands:\n - %s' % args
            print(msg)

    else:
        msg = '[yellow]%s[/yellow]' % c.__doc__
        cn = parser.command
        args = (cn, msg)
        msg = '\n[bold][red]ERROR[/red]: Missing argument(s)\n\nHelp for command `[blue]%s[/blue]`:[/bold]\n\n%s' % args
        print(msg)


def parse_args(command, args, x, destdir=tempfile.gettempdir()):
    from bx.command import Command
    parser = Command(command, args, x, destdir)

    import bx
    commands = __find_all_commands__(bx)
    commands = {e.__name__.split('.')[-1].lower()[:-7]: e for e in commands}

    if command in commands.keys():

        print('Command: %s' % command)
        if command == 'nifti' and len(args) == 1:
            args.insert(0, 'usable')
        elif command in ['freesurfer6', 'freesurfer']:
            ans = 3
            msg = 'Please confirm if you want FREESURFER6, ' \
                  'FREESURFER6_HIRES or FREESURFER7 or FREESURFER7_EXTRAS? '\
                  ' (1) FREESURFER6 (2) FREESURFER6_HIRES '\
                  '(3) FREESURFER7 (4) FREESURFER7_EXTRAS ?'
            if not os.environ.get('CI_TEST', None):
                while ans not in ['1', '2', '3', '4']:
                    ans = input(msg)
            options = ['freesurfer6', 'freesurfer6hires', 'freesurfer7',
                       'freesurfer7extras']
            parser = Command(options[int(ans) - 1], args, x, destdir)
        elif command in ['freesurfer7'] and len(args) > 1\
                and args[0] in ['files', 'report', 'snapshot']:
            ans = 1
            msg = 'Please confirm if you want FREESURFER7 or FREESURFER7_EXTRAS? '\
                  '(1) FREESURFER7 (2) FREESURFER7_EXTRAS ?'
            if not os.environ.get('CI_TEST', None):
                while ans not in ['1', '2']:
                    ans = input(msg)
            options = ['freesurfer7', 'freesurfer7extras']
            parser = Command(options[int(ans) - 1], args, x, destdir)
        elif command == 'spm12':
            ans = 3
            msg = 'Please confirm if you want SPM12_SEGMENT (T1-only)'\
                  ' or SPM12_SEGMENT_T1T2 (multimodal)? '\
                  ' (1) SPM12_SEGMENT (2) SPM12_SEGMENT_T1T2\n> '
            if not os.environ.get('CI_TEST', None):
                while ans not in ['1', '2']:
                    ans = input(msg)
                    rn, vn = 'SPM12_SEGMENT_T1T2', 'SPM12SegmentT1T2Validator'
                    if ans == '1':
                        rn, vn = 'SPM12_SEGMENT', 'SPM12SegmentValidator'
                    args.append((rn, vn))
            parser = Command('spm12', args, x, destdir)

        try:
            parse(parser, commands[command])
        except ValueError as ve:
            log.error(ve)

    else:
        valid = [e for e, v in commands.items() if e != '']
        args = (command, '\n '.join(valid))
        msg = '%s not found \n\nValid commands:\n %s' % args
        log.error(msg)


class AParser(argparse.ArgumentParser):
    def _print_message(self, message, file=None):
        if message:
            print(message)


def create_parser():
    import bx
    cfgfile = op.join(op.expanduser('~'), '.xnat.cfg')
    commands = __find_all_commands__(bx)
    commands = {e.__name__.split('.')[-1].lower()[:-7]: e.__doc__
                for e in commands if e.__name__ != 'Command'}
    from bx import __version__
    logo = open(op.join(op.dirname(bx.__file__),
                        'data', 'logo')).read()
    desc = '[green on white]%s[/green on white]\n' % logo
    desc = desc + '[bold]bx[/bold] (v%s)\n\nAvailable commands:\n' % __version__

    for e, v in commands.items():
        i = int(len(str(e)) / 6)
        tabs = (3 - i) * '\t'
        v = '%s%s' % (tabs, v) if v is not None else ''
        desc = desc + ' [bold cyan]%s[/bold cyan] %s\n' % (e, str(v).split('\n')[0])

    desc = desc + '\nbx is distributed in the hope that it will be useful, ' \
                  'but WITHOUT ANY WARRANTY. \nSubmit issues/comments/PR at ' \
                  'http://gitlab.com/xgrg/bx.\n\nAuthors: Greg Operto, ' \
                  'Jordi Huguet, Marina Garcia Prat - BarcelonaBeta Brain '\
                  'Research Center (2019-2021)'

    from argparse import RawTextHelpFormatter
    parser = AParser(description=desc, formatter_class=RawTextHelpFormatter)
    parser.add_argument('command', help='bx command')
    parser.add_argument('args', help='Arguments', nargs="*")
    parser.add_argument('--config', help='XNAT configuration file',
                        required=False, default=cfgfile)
    parser.add_argument('--dest', help='Destination folder',
                        required=False, action=ReadableDir)
    parser.add_argument('--verbose', '-v', action='store_true', default=False,
                        help='Display verbosal information (optional)',
                        required=False)

    from bx import __version__
    parser.add_argument('-V', '--version', action='version',
                        version="%(prog)s ("+__version__+")")

    return parser
