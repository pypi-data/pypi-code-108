# Copyright (C) 2021 FernOfSigma.

# This file is part of owoifier.

# owoifier is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.

# owoifier is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# owoifier. If not, see <https://www.gnu.org/licenses/>.

"""Contains the argument parser instance."""

from argparse import (
    ArgumentParser,
    ArgumentTypeError,
    RawDescriptionHelpFormatter,
)
import os.path as path

from .. import __version__


argparser = ArgumentParser(
    formatter_class=RawDescriptionHelpFormatter,
    description="Translates English text into OwO using magic.",
    epilog=(
        f"Copyright (C) 2021 FernOfSigma.\n"
        "This program is licensed under GNU GPL version 3 or later "
        "<https://gnu.org/licenses/gpl.html>. "
        "There is NO WARRANTY, to the extent permitted by law."
    ),
    add_help=False,
    allow_abbrev=False
)

# Mutually exclusive argument group for types of input data.
mandatory = argparser.add_mutually_exclusive_group(required=True)

def file(file_path: str) -> str:
    """Argument type for an existing file."""
    if path.isfile(file_path):
        file_path = path.expanduser(file_path)
        file_path = path.expandvars(file_path)
        return path.normpath(file_path)
    raise ArgumentTypeError(f"{file_path} is not a file.")

mandatory.add_argument(
    "-i", "--input-file",
    metavar="FILE", type=file,
    help="path to text file that needs to be translated"
)

mandatory.add_argument(
    "-t", "--text",
    metavar="TEXT", nargs="+",
    help="text that needs to be translated"
)

# Argument group for optional arguments.
optional = argparser.add_argument_group("optional arguments")

optional.add_argument(
    "-p", "--add-prefix",
    action="store_true",
    help="add a funny prefix"
)

optional.add_argument(
    "-s", "--add-suffix",
    action="store_true",
    help="add a funny suffix"
)

# Argument group for more miscellaneous arguments.
misc = argparser.add_argument_group("miscellaneous arguments")

misc.add_argument(
    "--help",
    action="help",
    help="show this help message and exit"
)

misc.add_argument(
    "--version",
    action="version",
    version=__version__
)
