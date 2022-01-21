""" Functions to extract the appropriate section of mdp-options.rst
"""
import importlib


def mdp_section(parameter_name):
    """Extract user guide section about a specific mdp parameter

       :raises ValueError: if parameter_name is not found in .mdp options

    Args:
        parameter_name (str): the mdp option to be looked for
    """
    # we read the file every time we parse a parameter
    # might be worth moving up to module startup if this is slow
    mdp_options = importlib.resources.read_text(__package__,
                                                "mdp-options.rst")

    parameter_tag = ".. mdp:: "
    start = mdp_options.index(parameter_tag + parameter_name + "\n") + len(parameter_tag)

    # find the end of the parameter description:
    #   - new option
    #   - new section

    # use find so we don't raise an error if at the end of the file
    next_tag_position = mdp_options[start:].find(parameter_tag)

    # two newlines mark a new section
    section_tag = "\n\n\n"
    next_section_position = mdp_options[start:].find(section_tag)

    # if there is no next tag set this to next section so that end(..) works
    if next_tag_position == -1:
        next_tag_position = next_section_position

    if next_section_position == -1:
        next_section_position = next_tag_position

    # whatever comes first
    end = min(next_section_position, next_tag_position)

    return mdp_options[start + len(parameter_name): start+end].strip()
