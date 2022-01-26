#!/usr/bin/env python3

import argparse
import os
import sys
from typing import List

from sandboxcreator.creator import create


def _parse_cli_args(cli_args: List[str]) -> argparse.ArgumentParser:
    """Parse command line arguments"""

    parser = argparse.ArgumentParser()

    parser.add_argument("topology_file",
                        help="path to the topology definition")
    parser.add_argument("-o", "--output-dir",
                        help="output directory for the sandbox",
                        default="",
                        action="store")
    parser.add_argument("-a", "--ansible-installed",
                        help="use Ansible installed on the host machine",
                        action="store_true")
    parser.add_argument("--rewrite-provisioning",
                        help="always generate clean user provisioning",
                        action="store_true")
    parser.add_argument("--provisioning-dir",
                        help="path to directory with user provisioning files",
                        default="",
                        action="store")
    parser.add_argument("--extra-vars",
                        help="path to file with extra_vars for Ansible",
                        default="",
                        action="store")
    parser.add_argument("--verbose-ansible",
                        help="set verbose output for Ansible (-vv)",
                        action="store_true")

    return parser.parse_args(cli_args)


def _run_create(parsed_cli_args: argparse.ArgumentParser) -> None:
    """Run the create module to generate the intermediate definition"""

    try:
        create(parsed_cli_args.topology_file, parsed_cli_args.output_dir,
               parsed_cli_args.ansible_installed,
               parsed_cli_args.provisioning_dir, parsed_cli_args.extra_vars,
               parsed_cli_args.rewrite_provisioning,
               parsed_cli_args.verbose_ansible, os.getcwd())
    except Exception as e:
        print(f"Could not create intermediate sandbox definition:\n{e}")
        sys.exit(1)

    print("Intermediate sandbox definition was successfully created")


def main():
    parsed_args: argparse.ArgumentParser = _parse_cli_args(sys.argv[1:])
    _run_create(parsed_args)


if __name__ == '__main__':
    main()
