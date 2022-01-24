# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import argparse
import sys
from knack.arguments import ignore_type
from .commands_utility import introspect
from .constants import SUPPORTED_RUNTIMES


def register_command_arguments(az_command_loader, command_name, command_json_file):
    """ Takes the name of a command (ex: "ml service list") and empty string for
        all commands, and register all arguments for the chosen command(s).

    :param az_command_loader: AzML CLI command loader object
    :type az_command_loader: MachineLearningCommandsLoader
    :param command_name: Name of the AzML CLI command whose arguments will be loaded.
                        An empty string means to load all applicable commands
    :type command_name: str
    :param command_json_file: Path to a json file which declares all commands and arguments
    :type command_json_file: str
    """

    details = introspect(command_json_file)

    # Checking if this is a declared command.
    if command_name and command_name not in details:
        return

    if not command_name:
        # load arguments for all commands
        for current_command_name in details.keys():
            _register_single_command_arguments(az_command_loader, current_command_name, details)
    else:
        _register_single_command_arguments(az_command_loader, command_name, details)


def _register_single_command_arguments(az_command_loader, command_name, details):
    """ Takes arguements for a single AzML CLI command, which registers the arguments.

    :param az_command_loader: AzML CLI command loader object
    :type az_command_loader: MachineLearningCommandsLoader
    :param command_name: Name of the AzML CLI command whose arguments will be loaded.
    :type command_name: str
    :param details: deserialized dict which contains all o16n commands and arguments
    :type details: dict
    """
    command = details[command_name].copy()

    with az_command_loader.argument_context(command_name) as argument_context:
        for argument_name in command["arguments"].keys():
            try:
                argument_dict = command["arguments"][argument_name]

                if "positional_argument" in argument_dict:
                    arguments_dict = {"options_list": [argument_name], "help": argument_dict["description"],
                                      "nargs": argparse.REMAINDER}
                    argument_context.positional(argument_name, **arguments_dict)
                else:
                    args = get_arguments(argument_dict, argument_name)
                    argument_context.argument(argument_name, **args)
            except KeyError as error:
                sys.exit('The given command is not part of command_details.json: {}, \n'
                         'error: {}'.format(argument_name, error))


def get_arguments(arguments, key):
    """ Takes the dictionary of arguments and modifies it based on args that need
        additional modification. Uses key to check if description needs to be replaced.
    """

    if "long_form" in arguments and "short_form" in arguments:
        arguments["options_list"] = get_options(arguments)
    arguments.pop('long_form', None)
    arguments.pop('short_form', None)

    if "description" in arguments:
        arguments["help"] = process_description(arguments["description"], key)
    arguments.pop('description', None)

    if "default" in arguments:
        arguments["default"] = process_default(arguments["default"])

    if "arg_type" in arguments:
        arguments["arg_type"] = process_arg_type(arguments["arg_type"])

    if "type" in arguments:
        arguments["type"] = process_type(arguments["type"])
    return arguments


def get_options(arguments):
    """ Converts long_form/short_form into the appropriate tuple for argument
        registration.
    """

    if arguments["long_form"] != '' and arguments["short_form"] != '':
        return (arguments["long_form"], arguments["short_form"])
    if arguments["long_form"] == '':
        return (arguments["short_form"], )
    return (arguments["long_form"], )


def process_default(value):
    if value == "None":
        return None
    return value


def process_arg_type(value):
    if value == "ignore_type":
        return ignore_type
    return value


def process_type(value):
    if value == "int":
        return int
    if value == "float":
        return float
    if value == "[]":
        return []
    return value


def process_description(value, key):
    if value == "argparse.SUPPRESS":
        return argparse.SUPPRESS
    if key == "target_runtime" or key == "runtime":
        return value + '{}'.format('|'.join(SUPPORTED_RUNTIMES.keys()))
    return value
