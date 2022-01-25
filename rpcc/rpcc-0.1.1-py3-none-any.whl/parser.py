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
from typing import Tuple

from lark import Lark, Tree
import lark.exceptions
from loguru import logger

from rpcc.exceptions import (
    EmptyRpcDefinition, MissingRpcDefinition, MissingRpcName, UnexpectedToken,
    UnexpectedCharacters, UnexpectedEOF
)
from rpcc.meta import FilePosition

INVALID_INPUT_EXAMPLES = {
    EmptyRpcDefinition: ['rpc foo {}',
                         'rpc foo { arguments {} returns {} } rpc bar {}'],
    MissingRpcDefinition: ['',
                           'foo',
                           'foo {',
                           'foo {}',
                           '{',
                           'arguments {',
                           'returns {'
                           ],
    MissingRpcName: ['rpc {']
}


class Parser:
    """The main parser class"""

    def __init__(self) -> None:
        self.parser = Lark.open_from_package("rpcc", "grammars/rpcc.lark", propagate_positions=True, parser='lalr')

    def parse(self, input_file: pathlib.Path) -> Tuple[Tree, str]:
        """Parse an input file.

        :param input_file: A `pathlib.Path` containing the path to the RPC description file to parse.
        :return: An AST tree with a representation of the parsed text.
        """

        try:
            file = open(input_file, "r", encoding="utf-8")
        except (FileNotFoundError, EnvironmentError) as err:
            logger.error(f"Error parsing file: {err}")
            raise
        else:
            with file:
                text = file.read()
                try:
                    return self.parser.parse(text), text
                except lark.exceptions.UnexpectedInput as u:

                    location = FilePosition(input_file, text, u.line, u.column, u.pos_in_stream)

                    exc_class = u.match_examples(self.parser.parse, INVALID_INPUT_EXAMPLES, use_accepts=True)

                    if exc_class:
                        raise exc_class(location) from None

                    if isinstance(u, lark.exceptions.UnexpectedToken):
                        raise UnexpectedToken(location, u.token, u.expected, self.parser.terminals) from None

                    if isinstance(u, lark.exceptions.UnexpectedCharacters):
                        raise UnexpectedCharacters(location) from None

                    if isinstance(u, lark.exceptions.UnexpectedEOF):
                        raise UnexpectedEOF(location) from None

                    raise u
