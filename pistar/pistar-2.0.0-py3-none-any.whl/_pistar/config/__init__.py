"""
this file is the entry of the framework. it defines the config, pluginmanager to manage the hook function and args.
The code implementation refers to pytest.
"""
import argparse
import enum
import os
import sys
from pathlib import Path
from typing import Optional, Union, List
from pluggy import PluginManager
from _pistar.config import hookspec as pistar_spec
from _pistar.utilities.argument_parser import ArgumentParser
from _pistar.utilities.auto_generate import generate_file
from _pistar.utilities.exceptions import UsageError

builtin_plugins = ("config.cmdline", "main", "console", "ide")


class COMMANDS:
    GENERATE = "generate"
    EXECUTE = "run"
    COLLECT = "collect"


class ExitCode(enum.IntEnum):
    """Exit Code for PiStar."""

    #: run successfully.
    OK = 0
    #: misused.
    USAGE_ERROR = 4


class PiStarPluginManager(PluginManager):
    """
    the pistarpluginmanager is used to manage registration of plugin
    and offer the function to register and call the hook.
    """

    def __init__(self):
        super().__init__("pistar")
        self.add_hookspecs(pistar_spec)

    def parse_hookimpl_opts(self, plugin, name: str):
        if not name.startswith("pistar_"):
            return None

        return super().parse_hookimpl_opts(plugin, name)

    def import_plugin(self, modname: str) -> None:
        if self.is_blocked(modname) or self.get_plugin(modname) is not None:
            return
        import_spec = "_pistar." + modname if modname in builtin_plugins else modname

        try:
            __import__(import_spec)
        except ImportError as e:
            raise ImportError(f"Error importing plugin {modname}: {str(e.args[0])}").with_traceback(
                e.__traceback__) from e
        else:
            mod = sys.modules[import_spec]
            self.register(mod, modname)


class Config:
    """
    Access to configuration values, pluginmanager and plugin hooks.
    todo:realize this class.
    """

    def __init__(self, pluginmanager: PiStarPluginManager,
                 args: Optional[Union[List[str], "os.PathLike[str]"]]):
        self._generate_command = None
        self._run_command = None
        self.pluginmanager = pluginmanager
        self.hook = self.pluginmanager.hook
        self.parser = ArgumentParser(
            prog="pistar", usage="pistar [options] <command> <args>")
        self._subparser = self.parser.add_subparsers(
            dest="command", metavar="")
        self.parser.add_argument("-v", "--version", action="store_true", help="Show the version of pistar")
        self._run_command = self._subparser.add_parser(name=COMMANDS.EXECUTE, prog="pistar run",
                                                       usage="pistar run [options] files_or_dir",
                                                       help="Execute test cases")
        self._generate_command = self._subparser.add_parser(name=COMMANDS.GENERATE,
                                                            usage="pistar generate [options]",
                                                            help="Generate interface test cases")
        self._rootpath = Path.cwd().absolute()
        self.option = argparse.Namespace()
        self.arguments = None
        self.option_arguments = set()
        self.__add_generate_option()

    def add_option(self, *args, **kwargs):
        """add option for parser argument"""
        conflict = set(args).intersection(self.option_arguments)
        if conflict:
            raise ValueError("option names %s already added" % conflict)
        try:
            self._run_command.add_argument(*args, **kwargs)
            self.option_arguments.update(args)
        except ValueError as e:
            raise ValueError("option names %s already added" % args) from e

    def get_option(self, name):
        """get opttion value by args name"""
        try:
            return self.option.__getattribute__(name)
        except ValueError as e:
            raise ValueError("option names %s not added" % name) from e

    @property
    def rootpath(self) -> Path:
        """The directory from which :func:`pistar.main` was invoked (work directory)."""
        return self._rootpath

    @property
    def outpath(self) -> Path:
        """The path to store cases output."""
        return Path(self.option.output).absolute()

    @property
    def args(self) -> List[str]:
        """The input file or dir list"""
        return self.option.files_or_dir

    @property
    def subcommand(self):
        return self.option.command

    @property
    def collectonly(self) -> bool:
        return self.option.collectonly

    @property
    def version(self):
        return self.option.version

    @property
    def debug(self) -> bool:
        return self.option.debug

    @property
    def no_color(self):
        return self.option.nocolor

    def __add_generate_option(self):
        self._generate_command.add_argument(
            "-i",
            "--interface",
            action="store",
            type=str,
            required=True,
            metavar="",
            help="Specify an OpenAPI definition file by swagger yaml to generate interface test case files",
        )
        self._generate_command.add_argument(
            "-o",
            "--output",
            action="store",
            type=str,
            required=False,
            default=os.curdir,
            metavar="",
            help="Generate case files to the specified directory, the default value is current directory",
        )

    def parse(self, args: Optional[Union[List[str], "os.PathLike[str]"]]):
        """
        Put the parsed parameters into the option, when you get the parameters, just call get_option
        """
        arguments = self.parser.parse_args(args)
        for _args in arguments.__dir__():
            if _args.startswith("_"):
                continue
            setattr(self.option, _args, getattr(arguments, _args))
        self.arguments = arguments


def prepare_config(
        args: Optional[Union[List[str], "os.PathLike[str]"]] = None) -> Config:
    if args is None:
        args = sys.argv[1:]
    plugin_manager = PiStarPluginManager()
    config = Config(plugin_manager, args)
    for spec in builtin_plugins:
        plugin_manager.import_plugin(spec)  # import impl for the spec
    config.pluginmanager.load_setuptools_entrypoints("pistar_plugin")
    config.hook.pistar_add_option(config=config)
    config.parse(args)
    config.hook.pistar_config(config=config)
    return config


def main(args: Optional[Union[List[str], "os.PathLike[str]"]] = None):
    try:
        config = prepare_config(args)
    except UsageError:
        return ExitCode.USAGE_ERROR

    if config.version:
        print("pistar", VERSION)

    elif config.subcommand == COMMANDS.EXECUTE:
        try:
            config.hook.pistar_main(config=config)
        except UsageError as e:
            for msg in e.args:
                print(f"ERROR: {msg}")

            return ExitCode.USAGE_ERROR

    elif config.subcommand == COMMANDS.GENERATE:
        generate_file(config.arguments)
    else:
        config.parser.print_help()
    return ExitCode.OK


def console_main() -> int:
    """
    The CLI entry point for pistar.

    """
    return main()


VERSION = "2.0.0"
