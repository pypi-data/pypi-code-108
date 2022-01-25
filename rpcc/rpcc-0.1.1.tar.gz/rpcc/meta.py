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

import pathlib


class FilePosition:
    """An object representing a specific location in the parsed text"""

    def __init__(self, filename: pathlib.Path, text: str, line: int, column: int, pos_in_stream: int) -> None:
        """Initialize a `FileLocation`.

        :param filename: The filename.
        :param text: The parsed text.
        :param line: The line of interest.
        :param column: The column of interest.
        :param pos_in_stream: The position of the location of interest in the file stream.
        """

        self.filename = filename
        self.text = text
        self.line = line
        self.column = column
        self.pos_in_stream = pos_in_stream
