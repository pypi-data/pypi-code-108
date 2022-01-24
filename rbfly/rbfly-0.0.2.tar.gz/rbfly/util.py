#
# rbfly - a library for RabbitMQ Streams using Python asyncio
#
# Copyright (C) 2021-2022 by Artur Wroblewski <wrobell@riseup.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
RbFly utilities.
"""

import typing as tp

T = tp.TypeVar('T')

class Option(tp.Generic[T]):
    """
    Optional type.

    This differes from `typing.Optional`

    - use `Option.empty` property to check if value is set
    - use `Option.value` to retrieve non-null value; if value is not set,
      then assertion error is raised

    Use of null values is not allowed.

    Supported::

        >>> Option[int]()  # doctest: +SKIP
        >>> Option(1)  # doctest: +SKIP

    Not supported::

        >>> Option[int](None)  # doctest: +SKIP
        >>> Option[NoneType](None)  # doctest: +SKIP

    This is not expressed with type annotations below, unfortunately.
    """
    _value: T | None

    def __init__(self, obj: T | None=None) -> None:
        """
        Create instance of optional.

        :param type_obj: Type, class or a value.
        """
        self._value = obj

    @property
    def value(self) -> T:
        """
        Retrieve value, but raise error if it is not set.
        """
        assert self._value is not None
        return self._value

    @property
    def empty(self) -> bool:
        """
        Check if value is unset.
        """
        return self._value is None

# vim: sw=4:et:ai
