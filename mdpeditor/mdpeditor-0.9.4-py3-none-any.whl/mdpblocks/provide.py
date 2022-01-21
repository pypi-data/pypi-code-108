""" Allow to access the contents of pre-defined mdp parameter blocks"""
import importlib.resources
import configparser
import io
import sys

from collections import OrderedDict


def available_parameter_blocks():
    """
    List available parameter blocks in the package resource
    """

    available_mdp_blocks = []

    # the mdp blocks are stored as a sub-package with non-python data
    # in nested folders like default/parameters.mdp
    mdpblock_package_contents = importlib.resources.contents(__package__)

    for package_content in mdpblock_package_contents:

        # go through all subfolders
        if not importlib.resources.is_resource(__package__, package_content):
            # look for .mdp files
            for block in importlib.resources.contents(__package__ + "." +
                                                      package_content):
                if block[-4:] == ".mdp":
                    available_mdp_blocks += [
                        package_content + "." + block[:-4]
                    ]
    available_mdp_blocks.sort()
    return available_mdp_blocks


def default_parameter_block():
    """
    Return a parameter block that has all parameters set to default values
    """

    return mdp_string_to_ordered_dict(
        parameter_block_as_string("default.parameters"))


def read_parameter_blocks(blocks):
    """
    Read a list of specified parameter blocks as a mapping to an OrderedDict.
    """

    if not blocks:
        return map(mdp_string_to_ordered_dict, [""])

    mdp_option_blocks_as_strings = [
        parameter_block_as_string(block_to_compile)
        for block_to_compile in blocks
    ]

    return map(mdp_string_to_ordered_dict, mdp_option_blocks_as_strings)


def describe_parameter_blocks() -> str:
    """Return a string with a self-description of all parameter blocks
    """
    description_string = ""
    for block in available_parameter_blocks():
        if sys.stdout.isatty():
            # make things bold
            description_string += '\033[1m'

        description_string += f'{block}'

        if sys.stdout.isatty():
            # back to normal formatting
            description_string += '\033[0m'

        description_string += "\n\t"
        
        # print the first lines of the parameter file that are prepended with
        # a semicolon, omitting the semicolon
        block_as_string = parameter_block_as_string(block)
        for line in block_as_string.splitlines():
            if len(line) > 0 and (line[0] == ';'):
                description_string += line[1:]
            else:
                # newline for next block
                description_string += "\n\n"
                break

    return description_string


def parameter_block_as_string(block_name):
    """
    Return an .mdp parameter block from the package resources
    """

    return importlib.resources.read_text(
        __package__ + "." + block_name.split(".")[0],
        block_name.split(".")[1] + ".mdp")


def mdp_string_to_ordered_dict(mdp_string: str) -> OrderedDict:
    """
    Convert a string in .mdp format to an OrderedDict

    Values are treated as strings, comments are stripped.

    Args:
        mdp_string (string): Input string in .mdp format (key = value)

    Returns:
        OrderedDict: A dict with the parameters in order
    """

    # add a section heading to satisfy configparser
    mdp_string = "[parameters]\n" + mdp_string
    # provide this string as a file for configparser to read
    mdp_string_as_file = io.StringIO(mdp_string)

    config = configparser.ConfigParser(
        comment_prefixes=[";"], inline_comment_prefixes=[";"])
    config.read_file(mdp_string_as_file)

    return OrderedDict(config['parameters'])
