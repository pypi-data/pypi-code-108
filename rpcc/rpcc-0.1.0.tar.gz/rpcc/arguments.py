# Copyright 2021-2022, Barcelona Supercomputing Center (BSC), Spain
#
# This software was partially supported by the EuroHPC-funded project ADMIRE
#   (Project ID: 956748, https://www.admire-eurohpc.eu).
#
# This file is part of rpcc.
#
# rpcc is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# rpcc is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License along with rpcc.  If not, see
# <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import logging
import sys
from pathlib import Path
from rpcc.version import __version__ as rpcc_version
from rpcc.console import console


class _SetVerbosity(argparse.Action):
    def __init__(self, option_strings, dest, const=None, default=None,
                 required=False, help=None, metavar=None):
        super().__init__(option_strings=option_strings,
                         dest=dest,
                         nargs=0,
                         const=const,
                         default=default,
                         required=required,
                         help=help)

        self.count = 0

    def __call__(self, parser, namespace, values, option_string=None):
        levels = [
            logging.CRITICAL,
            logging.ERROR,
            logging.WARNING,
            25,  # LOGURU_SUCCESS_NO
            logging.INFO,
            logging.DEBUG,
            5  # LOGURU_TRACE_NO
        ]

        setattr(namespace, self.dest, levels[self.count])
        self.count = min(self.count + 1, len(levels) - 1)


class _PrintVersion(argparse.Action):
    def __init__(self, option_strings, dest, const=None, default=None,
                 required=False, help=None, metavar=None):
        super().__init__(option_strings=option_strings,
                         dest=dest,
                         nargs=0,
                         const=const,
                         default=default,
                         required=required,
                         help=help)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, self.const)
        console.print(f"rpcc {rpcc_version}")
        sys.exit(0)


def parse_args(args) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="rpcc",
                                     description="Parse RPC_PROTO_FILE and generate C++ output based on the options "
                                                 "given.")
    parser.add_argument(
        "rpc_proto_file",
        type=Path,
        metavar="RPC_PROTO_FILE",
        help="The file containing the specifications for the RPCs."
    )

    parser.add_argument(
        "--output-mode",
        choices=["hermes"],
        dest="output_mode",
        metavar="LIBRARY",
        default="hermes",
        help="Set the output mode. Possible values for LIBRARY are:\n"
             "\n"
             "hermes\n"
             "    Generate code that can be used with the Hermes library."
    )

    parser.add_argument(
        "--std",
        choices=["c++17"],
        dest="output_lang",
        metavar="LANG",
        default="c++17",
        help="Determine the output language. Possible values for LANG are:\n"
             "\n"
             "c++17\n"
             "    2017 ISO C++ standard."
    )

    parser.add_argument(
        "--c_out",
        type=Path,
        metavar="OUT_DIR",
        dest="impl_output_dir",
        help="The directory where C/C++ implementation files should be generated.",
        default=Path.cwd()
    )

    parser.add_argument(
        "--h_out",
        type=Path,
        metavar="OUT_DIR",
        dest="header_output_dir",
        help="The directory where C/C++ header files should be generated.",
        default=Path.cwd()
    )

    parser.add_argument(
        "--copyright-file",
        type=Path,
        default=None,
        help="Use the text in COPYRIGHT_FILE as the copyright header of all generated files."
    )

    parser.add_argument(
        "--color-diagnostics",
        choices=["never", "always", "auto"],
        metavar="WHEN",
        default="auto",
        help="Use escape sequences in diagnostic messages to display them in color in the terminal. WHEN is never, "
             "always, or auto (the default)."
    )

    parser.add_argument(
        "--debug",
        "-d",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.WARNING,
        help=argparse.SUPPRESS
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action=_SetVerbosity,
        dest="loglevel",
        default=logging.INFO,
        help="Increase verbosity"
    )

    parser.add_argument(
        "--version",
        "-V",
        action=_PrintVersion,
        help="Display rpcc version information."
    )

    return parser.parse_args(args)
