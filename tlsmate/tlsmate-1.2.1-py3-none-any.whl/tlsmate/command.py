# -*- coding: utf-8 -*-
"""Module containing the CLI implementation
"""
# import basic stuff
import importlib
import argparse
import logging

# import own stuff
import tlsmate.config as conf
import tlsmate.plugin as plg
import tlsmate.tlsmate as tm
import tlsmate.utils as utils

# import other stuff


class _PreParser(plg.Plugin):
    plugins = [plg.ArgConfig, plg.ArgPlugin, plg.ArgLogging]


def build_parser() -> argparse.ArgumentParser:
    """Creates the parser object

    Returns:
        the parser object as created with argparse
    """

    return plg.BaseCommand.create_parser()


def _load_plugins(config: conf.Configuration) -> None:

    pre_parser = argparse.ArgumentParser(add_help=False)
    _PreParser.extend_parser(pre_parser, None)
    pre_args, _ = pre_parser.parse_known_args()

    # logging should be setup as early as possible
    utils.set_logging_level(pre_args.logging)

    if pre_args.plugin:
        plugins = pre_args.plugin

    else:
        plugins = config.get_from_external(pre_args.config_file, "plugin")

    if plugins:
        for plugin in plugins:
            if plugin.startswith("tlsmate_"):
                try:
                    importlib.import_module(plugin)
                    logging.debug(f"Plugin module {plugin} successfully loaded")

                except ModuleNotFoundError:
                    pass


def main() -> None:
    """The entry point for the command line interface"""

    utils.set_logging_format()
    config = conf.Configuration()
    _load_plugins(config)

    parser = build_parser()
    args = parser.parse_args()

    plg.BaseCommand.register_config(config)
    config.init_from_external(args.config_file)
    config.set("logging", args.logging)
    work_manager = plg.WorkManager()
    plg.BaseCommand.args_parsed(args, parser, None, config)
    tlsmate = tm.TlsMate(config=config)
    work_manager.run(tlsmate)


# And now load the plugins which are shipped by default with tlsmate...
from tlsmate.plugins import scan, version  # NOQA
