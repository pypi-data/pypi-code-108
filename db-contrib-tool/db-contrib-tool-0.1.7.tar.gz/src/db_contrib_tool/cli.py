"""Command-line entry-point into db-contrib-tool."""

import argparse
import sys

from db_contrib_tool.bisect import BisectPlugin
from db_contrib_tool.setup_repro_env.setup_repro_env import SetupReproEnvPlugin
from db_contrib_tool.symbolizer.mongosymb import SymbolizerPlugin
from db_contrib_tool.usage_analytics import track_usage

_PLUGINS = [BisectPlugin(), SetupReproEnvPlugin(), SymbolizerPlugin()]


def parse(sys_args):
    """Parse the CLI args."""

    parser = argparse.ArgumentParser(
        description="The db-contrib-tool - MongoDB's tools for contributors."
        " For more information, see the help message for each subcommand."
        " For example: db-contrib-tool setup-repro-env -h"
    )
    subparsers = parser.add_subparsers(dest="command")

    # Add sub-commands.
    for plugin in _PLUGINS:
        plugin.add_subcommand(subparsers)

    parsed_args = parser.parse_args(sys_args)

    return parser, parsed_args


def parse_command_line(sys_args, **kwargs):
    """Parse the command line arguments passed to db-contrib-tool and return the subcommand object to execute."""
    parser, parsed_args = parse(sys_args)

    command = parsed_args.command

    track_usage(
        event="Command Line Tool Invoked",
        properties={
            "command": command,
            "parsed_arguments": vars(parsed_args),
        },
    )

    for plugin in _PLUGINS:
        subcommand_obj = plugin.parse(command, parser, parsed_args, **kwargs)
        if subcommand_obj is not None:
            return subcommand_obj


def main():
    subcommand = parse_command_line(sys.argv[1:])
    result = subcommand.execute()
    exit(result.value)


if __name__ == "__main__":
    main()
