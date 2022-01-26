#pylint: disable=W1202
"""
Usage:
    edged [options] [<command>] [<args>...]

Commands:
    go          Start recording to ExoSense

Options:
    -h --help                               Show this screen.
    -v --version                            Print the current version of the ExoEdge library.
    -L --list-commands                      Print installed and available commands.
    -i --ini-file <file>                    INI file with device information.
    -c --config-io-file <cfgfile>           Local file in which to cache config_io, or to start
                                            ExoEdge with a config_io setting for the first time.
                                            Any changes to this setting in ExoSense will be
                                            synced and cached in this file.
    -a --config-applications-file <cfgfile> Local file in which to cache config_applications, or
                                            to start ExeEdge with a config_applications setting
                                            for the first time. Any changes to this setting in
                                            ExoSense will be synced and cached in this file.
    -s --murano-id <sn>                     The device serial number to use.
    -t --murano-token <token>               Token for device authentication.
    -K --pkeyfile <pkey>                    Private key for TLS provisioning.
    -C --certfile <cert>                    Public cert for TLS provisioning.
    -E --murano-cacert <cacert>             CA cert for PKI integration.
    -H --murano-host <host>                 Set host for API requests.
    -p --murano-port <port>                 Set port for API requests.
    -d --debug <lvl>                        Tune the debug output. Logs curl commands at
                                            DEBUG.
                                            (DEBUG|INFO|WARNING|ERROR|CRITICAL).
    -q --queuing <bool>                     Store data when no network and resend data when backing online.
                                            Default: True (True|False)
    --queuing-batch-amount <number>         For queuing. Numbers of records to send in one payload in one payload.
                                            When the number is 0, it would auto-adjust payload to within and close to 64KB.
                                            Default: 0
    --queuing-db-max-size <byte>            For queuing. Limit DB file size to prevent full fill hard disk.
                                            Default: 20000000; 20MB
    --queuing-db-path <path>                For queuing. Put exoedge.db at a specific path.
                                            Default:
                                                On macOS: '/Users/trentm/Library/Application Support/exoedeg'
                                                On Windows: 'C:\\Users\\trentm\\AppData\\Local\\Acme\\exoedeg'
                                                On Linux: '/home/trentm/.local/share/exoedeg
    --queuing-drop-strategy <oldest|latest> For queuing. The behavior when DB is full. Drop old data and then append new data or just drop new data.
                                            Default: oldest
    --queuing-record-rate <second>          For queuing. How long report data one time.
                                            Default: 1
    --queuing-remove-unused-device <bool>   Remove DB's table when device is not used. The device is according to --murano-id. This is useful when you change devices and want to clean DB.
                                            Default: False
    --strategy <strategy>                   DEPRECATED. See Notes #2 below for details.
    --local-strategy                        DEPRECATED. See option --strategy.
    --no-filesystem                         DEPRECATED. Don't rely on a file system.
    --no-config-cache                       DEPRECATED. Don't store a local copy of config_io.
    --no-config-sync                        DEPRECATED. Don't keep config_io synced with ExoSense.
    --http-timeout <timeout>                Timeout to use for long-poll requests.
    --edged-timeout <timeout>               Timeout for edged process, in seconds. The edged
                                            process will exit after <timeout> seconds.
    --watchlist <watchlist>                 DEPRECATED. Murano resources to watch. Comma separated
                                            list (e.g. --watchlist=config_io,data_out). Settable in
                                            INI file.
    <command>                               The ExoEdge subcommand name.
    <args>                                  Supported arguments for <command>

Notes:

    1. ExoEdge logs default to 'stdout'. This can be overridden to either 'stderr' or
       a logfile of choice. If using a logfile of choice, then the log file will be
       rotated once it reaches a given size (in bytes).

       e.g.

            $ export EDGED_LOG_FILENAME=${PWD}/edged.log
            $ edged -i f5330e5s8cho0000.ini go

       Other supported environment variables for logging configuration are:

            EDGED_LOG_DEBUG (default:CRITICAL)
            EDGED_LOG_MAX_BYTES (default:1024000)
            EDGED_LOG_MAX_BACKUPS (default:3)

    2. The ExoEdge config management state machine* replaces the
       deprecated --strategy CLI options.

       * See exoedge.configs.ConfigWatcher docstring for diagram.

"""
from __future__ import print_function
import sys
import logging
import os
import pkgutil
from docopt import docopt, DocoptExit
import exoedge.commands
from exoedge import __version__ as VERSION
from exoedge import logger

LOG = logger.getLogger(__name__)

def main():
    args = docopt(__doc__, version=VERSION, options_first=True)
    # If no command specified, fallback to 'go' (quickly enables support for pre-built executables)
    args['<command>'] = args['<command>'] or 'go'

    if args.get('--version'):
        print(VERSION)
        return

    if args.get('--list-commands'):
        sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), 'commands'))
        for _, module_name, _ in pkgutil.iter_modules(exoedge.commands.__path__):
            print(module_name)
        return

    if args.get('--debug'):
        level = args.get('--debug')
        if isinstance(level, str):
            level = level.upper()
        LOG.setLevel(getattr(logging, level) or logging.CRITICAL)

    arg = '--local-strategy'
    if args.get(arg):
        LOG.warning(
            "DEPRECATED Command Line Option: <{}>. Please use --strategy option instead (see --help for more info)."
            .format(arg))

    arg = '--strategy'
    if args.get(arg):
        LOG.warning(
            "DEPRECATED Command Line Option: <{}>. See edged -h for more info on configuration management."
            .format(arg))

    for arg in ['--no-filesystem', '--no-config-cache', '--no-config-sync', '--watchlist']:
        if args.get(arg):
            LOG.warning(
                "DEPRECATED Command Line Option: <{}>. Option removed."
                .format(arg))

    if args.get('<command>'):
        command_name = args.pop('<command>')
        argv = args.pop('<args>')
        if argv is None:
            argv = {}

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'commands'))
        try:
            # TODO: If more commands ever added, would need refactoring for dynamic loading
            if command_name != 'go':
                raise ImportError

            from exoedge.commands import go
            command_class = getattr(go, 'ExoCommand')
        except ImportError as exc:
            raise DocoptExit("Cannot find command {!r}: {}"
                             .format(command_name, exc))

        command = command_class(argv, args)

        command.execute()
        return

    raise DocoptExit("Provide an option or subcommand\n")


if __name__ == '__main__':
    main()
