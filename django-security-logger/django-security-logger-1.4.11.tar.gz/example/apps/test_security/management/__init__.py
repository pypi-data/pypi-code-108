import sys
from distutils.version import StrictVersion

import django
from django.core.management import CommandError, CommandParser
from django.core.management import call_command as call_command_original
from django.core.management import execute_from_command_line as execute_from_command_line_original
from django.core.management import handle_default_options
from django.utils.version import get_main_version


def execute_from_command_line(argv=None):

    def execute_from_command_line_with_stdout(argv=None, stdout=None, stderr=None):
        try:
            if stdout:
                sys.stdout = stdout
            if stderr:
                sys.stderr = stderr
            execute_from_command_line_original(argv=argv)
        finally:
            if stdout:
                sys.stdout = sys.__stdout__
            if stderr:
                sys.stderr = sys.__stderr__

    if len(argv) > 1:
        from security.utils import CommandLogger

        # some arguments must be processed before django setup
        parser_args = (None,) if StrictVersion(get_main_version()) < StrictVersion('2.1') else tuple()
        parser = CommandParser(*parser_args, usage='%(prog)s subcommand [options] [args]', add_help=False)
        parser.add_argument('--settings')
        parser.add_argument('--pythonpath')
        parser.add_argument('args', nargs='*')  # catch-all
        try:
            options, args = parser.parse_known_args(argv[2:])
            handle_default_options(options)
        except CommandError:
            pass  # Ignore any option errors at this point.

        django.setup()

        return CommandLogger(
            command_function=execute_from_command_line_with_stdout,
            command_kwargs={'argv': argv},
            name=argv[1],
            input=' '.join(argv[2:]),
            executed_from_command_line=True
        ).run()

    else:
        execute_from_command_line_original(argv=argv)


def call_command(command_name, stdout=None, stderr=None, *args, **options):
    stdout = sys.stdout if stdout is None else stdout
    stderr = sys.stderr if stderr is None else stderr

    from security.utils import CommandLogger
    return CommandLogger(
        command_function=call_command_original,
        command_args=(command_name,) + tuple(args),
        command_kwargs=options,
        stdout=stdout,
        stderr=stderr,
        name=command_name,
        input=', '.join(
            list(args)+['{}={}'.format(k, v) for k, v in options.items()]
        )
    ).run()
