import argparse
import sys

from mdpeditor.mdpblocks import provide


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

    parser.add_argument("--version",
                        action="version",
                        version=(f"{program_name} {version}"))

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
