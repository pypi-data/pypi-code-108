"""
Convert old-style DLPOLY scripts to the new format

J. Wilkins Sep 2020
"""

import argparse
from collections import defaultdict
import sys
from dlpoly.control import Control


CONVERSIONS = {r"&s": "source", r"&n": "num"}
CONV_HELP = str(", ".join([f"{orig} => {sub}" for orig, sub in CONVERSIONS.items()]))

_PARSER = argparse.ArgumentParser(description='Convert from old-style DLPOLY script to new-style', add_help=True)
_PARSER.add_argument('sources', nargs="+", help="List of files to convert")
_PARSER.add_argument('-o', '--output-format', default="&s.new",
                     help=f"Format of output filenames {CONV_HELP}. Default: %(default)s")


def get_command_args():
    """Run parser and parse arguments

    :returns: List of arguments
    :rtype: argparse.Namespace

    """
    argList = _PARSER.parse_args()
    if not argList.sources:
        _PARSER.print_help()
        sys.exit()
    return argList


def convert_format(fmt, **kwargs):
    """ Return the new filename according to the format

    :param fmt: format to apply

    """
    out = fmt.format(d=defaultdict(str, **kwargs))
    return out


def convert(source, output):
    """ Convert an old-style control to new style

    :param source: source file
    :param output: output file

    """
    control = Control(source)
    newControl = control.to_new()
    newControl.write(output)


def to_dict(string):
    """ Perform conversion to dictref

    :param string: string toconvert

    """
    return "{d[" + string + "]}"


def main():
    """ Run the main program using CLI """
    argList = get_command_args()

    outputFormat = argList.output_format
    for item in CONVERSIONS.items():
        outputFormat = outputFormat.replace(item[0], to_dict(item[1]))

    for i, source in enumerate(argList.sources, 0):
        try:
            newName = convert_format(outputFormat, source=source, num=i)
            convert(source, newName)
        except Exception as err:
            print(f"Warning: Failure to convert source {source}")
            print(err)
            raise


if __name__ == "__main__":
    main()
