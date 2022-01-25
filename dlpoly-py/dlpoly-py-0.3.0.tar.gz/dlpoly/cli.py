"""
Set up command line input for DLPOLY parser
"""

import argparse as arg


# SmartFormatter taken from StackOverflow
class SmartFormatter(arg.HelpFormatter):
    """ Class to allow raw formatting only on certain lines """

    def _split_lines(self, text, width):
        """ Do not format lines prefixed with R|

        :param text: Texto to parse
        :param width: Max width

        """
        if text.startswith("R|"):
            return text[2:].splitlines()
        # this is the RawTextHelpFormatter._split_lines
        return arg.HelpFormatter._split_lines(self, text, width)


# DictKeyPair taken from StackOverflow
class StoreDictKeyPair(arg.Action):
    """ Class to convert a=b into dictionary key, value pair """

    def __call__(self, parser, namespace, values, optionString=None):
        """ Take a=b and map to dict

        :param parser: Parse in
        :param namespace: Object to write to
        :param values: Vals to map
        :param optionString: Extra options

        """
        newDict = {}
        for keyVal in values.split(","):
            key, value = keyVal.split("=")
            newDict[key] = value
        setattr(namespace, self.dest, newDict)


_PARSER = arg.ArgumentParser(
    description="Parser for the DLPOLY file parser",
    add_help=True,
    formatter_class=SmartFormatter,
)
_PARSER.add_argument("-s", "--statis", help="Statis file to load", type=str)
_PARSER.add_argument("-c", "--control", help="Control file to load", type=str)
_PARSER.add_argument("-f", "--field", help="Field file to load", type=str)
_PARSER.add_argument("-C", "--config", help="Config file to load", type=str)
_PARSER.add_argument(
    "-w", "--workdir", help="Work directory in which to run", type=str, default="myRun"
)
_PARSER.add_argument(
    "-e", "--dlp", help="Name of DLP execuable to run", default="DLPOLY.Z"
)


def get_command_args():
    """Run parser and parse arguments

    :returns: List of arguments
    :rtype: argparse.Namespace

    """
    return _PARSER.parse_args()
