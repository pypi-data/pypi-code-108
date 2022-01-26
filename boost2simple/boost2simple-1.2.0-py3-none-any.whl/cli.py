#  boost2simple - the BoostNote->SimpleNote converter
#  Copyright (c) 2021, Rafael Witak.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
import argparse
import os
import pathlib

from boost2simple.converter import Converter

description = f"{os.path.basename(__file__)} takes one or more " \
              f"BoostNote collection exports (JSON format) \n" \
              f"and converts them to a single, " \
              f"SimpleNote-style export zip-file \n" \
              f"which can then easily be imported with SimpleNote."

epilog = ("'--no-markdown' sets the SimpleNote's markdown flag to false. \n"
          "Unless '--no-title' is set, it uses BoostNote's title \n"
          "as first line of the converted SimpleNote, \n"
          "followed by a single empty line. \n\n"
          "'--markdown' sets the SimpleNote's markdown flag to true. \n"
          "If not set to '--no-title', it also uses \n"
          "BoostNote's title as first line, \n"
          "but prefixes it with '# ' and follows up with an empty line; \n"
          "this effectively turns the BoostNote title into an h1 header. \n\n"
          "If you want your collection(s) to be tagged "
          "with their respective names, \n"
          "it is advised to put them in separate folders within ORIGIN_DIR; \n"
          "their folder name will be turned into a tag in SimpleNote; \n"
          "this allows you to intuitively navigate & find them later!")


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--markdown',
                        help="activate/deactivate SimpleNote's markdown flag",
                        default=True,
                        action=argparse.BooleanOptionalAction)
    parser.add_argument('--title',
                        help="add title of original note to first line "
                             "or omit it",
                        default=True,
                        action=argparse.BooleanOptionalAction)
    parser.add_argument('--from', metavar="ORIGIN_DIR", nargs=1,
                        type=pathlib.Path, required=False,
                        dest='boost_note_dir',
                        default=[pathlib.Path('')],
                        help='directory containing BoostNote collection(s) '
                             '(default: current directory)')
    parser.add_argument('--to', metavar="TARGET_DIR", nargs=1,
                        type=pathlib.Path, required=False,
                        dest='simple_note_dir',
                        default=[pathlib.Path('')],
                        help='directory to save the zip-file to '
                             '(default: current directory)')
    return parser


def main():
    args = get_parser().parse_args()
    simple_dir = sanitize_dir_path(vars(args).get("simple_note_dir")[0])
    boost_dir = sanitize_dir_path(vars(args).get("boost_note_dir")[0])
    md = vars(args).get("markdown", True)
    title = vars(args).get("title", True)
    converter = Converter(boost_dir, simple_dir, md, title)
    converter.convert_and_export()
    print(converter.status)


def sanitize_dir_path(path: pathlib.Path) -> pathlib.Path:
    if os.path.isdir(path):
        return path
    else:
        print(str(path) + " is not a valid directory name.")
        exit()


if __name__ == "__main__":
    main()
