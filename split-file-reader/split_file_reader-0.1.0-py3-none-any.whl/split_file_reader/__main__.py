#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
    split_file_reader
    Copyright (C) 2022  Xavier Halloran, United States

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import os
import typing
import sys

from .split_file_reader import SplitFileReader


long_description = """
Identify and process parted archives without manual concat.
This command line capability provides support only Tar and Zip files; but not 7z or Rar.
Designed to work for files that have been split via the `split` utility, or any other binary cut;
but does not support Zip's built-in split capability. 
The python module supports any arbitrarily split files, regardless of type.
Copyright (C) 2022  Xavier Haloran
"""


def main(test_args: typing.List[str] = None):
    import argparse

    parser = argparse.ArgumentParser(description=long_description, prog="python -m split_file_reader")
    parser.add_argument(
        "-a",
        "--archive",
        default="zip",
        choices=["zip", "z", "tar", "t", "tgz", "tbz", "txz"],
        help="Archive type, either zip, tar, tgz, tbz, or txz",
    )
    parser.add_argument("-p", "--password", metavar="<password>", default=None, help="Zip password, if needed")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-t",
        "--test",
        action="store_true",
        help="Test the archive, using the module's built-in test.  Produces the same output of the "
        "respective module's equivalent of `--test`",
    )
    group.add_argument("-l", "--list", action="store_true", help="List all the payload files in the archive.")
    group.add_argument(
        "-x", "--extract", metavar="<destination>", help="Extract the entire archive to filepath <destination>."
    )
    # group.add_argument('-m', '--match', metavar=('<match>', '<directory>'), nargs=2,
    #                    help="Extract payload files with name matching <match> to <directory>.")
    group.add_argument("-r", "--read", metavar="<filename>", help="Read out payload file contents to stdout.")
    parser.add_argument(
        "files",
        metavar="<filepath>",
        nargs="+",
        help="In-order list of the parted files on disk.  Use shell expansion, such as ./files.zip.*",
    )
    if test_args:
        args = parser.parse_args(test_args)
    else:
        args = parser.parse_args()

    sfr = SplitFileReader(args.files)

    if args.archive in ("zip", "z"):
        import zipfile

        with zipfile.ZipFile(sfr, mode="r") as zf:
            zf: zipfile.ZipFile = zf
            if args.test:
                zf.testzip()
            elif args.list:
                for zff in zf.filelist:
                    print(zff.filename)
            elif args.read:
                import shutil

                zff = zf.open(args.read, pwd=args.password)
                # Pytest swaps out the stdout for a StringIO, which has no buffer.
                if "PYTEST_CURRENT_TEST" not in os.environ:
                    shutil.copyfileobj(zff, sys.stdout.buffer)
            elif args.extract:
                zf.extractall(path=args.extract, pwd=args.password)
    elif args.archive in ("t", "tar", "tgz", "tbz", "txz"):
        import tarfile

        with tarfile.TarFile(fileobj=sfr, mode="r") as tf:
            if args.test:
                tf.getmembers()
                print(tf.getmembers(), file=sys.stderr)
            elif args.list:
                for tff in tf:
                    tff: tarfile.TarInfo = tff
                    print(tff.name)
            elif args.read:
                import shutil

                tff = tf.extractfile(args.read)
                # Pytest swaps out the stdout for a StringIO, which has no buffer.
                if "PYTEST_CURRENT_TEST" not in os.environ:
                    shutil.copyfileobj(tff, sys.stdout.buffer)
            elif args.extract:
                tf.extractall(path=args.extract)


if __name__ == "__main__":
    main()
