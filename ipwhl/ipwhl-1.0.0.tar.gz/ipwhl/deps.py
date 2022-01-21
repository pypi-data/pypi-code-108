# Wrappers around packaging requirements and specifiers
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

from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet

__all__ = ['Req', 'Spec']


class Magic:
    """Mix-in class for some magic methods."""

    def __eq__(self, other: object) -> bool:
        return str(self) == str(other)

    def __hash__(self) -> int:
        return hash(str(self))


class Req(Magic, Requirement): pass
class Spec(Magic, SpecifierSet): pass
