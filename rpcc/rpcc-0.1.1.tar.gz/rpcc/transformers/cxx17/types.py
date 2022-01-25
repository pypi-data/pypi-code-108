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

from abc import ABCMeta, abstractmethod
from typing import Optional, Dict, Type, Callable


class NameSpace:
    id: str

    def __init__(self, id='') -> None:
        self.id = id

    def __str__(self) -> str:
        return self.id

    def __repr__(self) -> str:
        return f"NameSpace(id='{self.id}')"


class CxxType(metaclass=ABCMeta):
    @abstractmethod
    def is_fundamental(self) -> bool:
        raise NotImplemented

    @abstractmethod
    def member_operator(self) -> str:
        raise NotImplemented

    @abstractmethod
    def hg_type(self) -> str:
        raise NotImplemented


class FundamentalType(CxxType, metaclass=ABCMeta):
    def is_fundamental(self) -> bool:
        return True

    def member_operator(self) -> str:
        raise ValueError("C++ fundamental types don't have member operators!")

    def hg_type(self) -> str:
        raise NotImplemented

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class CompoundType(CxxType, metaclass=ABCMeta):
    classname: str
    namespace: Optional[NameSpace]

    def __init__(self, classname: str, namespace: Optional[NameSpace] = NameSpace()) -> None:
        self.classname = classname
        self.namespace = namespace

    def is_fundamental(self) -> bool:
        return False

    def member_operator(self) -> str:
        return "."

    def hg_type(self) -> str:
        raise NotImplemented

    def __str__(self) -> str:
        return '::'.join(filter(None, [str(self.namespace), self.classname]))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(classname='{self.classname}', namespace={self.namespace.__repr__()})"


class Void(FundamentalType):
    def __str__(self) -> str:
        return "void"

    def hg_type(self) -> str:
        return "void"


class Bool(FundamentalType):
    def __str__(self) -> str:
        return "bool"

    def hg_type(self) -> str:
        return "hg_bool_t"


class Integer(FundamentalType):
    width: int
    unsigned: bool

    def __init__(self, width: int, unsigned: bool) -> None:
        self.width = width
        self.unsigned = unsigned

    def hg_type(self) -> str:
        return f"hg_{self}"

    def __str__(self) -> str:
        prefix = "u" if self.unsigned else ""
        return f"{prefix}int{self.width}_t"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(width={self.width}, unsigned={self.unsigned})"


class CSize(FundamentalType):
    def hg_type(self) -> str:
        return "hg_size_t"

    def __str__(self) -> str:
        return "size_t"


class Float(FundamentalType):
    def hg_type(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return "float"


class Double(FundamentalType):
    def hg_type(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return "double"


class Object(CompoundType):
    """A generic object."""
    pass


class String(CompoundType):
    def __init__(self) -> None:
        super().__init__("string", NameSpace("std"))

    def hg_type(self) -> str:
        return "hg_const_string_t"


class ExposedBuffer(CompoundType):
    def __init__(self) -> None:
        super().__init__("exposed_memory", NameSpace("hermes"))

    def hg_type(self) -> str:
        return "hg_bulk_t"


class Pointer(CompoundType):
    to_type: CxxType

    def __init__(self, to_type: CxxType) -> None:
        self.to_type = to_type

    def member_operator(self) -> str:
        return "->"

    def __str__(self) -> str:
        return f"{self.to_type} *"


class ReferenceType(CompoundType):
    to_type: CxxType

    def __init__(self, to_type: CxxType) -> None:
        self.to_type = to_type

    def __str__(self) -> str:
        return f"{self.to_type}&"


class Identifier:
    id: str
    typeinfo: CxxType
    parent: Optional["Identifier"]

    def __init__(self, id: str, typeinfo: CxxType, parent: Optional["Identifier"] = None) -> None:
        self.id = id
        self.typeinfo = typeinfo
        self.parent = parent

    def member_operator(self) -> str:
        return self.typeinfo.member_operator()

    def as_declarator(self) -> str:
        return f"{self.typeinfo} {self.id}"

    def as_member_of(self) -> str:
        if not self.parent:
            return str(self.id)
        return f"{self.parent}{self.parent.member_operator()}{self.id}"

    def as_hg_conversion(self) -> str:

        valid_hg_conversions: Dict[Type[CxxType], Callable[[Identifier], str]] = {
            String: lambda a: f"{a}.c_str()",
            ExposedBuffer: lambda a: f"hg_bulk_t({a})",
        }

        if self.typeinfo.is_fundamental():
            return self.id

        if type(self.typeinfo) in valid_hg_conversions:
            return valid_hg_conversions[type(self.typeinfo)](self)

        raise ValueError(f"No known conversion for compound type '{self.typeinfo}'")

    def __str__(self) -> str:
        return self.id

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(" \
               f"id='{self.id}', typeinfo={self.typeinfo.__repr__()}, parent={self.parent.__repr__() or 'None'})"


class LValueReference(Identifier):

    def __init__(self, id: str, typeinfo: CxxType, parent: Optional["Identifier"] = None) -> None:
        super().__init__(id, typeinfo, parent)

    def as_declarator(self) -> str:
        return f"{self.typeinfo}& {self.id}"


class ConstLValueReference(Identifier):

    def __init__(self, id: str, typeinfo: CxxType, parent: Optional["Identifier"] = None) -> None:
        super().__init__(id, typeinfo, parent)

    def as_declarator(self) -> str:
        return f"const {self.typeinfo}& {self.id}"


class RValueReference(Identifier):

    def __init__(self, id: str, typeinfo: CxxType, parent: Optional["Identifier"] = None) -> None:
        super().__init__(id, typeinfo, parent)

    def as_declarator(self) -> str:
        return f"{self.typeinfo}&& {self.id}"
