""" Run the command line interface """
import argparse
import importlib.metadata
import itertools
import sys

import mdpeditor.parameterhandler as parameterhandler
import mdpeditor.commandlineinterface.arguments as arguments

from mdpeditor.mdpblocks import provide
from mdpeditor.mdpblocks.process import apply_instructions
from mdpeditor.parameterhelp import extract
from mdpeditor.commandlineinterface import parsesetparameters
from rich.console import Console
from rich import print
import rich.markdown


def run():
    """ run the command line interface """

    # set up the console for printing
    console = Console()

    # derive the program version via git
    try:
        version = importlib.metadata.version("mdpeditor")
    except importlib.metadata.PackageNotFoundError:
        version = "Unknown"

    command_line_arguments = arguments.get_command_line_arguments(version)

    if (command_line_arguments.describe_blocks
            and command_line_arguments.show_block):
        raise SystemExit("Cannot run --show and --blocks at the same time.")

    if command_line_arguments.describe_blocks:
        console.print("\nPre-defined parameter blocks for --compile\n")
        console.print(provide.describe_parameter_blocks())
        sys.exit()

    if command_line_arguments.show_block:
        console.print(
            provide.parameter_block_as_string(
                command_line_arguments.show_block))
        sys.exit()

    if command_line_arguments.describe:
        try:
            description_as_md=rich.markdown.Markdown(
                extract.mdp_section(command_line_arguments.describe))
            console.print(description_as_md)
        except ValueError as e:
            raise SystemExit("Cannot find " +
                             f"{command_line_arguments.describe}" +
                             " in the documented .mdp options")
        sys.exit()

    # read user parameter file
    mdp_input_as_string = ""
    if command_line_arguments.input_mdp:
        mdp_input_as_string = command_line_arguments.input_mdp.read()
    mdp_input = provide.mdp_string_to_ordered_dict(mdp_input_as_string)

    # read parameter blocks
    mdp_option_blocks = provide.read_parameter_blocks(
        command_line_arguments.compile)

    # add user-provided parameters
    input_parameter_blocks = itertools.chain(
        [mdp_input], mdp_option_blocks,
        [parsesetparameters.parse_set_parameters(command_line_arguments.set)])

    compiled_parameters = parameterhandler.compile_parameters(
        input_parameter_blocks)

    if (not command_line_arguments.merge_right
            and compiled_parameters.duplicate_keys):
        raise SystemExit(
            "\nAborting compilation due to duplicate parameter(s)\n\n\t" +
            "\n\t".join(list(compiled_parameters.duplicate_keys)) +
            "\n\nUse --merge-duplicates to override parameters\n")

    apply_instructions(compiled_parameters.parameters,
                       command_line_arguments.compile)

    output_parameters = parameterhandler.OutputParameters(
        compiled_parameters.parameters)

    if command_line_arguments.minimal:
        # discard all parameters that were not explicitely chosen
        output_parameters.keep_only(compiled_parameters.parameters.keys())

    # color output only if we have an interactive terminal and
    # a full-blown .mdp is asked for
    output_string = output_parameters.as_string(compiled_parameters.parameters.keys())

    # if we write or pipe to a file, keep track of the command used to generate
    # the output by prepending a commented line
    output_string = f"[blue]; Created by mdpeditor version {version}\n" + \
                    "; " + ' '.join(sys.argv) + '\n[/]' + output_string

    if command_line_arguments.output:
        console = Console(file=command_line_arguments.output)

    console.print(output_string)
