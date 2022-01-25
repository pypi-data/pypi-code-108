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
#  SPDX-License-Identifier: GPL-3.0-or-later

import sys
from rpcc import Rpcc
from rpcc.arguments import parse_args
from rpcc.exceptions import RpccSyntaxError
from rpcc.console import console
from loguru import logger


def main(args=None):
    """"The main routine"""

    if args is None:
        args = sys.argv[1:]

    args = parse_args(args)

    # configure console
    console.configure(args.color_diagnostics)

    # configure logging
    logger.remove()
    logger.add(sys.stderr, level=args.loglevel)

    try:
        Rpcc(
            args.rpc_proto_file,
            args.copyright_file,
            args.output_lang,
            args.header_output_dir,
            args.impl_output_dir
        ).transform()
    except (RpccSyntaxError, OSError) as e:
        console.eprint(f"ERROR: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
