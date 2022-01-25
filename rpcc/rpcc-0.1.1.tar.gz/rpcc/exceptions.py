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

from typing import Collection

from rpcc.meta import FilePosition


class ConfigurationError(ValueError):
    pass


def assert_config(value, options: Collection, msg="Got %r, expected one of %s"):
    if value not in options:
        raise ConfigurationError(msg % (value, options))


class RpccSyntaxError(SyntaxError):
    label = "syntax error"

    def __init__(self, location: FilePosition) -> None:
        self.location = location

    def __str__(self):
        return f"{self.location.filename}:{self.location.line}:{self.location.column}: error: {self.label}"


class UnexpectedToken(RpccSyntaxError):
    label = "unexpected token"

    def __init__(self, location: FilePosition, token, expected, terminals):
        super().__init__(location)
        self.token = token
        self.expected_tokens = expected
        self.terminals = terminals

    @staticmethod
    def _format_expected(expected, terminals):
        d = {t.name: t for t in terminals}

        expected = [str(d[t_name].pattern).replace('\\', "").replace('\'', '’') if t_name in d else t_name for t_name in
                    expected]

        if len(expected) > 1:
            return "Expected one of:\n\t* %s\n" % '\n\t* '.join(expected)
        else:
            return "Expected:\n\t%s\n" % '\n\t* '.join(expected)

    def __str__(self):
        return (super().__str__() + f" ’{self.token}’\n" +
                f"{get_context(self.location)}\n" +
                f"{self._format_expected(self.expected_tokens, self.terminals)}")


class UnexpectedCharacters(RpccSyntaxError):
    label = "unexpected character"

    def __str__(self):
        return (super().__str__() + "\n" +
                get_context(self.location))


class UnexpectedEOF(RpccSyntaxError):
    label = "unexpected End-of-File."


class MissingRpcDefinition(RpccSyntaxError):
    label = "missing rpc definition"

    def __str__(self):
        return (super().__str__() + "\n" +
                get_context(self.location))


class MissingRpcName(RpccSyntaxError):
    label = "missing rpc name"

    def __str__(self):
        return (super().__str__() + "\n" +
                get_context(self.location))


class EmptyRpcDefinition(RpccSyntaxError):
    label = "rpc definition is empty"

    def __str__(self):
        return (super().__str__() + "\n" +
                get_context(self.location))


class RpcRedefinition(RpccSyntaxError):
    label = "redefinition of rpc"
    prev_label = "previously defined here"

    def __init__(self, location: FilePosition, name: str, prev_definition: FilePosition):
        super().__init__(location)
        self.name = name
        self.prev = prev_definition

    def __str__(self):
        return (super().__str__() + f" ’{self.name}’\n" +
                get_context(self.location) + "\n" +
                f"{self.prev.filename}:{self.prev.line}:{self.prev.column}: note: ’{self.name}’ {self.prev_label}\n" +
                get_context(self.prev))


def get_context(location: FilePosition, span: int = 40) -> str:
    """Returns a pretty string pinpointing the error in the text,
       with span amount of context characters around it.
    """
    pos = location.pos_in_stream
    start = max(pos - span, 0)
    end = pos + span
    max_width = 6
    if not isinstance(location.text, bytes):
        before = location.text[start:pos].rsplit('\n', 1)[-1]
        after = location.text[pos:end].split('\n', 1)[0]
        return f'{location.line:>{max_width}} | ' + before + after + '\n' + \
               ' ' * max_width + ' | ' + ' ' * len(before.expandtabs()) + '^\n'
    else:
        before = location.text[start:pos].rsplit(b'\n', 1)[-1]
        after = location.text[pos:end].split(b'\n', 1)[0]
        return (before + after + b'\n' + b' ' * len(before.expandtabs()) + b'^\n').decode("ascii",
                                                                                          "backslashreplace")
