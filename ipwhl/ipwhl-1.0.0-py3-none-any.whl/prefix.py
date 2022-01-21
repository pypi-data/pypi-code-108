#!/usr/bin/env python
# Give each Python project a hexadecimal prefix for IPWHL metadata
# Copyright (C) 2021  Nguyễn Gia Phong
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from functools import reduce
from operator import add
from os.path import join
from sys import argv

__all__ = ['prefix']


def prefix(name: str) -> str:
    """Return directory prefix for given project name."""
    return format(reduce(add, map(ord, name)) & 0xFF, '02x')


def main() -> None:
    for name in argv[1:]:  # skip script name
        print(join(prefix(name), name))


if __name__ == '__main__': main()
