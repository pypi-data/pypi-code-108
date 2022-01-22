""" Run the command line interface """
import argparse
import itertools
import json
import sys
import setuptools_scm

import mdpeditor.parameterhandler as parameterhandler

import importlib.metadata

from mdpeditor.mdpblocks import provide
from mdpeditor.mdpblocks.process import apply_instructions
from mdpeditor.parameterhelp import extract
from mdpeditor.commandlineinterface import parsesetparameters


def get_command_line_arguments(version: str):
    """build, parse and return command line arguments

    Args:
        version (str): the current program version

    Returns:
        the parsed command line arguments
    """

    program_name = "mdpeditor"
    description = """Compiles an .mdp file from preset .mdp parameter blocks
       and user settings. To learn more about available parameters
       use --blocks.
       """

    epilog = """examples:
    mdpeditor --blocks
    \tShows available pre-defined parameter blocks

    mdpeditor --compile force_field.charmm --set nsteps=100
    \tCompiles the pre-defined block force_field.charmm and
    \tsets "nsteps = 100" in the output

    mdpeditor --compile pressure.atmospheric force_field.charmm --minimal
    \tWrite only values that were set when compiling pressure.atmospheric
    \tforce_field.charmm, skip all defaults
    """

    parser = argparse.ArgumentParser(
        description=description,
        prog=program_name,
        add_help=False,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parameters_argument_group = parser.add_argument_group(
        "simulation parameters")

    parameters_argument_group.add_argument(
        "--set",
        nargs="+",
        default="",
        help="Set parmaters as parameter1=value1 parameter2=value2")

    parameters_argument_group.add_argument(
        "--compile",
        nargs="+",
        help="pre-defined mdp option blocks to compile an .mdp file, use"
        "--blocks to list all available blocks",
        choices=provide.available_parameter_blocks(),
        metavar="parameter.block")

    parameters_argument_group.add_argument(
        "--input-mdp",
        dest="input_mdp",
        type=argparse.FileType('r'),
        help="read parameters from an .mdp file",
        metavar="input.mdp")

    behaviour_argument_group = parser.add_argument_group("behavior")

    behaviour_argument_group.add_argument(
        "--merge-duplicates",
        dest="merge_right",
        action='store_true',
        default=False,
        help="allow duplicate parameters by overwriting previously set"
        " parameters in the following order, --input-mdp < --compile < --set, "
        " so that parameters specified with --set always prevail")

    parser.add_argument("-h",
                        "--help",
                        action="help",
                        help="show this help message and exit")

    parser.add_argument(
        "--version",
        action="version",
        version=(f"{program_name} {version}")
    )

    inspection_argument_group = parser.add_argument_group("inspect parameters")

    inspection_argument_group.add_argument(
        "--blocks",
        dest="describe_blocks",
        action='store_true',
        default=False,
        help="print description of all available parameter blocks and exit")

    inspection_argument_group.add_argument(
        "--show",
        dest="show_block",
        choices=provide.available_parameter_blocks(),
        help="show the selected parameter block and exit",
        metavar="block")

    inspection_argument_group.add_argument("--describe",
                                           dest="describe",
                                           help="describe an .mdp parameter",
                                           metavar="parameter")

    output_argument_group = parser.add_argument_group("output")

    output_argument_group.add_argument(
        "--output",
        nargs='?',
        const='compiled.mdp',
        type=argparse.FileType('w'),
        help="write the compiled parameters to an .mdp file"
        " (instead of command line)",
        metavar="compiled.mdp")

    output_argument_group.add_argument("--minimal",
                                       dest="minimal",
                                       action='store_true',
                                       default=False,
                                       help="keep the output minimal")

    # print the help text if no arguments are given
    if len(sys.argv) == 1:
        return parser.parse_args(args=["--help"])

    return parser.parse_args()


def run():
    """ run the command line interface """

    # derive the program version via git
    try:
        version = importlib.metadata.version("mdpeditor")
    except importlib.metadata.PackageNotFoundError:
        version = "Unknown"

    command_line_arguments = get_command_line_arguments(version)

    if (command_line_arguments.describe_blocks
            and command_line_arguments.show_block):
        raise SystemExit(
            "Cannot run --show and --blocks at the same time.")

    if command_line_arguments.describe_blocks:
        print("\nPre-defined parameter blocks for --compile\n")
        print(provide.describe_parameter_blocks())
        sys.exit()

    if command_line_arguments.show_block:
        print(
            provide.parameter_block_as_string(
                command_line_arguments.show_block))
        sys.exit()

    if command_line_arguments.describe:
        try:
            print(extract.mdp_section(command_line_arguments.describe))
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
        [parsesetparameters.parse_set_parameters(
            command_line_arguments.set)])

    compiled_parameters = parameterhandler.compile_parameters(input_parameter_blocks)

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

    writing_to_terminal = True if (not command_line_arguments.output
                                   and sys.stdout.isatty()) else False
    # color output only if we have an interactive terminal and
    # a full-blown .mdp is asked for
    if writing_to_terminal and not command_line_arguments.minimal:
        output_string = output_parameters.as_colored_string(
            compiled_parameters.parameters.keys())
    else:
        output_string = output_parameters.as_string()

    # if we write or pipe to a file, keep track of the command used to generate
    # the output by prepending a commented line
    if not writing_to_terminal:
        output_string = f"; Created by mdpeditor version {version}\n" + \
                        "; " + ' '.join(sys.argv) + '\n' + output_string

    # write either to terminal or to file
    if command_line_arguments.output:
        command_line_arguments.output.write(output_string)
    else:
        print(output_string)
