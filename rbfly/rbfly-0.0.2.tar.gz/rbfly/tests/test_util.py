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
Unit tests for RbFly utility functions.
"""

from rbfly.streams.util import retry, suppress
from ..util import Option

import pytest

@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_suppress() -> None:
    """
    Test suppressing an exception without retry.

    Note, this test is guarded with timeout to avoid infinite execution if
    no-retry logic is incorrect.
    """
    @suppress(ConnectionError)
    async def f() -> None:
        raise ConnectionError('raising')

    try:
        await f()
    except ConnectionError:
        pytest.fail('Connection error shall not be raised')

@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_retry() -> None:
    """
    Test retrying an asynchronous coroutine.

    Note, this test is guarded with timeout to avoid infinite execution if
    retry logic is incorrect.
    """
    @retry(ConnectionError, retry_after=1)
    async def f(guard: dict[str, int]) -> str:
        guard['value'] -= 1
        while guard['value'] > 0:
            raise ConnectionError('raising')
        return 'it worked'

    try:
        result = await f({'value': 3})  # raise error 3 times
        assert result == 'it worked'
    except ConnectionError:
        pytest.fail('Connection error shall not be raised')

@pytest.mark.parametrize('cls', [int, list[int], tuple[float]])
def test_option_empty(cls: type) -> None:
    """
    Test option object for empty value.
    """
    v = Option[cls]()  # type: ignore
    assert v.empty

    with pytest.raises(AssertionError):
        v.value

def test_option() -> None:
    """
    Test option object for a value.
    """
    v = Option(1)
    assert not v.empty
    assert v.value == 1

def test_option_cls() -> None:
    """
    Test option object with a class.
    """
    class _T:
        obj: Option[list[int]]

        def __init__(self) -> None:
            self.obj = Option[list[int]]()

        def set(self) -> None:
            self.obj = Option([1, 2, 3])

        def get(self) -> list[int]:
            return self.obj.value

    v = _T()
    with pytest.raises(AssertionError):
        v.get()

    v.set()
    assert v.get() == [1, 2, 3]

# vim: sw=4:et:ai
