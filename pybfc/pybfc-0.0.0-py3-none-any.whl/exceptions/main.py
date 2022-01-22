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


__all__ = ("InvalidPointerLocation", "InvalidMemory", "SyntaxError")


class InvalidPointerLocation(Exception):
    def __init__(self, location: int) -> None:
        message = f"{location} is invalid pointer location!"
        super(InvalidPointerLocation, self).__init__(message)


class InvalidMemory(Exception):
    def __init__(self, memory_length: int) -> None:
        message = f"Memory with {memory_length} length is invalid memory!"
        super(InvalidMemory, self).__init__(message)


class SyntaxError(Exception):
    def __init__(self, message: str) -> None:
        super(SyntaxError, self).__init__(message)
