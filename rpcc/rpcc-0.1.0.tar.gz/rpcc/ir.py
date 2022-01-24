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

import itertools
from abc import ABC, abstractmethod
from typing import List, Any, Optional


class Argument:
    """A remote procedure argument.

    Parameters:
        id: a string with the argument's name.
        typeinfo: an object instance with the argument's type information.

    Example:
        >>> Argument("foobar", Integer(32, True))
        Argument(...)
    """

    id: str
    typeinfo: Any

    def __init__(self, id: str, typeinfo: Any) -> None:
        self.id = id
        self.typeinfo = typeinfo

    def __repr__(self) -> str:
        return f"Argument(id='{self.id}', typeinfo='{self.typeinfo}')"


class ReturnValue:
    """A remote procedure return value.

    Parameters:
        id: a string with the return variable's name.
        typeinfo: an object instance with the argument's type information.

    Example:
        >>> ReturnValue("barbaz", Integer(32, True))
        ReturnValue(...)
    """

    id: str
    typeinfo: Any

    def __init__(self, id: str, typeinfo: Any) -> None:
        self.id = id
        self.typeinfo = typeinfo

    def __repr__(self) -> str:
        return f"ReturnVariable(id='{self.id}', typeinfo='{self.typeinfo}')"


class ArgumentList:
    """A list of RPC arguments."""

    args: List[Argument]

    def __init__(self, args: List[Argument]):
        self.args = args

    def __iter__(self):
        for arg in self.args:
            yield arg

    def __len__(self):
        return len(self.args)


class ReturnValueList:
    """A list of RPC return values."""

    retvals: List[ReturnValue]

    def __init__(self, retvals: List[ReturnValue]):
        self.retvals = retvals

    def __iter__(self):
        for retval in self.retvals:
            yield retval

    def __len__(self):
        return len(self.retvals)


class ConditionalDefinition(ABC):
    @property
    @abstractmethod
    def start_keyword(self):
        raise NotImplemented

    @property
    @abstractmethod
    def end_keyword(self):
        raise NotImplemented

    @property
    @abstractmethod
    def symbol(self):
        raise NotImplemented

    @symbol.setter
    @abstractmethod
    def symbol(self, value):
        raise NotImplemented


class RemoteProcedure:
    """A remote procedure.

    Parameters:
        name: a string with the remote procedure's name.
        args: an ArgumentList containing the remote procedure's arguments.
        retvals: a ReturnValueList containing the remote procedure's return variables.

    Example:
        >>> RemoteProcedure("send_message",
        >>>                 ArgumentList([Argument("message", "string")],
        >>>                 ReturnValueList([ReturnValue("retval", "uint32")])))
        RemoteProcedure(...)
    """

    id: int
    name: str
    args: ArgumentList
    retvals: ReturnValueList
    include_if_expr: Optional[ConditionalDefinition]

    id_iter = itertools.count()

    def __init__(self, id: int, name: str, args: ArgumentList, retvals: ReturnValueList,
                 include_if_expr: Optional[ConditionalDefinition]) -> None:
        self.id = id
        self.name = name
        self.args = args
        self.retvals = retvals
        self.include_if_expr = include_if_expr

    def __repr__(self) -> str:
        return f"RemoteProcedure(id={self.id}, name='{self.name}', args={self.args}, retvals={self.retvals})"

    @staticmethod
    def generate_id(margo_compatible: bool = False) -> int:
        if not margo_compatible:
            return next(RemoteProcedure.id_iter)
        raise NotImplemented
        # TODO: generate a margo compatible id using the rpc name


class IRTree:
    """The Intermediate Representation Tree for our source-to-source compiler.

    Parameters:
        rpcs: a list of the remote procedures defined in the input file.

    Example:
        >>> IRTree([
        >>>    RemoteProcedure("send_message",
        >>>                    ArgumentList([Argument("message", "string")]),
        >>>                    ReturnValueList([ReturnValue("retval", "uint32"))])
        >>>    RemoteProcedure("shutdown", ArgumentList([]), ReturnValueList([ReturnValue("retval", "uint32")]))
        >>> ]
        Tree(...)
    """

    package: Optional[str]
    rpcs: List[RemoteProcedure]

    def __init__(self, package: Optional[str], rpcs: List[RemoteProcedure]):
        self.package = package
        self.rpcs = rpcs
