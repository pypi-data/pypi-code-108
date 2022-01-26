#! /usr/bin/env python

import argparse
import sys
import os
from pathlib import Path
import pathlib

import logging

logging.basicConfig(format="[%(asctime)s] %(message)s", level=logging.INFO)

path_to_hermes = pathlib.Path(__file__).parent.resolve()
sys.path.append(str(path_to_hermes))
from .core.execution_file import ExecutionFile
from .core.execution import Execution
from .core import settings as settings
from .core import bot as bot


def bot_handler(args):
    if args.register:
        handler = bot.Bot_handler()
        handler.register()


def execute_file(args):
    """Executes the instructions in a .hermes file given via args.execution_file

    :param args: Namespace returned by hermes parser
    """
    logging.info("Executing from hermes execution file %s", str(args.execution_file))
    execution_file = ExecutionFile(
        args.execution_file, args.comment if args.comment else [], args.root
    )
    if args.compile_only:
        execution_file.print_lines()
    else:
        execution = Execution(execution_file, args.name, args.debug)
        execution.run()


def single_execution(args):
    """Executes a single command given to hermes via args.executable

    :param args: Namespace returned by hermes parser
    """
    # TODO input validation
    logging.info('Perfoming single execution of "%s"', args.executable)
    raise NotImplementedError


def execute(args):
    """Function called by exec command checks if a .hermes file or a command is given.

    :param args: Namespace returned by hermes parser
    """
    if args.executable:
        single_execution(args)
    elif args.execution_file:
        execute_file(args)


def create_hermes_execution_file(args):
    """Create a barebone execution file in args.target_directory with name args.filename.
        if script names are given in args.scripts, respective template exec lines are created.

    :param args: Namespace returned by hermes parser
    """
    # TODO input validation
    logging.info('Creating barebone hermes execution file "%s"', args.target_directory)
    args.scripts = args.scripts if args.scripts else ["your_script.py"]
    args.scripts = [s + ".py" if not ".py" in s else s for s in args.scripts]
    n_scripts = len(args.scripts)
    path = os.path.join(args.target_directory, args.filename)
    with open(path, "w") as f:
        ExecutionFile.write_pre(f)
        ExecutionFile.write_std(f)
        ExecutionFile.write_exec(args.scripts, [{}] * n_scripts, [{}] * n_scripts, f=f)


def detailed_help(args):
    """Prints a deatiled help. Used by the help command. If a
    command is specified print help only for that command. Else
    print help for all commands.

    :param args: Namespace returned by hermes parser
    """
    if args.command == "ALL":
        for command in args.commands:
            print('Help for "hermes %s":' % command)
            args.commands[command].print_help()
            print("")
    elif args.command in args.commands:
        args.commands[args.command].print_help()
    else:
        print("Unknown Command: %s" % args.command)


def _git_is_available() -> bool:
    try:
        settings.get_repo_path()
        return True
    except RuntimeError:
        logging.warning("Git is not available.")
        return False


def main():
    # system information
    git_is_available = _git_is_available()

    """Entry point for hermes. This function is called when execuinh "hermes [...]" in console."""
    # root parser
    hermes_parser = argparse.ArgumentParser(
        prog="hermes",
        description="A command line tool for organized execution of "
        "experiments in form of python scripts",
    )
    hermes_parser.add_argument(
        "-ho",
        action="store_true",
        help="Print help for hermes options used by .hermes files and exit",
    )
    subparsers = hermes_parser.add_subparsers(
        help="hermes commands, exactly one is required", dest="subparser_name"
    )

    ## default hermes settings
    hermes_parser.set_defaults(**settings.DEFAULT_SETTINGS)

    # create subparser for single execution and file execution
    ## hermes exec
    exec_parser = subparsers.add_parser(
        "exec",
        help="Used to manage execution of either a given call to a python script (single execution), or a hermes execution file",
    )
    ## make sure EXACTLY ONE of the execution options is used
    exec_types = exec_parser.add_mutually_exclusive_group(required=True)
    exec_types.add_argument(
        "-e",
        "--executable",
        help="Provided a script call in quotes, perform single execution",
    )
    exec_types.add_argument(
        "-f",
        "--execution_file",
        type=Path,
        help="Provided a path to a hermes execution file, follow the instructions it gives",
    )
    exec_parser.add_argument(
        "-n",
        "--name",
        type=str,
        required=True,
        help="Give the experiment(s) you are about to execute a name to be included in their identifier",
    )
    exec_parser.add_argument(
        "-c",
        "--comment",
        type=str,
        action="append",
        help="Optional comment that is going to be stored in each hermes.info file created as a result of this execution",
    )
    exec_parser.add_argument(
        "--debug",
        action="store_true",
        help="Enables Debug mod. Storage is skipped in order to prevent cluttered experiment directories",
    )
    exec_parser.add_argument(
        "--compile_only",
        action="store_true",
        help="Only compile the hermes file (i.e. resolve directives) and show what would normally be executed without actually executing anything",
    )
    exec_parser.add_argument(
        "--root",
        type=Path,
        help="""
            Per default, Hermes uses the git repository root as the root path for IO operations, e.g. for loading hermes settings.
            This argument allows you to override the root path. If git is not available, it is strictly required, otherwise it is optional.
        """,
        required=not git_is_available,
        default=None,
    )

    ## set function to be called for execution command
    exec_parser.set_defaults(func=execute)

    # create subparser for barebone execution file creation
    ## hermes create
    create_parser = subparsers.add_parser(
        "create", help="Used for creation of barebone execution files"
    )
    create_parser.add_argument("filename", type=str)
    create_parser.add_argument(
        "-s",
        "--scripts",
        required=False,
        action="append",
        help="Optional list of script names to include in the barebone file",
    )
    create_parser.add_argument(
        "-t",
        "--target-directory",
        required=False,
        action="store",
        default="./",
        help="Optional path to target directory, by default the current working directory",
    )

    ## set function to be called for create command
    create_parser.set_defaults(func=create_hermes_execution_file)

    # bot subparser for telegram bot functions
    ## hermes bot
    bot_parser = subparsers.add_parser("bot", help="Interface to Hermes Telegram Bot")
    bot_parser.add_argument(
        "--register",
        action="store_true",
        help="Register for Hermes Telegram Bot. Your bot id will be read from the hermes settings file.",
    )
    bot_parser.set_defaults(func=bot_handler)

    # create subparser for detailed help
    help_parser = subparsers.add_parser(
        "help", help="Display a detailed help for all commands or a given command"
    )
    help_parser.add_argument("command", type=str, default="ALL", nargs="?")
    help_parser.set_defaults(func=detailed_help)
    help_parser.set_defaults(commands={"exec": exec_parser, "create": create_parser})

    # parse args
    args = hermes_parser.parse_args()

    if args.ho:
        print("Hermes Options usage")
        ExecutionFile.option_parser.print_help()
        exit()

    # no command given
    if not hasattr(args, "func"):
        hermes_parser.print_help()
        exit()

    # run selected command
    logging.info(
        "Launching Hermes with experiments path set to %s", args.path_to_experiments
    )
    args.func(args)


if __name__ == "__main__":
    main()
