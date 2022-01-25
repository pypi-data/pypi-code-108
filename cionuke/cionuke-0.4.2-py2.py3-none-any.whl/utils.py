import nuke
import os

import re

TOKENS = (r"#+", r"%0\d+d", r"%V")  
# hashes 
# image.%04d.exr
# %V (stereo view) or %v (version)

TOKEN_RX = re.compile("|".join(TOKENS), re.IGNORECASE)


def divider(submitter, name):
    """
    UI horizontal rule.
    """
    k = nuke.Text_Knob(name, "", "")
    submitter.addKnob(k)


def as_globbable_path(knob):
    """
    Get a representation of the path in this knob that can be globbed.

    The value in the knob is a path that may contain TCL expressions and/or tokens such as # or %04d. We want a
    representation of the path that can be used to give us the assets that exist on disk, for all frames.

    1. Use nuke.runIn() to evaluate the TCL in the context of the node. This will NOT evaluate frame number tokens.
    2. If the path is relative, we prefix it with the script directory.
    3. Replace Nuke's frame number and stereo representations (See TOKENS) with '*'s.

    Example:
        Knob value: '[python {nuke.script_directory()}]/../images/sequences/02/image.%04d.jpg'
        Result: "/Volumes/projects/project1/nuke/../images/sequences/02/image.*.jpg'"

        This result has no special Nuke stuff and can be used to find the actual files on disk (if
        any) represented by this knob. 

    Args:
        knob (File_Knob): The knob

    Returns:
        string: A path that may contain '*'s for later globbing.
    """

    value = knob.value().replace("'", "\\'")
    if not value:
        return None
    try:
        value = nuke.runIn(knob.node().fullName(), "nuke.tcl('return {}')".format(value))
    except:
        pass
    if not value:
        return None
    if not os.path.isabs(value):
        value = os.path.join(nuke.script_directory(), value)
    value = TOKEN_RX.sub("*", value)
    return value


def truncate_path_to_star(in_path):
    """
    Make sure the path contains no wildcards (stars).

    We need a literal ancestor of paths in write nodes in order to generate a common ancestor for
    the output path. We can't entertain '*'s, so we go up a level until they're all gone.

    Inputs to this function should have already gone through as_globbable_path() above, since we
    only check for '*'s.

    Args:
        in_path (str): The path to examine.

    Returns:
        [str]: Possibly truncated path
    """

    result = in_path
    while True:
        if not "*" in result:
            return result
        result = os.path.dirname(result)
