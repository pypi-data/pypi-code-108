# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

import os
import sys

from appdynamics.lang import keys
from appdynamics.scripts.pyagent import CommandInvocationError, CommandExecutionError, parse_options, HELP_OPTIONS
from appdynamics.scripts.pyagent.commands import proxy, run, config, version

PYAGENT = os.path.basename(sys.argv[0])

COMMANDS = {
    'proxy': proxy,
    'run': run,
    'config': config,
    'version': version,
}
COMMANDS_ORDER = ('proxy', 'run', 'config')

HELP_TEMPLATE = """\
USAGE
    {pyagent} {usage}

ABOUT
    {about}"""

USAGE = """\
USAGE
    {pyagent} <command> <args...>

ABOUT
    AppDynamics Python Agent management utility

COMMANDS
    help                Print this message
    help <command>      Show detailed help for the given pyagent command
"""


def main():
    if len(sys.argv) < 2:
        print_usage()

    command = sys.argv[1]
    args = sys.argv[2:]

    if command in HELP_OPTIONS or command == 'help':
        if args:
            print_usage(command=args[0])
        else:
            print_usage()

    if command not in COMMANDS:
        print_usage(error="%s: unrecognized command" % command)

    mod = COMMANDS[command]

    try:
        options, args = parse_options(getattr(mod, 'OPTIONS', {}), args)

        if 'help' in options:
            print_usage(command=command)

        mod.command(options, args)
    except CommandInvocationError as exc:
        print_usage(command=command, error=str(exc))
    except CommandExecutionError as exc:
        print(str(exc))


def indent(text, spaces=4):
    indentation = ' ' * spaces
    indented_text = ('\n%s' % indentation).join(text.split('\n'))
    return indented_text


def print_usage(command=None, error=None):
    if command and command not in COMMANDS:
        error = '%s: unrecognized command' % command
        command = None

    if command:
        mod = COMMANDS[command]
        about = indent(mod.ABOUT.format(pyagent=PYAGENT))

        print(HELP_TEMPLATE.format(pyagent=PYAGENT, usage=mod.USAGE, about=about))

        if getattr(mod, 'OPTIONS', None):
            print('OPTIONS')
            for opt in sorted(keys(mod.OPTIONS)):
                opt_descr = mod.OPTIONS[opt]
                if isinstance(opt_descr, dict):
                    if 'short' in opt_descr:
                        opt = '%s / -%s' % (opt, opt_descr['short'])
                    if opt_descr.get('value', False):
                        opt += ' %s' % (opt_descr.get('value_help', ' <value>'))

                    opt_help = opt_descr.get('help', False)

                    if opt_help is False:
                        continue

                    if opt_descr.get('required', False):
                        opt_help = 'REQUIRED: %s' % opt_help
                else:
                    opt_help = opt_descr

                print('    --%-28s  %s' % (opt, opt_help))
    else:
        print(USAGE.format(pyagent=PYAGENT))

        for cmd in COMMANDS_ORDER:
            mod = COMMANDS[cmd]
            first_line = mod.ABOUT.splitlines()[0]
            print("    %-18s  %s" % (cmd, first_line))

    if error:
        prefix = "{pyagent} {command}".format(pyagent=PYAGENT, command=command) if command else PYAGENT
        print('')
        print("ERROR: {prefix}: {error}".format(prefix=prefix, error=error))

    sys.exit(1 if error else 0)


if __name__ == '__main__':
    main()
