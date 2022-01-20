#!/usr/bin/env python3

import click
import getpass
import json
import os
import stat
import sys

from DKCloudCommand.version import DK_VERSION
from DKCommon.typing import JSONData
from datetime import datetime
from os.path import expanduser
from signal import signal, SIGINT, getsignal
from sys import path, exit
from typing import List, Dict, Tuple, Callable, Union, Optional

__author__ = "DataKitchen, Inc."

home = expanduser("~")  # does not end in a '/'
if os.path.join(home, "dev/DKCloudCommand") not in path:
    path.insert(0, os.path.join(home, "dev/DKCloudCommand"))
from DKCloudCommand.modules.DKCLIRecipeChecker import DKCLIRecipeChecker
from DKCloudCommand.modules.DKCloudAPI import DKCloudAPI
from DKCloudCommand.modules.DKCloudCommandConfig import DKCloudCommandConfig
from DKCloudCommand.modules.DKCloudCommandRunner import DKCloudCommandRunner
from DKCloudCommand.modules.DKFileHelper import DKFileHelper
from DKCloudCommand.modules.DKKitchenDisk import DKKitchenDisk
from DKCloudCommand.modules.DKRecipeDisk import DKRecipeDisk
from DKCloudCommand.modules.DKCloudAPI import DKReturnCode

DEFAULT_IP = "https://cloud.datakitchen.io"
DEFAULT_PORT = "443"
DEFAULT_CONTEXT = "default"
PY2 = sys.version_info[0] == 2
MASTER = "master"

alias_exceptions = {
    "recipe-copy": "ry",
    "recipe-conflicts": "rf",
    "kitchen-config": "kf",
    "recipe-create": "re",
    "file-diff": "fdi",
    "context-list": "xl",
}

ORIGINAL_SIGINT = None
HOOK_FILES = ["pre-commit"]
GITHOOK_TEMPLATE = """
#!/bin/bash
python -m DKCloudCommand.hooks.DKHooks $0 "$@"
exit $?
"""


def handle_exception(e):
    message = str(e)
    if "CERTIFICATE_VERIFY_FAILED" in message:
        certificate_message = (
            "There is a problem with the SSL Certificate. "
            "To solve it, please run the following command. "
            "Paste the following line into the Mac Terminal app "
            "(adjust the Python version as needed) "
            "(you may need to login as a super user)"
            ", and press Enter/Return.:"
        )
        certificate_message += os.linesep + os.linesep + "/Applications/Python\\ 3.8/Install\\ Certificates.command"
        message = certificate_message + os.linesep + os.linesep + "Further details: " + os.linesep + message
    raise click.ClickException(message)


def exit_if_python2():
    if PY2:
        sys.exit(
            "Python2 reached end of life and is not supported by DKCloudCommand. Please use Python 3.6 (or later) "
            "and reinstall DKCloudCommand using pip3 ('pip3 install DKCloudCommand')."
        )


# Use this to override the automated help
class DKClickCommand(click.Command):
    def __init__(
        self,
        name: str,
        context_settings: Optional[JSONData] = None,
        callback: Optional[Callable] = None,
        params: Optional[List[Union[click.Option, click.Argument]]] = None,
        help: Optional[str] = None,
        epilog: Optional[str] = None,
        short_help: Optional[str] = None,
        options_metavar: str = "[OPTIONS]",
        add_help_option: bool = True,
    ) -> None:
        super(DKClickCommand, self).__init__(
            name,
            context_settings,
            callback,
            params,
            help,
            epilog,
            short_help,
            options_metavar,
            add_help_option,
        )

    def get_help(self, ctx: click.Context) -> str:
        # my_help = click.Command.get_help(ctx)
        my_help = super(DKClickCommand, self).get_help(ctx)
        return my_help


class Backend(object):
    _short_commands = {}

    def __init__(self, only_check_version: bool = False, current_command: Optional[str] = None) -> None:
        self.cfg = None
        self.dki = None

        self.init_folders()

        if not self.check_version(self.cfg):
            exit(1)

        if only_check_version:
            return

        self.current_command = current_command
        self.init_context()

        self.cfg.check_working_path()
        self.cfg.print_current_context(current_command)

    def init_folders(self) -> None:
        dk_temp_folder = os.path.join(home, ".dk")

        # Create path if do not exist
        try:
            os.makedirs(dk_temp_folder)
        except Exception:
            pass
        cfg = DKCloudCommandConfig()
        cfg.set_dk_temp_folder(dk_temp_folder)
        cfg.init_ignore_file(dk_temp_folder)
        self.cfg = cfg

    def init_context(self) -> None:
        # Check context
        dk_context_path = os.path.join(self.cfg.get_dk_temp_folder(), ".context")
        if not os.path.isfile(dk_context_path):
            DKFileHelper.write_file(dk_context_path, DEFAULT_CONTEXT)
        dk_context = DKFileHelper.read_file(dk_context_path)
        dk_customer_temp_folder = os.path.join(self.cfg.get_dk_temp_folder(), dk_context.strip())

        # Create path if do not exist
        try:
            os.makedirs(dk_customer_temp_folder)
        except Exception:
            pass

        self.cfg.set_dk_customer_temp_folder(dk_customer_temp_folder)
        self.cfg.set_context(dk_context.strip())

        # If they are running the config command, they're about to do this anyways so skip it
        if self.current_command != "config" and not os.path.isfile(self.cfg.get_config_file_location()):
            click.secho("You are running an un-configured system!", fg="yellow")
            click.secho("Let's run configuration before continuing.", fg="yellow")
            perform_general_config = not os.path.isfile(self.cfg.get_general_config_file_location())
            self.setup_cli(self.cfg.get_config_file_location(), perform_general_config, True)

        if not self.cfg.init_from_file(self.cfg.get_config_file_location()):
            s = f"Unable to load configuration from '{self.cfg.get_config_file_location()}'"
            raise click.ClickException(s)
        self.dki = DKCloudAPI(self.cfg)
        if self.dki is None:
            s = "Unable to create and/or connect to backend object."
            raise click.ClickException(s)

        token = self.dki.login()

        if token is None:
            message = (
                f"\nLogin failed. You are in context {dk_context}, do you want to reconfigure your context? [yes/No]"
            )
            confirm = input(message)
            if confirm.lower() != "yes":
                exit(0)
            else:
                self.setup_cli(self.cfg.get_config_file_location(), False, True)
                print(f"Context {dk_context} has been reconfigured")
                exit(0)

    def check_version(self, cfg: DKCloudCommandConfig) -> bool:
        if self.cfg.is_skip_version_check_present():
            return True

        if "rc" in DK_VERSION:
            return True

        # Get current code version
        current_version = self.version_to_int(DK_VERSION)

        # Get latest version from local file
        latest_version_file = os.path.join(cfg.get_dk_temp_folder(), ".latest_version")
        latest_version = None
        if os.path.exists(latest_version_file):
            latest_version = DKFileHelper.read_file(latest_version_file).strip()

        # Get latest version number from pypi API and update local file.
        try:
            latest_version = cfg.get_latest_version_from_pip()
        except Exception:
            click.secho("Warning: could not get DKCloudCommand latest version number from pip.", fg="red")

        # update local file with latest version number from pip
        try:
            if latest_version is not None:
                DKFileHelper.write_file(latest_version_file, latest_version)
        except Exception:
            click.secho(f"Warning: {latest_version_file} file could not be written.", fg="red")

        # If we are not in latest known version. Prompt the user to update.
        if latest_version and self.version_to_int(latest_version) > current_version:
            divider = "\033[31m" + ("*" * 83) + "\033[39m"
            print(divider)
            print(
                "\033[31m Warning !!!\033[39m\n"
                "\033[31m Your command line is out of date, "
                f"new version {latest_version} is available. Please update.\033[39m\n"
                '\033[31m Type "pip3 install DKCloudCommand --upgrade" to upgrade.\033[39m'
            )
            print(divider + "\n")
            return False

        return True

    def version_to_int(self, version_str: str) -> int:
        tokens = self.padded_version(version_str).split(".")
        tokens.reverse()
        return sum([int(v) * pow(100, i) for i, v in enumerate(tokens)])

    def padded_version(self, version_str: str) -> str:
        while True:
            tokens = version_str.split(".")
            if len(tokens) >= 4:
                return version_str
            version_str += ".0"

    def setup_cli(self, file_path: str, general: bool = False, context: bool = False) -> None:
        if context:
            username = input("\nEnter username: ")
            password = getpass.getpass("Enter password: ")
            ip = input("DK Cloud Address (default https://cloud.datakitchen.io): ")
            port = input("DK Cloud Port (default 443): ")

            if not ip:
                ip = DEFAULT_IP
            if not port:
                port = DEFAULT_PORT

            print("")
            if username == "" or password == "":
                raise click.ClickException("Invalid credentials")

            data = {
                "dk-cloud-ip": ip,
                "dk-cloud-port": port,
                "dk-cloud-username": username,
                "dk-cloud-password": password,
            }

            self.cfg.delete_jwt_from_file()

            with open(file_path, "w+") as f:
                json.dump(data, f, indent=4)

        if general:
            merge_tool = input("DK Cloud Merge Tool Template (default None): ")
            diff_tool = input("DK Cloud File Diff Tool Template (default None): ")

            check_working_path = input("Check current working path against existing contexts?[yes/No] (default No): ")
            if check_working_path is not None and check_working_path.lower() == "yes":
                check_working_path = True
            else:
                check_working_path = False

            hide_context_legend = input("Hide current context legend on each command response?[yes/No] (default No): ")
            if hide_context_legend is not None and hide_context_legend.lower() == "yes":
                hide_context_legend = True
            else:
                hide_context_legend = False

            skip_recipe_checker = input(
                "Skip checking the recipe locally, before recipe-update like commands?[yes/No] (default No): "
            )
            if skip_recipe_checker is not None and skip_recipe_checker.lower() == "yes":
                skip_recipe_checker = True
            else:
                skip_recipe_checker = False

            self.cfg.configure_general_file(
                merge_tool, diff_tool, check_working_path, hide_context_legend, skip_recipe_checker
            )
        print("\n")

    @staticmethod
    def get_kitchen_name_soft(given_kitchen: Optional[str] = None) -> Optional[str]:
        """
        Get the kitchen name if it is available.
        :return: kitchen name or None
        """
        if given_kitchen is not None:
            return given_kitchen
        else:
            in_kitchen = DKCloudCommandRunner.which_kitchen_name()
            return in_kitchen

    @staticmethod
    def check_in_kitchen_root_folder_and_get_name() -> str:
        """
        Ensures that the caller is in a kitchen folder.
        :return: kitchen name or None
        """
        in_kitchen = DKCloudCommandRunner.which_kitchen_name()
        if in_kitchen is None:
            raise click.ClickException("Please change directory to a kitchen folder.")
        else:
            return in_kitchen

    @staticmethod
    def get_kitchen_from_user(kitchen: Optional[str] = None) -> Tuple[str, str]:
        in_kitchen = DKCloudCommandRunner.which_kitchen_name()
        if kitchen is None and in_kitchen is None:
            raise click.ClickException("You must provide a kitchen name or be in a kitchen folder.")

        if in_kitchen is not None:
            use_kitchen = in_kitchen

        if kitchen is not None:
            use_kitchen = kitchen

        use_kitchen = Backend.remove_slashes(use_kitchen)

        return "ok", use_kitchen

    @staticmethod
    def get_recipe_name(recipe: str) -> Tuple[str, str]:
        in_recipe = DKRecipeDisk.find_recipe_name()
        if recipe is None and in_recipe is None:
            raise click.ClickException("You must provide a recipe name or be in a recipe folder.")
        elif recipe is not None and in_recipe is not None:
            info = "Please provide a recipe parameter or change directory to a recipe folder, not both."
            raise click.ClickException(f"{info}\nYou are in Recipe '{in_recipe}'")

        if in_recipe is not None:
            use_recipe = in_recipe
        else:
            use_recipe = recipe

        use_recipe = Backend.remove_slashes(use_recipe)
        return "ok", use_recipe

    @staticmethod
    def remove_slashes(name: str) -> str:
        if len(name) > 1 and (name.endswith("\\") or name.endswith("/")):
            return name[:-1]
        return name

    def set_short_commands(self, commands: Dict[str, DKClickCommand]) -> Dict[str, str]:
        short_commands = {}
        for long_command in commands:
            if long_command in alias_exceptions:
                short_commands[long_command] = alias_exceptions[long_command]
                continue
            short_commands[long_command] = short_command_from_long(long_command)
        self._short_commands = short_commands
        return self._short_commands

    def get_short_commands(self) -> Dict[str, str]:
        return self._short_commands


def check_and_print(rc: DKReturnCode) -> None:
    if rc.ok():
        click.echo(rc.get_message())
    else:
        raise handle_exception(rc.get_message())


def short_command_from_long(long_command: str) -> str:
    parts = long_command.split("-")
    short_command = ""
    for part in parts:
        if part == "orderrun":
            short_command += "or"
        else:
            short_command += part[0]
    return short_command


class AliasedGroup(click.Group):
    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command:
        self._check_unique(ctx)
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv

        found_command = next(
            (long_command for long_command, short_command in alias_exceptions.items() if short_command == cmd_name),
            None,
        )

        if found_command is not None:
            return click.Group.get_command(self, ctx, found_command)

        all_commands = self.list_commands(ctx)
        for long_command in all_commands:
            short_command = self.short_command(long_command)
            if short_command == cmd_name:
                return click.Group.get_command(self, ctx, long_command)
        ctx.fail(f"Unable to find command for alias '{cmd_name}'")

    def short_command(self, long_command: str) -> str:
        if long_command in alias_exceptions:
            return alias_exceptions[long_command]
        return short_command_from_long(long_command)

    def _check_unique(self, ctx: click.Context) -> None:
        all_commands = self.list_commands(ctx)
        short_commands = {}
        for long_command in all_commands:
            if long_command in alias_exceptions:
                continue

            short_command = self.short_command(long_command)

            if short_command in short_commands:
                click.secho(f"The short alias {short_command} is ambiguous", fg="red")
            else:
                short_commands[short_command] = long_command

    def format_commands(self, ctx: click.Context, formatter: click.formatting.HelpFormatter) -> None:
        # override default behavior
        rows = []
        for sub_command in self.list_commands(ctx):
            cmd = self.get_command(ctx, sub_command)
            if cmd is None:
                continue

            help = cmd.short_help or ""
            rows.append((f"{sub_command} ({self.short_command(sub_command)})", help))
        if rows:
            with formatter.section("Commands"):
                formatter.write_dl(rows)


@click.group(cls=AliasedGroup)
@click.version_option(version=DK_VERSION)
@click.pass_context
def dk(ctx: click.Context):

    exit_if_python2()
    ctx.obj = Backend(current_command=ctx.invoked_subcommand)
    ctx.obj.set_short_commands(ctx.command.commands)


@dk.command(name="config-list", cls=DKClickCommand)
@click.option(
    "--hide-password",
    "-u",
    type=bool,
    required=False,
    default=True,
    help="Control if the password is hidden on printing. By default, the password is hidden.",
)
@click.pass_obj
def config_list(backend: Backend, hide_password: bool) -> None:
    """
    Print the current configuration.
    """
    try:
        click.secho("Current configuration is...", fg="green")
        ret = ""
        customer_name = backend.dki.get_customer_name()
        if customer_name:
            ret += f"Customer Name:\t\t\t{customer_name}\n"
        ret += backend.dki.get_config().to_str(hide_password=hide_password)
        click.echo(ret)
    except Exception as e:
        handle_exception(e)


@dk.command(name="config", cls=DKClickCommand)
@click.option(
    "--full",
    "-f",
    default=False,
    is_flag=True,
    required=False,
    help="General and context configuration",
)
@click.option("--context", "-c", default=False, is_flag=True, required=False, help="Context configuration")
@click.option("--general", "-g", default=False, is_flag=True, required=False, help="General configuration")
@click.pass_obj
def config(backend: Backend, full: bool, context: bool, general: bool) -> None:
    """
    Configure Command Line.
    """
    try:
        if not any([full, context, general]):
            full = True
        if full:
            general = True
            context = True

        if context and backend.cfg.get_hide_context_legend():
            click.echo(f"Current context is: {backend.cfg.get_current_context()}\n")

        backend.setup_cli(backend.cfg.get_config_file_location(), general, context)
        click.echo("Configuration changed!.\n")
    except Exception as e:
        handle_exception(e)


@dk.command(name="context-list", cls=DKClickCommand)
@click.pass_obj
def context_list(backend: Backend) -> None:
    """
    List available contexts.

    """
    try:
        click.secho("Available contexts are...\n")
        contexts = backend.cfg.context_list()
        for context in contexts:
            click.echo(f"{context}")
        if backend.cfg.get_hide_context_legend():
            click.echo(f"\nCurrent context is: {backend.cfg.get_current_context()} \n")
    except Exception as e:
        handle_exception(e)


@dk.command(name="context-delete", cls=DKClickCommand)
@click.option("--yes", "-y", default=False, is_flag=True, required=False, help="Force yes")
@click.argument("context_name", required=True)
@click.pass_obj
def context_delete(backend: Backend, context_name: str, yes: bool) -> None:
    """
    Deletes a context.

    """
    try:
        if not backend.cfg.context_exists(context_name):
            click.echo("\nContext does not exist.")
            return

        current_context = backend.cfg.get_current_context()
        if current_context == context_name:
            click.echo("Please switch to another context before proceeding")
            click.echo("Use context-switch command.")
            return

        if DEFAULT_CONTEXT == context_name:
            click.echo("Default context cannot be removed.")
            return

        if not yes:
            message = "\nCredential information will be lost.\n"
            message += f"Are you sure you want to delete context {context_name}? [yes/No]"
            confirm = input(message)
            if confirm.lower() != "yes":
                click.echo("\nExiting.")
                return

        click.secho(f"Deleting context '{context_name}'...\n")
        backend.cfg.delete_context(context_name)
        click.secho("Done!")
    except Exception as e:
        handle_exception(e)


@dk.command(name="context-switch", cls=DKClickCommand)
@click.option("--yes", "-y", default=False, is_flag=True, required=False, help="Force yes")
@click.argument("context_name", required=True)
@click.pass_obj
def context_switch(backend: Backend, context_name: str, yes: bool) -> None:
    """
    Create or switch to a new context.
    """
    try:
        context_name = context_name.strip()

        current_context = backend.cfg.get_current_context()
        if current_context == context_name:
            click.echo(f"You already are in context {context_name}")
            return

        if not backend.cfg.context_exists(context_name):
            if not yes:
                message = f"\nContext does not exist. Are you sure you want to create context {context_name}? [yes/No]"
                confirm = input(message)
                if confirm.lower() != "yes":
                    return
                backend.cfg.create_context(context_name)
        click.secho(f"Switching to context {context_name}...")
        backend.cfg.switch_context(context_name)
        backend.init_context()
        click.echo("Context switch done.")
        click.echo("Use dk user-info and dk config-list to get context details.")
    except Exception as e:
        handle_exception(e)


@dk.command(name="recipe-status")
@click.pass_obj
def recipe_status(backend: Backend) -> None:
    """
    Compare local recipe to remote recipe for the current recipe.
    """
    try:
        kitchen = DKCloudCommandRunner.which_kitchen_name()
        if kitchen is None:
            raise click.ClickException("You are not in a Kitchen")
        recipe_dir = DKRecipeDisk.find_recipe_root_dir()
        if recipe_dir is None:
            raise click.ClickException("You must be in a Recipe folder")
        recipe_name = DKRecipeDisk.find_recipe_name()
        click.secho(
            f"{get_datetime()} - Getting the status of Recipe '{recipe_name}' in Kitchen '{kitchen}'\n\tversus directory '{recipe_dir}'",
            fg="green",
        )
        check_and_print(DKCloudCommandRunner.recipe_status(backend.dki, kitchen, recipe_name, recipe_dir))
    except Exception as e:
        handle_exception(e)


# -------------------------------------------------------------------------------------------------
# User and Authentication Commands
# -------------------------------------------------------------------------------------------------
@dk.command(name="user-info")
@click.pass_obj
def user_info(backend: Backend) -> None:
    """
    Get information about this user.
    """
    try:
        check_and_print(DKCloudCommandRunner.user_info(backend.dki))
    except Exception as e:
        handle_exception(e)


# -------------------------------------------------------------------------------------------------
#  kitchen commands
# -------------------------------------------------------------------------------------------------
def get_datetime() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@dk.command(name="kitchen-list")
@click.pass_obj
def kitchen_list(backend: Backend) -> None:
    """
    List all Kitchens
    """
    try:
        click.echo(click.style(f"{get_datetime()} - Getting the list of kitchens", fg="green"))
        check_and_print(DKCloudCommandRunner.list_kitchen(backend.dki))
    except Exception as e:
        handle_exception(e)


@dk.command(name="kitchen-get")
@click.option(
    "--recipe",
    "-r",
    type=str,
    multiple=True,
    help="Get the recipe along with the kitchen. Multiple allowed",
)
@click.option("--all", "-a", is_flag=True, help="Get all recipes along with the kitchen.")
@click.argument("kitchen_name", required=True)
@click.pass_obj
def kitchen_get(backend: Backend, kitchen_name: str, recipe: Tuple[str, ...], all: bool) -> None:
    """
    Get an existing Kitchen locally. You may also get one or multiple Recipes from the Kitchen.
    """
    try:
        found_kitchen = DKKitchenDisk.find_kitchen_name()
        if found_kitchen is not None and len(found_kitchen) > 0:
            raise click.ClickException("You cannot get a kitchen into an existing kitchen directory structure.")

        if len(recipe) > 0:
            click.secho(
                f"{get_datetime()} - Getting kitchen '{kitchen_name}' and the recipes {recipe}",
                fg="green",
            )
        else:
            click.secho(f"{get_datetime()} - Getting kitchen '{kitchen_name}'", fg="green")

        check_and_print(DKCloudCommandRunner.get_kitchen(backend.dki, kitchen_name, os.getcwd(), recipe, all))
    except Exception as e:
        handle_exception(e)


@dk.command(name="kitchen-which")
@click.pass_obj
def kitchen_which(backend: Backend) -> None:
    """
    What Kitchen am I working in?
    """
    try:
        check_and_print(DKCloudCommandRunner.which_kitchen(backend.dki, None))
    except Exception as e:
        handle_exception(e)


@dk.command(name="kitchen-create")
@click.argument("kitchen", required=True)
@click.option("--parent", "-p", type=str, required=True, help="name of parent kitchen")
@click.option("--description", "-d", type=str, required=False, help="Kitchen description")
@click.pass_obj
def kitchen_create(backend: Backend, parent: str, description: Optional[str], kitchen: str) -> None:
    """
    Create and name a new child Kitchen. Provide parent Kitchen name.
    """
    try:
        if not DKCloudCommandRunner.kitchen_exists(backend.dki, parent):
            raise click.ClickException("Parent kitchen {parent} does not exist. Check spelling.")

        click.secho(
            f"{get_datetime()} - Creating kitchen {kitchen} from parent kitchen {parent}",
            fg="green",
        )
        if kitchen.lower() != MASTER:
            check_and_print(DKCloudCommandRunner.create_kitchen(backend.dki, parent, kitchen, description))
        else:
            raise click.ClickException(f"Cannot create a kitchen called {MASTER}")
    except Exception as e:
        handle_exception(e)


@dk.command(name="kitchen-delete")
@click.argument("kitchen", required=True)
@click.option("--yes", "-y", default=False, is_flag=True, required=False, help="Force yes")
@click.pass_obj
def kitchen_delete(backend: Backend, kitchen: str, yes: bool) -> None:
    """
    Provide the name of the kitchen to delete
    """
    try:
        DKCloudCommandRunner.print_kitchen_children(backend.dki, kitchen)

        if not yes:
            confirm = input(f"\nAre you sure you want to delete the remote copy of the Kitchen {kitchen}? [yes/No]")
            if confirm.lower() != "yes":
                return

        click.secho(
            f"{get_datetime()} - Deleting remote copy of kitchen {kitchen}. Local files will not change.",
            fg="green",
        )
        if kitchen.lower() != MASTER:
            check_and_print(DKCloudCommandRunner.delete_kitchen(backend.dki, kitchen))
        else:
            raise click.ClickException(f"Cannot delete the kitchen called {MASTER}")
    except Exception as e:
        handle_exception(e)


@dk.command(name="kitchen-config")
@click.option("--kitchen", "-k", type=str, required=False, help="kitchen name")
@click.option(
    "--add",
    "-a",
    type=str,
    required=False,
    nargs=2,
    help="Add a new override to this kitchen. This will update an existing override variable.\n"
    "Usage: --add VARIABLE VALUE\n"
    "Example: --add kitchen_override 'value1'",
    multiple=True,
)
@click.option(
    "--get",
    "-g",
    type=str,
    required=False,
    help="Get the value for an override variable.",
    multiple=True,
)
@click.option("--unset", "-u", type=str, required=False, help="Delete an override variable.", multiple=True)
@click.option(
    "--listall",
    "-la",
    type=str,
    is_flag=True,
    required=False,
    help="List all variables and their values.",
)
@click.pass_obj
def kitchen_config(
    backend: Backend,
    kitchen: Optional[str],
    add: Optional[str],
    get: Optional[Tuple[str, ...]],
    unset: Optional[Tuple[str, ...]],
    listall: bool,
) -> None:
    """
    Get and Set Kitchen variable overrides

    Example:
    dk kf -k Dev_Sprint -a kitchen_override 'value1'
    """
    try:
        err_str, use_kitchen = Backend.get_kitchen_from_user(kitchen)
        if use_kitchen is None:
            raise click.ClickException(err_str)
        check_and_print(DKCloudCommandRunner.config_kitchen(backend.dki, use_kitchen, add, get, unset, listall))
    except Exception as e:
        handle_exception(e)


@dk.command(name="kitchen-merge-preview")
@click.option("--source_kitchen", "-sk", type=str, required=False, help="source (from) kitchen name")
@click.option("--target_kitchen", "-tk", type=str, required=True, help="target (to) kitchen name")
@click.option(
    "--clean_previous_run",
    "-cpr",
    default=False,
    is_flag=True,
    required=False,
    help="Clean previous run of this command",
)
@click.pass_obj
def kitchen_merge_preview(
    backend: Backend, source_kitchen: Optional[str], target_kitchen: str, clean_previous_run: bool
) -> None:
    """
    Preview the merge of two Kitchens. No change will actually be applied.
    Provide the names of the Source (Child) and Target (Parent) Kitchens.
    """

    try:
        recipe_dir = DKRecipeDisk.find_recipe_root_dir()
        if recipe_dir is not None:
            message = "Warning: You are inside a recipe. Please go at least one level above. This command is typically used from the level above kitchen level."
            click.secho(message, fg="yellow")
            return

        kitchen = DKCloudCommandRunner.which_kitchen_name()
        if kitchen is None and source_kitchen is None:
            raise click.ClickException("You are not in a Kitchen and did not specify a source_kitchen")

        if kitchen is not None and source_kitchen is not None and kitchen != source_kitchen:
            raise click.ClickException(
                "There is a conflict between the kitchen in which you are, and the source_kitchen you have specified"
            )

        if kitchen is not None:
            use_source_kitchen = kitchen
        else:
            use_source_kitchen = source_kitchen

        kitchens_root = DKKitchenDisk.find_kitchens_root(reference_kitchen_names=[use_source_kitchen, target_kitchen])
        if kitchens_root:
            DKCloudCommandRunner.check_local_recipes(backend.dki, kitchens_root, use_source_kitchen)
            DKCloudCommandRunner.check_local_recipes(backend.dki, kitchens_root, target_kitchen)
        else:
            click.secho("The root path for your kitchens was not found, skipping local checks.")

        click.secho(
            f"{get_datetime()} - Previewing merge Kitchen {use_source_kitchen} into Kitchen {target_kitchen}",
            fg="green",
        )
        check_and_print(
            DKCloudCommandRunner.kitchen_merge_preview(
                backend.dki, use_source_kitchen, target_kitchen, clean_previous_run
            )
        )
    except Exception as e:
        error_message = str(e)
        if "Recipe" in str(e) and "does not exist on remote." in str(e):
            error_message += " Delete your local copy before proceeding."
        handle_exception(error_message)


@dk.command(name="kitchen-merge")
@click.option("--source_kitchen", "-sk", type=str, required=False, help="source (from) kitchen name")
@click.option("--target_kitchen", "-tk", type=str, required=True, help="target (to) kitchen name")
@click.option("--yes", "-y", default=False, is_flag=True, required=False, help="Force yes")
@click.pass_obj
def kitchen_merge(backend: Backend, source_kitchen: Optional[str], target_kitchen: str, yes: bool) -> None:
    """
    Merge two Kitchens. Provide the names of the Source (Child) and Target (Parent) Kitchens.
    """
    try:
        kitchen = DKCloudCommandRunner.which_kitchen_name()
        if kitchen is None and source_kitchen is None:
            raise click.ClickException("You are not in a Kitchen and did not specify a source_kitchen")

        if kitchen is not None and source_kitchen is not None and kitchen != source_kitchen:
            raise click.ClickException(
                "There is a conflict between the kitchen in which you are, and the source_kitchen you have specified"
            )

        if kitchen is not None:
            use_source_kitchen = kitchen
        else:
            use_source_kitchen = source_kitchen

        kitchens_root = DKKitchenDisk.find_kitchens_root(reference_kitchen_names=[use_source_kitchen, target_kitchen])
        if kitchens_root:
            DKCloudCommandRunner.check_local_recipes(backend.dki, kitchens_root, use_source_kitchen)
            DKCloudCommandRunner.check_local_recipes(backend.dki, kitchens_root, target_kitchen)
        else:
            click.secho("The root path for your kitchens was not found, skipping local checks.")

        if not yes:
            confirm = input(
                "Are you sure you want to merge the "
                f"\033[1mremote copy of Source Kitchen {use_source_kitchen}\033[0m into the "
                f"\033[1mremote copy of Target Kitchen {target_kitchen}\033[0m? [yes/No]"
            )
            if confirm.lower() != "yes":
                return

        click.secho(
            f"{get_datetime()} - Merging Kitchen {use_source_kitchen} into Kitchen {target_kitchen}",
            fg="green",
        )
        check_and_print(DKCloudCommandRunner.kitchen_merge(backend.dki, use_source_kitchen, target_kitchen))

        retry = True
        while retry:
            try:
                DKCloudCommandRunner.update_local_recipes_with_remote(backend.dki, kitchens_root, target_kitchen)
                retry = False
            except Exception as e:
                confirm = input(f"{e}\nRetry? [yes/No]")
                if confirm.lower() != "yes":
                    retry = False

    except Exception as e:
        handle_exception(e)


@dk.command(name="kitchen-revert")
@click.option("--kitchen", "-k", type=str, required=False, help="kitchen name")
@click.option("--preview", "-p", default=False, is_flag=True, required=False, help="dry run of the revert operation")
@click.option("--yes", "-y", default=False, is_flag=True, required=False, help="Force yes")
@click.pass_obj
def kitchen_revert(backend: Backend, kitchen: str, preview: bool, yes: bool) -> None:
    """
    Revert latest kitchen commit (can be a merge or a simple commit)
    """
    try:
        err_str, use_kitchen = Backend.get_kitchen_from_user(kitchen)
        if use_kitchen is None:
            raise click.ClickException(err_str)

        if not preview and not yes:
            confirm = input(f"\nAre you sure you want to revert the Kitchen {use_kitchen} to previous state? [yes/No]")
            if confirm.lower() != "yes":
                return

        if preview:
            message = f"{get_datetime()} - Preview of reverting kitchen {use_kitchen} to previous state."
        else:
            message = (
                f"{get_datetime()} - Reverting kitchen {use_kitchen} to previous state. Local files will not change."
            )
            message += os.linesep + "After this operation, run recipe-get -o in the related recipes."

        click.secho(message, fg="green")

        msg, _ = DKCloudCommandRunner.revert_kitchen(backend.dki, use_kitchen, preview)
        click.secho(msg, fg="green")
    except Exception as e:
        handle_exception(e)


@dk.command(name="kitchen-history")
@click.option("--kitchen", "-k", type=str, required=False, help="kitchen name")
@click.option(
    "--count", "-c", type=int, required=False, default=10, help="Number of commits to display, default is 10 commits."
)
@click.pass_obj
def kitchen_history(backend: Backend, kitchen: str, count: int) -> None:
    """
    Get Kitchen history
    """
    try:
        err_str, use_kitchen = Backend.get_kitchen_from_user(kitchen)
        if use_kitchen is None:
            raise click.ClickException(err_str)

        message = f"{get_datetime()} - Getting kitchen history for kitchen {use_kitchen}."
        click.secho(message, fg="green")

        click.secho(DKCloudCommandRunner.kitchen_history(backend.dki, use_kitchen, count))
    except Exception as e:
        handle_exception(e)


# -------------------------------------------------------------------------------------------------
#  Recipe commands
# -------------------------------------------------------------------------------------------------
@dk.command(name="recipe-list")
@click.option("--kitchen", "-k", type=str, help="kitchen name")
@click.pass_obj
def recipe_list(backend: Backend, kitchen: str) -> None:
    """
    List the Recipes in a Kitchen
    """
    try:
        err_str, use_kitchen = Backend.get_kitchen_from_user(kitchen)
        if use_kitchen is None:
            raise click.ClickException(err_str)
        click.secho(
            f"{get_datetime()} - Getting the list of Recipes for Kitchen '{use_kitchen}'",
            fg="green",
        )
        check_and_print(DKCloudCommandRunner.list_recipe(backend.dki, use_kitchen))
    except Exception as e:
        handle_exception(e)


@dk.command(name="recipe-create")
@click.option("--kitchen", "-k", type=str, help="kitchen name")
@click.option("--template", "-tm", type=str, help="template name")
@click.argument("name", required=True)
@click.pass_obj
def recipe_create(backend: Backend, kitchen: str, name: str, template: str) -> None:
    """
    Create a new Recipe.

    Available templates: qs1, qs2, qs3
    """
    try:
        err_str, use_kitchen = Backend.get_kitchen_from_user(kitchen)
        if use_kitchen is None:
            raise click.ClickException(err_str)
        click.secho(f"{get_datetime()} - Creating Recipe {name} for Kitchen '{use_kitchen}'", fg="green")
        check_and_print(DKCloudCommandRunner.recipe_create(backend.dki, use_kitchen, name, template=template))
    except Exception as e:
        handle_exception(e)


@dk.command(name="recipe-copy")
@click.option("--kitchen", "-k", type=str, help="kitchen name")
@click.argument("source", required=True)
@click.argument("name", required=True)
@click.pass_obj
def recipe_copy(backend: Backend, kitchen: Optional[str], source: str, name: str) -> None:
    """
    Create a new Recipe based on the given recipe.

    Example:
    dk ry -k my_kitchen existing_recipe my_brand_new_recipe

    """
    try:
        err_str, use_kitchen = Backend.get_kitchen_from_user(kitchen)
        if use_kitchen is None:
            raise click.ClickException(err_str)
        click.secho(
            f"{get_datetime()} - Creating Recipe {name} from recipe {source} for Kitchen '{use_kitchen}'",
            fg="green",
        )
        check_and_print(DKCloudCommandRunner.recipe_copy(backend.dki, use_kitchen, source, name))
    except Exception as e:
        handle_exception(e)


@dk.command(name="recipe-delete")
@click.option("--kitchen", "-k", type=str, help="kitchen name")
@click.option("--yes", "-y", default=False, is_flag=True, required=False, help="Force yes")
@click.argument("name", required=True)
@click.pass_obj
def recipe_delete(backend: Backend, kitchen: Optional[str], name: str, yes: bool) -> None:
    """
    Deletes local and remote copy of the given recipe
    """
    try:
        err_str, use_kitchen = Backend.get_kitchen_from_user(kitchen)
        if use_kitchen is None:
            raise click.ClickException(err_str)

        click.secho(
            f"This command will delete the local and remote copy of recipe '{name}' for kitchen '{use_kitchen}'. "
        )
        if not yes:
            confirm = input(f"Are you sure you want to delete the local and remote copy of recipe {name}? [yes/No]")
            if confirm.lower() != "yes":
                return

        click.secho(f"{get_datetime()} - Deleting Recipe {name} for Kitchen '{use_kitchen}'", fg="green")
        check_and_print(DKCloudCommandRunner.recipe_delete(backend.dki, use_kitchen, name))
    except Exception as e:
        handle_exception(e)


@dk.command(name="recipe-get")
@click.option(
    "--delete_local",
    "-d",
    default=False,
    is_flag=True,
    required=False,
    help="Deletes Recipe files that only exist on local.",
)
@click.option(
    "--overwrite",
    "-o",
    default=False,
    is_flag=True,
    required=False,
    help="Overwrites local version of Recipe files if said files exist on remote.",
)
@click.option(
    "--yes",
    "-y",
    default=False,
    is_flag=True,
    required=False,
    help="Force through the command's subprompt.",
)
@click.argument("recipe", required=False)
@click.pass_obj
def recipe_get(backend: Backend, recipe: Optional[str], delete_local: bool, overwrite: bool, yes: bool) -> None:
    """
    Get the latest remote versions of Recipe files. Changes will be auto-merged to local where
    possible. Conflicts will be written to local such that the impacted files contain full copies
    of both remote and local versions for the user to manually resolve. Local vs remote conflicts
    can be viewed via the file-diff command.
    """
    try:
        recipe_root_dir = DKRecipeDisk.find_recipe_root_dir()
        if recipe_root_dir is None:
            if recipe is None:
                raise click.ClickException("\nPlease change to a recipe folder or provide a recipe name argument")

            # raise click.ClickException('You must be in a Recipe folder')
            kitchen_root_dir = DKKitchenDisk.is_kitchen_root_dir()
            if not kitchen_root_dir:
                raise click.ClickException("\nPlease change to a recipe folder or a kitchen root dir.")
            recipe_name = recipe
            start_dir = DKKitchenDisk.find_kitchen_root_dir()
        else:
            recipe_name = DKRecipeDisk.find_recipe_name()
            if recipe is not None:
                if recipe_name != recipe:
                    raise click.ClickException(
                        f"\nThe recipe name argument '{recipe}' is inconsistent with the current directory '{recipe_root_dir}'"
                    )
            start_dir = recipe_root_dir

        kitchen_name = Backend.get_kitchen_name_soft()
        click.secho(
            f"{get_datetime()} - Getting the latest version of Recipe '{recipe_name}' in Kitchen '{kitchen_name}'",
            fg="green",
        )
        check_and_print(
            DKCloudCommandRunner.get_recipe(
                backend.dki,
                kitchen_name,
                recipe_name,
                start_dir,
                delete_local=delete_local,
                overwrite=overwrite,
                yes=yes,
            )
        )
    except Exception as e:
        handle_exception(e)


@dk.command(name="recipe-compile")
@click.option("--variation", "-v", type=str, required=True, help="variation name")
@click.option("--kitchen", "-k", type=str, help="kitchen name")
@click.option("--recipe", "-r", type=str, help="recipe name")
@click.pass_obj
def recipe_compile(backend: Backend, kitchen: Optional[str], recipe: Optional[str], variation: str) -> None:
    """
    Apply variables to a Recipe
    """
    try:
        err_str, use_kitchen = Backend.get_kitchen_from_user(kitchen)
        if use_kitchen is None:
            raise click.ClickException(err_str)

        if recipe is None:
            recipe = DKRecipeDisk.find_recipe_name()
            if recipe is None:
                raise click.ClickException("You must be in a recipe folder, or provide a recipe name.")

        click.secho(
            f"{get_datetime()} - Get the Compiled Recipe {recipe}.{variation} in Kitchen {use_kitchen}",
            fg="green",
        )
        check_and_print(DKCloudCommandRunner.get_compiled_order_run(backend.dki, use_kitchen, recipe, variation))
    except Exception as e:
        handle_exception(e)


@dk.command(name="file-compile")
@click.option("--variation", "-v", type=str, required=True, help="variation name")
@click.option("--file", "-f", type=str, required=True, help="file path")
@click.pass_obj
def file_compile(backend: Backend, variation: str, file: str) -> None:
    """
    Apply variables to a File
    """
    try:
        kitchen = DKCloudCommandRunner.which_kitchen_name()
        if kitchen is None:
            raise click.ClickException("You are not in a Kitchen")

        recipe_dir = DKRecipeDisk.find_recipe_root_dir()
        if recipe_dir is None:
            raise click.ClickException("You must be in a Recipe folder")
        recipe_name = DKRecipeDisk.find_recipe_name()

        click.secho(
            f"{get_datetime()} - Get the Compiled File of Recipe {recipe_name}.{variation} in Kitchen {kitchen}",
            fg="green",
        )
        check_and_print(DKCloudCommandRunner.get_compiled_file(backend.dki, kitchen, recipe_name, variation, file))
    except Exception as e:
        handle_exception(e)


@dk.command(name="file-history")
@click.option(
    "--change_count",
    "-cc",
    type=int,
    required=False,
    default=0,
    help="Number of last changes to display",
)
@click.argument("filepath", required=True)
@click.pass_obj
def file_history(backend: Backend, change_count: int, filepath: str) -> None:
    """
    Show file change history.
    """
    try:
        kitchen = DKCloudCommandRunner.which_kitchen_name()
        if kitchen is None:
            raise click.ClickException("You are not in a Kitchen")

        recipe = DKRecipeDisk.find_recipe_name()
        if recipe is None:
            raise click.ClickException("You must be in a recipe folder.")

        click.secho(f"{get_datetime()} - Retrieving file history")

        if not os.path.exists(filepath):
            raise click.ClickException(f"{filepath} does not exist")
        check_and_print(DKCloudCommandRunner.file_history(backend.dki, kitchen, recipe, filepath, change_count))
    except Exception as e:
        handle_exception(e)


@dk.command(name="recipe-validate")
@click.option("--variation", "-v", type=str, required=True, help="variation name")
@click.pass_obj
def recipe_validate(backend: Backend, variation: str) -> None:
    """
    Validates local copy of a recipe, returning a list of errors and warnings. If there are no
    local changes, will only validate remote files.
    """
    try:
        kitchen = DKCloudCommandRunner.which_kitchen_name()
        if kitchen is None:
            raise click.ClickException("You are not in a Kitchen")
        recipe_dir = DKRecipeDisk.find_recipe_root_dir()
        if recipe_dir is None:
            raise click.ClickException("You must be in a Recipe folder")
        recipe_name = DKRecipeDisk.find_recipe_name()

        if not backend.cfg.get_skip_recipe_checker():
            click.secho("Performing local recipe check...", fg="green")
            DKCLIRecipeChecker(backend.cfg).check_recipe(recipe_dir)
            click.secho("Local recipe check done.")
        click.secho(
            f"{get_datetime()} - Validating recipe/variation {recipe_name}.{variation} in Kitchen {kitchen}",
            fg="green",
        )
        check_and_print(DKCloudCommandRunner.recipe_validate(backend.dki, kitchen, recipe_name, variation))
    except Exception as e:
        handle_exception(e)


@dk.command(name="recipe-variation-list")
@click.option("--kitchen", "-k", type=str, help="kitchen name")
@click.option("--recipe", "-r", type=str, help="recipe name")
@click.pass_obj
def recipe_variation_list(backend: Backend, kitchen: Optional[str], recipe: Optional[str]) -> None:
    """
    Shows the available variations for the current recipe in a kitchen
    """
    try:
        recipe_local = DKRecipeDisk.find_recipe_name()
        if recipe_local is None:
            get_remote = True
            err_str, use_kitchen = Backend.get_kitchen_from_user(kitchen)
            if use_kitchen is None:
                raise click.ClickException(err_str)
            if recipe is None:
                raise click.ClickException("You must be in a recipe folder, or provide a recipe name.")
            use_recipe = Backend.remove_slashes(recipe)
            click.secho("Getting variations from remote ...", fg="green")
        else:
            get_remote = False
            use_recipe = recipe_local
            use_kitchen = DKCloudCommandRunner.which_kitchen_name()
            if use_kitchen is None:
                raise click.ClickException("You are not in a Kitchen")
            click.secho("Getting variations from local ...", fg="green")

        if not DKCloudCommandRunner.kitchen_exists(backend.dki, use_kitchen):
            raise click.ClickException(f"Kitchen {use_kitchen} does not exist. Check spelling.")

        click.secho(
            f"{get_datetime()} - Listing variations for recipe {use_recipe} in Kitchen {use_kitchen}",
            fg="green",
        )
        check_and_print(DKCloudCommandRunner.recipe_variation_list(backend.dki, use_kitchen, use_recipe, get_remote))
    except Exception as e:
        handle_exception(e)


@dk.command(name="recipe-ingredient-list")
@click.pass_obj
def recipe_ingredient_list(backend: Backend) -> None:
    """
    Shows the available ingredients for the current recipe in a kitchen
    """
    try:
        kitchen = DKCloudCommandRunner.which_kitchen_name()
        if kitchen is None:
            raise click.ClickException("You are not in a Kitchen")
        print(kitchen)
        recipe_dir = DKRecipeDisk.find_recipe_root_dir()
        if recipe_dir is None:
            raise click.ClickException("You must be in a Recipe folder")
        recipe_name = DKRecipeDisk.find_recipe_name()

        click.secho(
            f"{get_datetime()} - Listing ingredients for recipe {recipe_name} in Kitchen {kitchen}",
            fg="green",
        )
        check_and_print(DKCloudCommandRunner.recipe_ingredient_list(backend.dki, kitchen, recipe_name))
    except Exception as e:
        handle_exception(e)


# -------------------------------------------------------------------------------------------------
#  File commands
# -------------------------------------------------------------------------------------------------
@dk.command(name="file-diff")
@click.option("--kitchen", "-k", type=str, help="kitchen name")
@click.option("--recipe", "-r", type=str, help="recipe name")
@click.argument("filepath", required=True)
@click.pass_obj
def file_diff(backend: Backend, kitchen: Optional[str], recipe: Optional[str], filepath: str) -> None:
    """
    Show differences with remote version of the file

    """
    try:
        err_str, use_kitchen = Backend.get_kitchen_from_user(kitchen)
        if use_kitchen is None:
            raise click.ClickException(err_str)
        recipe_dir = DKRecipeDisk.find_recipe_root_dir()
        if recipe_dir is None:
            raise click.ClickException("You must be in a Recipe folder")
        if recipe is None:
            recipe = DKRecipeDisk.find_recipe_name()
            if recipe is None:
                raise click.ClickException("You must be in a recipe folder, or provide a recipe name.")

        click.secho(
            f"{get_datetime()} - File Diff for file {filepath}, in Recipe ({recipe}) in Kitchen ({use_kitchen})",
            fg="green",
        )
        check_and_print(DKCloudCommandRunner.file_diff(backend.dki, use_kitchen, recipe, recipe_dir, filepath))
    except Exception as e:
        handle_exception(e)


@dk.command(name="file-merge")
@click.option("--source_kitchen", "-sk", type=str, required=False, help="source (from) kitchen name")
@click.option("--target_kitchen", "-tk", type=str, required=True, help="target (to) kitchen name")
@click.argument("filepath", required=True)
@click.pass_obj
def file_merge(backend: Backend, source_kitchen: Optional[str], target_kitchen: str, filepath: str) -> None:
    """
    To be used after kitchen-merge-preview command.
    Launch the merge tool of choice, to resolve conflicts.
    File path needs to be stated as it is coming from kitchen-merge-preview output

    """
    try:
        recipe_dir = DKRecipeDisk.find_recipe_root_dir()
        if recipe_dir is not None:
            message_1 = "Warning: You are inside a recipe. Please go at least one level above. This command is typically used from the level above kitchen level."
            message_2 = (
                "Keep in mind that the file path needs to be stated as it is coming from kitchen-merge-preview output."
            )
            message_3 = f'i.e. dk file-merge -sk source_kitchen_name -tk target_kitchen_name {os.path.normpath("recipe_name/graph.json")}'
            click.secho(message_1, fg="yellow")
            click.secho(message_2, fg="yellow")
            click.secho(message_3, fg="yellow")
            return

        kitchen = DKCloudCommandRunner.which_kitchen_name()

        if kitchen is None and source_kitchen is None:
            raise click.ClickException("You are not in a Kitchen and did not specify a source_kitchen")

        if kitchen is not None and source_kitchen is not None and kitchen != source_kitchen:
            raise click.ClickException(
                "There is a conflict between the kitchen in which you are, and the source_kitchen you have specified"
            )

        if kitchen is not None:
            use_source_kitchen = kitchen
        else:
            use_source_kitchen = source_kitchen

        click.secho(
            f"{get_datetime()} - File Merge for file {filepath},"
            f" source kitchen ({use_source_kitchen}), target kitchen({target_kitchen})",
            fg="green",
        )
        check_and_print(DKCloudCommandRunner.file_merge(backend.dki, filepath, use_source_kitchen, target_kitchen))
    except Exception as e:
        handle_exception(e)


@dk.command(name="file-resolve")
@click.option("--source_kitchen", "-sk", type=str, required=False, help="source (from) kitchen name")
@click.option("--target_kitchen", "-tk", type=str, required=True, help="target (to) kitchen name")
@click.argument("filepath", required=True)
@click.pass_obj
def file_resolve(backend: Backend, source_kitchen: Optional[str], target_kitchen: str, filepath: str) -> None:
    """
    Mark a conflicted file as resolved, so that a merge can be completed
    File path needs to be stated as it is coming from kitchen-merge-preview output
    """
    try:
        recipe_dir = DKRecipeDisk.find_recipe_root_dir()
        if recipe_dir is not None:
            message_1 = "Warning: You are inside a recipe. Please go at least one level above. This command is typically used from the level above kitchen level."
            message_2 = (
                "Keep in mind that the file path needs to be stated as it is coming from kitchen-merge-preview output."
            )
            message_3 = f'i.e. dk file-resolve -sk source_kitchen_name -tk target_kitchen_name {os.path.normpath("recipe_name/graph.json")}'
            click.secho(message_1, fg="yellow")
            click.secho(message_2, fg="yellow")
            click.secho(message_3, fg="yellow")
            return

        kitchen = DKCloudCommandRunner.which_kitchen_name()
        if kitchen is None and source_kitchen is None:
            raise click.ClickException("You are not in a Kitchen and did not specify a source_kitchen")

        if kitchen is not None and source_kitchen is not None and kitchen != source_kitchen:
            raise click.ClickException(
                "There is a conflict between the kitchen in which you are, and the source_kitchen you have specified"
            )

        if kitchen is not None:
            use_source_kitchen = kitchen
        else:
            use_source_kitchen = source_kitchen

        click.secho(
            f"{get_datetime()} - File resolve for file {filepath}, source kitchen ({use_source_kitchen}), target kitchen({target_kitchen})"
        )
        check_and_print(DKCloudCommandRunner.file_resolve(backend.dki, use_source_kitchen, target_kitchen, filepath))
    except Exception as e:
        handle_exception(e)


@dk.command(name="file-get")
@click.argument("filepath", required=True)
@click.pass_obj
def file_get(backend: Backend, filepath: str) -> None:
    """
    Get the latest version of a file from the server and overwriting your local copy.
    """
    try:
        kitchen = DKCloudCommandRunner.which_kitchen_name()
        if kitchen is None:
            raise click.ClickException("You must be in a Kitchen")
        recipe = DKRecipeDisk.find_recipe_name()
        if recipe is None:
            raise click.ClickException("You must be in a recipe folder.")

        click.secho(
            f"{get_datetime()} - Getting File ({filepath}) to Recipe ({recipe}) in kitchen({kitchen})",
            fg="green",
        )
        check_and_print(DKCloudCommandRunner.get_file(backend.dki, kitchen, recipe, filepath))
    except Exception as e:
        handle_exception(e)


@dk.command(name="file-update")
@click.option("--kitchen", "-k", type=str, help="kitchen name")
@click.option("--recipe", "-r", type=str, help="recipe name")
@click.option("--message", "-m", type=str, required=True, help="change message")
@click.argument("filepaths", required=True, nargs=-1)
@click.pass_obj
def file_update(
    backend: Backend,
    kitchen: Optional[str],
    recipe: Optional[str],
    message: str,
    filepaths: Tuple[str, ...],
) -> None:
    """
    Update a Recipe file.

    Examples:

        \b
        1) update a single file
        dk fu -m "my change" -k myKitchen resources/file001.txt

        \b
        2) update multiple files
        dk fu -m "my change" -k myKitchen resources/file001.txt resources/file002.txt


    """
    try:
        # Check for invalid separators
        invalid_separators = [",", ";", ":"]
        for item in filepaths:
            if any(invalid_separator in item for invalid_separator in invalid_separators):
                error_message = "Files to be updated must be delimited by whitespace (i.e. 'file1.txt file2.txt' as opposed to 'file1.txt,file2.txt')"
                raise click.ClickException(error_message)

        err_str, use_kitchen = Backend.get_kitchen_from_user(kitchen)
        if use_kitchen is None:
            raise click.ClickException(err_str)
        recipe_dir = DKRecipeDisk.find_recipe_root_dir()
        if recipe_dir is None:
            raise click.ClickException("You must be in a Recipe folder")
        if recipe is None:
            recipe = DKRecipeDisk.find_recipe_name()
            if recipe is None:
                raise click.ClickException("You must be in a recipe folder, or provide a recipe name.")

        click.secho(
            f"{get_datetime()} - Updating File(s) ({filepaths}) in Recipe ({recipe}) in Kitchen({use_kitchen}) with message ({message})",
            fg="green",
        )
        check_and_print(
            DKCloudCommandRunner.update_file(backend.dki, use_kitchen, recipe, recipe_dir, message, filepaths)
        )
    except Exception as e:
        handle_exception(e)


@dk.command(name="recipe-update")
@click.option(
    "--delete_remote",
    "-d",
    default=False,
    is_flag=True,
    required=False,
    help="Delete remote files to match local",
)
@click.option("--message", "-m", type=str, required=True, help="change message")
@click.pass_obj
def file_update_all(backend: Backend, message: bool, delete_remote: str) -> None:
    """
    Update all of the changed files for this Recipe
    """
    try:
        kitchen = DKCloudCommandRunner.which_kitchen_name()
        if kitchen is None:
            raise click.ClickException("You must be in a Kitchen")
        recipe_dir = DKRecipeDisk.find_recipe_root_dir()
        if recipe_dir is None:
            raise click.ClickException("You must be in a Recipe folder")
        recipe = DKRecipeDisk.find_recipe_name()

        click.secho(
            f"{get_datetime()} - Updating all changed files in Recipe ({recipe}) in Kitchen({kitchen}) with message ({message})",
            fg="green",
        )
        DKCLIRecipeChecker(backend.cfg).check_recipe(recipe_dir)
        check_and_print(
            DKCloudCommandRunner.update_all_files(
                backend.dki, kitchen, recipe, recipe_dir, message, delete_remote=delete_remote
            )
        )
    except Exception as e:
        handle_exception(e)


@dk.command(name="file-delete")
@click.option("--kitchen", "-k", type=str, help="kitchen name")
@click.option("--recipe", "-r", type=str, help="recipe name")
@click.option("--message", "-m", type=str, required=True, help="change message")
@click.argument("filepath", required=True, nargs=-1)
@click.pass_obj
def file_delete(
    backend: Backend,
    kitchen: Optional[str],
    recipe: Optional[str],
    message: str,
    filepath: Tuple[str, ...],
) -> None:
    """
    Delete one or more Recipe files. If you are not in a recipe path, provide the file path(s)
    relative to the recipe root. Separate multiple file paths with spaces.  File paths need no
    preceding backslash.

    To delete the directory, delete all files in that directory and then the directory will
    automatically be deleted.

    Example...

    dk file-delete -m "my delete message" file1.json dir2/file2.json
    """
    try:
        err_str, use_kitchen = Backend.get_kitchen_from_user(kitchen)
        if use_kitchen is None:
            raise click.ClickException(err_str)
        if recipe is None:
            recipe = DKRecipeDisk.find_recipe_name()
            if recipe is None:
                raise click.ClickException("You must be in a recipe folder, or provide a recipe name.")

        click.secho(
            f"{get_datetime()} - Deleting ({filepath}) in Recipe ({recipe}) in kitchen({use_kitchen}) with message ({message})",
            fg="green",
        )
        check_and_print(DKCloudCommandRunner.delete_file(backend.dki, use_kitchen, recipe, message, filepath))
    except Exception as e:
        handle_exception(e)


# -------------------------------------------------------------------------------------------------
#  Active Serving commands
# -------------------------------------------------------------------------------------------------


@dk.command(name="active-serving-watcher")
@click.option("--kitchen", "-k", type=str, required=False, help="Kitchen name")
@click.option("--interval", "-i", type=int, required=False, default=5, help="watching interval, in seconds")
@click.pass_obj
def active_serving_watcher(backend: Backend, kitchen: Optional[str], interval: int) -> None:
    """
    Watches all cooking Recipes in a Kitchen. Provide the Kitchen name as an argument or be in a
    Kitchen folder. Optionally provide a watching period as an integer, in seconds. Ctrl+C to
    terminate.
    """
    try:
        err_str, use_kitchen = Backend.get_kitchen_from_user(kitchen)
        if use_kitchen is None:
            raise click.ClickException(err_str)
        click.secho(
            f"{get_datetime()} - Watching Active OrderRun Changes in Kitchen {use_kitchen}",
            fg="green",
        )
        DKCloudCommandRunner.watch_active_servings(backend.dki, use_kitchen, interval)
        while True:
            try:
                DKCloudCommandRunner.join_active_serving_watcher_thread_join()
                if not DKCloudCommandRunner.watcher_running():
                    break
            except KeyboardInterrupt:
                print("KeyboardInterrupt")
                exit_gracefully(None, None)
        exit(0)
    except Exception as e:
        handle_exception(e)


# -------------------------------------------------------------------------------------------------
#  Order commands
# -------------------------------------------------------------------------------------------------


@dk.command(name="order-run")
@click.argument("variation", required=True)
@click.option("--kitchen", "-k", type=str, help="kitchen name")
@click.option("--recipe", "-r", type=str, help="recipe name")
@click.option("--node", "-n", type=str, required=False, help="Name of the node to run")
@click.option("--now", "-w", default=False, is_flag=True, required=False, help="Run the order now")
@click.option("--yes", "-y", default=False, is_flag=True, required=False, help="Force yes")
@click.option("--params", "-p", required=False, help="Overrides passed as parameters")
@click.pass_obj
def order_run(
    backend: Backend,
    kitchen: Optional[str],
    recipe: Optional[str],
    variation: str,
    node: Optional[str],
    now: bool,
    yes: bool,
    params: Optional[str],
) -> None:
    """
    Run an order: cook a recipe variation

    Examples:

        \b
        1) run an order
        dk or -y -k myKitchen myVariation

        \b
        2) run an order with just one node
        dk or -y -k myKitchen -n myNode myVariation

        \b
        3) run an order now
        dk or -y --now -k myKitchen myVariation

        \b
        4) run an order with parameters
        dk or -y -k myKitchen -p "{\\"my-key\\":\\"my-value\\"}" myVariation

        \b
        5) run an order with parameters (example using apostrophes)
        dk or -y -k myKitchen -p "{\\"my-key\\":\\"value with 'quoted text'\\"}" myVariation

    Note that:

        \b
        if a node is selected, as in example 2, variation's schedule will be overridden and the
        node will be executed immediately.

        \b
        In examples 4 and 5, variable 'my-key' will be added to the running order, and will have
        highest precedence in case variable already exists in the recipe.
    """
    try:
        err_str, use_kitchen = Backend.get_kitchen_from_user(kitchen)
        if use_kitchen is None:
            raise click.ClickException(err_str)
        if recipe is None:
            recipe = DKRecipeDisk.find_recipe_name()
            if recipe is None:
                raise click.ClickException("You must be in a recipe folder, or provide a recipe name.")

        if not yes:
            confirm = input(
                f"Kitchen {use_kitchen}, Recipe {recipe}, Variation {variation}.\n"
                "Are you sure you want to run an Order? [yes/No]"
            )
            if confirm.lower() != "yes":
                return

        msg = f"{get_datetime()} - Create an Order:\n\tKitchen: {use_kitchen}\n\tRecipe: {recipe}\n\tVariation: {variation}\n"
        if node is not None:
            msg += f"\tNode: {node}\n"

        click.secho(msg, fg="green")

        params_json = _parse_params(params)

        check_and_print(
            DKCloudCommandRunner.create_order(backend.dki, use_kitchen, recipe, variation, node, params_json, now)
        )
    except Exception as e:
        handle_exception(e)


def _parse_params(params: str) -> Optional[JSONData]:
    if params:
        if params[0] == "@":
            with open(params, "r") as f:
                return json.load(f)
        else:
            try:
                return json.loads(params)
            except Exception as e:
                raise click.ClickException(
                    "Invalid parameters format, they must be a file reference or a well formatted JSON string"
                )
                pass
    return None


@dk.command(name="order-delete")
@click.option("--kitchen", "-k", type=str, default=None, help="kitchen name")
@click.option("--order_id", "-o", type=str, default=None, help="Order ID")
@click.option("--yes", "-y", default=False, is_flag=True, required=False, help="Force yes")
@click.pass_obj
def order_delete(backend: Backend, kitchen: Optional[str], order_id: Optional[str], yes: bool) -> None:
    """
    Delete one order or all orders in a kitchen
    """
    try:
        use_kitchen = Backend.get_kitchen_name_soft(kitchen)
        print(use_kitchen)
        if use_kitchen is None:
            raise click.ClickException("You must specify either a kitchen or be in a kitchen directory")

        if not yes:
            if order_id is None:
                confirm = input(f"Are you sure you want to delete all Orders in kitchen {use_kitchen}? [yes/No]")
            else:
                confirm = input(f"Are you sure you want to delete Order {order_id}? [yes/No]")
            if confirm.lower() != "yes":
                return

        if order_id is not None:
            click.secho(f"{get_datetime()} - Delete an Order using id {order_id}", fg="green")
            check_and_print(DKCloudCommandRunner.delete_one_order(backend.dki, use_kitchen, order_id))
        else:
            click.secho(f"{get_datetime()} - Delete all orders in Kitchen {use_kitchen}", fg="green")
            check_and_print(DKCloudCommandRunner.delete_all_order(backend.dki, use_kitchen))
    except Exception as e:
        handle_exception(e)


@dk.command(name="order-pause")
@click.option("--kitchen", "-k", type=str, default=None, help="kitchen name")
@click.option("--order_id", "-o", type=str, required=True, help="Order ID")
@click.option("--yes", "-y", default=False, is_flag=True, required=False, help="Force yes")
@click.pass_obj
def order_pause(backend: Backend, order_id: str, kitchen: Optional[str], yes: bool) -> None:
    """
    Pause an order - No further order runs will be generated.
    Order runs already in progress are unaffected.
    You can revert this command using: order-unpause
    """
    try:
        use_kitchen = Backend.get_kitchen_name_soft(kitchen)
        if use_kitchen is None:
            raise click.ClickException("You must specify either a kitchen or be in a kitchen directory")

        if order_id is None:
            raise click.ClickException(f"invalid order id {order_id}")

        if not yes:
            confirm = input(f"Are you sure you want to pause Order {order_id}? [yes/No]")
            if confirm.lower() != "yes":
                return

        click.secho(f"{get_datetime()} - Pause order id {order_id}", fg="green")
        check_and_print(DKCloudCommandRunner.pause_order(backend.dki, use_kitchen, order_id))
    except Exception as e:
        handle_exception(e)


@dk.command(name="order-unpause")
@click.option("--kitchen", "-k", type=str, default=None, help="kitchen name")
@click.option("--order_id", "-o", type=str, required=True, help="Order ID")
@click.option("--yes", "-y", default=False, is_flag=True, required=False, help="Force yes")
@click.pass_obj
def order_unpause(backend: Backend, order_id: str, kitchen: Optional[str], yes: bool) -> None:
    """
    Unpause an order.
    After unpausing, order runs will be generated as expected (per schedule).
    """
    try:
        use_kitchen = Backend.get_kitchen_name_soft(kitchen)
        if use_kitchen is None:
            raise click.ClickException("You must specify either a kitchen or be in a kitchen directory")

        if order_id is None:
            raise click.ClickException(f"invalid order id {order_id}")

        if not yes:
            confirm = input(f"Are you sure you want to unpause Order {order_id}? [yes/No]")
            if confirm.lower() != "yes":
                return

        click.secho(f"{get_datetime()} - Unpause order id {order_id}", fg="green")
        check_and_print(DKCloudCommandRunner.unpause_order(backend.dki, use_kitchen, order_id))
    except Exception as e:
        handle_exception(e)


@dk.command(name="order-stop")
@click.option("--kitchen", "-k", type=str, default=None, help="kitchen name")
@click.option("--order_id", "-o", type=str, required=True, help="Order ID")
@click.option("--yes", "-y", default=False, is_flag=True, required=False, help="Force yes")
@click.pass_obj
def order_stop(backend: Backend, order_id: str, kitchen: Optional[str], yes: bool) -> None:
    """
    Stop an order - Turn off the serving generation ability of an order.  Stop any running jobs.
    Keep all state around.
    """
    try:
        use_kitchen = Backend.get_kitchen_name_soft(kitchen)
        if use_kitchen is None:
            raise click.ClickException("You must specify either a kitchen or be in a kitchen directory")

        if order_id is None:
            raise click.ClickException(f"invalid order id {order_id}")

        if not yes:
            confirm = input(f"Are you sure you want to stop Order {order_id}? [yes/No]")
            if confirm.lower() != "yes":
                return

        click.secho(f"{get_datetime()} - Stop order id {order_id}", fg="green")
        check_and_print(DKCloudCommandRunner.stop_order(backend.dki, use_kitchen, order_id))
    except Exception as e:
        handle_exception(e)


@dk.command(name="orderrun-stop")
@click.option("--kitchen", "-k", type=str, help="kitchen name")
@click.option("--order_run_id", "-ori", type=str, required=True, help="OrderRun ID")
@click.option("--yes", "-y", default=False, is_flag=True, required=False, help="Force yes")
@click.pass_obj
def orderrun_stop(backend: Backend, kitchen: Optional[str], order_run_id: str, yes: bool) -> None:
    """
    Stop the run of an order - Stop the running order and keep all state around.
    """
    try:
        use_kitchen = Backend.get_kitchen_name_soft(kitchen)
        if use_kitchen is None:
            raise click.ClickException("You must specify either a kitchen or be in a kitchen directory")

        if order_run_id is None:
            raise click.ClickException(f"invalid order run id {order_run_id}")

        if not yes:
            confirm = input(f"Are you sure you want to stop Order-Run {order_run_id}? [yes/No]")
            if confirm.lower() != "yes":
                return

        click.secho(f"{get_datetime()} - Stop order run id {order_run_id}", fg="green")
        check_and_print(DKCloudCommandRunner.stop_orderrun(backend.dki, use_kitchen, order_run_id.strip()))
    except Exception as e:
        handle_exception(e)


@dk.command(name="orderrun-info")
@click.option("--kitchen", "-k", type=str, help="kitchen name")
@click.option("--order_id", "-o", type=str, default=None, help="Order ID")
@click.option("--order_run_id", "-ori", type=str, default=None, help="OrderRun ID to display")
@click.option(
    "--summary",
    "-s",
    default=False,
    is_flag=True,
    required=False,
    help="display run summary information",
)
@click.option(
    "--nodestatus",
    "-ns",
    default=False,
    is_flag=True,
    required=False,
    help=" display node status info",
)
@click.option("--full_log", "-fl", default=False, is_flag=True, required=False, help="display full logs")
@click.option("--log", "-l", default=False, is_flag=True, required=False, help="display log info")
@click.option(
    "--log_threshold",
    "-lt",
    type=str,
    default="INFO",
    required=False,
    help="Log display threshold. Can be ERROR, WARN, INFO, DEBUG, TRACE. Default value is INFO. This does not affect full_log",
)
@click.option("--timing", "-t", default=False, is_flag=True, required=False, help="display timing results")
@click.option("--test", "-q", default=False, is_flag=True, required=False, help="display test results")
@click.option(
    "--runstatus",
    default=False,
    is_flag=True,
    required=False,
    help=" display status of the run (single line)",
)
@click.option(
    "--disp_order_id",
    default=False,
    is_flag=True,
    required=False,
    help=" display the order id (single line)",
)
@click.option(
    "--disp_orderrun_id",
    default=False,
    is_flag=True,
    required=False,
    help=" display order run id (single line)",
)
@click.option(
    "--all_things",
    "-at",
    default=False,
    is_flag=True,
    required=False,
    help="display all information",
)
# @click.option('--recipe', '-r', type=str, help='recipe name')
@click.pass_obj
def orderrun_detail(
    backend: Backend,
    kitchen: Optional[str],
    summary: bool,
    nodestatus: bool,
    runstatus: bool,
    full_log: bool,
    log: bool,
    log_threshold: str,
    timing: bool,
    test: bool,
    all_things: bool,
    order_id: Optional[str],
    order_run_id: Optional[str],
    disp_order_id: bool,
    disp_orderrun_id: bool,
) -> None:
    """
    Display information about an Order-Run
    """
    try:
        err_str, use_kitchen = Backend.get_kitchen_from_user(kitchen)
        if use_kitchen is None:
            raise click.ClickException(err_str)
        # if recipe is None:
        #     recipe = DKRecipeDisk.find_recipe_name()
        #     if recipe is None:
        #         raise click.ClickException(
        #         'You must be in a recipe folder, or provide a recipe name.')
        pd = dict()
        if all_things:
            pd["summary"] = True
            pd["logs"] = True
            pd["timingresults"] = True
            pd["testresults"] = True
            # pd['state'] = True
            pd["status"] = True
        if summary:
            pd["summary"] = True
        if log:
            pd["logs"] = True
        if timing:
            pd["timingresults"] = True
        if test:
            pd["testresults"] = True
        if nodestatus:
            pd["status"] = True

        if runstatus:
            pd["runstatus"] = True
        if disp_order_id:
            pd["disp_order_id"] = True
        if disp_orderrun_id:
            pd["disp_orderrun_id"] = True

        # if the user does not specify anything to display, show the summary information
        if (
            not runstatus
            and not all_things
            and not test
            and not timing
            and not log
            and not nodestatus
            and not summary
            and not disp_order_id
            and not disp_orderrun_id
        ):
            pd["summary"] = True

        if order_id is not None and order_run_id is not None:
            raise click.ClickException("Cannot specify both the Order Id and the OrderRun Id")
        if order_id is not None:
            pd["serving_book_hid"] = order_id.strip()
        elif order_run_id is not None:
            pd["serving_hid"] = order_run_id.strip()

        log_threshold_options = {"ERROR", "INFO", "DEBUG", "TRACE"}
        if log_threshold not in log_threshold_options:
            log_threshold_options_str = "ERROR, INFO, DEBUG, TRACE"
            raise click.ClickException(f"log_threshold needs to be one of this options: {log_threshold_options_str}")

        # don't print the green thing if it is just runstatus
        if not runstatus and not disp_order_id and not disp_orderrun_id:
            backend.cfg.print_current_context()
            click.secho(
                f"{get_datetime()} - Display Order-Run details from kitchen {use_kitchen}",
                fg="green",
            )
        check_and_print(
            DKCloudCommandRunner.orderrun_detail(
                backend.dki, use_kitchen, pd, full_log=full_log, log_threshold=log_threshold
            )
        )
    except Exception as e:
        if not runstatus and not disp_order_id and not disp_orderrun_id:
            handle_exception(e)
        else:
            click.echo("UNKNOWN")


@dk.command("orderrun-delete")
@click.argument("orderrun_id", required=True)
@click.option("--yes", "-y", default=False, is_flag=True, required=False, help="Force yes")
@click.option("--kitchen", "-k", type=str, help="kitchen name")
@click.pass_obj
def delete_orderrun(backend: Backend, orderrun_id: str, kitchen: Optional[str], yes: bool) -> None:
    """
    Delete the orderrun specified by the argument.
    """
    try:
        use_kitchen = Backend.get_kitchen_name_soft(kitchen)
        if use_kitchen is None:
            raise click.ClickException("You must specify either a kitchen or be in a kitchen directory")

        if orderrun_id is None:
            raise click.ClickException(f"invalid order id {orderrun_id}")

        if not yes:
            confirm = input(f"Are you sure you want to delete Order-Run  {orderrun_id}? [yes/No]")
            if confirm.lower() != "yes":
                return

        click.secho(f"{get_datetime()} - Deleting orderrun {orderrun_id}", fg="green")
        check_and_print(DKCloudCommandRunner.delete_orderrun(backend.dki, use_kitchen, orderrun_id.strip()))
    except Exception as e:
        handle_exception(e)


@dk.command("orderrun-resume")
@click.argument("orderrun_id", required=True)
@click.option("--kitchen", "-k", type=str, help="kitchen name")
@click.option("--yes", "-y", default=False, is_flag=True, required=False, help="Force yes")
@click.pass_obj
def order_resume(backend: Backend, orderrun_id: str, kitchen: Optional[str], yes: bool) -> None:
    """
    Resumes a failed order run
    """
    try:
        use_kitchen = Backend.get_kitchen_name_soft(kitchen)
        if use_kitchen is None:
            raise click.ClickException("You must specify either a kitchen or be in a kitchen directory")

        if orderrun_id is None:
            raise click.ClickException(f"invalid order id {orderrun_id}")

        if not yes:
            confirm = input(f"Are you sure you want to resume Order-Run {orderrun_id}? [yes/No]")
            if confirm.lower() != "yes":
                return

        click.secho(f"{get_datetime()} - Resuming Order-Run {orderrun_id}", fg="green")
        check_and_print(DKCloudCommandRunner.order_resume(backend.dki, use_kitchen, orderrun_id.strip()))
    except Exception as e:
        handle_exception(e)


@dk.command(name="order-list")
@click.option("--kitchen", "-k", type=str, required=False, help="Filter results for kitchen only")
@click.option("--start", "-s", type=int, required=False, default=0, help="Start offset for displaying orders")
@click.option("--order_count", "-oc", type=int, required=False, default=5, help="Number of orders to display")
@click.option(
    "--order_run_count",
    "-orc",
    type=int,
    required=False,
    default=3,
    help="Number of order runs to display, for each order",
)
@click.option(
    "--recipe",
    "-r",
    type=str,
    required=False,
    default=None,
    help="Filter results for this recipe only",
)
@click.pass_obj
def order_list(
    backend: Backend,
    kitchen: Optional[str],
    order_count: int,
    order_run_count: int,
    start: int,
    recipe: Optional[str],
) -> None:
    """
    List Orders in a Kitchen.

    Examples:

    1) Basic usage with no paging, 5 orders, 3 order runs per order.

    dk order-list

    2) Get first, second and third page, ten orders per page, two order runs per order.

    dk order-list --start 0  --order_count 10 --order_run_count 2

    dk order-list --start 10 --order_count 10 --order_run_count 2

    dk order-list --start 20 --order_count 10 --order_run_count 2

    3) Get first five orders per page, two order runs per order, for recipe recipe_name

    dk order-list --recipe recipe_name --order_count 5 --order_run_count 2

    """
    try:
        err_str, use_kitchen = Backend.get_kitchen_from_user(kitchen)
        if use_kitchen is None:
            raise click.ClickException(err_str)

        if order_count <= 0:
            raise click.ClickException("order_count must be an integer greater than 0")

        if order_run_count <= 0:
            raise click.ClickException("order_count must be an integer greater than 0")

        click.secho(f"{get_datetime()} - Get Order information for Kitchen {use_kitchen}", fg="green")

        check_and_print(
            DKCloudCommandRunner.list_order(
                backend.dki, use_kitchen, order_count, order_run_count, start, recipe=recipe
            )
        )
    except Exception as e:
        handle_exception(e)


# -------------------------------------------------------------------------------------------------
#  Vault commands
# -------------------------------------------------------------------------------------------------


@dk.command(name="vault-info")
@click.option("--kitchen", "-k", required=False, help="Kitchen name")
@click.option("--global-secrets", "-g", is_flag=True, required=False, help="list global secrets")
@click.pass_obj
def vault_info(backend: Backend, global_secrets: bool, kitchen: Optional[str]) -> None:
    """
    List vault info

    Examples:

        \b
        1) Get global vault info
        dk vault-info

        \b
        2) Get kitchen specific vault info
        dk vault-info -k my-kitchen

        \b
        3) Get kitchen specific and global vault info
        dk vault-info -g -k my-kitchen

    """
    try:
        if not kitchen:
            global_secrets = True
        click.echo(click.style(f"{get_datetime()} - Getting the vault info", fg="green"))
        click.echo(DKCloudCommandRunner.vault_info(backend.dki, global_secrets, kitchen))
    except Exception as e:
        handle_exception(e)


@dk.command(name="vault-config")
@click.option("--kitchen", "-k", required=False, help="Kitchen name")
@click.option(
    "--inherit",
    "-h",
    default=False,
    is_flag=True,
    required=False,
    help="Configuration inherited from parent kitchen",
)
@click.option("--service", "-s", required=False, help="Service can be custom or default")
@click.option("--url", "-u", required=False, help="Vault url (with port)")
@click.option("--token", "-t", required=False, help="Vault token")
@click.option("--prefix", "-r", required=False, help="Vault prefix, if exist")
@click.option("--private", "-p", default="False", required=False, help="Whether vault is private or not")
@click.option(
    "--inheritable",
    "-i",
    default="False",
    required=False,
    help="Whether vault Values are Inheritable or not",
)
@click.option("--disable", "-d", default=False, is_flag=True, required=False, help="Disable global vault")
@click.option("--yes", "-y", default=False, is_flag=True, required=False, help="Force yes")
@click.pass_obj
def vault_config(
    backend: Backend,
    kitchen: Optional[str],
    inherit: bool,
    service: Optional[str],
    url: Optional[str],
    token: Optional[str],
    prefix: Optional[str],
    private: str,  # TODO:  This should be a flag/bool, right?
    inheritable: str,  # TODO:  This should be a flag/bool, right?
    disable: bool,
    yes: bool,
) -> None:
    """
    Configure vault. Your role must be "IT" or "ADMIN" to run global vault configuration.

    Examples:

        \b
        1a) Global vault config
        dk vault-config --url http://dummy-vault-url:8200 --token my-vault-token

        \b
        1b) Global vault config: disable
        dk vault-config --disable

        \b
        2) Kitchen vault config with default service
        dk vault-config --kitchen my-kitchen --service default

        \b
        3) Kitchen vault config with configuration inherited from parent
        dk vault-config --kitchen my-kitchen --inherit

        \b
        4) Kitchen vault config with custom service
        dk vault-config --kitchen my-kitchen \\
            --prefix my-kitchen-prefix \\
            --private True \\
            --service custom \\
            --token my-vault-token \\
            --inheritable True \\
            --url http://dummy-vault-url:8200

        \b
        Note: To continue the command in next line, use
            \\ (in Linux)
            or
            ^ (in Windows)

    """
    try:
        for item in [private, inheritable]:
            error_message = 'private and inheritable need to be set to "True" or "False"'
            if item.lower() not in ["true", "false"]:
                raise click.ClickException(error_message)

        if not kitchen and not (backend.dki.is_user_role("IT") or backend.dki.is_user_role("ADMIN")):
            raise click.ClickException("You do not have IT or ADMIN privileges to run this command for global vault.")

        param_dict = {
            "service": service if service else "default",
            "url": url if url else "",
            "token": token if token else "",
            "prefix": prefix if prefix else "",
            "private": True if private.lower() == "true" else False,
            "inheritable": True if inheritable.lower() == "true" else False,
        }

        if param_dict["service"] not in set(["default", "custom"]):
            raise click.ClickException('service needs to be either "default" or "custom"')

        # Global configuration checks
        if not kitchen:
            if service == "custom":
                raise click.ClickException('--service "custom" does not apply for global vault config')

            if not disable and not url and not token:
                raise click.ClickException("You need to configure url and token to proceed.")

            if not yes:
                message = "You are configuring the global vault!. Are you sure you want to proceed? [yes/No]"
                confirm = input(message)
                if confirm.lower() != "yes":
                    return

            if disable:
                param_dict = {"disabled": disable}

        # Kitchen configuration checks
        if kitchen:
            if disable:
                raise click.ClickException("Kitchen vault cannot be disabled. Check vault-delete command instead.")
            if inherit:
                if any(
                    [
                        service,
                        url,
                        token,
                        prefix,
                        private.lower() == "true",
                        inheritable.lower() == "true",
                    ]
                ):
                    raise click.ClickException(
                        "When inherit is selected: service, url, token, prefix, private and inheritable cannot be set."
                    )

                try:
                    DKCloudCommandRunner.vault_delete(backend.dki, kitchen)
                except Exception as e:
                    if "No configuration exists" not in str(e):
                        raise e

                click.echo("Done.")
                return

            if service == "default":
                if any([url, token, prefix, private.lower() == "true", inheritable.lower() == "true"]):
                    raise click.ClickException(
                        "When service is default: url, token, prefix, private and inheritable cannot be set."
                    )

        click.echo(click.style(f"{get_datetime()} - Setting the vault info", fg="green"))
        click.echo(DKCloudCommandRunner.vault_config(backend.dki, kitchen, param_dict))
    except Exception as e:
        handle_exception(e)


@dk.command(name="vault-delete")
@click.option("--kitchen", "-k", required=True, help="Kitchen name")
@click.option("--yes", "-y", default=False, is_flag=True, required=False, help="Force yes")
@click.pass_obj
def vault_delete(backend: Backend, kitchen: str, yes: bool):
    """
    Delete kitchen vault configuration.

    Example:

        \b
        dk vault-delete -k my-kitchen
    """
    try:
        if not yes:
            confirm = input(
                f"You are deleting kitchen vault config for kitchen {kitchen}!."
                " Are you sure you want to proceed? [yes/No]"
            )
            if confirm.lower() != "yes":
                return

        click.echo(
            click.style(
                f"{get_datetime()} - Deleting the vault configuration for kitchen {kitchen}",
                fg="green",
            )
        )
        click.echo(DKCloudCommandRunner.vault_delete(backend.dki, kitchen))
    except Exception as e:
        handle_exception(e)


# --------------------------------------------------------------------------------------------------------------------
#  Secret commands
# --------------------------------------------------------------------------------------------------------------------
@dk.command(name="secret-list")
@click.option("--kitchen", "-k", required=False, help="Kitchen name")
@click.option("--global-secrets", "-g", is_flag=True, required=False, help="list global secrets")
@click.argument("path", required=False)
@click.pass_obj
def secret_list(backend: Backend, path: Optional[str], global_secrets: bool, kitchen: Optional[str]) -> None:
    """
    List Secrets

    Examples:

        \b
        1) List all global Secrets
        dk secret-list

        \b
        2) List all global Secrets starting for a given secret path
        dk secret-list path

        \b
        3) List Secrets related to a specific kitchen
        dk secret-list -k my-kitchen

        \b
        4) List Secrets related to a specific kitchen, but include global secrets as well
        dk secret-list -k my-kitchen -g

        \b
        5) List Secrets related to a specific kitchen, but include global secrets as well, provide a path
        dk secret-list -k my-kitchen -g sftp/

    """
    try:
        DKCloudCommandRunner.check_secret_path(path)

        if not kitchen:
            global_secrets = True
        click.echo(click.style(f"{get_datetime()} - Getting the list of secrets", fg="green"))
        click.echo(DKCloudCommandRunner.secret_list(backend.dki, path, global_secrets, kitchen))
    except Exception as e:
        handle_exception(e)


@dk.command(name="secret-write")
@click.argument("entry", required=True)
@click.option("--kitchen", "-k", required=False, help="Kitchen name")
@click.option("--yes", "-y", default=False, is_flag=True, required=False, help="Force yes")
@click.pass_obj
def secret_write(backend: Backend, entry: str, yes: bool, kitchen: Optional[str]):
    """
    Write one secret to the Vault. Spaces are not allowed.

    Examples:

        \b
        1) Write global Secret my-key
        dk secret-write my-key=my-value

        \b
        2) Write kitchen specific Secret my-key
        dk secret-write -k my-kitchen my-key=my-value

        \b
        3) Write Secret my-key with file as value
        dk secret-write my-key=@example-file.pem


    """
    try:
        path, value = entry.split("=")
        DKCloudCommandRunner.check_secret_path(path)

        if value.startswith("@"):
            value = DKFileHelper.read_file(value[1:])

        secret_exists, _ = DKCloudCommandRunner.secret_exists(backend.dki, path, kitchen)

        if kitchen and not DKCloudCommandRunner.is_vault_config_writable(backend.dki, kitchen):
            raise click.ClickException(f"No vault service configured for kitchen {kitchen}, or vault is read only.")

        # If secret already exists, prompt confirmation message
        if secret_exists:
            if not yes:
                confirm = input(f"Are you sure you want to overwrite the existing Vault Secret {path} ? [yes/No]")
                if confirm.lower() != "yes":
                    return

        click.echo(click.style(f"{get_datetime()} - Writing secret", fg="green"))
        check_and_print(DKCloudCommandRunner.secret_write(backend.dki, path, value, kitchen))
    except Exception as e:
        handle_exception(e)


@dk.command(name="secret-delete")
@click.argument("path", required=True)
@click.option("--kitchen", "-k", required=False, help="Kitchen name")
@click.option("--yes", "-y", default=False, is_flag=True, required=False, help="Force yes")
@click.pass_obj
def secret_delete(backend: Backend, path: str, kitchen: Optional[str], yes: bool) -> None:
    """
    Delete a secret

    Examples:

        \b
        1) Delete global Secret my-key
        dk secret-delete my-key

        \b
        2) Delete kitchen specific Secret my-key
        dk secret-delete -k my-kitchen my-key

    """
    try:
        if path is None:
            raise click.ClickException(f"invalid path {path}")
        DKCloudCommandRunner.check_secret_path(path)

        if kitchen and not DKCloudCommandRunner.is_vault_config_writable(backend.dki, kitchen):
            raise click.ClickException(f"No vault service configured for kitchen {kitchen}, or vault is read only.")

        if not yes:
            confirm = input(f"Are you sure you want to delete Secret {path}? [yes/No]")
            if confirm.lower() != "yes":
                return

        click.echo(click.style(f"{get_datetime()} - Deleting secret", fg="green"))
        check_and_print(DKCloudCommandRunner.secret_delete(backend.dki, path, kitchen))
    except Exception as e:
        handle_exception(e)


@dk.command(name="secret-exists")
@click.option("--kitchen", "-k", required=False, help="Kitchen name")
@click.argument("path", required=True)
@click.pass_obj
def secret_exists(backend: Backend, path: str, kitchen: Optional[str]) -> None:
    """
    Checks if a secret exists

    Examples:

        \b
        1) Delete global secret my-key
        dk secret-exists my-key

        \b
        2) Delete kitchen specific secret my-key
        dk secret-exists -k my-kitchen my-key

    """
    try:
        DKCloudCommandRunner.check_secret_path(path)
        if kitchen:
            message = f"{get_datetime()} Checking secret in kitchen vault {kitchen}"
        else:
            message = f"{get_datetime()} Checking secret in global vault"
        click.echo(click.style(message, fg="green"))
        _, output_message = DKCloudCommandRunner.secret_exists(backend.dki, path, kitchen)
        click.echo(output_message)
    except Exception as e:
        handle_exception(e)


@dk.command(name="kitchen-settings-get")
@click.pass_obj
def kitchen_settings_get(backend: Backend) -> None:
    """
    Get Kitchen Settings (kitchen-settings.json) for your customer account.
    This file is global to all Kitchens.  Your role must be "IT" or "ADMIN" to get
    the kitchen-settings.json file.
    """
    try:
        if not (backend.dki.is_user_role("IT") or backend.dki.is_user_role("ADMIN")):
            raise click.ClickException("You do not have IT or ADMIN privileges to run this command")

        kitchen = "master"

        click.secho(f"{get_datetime()} - Getting a local copy of kitchen-settings.json", fg="green")
        check_and_print(DKCloudCommandRunner.kitchen_settings_get(backend.dki, kitchen))
    except Exception as e:
        handle_exception(e)


@dk.command(name="kitchen-settings-update")
@click.argument("filepath", required=True, nargs=-1)
@click.pass_obj
def kitchen_settings_update(backend: Backend, filepath: Tuple[str, ...]) -> None:
    """
    Upload Kitchen Settings (kitchen-settings.json) for your customer account.
    This file is global to all Kitchens.  Your role must be "IT" or "ADMIN" to upload
    the kitchen-settings.json file.
    """
    try:
        if not (backend.dki.is_user_role("IT") or backend.dki.is_user_role("ADMIN")):
            raise click.ClickException("You do not have IT or ADMIN privileges to run this command")

        kitchen = "master"

        click.secho(f"{get_datetime()} - Updating the settings", fg="green")
        check_and_print(DKCloudCommandRunner.kitchen_settings_update(backend.dki, kitchen, filepath))
    except Exception as e:
        handle_exception(e)


def _get_repo_root_dir(directory: Optional[str]) -> Optional[str]:
    if not directory or directory == "/":
        return None
    elif os.path.isdir(os.path.join(directory, ".git")):
        return directory

    parent, _ = os.path.split(directory)
    return _get_repo_root_dir(parent)


def _install_hooks(hooks_dir: str) -> None:
    for hook in HOOK_FILES:
        pre_commit_file = os.path.join(hooks_dir, hook)
        DKFileHelper.write_file(pre_commit_file, GITHOOK_TEMPLATE)

        os.chmod(pre_commit_file, stat.S_IXUSR | stat.S_IRUSR | stat.S_IWUSR)


def _setup_user(config: DKCloudCommandConfig) -> None:
    import subprocess

    user = config.get_username()
    subprocess.check_output(["git", "config", "--local", "user.name", user])
    subprocess.check_output(["git", "config", "--local", "user.email", user])


@dk.command(name="git-setup")
@click.pass_obj
def git_setup(backend: Backend) -> None:
    """
    Set up a GIT repository for DK CLI.
    """
    repo_root_dir = _get_repo_root_dir(os.getcwd())

    if not repo_root_dir:
        raise click.ClickException("You are not in a git repository")

    hooks_dir = os.path.join(repo_root_dir, ".git", "hooks")

    _install_hooks(hooks_dir)
    _setup_user(backend.dki.get_config())


# http://stackoverflow.com/questions/18114560/python-catch-ctrl-c-command-prompt-really-want-to-quit-y-n-resume-executi
def exit_gracefully(signum, frame) -> None:
    global ORIGINAL_SIGINT
    # restore the original signal handler as otherwise evil things will happen
    # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
    DKCloudCommandRunner.stop_watcher()
    signal(SIGINT, ORIGINAL_SIGINT)
    question = False
    if question is True:
        try:
            if input("\nReally quit? (y/n)> ").lower().startswith("y"):
                exit(1)
        except (KeyboardInterrupt, SystemExit):
            print("Ok, quitting")
            exit(1)
    else:
        print("Ok, quitting now")
        DKCloudCommandRunner.join_active_serving_watcher_thread_join()
        exit(1)
    # restore the exit gracefully handler here
    signal(SIGINT, exit_gracefully)


# https://chriswarrick.com/blog/2014/09/15/python-apps-the-right-way-entry_points-and-scripts/
def main(args=None) -> None:
    global ORIGINAL_SIGINT

    if args is None:
        args = sys.argv[1:]
        Backend(only_check_version=True)  # force to check version

    # store the original SIGINT handler
    ORIGINAL_SIGINT = getsignal(SIGINT)
    signal(SIGINT, exit_gracefully)

    dk(prog_name="dk")


if __name__ == "__main__":

    exit_if_python2()
    main()
