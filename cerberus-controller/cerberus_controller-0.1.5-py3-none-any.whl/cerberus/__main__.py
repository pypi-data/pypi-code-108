#!/usr/bin/python3

import argparse
import os
import sys
from importlib.metadata import version


def parse_args(sys_args):
    """ Parse Arguments for Cerberus

    Args:
        sys_args (sys.args): System arguments to parse

    Returns:
        argparse.Namespace: command line arguments
    """

    args = argparse.ArgumentParser(
        prog="cerberus",
        description="Proactive layer 2 Openflow Controller"
    )
    args.add_argument(
        '-c', '--config',
        action='store',
        help="Specify config file"
    )
    args.add_argument(
        '-v', '--version',
        action='store_true',
        help="Print version and exit"
    )
    args.add_argument(
        '--verbose',
        action='store_true',
        help='Enables verbose logging'
    )
    args.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Runs in background with no output'
    )

    return args.parse_args(sys_args)


def print_version():
    print(f"Cerberus: {version('cerberus-controller')}")
    sys.exit()


def main():
    """ Main program launching point """
    args = parse_args(sys.argv[1:])

    if args.version:
        print_version()

    os.execvp('ryu-manager', ['ryu-manager', "cerberus.cerberus"])


if __name__ == '__main__':
    main()