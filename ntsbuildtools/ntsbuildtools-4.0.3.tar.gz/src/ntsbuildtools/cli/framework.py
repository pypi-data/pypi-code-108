#!/usr/bin/env python3
"""This module provides the `register` function for establishing the command-line interface,
and the `run` function to act as the main entry point for the entirety of ntsbuildtools.
"""
import configargparse
import importlib
import os
import pkgutil

import ntsbuildtools.exceptions
import ntsbuildtools
from ntsbuildtools.cli.tree import ArgParserNode


# Initialize the "Root ArgumentParser" for the whole project
_root_parser = configargparse.ArgumentParser(
    description="Tools that help with Jenkins build scripts.", 
    default_config_files=["./buildtools.yaml", "./buildtools.ini"]
)

# Intitialize the ArgParserNode (also for the whole project)
_parser_tree = ArgParserNode(command='buildtools', parser=_root_parser)

def set_version(version: str):
    global _root_parser
    _root_parser.add_argument('--version', action='version', 
                              version=f"BuildTools CLI {version}")


def register(package) -> ArgParserNode:
    """Register all the modules found in the package. `package` will be fully traversed to
    collect the 'docstrings' for each subcommand in the CLI tree. Additionally, the `main` 
    and `config_parser` methods for each subcommand are processed into the root parser.

    Once registration of subcommands is complete, invoking `run(sys.argv[:1])` function
    will execute the appropriate 'main' function depending on the command-line arguments provided.

    Args:
        package (package|str): The `subcommands` package to be registered (or name of the package).

    Returns:
        ArgParserNode: The CLI tree data structure, which now contains the registered modules.

    Example:
        The simplest example is also representative of the 
            import ntsbuildtools.cli
            import ntsbuildtools.subcommands

            ntsbuildtools.cli.register(ntsbuildtools.subcommands)
            ntsbuildtools.cli.run(sys.argv[1:])
    """
    if isinstance(package, str):
        package = importlib.import_module(package)
    _register(package, _parser_tree)
    return _parser_tree


def children_module_info_of(package):
    if isinstance(package, str):
        package = importlib.import_module(package)
    path_to_package = os.path.dirname(package.__file__)
    return [_ for _ in pkgutil.iter_modules([path_to_package])]


def _register(package, node):
    for module_info in children_module_info_of(package):
        module_name = f'{package.__name__}.{module_info.name}'
        if module_info.ispkg:
            # If this is a package (think directory), create an inner node and RECURSE!
            loaded_package = importlib.import_module(module_name)
            child = node.add(module_info.name, loaded_package.__doc__)
            _register(loaded_package, child)
        else:
            # If this is a module (think .py file), create a leaf node!
            loaded_module = importlib.import_module(module_name)
            if not hasattr(loaded_module, 'main'):
                raise ntsbuildtools.exceptions.BTMainFuncMissingError(module_name)
            leaf = node.add_leaf(module_info.name, loaded_module.__doc__, loaded_module.main)
            # Each subcommand can OPTIONALLY provide a config_parser(parser) function
            if hasattr(loaded_module, 'config_parser'):
                leaf.config_parser(loaded_module.config_parser)


def get_parser():
    return _root_parser


def run(args):
    """Run BuildTools!"""
    parsed_args = _root_parser.parse_args(args)
    parsed_args.func(parsed_args)
