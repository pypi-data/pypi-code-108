# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

from appdynamics.lang import items, keys

HELP_OPTIONS = ('--help', '-h', '-?')


class CommandInvocationError(Exception):
    pass


class CommandExecutionError(Exception):
    pass


def parse_options(option_descrs, args):
    options = {}

    required = set()
    short_flags = {}
    for opt, opt_descr in items(option_descrs):
        if isinstance(opt_descr, dict):
            if 'short' in opt_descr:
                short_flags[opt_descr['short'][0]] = opt
            if opt_descr.get('required', False):
                required.add(opt)

    i = 0
    argc = len(args)

    while i < argc and args[i][:1] == '-':  # While there's an arg and it's an option...
        arg = args[i]

        if arg == '--' or arg == '-':       # The option to end all options.
            i += 1                          # Skip the dash.
            break

        if arg in HELP_OPTIONS:             # Help options short circuit everything.
            return {'help': True}, []

        if arg[1] == '-':                   # Long option.
            opt = arg[2:]
        else:                               # Short option.
            opt = short_flags.get(arg[1])

        if opt not in option_descrs:
            raise CommandInvocationError('unrecognized option: %s' % arg)

        option_descr = option_descrs[opt]

        if isinstance(option_descr, dict) and option_descr.get('value'):
            value_label = option_descr.get('value_help', '<value>')
            i += 1

            if i >= argc:
                raise CommandInvocationError('missing value for option: %s %s' % (arg, value_label))

            options[opt] = args[i]
        else:
            options[opt] = True

        i += 1

    missing = ['--%s' % r for r in required - set(keys(options))]

    if missing:
        plural = 's' if len(missing) != 1 else ''
        missing = ', '.join(missing)
        raise CommandInvocationError('missing required option%s: %s' % (plural, missing))

    return options, args[i:]
