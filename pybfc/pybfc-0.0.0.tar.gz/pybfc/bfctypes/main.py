# Pybfc - BranFuck compiler write in python
# Copyright (C) 2022 - Awiteb <awiteb@hotmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from enum import Enum
from typing import List

from ..exceptions import InvalidMemory, InvalidPointerLocation

__all__ = (
    "CompilerSettings",
    "BFCommand",
    "Memory",
)


class BFCommand(Enum):
    INPUT: str = ","
    PRINT: str = "."
    PLUS: str = "+"
    MINUS: str = "-"
    RIGHT: str = ">"
    LEFT: str = "<"


class CompilerSettings:
    __slots__ = ("debug",)

    def __init__(self, debug: bool = False) -> None:
        self.debug = debug


class Memory:
    def __init__(self, pointer: int = 0, memory: List[int] = [0]) -> None:
        self.memory = memory
        self.pointer = pointer

    @property
    def memory(self):
        return self.__memory

    @memory.setter
    def memory(self, value: List[int]) -> None:
        if not (1 <= len(value) < 30_000):
            raise InvalidMemory(len(value))
        self.__memory = value

    @property
    def value(self) -> int:
        return self.memory[self.pointer]

    @value.setter
    def value(self, value: int) -> None:
        self.memory[self.pointer] = value % 256

    @property
    def pointer(self) -> int:
        return self.__pointer

    @pointer.setter
    def pointer(self, value: int) -> None:
        if 0 <= value < 30_000:
            if len(self.memory) <= value:
                self.memory.append(0)
            self.__pointer = value
        else:
            raise InvalidPointerLocation(value)

    def execute(self, command: BFCommand) -> None:
        """Execute the command in the memory

        Args:
            command (BFCommand): Command to execute it
        """
        if command == BFCommand.RIGHT:
            self.pointer += 1
        elif command == BFCommand.LEFT:
            self.pointer -= 1
        elif command == BFCommand.PLUS:
            self.value += 1
        elif command == BFCommand.MINUS:
            self.value -= 1
        elif command == BFCommand.PRINT:
            print(chr(self.value), end="")
        elif command == BFCommand.INPUT:
            self.value += sum(map(ord, input()))
