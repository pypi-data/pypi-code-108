#!/usr/bin/env python3
"""Command-line interface script for sandbox manager"""

import argparse
import os
import sys
from typing import List, Optional

from sandboxcreator import manager
from sandboxcreator.commands.command_attributes import OutputLocation


def _parse_cli_args(cli_args: List[str]) -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("command",
                        help="command to be executed",
                        choices=["build", "destroy", "access", "suspend",
                                 "resume", "shutdown", "reload"])
    parser.add_argument("-d", "--sandbox-directory",
                        help="path to the sandbox directory",
                        default=os.getcwd())
    parser.add_argument("-m", "--machines",
                        help="list of machines involved",
                        nargs='*',
                        default=[])
    parser.add_argument("-v", "--verbose",
                        help="show Vagrant and Ansible output",
                        action="store_true",
                        default=False)
    parser.add_argument("--ansible-vars",
                        help="Ansible variables",
                        default="")
    parser.add_argument("-o", "--out",
                        help="command line output",
                        choices=["devnull", "stdout"],
                        default="devnull")
    parser.add_argument("-e", "--err",
                        help="command line error output",
                        choices=["devnull", "stdout"],
                        default="stdout")
    return parser.parse_args(cli_args)


def _print_progress_message(command_name: str) -> None:
    """Print messages about progress"""
    if command_name == "build":
        print("Building the sandbox...")
    elif command_name == "destroy":
        print("Destroying the sandbox...")
    elif command_name == "access":
        print("Accessing the virtual machine...")
    elif command_name == "suspend":
        print("Suspending...")
    elif command_name == "resume":
        print("Resuming...")
    elif command_name == "shutdown":
        print("Shutting down...")
    elif command_name == "reload":
        print("Reloading...")
    else:
        raise ValueError(f"Invalid command: {command_name}")


def _print_final_message(command_name: str,
                         exception: Optional[Exception] = None) -> None:
    """Print final message about success or failure"""
    if not command_name:
        print("\nInvalid command")
        return
    if exception is None:
        if command_name == "build":
            print("\nSandbox was successfully built")
        elif command_name == "destroy":
            print("\nSandbox was successfully destroyed")
        elif command_name == "access":
            pass
        elif command_name == "suspend":
            print("\nSandbox was successfully suspended")
        elif command_name == "resume":
            print("\nSandbox was successfully resumed")
        elif command_name == "shutdown":
            print("\nSandbox was successfully shut down")
        elif command_name == "reload":
            print("Sandbox was successfully reloaded")
    else:
        if command_name == "build":
            print(f"\nSandbox building process has failed:\n{exception}")
        elif command_name == "destroy":
            print(f"\nSandbox destroying process has failed:\n{exception}")
        elif command_name == "access":
            print(f"\nCould not access the virtual machine:\n{exception}")
        elif command_name == "suspend":
            print(f"\nCould not suspend the sandbox:\n{exception}")
        elif command_name == "resume":
            print(f"\nCould not resume the sandbox:\n{exception}")
        elif command_name == "shutdown":
            print(f"\nCould not shut down the sandbox:\n{exception}")
        elif command_name == "reload":
            print(f"\nCould not reload the sandbox:\n{exception}")


def _translate_str_output(output_str: str) -> OutputLocation:
    """Translate string output device to enum"""
    if output_str == "devnull":
        return OutputLocation.DEVNULL
    if output_str == "stdout":
        return OutputLocation.STDOUT
    raise ValueError(f"Invalid output device: {output_str}")


def _determine_standard_output(standard_output_str: str,
                               verbose: bool) -> OutputLocation:
    """Determine the standard output location"""
    if _translate_str_output(standard_output_str) is OutputLocation.DEVNULL\
            and verbose:
        return OutputLocation.STDOUT

    return _translate_str_output(standard_output_str)


def _run_manager(cli_args: argparse.Namespace) -> None:
    command_name: str = ""
    try:
        command_name = cli_args.command
        _print_progress_message(command_name)
        output_dev: OutputLocation = _determine_standard_output(cli_args.out,
                                                                cli_args.verbose)
        error_dev: OutputLocation = _translate_str_output(cli_args.err)
        manager.manage(command_name=command_name,
                       sandbox_location=cli_args.sandbox_directory,
                       machines=cli_args.machines,
                       ansible_vars=cli_args.ansible_vars,
                       output=output_dev,
                       error=error_dev)
    except Exception as error:
        _print_final_message(command_name, error)
        sys.exit(1)
    _print_final_message(command_name)


def main():
    """Executable main function"""
    parsed_args: argparse.Namespace = _parse_cli_args(sys.argv[1:])
    _run_manager(parsed_args)


if __name__ == '__main__':
    main()
