"""
CLI for configbuilder
"""

import sys
import argparse


_PARSER = argparse.ArgumentParser(description='Code to compile CONFIG/FIELD files', add_help=True)
_PARSER.add_argument('sources', nargs="+", help="List of sources to compile")
_PARSER.add_argument('-o', '--output', help="Filenames to create, default %(default)s", default="a")


def get_command_args():
    """Run parser and parse arguments

    :returns: List of arguments
    :rtype: argparse.Namespace

    """
    argList = _PARSER.parse_args()
    print(argList)
    if not argList.sources:
        _PARSER.print_help()
        sys.exit()
    return argList
